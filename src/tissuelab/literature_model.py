"""Viability lookup trained only on hand-curated published live/dead %."""

from __future__ import annotations

import json

import joblib
import numpy as np
import pandas as pd

from tissuelab.benchmark import FEATURES_CAT, FEATURES_NUM, leave_one_paper_out, load_viability
from tissuelab.db import connect
from tissuelab.paths import DB_PATH, HONEST_METRICS_PATH, LITERATURE_MODEL_PATH
from tissuelab.shrinkage import N0, knob_deltas, shrinkage_estimate


def load_curated_viability(path=DB_PATH) -> pd.DataFrame:
    return load_viability(path)


def _material_mean_estimate(design: dict, frame: pd.DataFrame) -> tuple[float | None, str, int]:
    if frame.empty:
        return None, "empty", 0
    material = design.get("material_class")
    if material:
        subset = frame[frame["material_class"] == material]
        if not subset.empty:
            return float(subset["viability_pct"].mean()), "material_mean", int(len(subset))
    return float(frame["viability_pct"].mean()), "global_mean", int(len(frame))


def _lopo_cached(frame: pd.DataFrame) -> dict:
    if HONEST_METRICS_PATH.exists():
        try:
            report = json.loads(HONEST_METRICS_PATH.read_text())
        except json.JSONDecodeError:
            report = {}
        fresh = (
            report.get("n_rows") == int(len(frame))
            and report.get("n_studies") == int(frame["study_id"].nunique())
            and "shrinkage_lopo" in report
            and "deployed_estimator" in report
        )
        if fresh:
            return report
    return leave_one_paper_out(frame)


def train_literature_viability(path=DB_PATH):
    frame = load_curated_viability(path)
    lopo = leave_one_paper_out(frame)
    material_means = (
        frame.groupby("material_class")["viability_pct"].mean().astype(float).to_dict()
        if not frame.empty
        else {}
    )
    payload = {
        "frame": frame,
        "pipeline": None,
        "lopo": lopo,
        "material_means": material_means,
        "global_mean": float(frame["viability_pct"].mean()) if not frame.empty else None,
        "deployed_estimator": lopo.get("deployed_estimator"),
        "features_num": FEATURES_NUM,
        "features_cat": FEATURES_CAT,
    }
    LITERATURE_MODEL_PATH.parent.mkdir(parents=True, exist_ok=True)
    joblib.dump(payload, LITERATURE_MODEL_PATH)
    HONEST_METRICS_PATH.write_text(json.dumps(lopo, indent=2))
    return payload


def load_literature_model():
    if LITERATURE_MODEL_PATH.exists():
        return joblib.load(LITERATURE_MODEL_PATH)
    return train_literature_viability()


def _query_from_design(design: dict) -> dict:
    kpa = design.get("stiffness_kpa")
    days = design.get("culture_time_days")
    return {
        "material_class": design.get("material_class"),
        "cell_type": design.get("cell_type"),
        "growth_factor": design.get("growth_factor") or "none",
        "stiffness_kpa": None if kpa in (None, "") else float(kpa),
        "culture_time_days": None if days in (None, "") else float(days),
    }


COMPETITOR = {
    "material_class": "GelMA",
    "stiffness_kpa": 25.0,
    "cell_type": "articular_chondrocyte",
    "growth_factor": "TGF_b3",
    "culture_time_days": 14,
}


def _coverage(frame: pd.DataFrame, material: str | None) -> dict:
    n_total = int(len(frame))
    n_kpa = int(frame["stiffness_kpa"].notna().sum()) if n_total else 0
    sub = frame[frame["material_class"] == material] if material else frame.iloc[0:0]
    return {
        "n_total": n_total,
        "n_studies": int(frame["study_id"].nunique()) if n_total else 0,
        "n_with_kpa": n_kpa,
        "pct_kpa_missing": round(100.0 * (1 - n_kpa / n_total), 0) if n_total else 100.0,
        "n_material": int(len(sub)),
        "n_material_with_kpa": int(sub["stiffness_kpa"].notna().sum()) if len(sub) else 0,
    }


def _chart_points(frame: pd.DataFrame, weights: np.ndarray, material: str | None) -> list[dict]:
    out = []
    w = weights if weights is not None and len(weights) == len(frame) else np.ones(len(frame))
    for i, row in enumerate(frame.itertuples(index=False)):
        kpa = getattr(row, "stiffness_kpa", None)
        out.append(
            {
                "kpa": None if kpa is None or pd.isna(kpa) else float(kpa),
                "viability_pct": float(row.viability_pct),
                "material_class": row.material_class,
                "same_material": bool(material and row.material_class == material),
                "weight": round(float(w[i]), 3),
                "study_id": row.study_id,
            }
        )
    return out


def _verdict(design: dict, mean: float | None, coverage: dict, competitor_mean: float | None, mae: float | None) -> str:
    material = design.get("material_class") or "this gel"
    kpa = design.get("stiffness_kpa")
    kpa_s = f" ~{float(kpa):.0f} kPa" if kpa not in (None, "") else ""
    n = coverage.get("n_material") or 0
    n_kpa = coverage.get("n_material_with_kpa") or 0
    if mean is None:
        return "Ainda não há live/dead extraído para treinar um número."
    if n == 0:
        return (
            f"Não há live/dead extraído para {material}. O valor mostrado pede emprestado a outros géis — "
            "não o uses para escolher o próximo encapsulamento."
        )
    if n == 1:
        extra = " A rigidez move o número sobretudo por empréstimo de outros materiais." if n_kpa == 0 else ""
        return (
            f"Há só 1 condição {material} na tabela.{extra} Trata {mean:.0f}% como uma âncora fraca; "
            "abre os papers vizinhos."
        )
    band = f" (±{mae:.0f} pontos entre papers)" if mae else ""
    vs = ""
    if competitor_mean is not None:
        diff = mean - competitor_mean
        vs = (
            f" Comparado com o protocolo típico GelMA 25 kPa + TGF-β3 ({competitor_mean:.0f}%), "
            f"isto está {abs(diff):.0f} pontos {'acima' if diff > 0 else 'abaixo'}."
        )
    return (
        f"Para {material}{kpa_s}, a literatura aponta para {mean:.0f}% live/dead{band}, "
        f"com {n} condições extraídas ({n_kpa} com kPa).{vs} "
        "Isto não substitui o teu próximo frasco."
    )


def predict_literature_viability(design: dict) -> dict:
    """Empirical-Bayes point estimate. Does not need the XGBoost joblib."""
    frame = load_curated_viability()
    lopo = _lopo_cached(frame)
    query = _query_from_design(design)
    est = shrinkage_estimate(query, frame)
    mean = est["mean"]
    deployed_lopo = lopo.get("deployed_lopo") or {}
    dummy_lopo = lopo.get("dummy_lopo") or {}
    ridge_lopo = lopo.get("ridge_lopo") or {}
    material_lopo = lopo.get("material_mean_lopo") or {}
    shrinkage_lopo = lopo.get("shrinkage_lopo") or {}
    mae = (shrinkage_lopo.get("mae") if shrinkage_lopo else None) or deployed_lopo.get("mae") or dummy_lopo.get("mae")
    band = float(mae) if mae is not None else 12.0
    low = None if mean is None else float(np.clip(mean - band, 0, 100))
    high = None if mean is None else float(np.clip(mean + band, 0, 100))
    similar = similar_published(design, k=5, weights=est.get("weights"), frame=frame)
    coverage = _coverage(frame, design.get("material_class"))
    competitor = shrinkage_estimate(COMPETITOR, frame)
    competitor_mean = None if competitor["mean"] is None else round(float(competitor["mean"]), 1)
    chart_points = _chart_points(frame, est.get("weights"), design.get("material_class"))
    verdict = _verdict(design, None if mean is None else float(mean), coverage, competitor_mean, mae)
    return {
        "mean": None if mean is None else round(mean, 1),
        "low": None if low is None else round(low, 1),
        "high": None if high is None else round(high, 1),
        "local": None if est["local"] is None else round(est["local"], 1),
        "prior": None if est["prior"] is None else round(est["prior"], 1),
        "n_eff": round(float(est["n_eff"]), 1),
        "local_weight": round(float(est["local_weight"]), 3),
        "prior_strength": N0,
        "estimator": est["estimator"],
        "n_support": est["n_support"],
        "interval_is_lopo_mae": True,
        "knob_deltas": knob_deltas(query, frame),
        "coverage": coverage,
        "chart_points": chart_points,
        "competitor": {"label": "GelMA 25 kPa + TGF-β3", "mean": competitor_mean},
        "verdict": verdict,
        "lopo": {
            "n_studies": lopo.get("n_studies"),
            "n_rows": lopo.get("n_rows"),
            "dummy_mae": dummy_lopo.get("mae"),
            "ridge_mae": ridge_lopo.get("mae"),
            "ridge_r2": ridge_lopo.get("r2"),
            "material_mean_mae": material_lopo.get("mae"),
            "material_mean_r2": material_lopo.get("r2"),
            "shrinkage_mae": shrinkage_lopo.get("mae"),
            "shrinkage_r2": shrinkage_lopo.get("r2"),
            "deployed_estimator": lopo.get("deployed_estimator"),
            "deployed_mae": deployed_lopo.get("mae"),
            "deployed_r2": deployed_lopo.get("r2"),
            "beats_dummy": lopo.get("beats_dummy"),
            "ridge_beats_dummy": lopo.get("ridge_beats_dummy"),
            "mvp_pass": lopo.get("mvp_pass"),
        },
        "similar": similar,
        "notes": _notes(
            lopo,
            estimator=est["estimator"],
            n_support=est["n_support"],
            material=design.get("material_class"),
            n_eff=est["n_eff"],
            local=est["local"],
            prior=est["prior"],
        ),
    }


def _notes(
    lopo: dict,
    estimator: str | None = None,
    n_support: int | None = None,
    material: str | None = None,
    n_eff: float | None = None,
    local: float | None = None,
    prior: float | None = None,
) -> list[str]:
    notes = [
        "Trained only on hand-curated live/dead percents (no pmid* auto-promote, no simulator).",
        "Point estimate is empirical Bayes: a kernel over published conditions, shrunk toward the material-class mean. Not a neural net.",
        "Interval is ± leave-one-paper-out MAE of shrinkage, not a biological confidence interval.",
    ]
    if estimator == "shrinkage_global_prior" and material:
        notes.append(
            f"No published live/dead rows for {material} — prior is the global mean, pulled by similar gels."
        )
    elif n_support and material:
        notes.append(f"Material prior from {n_support} published {material} live/dead rows.")
    if local is not None and prior is not None and n_eff is not None:
        notes.append(
            f"Matched-condition mean {local:.1f}% shrunk toward prior {prior:.1f}% "
            f"(effective n={n_eff:.1f}, prior strength n0={N0:.0f})."
        )
    if not lopo.get("beats_dummy"):
        notes.append(
            "Does not yet beat a dummy mean — use nearest extracted papers, not the point estimate, to pick a gel."
        )
    elif not lopo.get("mvp_pass"):
        notes.append(
            "Shrinkage beats dummy on LOPO MAE but has not met the MVP bar "
            "(15% better, R²>0, n_studies≥15). Use nearest extracted papers to choose the next gel."
        )
    else:
        notes.append("Deployed LOPO currently meets the viability MVP bar.")
    return notes


def similar_published(design: dict, k: int = 5, weights: np.ndarray | None = None, frame: pd.DataFrame | None = None) -> list[dict]:
    if frame is None:
        conn = connect(DB_PATH)
        frame = pd.read_sql_query(
            """
            SELECT experiment_id, study_id, citation, doi, material_class, stiffness_kpa,
                   cell_type, growth_factor, culture_time_days, viability_pct
            FROM v_model_viability
            """,
            conn,
        )
        conn.close()
    if frame.empty:
        return []
    query = _query_from_design(design)
    if weights is None or len(weights) != len(frame):
        weights = shrinkage_estimate(query, frame)["weights"]
    want = str(query.get("material_class") or "")
    mats = frame["material_class"].astype(str).to_numpy()
    ranked = sorted(
        range(len(frame)),
        key=lambda i: (0 if mats[i] == want else 1, -float(weights[i])),
    )
    out = []
    for pos in ranked[:k]:
        row = frame.iloc[int(pos)]
        out.append(
            {
                "experiment_id": row["experiment_id"],
                "study_id": row["study_id"],
                "citation": None if pd.isna(row.get("citation")) else row.get("citation"),
                "doi": None if pd.isna(row.get("doi")) else row.get("doi"),
                "material_class": row["material_class"],
                "cell_type": None if pd.isna(row.get("cell_type")) else row.get("cell_type"),
                "stiffness_kpa": None if pd.isna(row["stiffness_kpa"]) else float(row["stiffness_kpa"]),
                "viability_pct": float(row["viability_pct"]),
                "growth_factor": None if pd.isna(row.get("growth_factor")) else row.get("growth_factor"),
                "culture_time_days": None
                if pd.isna(row["culture_time_days"])
                else float(row["culture_time_days"]),
                "match_score": round(float(weights[int(pos)]), 3),
            }
        )
    return out

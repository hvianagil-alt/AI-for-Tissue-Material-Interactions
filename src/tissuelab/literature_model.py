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
    stats = _material_stats(sub)
    return {
        "n_total": n_total,
        "n_studies": int(frame["study_id"].nunique()) if n_total else 0,
        "n_with_kpa": n_kpa,
        "pct_kpa_missing": round(100.0 * (1 - n_kpa / n_total), 0) if n_total else 100.0,
        "n_material": int(len(sub)),
        "n_material_with_kpa": int(sub["stiffness_kpa"].notna().sum()) if len(sub) else 0,
        "n_material_studies": int(sub["study_id"].nunique()) if len(sub) else 0,
        "material_mean": stats.get("mean"),
        "material_median": stats.get("median"),
        "material_sd": stats.get("sd"),
        "material_min": stats.get("min"),
        "material_max": stats.get("max"),
        "material_p10": stats.get("p10"),
    }


def _material_stats(sub: pd.DataFrame) -> dict:
    if sub is None or sub.empty:
        return {}
    values = sub["viability_pct"].astype(float)
    out = {
        "mean": round(float(values.mean()), 1),
        "median": round(float(values.median()), 1),
        "min": round(float(values.min()), 1),
        "max": round(float(values.max()), 1),
        "p10": round(float(np.percentile(values, 10)), 1),
    }
    if len(values) > 1:
        out["sd"] = round(float(values.std(ddof=1)), 1)
    return out


def _variance_split(frame: pd.DataFrame) -> dict:
    if frame.empty or frame["study_id"].nunique() < 2:
        return {"between_paper_sd": None, "within_paper_sd_median": None}
    paper_means = frame.groupby("study_id")["viability_pct"].mean()
    within = frame.groupby("study_id")["viability_pct"].std(ddof=1)
    return {
        "between_paper_sd": round(float(paper_means.std(ddof=1)), 1),
        "within_paper_sd_median": None
        if within.dropna().empty
        else round(float(within.median()), 1),
    }


def _chart_points(frame: pd.DataFrame, weights: np.ndarray, material: str | None) -> list[dict]:
    out = []
    w = weights if weights is not None and len(weights) == len(frame) else np.ones(len(frame))
    for i, row in enumerate(frame.itertuples(index=False)):
        kpa = getattr(row, "stiffness_kpa", None)
        citation = getattr(row, "citation", None)
        out.append(
            {
                "kpa": None if kpa is None or pd.isna(kpa) else float(kpa),
                "viability_pct": float(row.viability_pct),
                "material_class": row.material_class,
                "same_material": bool(material and row.material_class == material),
                "weight": round(float(w[i]), 3),
                "study_id": row.study_id,
                "citation": None if citation is None or pd.isna(citation) else str(citation),
            }
        )
    return out


def _adaptive_band(
    mae: float,
    coverage: dict,
    query: dict,
    n_eff_same: float,
    global_sd: float | None,
) -> tuple[float, list[str]]:
    """Widen ±LOPO MAE when this gel is thin, heterogeneous, or borrowing kPa.

    Never narrower than LOPO MAE: that is the honest error for a new paper.
    """
    reasons: list[str] = ["chão = MAE leave-one-paper-out"]
    half = float(mae)
    n_sup = int(coverage.get("n_material") or 0)
    n_kpa = int(coverage.get("n_material_with_kpa") or 0)
    material_sd = coverage.get("material_sd")
    gsd = float(global_sd) if global_sd else 23.0
    if material_sd is not None and n_sup >= 3 and gsd > 0:
        het = (float(material_sd) / gsd) ** 2
        if het > 1:
            half *= float(np.sqrt(1.0 + 0.5 * (het - 1.0)))
            reasons.append("este gel é mais heterogéneo do que a tabela")
    half *= float(np.sqrt(1.0 + 1.0 / max(n_sup, 1)))
    if n_sup <= 1:
        reasons.append("muito poucas condições deste gel")
    kpa = query.get("stiffness_kpa")
    if kpa not in (None, "") and n_kpa == 0:
        half *= 1.2
        reasons.append("rigidez pedida emprestada a outros materiais")
    if n_eff_same is not None and float(n_eff_same) < 2:
        reasons.append("n efectivo neste gel < 2")
    half = float(np.clip(half, mae, 40.0))
    return half, reasons


def _trust(coverage: dict, n_eff_same: float) -> dict:
    n = int(coverage.get("n_material") or 0)
    n_kpa = int(coverage.get("n_material_with_kpa") or 0)
    sd = coverage.get("material_sd")
    if n == 0:
        return {
            "level": "sem_dados",
            "label": "Sem evidência deste gel",
            "fill": 0,
            "why": "Não há live/dead extraído para esta classe de material.",
        }
    if n == 1 or n_eff_same < 2:
        extra = " A rigidez, se mexer, vem de outros géis." if n_kpa == 0 else ""
        return {
            "level": "fraca",
            "label": "Evidência fraca",
            "fill": 1,
            "why": f"Só {n} condição extraída deste gel.{extra}",
        }
    if sd is not None and float(sd) >= 20:
        return {
            "level": "heterogenea",
            "label": "Evidência heterogénea",
            "fill": 2,
            "why": f"{n} condições, mas o live/dead deste gel varia ~{sd:.0f} pontos. Olha o mínimo publicado, não só a média.",
        }
    if n >= 4 and n_kpa >= 2:
        return {
            "level": "util",
            "label": "Evidência útil (ainda pequena)",
            "fill": 3,
            "why": f"{n} condições deste gel, {n_kpa} com kPa. Serve para comparar papers, não para substituir o frasco.",
        }
    return {
        "level": "fraca",
        "label": "Evidência limitada",
        "fill": 1,
        "why": f"{n} condições extraídas; {n_kpa} com kPa.",
    }


def _verdict(
    design: dict,
    mean: float | None,
    coverage: dict,
    competitor_mean: float | None,
    band: float | None,
    trust: dict,
) -> str:
    material = design.get("material_class") or "este gel"
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
    floor = coverage.get("material_min")
    floor_s = f" O pior live/dead extraído deste gel é {floor:.0f}%." if floor is not None else ""
    band_s = f" (±{band:.0f} pontos; chão = erro entre papers)" if band else ""
    vs = ""
    if competitor_mean is not None:
        diff = mean - competitor_mean
        side = "acima" if diff > 0 else "abaixo" if diff < 0 else "ao nível"
        vs = (
            f" Comparado com GelMA 25 kPa + TGF-β3 ({competitor_mean:.0f}%), "
            f"isto está {abs(diff):.0f} pontos {side}."
        )
    borrow = ""
    if kpa not in (None, "") and n_kpa == 0:
        borrow = " A barra de rigidez está a pedir kPa a outros materiais."
    return (
        f"{trust.get('label')}. Para {material}{kpa_s}, a literatura aponta para {mean:.0f}% live/dead{band_s}, "
        f"com {n} condições extraídas ({n_kpa} com kPa).{vs}{borrow}{floor_s} "
        "Isto não substitui o teu próximo frasco."
    )


def _alternatives(query: dict, frame: pd.DataFrame) -> list[dict]:
    specs = [
        ("you", query, "O teu protocolo"),
        ("competitor", COMPETITOR, "GelMA 25 kPa + TGF-β3"),
    ]
    if (query.get("growth_factor") or "none") == "none":
        specs.append(("plus_tgf", {**query, "growth_factor": "TGF_b3"}, "O mesmo gel + TGF-β3"))
    else:
        specs.append(("no_tgf", {**query, "growth_factor": "none"}, "O mesmo gel sem TGF"))
    specs.append(("soft", {**query, "stiffness_kpa": 2.0}, "O mesmo gel a 2 kPa (mole)"))
    specs.append(("stiff", {**query, "stiffness_kpa": 40.0}, "O mesmo gel a 40 kPa (rígido)"))
    seen = set()
    out = []
    for key, spec, label in specs:
        fingerprint = (
            spec.get("material_class"),
            spec.get("stiffness_kpa"),
            spec.get("cell_type"),
            spec.get("growth_factor"),
            spec.get("culture_time_days"),
        )
        if fingerprint in seen:
            continue
        seen.add(fingerprint)
        est = shrinkage_estimate(spec, frame)
        if est["mean"] is None:
            continue
        out.append(
            {
                "id": key,
                "label": label,
                "mean": round(float(est["mean"]), 1),
                "material_class": spec.get("material_class"),
                "stiffness_kpa": spec.get("stiffness_kpa"),
                "growth_factor": spec.get("growth_factor"),
            }
        )
    return out


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
    coverage = _coverage(frame, design.get("material_class"))
    n_eff_same = float(est.get("n_eff_same") or 0.0)
    global_sd = lopo.get("viability_std")
    if mae is None:
        band, interval_reasons = 12.0, ["MAE indisponível — banda provisória"]
    else:
        band, interval_reasons = _adaptive_band(float(mae), coverage, query, n_eff_same, global_sd)
    low = None if mean is None else float(np.clip(mean - band, 0, 100))
    high = None if mean is None else float(np.clip(mean + band, 0, 100))
    similar = similar_published(design, k=5, weights=est.get("weights"), frame=frame)
    competitor = shrinkage_estimate(COMPETITOR, frame)
    competitor_mean = None if competitor["mean"] is None else round(float(competitor["mean"]), 1)
    chart_points = _chart_points(frame, est.get("weights"), design.get("material_class"))
    trust = _trust(coverage, n_eff_same)
    verdict = _verdict(
        design,
        None if mean is None else float(mean),
        coverage,
        competitor_mean,
        band,
        trust,
    )
    dummy_mae = dummy_lopo.get("mae")
    target_mae = None if dummy_mae is None else round(float(dummy_mae) * 0.85, 2)
    next_read = None
    for row in similar:
        if row.get("material_class") == design.get("material_class") and row.get("doi"):
            next_read = {
                "citation": row.get("citation") or row.get("study_id"),
                "doi": row.get("doi"),
                "viability_pct": row.get("viability_pct"),
            }
            break
    if next_read is None and similar:
        top = similar[0]
        if top.get("doi"):
            next_read = {
                "citation": top.get("citation") or top.get("study_id"),
                "doi": top.get("doi"),
                "viability_pct": top.get("viability_pct"),
            }
    return {
        "mean": None if mean is None else round(mean, 1),
        "low": None if low is None else round(low, 1),
        "high": None if high is None else round(high, 1),
        "local": None if est["local"] is None else round(est["local"], 1),
        "prior": None if est["prior"] is None else round(est["prior"], 1),
        "n_eff": round(float(est["n_eff"]), 1),
        "n_eff_same": round(n_eff_same, 1),
        "local_weight": round(float(est["local_weight"]), 3),
        "prior_strength": N0,
        "estimator": est["estimator"],
        "n_support": est["n_support"],
        "interval_is_lopo_mae": False,
        "interval_floor_is_lopo_mae": True,
        "interval_half": round(float(band), 1),
        "interval_reasons": interval_reasons,
        "knob_deltas": knob_deltas(query, frame),
        "coverage": coverage,
        "trust": trust,
        "material_counts": (
            {str(k): int(v) for k, v in frame.groupby("material_class").size().items()}
            if not frame.empty
            else {}
        ),
        "chart_points": chart_points,
        "competitor": {
            "label": "GelMA 25 kPa + TGF-β3",
            "mean": competitor_mean,
            "stiffness_kpa": COMPETITOR["stiffness_kpa"],
            "delta": None if mean is None or competitor_mean is None else round(float(mean) - competitor_mean, 1),
        },
        "alternatives": _alternatives(query, frame),
        "variance_split": _variance_split(frame),
        "next_read": next_read,
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
            "target_mae": target_mae,
            "viability_std": global_sd,
        },
        "similar": similar,
        "notes": _notes(
            lopo,
            estimator=est["estimator"],
            n_support=est["n_support"],
            material=design.get("material_class"),
            n_eff=est["n_eff"],
            n_eff_same=n_eff_same,
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
    n_eff_same: float | None = None,
    local: float | None = None,
    prior: float | None = None,
) -> list[str]:
    notes = [
        "Treino só com live/dead extraído à mão (sem pmid* auto-promovido, sem simulador).",
        "A estimativa é Bayes empírico: kernel sobre condições publicadas, encolhido para a média da classe de material. Não é uma rede neuronal.",
        "A banda nunca é mais estreita do que o MAE leave-one-paper-out; alarga-se se o gel tiver poucas linhas, for heterogéneo, ou se a rigidez for emprestada. Não é um intervalo de confiança biológico.",
        "Não baixamos os 5% de live/dead com Huber/mediana: são evidência de géis que matam células, não ruído.",
    ]
    if estimator == "shrinkage_global_prior" and material:
        notes.append(
            f"Não há live/dead publicado para {material} — o prior é a média global, puxado por géis parecidos."
        )
    elif n_support and material:
        notes.append(f"Prior do material a partir de {n_support} linhas {material} extraídas.")
    if local is not None and prior is not None and n_eff is not None:
        same_s = f"{n_eff_same:.1f}" if n_eff_same is not None else "—"
        notes.append(
            f"Média local {local:.1f}% encolhida para o prior {prior:.1f}% "
            f"(n efectivo neste gel={same_s}, n0={N0:.0f}). "
            f"O n efectivo do kernel inteiro ({n_eff:.1f}) conta outros materiais e não é o tamanho de amostra deste gel."
        )
    if not lopo.get("beats_dummy"):
        notes.append(
            "Ainda não bate um dummy mean — usa os papers extraídos, não o número pontual, para escolher o gel."
        )
    elif not lopo.get("mvp_pass"):
        notes.append(
            "O shrinkage bate o dummy no LOPO MAE mas ainda não atinge a barra MVP "
            "(15% melhor, R²>0, n_studies≥15). Usa os papers vizinhos para escolher o próximo gel."
        )
    else:
        notes.append("O LOPO actual atinge a barra MVP de viabilidade.")
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

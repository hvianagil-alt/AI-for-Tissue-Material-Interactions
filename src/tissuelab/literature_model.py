"""Viability lookup trained only on hand-curated published live/dead %."""

from __future__ import annotations

import json

import joblib
import numpy as np
import pandas as pd

from tissuelab.benchmark import FEATURES_CAT, FEATURES_NUM, leave_one_paper_out, load_viability
from tissuelab.db import connect
from tissuelab.paths import DB_PATH, HONEST_METRICS_PATH, LITERATURE_MODEL_PATH


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


def _point_estimate(design: dict, frame: pd.DataFrame, deployed: str | None) -> tuple[float | None, str, int]:
    if frame.empty:
        return None, "empty", 0
    if deployed == "material_mean":
        return _material_mean_estimate(design, frame)
    return float(frame["viability_pct"].mean()), "dummy", int(len(frame))


def _lopo_cached(frame: pd.DataFrame) -> dict:
    if HONEST_METRICS_PATH.exists():
        try:
            report = json.loads(HONEST_METRICS_PATH.read_text())
        except json.JSONDecodeError:
            report = {}
        fresh = (
            report.get("n_rows") == int(len(frame))
            and report.get("n_studies") == int(frame["study_id"].nunique())
            and "material_mean_lopo" in report
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


def predict_literature_viability(design: dict) -> dict:
    """Point estimate from the deployed LOPO estimator. Does not need the XGBoost joblib."""
    frame = load_curated_viability()
    lopo = _lopo_cached(frame)
    deployed = lopo.get("deployed_estimator")
    mean, estimator, n_support = _point_estimate(design, frame, deployed)
    if mean is not None:
        mean = float(np.clip(mean, 0, 100))
    deployed_lopo = lopo.get("deployed_lopo") or {}
    dummy_lopo = lopo.get("dummy_lopo") or {}
    ridge_lopo = lopo.get("ridge_lopo") or {}
    material_lopo = lopo.get("material_mean_lopo") or {}
    mae = deployed_lopo.get("mae")
    if mae is None:
        mae = dummy_lopo.get("mae")
    band = float(mae) if mae is not None else 12.0
    low = None if mean is None else float(np.clip(mean - band, 0, 100))
    high = None if mean is None else float(np.clip(mean + band, 0, 100))
    similar = similar_published(design, k=5)
    return {
        "mean": None if mean is None else round(mean, 1),
        "low": None if low is None else round(low, 1),
        "high": None if high is None else round(high, 1),
        "estimator": estimator,
        "n_support": n_support,
        "interval_is_lopo_mae": True,
        "lopo": {
            "n_studies": lopo.get("n_studies"),
            "n_rows": lopo.get("n_rows"),
            "dummy_mae": dummy_lopo.get("mae"),
            "ridge_mae": ridge_lopo.get("mae"),
            "ridge_r2": ridge_lopo.get("r2"),
            "material_mean_mae": material_lopo.get("mae"),
            "material_mean_r2": material_lopo.get("r2"),
            "deployed_estimator": deployed,
            "deployed_mae": deployed_lopo.get("mae"),
            "deployed_r2": deployed_lopo.get("r2"),
            "beats_dummy": lopo.get("beats_dummy"),
            "ridge_beats_dummy": lopo.get("ridge_beats_dummy"),
            "mvp_pass": lopo.get("mvp_pass"),
        },
        "similar": similar,
        "notes": _notes(lopo, estimator=estimator, n_support=n_support, material=design.get("material_class")),
    }


def _notes(
    lopo: dict,
    estimator: str | None = None,
    n_support: int | None = None,
    material: str | None = None,
) -> list[str]:
    deployed = lopo.get("deployed_estimator") or estimator or "material_mean"
    label = str(deployed).replace("_", " ")
    notes = [
        "Trained only on hand-curated live/dead percents (no pmid* auto-promote, no simulator).",
        f"Point estimate is the {label} of published live/dead % (unseen gels fall back to the global mean).",
        "Interval is ± leave-one-paper-out MAE of the deployed estimator, not a biological confidence interval.",
    ]
    if estimator == "global_mean" and material:
        notes.append(
            f"No published live/dead rows for {material} in the training table — showing the global mean."
        )
    elif n_support and material and estimator == "material_mean":
        notes.append(f"Based on {n_support} published {material} live/dead rows.")
    if not lopo.get("beats_dummy"):
        notes.append(
            "Does not yet beat a dummy mean — use nearest extracted papers, not the point estimate, to pick a gel."
        )
    elif not lopo.get("mvp_pass"):
        notes.append(
            f"{label.capitalize()} beats dummy on LOPO MAE but has not met the MVP bar "
            "(15% better, R²>0, n_studies≥15). Use nearest extracted papers to choose the next gel."
        )
    else:
        notes.append("Deployed LOPO currently meets the viability MVP bar.")
    return notes


def similar_published(design: dict, k: int = 5) -> list[dict]:
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
    want_mat = design.get("material_class")
    want_kpa = design.get("stiffness_kpa")
    want_cell = design.get("cell_type")
    scored = []
    for _, row in frame.iterrows():
        score = 0.0
        if want_mat and row["material_class"] == want_mat:
            score += 3.0
        if want_cell and row["cell_type"] == want_cell:
            score += 1.0
        if want_kpa is not None and pd.notna(row["stiffness_kpa"]):
            score += max(0.0, 2.0 - abs(float(row["stiffness_kpa"]) - float(want_kpa)) / 20.0)
        else:
            score += 0.2
        scored.append((score, row))
    scored.sort(key=lambda item: (-item[0], abs((item[1]["viability_pct"] or 0) - 90)))
    out = []
    for score, row in scored[:k]:
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
                "growth_factor": row.get("growth_factor"),
                "culture_time_days": None
                if pd.isna(row["culture_time_days"])
                else float(row["culture_time_days"]),
                "match_score": round(float(score), 2),
            }
        )
    return out

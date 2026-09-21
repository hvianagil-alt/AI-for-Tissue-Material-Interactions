"""Viability model trained only on hand-curated published live/dead %."""

from __future__ import annotations

import json

import joblib
import numpy as np
import pandas as pd
from sklearn.linear_model import Ridge
from sklearn.pipeline import Pipeline

from tissuelab.benchmark import FEATURES_CAT, FEATURES_NUM, _pipe, leave_one_paper_out, load_viability
from tissuelab.db import connect
from tissuelab.paths import DB_PATH, HONEST_METRICS_PATH, LITERATURE_MODEL_PATH


def load_curated_viability(path=DB_PATH) -> pd.DataFrame:
    return load_viability(path)


def train_literature_viability(path=DB_PATH):
    frame = load_curated_viability(path)
    lopo = leave_one_paper_out(frame)
    if frame.empty or frame["study_id"].nunique() < 3:
        payload = {"frame": frame, "pipeline": None, "lopo": lopo}
        LITERATURE_MODEL_PATH.parent.mkdir(parents=True, exist_ok=True)
        joblib.dump(payload, LITERATURE_MODEL_PATH)
        return payload
    x = frame[FEATURES_NUM + FEATURES_CAT]
    y = frame["viability_pct"].astype(float)
    pipe = _pipe(Ridge(alpha=1.0))
    pipe.fit(x, y)
    payload = {
        "frame": frame,
        "pipeline": pipe,
        "lopo": lopo,
        "features_num": FEATURES_NUM,
        "features_cat": FEATURES_CAT,
    }
    LITERATURE_MODEL_PATH.parent.mkdir(parents=True, exist_ok=True)
    joblib.dump(payload, LITERATURE_MODEL_PATH)
    HONEST_METRICS_PATH.write_text(json.dumps(lopo, indent=2))
    return payload


def load_literature_model():
    if not LITERATURE_MODEL_PATH.exists():
        return train_literature_viability()
    return joblib.load(LITERATURE_MODEL_PATH)


def _design_row(design: dict) -> pd.DataFrame:
    row = {key: design.get(key) for key in FEATURES_NUM + FEATURES_CAT}
    return pd.DataFrame([row])


def predict_literature_viability(design: dict) -> dict:
    model = load_literature_model()
    frame = model["frame"]
    lopo = model["lopo"]
    pipe: Pipeline | None = model.get("pipeline")
    x = _design_row(design)
    mae = None
    if lopo.get("ridge_lopo"):
        mae = float(lopo["ridge_lopo"]["mae"])
    elif lopo.get("dummy_lopo"):
        mae = float(lopo["dummy_lopo"]["mae"])
    if pipe is None:
        mean = float(frame["viability_pct"].mean()) if not frame.empty else None
    else:
        mean = float(pipe.predict(x)[0])
    if mean is not None:
        mean = float(np.clip(mean, 0, 100))
    band = mae or 12.0
    low = None if mean is None else float(np.clip(mean - band, 0, 100))
    high = None if mean is None else float(np.clip(mean + band, 0, 100))
    similar = similar_published(design, k=5)
    return {
        "mean": None if mean is None else round(mean, 1),
        "low": None if low is None else round(low, 1),
        "high": None if high is None else round(high, 1),
        "interval_is_lopo_mae": True,
        "lopo": {
            "n_studies": lopo.get("n_studies"),
            "n_rows": lopo.get("n_rows"),
            "dummy_mae": (lopo.get("dummy_lopo") or {}).get("mae"),
            "ridge_mae": (lopo.get("ridge_lopo") or {}).get("mae"),
            "ridge_r2": (lopo.get("ridge_lopo") or {}).get("r2"),
            "beats_dummy": lopo.get("beats_dummy"),
            "mvp_pass": lopo.get("mvp_pass"),
        },
        "similar": similar,
        "notes": _notes(lopo),
    }


def _notes(lopo: dict) -> list[str]:
    notes = [
        "Trained only on hand-curated live/dead percents (no pmid* auto-promote, no simulator).",
        "Interval is ± leave-one-paper-out MAE, not a biological confidence interval.",
    ]
    if not lopo.get("beats_dummy"):
        notes.append(
            "Does not yet beat a dummy mean — use nearest extracted papers, not the point estimate, to pick a gel."
        )
    elif not lopo.get("mvp_pass"):
        notes.append(
            "Ridge beats dummy on LOPO MAE but has not met the MVP bar (15% better, R²>0, n_studies≥15)."
        )
    else:
        notes.append("Ridge LOPO currently meets the viability MVP bar.")
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

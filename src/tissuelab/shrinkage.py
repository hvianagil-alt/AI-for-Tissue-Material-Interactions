"""Empirical-Bayes viability: kernel-weighted published live/dead, shrunk to the material mean.

Ridge overfits 42 rows. A raw kNN also loses leave-one-paper-out. This estimator
keeps the material-class mean as the prior and lets stiffness / time / TGF / cell
type pull the point estimate only as far as the matched papers support.

Hyperparameters are locked (not fit per query). They were chosen by LOPO MAE
on v_model_viability. This is statistics, not a neural net.
"""

from __future__ import annotations

import numpy as np
import pandas as pd

# Locked after LOPO search. Do not retune on the query you are serving.
N0 = 12.0
TAU_KPA = 20.0
TAU_DAYS = 21.0
MISMATCH_MATERIAL = 0.45
W_CELL_MATCH = 1.20
W_GF_MATCH = 1.25
MISSING_KPA = 0.70
MISSING_DAYS = 0.80


def _col_str(frame: pd.DataFrame, col: str, default: str = "") -> np.ndarray:
    if col not in frame.columns:
        return np.full(len(frame), default, dtype=object)
    return frame[col].fillna(default).astype(str).to_numpy()


def kernel_weights(query: dict, train: pd.DataFrame) -> np.ndarray:
    n = len(train)
    if n == 0:
        return np.zeros(0, dtype=float)
    w = np.ones(n, dtype=float)
    mats = _col_str(train, "material_class")
    cells = _col_str(train, "cell_type")
    gfs = _col_str(train, "growth_factor", "none")
    gfs = np.where(gfs == "nan", "none", gfs)
    kpas = train["stiffness_kpa"].to_numpy(dtype=float) if "stiffness_kpa" in train.columns else np.full(n, np.nan)
    days = (
        train["culture_time_days"].to_numpy(dtype=float)
        if "culture_time_days" in train.columns
        else np.full(n, np.nan)
    )
    qmat = str(query.get("material_class") or "")
    qcell = str(query.get("cell_type") or "")
    qgf = str(query.get("growth_factor") or "none") or "none"
    qkpa = query.get("stiffness_kpa")
    qdays = query.get("culture_time_days")
    w *= np.where(mats == qmat, 1.0, MISMATCH_MATERIAL)
    w *= np.where(cells == qcell, W_CELL_MATCH, 2.0 - W_CELL_MATCH)
    w *= np.where(gfs == qgf, W_GF_MATCH, 2.0 - W_GF_MATCH)
    if qkpa is not None and qkpa != "":
        dk = np.abs(kpas - float(qkpa))
        wk = np.exp(-((dk / TAU_KPA) ** 2))
        w *= np.where(np.isnan(kpas), MISSING_KPA, wk)
    if qdays is not None and qdays != "":
        dd = np.abs(days - float(qdays))
        wd = np.exp(-((dd / TAU_DAYS) ** 2))
        w *= np.where(np.isnan(days), MISSING_DAYS, wd)
    return w


def _n_eff(weights: np.ndarray) -> float:
    s = float(weights.sum())
    if s <= 0:
        return 0.0
    return float((s * s) / (float((weights ** 2).sum()) + 1e-12))


def shrinkage_estimate(query: dict, train: pd.DataFrame) -> dict:
    """Return a shrunk point estimate and the pieces needed for the UI."""
    if train.empty:
        return {
            "mean": None,
            "local": None,
            "prior": None,
            "n_eff": 0.0,
            "n_support": 0,
            "local_weight": 0.0,
            "weights": np.zeros(0),
            "estimator": "empty",
        }
    y = train["viability_pct"].astype(float).to_numpy()
    weights = kernel_weights(query, train)
    if float(weights.sum()) <= 0:
        prior = float(y.mean())
        return {
            "mean": prior,
            "local": prior,
            "prior": prior,
            "n_eff": 0.0,
            "n_support": int(len(train)),
            "local_weight": 0.0,
            "weights": weights,
            "estimator": "global_mean",
        }
    local = float(np.average(y, weights=weights))
    n_eff = _n_eff(weights)
    same = _col_str(train, "material_class") == str(query.get("material_class") or "")
    if same.any():
        prior = float(y[same].mean())
        estimator = "shrinkage"
        n_support = int(same.sum())
    else:
        prior = float(y.mean())
        estimator = "shrinkage_global_prior"
        n_support = int(len(train))
    mean = (n_eff * local + N0 * prior) / (n_eff + N0)
    local_weight = n_eff / (n_eff + N0)
    return {
        "mean": float(np.clip(mean, 0, 100)),
        "local": float(np.clip(local, 0, 100)),
        "prior": float(np.clip(prior, 0, 100)),
        "n_eff": n_eff,
        "n_support": n_support,
        "local_weight": float(local_weight),
        "weights": weights,
        "estimator": estimator,
    }


def lopo_shrinkage_predictions(frame: pd.DataFrame) -> np.ndarray:
    pred = np.empty(len(frame), dtype=float)
    y = frame["viability_pct"].astype(float)
    for study in frame["study_id"].unique():
        train_mask = frame["study_id"] != study
        train = frame.loc[train_mask]
        for idx in frame.index[~train_mask]:
            row = frame.loc[idx]
            query = {
                "material_class": row.get("material_class"),
                "cell_type": row.get("cell_type"),
                "growth_factor": "none"
                if pd.isna(row.get("growth_factor"))
                else row.get("growth_factor"),
                "stiffness_kpa": None
                if pd.isna(row.get("stiffness_kpa"))
                else float(row.get("stiffness_kpa")),
                "culture_time_days": None
                if pd.isna(row.get("culture_time_days"))
                else float(row.get("culture_time_days")),
            }
            est = shrinkage_estimate(query, train)
            pred[frame.index.get_loc(idx)] = float(y[train_mask].mean()) if est["mean"] is None else est["mean"]
    return pred


def knob_deltas(query: dict, train: pd.DataFrame) -> list[dict]:
    """How much each knob pulled the estimate away from the ablated query."""
    base = shrinkage_estimate(query, train)
    if base["mean"] is None:
        return []
    full = base["mean"]
    out = []
    ablations = [
        ("material_class", {**query, "material_class": "__none__"}, "Hydrogel"),
        ("stiffness_kpa", {**query, "stiffness_kpa": None}, "Stiffness"),
        ("cell_type", {**query, "cell_type": ""}, "Cell type"),
        ("growth_factor", {**query, "growth_factor": "none"}, "Growth factor"),
        ("culture_time_days", {**query, "culture_time_days": None}, "Culture time"),
    ]
    # Don't report GF if the query is already none (ablation is a no-op).
    for key, ablated, label in ablations:
        if key == "growth_factor" and (query.get("growth_factor") or "none") == "none":
            other = shrinkage_estimate({**query, "growth_factor": "TGF_b3"}, train)
            out.append(
                {
                    "feature": label,
                    "delta": round(float(other["mean"] - full), 2),
                    "note": "turn TGF-β3 on to see this pull",
                    "hypothetical": True,
                }
            )
            continue
        other = shrinkage_estimate(ablated, train)
        if other["mean"] is None:
            continue
        out.append(
            {
                "feature": label,
                "delta": round(float(full - other["mean"]), 2),
                "note": "pull vs this knob ignored",
                "hypothetical": False,
            }
        )
    return out

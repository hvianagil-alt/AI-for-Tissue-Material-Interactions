"""Honest MVP metric: leave-one-paper-out on numeric viability only.

The Streamlit holdout R² is mostly simulated data. This script is the number
the product has to beat: dummy mean, grouped by study_id, native live/dead %.

Ridge is reported for honesty. The deployed estimator is the LOPO winner
among dummy and material-class mean — Ridge overfits this table.
"""

from __future__ import annotations

import json

import numpy as np
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.dummy import DummyRegressor
from sklearn.impute import SimpleImputer
from sklearn.linear_model import Ridge
from sklearn.metrics import mean_absolute_error, r2_score
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler

from tissuelab.db import connect
from tissuelab.paths import DB_PATH, HONEST_METRICS_PATH

FEATURES_NUM = ["stiffness_kpa", "polymer_concentration_wt_pct", "culture_time_days"]
FEATURES_CAT = ["material_class", "cell_type"]


def load_viability(path=DB_PATH) -> pd.DataFrame:
    conn = connect(path)
    frame = pd.read_sql_query("SELECT * FROM v_model_viability", conn)
    conn.close()
    return frame


def _pipe(model):
    numeric = Pipeline(
        [
            ("impute", SimpleImputer(strategy="median", keep_empty_features=True)),
            ("scale", StandardScaler()),
        ]
    )
    categorical = Pipeline(
        [
            ("impute", SimpleImputer(strategy="most_frequent")),
            ("onehot", OneHotEncoder(handle_unknown="ignore")),
        ]
    )
    prep = ColumnTransformer(
        [("num", numeric, FEATURES_NUM), ("cat", categorical, FEATURES_CAT)]
    )
    return Pipeline([("prep", prep), ("model", model)])


def _lopo_group_mean(frame: pd.DataFrame, y: pd.Series, group_col: str) -> np.ndarray:
    pred = np.empty(len(frame), dtype=float)
    study_ids = frame["study_id"].to_numpy()
    groups = frame[group_col].fillna("__missing__").astype(str).to_numpy()
    y_vals = y.to_numpy(dtype=float)
    for study in frame["study_id"].unique():
        train = study_ids != study
        test = ~train
        y_train = y_vals[train]
        g_train = groups[train]
        g_test = groups[test]
        global_mean = float(y_train.mean()) if y_train.size else float(y_vals.mean())
        lookup: dict[str, list[float]] = {}
        for group, val in zip(g_train, y_train):
            lookup.setdefault(group, []).append(val)
        means = {group: float(np.mean(vals)) for group, vals in lookup.items()}
        pred[test] = [means.get(group, global_mean) for group in g_test]
    return pred


def _scores(y: pd.Series, pred: np.ndarray) -> dict:
    return {
        "mae": float(mean_absolute_error(y, pred)),
        "r2": float(r2_score(y, pred)),
    }


def leave_one_paper_out(frame: pd.DataFrame) -> dict:
    if frame.empty or frame["study_id"].nunique() < 3:
        return {
            "n_rows": int(len(frame)),
            "n_studies": int(frame["study_id"].nunique()) if not frame.empty else 0,
            "status": "too_few_studies",
            "deployed_estimator": None,
            "message": "Need numeric viability from at least 3 papers before LOPO is defined.",
        }
    y = frame["viability_pct"].astype(float)
    x = frame[FEATURES_NUM + FEATURES_CAT]
    dummy_pred = np.zeros(len(frame))
    ridge_pred = np.zeros(len(frame))
    for study in frame["study_id"].unique():
        train = frame["study_id"] != study
        test = ~train
        if train.sum() < 2 or test.sum() < 1:
            fallback = float(y[train].mean()) if train.any() else float(y.mean())
            dummy_pred[test.values] = fallback
            ridge_pred[test.values] = fallback
            continue
        dummy = DummyRegressor(strategy="mean")
        dummy.fit(x[train], y[train])
        dummy_pred[test.values] = dummy.predict(x[test])
        ridge = _pipe(Ridge(alpha=1.0))
        ridge.fit(x[train], y[train])
        ridge_pred[test.values] = ridge.predict(x[test])
    material_pred = _lopo_group_mean(frame, y, "material_class")
    dummy_lopo = _scores(y, dummy_pred)
    ridge_lopo = _scores(y, ridge_pred)
    material_mean_lopo = _scores(y, material_pred)
    dummy_mae = dummy_lopo["mae"]
    if material_mean_lopo["mae"] < dummy_mae:
        deployed = "material_mean"
        deployed_lopo = material_mean_lopo
    else:
        deployed = "dummy"
        deployed_lopo = dummy_lopo
    report = {
        "n_rows": int(len(frame)),
        "n_studies": int(frame["study_id"].nunique()),
        "studies": sorted(frame["study_id"].unique().tolist()),
        "viability_mean": float(y.mean()),
        "viability_std": float(y.std(ddof=1)) if len(y) > 1 else None,
        "dummy_lopo": dummy_lopo,
        "ridge_lopo": ridge_lopo,
        "material_mean_lopo": material_mean_lopo,
        "deployed_estimator": deployed,
        "deployed_lopo": deployed_lopo,
        "pass_bar": {
            "description": (
                "Deployed tabular estimator LOPO MAE at least 15% below dummy LOPO, "
                "R² > 0, n_studies >= 15. Ridge is reported but not served."
            ),
            "dummy_mae_target_ratio": 0.85,
            "min_studies": 15,
        },
        "notes": [
            "This is the MVP scientific metric on hand-curated live/dead only. Simulated holdout R² is not.",
            "Auto-promoted pmid* rows are excluded from this split.",
            "Do not add unpaired regex hits to inflate n_rows.",
            "Deployed estimator is the LOPO winner among dummy and material-class mean. Ridge overfits this table.",
        ],
        "status": "baseline",
    }
    report["beats_dummy"] = bool(deployed != "dummy" and deployed_lopo["mae"] < dummy_mae)
    report["ridge_beats_dummy"] = bool(ridge_lopo["mae"] < dummy_mae)
    report["mvp_pass"] = bool(
        report["n_studies"] >= 15
        and deployed_lopo["r2"] > 0
        and deployed_lopo["mae"] <= dummy_mae * 0.85
    )
    return report


def run(path=DB_PATH) -> dict:
    frame = load_viability(path)
    report = leave_one_paper_out(frame)
    HONEST_METRICS_PATH.parent.mkdir(parents=True, exist_ok=True)
    HONEST_METRICS_PATH.write_text(json.dumps(report, indent=2))
    return report


def main() -> None:
    report = run()
    print(json.dumps(report, indent=2))
    print(f"Wrote {HONEST_METRICS_PATH}")


if __name__ == "__main__":
    main()

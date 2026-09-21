"""Honest MVP metric: leave-one-paper-out on numeric viability only.

The Streamlit holdout R² is mostly simulated data. This script is the number
the product has to beat: dummy mean, grouped by study_id, native live/dead %.
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


def leave_one_paper_out(frame: pd.DataFrame) -> dict:
    if frame.empty or frame["study_id"].nunique() < 3:
        return {
            "n_rows": int(len(frame)),
            "n_studies": int(frame["study_id"].nunique()) if not frame.empty else 0,
            "status": "too_few_studies",
            "message": "Need numeric viability from at least 3 papers before LOPO is defined.",
        }
    y = frame["viability_pct"].astype(float)
    x = frame[FEATURES_NUM + FEATURES_CAT]
    studies = frame["study_id"].tolist()
    dummy_pred = np.zeros(len(frame))
    ridge_pred = np.zeros(len(frame))
    for study in frame["study_id"].unique():
        train = frame["study_id"] != study
        test = ~train
        if train.sum() < 2 or test.sum() < 1:
            dummy_pred[test.values] = float(y[train].mean()) if train.any() else float(y.mean())
            ridge_pred[test.values] = dummy_pred[test.values]
            continue
        dummy = DummyRegressor(strategy="mean")
        dummy.fit(x[train], y[train])
        dummy_pred[test.values] = dummy.predict(x[test])
        ridge = _pipe(Ridge(alpha=1.0))
        ridge.fit(x[train], y[train])
        ridge_pred[test.values] = ridge.predict(x[test])
    report = {
        "n_rows": int(len(frame)),
        "n_studies": int(frame["study_id"].nunique()),
        "studies": sorted(frame["study_id"].unique().tolist()),
        "viability_mean": float(y.mean()),
        "viability_std": float(y.std(ddof=1)) if len(y) > 1 else None,
        "dummy_lopo": {
            "mae": float(mean_absolute_error(y, dummy_pred)),
            "r2": float(r2_score(y, dummy_pred)),
        },
        "ridge_lopo": {
            "mae": float(mean_absolute_error(y, ridge_pred)),
            "r2": float(r2_score(y, ridge_pred)),
        },
        "pass_bar": {
            "description": "Ridge LOPO MAE at least 15% below dummy LOPO, R² > 0, n_studies >= 15.",
            "dummy_mae_target_ratio": 0.85,
            "min_studies": 15,
        },
        "notes": [
            "This is the MVP scientific metric on hand-curated live/dead only. Simulated holdout R² is not.",
            "Auto-promoted pmid* rows are excluded from this split.",
            "Do not add unpaired regex hits to inflate n_rows.",
        ],
        "status": "baseline",
    }
    dummy_mae = report["dummy_lopo"]["mae"]
    ridge_mae = report["ridge_lopo"]["mae"]
    report["beats_dummy"] = bool(ridge_mae < dummy_mae)
    report["mvp_pass"] = bool(
        report["n_studies"] >= 15
        and report["ridge_lopo"]["r2"] > 0
        and ridge_mae <= dummy_mae * 0.85
    )
    _ = studies
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

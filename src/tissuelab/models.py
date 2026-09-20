"""Baseline models, uncertainty, and nearest-experiment retrieval."""

from __future__ import annotations

from dataclasses import dataclass, field

import numpy as np
import pandas as pd
from sklearn.dummy import DummyRegressor
from sklearn.ensemble import RandomForestRegressor
from sklearn.linear_model import Ridge
from sklearn.metrics import mean_absolute_error, r2_score
from sklearn.model_selection import train_test_split
from sklearn.multioutput import MultiOutputRegressor
from sklearn.neighbors import NearestNeighbors
from sklearn.pipeline import Pipeline
from xgboost import XGBRegressor

from tissuelab.features import build_preprocessor, split_xy
from tissuelab.schema import FEATURE_COLUMNS, TARGETS

MODEL_SPECS = {
    "dummy_mean": lambda: DummyRegressor(strategy="mean"),
    "ridge": lambda: Ridge(alpha=1.0),
    "random_forest": lambda: RandomForestRegressor(
        n_estimators=250,
        min_samples_leaf=2,
        random_state=42,
        n_jobs=-1,
    ),
    "xgboost": lambda: MultiOutputRegressor(
        XGBRegressor(
            n_estimators=280,
            max_depth=4,
            learning_rate=0.06,
            subsample=0.85,
            colsample_bytree=0.85,
            min_child_weight=3,
            objective="reg:squarederror",
            random_state=42,
            n_jobs=1,
        )
    ),
}


@dataclass
class FittedModel:
    name: str
    pipeline: Pipeline
    metrics: dict[str, dict[str, float]]


@dataclass
class TissueInteractionModel:
    point_model: Pipeline
    quantile_low: dict[str, Pipeline]
    quantile_high: dict[str, Pipeline]
    neighbor_features: np.ndarray
    neighbor_frame: pd.DataFrame
    feature_names: list[str]
    importances: list[dict]
    metrics: dict = field(default_factory=dict)
    baselines: dict = field(default_factory=dict)

    def predict_frame(self, frame: pd.DataFrame) -> pd.DataFrame:
        means = self.point_model.predict(frame[FEATURE_COLUMNS])
        means = np.asarray(means, dtype=float)
        result = pd.DataFrame(means, columns=TARGETS, index=frame.index)
        for target in TARGETS:
            result[f"{target}_low"] = self.quantile_low[target].predict(frame[FEATURE_COLUMNS])
            result[f"{target}_high"] = self.quantile_high[target].predict(frame[FEATURE_COLUMNS])
            result[f"{target}_low"] = np.minimum(result[f"{target}_low"], result[target])
            result[f"{target}_high"] = np.maximum(result[f"{target}_high"], result[target])
            result[target] = result[target].clip(0, 100)
            result[f"{target}_low"] = result[f"{target}_low"].clip(0, 100)
            result[f"{target}_high"] = result[f"{target}_high"].clip(0, 100)
        return result

    def similar_experiments(self, frame: pd.DataFrame, k: int = 5) -> list[list[dict]]:
        encoded = self.point_model.named_steps["prep"].transform(frame[FEATURE_COLUMNS])
        encoded = np.asarray(encoded.todense() if hasattr(encoded, "todense") else encoded)
        nn = NearestNeighbors(n_neighbors=min(k, len(self.neighbor_features)))
        nn.fit(self.neighbor_features)
        distances, indices = nn.kneighbors(encoded)
        results: list[list[dict]] = []
        keep = [
            "record_id",
            "source",
            "citation",
            "doi",
            "material_class",
            "stiffness_kpa",
            "growth_factor",
            "culture_time_days",
            *TARGETS,
        ]
        for dist_row, idx_row in zip(distances, indices):
            hits = []
            for dist, idx in zip(dist_row, idx_row):
                row = self.neighbor_frame.iloc[int(idx)]
                item = {key: _jsonable(row[key]) for key in keep if key in row}
                item["distance"] = float(dist)
                hits.append(item)
            results.append(hits)
        return results


def _jsonable(value):
    if pd.isna(value):
        return None
    if isinstance(value, (np.floating, np.integer)):
        return float(value) if isinstance(value, np.floating) else int(value)
    return value


def _evaluate(y_true: pd.DataFrame, y_pred: np.ndarray) -> dict[str, dict[str, float]]:
    y_pred = np.asarray(y_pred)
    metrics: dict[str, dict[str, float]] = {}
    for i, target in enumerate(TARGETS):
        metrics[target] = {
            "mae": float(mean_absolute_error(y_true[target], y_pred[:, i])),
            "r2": float(r2_score(y_true[target], y_pred[:, i])),
        }
    metrics["overall"] = {
        "mae": float(np.mean([metrics[t]["mae"] for t in TARGETS])),
        "r2": float(np.mean([metrics[t]["r2"] for t in TARGETS])),
    }
    return metrics


def evaluate_baselines(frame: pd.DataFrame, seed: int = 42) -> dict:
    x, y = split_xy(frame)
    x_train, x_test, y_train, y_test = train_test_split(x, y, test_size=0.2, random_state=seed)
    report = {}
    for name, factory in MODEL_SPECS.items():
        pipe = Pipeline([("prep", build_preprocessor()), ("model", factory())])
        pipe.fit(x_train, y_train)
        pred = pipe.predict(x_test)
        report[name] = _evaluate(y_test, pred)
    literature = frame[frame["source"] == "literature"]
    if len(literature) >= 5:
        # Train on simulated only, test on literature — the honest generalisation check.
        sim = frame[frame["source"] != "literature"]
        if len(sim) >= 20:
            pipe = Pipeline([("prep", build_preprocessor()), ("model", MODEL_SPECS["xgboost"]())])
            xs, ys = split_xy(sim)
            xl, yl = split_xy(literature)
            pipe.fit(xs, ys)
            report["xgboost_sim_to_literature"] = _evaluate(yl, pipe.predict(xl))
    return report


def _quantile_model(alpha: float) -> XGBRegressor:
    # xgboost>=2 quantile objective
    return XGBRegressor(
        n_estimators=220,
        max_depth=3,
        learning_rate=0.07,
        subsample=0.85,
        colsample_bytree=0.85,
        min_child_weight=4,
        objective="reg:quantileerror",
        quantile_alpha=alpha,
        random_state=42,
        n_jobs=-1,
    )


def _feature_names(preprocessor) -> list[str]:
    return list(preprocessor.get_feature_names_out())


def _importances(pipeline: Pipeline, feature_names: list[str], top_k: int = 12) -> list[dict]:
    model = pipeline.named_steps["model"]
    if isinstance(model, MultiOutputRegressor):
        values = np.mean([est.feature_importances_ for est in model.estimators_], axis=0)
    elif hasattr(model, "feature_importances_"):
        values = np.asarray(model.feature_importances_, dtype=float)
        if values.ndim > 1:
            values = values.mean(axis=0)
    else:
        return []
    order = np.argsort(values)[::-1][:top_k]
    return [
        {
            "feature": feature_names[i].replace("num__", "").replace("cat__", ""),
            "importance": float(values[i]),
        }
        for i in order
    ]


def train_tissue_model(frame: pd.DataFrame, seed: int = 42) -> TissueInteractionModel:
    x, y = split_xy(frame)
    x_train, x_test, y_train, y_test = train_test_split(x, y, test_size=0.2, random_state=seed)
    baselines = evaluate_baselines(frame, seed=seed)

    point = Pipeline([("prep", build_preprocessor()), ("model", MODEL_SPECS["xgboost"]())])
    point.fit(x_train, y_train)
    point_metrics = _evaluate(y_test, point.predict(x_test))

    q_low: dict[str, Pipeline] = {}
    q_high: dict[str, Pipeline] = {}
    for target in TARGETS:
        low = Pipeline([("prep", build_preprocessor()), ("model", _quantile_model(0.1))])
        high = Pipeline([("prep", build_preprocessor()), ("model", _quantile_model(0.9))])
        low.fit(x_train, y_train[target])
        high.fit(x_train, y_train[target])
        q_low[target] = low
        q_high[target] = high

    names = _feature_names(point.named_steps["prep"])
    # Refit point and quantile models on all data for deployment.
    deploy = Pipeline([("prep", build_preprocessor()), ("model", MODEL_SPECS["xgboost"]())])
    deploy.fit(x, y)
    for target in TARGETS:
        q_low[target].fit(x, y[target])
        q_high[target].fit(x, y[target])
    encoded = deploy.named_steps["prep"].transform(x)
    encoded = np.asarray(encoded.todense() if hasattr(encoded, "todense") else encoded)

    return TissueInteractionModel(
        point_model=deploy,
        quantile_low=q_low,
        quantile_high=q_high,
        neighbor_features=encoded,
        neighbor_frame=frame.reset_index(drop=True),
        feature_names=names,
        importances=_importances(deploy, names),
        metrics={"xgboost_holdout": point_metrics, "baselines": baselines},
        baselines=baselines,
    )

"""Feature encoding for the hydrogel–chondrocyte tabular model."""

from __future__ import annotations

import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.impute import SimpleImputer
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler

from tissuelab.schema import CATEGORICAL_FEATURES, FEATURE_COLUMNS, NUMERIC_FEATURES, TARGETS


def records_to_frame(records: list[dict]) -> pd.DataFrame:
    frame = pd.DataFrame(records)
    for column in FEATURE_COLUMNS + TARGETS:
        if column not in frame.columns:
            frame[column] = None
    return frame


def build_preprocessor() -> ColumnTransformer:
    numeric = Pipeline(
        steps=[
            ("impute", SimpleImputer(strategy="median")),
            ("scale", StandardScaler()),
        ]
    )
    categorical = Pipeline(
        steps=[
            ("impute", SimpleImputer(strategy="most_frequent")),
            ("onehot", OneHotEncoder(handle_unknown="ignore")),
        ]
    )
    return ColumnTransformer(
        transformers=[
            ("num", numeric, NUMERIC_FEATURES),
            ("cat", categorical, CATEGORICAL_FEATURES),
        ]
    )


def split_xy(frame: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    return frame[FEATURE_COLUMNS].copy(), frame[TARGETS].copy()

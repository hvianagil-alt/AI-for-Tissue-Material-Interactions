"""Prediction helper used by the API and Streamlit app."""

from __future__ import annotations

import pandas as pd

from tissuelab.models import TissueInteractionModel
from tissuelab.protocol import protocol_from_row
from tissuelab.schema import FEATURE_COLUMNS, TARGETS, DesignInput, PredictionResult


def design_to_frame(design: DesignInput | dict) -> pd.DataFrame:
    data = design.model_dump() if isinstance(design, DesignInput) else dict(design)
    return pd.DataFrame([{key: data[key] for key in FEATURE_COLUMNS}])


def predict_design(model: TissueInteractionModel, design: DesignInput | dict) -> PredictionResult:
    frame = design_to_frame(design)
    pred = model.predict_frame(frame).iloc[0]
    similar = model.similar_experiments(frame, k=5)[0]
    outcomes = {
        target: {
            "mean": round(float(pred[target]), 1),
            "low": round(float(pred[f"{target}_low"]), 1),
            "high": round(float(pred[f"{target}_high"]), 1),
        }
        for target in TARGETS
    }
    notes = []
    if outcomes["viability_pct"]["high"] - outcomes["viability_pct"]["low"] > 20:
        notes.append("Wide viability interval — treat as exploratory, not a go/no-go decision.")
    if frame.iloc[0]["material_class"] in {"PEG", "PEG_dextran"} and frame.iloc[0]["has_adhesion_ligand"] < 0.3:
        notes.append("Bioinert PEG-like networks often need adhesive ligands or MMP-degradable crosslinks.")
    if frame.iloc[0]["culture_model"] == "2D":
        notes.append("2D culture typically inflates proliferation and suppresses chondrogenesis.")
    return PredictionResult(
        outcomes=outcomes,
        influential_features=model.importances[:8],
        similar_experiments=similar,
        protocol=protocol_from_row(frame.iloc[0]),
        notes=notes,
    )

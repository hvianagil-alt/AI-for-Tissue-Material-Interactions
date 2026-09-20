"""Minimal TissueLab prediction API."""

from __future__ import annotations

import sys
from functools import lru_cache
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from fastapi import FastAPI
from pydantic import BaseModel, Field

from tissuelab.inverse import inverse_design
from tissuelab.predict import predict_design
from tissuelab.recommend import recommend_experiments
from tissuelab.schema import DesignInput, TARGETS
from tissuelab.train import load_model, main as train_main
from tissuelab.paths import MODEL_PATH

app = FastAPI(title="TissueLab AI", version="0.1.0")


@lru_cache(maxsize=1)
def get_model():
    if not MODEL_PATH.exists():
        train_main()
    return load_model()


class InverseRequest(BaseModel):
    viability_pct: float = 90
    proliferation_score: float = 55
    differentiation_score: float = 80
    ecm_deposition_score: float = 80
    material_class: list[str] | None = None
    stiffness_kpa_max: float | None = 50
    top_k: int = 5


class RecommendRequest(BaseModel):
    objective: str = Field(default="ecm_deposition_score")
    n: int = 5


@app.get("/health")
def health():
    return {"status": "ok", "mvp": "hydrogel-chondrocyte"}


@app.post("/predict")
def predict(design: DesignInput):
    result = predict_design(get_model(), design)
    return result.model_dump()


@app.post("/inverse")
def inverse(req: InverseRequest):
    targets = {key: getattr(req, key) for key in TARGETS}
    constraints = {}
    if req.material_class:
        constraints["material_class"] = req.material_class
    if req.stiffness_kpa_max is not None:
        constraints["stiffness_kpa_max"] = req.stiffness_kpa_max
    ranked = inverse_design(get_model(), targets=targets, constraints=constraints, top_k=req.top_k)
    return ranked.to_dict(orient="records")


@app.post("/recommend")
def recommend(req: RecommendRequest):
    ranked = recommend_experiments(get_model(), objective=req.objective, n=req.n)
    return ranked.to_dict(orient="records")

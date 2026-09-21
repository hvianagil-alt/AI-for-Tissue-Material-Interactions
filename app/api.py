"""Minimal TissueLab prediction API."""

from __future__ import annotations

import sys
from functools import lru_cache
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from fastapi import FastAPI, HTTPException, Query
from fastapi.responses import HTMLResponse
from pydantic import BaseModel, Field

from tissuelab.inverse import inverse_design
from tissuelab.literature_model import predict_literature_viability
from tissuelab.paths import MODEL_PATH
from tissuelab.predict import predict_design
from tissuelab.recommend import recommend_experiments
from tissuelab.schema import DesignInput, TARGETS
from tissuelab.train import load_model

from app.ui import CELL_TYPES, GROWTH_FACTORS, MATERIALS, render_predict_page

app = FastAPI(title="TissueLab AI", version="0.1.0")


@lru_cache(maxsize=1)
def get_model():
    if not MODEL_PATH.exists():
        return None
    return load_model()


def require_simulator():
    model = get_model()
    if model is None:
        raise HTTPException(
            status_code=503,
            detail="Simulator model not on disk. POST /predict still returns literature viability.",
        )
    return model


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


@app.get("/", response_class=HTMLResponse)
def home(
    material_class: str = Query(default="GelMA"),
    stiffness_kpa: float = Query(default=25.0),
    cell_type: str = Query(default="articular_chondrocyte"),
    growth_factor: str = Query(default="none"),
    culture_time_days: int = Query(default=14),
):
    if material_class not in MATERIALS:
        material_class = "GelMA"
    if cell_type not in CELL_TYPES:
        cell_type = "articular_chondrocyte"
    if growth_factor not in GROWTH_FACTORS:
        growth_factor = "none"
    stiffness_kpa = min(200.0, max(0.5, float(stiffness_kpa)))
    culture_time_days = min(42, max(1, int(culture_time_days)))
    lit = predict_literature_viability(
        {
            "material_class": material_class,
            "stiffness_kpa": stiffness_kpa,
            "cell_type": cell_type,
            "growth_factor": growth_factor,
            "culture_time_days": culture_time_days,
        }
    )
    return render_predict_page(
        material_class=material_class,
        stiffness_kpa=stiffness_kpa,
        cell_type=cell_type,
        growth_factor=growth_factor,
        culture_time_days=culture_time_days,
        literature=lit,
    )


@app.get("/health")
def health():
    return {
        "status": "ok",
        "mvp": "hydrogel-chondrocyte",
        "simulator_available": MODEL_PATH.exists(),
    }


@app.post("/predict")
def predict(design: DesignInput):
    lit = predict_literature_viability(design.model_dump())
    model = get_model()
    if model is None:
        return {
            "literature_viability": lit,
            "simulator_available": False,
            "notes": [
                "Simulator joblib not on disk. Literature viability is the scientific output.",
            ],
        }
    result = predict_design(model, design)
    payload = result.model_dump()
    payload["literature_viability"] = lit
    payload["simulator_available"] = True
    return payload


@app.post("/inverse")
def inverse(req: InverseRequest):
    targets = {key: getattr(req, key) for key in TARGETS}
    constraints = {}
    if req.material_class:
        constraints["material_class"] = req.material_class
    if req.stiffness_kpa_max is not None:
        constraints["stiffness_kpa_max"] = req.stiffness_kpa_max
    ranked = inverse_design(require_simulator(), targets=targets, constraints=constraints, top_k=req.top_k)
    return ranked.to_dict(orient="records")


@app.post("/recommend")
def recommend(req: RecommendRequest):
    ranked = recommend_experiments(require_simulator(), objective=req.objective, n=req.n)
    return ranked.to_dict(orient="records")

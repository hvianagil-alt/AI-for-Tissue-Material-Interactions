"""Minimal TissueLab prediction API."""

from __future__ import annotations

import csv
import io
import sys
from functools import lru_cache
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from fastapi import FastAPI, HTTPException, Query
from fastapi.responses import HTMLResponse, Response
from pydantic import BaseModel, Field

from tissuelab.inverse import inverse_design
from tissuelab.lit_search import search_question
from tissuelab.literature_model import list_viability_evidence, predict_literature_viability
from tissuelab.paths import MODEL_PATH
from tissuelab.predict import predict_design
from tissuelab.protocol_finder import find_protocol
from tissuelab.recommend import recommend_experiments
from tissuelab.schema import DesignInput, TARGETS
from tissuelab.train import load_model

from app.protocol_ui import render_protocol_page
from app.ui import CELL_TYPES, GROWTH_FACTORS, MATERIALS, render_compare_page, render_predict_page, render_table_page

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


def _clamp_design(material_class: str, stiffness_kpa: float, cell_type: str, growth_factor: str, culture_time_days: int):
    if material_class not in MATERIALS:
        material_class = "GelMA"
    if cell_type not in CELL_TYPES:
        cell_type = "articular_chondrocyte"
    if growth_factor not in GROWTH_FACTORS:
        growth_factor = "none"
    stiffness_kpa = min(200.0, max(0.5, float(stiffness_kpa)))
    culture_time_days = min(42, max(1, int(culture_time_days)))
    return {
        "material_class": material_class,
        "stiffness_kpa": stiffness_kpa,
        "cell_type": cell_type,
        "growth_factor": growth_factor,
        "culture_time_days": culture_time_days,
    }


@app.get("/", response_class=HTMLResponse)
def home(
    cell_type: str = Query(default="articular_chondrocyte"),
    goal: str = Query(default="alive"),
    how: str = Query(default="encapsulate"),
    tgf: str = Query(default="either"),
    stock: str = Query(default="any"),
    live: bool = Query(default=False),
    lang: str = Query(default="en"),
):
    if cell_type not in CELL_TYPES:
        cell_type = "articular_chondrocyte"
    result = find_protocol(
        cell_type=cell_type,
        goal=goal,
        how=how,
        tgf=tgf,
        stock=stock,
        lang=lang,
    )
    gel = result["protocol"]["material_class"]
    search = search_question(cell_type, goal, gel, live=bool(live))
    return render_protocol_page(result=result, search=search, lang=lang, live=bool(live))


@app.get("/lookup", response_class=HTMLResponse)
def lookup(
    material_class: str = Query(default="GelMA"),
    stiffness_kpa: float = Query(default=25.0),
    cell_type: str = Query(default="articular_chondrocyte"),
    growth_factor: str = Query(default="none"),
    culture_time_days: int = Query(default=14),
    lang: str = Query(default="en"),
):
    design = _clamp_design(material_class, stiffness_kpa, cell_type, growth_factor, int(culture_time_days))
    lit = predict_literature_viability(design)
    return render_predict_page(lang=lang, literature=lit, **design)


@app.get("/table", response_class=HTMLResponse)
def table(
    material_class: str | None = Query(default=None),
    lang: str = Query(default="en"),
):
    rows = list_viability_evidence()
    all_materials = sorted({row["material_class"] for row in rows if row.get("material_class")})
    want = (material_class or "").strip()
    filtered = rows
    if want:
        filtered = [row for row in rows if row.get("material_class") == want]
    return render_table_page(filtered, want or None, lang=lang, all_materials=all_materials)


@app.get("/export.csv")
def export_csv():
    rows = list_viability_evidence()
    buf = io.StringIO()
    fields = [
        "year",
        "study_id",
        "citation",
        "doi",
        "material_class",
        "stiffness_kpa",
        "cell_type",
        "species",
        "growth_factor",
        "culture_time_days",
        "viability_pct",
        "viability_sd",
        "qualitative_label",
        "evidence",
    ]
    writer = csv.DictWriter(buf, fieldnames=fields, extrasaction="ignore")
    writer.writeheader()
    for row in rows:
        writer.writerow(row)
    return Response(
        content=buf.getvalue(),
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=tissuelab_viability.csv"},
    )


@app.get("/compare", response_class=HTMLResponse)
def compare(
    a_material: str = Query(default="GelMA"),
    a_kpa: float = Query(default=25.0),
    a_gf: str = Query(default="none"),
    b_material: str = Query(default="fibrin"),
    b_kpa: float = Query(default=25.0),
    b_gf: str = Query(default="TGF_b3"),
    lang: str = Query(default="en"),
):
    left_design = _clamp_design(a_material, a_kpa, "articular_chondrocyte", a_gf, 14)
    right_design = _clamp_design(b_material, b_kpa, "articular_chondrocyte", b_gf, 14)
    return render_compare_page(
        predict_literature_viability(left_design),
        predict_literature_viability(right_design),
        left_design,
        right_design,
        lang=lang,
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

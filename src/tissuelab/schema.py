"""Canonical schema for a material–tissue experimental record.

The first MVP is deliberately narrow:

    hydrogel properties + chondrocyte context → viability / proliferation /
    differentiation / ECM deposition
"""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field

MaterialClass = Literal[
    "GelMA",
    "fibrin",
    "silk_fibrin",
    "PEG",
    "PEG_dextran",
    "alginate",
    "HA",
    "collagen",
    "agarose",
    "chitosan_HA",
    "gelatin_alginate",
]

Crosslinking = Literal["photocrosslink", "ionic", "enzymatic", "thermal", "chemical"]
CellType = Literal["articular_chondrocyte", "MSC"]
Species = Literal["human", "bovine", "porcine", "rabbit"]
CultureModel = Literal["3D_encapsulation", "3D_bioprint", "2D"]
GrowthFactor = Literal["none", "TGF_b1", "TGF_b3"]
SurfaceChemistry = Literal["native", "RGD", "MMP_degradable", "none"]
RecordSource = Literal["literature", "simulated_literature_informed"]

CATEGORICAL_FEATURES = [
    "material_class",
    "crosslinking",
    "cell_type",
    "species",
    "culture_model",
    "growth_factor",
    "surface_chemistry",
]

NUMERIC_FEATURES = [
    "polymer_concentration_wt_pct",
    "stiffness_kpa",
    "porosity_pct",
    "degradation_half_life_days",
    "culture_time_days",
    "cell_density_million_per_ml",
    "passage",
    "has_adhesion_ligand",
]

TARGETS = [
    "viability_pct",
    "proliferation_score",
    "differentiation_score",
    "ecm_deposition_score",
]

FEATURE_COLUMNS = CATEGORICAL_FEATURES + NUMERIC_FEATURES


class MaterialInput(BaseModel):
    material_class: MaterialClass
    crosslinking: Crosslinking = "photocrosslink"
    polymer_concentration_wt_pct: float = Field(ge=0.1, le=30)
    stiffness_kpa: float = Field(ge=0.1, le=800)
    porosity_pct: float = Field(ge=20, le=99)
    degradation_half_life_days: float = Field(ge=0.5, le=365)
    surface_chemistry: SurfaceChemistry = "native"
    has_adhesion_ligand: float = Field(default=0.0, ge=0.0, le=1.0)


class BiologicalContext(BaseModel):
    tissue: Literal["cartilage"] = "cartilage"
    cell_type: CellType = "articular_chondrocyte"
    species: Species = "human"
    culture_model: CultureModel = "3D_encapsulation"
    growth_factor: GrowthFactor = "none"
    culture_time_days: float = Field(default=14, ge=1, le=90)
    cell_density_million_per_ml: float = Field(default=5.0, ge=0.1, le=50)
    passage: int = Field(default=2, ge=0, le=8)


class DesignInput(MaterialInput, BiologicalContext):
    """Combined researcher-facing input for a prediction or inverse-design query."""


class PredictedOutcomes(BaseModel):
    viability_pct: float
    proliferation_score: float
    differentiation_score: float
    ecm_deposition_score: float


class OutcomeInterval(BaseModel):
    mean: float
    low: float
    high: float


class PredictionResult(BaseModel):
    outcomes: dict[str, OutcomeInterval]
    influential_features: list[dict]
    similar_experiments: list[dict] = Field(default_factory=list)
    protocol: str = ""
    notes: list[str] = Field(default_factory=list)


class ExperimentRecord(DesignInput):
    record_id: str
    source: RecordSource
    citation: str | None = None
    doi: str | None = None
    year: int | None = None
    notes: str | None = None
    imputed_fields: list[str] = Field(default_factory=list)
    viability_pct: float | None = None
    proliferation_score: float | None = None
    differentiation_score: float | None = None
    ecm_deposition_score: float | None = None

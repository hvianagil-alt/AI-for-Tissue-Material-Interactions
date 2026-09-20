"""Inverse design: desired tissue response → candidate hydrogel designs."""

from __future__ import annotations

import numpy as np
import pandas as pd

from tissuelab.models import TissueInteractionModel
from tissuelab.schema import TARGETS
from tissuelab.simulator import sample_designs

DEFAULT_WEIGHTS = {
    "viability_pct": 0.2,
    "proliferation_score": 0.1,
    "differentiation_score": 0.3,
    "ecm_deposition_score": 0.4,
}


def _apply_constraints(frame: pd.DataFrame, constraints: dict | None) -> pd.DataFrame:
    if not constraints:
        return frame
    out = frame
    if materials := constraints.get("material_class"):
        out = out[out["material_class"].isin(materials)]
    if "stiffness_kpa_max" in constraints:
        out = out[out["stiffness_kpa"] <= float(constraints["stiffness_kpa_max"])]
    if "stiffness_kpa_min" in constraints:
        out = out[out["stiffness_kpa"] >= float(constraints["stiffness_kpa_min"])]
    if "growth_factor" in constraints:
        out = out[out["growth_factor"] == constraints["growth_factor"]]
    if "species" in constraints:
        out = out[out["species"] == constraints["species"]]
    if "culture_model" in constraints:
        out = out[out["culture_model"] == constraints["culture_model"]]
    return out.reset_index(drop=True)


def inverse_design(
    model: TissueInteractionModel,
    targets: dict[str, float],
    constraints: dict | None = None,
    n_candidates: int = 2500,
    top_k: int = 5,
    seed: int = 7,
    weights: dict[str, float] | None = None,
) -> pd.DataFrame:
    """Score randomly sampled feasible designs against a desired outcome vector."""
    rng = np.random.default_rng(seed)
    designs = sample_designs(n_candidates, rng)
    constraints = dict(constraints or {})
    if "culture_model" not in constraints:
        designs = designs[designs["culture_model"] != "2D"].reset_index(drop=True)
    designs = _apply_constraints(designs, constraints)
    if designs.empty:
        return designs

    pred = model.predict_frame(designs)
    weights = weights or DEFAULT_WEIGHTS
    error = np.zeros(len(designs))
    uncertainty = np.zeros(len(designs))
    for target, weight in weights.items():
        desired = float(targets.get(target, 70))
        error += weight * (pred[target] - desired) ** 2
        uncertainty += weight * (pred[f"{target}_high"] - pred[f"{target}_low"])

    # Soft prior: cartilage hydrogels in the literature cluster near ~10–35 kPa.
    physio = np.exp(
        -0.5
        * ((np.log(designs["stiffness_kpa"].clip(lower=0.5)) - np.log(25.0)) / 0.9) ** 2
    )
    score = -np.sqrt(error) - 0.04 * uncertainty + 3.5 * physio
    ranked = designs.copy()
    for target in TARGETS:
        ranked[f"pred_{target}"] = pred[target].to_numpy()
        ranked[f"pred_{target}_low"] = pred[f"{target}_low"].to_numpy()
        ranked[f"pred_{target}_high"] = pred[f"{target}_high"].to_numpy()
    ranked["match_score"] = score
    ranked["uncertainty"] = uncertainty
    ranked = ranked.sort_values("match_score", ascending=False).head(top_k).reset_index(drop=True)
    ranked["rank"] = np.arange(1, len(ranked) + 1)
    return ranked


def candidate_rationale(row: pd.Series) -> str:
    bits = [
        f"{row['material_class']} at {row['stiffness_kpa']:.1f} kPa",
        f"{row['polymer_concentration_wt_pct']:.1f} wt%",
        f"{row['culture_model'].replace('_', ' ')} for {int(row['culture_time_days'])} days",
    ]
    if row["growth_factor"] != "none":
        bits.append(f"with {row['growth_factor'].replace('_', '-')}")
    if row["surface_chemistry"] == "MMP_degradable":
        bits.append("MMP-degradable network to allow matrix distribution")
    if row["has_adhesion_ligand"] >= 0.7:
        bits.append("adhesive ligands present")
    return "; ".join(bits)

"""Recommend the next hydrogel–chondrocyte experiments.

Acquisition is a simple expected-improvement / UCB hybrid over a sampled
design space, using quantile-model uncertainty. This is the closed-loop
piece of the MVP — not a full lab-in-the-loop system.
"""

from __future__ import annotations

import numpy as np
import pandas as pd

from tissuelab.models import TissueInteractionModel
from tissuelab.schema import TARGETS
from tissuelab.simulator import sample_designs

OBJECTIVE_LABELS = {
    "viability_pct": "cell viability",
    "proliferation_score": "proliferation",
    "differentiation_score": "chondrogenic differentiation",
    "ecm_deposition_score": "ECM deposition",
}


def recommend_experiments(
    model: TissueInteractionModel,
    objective: str = "ecm_deposition_score",
    n: int = 5,
    n_candidates: int = 2000,
    kappa: float = 1.15,
    seed: int = 11,
    best_so_far: float | None = None,
) -> pd.DataFrame:
    if objective not in TARGETS:
        raise ValueError(f"Unknown objective {objective}")

    rng = np.random.default_rng(seed)
    designs = sample_designs(n_candidates, rng)
    # Keep recommendations in the experimentally common 3D setting.
    designs = designs[designs["culture_model"] != "2D"].reset_index(drop=True)
    pred = model.predict_frame(designs)
    mean = pred[objective].to_numpy()
    std = ((pred[f"{objective}_high"] - pred[f"{objective}_low"]) / 3.2).to_numpy()
    std = np.clip(std, 0.5, None)
    incumbent = best_so_far if best_so_far is not None else float(np.quantile(mean, 0.8))
    z = (mean - incumbent) / std
    # Gaussian EI approximation
    from math import erf, exp, sqrt

    def _phi(v: np.ndarray) -> np.ndarray:
        return np.exp(-0.5 * v**2) / np.sqrt(2 * np.pi)

    def _psi(v: np.ndarray) -> np.ndarray:
        return 0.5 * (1.0 + np.vectorize(lambda x: erf(x / sqrt(2)))(v))

    ei = (mean - incumbent) * _psi(z) + std * _phi(z)
    ucb = mean + kappa * std
    acquisition = 0.65 * ei + 0.35 * (ucb - incumbent)

    ranked = designs.copy()
    for target in TARGETS:
        ranked[f"pred_{target}"] = pred[target].to_numpy()
        ranked[f"pred_{target}_low"] = pred[f"{target}_low"].to_numpy()
        ranked[f"pred_{target}_high"] = pred[f"{target}_high"].to_numpy()
    ranked["acquisition"] = acquisition
    ranked["expected_improvement"] = ei
    ranked["uncertainty"] = std
    ranked["objective"] = objective
    ranked = ranked.sort_values("acquisition", ascending=False).head(n).reset_index(drop=True)
    ranked["rank"] = np.arange(1, len(ranked) + 1)
    return ranked


def recommendation_reason(row: pd.Series) -> str:
    objective = OBJECTIVE_LABELS.get(row["objective"], row["objective"])
    return (
        f"High expected improvement on {objective} "
        f"(pred {row[f'pred_{row['objective']}']:.0f}, "
        f"uncertainty ±{row['uncertainty']:.1f}). "
        f"{row['material_class']} @ {row['stiffness_kpa']:.1f} kPa, "
        f"{row['growth_factor']} growth factor, {int(row['culture_time_days'])} d culture."
    )

"""Literature-informed simulator for hydrogel–chondrocyte outcomes.

This is NOT a mechanistic tissue model. It encodes directional relationships
repeatedly reported for 3D chondrocyte-laden hydrogels so the MVP can train a
baseline predictor before a large curated corpus exists.

Relationships encoded (see docs/LANDSCAPE.md for sources):
- Natural adhesive gels (fibrin, GelMA, HA) keep high viability; bioinert dense
  PEG-dextran viability collapses with stiffness (Bachmann 2020).
- Chondrogenic phenotype / ECM often peaks near ~20–35 kPa in 3D protein gels
  (Li 2016; Bachmann 2020), while very soft gels encourage spreading.
- TGF-β3 boosts redifferentiation and ECM.
- MMP-degradable networks improve distributed ECM vs non-degradable PEG
  (Bryant/Anseth; Sridhar 2015).
- Alginate/agarose: low adhesion, round morphology, strong chondrogenic genes.
- 2D culture: high proliferation, poor chondrogenesis.
- Higher passage: more dedifferentiation.
"""

from __future__ import annotations

import math

import numpy as np
import pandas as pd

from tissuelab.schema import FEATURE_COLUMNS, TARGETS

MATERIAL_PRIORS: dict[str, dict] = {
    "GelMA": {
        "viability": 92,
        "adhesion": 0.9,
        "chondrogenic": 0.72,
        "default_xl": "photocrosslink",
        "ligand": 1.0,
    },
    "fibrin": {
        "viability": 95,
        "adhesion": 0.95,
        "chondrogenic": 0.84,
        "default_xl": "enzymatic",
        "ligand": 1.0,
    },
    "silk_fibrin": {
        "viability": 93,
        "adhesion": 0.9,
        "chondrogenic": 0.86,
        "default_xl": "enzymatic",
        "ligand": 1.0,
    },
    "PEG": {
        "viability": 82,
        "adhesion": 0.12,
        "chondrogenic": 0.48,
        "default_xl": "photocrosslink",
        "ligand": 0.0,
    },
    "PEG_dextran": {
        "viability": 58,
        "adhesion": 0.05,
        "chondrogenic": 0.18,
        "default_xl": "chemical",
        "ligand": 0.0,
    },
    "alginate": {
        "viability": 90,
        "adhesion": 0.12,
        "chondrogenic": 0.86,
        "default_xl": "ionic",
        "ligand": 0.0,
    },
    "HA": {
        "viability": 91,
        "adhesion": 0.7,
        "chondrogenic": 0.9,
        "default_xl": "photocrosslink",
        "ligand": 0.7,
    },
    "collagen": {
        "viability": 93,
        "adhesion": 1.0,
        "chondrogenic": 0.62,
        "default_xl": "chemical",
        "ligand": 1.0,
    },
    "agarose": {
        "viability": 88,
        "adhesion": 0.1,
        "chondrogenic": 0.76,
        "default_xl": "thermal",
        "ligand": 0.0,
    },
    "chitosan_HA": {
        "viability": 84,
        "adhesion": 0.55,
        "chondrogenic": 0.7,
        "default_xl": "chemical",
        "ligand": 0.5,
    },
    "gelatin_alginate": {
        "viability": 91,
        "adhesion": 0.82,
        "chondrogenic": 0.74,
        "default_xl": "ionic",
        "ligand": 1.0,
    },
}

MATERIALS = list(MATERIAL_PRIORS)


def _clip(value: float, lo: float = 0.0, hi: float = 100.0) -> float:
    return float(np.clip(value, lo, hi))


def _gauss(x: float, mu: float, sigma: float) -> float:
    return math.exp(-0.5 * ((x - mu) / sigma) ** 2)


def _log_gauss(x: float, mu: float, sigma: float) -> float:
    return math.exp(-0.5 * ((math.log(max(x, 0.2)) - math.log(mu)) / sigma) ** 2)


def sample_designs(n: int, rng: np.random.Generator) -> pd.DataFrame:
    """Sample realistic hydrogel–chondrocyte experimental conditions."""
    rows: list[dict] = []
    for _ in range(n):
        material = str(rng.choice(MATERIALS))
        prior = MATERIAL_PRIORS[material]
        conc = float(np.clip(rng.lognormal(mean=1.6, sigma=0.55), 0.4, 22))
        # Stiffness rises with concentration; material-specific scale.
        stiffness_scale = {
            "PEG": 8.0,
            "PEG_dextran": 4.5,
            "chitosan_HA": 8.0,
            "agarose": 6.0,
            "fibrin": 3.5,
            "silk_fibrin": 4.0,
            "alginate": 4.0,
            "HA": 3.0,
            "GelMA": 2.8,
            "gelatin_alginate": 2.2,
            "collagen": 2.0,
        }[material]
        stiffness = float(np.clip(conc * stiffness_scale * rng.uniform(0.6, 1.5), 0.4, 90))
        if material == "chitosan_HA":
            stiffness = float(np.clip(stiffness * rng.uniform(1.0, 3.0), 1.0, 220))
        if material == "PEG" and rng.random() < 0.12:
            stiffness = float(rng.uniform(80, 500))
        porosity = float(np.clip(96 - 1.6 * conc - 0.04 * min(stiffness, 80) + rng.normal(0, 4), 30, 97))
        if material in {"PEG_dextran", "PEG"} and rng.random() < 0.25:
            stiffness = float(np.clip(stiffness * rng.uniform(1.2, 1.8), 0.4, 120))
            porosity = float(np.clip(porosity - rng.uniform(5, 15), 30, 97))

        degradable = material not in {"agarose", "alginate"} or rng.random() < 0.15
        if material in {"PEG", "PEG_dextran"} and rng.random() < 0.55:
            degradable = False
        if degradable:
            half_life = float(np.clip(rng.lognormal(2.6, 0.55), 3, 90))
            surface = str(rng.choice(["native", "MMP_degradable", "RGD"], p=[0.55, 0.3, 0.15]))
        else:
            half_life = float(np.clip(rng.lognormal(5.2, 0.35), 80, 365))
            surface = str(rng.choice(["none", "native", "RGD"], p=[0.55, 0.25, 0.2]))

        ligand = prior["ligand"]
        if surface == "RGD":
            ligand = 1.0
        elif surface == "none":
            ligand = min(ligand, 0.15)

        growth = str(rng.choice(["none", "TGF_b3", "TGF_b1"], p=[0.5, 0.35, 0.15]))
        culture = str(rng.choice(["3D_encapsulation", "3D_bioprint", "2D"], p=[0.72, 0.18, 0.1]))
        cell_type = str(rng.choice(["articular_chondrocyte", "MSC"], p=[0.78, 0.22]))
        species = str(rng.choice(["human", "bovine", "porcine", "rabbit"], p=[0.5, 0.3, 0.12, 0.08]))
        passage = int(rng.choice([0, 1, 2, 3, 4, 5], p=[0.08, 0.18, 0.38, 0.22, 0.1, 0.04]))
        time_days = float(rng.choice([7, 14, 21, 28, 42], p=[0.15, 0.35, 0.3, 0.15, 0.05]))
        density = float(np.clip(rng.lognormal(1.5, 0.7), 0.4, 40))

        rows.append(
            {
                "material_class": material,
                "crosslinking": prior["default_xl"],
                "polymer_concentration_wt_pct": round(conc, 2),
                "stiffness_kpa": round(stiffness, 2),
                "porosity_pct": round(porosity, 1),
                "degradation_half_life_days": round(half_life, 1),
                "surface_chemistry": surface,
                "has_adhesion_ligand": round(float(ligand), 2),
                "cell_type": cell_type,
                "species": species,
                "culture_model": culture,
                "growth_factor": growth,
                "culture_time_days": time_days,
                "cell_density_million_per_ml": round(density, 2),
                "passage": passage,
            }
        )
    return pd.DataFrame(rows)


def simulate_outcomes(row: dict | pd.Series, rng: np.random.Generator | None = None) -> dict:
    """Map a design to four 0–100 biological scores plus optional noise."""
    rng = rng or np.random.default_rng(0)
    material = row["material_class"]
    prior = MATERIAL_PRIORS[material]
    stiffness = float(row["stiffness_kpa"])
    porosity = float(row["porosity_pct"])
    conc = float(row["polymer_concentration_wt_pct"])
    half_life = float(row["degradation_half_life_days"])
    ligand = float(row["has_adhesion_ligand"])
    time_days = float(row["culture_time_days"])
    density = float(row["cell_density_million_per_ml"])
    passage = int(row["passage"])
    culture = row["culture_model"]
    growth = row["growth_factor"]
    cell_type = row["cell_type"]
    surface = row["surface_chemistry"]

    chondro_stiffness = _log_gauss(stiffness, mu=26.0, sigma=0.55)
    soft_spread = _log_gauss(stiffness, mu=2.5, sigma=0.7)
    dense = max(0.0, (70 - porosity) / 50.0) + max(0.0, (conc - 12) / 12.0)

    viability = prior["viability"]
    viability += 6 * ligand
    viability += 0.08 * (porosity - 75)
    viability -= 10 * dense
    if material == "PEG_dextran":
        viability -= 18 * math.log10(stiffness + 1) - 4 * ligand
    if material == "PEG" and ligand < 0.3:
        viability -= 6 + 0.04 * stiffness
    if culture == "2D":
        viability += 4
    viability -= 0.08 * max(time_days - 21, 0)
    viability -= 1.5 * max(passage - 3, 0)
    if density > 25 and porosity < 70:
        viability -= 6

    proliferation = 48 + 18 * prior["adhesion"] + 12 * ligand
    proliferation += 16 * soft_spread
    proliferation -= 14 * chondro_stiffness
    proliferation -= 12 * dense
    if culture == "2D":
        proliferation += 18
    if cell_type == "MSC":
        proliferation += 8
    proliferation -= 0.25 * time_days
    proliferation -= 4 * max(passage - 2, 0)
    if growth != "none":
        proliferation += 4

    differentiation = 100 * prior["chondrogenic"]
    differentiation += 28 * chondro_stiffness
    differentiation -= 16 * soft_spread
    differentiation -= 10 * prior["adhesion"] * soft_spread  # spreading on adhesive soft gels
    if culture == "2D":
        differentiation -= 28
    if growth == "TGF_b3":
        differentiation += 16
    elif growth == "TGF_b1":
        differentiation += 11
    differentiation -= 7 * max(passage - 2, 0)
    if cell_type == "MSC" and growth == "none":
        differentiation -= 14
    if cell_type == "MSC" and growth != "none":
        differentiation += 4
    if density >= 8:
        differentiation += 5
    if surface == "RGD" and stiffness < 8:
        differentiation -= 8  # RGD + soft matrix → spreading / dedifferentiation

    ecm = 0.55 * differentiation + 8 * chondro_stiffness
    ecm += 10 * min(time_days / 21.0, 1.4)
    if 8 <= half_life <= 32:
        ecm += 10
    elif half_life < 5:
        ecm -= 8
    elif half_life > 90:
        ecm -= 12 + 8 * dense
    if surface == "MMP_degradable":
        ecm += 9
    if culture == "2D":
        ecm -= 22
    if growth != "none":
        ecm += 8
    if material in {"HA", "fibrin", "silk_fibrin", "alginate"}:
        ecm += 4

    noise = 3.8
    outcomes = {
        "viability_pct": _clip(viability + rng.normal(0, noise)),
        "proliferation_score": _clip(proliferation + rng.normal(0, noise)),
        "differentiation_score": _clip(differentiation + rng.normal(0, noise)),
        "ecm_deposition_score": _clip(ecm + rng.normal(0, noise)),
    }
    return outcomes


def simulate_dataframe(n: int = 600, seed: int = 42) -> pd.DataFrame:
    rng = np.random.default_rng(seed)
    designs = sample_designs(n, rng)
    outcomes = [simulate_outcomes(row, rng) for row in designs.to_dict(orient="records")]
    out = pd.concat([designs, pd.DataFrame(outcomes)], axis=1)
    out["source"] = "simulated_literature_informed"
    out["citation"] = "TissueLab literature-informed simulator v0.1"
    out["doi"] = None
    out["year"] = 2026
    out["notes"] = "Generated from published directional relationships, not a real experiment."
    out["imputed_fields"] = "[]"
    out["record_id"] = [f"sim-{i:04d}" for i in range(len(out))]
    return out[FEATURE_COLUMNS + TARGETS + ["record_id", "source", "citation", "doi", "year", "notes", "imputed_fields"]]

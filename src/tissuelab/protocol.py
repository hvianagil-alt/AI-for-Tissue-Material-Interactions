"""Template experimental protocols for recommended hydrogel designs."""

from __future__ import annotations

import pandas as pd

CROSSLINK_PROTOCOL = {
    "photocrosslink": "dissolve macromer with 0.05–0.5% Irgacure 2959 and photocrosslink at 365 nm",
    "ionic": "mix with CaCl2 or other divalent cations to gel",
    "enzymatic": "gel with thrombin (fibrin) or Factor XIIIa / transglutaminase as applicable",
    "thermal": "cast at ~40 °C and gel by cooling to 4–37 °C",
    "chemical": "crosslink with the published small-molecule or peptide crosslinker for this chemistry",
}


def protocol_from_row(row: pd.Series | dict) -> str:
    material = row["material_class"].replace("_", " ")
    xl = CROSSLINK_PROTOCOL.get(row["crosslinking"], row["crosslinking"])
    gf = (
        "chondrogenic medium + 10 ng/mL TGF-β3"
        if row["growth_factor"] == "TGF_b3"
        else "chondrogenic medium + 10 ng/mL TGF-β1"
        if row["growth_factor"] == "TGF_b1"
        else "expansion / basal medium without added TGF-β"
    )
    ligand = (
        "include RGD or native adhesive motifs"
        if float(row["has_adhesion_ligand"]) >= 0.5
        else "no added adhesive peptide"
    )
    surface = row["surface_chemistry"].replace("_", " ")
    return (
        f"Encapsulate {row['species']} {row['cell_type'].replace('_', ' ')}s "
        f"(P{int(row['passage'])}, {row['cell_density_million_per_ml']:.1f}×10^6 cells/mL) "
        f"in {row['polymer_concentration_wt_pct']:.1f} wt% {material} "
        f"(target stiffness {row['stiffness_kpa']:.1f} kPa, porosity ~{row['porosity_pct']:.0f}%). "
        f"Network: {xl}; surface chemistry {surface}; {ligand}. "
        f"Culture as {row['culture_model'].replace('_', ' ')} for {int(row['culture_time_days'])} days in {gf}. "
        f"Readouts: live/dead viability, DNA (proliferation), COL2A1/SOX9/ACAN, sGAG and collagen II."
    )

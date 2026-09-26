"""SQLite helpers for the TissueLab experimental database."""

from __future__ import annotations

import sqlite3

from tissuelab.paths import DB_PATH, SCHEMA_SQL_PATH

VOCAB_CELL_TYPES = [
    ("articular_chondrocyte", "cartilage", "Primary or expanded articular chondrocytes"),
    ("auricular_chondrocyte", "cartilage", "Primary auricular (elastic cartilage) chondrocytes"),
    ("nasal_chondrocyte", "cartilage", "Nasoseptal / hyaline nasal chondrocytes; not articular or auricular"),
    ("MSC", "stromal", "Bone-marrow or otherwise unspecified MSCs in a cartilage protocol"),
    ("adipose_MSC", "stromal", "Adipose-derived MSCs / ASCs in a cartilage protocol"),
    ("ATDC5", "cartilage", "Murine ATDC5 chondrogenic cell line"),
    ("cartilage_progenitor", "cartilage", "Articular cartilage-resident chondroprogenitor cells (ACPCs)"),
]

VOCAB_MATERIALS = [
    ("GelMA", "protein", None),
    ("fibrin", "protein", None),
    ("silk_fibrin", "protein", None),
    ("PEG", "synthetic", None),
    ("PEG_dextran", "synthetic", None),
    ("PEGMA", "synthetic", "Includes commercial BioINK PEGMA"),
    ("alginate", "polysaccharide", None),
    ("HA", "polysaccharide", None),
    ("collagen", "protein", None),
    ("agarose", "polysaccharide", None),
    ("chitosan_HA", "polysaccharide", None),
    ("chitosan", "polysaccharide", None),
    ("gelatin", "protein", None),
    ("PVA", "synthetic", None),
    ("PVA_dECM", "composite", "PVA-norbornene plus solubilized decellularized cartilage matrix"),
    ("dextran", "polysaccharide", None),
    ("cellulose", "polysaccharide", None),
    ("gellan", "polysaccharide", None),
    ("gelatin_alginate", "composite", None),
    ("fibrin_alginate", "composite", None),
    ("GelMA_chitosan", "composite", "GelMA plus glycol chitosan"),
    ("GelMA_HA", "composite", "GelMA / gelatin-methacrylamide plus HA-MA"),
    ("GelMA_alginate", "composite", "GelMA plus oxidized methacrylated alginate (OMA)"),
    ("chitosan_gelatin_PVA", "composite", "CS/Gel/PVA freeze–thaw hydrogels"),
    ("alginate_dECM", "composite", "Alginate bioink with processed cartilage matrix"),
    ("collagen_alginate", "composite", "Collagen I / alginate blends"),
    ("fibrin_dECM", "composite", "Fibrin plus decellularized cartilage and/or amnion matrix"),
    ("PDLLA_PEG_HA", "synthetic", "Methacrylated PDLLA-PEG with HA, PSL scaffolds"),
    ("cellulose_alginate", "composite", "Nanocellulose–alginate bioinks"),
    ("fibrin_HA", "composite", "Fibrin plus methacrylated hyaluronic acid"),
    ("chitosan_silk", "composite", "Chitosan–silk fibroin scaffolds"),
    ("PEG_HA", "composite", "PEG or pHPMA-PEG hydrogels with methacrylated HA"),
    ("PEG_silk", "composite", "Silk fibroin plus PEGDMA / PEG hydrogels"),
    ("saccharide_peptide", "synthetic", "Saccharide-peptide copolymer hydrogels"),
]

VOCAB_ASSAYS = [
    ("viability_pct", "viability", "%", None, "Live/dead or equivalent percent live cells"),
    ("dna_ug", "proliferation", "ug", None, "Absolute DNA; not comparable across kits without a standard"),
    ("dna_fold_vs_day0", "proliferation", "fold", None, None),
    ("col2_col1_ratio", "differentiation", "ratio", "cartilage", "COL2A1 / COL1A1 redifferentiation index"),
    ("col2a1_fold", "differentiation", "fold", "cartilage", "qPCR fold vs a paper-local control"),
    ("sox9_fold", "differentiation", "fold", "cartilage", None),
    ("acan_fold", "differentiation", "fold", "cartilage", None),
    ("sgag_per_dna", "ecm", "ug/ug", "cartilage", "sGAG/DNA; kit-dependent"),
    ("sgag_ug", "ecm", "ug", "cartilage", None),
    ("collagen2_histology", "ecm", "ordinal", "cartilage", "Ordinal 0-3 from staining description"),
    ("sgag_histology", "ecm", "ordinal", "cartilage", None),
    ("morphology_spherical", "differentiation", "ordinal", "cartilage", "0 fibroblastic … 1 spherical"),
    # Future cell families — registered now so osteoblast/neuron rows do not need a migration.
    ("alp_activity", "differentiation", "U/mg", "bone", "Alkaline phosphatase; osteoblast/MSC osteogenesis"),
    ("calcium_deposition", "ecm", "ug", "bone", None),
    ("uptake_pct", "other", "%", "delivery", "Nanoparticle or drug uptake"),
]


def connect(path=DB_PATH) -> sqlite3.Connection:
    path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(path)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def init_schema(conn: sqlite3.Connection) -> None:
    conn.executescript(SCHEMA_SQL_PATH.read_text())
    conn.executemany(
        "INSERT OR REPLACE INTO vocab_cell_types VALUES (?, ?, ?)",
        VOCAB_CELL_TYPES,
    )
    conn.executemany(
        "INSERT OR REPLACE INTO vocab_materials VALUES (?, ?, ?)",
        VOCAB_MATERIALS,
    )
    conn.executemany(
        "INSERT OR REPLACE INTO vocab_assays VALUES (?, ?, ?, ?, ?)",
        VOCAB_ASSAYS,
    )
    conn.commit()

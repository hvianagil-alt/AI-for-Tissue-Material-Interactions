"""Controlled vocabularies that uniformize papers before any model sees them.

Chemistry, architecture, and application are the missing axes. Every paper
and every experiment is tagged with the same labels so GelMA-methacrylate-10%
and “methacrylated gelatin” are one thing.
"""

from __future__ import annotations

import re
from typing import Any

CHEM_PATTERNS: list[tuple[str, re.Pattern[str]]] = [
    ("methacrylated", re.compile(r"\b(?:gelma|hama|algma|meha|methacrylat(?:ed|e)|methacryl(?:oyl|amide)|gelatin methacrylate)\b", re.I)),
    ("norbornene", re.compile(r"\bnorbornene\b|\bthiol[- ]ene\b|\bPEG[- ]NB\b", re.I)),
    ("oxidized", re.compile(r"\b(?:periodate[- ]oxidiz|oxidized (?:alginate|hyaluronan|HA)|alginate dialdehyde)\b", re.I)),
    ("tyramine", re.compile(r"\btyramine\b", re.I)),
    ("rgd_conjugated", re.compile(r"\bRGD\b|\bRGDS\b", re.I)),
    ("sulfated", re.compile(r"\bsulfat(?:ed|ion)\b|\bchondroitin sulfate\b", re.I)),
    ("photo_I2959", re.compile(r"\bIrgacure\s*2959\b|\bI2959\b", re.I)),
    ("photo_LAP", re.compile(r"\bLAP\b|\blithium phenyl\b", re.I)),
    ("enzymatic", re.compile(r"\b(?:thrombin|transglutaminase|FXIII|factor XIII|enzymatic(?:ally)? cross[- ]?link)\b", re.I)),
    ("thiolated", re.compile(r"\bthiolat(?:ed|ion)\b|\bthiol[- ]ene\b", re.I)),
    ("photo_VA086", re.compile(r"\bVA[- ]?086\b", re.I)),
    ("freeze_thaw", re.compile(r"\bfreeze[- ]thaw\b", re.I)),
    ("hofmeister", re.compile(r"\bHofmeister\b", re.I)),
    ("dopamine", re.compile(r"\b(?:dopamine|catechol|polydopamine)\b", re.I)),
    ("click", re.compile(r"\bclick chemistr|\bazide[- ]alkyne\b|\bSPAAC\b", re.I)),
    ("mmp_degradable", re.compile(r"\bMMP[- ]degradab", re.I)),
    ("genipin", re.compile(r"\bgenipin\b", re.I)),
    ("edc_nhs", re.compile(r"\bEDC\b|\bNHS\b", re.I)),
]

ARCH_PATTERNS: list[tuple[str, re.Pattern[str]]] = [
    ("3d_printed", re.compile(r"\b(?:bioprint|bio[- ]?ink|3d print)\b", re.I)),
    ("microgel", re.compile(r"\b(?:microgel|microstrand|granular hydrogel|jammed)\b", re.I)),
    ("fiber", re.compile(r"\b(?:electrospun|nanofiber|microfiber)\b", re.I)),
    ("bilayer", re.compile(r"\b(?:bilayer|multilayer|osteochondral scaffold)\b", re.I)),
    ("porous_scaffold", re.compile(r"\b(?:freeze[- ]dr(?:y|ied)|porogen|salt leach)\b", re.I)),
    ("microsphere", re.compile(r"\bmicrospheres?\b", re.I)),
    ("ipn", re.compile(r"\b(?:interpenetrating|IPN|semi[- ]IPN)\b", re.I)),
    ("injectable", re.compile(r"\binjectable\b", re.I)),
    ("monolayer", re.compile(r"\b(?:monolayer|2D cultur|seeded onto)\b", re.I)),
]

APP_PATTERNS: list[tuple[str, re.Pattern[str]]] = [
    ("osteoarthritis", re.compile(r"\bosteoarthrit|\bOA model\b", re.I)),
    ("osteochondral", re.compile(r"\bosteochondral\b", re.I)),
    ("meniscus", re.compile(r"\bmeniscus\b", re.I)),
    ("auricular", re.compile(r"\bauricular\b|\bear cartilage\b", re.I)),
    ("nucleus_pulposus", re.compile(r"\bnucleus pulposus\b|\bintervertebral\b", re.I)),
    ("tracheal", re.compile(r"\btrachea", re.I)),
    ("in_vivo_repair", re.compile(r"\b(?:in vivo|animal model|rabbit knee|subcutaneous)\b", re.I)),
    ("bioprinting", re.compile(r"\b(?:bioprint|bio[- ]?ink)\b", re.I)),
    ("drug_delivery", re.compile(r"\b(?:drug delivery|controlled release|loaded with)\b", re.I)),
    ("in_vitro_cartilage", re.compile(r"\b(?:cartilage|chondrogen|chondrocyte)\b", re.I)),
]

REVIEW_RE = re.compile(r"\b(?:systematic review|meta-analysis|this review|we review)\b", re.I)

CHEM_PRIORITY = [p[0] for p in CHEM_PATTERNS]
ARCH_PRIORITY = [p[0] for p in ARCH_PATTERNS]
APP_PRIORITY = [p[0] for p in APP_PATTERNS]


def _hits(text: str, patterns: list[tuple[str, re.Pattern[str]]]) -> list[str]:
    found: list[str] = []
    for label, pat in patterns:
        if pat.search(text) and label not in found:
            found.append(label)
    return found


def analyze_text(title: str | None = None, abstract: str | None = None, extra: str | None = None) -> dict[str, Any]:
    """Uniform labels from any paper-like blob. Not a measurement."""
    text = " ".join(part for part in (title, abstract, extra) if part) or ""
    chem = _hits(text, CHEM_PATTERNS)
    arch = _hits(text, ARCH_PATTERNS)
    apps = _hits(text, APP_PATTERNS)
    if not arch:
        blob = text.lower()
        if "bioprint" in blob or "bioink" in blob:
            arch = ["3d_printed"]
        elif "2d" in blob or "monolayer" in blob:
            arch = ["monolayer"]
        elif text:
            arch = ["bulk_hydrogel"]
    if not apps and re.search(r"\bcartilage\b|\bchondrogen|\bchondrocyte", text, re.I):
        apps = ["in_vitro_cartilage"]
    primary_chem = chem[0] if chem else "unmodified"
    primary_arch = arch[0] if arch else "bulk_hydrogel"
    primary_app = apps[0] if apps else "unspecified"
    is_review = bool(REVIEW_RE.search(text))
    return {
        "chemical_modifications": chem,
        "chemical_modification": primary_chem,
        "architectures": arch,
        "architecture": primary_arch,
        "applications": apps,
        "application": primary_app,
        "is_review_like": is_review,
    }


def tag_experiment(exp: dict, study: dict | None = None) -> dict:
    """Fill chemistry / structure / application on a curated experiment if blank."""
    study = study or {}
    # Chemistry must not inherit from comparison-paper notes (a GelMA/agarose
    # paper is not methacrylated agarose).
    chem_blob = " ".join(
        str(x)
        for x in (exp.get("material_class"), exp.get("material_detail"), exp.get("crosslinking"))
        if x
    )
    arch_blob = " ".join(
        str(x)
        for x in (
            exp.get("material_class"),
            exp.get("material_detail"),
            exp.get("culture_model"),
            exp.get("notes"),
            exp.get("extracted_from"),
        )
        if x
    )
    chem_tags = analyze_text(chem_blob)
    tags = analyze_text(arch_blob)
    study_tags = analyze_text(study.get("citation"), study.get("notes"))
    out = dict(exp)
    if not out.get("chemical_modification"):
        material = str(out.get("material_class") or "")
        if material in {"GelMA", "GelMA_HA", "GelMA_chitosan", "PEGMA"}:
            out["chemical_modification"] = "methacrylated"
        elif "methacryl" in chem_blob.lower():
            out["chemical_modification"] = "methacrylated"
        elif out.get("crosslinking") == "enzymatic":
            out["chemical_modification"] = "enzymatic"
        else:
            out["chemical_modification"] = chem_tags["chemical_modification"]
    if not out.get("architecture"):
        model = str(out.get("culture_model") or "")
        if model == "3D_bioprint":
            out["architecture"] = "3d_printed"
        elif model == "2D":
            out["architecture"] = "monolayer"
        else:
            out["architecture"] = tags["architecture"] if tags["architecture"] != "unmodified" else "bulk_hydrogel"
    if not out.get("application"):
        cell = str(out.get("cell_type") or "")
        if cell == "auricular_chondrocyte":
            out["application"] = "auricular"
        elif out.get("culture_model") == "3D_bioprint":
            out["application"] = "bioprinting"
        else:
            app = tags["application"]
            if app == "unspecified":
                app = study_tags["application"]
            out["application"] = app if app != "unspecified" else "in_vitro_cartilage"
    return out


def training_relevant(analysis: dict, *, has_hydrogel: bool, has_cartilage_cell: bool, has_viability: bool) -> bool:
    if analysis.get("is_review_like"):
        return False
    app = analysis.get("application")
    if app in {"meniscus", "nucleus_pulposus", "tracheal", "drug_delivery"} and not has_cartilage_cell:
        return False
    return bool(has_hydrogel and has_cartilage_cell and (has_viability or app in {"in_vitro_cartilage", "bioprinting", "osteochondral", "auricular"}))

"""Regex candidates from paper abstracts. Never treated as ground truth."""

from __future__ import annotations

import re
from typing import Any

from tissuelab.ontology import analyze_text

MATERIAL_PATTERNS: list[tuple[str, re.Pattern[str]]] = [
    ("GelMA", re.compile(r"\b(?:gelma|gelatin methacrylate|methacrylated gelatin)\b", re.I)),
    ("HA", re.compile(r"\b(?:hyaluronic acid|hyaluronan|\bHA\b|MeHA|methacrylated HA)\b", re.I)),
    ("alginate", re.compile(r"\balginate\b", re.I)),
    ("PEG", re.compile(r"\b(?:PEGDA|PEGMA|PEGDMA|poly(?:ethylene glycol)|PEG hydrogel|PEG-based)\b", re.I)),
    ("collagen", re.compile(r"\bcollagen(?: type [IVX]+)?\b", re.I)),
    ("fibrin", re.compile(r"\bfibrin(?:ogen)?\b", re.I)),
    ("chitosan", re.compile(r"\bchitosan\b", re.I)),
    ("agarose", re.compile(r"\bagarose\b", re.I)),
    ("silk_fibrin", re.compile(r"\bsilk fibroin\b", re.I)),
    ("gelatin", re.compile(r"\bgelatin\b(?!\s+methacrylate)", re.I)),
    ("dextran", re.compile(r"\bdextran\b", re.I)),
    ("PVA", re.compile(r"\b(?:PVA|polyvinyl alcohol)\b", re.I)),
    ("gellan", re.compile(r"\bgellan\b", re.I)),
    ("cellulose", re.compile(r"\b(?:cellulose|nanocellulose|CMC)\b", re.I)),
]

CELL_PATTERNS: list[tuple[str, re.Pattern[str]]] = [
    ("nasal_chondrocyte", re.compile(r"\b(?:nasoseptal|nasal(?:septal)?|septal) chondrocytes?\b", re.I)),
    ("auricular_chondrocyte", re.compile(r"\bauricular chondrocytes?\b", re.I)),
    ("articular_chondrocyte", re.compile(r"\b(?:articular chondrocytes?|chondrocytes?)\b", re.I)),
    ("adipose_MSC", re.compile(r"\b(?:adipose[- ]derived|hASCs?|hAdMSCs?|AD-hMSCs?)\b", re.I)),
    ("MSC", re.compile(r"\b(?:mesenchymal stem cells?|MSCs?|bone marrow stromal)\b", re.I)),
    ("ATDC5", re.compile(r"\bATDC5\b", re.I)),
    ("iPSC", re.compile(r"\b(?:iPSCs?|induced pluripotent)\b", re.I)),
]

VIABILITY_RES = [
    re.compile(
        r"(?:viability|viable cells?|cell viability|live cells?)[^\d%]{0,40}"
        r"(\d+(?:\.\d+)?)\s*%",
        re.I,
    ),
    re.compile(
        r"(\d+(?:\.\d+)?)\s*%\s*(?:viability|viable|live(?:/?dead)?)",
        re.I,
    ),
    re.compile(
        r"live[/\-]dead[^\d%]{0,48}(\d+(?:\.\d+)?)\s*%",
        re.I,
    ),
]

STIFFNESS_RE = re.compile(
    r"(\d+(?:\.\d+)?)\s*(?:[-–]\s*(\d+(?:\.\d+)?)\s*)?(kPa|MPa|Pa)\b",
    re.I,
)
CULTURE_DAYS_RE = re.compile(r"\b(?:after|at|for|day)\s+(\d{1,3})\s*(?:days?|d)\b", re.I)
CULTURE_DAYS_BARE_RE = re.compile(r"\b(\d{1,2})\s*days?\b", re.I)
HYDROGEL_RE = re.compile(r"\bhydrogels?\b|\bbioinks?\b|\bscaffolds?\b", re.I)
CARTILAGE_RE = re.compile(r"\bcartilage\b|\bchondrogen(?:ic|esis)\b", re.I)
OFF_TARGET_BIO_RE = re.compile(
    r"\b(?:H9c2|HUVECs?|hepatocytes?|cardiomyocytes?|keratinocytes?|"
    r"MCF[- ]?7|HeLa|Caco-2|PC-12|SH-SY5Y|osteoblasts?)\b",
    re.I,
)
TGF_RE = re.compile(r"\bTGF[-\s]?β?\s*3\b|\bTGF[-\s]?beta[-\s]?3\b", re.I)
TGF_B1_RE = re.compile(r"\bTGF[-\s]?β?\s*1\b|\bTGF[-\s]?beta[-\s]?1\b", re.I)
SPECIES_PATTERNS = [
    ("human", re.compile(r"\bhuman\b|\bprimary human\b", re.I)),
    ("bovine", re.compile(r"\bbovine\b|\bcow\b|\bcalf\b", re.I)),
    ("porcine", re.compile(r"\bporcine\b|\bpig\b", re.I)),
    ("rabbit", re.compile(r"\brabbit\b", re.I)),
    ("murine", re.compile(r"\bmurine\b|\bmouse\b|\brat\b", re.I)),
]
SENTENCE_SPLIT = re.compile(r"(?<=[.!?])\s+(?=[A-Z0-9])")
CANONICAL_DAYS = {1, 3, 7, 10, 14, 21, 28, 42, 56}
COMPOSITE_MATERIALS = {
    frozenset({"chitosan", "HA"}): "chitosan_HA",
    frozenset({"gelatin", "alginate"}): "gelatin_alginate",
    frozenset({"fibrin", "alginate"}): "fibrin_alginate",
    frozenset({"PEG", "dextran"}): "PEG_dextran",
    frozenset({"silk_fibrin", "fibrin"}): "silk_fibrin",
    frozenset({"GelMA", "chitosan"}): "GelMA_chitosan",
    frozenset({"GelMA", "HA"}): "GelMA_HA",
    frozenset({"GelMA", "alginate"}): "GelMA_alginate",
    frozenset({"chitosan", "gelatin", "PVA"}): "chitosan_gelatin_PVA",
    frozenset({"collagen", "alginate"}): "collagen_alginate",
    frozenset({"alginate", "HA"}): "alginate_HA",
    frozenset({"GelMA", "PEG"}): "GelMA_PEG",
}
MATERIAL_PRIORITY = [
    "GelMA",
    "alginate",
    "HA",
    "fibrin",
    "agarose",
    "collagen",
    "PEG",
    "chitosan",
    "silk_fibrin",
    "gelatin",
    "PVA",
    "dextran",
    "cellulose",
    "gellan",
]


def _span(text: str, m: re.Match[str], pad: int = 40) -> str:
    start = max(0, m.start() - pad)
    end = min(len(text), m.end() + pad)
    return " ".join(text[start:end].split())


def _kpa(value: float, unit: str) -> float | None:
    u = unit.lower()
    if u == "kpa":
        return value
    if u == "mpa":
        return value * 1000.0
    if u == "pa":
        return value / 1000.0
    return None


def extract_from_abstract(abstract: str | None, title: str | None = None) -> list[dict[str, Any]]:
    text = " ".join(part for part in (title, abstract) if part)
    if not text.strip():
        return []
    rows: list[dict[str, Any]] = []

    if HYDROGEL_RE.search(text):
        rows.append(
            {
                "field": "scaffold_class",
                "value_text": "hydrogel_or_bioink",
                "value_num": None,
                "unit": None,
                "evidence_span": None,
                "confidence": "medium",
            }
        )
    if CARTILAGE_RE.search(text):
        rows.append(
            {
                "field": "tissue",
                "value_text": "cartilage",
                "value_num": None,
                "unit": None,
                "evidence_span": None,
                "confidence": "medium",
            }
        )
    if TGF_RE.search(text):
        m = TGF_RE.search(text)
        rows.append(
            {
                "field": "growth_factor",
                "value_text": "TGF_b3",
                "value_num": None,
                "unit": None,
                "evidence_span": _span(text, m) if m else None,
                "confidence": "medium",
            }
        )

    tags = analyze_text(title, abstract)
    for field in ("chemical_modification", "architecture", "application"):
        val = tags.get(field)
        if val and val not in {"unmodified", "unspecified"}:
            rows.append(
                {
                    "field": field,
                    "value_text": val,
                    "value_num": None,
                    "unit": None,
                    "evidence_span": None,
                    "confidence": "medium",
                }
            )

    for label, pat in MATERIAL_PATTERNS:
        m = pat.search(text)
        if m:
            rows.append(
                {
                    "field": "material_class",
                    "value_text": label,
                    "value_num": None,
                    "unit": None,
                    "evidence_span": _span(text, m),
                    "confidence": "medium",
                }
            )
    for label, pat in CELL_PATTERNS:
        m = pat.search(text)
        if m:
            rows.append(
                {
                    "field": "cell_type",
                    "value_text": label,
                    "value_num": None,
                    "unit": None,
                    "evidence_span": _span(text, m),
                    "confidence": "medium",
                }
            )

    seen_viab: set[float] = set()
    for pat in VIABILITY_RES:
        for m in pat.finditer(text):
            val = float(m.group(1))
            if val > 100 or val < 5 or val in seen_viab:
                continue
            seen_viab.add(val)
            rows.append(
                {
                    "field": "viability_pct",
                    "value_text": str(val),
                    "value_num": val,
                    "unit": "%",
                    "evidence_span": _span(text, m),
                    "confidence": "low",
                }
            )

    seen_kpa: set[float] = set()
    for m in STIFFNESS_RE.finditer(text):
        lo = float(m.group(1))
        hi = float(m.group(2)) if m.group(2) else lo
        unit = m.group(3)
        for raw in {lo, hi}:
            kpa = _kpa(raw, unit)
            if kpa is None or kpa <= 0 or kpa > 5000 or kpa in seen_kpa:
                continue
            seen_kpa.add(kpa)
            rows.append(
                {
                    "field": "stiffness_kpa",
                    "value_text": str(kpa),
                    "value_num": kpa,
                    "unit": "kPa",
                    "evidence_span": _span(text, m),
                    "confidence": "low",
                }
            )

    seen_days: set[int] = set()
    for m in CULTURE_DAYS_RE.finditer(text):
        days = int(m.group(1))
        if days < 1 or days > 90 or days in seen_days:
            continue
        seen_days.add(days)
        rows.append(
            {
                "field": "culture_time_days",
                "value_text": str(days),
                "value_num": float(days),
                "unit": "days",
                "evidence_span": _span(text, m),
                "confidence": "low",
            }
        )
    return rows


def materials_in(text: str) -> list[str]:
    found = []
    for label, pat in MATERIAL_PATTERNS:
        if pat.search(text) and label not in found:
            found.append(label)
    return found


def cells_in(text: str) -> list[str]:
    found = []
    for label, pat in CELL_PATTERNS:
        if pat.search(text) and label not in found:
            found.append(label)
    return found


def viability_hits(text: str) -> list[tuple[float, str]]:
    seen: set[float] = set()
    hits = []
    for pat in VIABILITY_RES:
        for m in pat.finditer(text):
            val = float(m.group(1))
            if val > 99.5 or val < 40 or val in seen:
                continue
            seen.add(val)
            hits.append((val, _span(text, m, 60)))
    return hits


def stiffness_hits(text: str) -> list[tuple[float, str]]:
    seen: set[float] = set()
    hits = []
    for m in STIFFNESS_RE.finditer(text):
        lo = float(m.group(1))
        hi = float(m.group(2)) if m.group(2) else None
        unit = m.group(3)
        if hi is not None and hi != lo:
            continue
        kpa = _kpa(lo, unit)
        if kpa is None or kpa < 0.1 or kpa > 800 or kpa in seen:
            continue
        seen.add(kpa)
        hits.append((kpa, _span(text, m, 50)))
    return hits


def culture_days_in(text: str) -> list[int]:
    days: list[int] = []
    for pat in (CULTURE_DAYS_RE, CULTURE_DAYS_BARE_RE):
        for m in pat.finditer(text):
            val = int(m.group(1))
            if val in CANONICAL_DAYS and val not in days:
                days.append(val)
    return days


def pick_material(materials: list[str]) -> tuple[str | None, str | None]:
    unique = []
    for item in materials:
        if item not in unique:
            unique.append(item)
    if not unique:
        return None, None
    key = frozenset(unique)
    if key in COMPOSITE_MATERIALS:
        return COMPOSITE_MATERIALS[key], "+".join(sorted(unique))
    if len(unique) == 1:
        return unique[0], None
    for subset, mapped in COMPOSITE_MATERIALS.items():
        if subset <= key:
            extra = [m for m in unique if m not in subset]
            detail = "+".join(sorted(subset))
            if extra:
                detail = detail + " (+" + ",".join(extra) + ")"
            return mapped, detail
    for label in MATERIAL_PRIORITY:
        if label in unique:
            return label, "+".join(unique)
    return unique[0], "+".join(unique)


def pick_cell(cells: list[str]) -> str | None:
    if "nasal_chondrocyte" in cells:
        return "nasal_chondrocyte"
    if "auricular_chondrocyte" in cells:
        return "auricular_chondrocyte"
    if "articular_chondrocyte" in cells:
        return "articular_chondrocyte"
    if "adipose_MSC" in cells:
        return "adipose_MSC"
    if "MSC" in cells or "iPSC" in cells:
        return "MSC"
    if "ATDC5" in cells:
        return "ATDC5"
    return None


def pick_species(text: str) -> str | None:
    for label, pat in SPECIES_PATTERNS:
        if pat.search(text):
            return label
    return None


def pick_growth_factor(text: str) -> str:
    if TGF_RE.search(text):
        return "TGF_b3"
    if TGF_B1_RE.search(text):
        return "TGF_b1"
    return "none"


def pick_culture_model(text: str) -> str:
    blob = text.lower()
    if "bioprint" in blob or "bioink" in blob or "bio-ink" in blob:
        return "3D_bioprint"
    if "2d" in blob or "monolayer" in blob:
        return "2D"
    return "3D_encapsulation"


def _window_kpa(text: str, needle: str) -> float | None:
    if not needle:
        return None
    pos = text.find(needle[:40]) if needle else -1
    if pos < 0:
        pos = 0
    window = text[max(0, pos - 280) : pos + 280]
    hits = stiffness_hits(window)
    if len(hits) == 1:
        return hits[0][0]
    return None


def is_off_target_biology(title: str | None = None, abstract: str | None = None, extra: str | None = None) -> bool:
    """Heart/endothelium/liver lines are not cartilage training rows."""
    blob = " ".join(part for part in (title, abstract, extra) if part) or ""
    if not OFF_TARGET_BIO_RE.search(blob):
        return False
    if CARTILAGE_RE.search(blob) or cells_in(blob):
        return False
    return True


def extract_conditions(title: str | None, abstract: str | None, extra: str | None = None) -> list[dict[str, Any]]:
    """Promote sentence-level numbers into candidate experiments.

    Still not ground truth. Caller must store curator_confidence=low and
    never invent a second condition from unpaired numbers.
    """
    parts = [p for p in (title, abstract, extra) if p]
    text = " ".join(parts)
    if is_off_target_biology(title, abstract, extra):
        return []
    if not HYDROGEL_RE.search(text) and not CARTILAGE_RE.search(text):
        return []
    material, detail = pick_material(materials_in(text))
    cell = pick_cell(cells_in(text))
    if not material or not cell:
        return []
    species = pick_species(text)
    gf = pick_growth_factor(text)
    model = pick_culture_model(text)
    paper_days = culture_days_in(text)
    paper_day = paper_days[0] if len(paper_days) == 1 else None
    tags = analyze_text(title, abstract, extra)

    conditions: list[dict[str, Any]] = []
    for sent in SENTENCE_SPLIT.split(text):
        viabs = viability_hits(sent)
        if not viabs:
            continue
        kpas = stiffness_hits(sent)
        sent_mat, sent_detail = pick_material(materials_in(sent))
        use_mat = sent_mat or material
        use_detail = sent_detail or detail
        days = culture_days_in(sent)
        day = days[0] if len(days) == 1 else paper_day
        if len(viabs) == 1:
            kpa = kpas[0][0] if len(kpas) == 1 else None
            if kpa is None:
                kpa = _window_kpa(text, sent)
            conditions.append(
                {
                    "material_class": use_mat,
                    "material_detail": use_detail,
                    "cell_type": cell,
                    "species": species,
                    "growth_factor": gf,
                    "culture_model": model,
                    "culture_time_days": float(day) if day else None,
                    "stiffness_kpa": kpa,
                    "viability_pct": viabs[0][0],
                    "evidence_span": viabs[0][1],
                    "paired_stiffness": kpa is not None,
                }
            )
        elif len(viabs) == len(kpas) == 2:
            for (val, span), (kpa, _) in zip(viabs, kpas):
                conditions.append(
                    {
                        "material_class": use_mat,
                        "material_detail": use_detail,
                        "cell_type": cell,
                        "species": species,
                        "growth_factor": gf,
                        "culture_model": model,
                        "culture_time_days": float(day) if day else None,
                        "stiffness_kpa": kpa,
                        "viability_pct": val,
                        "evidence_span": span,
                        "paired_stiffness": True,
                    }
                )

    if not conditions:
        header = " ".join(p for p in (title, abstract) if p)
        viabs = viability_hits(header) or viability_hits(text)
        kpas = stiffness_hits(header)
        if len(viabs) == 1:
            kpa = kpas[0][0] if len(kpas) == 1 else _window_kpa(header, viabs[0][1])
            conditions.append(
                {
                    "material_class": material,
                    "material_detail": detail,
                    "cell_type": cell,
                    "species": species,
                    "growth_factor": gf,
                    "culture_model": model,
                    "culture_time_days": float(paper_day) if paper_day else None,
                    "stiffness_kpa": kpa,
                    "viability_pct": viabs[0][0],
                    "evidence_span": viabs[0][1],
                    "paired_stiffness": kpa is not None,
                }
            )

    uniq = []
    seen_keys = set()
    for row in conditions:
        key = (row["material_class"], row["viability_pct"], row["stiffness_kpa"], row["culture_time_days"])
        if key in seen_keys:
            continue
        seen_keys.add(key)
        row["chemical_modification"] = tags.get("chemical_modification")
        row["architecture"] = tags.get("architecture")
        row["application"] = tags.get("application")
        uniq.append(row)
    return uniq

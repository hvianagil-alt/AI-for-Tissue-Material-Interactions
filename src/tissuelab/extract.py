"""Regex candidates from paper abstracts. Never treated as ground truth."""

from __future__ import annotations

import re
from typing import Any

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
    ("articular_chondrocyte", re.compile(r"\b(?:articular chondrocytes?|chondrocytes?)\b", re.I)),
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
HYDROGEL_RE = re.compile(r"\bhydrogels?\b|\bbioinks?\b|\bscaffolds?\b", re.I)
CARTILAGE_RE = re.compile(r"\bcartilage\b|\bchondrogen(?:ic|esis)\b", re.I)
TGF_RE = re.compile(r"\bTGF[-\s]?β?\s*3\b|\bTGF[-\s]?beta[-\s]?3\b", re.I)


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

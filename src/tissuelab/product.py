"""The thing a lab pays for: this week’s gel, what to skip, three DOIs.

Not a viability predictor. Leave-one-paper-out still loses to a dummy mean.
Sell the extracted table + avoid board. Keep shrinkage in the evidence card
so the number is honest, never as the product.
"""

from __future__ import annotations

import json
from pathlib import Path

from tissuelab.benchmark import load_viability
from tissuelab.paths import DB_PATH, HONEST_METRICS_PATH
from tissuelab.protocol_finder import AVOID_MEAN, find_protocol
from tissuelab.shrinkage import N_LOCKED_HYPERPARAMETERS, PAPERS_NEEDED_BEGINNING

# Gels a cartilage PI already has in the fridge or can order this week.
COMMERCIAL_GELS = (
    "GelMA",
    "fibrin",
    "HA",
    "alginate",
    "collagen",
    "chitosan",
    "PEG",
    "gellan",
    "gelatin_alginate",
    "agarose",
)
COMMERCIAL_CELLS = (
    "articular_chondrocyte",
    "auricular_chondrocyte",
    "nasal_chondrocyte",
    "MSC",
    "adipose_MSC",
)
_GEL_WEIGHT = {
    "GelMA": 10,
    "fibrin": 9,
    "HA": 8,
    "alginate": 7,
    "collagen": 7,
    "PEG": 6,
    "chitosan": 5,
    "gellan": 4,
    "gelatin_alginate": 5,
    "agarose": 3,
}
_CELL_WEIGHT = {
    "articular_chondrocyte": 10,
    "MSC": 7,
    "nasal_chondrocyte": 6,
    "auricular_chondrocyte": 5,
    "adipose_MSC": 5,
}

OFFER = {
    "job": "friday_protocol",
    "headline": "This week’s gel, three papers, what not to start.",
    "headline_pt": "O gel desta semana, três papers, o que não começar.",
    "sell": (
        "Extracted live/dead table for cartilage hydrogels, with an avoid list "
        "and the DOIs. Not an AI that predicts viability."
    ),
    "sell_pt": (
        "Tabela live/dead extraída para hidrogéis de cartilagem, com lista do que "
        "evitar e os DOIs. Não é uma AI que prevê viabilidade."
    ),
    "price_pilot": "£400–1,200 / lab / quarter",
    "price_note": (
        "Priced like Covidence / a TGF vial, billed as supplies. The PI signs the PO. "
        "A PhD does not. Monthly SaaS is the wrong grain."
    ),
    "buyer": "Cartilage / bioink PI (signs) or core facility — a lab seat, not a patient or a gel SKU.",
    "not_a_prediction": True,
}

NEVER_EXTRACT = [
    "Viability floors (‘>90%’, ‘80–85%’, ‘high viability’) as training means",
    "MTT / CCK-8 / WST / alamarBlue / ISO 10993 extract cytotoxicity",
    "2D monolayer live/dead as if it were in-gel",
    "Wrong cells: HUVEC, osteoblasts, fibroblasts, muscle, CNS, cancer, NP, CEP, meniscus-only",
    "Reviews, citation-of-citation, day-unknown means",
    "ECM-matured kPa at week 3+ as the encapsulation modulus",
    "Print pressure as Young’s modulus; thermoplastic / PCL mesh E",
    "Post-thaw cryo viability; PRP counted as TGF-β3",
    "Do not expand death gels (PEG / PEG-dextran articular) to ‘fix’ the avoid board",
    "Meniscus-only, heart-valve, osteogenic-only, tribology, lignin cytotoxicity",
]

# Closed hunts. The hole stays on the board (Friday still cannot cite it).
# Do not invent a mean. Do not re-boost lookalike tags (silk fibroin ≠ fibrin).
HUNT_LOG = {
    ("fibrin", "articular_chondrocyte"): {
        "status": "hunted_empty",
        "hole": "missing_print",
        "date": "2026-09",
        "why": (
            "OA fulltext hunt found no numeric in-gel live/dead for fibrin × articular × "
            "3D_bioprint. Closest miss: Couto 2024 FGT extrusion OA articular — qualitative "
            "'minimal cell death' only. Existing gold: bachmann2020 + rojas2025 encapsulate. "
            "Do not invent a print mean."
        ),
        "skip": (
            "xu2013",
            "bowes2024",
            "couto2024",
            "li2025gelbrin",
            "henrionnet2020",
            "sun2019",
            "perriergroult2026",
        ),
        "not_this_material": ("silk_fibrin",),
    },
    ("GelMA", "MSC"): {
        "status": "hunted_empty",
        "hole": "missing_kpa",
        "date": "2026-09",
        "why": (
            "Existing GelMA×MSC gold (chen2020, daly2016, fang2024, mcmillan2025, pei2023) has "
            "no text-quoted starting Young's. McMillan week-3 E and print-pressure kPa excluded. "
            "New OA hits skipped: chai2022 osteogenic-only + about 68%; huang2022 floors "
            "('above 85%') and printed-fiber text; walejewska2024 osteoid/osteogenic medium; "
            "baldini2026 qualitative. Do not digitize Pei Fig. S1A."
        ),
        "skip": (
            "chen2020",
            "daly2016",
            "fang2024",
            "mcmillan2025",
            "pei2023",
            "chai2022",
            "huang2022",
            "walejewska2024",
            "baldini2026",
        ),
        "not_this_material": (),
    },
}


def _round(value, digits: int = 1):
    if value is None:
        return None
    return round(float(value), digits)


def coverage_table(path=DB_PATH) -> list[dict]:
    """Numeric in-gel live/dead only — the gold table, grouped gel × cell."""
    frame = load_viability(path)
    if frame.empty:
        return []
    grouped = []
    for (material, cell), sub in frame.groupby(["material_class", "cell_type"], dropna=False):
        values = sub["viability_pct"].astype(float)
        n_kpa = int(sub["stiffness_kpa"].notna().sum()) if "stiffness_kpa" in sub.columns else 0
        n_print = 0
        if "culture_model" in sub.columns:
            n_print = int((sub["culture_model"] == "3D_bioprint").sum())
        n_encap = int(len(sub)) - n_print
        mean = float(values.mean())
        grouped.append(
            {
                "material_class": str(material),
                "cell_type": str(cell),
                "n_rows": int(len(sub)),
                "n_papers": int(sub["study_id"].nunique()),
                "mean": _round(mean),
                "min": _round(float(values.min())),
                "n_kpa": n_kpa,
                "n_print": n_print,
                "n_encap": n_encap,
                "avoid": bool(mean < AVOID_MEAN),
                "fragile": int(sub["study_id"].nunique()) < 2,
            }
        )
    grouped.sort(key=lambda r: (r["cell_type"], r["mean"] if r["mean"] is not None else 999))
    return grouped


def coverage_for_cell(cell_type: str, path=DB_PATH) -> list[dict]:
    return [row for row in coverage_table(path) if row["cell_type"] == cell_type]


def avoid_board(cell_type: str = "articular_chondrocyte", path=DB_PATH) -> list[dict]:
    """Gels whose extracted live/dead mean is a death for these cells."""
    deaths = [row for row in coverage_for_cell(cell_type, path) if row["avoid"]]
    deaths.sort(key=lambda r: (r["mean"] if r["mean"] is not None else 0, r["material_class"]))
    return deaths


def honest_model_card(path: Path | None = None) -> dict:
    """LOPO as shipped. Dummy still slightly ahead — say so on the product."""
    metrics_path = Path(path) if path else HONEST_METRICS_PATH
    report: dict = {}
    if metrics_path.exists():
        try:
            report = json.loads(metrics_path.read_text())
        except json.JSONDecodeError:
            report = {}
    dummy = (report.get("dummy_lopo") or {}).get("mae")
    shrink = (report.get("shrinkage_lopo") or report.get("deployed_lopo") or {}).get("mae")
    r2 = (report.get("shrinkage_lopo") or report.get("deployed_lopo") or {}).get("r2")
    dummy_ahead = dummy is not None and shrink is not None and float(dummy) < float(shrink)
    n_studies = int(report.get("n_studies") or 0)
    n_rows = int(report.get("n_rows") or 0)
    n_priors = max(0, int(report.get("served_empirical_priors") or 0))
    return {
        "n_rows": n_rows,
        "n_studies": n_studies,
        "dummy_mae": _round(dummy, 2),
        "shrinkage_mae": _round(shrink, 2),
        "shrinkage_r2": _round(r2, 3),
        "deployed_estimator": report.get("deployed_estimator") or "shrinkage",
        "mvp_pass": bool(report.get("mvp_pass")),
        "beats_dummy": bool(report.get("beats_dummy")),
        "dummy_ahead": dummy_ahead,
        "served_locked_hyperparameters": N_LOCKED_HYPERPARAMETERS,
        "served_empirical_priors": n_priors,
        "papers_needed_beginning": PAPERS_NEEDED_BEGINNING,
        "sell": (
            "Do not buy this as a predictor. Dummy LOPO still slightly beats shrinkage. "
            "Buy the labeled table, the avoid list, and the DOIs."
            if dummy_ahead
            else "The served number is shrinkage, not a neural net. Use the papers, not the point estimate."
        ),
    }


def _hole_score(row: dict | None, material: str, cell: str) -> tuple[float, str]:
    gel_w = _GEL_WEIGHT.get(material, 2)
    cell_w = _CELL_WEIGHT.get(cell, 2)
    if row is None:
        return 20.0 * gel_w * cell_w / 10.0, "missing_pair"
    n_papers = int(row["n_papers"])
    mean = row["mean"]
    score = (gel_w * cell_w) / (n_papers + 1)
    kind = "thin"
    if material == "GelMA" and cell == "articular_chondrocyte" and n_papers < 3:
        score += 100
        kind = "fragile_competitor"
        if int(row.get("n_encap") or 0) == 0:
            score += 40
            kind = "missing_encap"
    elif row["avoid"]:
        # Deaths stay on the avoid board. Do not spend the next pass making PEG deader.
        return -1.0, "locked_avoid"
    elif material == "fibrin" and cell == "articular_chondrocyte" and int(row.get("n_print") or 0) == 0:
        score += 50
        kind = "missing_print"
    elif mean is not None and mean >= 90 and n_papers < 2:
        score += 30
        kind = "fragile_winner"
    elif n_papers < 2:
        score += 12
        kind = "fragile"
    if row["n_rows"] >= 3 and row["n_kpa"] == 0 and kind not in {"missing_encap", "fragile_competitor"}:
        score += 18
        if kind in {"thin", "fragile"}:
            kind = "missing_kpa"
    return score, kind


def research_queue(path=DB_PATH, limit: int = 15) -> list[dict]:
    """Next extraction holes ordered by product value, not abstract regex hits."""
    have = {(r["material_class"], r["cell_type"]): r for r in coverage_table(path)}
    holes = []
    seen = set()
    for gel in COMMERCIAL_GELS:
        for cell in COMMERCIAL_CELLS:
            key = (gel, cell)
            row = have.get(key)
            score, kind = _hole_score(row, gel, cell)
            if kind == "locked_avoid" or score < 0:
                seen.add(key)
                continue
            if row and not row["fragile"] and kind not in {
                "fragile_competitor",
                "missing_kpa",
                "missing_encap",
                "missing_print",
            }:
                if int(row["n_papers"]) >= 3 and (row["n_kpa"] or row["n_rows"] < 3):
                    continue
            seen.add(key)
            holes.append(_hole_record(gel, cell, kind, score, row))
    # Single-paper winners / deaths outside the commercial grid still matter.
    for key, row in have.items():
        if key in seen:
            continue
        if not (row["fragile"] or row["avoid"]):
            continue
        gel, cell = key
        score, kind = _hole_score(row, gel, cell)
        if kind == "locked_avoid" or score < 0:
            continue
        holes.append(_hole_record(gel, cell, kind, score, row))
    holes.sort(key=lambda h: (-h["score"], h["material_class"], h["cell_type"]))
    return _keep_hunted_empty(holes, limit)


def _keep_hunted_empty(holes: list[dict], limit: int) -> list[dict]:
    """Closed hunts stay on the board even when they score below the cut.

    Friday still cannot cite them. Do not let missing_pair noise bury a logged miss.
    """
    if limit >= len(holes):
        return holes
    kept = holes[:limit]
    missed = [h for h in holes[limit:] if h.get("hunt_status") == "hunted_empty"]
    if not missed:
        return kept
    replace_from = [i for i, h in enumerate(kept) if h.get("hunt_status") != "hunted_empty"]
    for pin in missed:
        if not replace_from:
            break
        kept[replace_from.pop()] = pin
    kept.sort(key=lambda h: (-h["score"], h["material_class"], h["cell_type"]))
    return kept


def _hunt_for(material: str, cell: str, kind: str) -> dict | None:
    rec = HUNT_LOG.get((material, cell))
    if not rec:
        return None
    if rec.get("hole") and rec["hole"] != kind:
        return None
    return rec


def _hole_record(gel: str, cell: str, kind: str, score: float, row: dict | None) -> dict:
    hunt = _hunt_for(gel, cell, kind)
    out = {
        "material_class": gel,
        "cell_type": cell,
        "kind": kind,
        "score": round(float(score), 1),
        "n_papers": 0 if row is None else row["n_papers"],
        "n_rows": 0 if row is None else row["n_rows"],
        "mean": None if row is None else row["mean"],
        "n_kpa": 0 if row is None else row["n_kpa"],
        "n_print": 0 if row is None else row.get("n_print") or 0,
        "n_encap": 0 if row is None else row.get("n_encap") or 0,
        "why": _hole_why(kind, gel, cell, row, hunt),
        "hunt_status": None if hunt is None else hunt.get("status"),
        "hunt_why": None if hunt is None else hunt.get("why"),
        "hunt_skip": [] if hunt is None else list(hunt.get("skip") or ()),
        "not_this_material": [] if hunt is None else list(hunt.get("not_this_material") or ()),
    }
    return out


def _hole_why(kind: str, gel: str, cell: str, row: dict | None, hunt: dict | None = None) -> str:
    cell_s = cell.replace("_", " ")
    if kind == "fragile_competitor":
        n = 0 if row is None else row["n_papers"]
        return (
            f"Labs already run {gel} on {cell_s}. Gold has {n} paper(s). "
            "The ranking vs fibrin is one paper away from flipping."
        )
    if kind == "missing_encap":
        return (
            f"Labs already run {gel} encapsulate on {cell_s}. Gold is print-only "
            f"({n_papers(row)} paper(s), 0 encapsulation rows). The Friday keep-alive path is empty."
        )
    if kind == "missing_print":
        text = (
            f"{gel} × {cell_s} ranks keep-alive but has 0 printed rows. "
            "Switching the job to print cannot cite this gel."
        )
        if hunt and hunt.get("status") == "hunted_empty":
            text += (
                " OA hunt logged empty (Couto 2024 qualitative only). "
                "Do not retry xu2013/bowes2024/silk fibroin; do not invent a %."
            )
        return text
    if kind == "missing_pair":
        return f"No numeric in-gel live/dead for {gel} × {cell_s}. A buyer will type this pair."
    if kind == "death_confirm":
        mean = "n/d" if not row or row["mean"] is None else f"{row['mean']:.0f}%"
        return f"Avoid-board candidate ({mean}) on {n_papers(row)} paper(s) — confirm before locking the skip."
    if kind == "fragile_winner":
        mean = "n/d" if not row or row["mean"] is None else f"{row['mean']:.0f}%"
        return f"High extracted mean ({mean}) from one paper — do not let a singleton rank the week."
    if kind == "missing_kpa":
        text = f"{gel} × {cell_s} has live/dead but no encapsulation kPa. Lookup looks empty."
        if hunt and hunt.get("status") == "hunted_empty":
            text += (
                " OA hunt logged empty on existing gold (McMillan week-3 E / print pressure skipped). "
                "Do not retry chai2022 (osteogenic), huang2022 (floors), walejewska2024 (osteoid)."
            )
        return text
    if kind == "fragile":
        return f"Only {n_papers(row)} paper(s) for {gel} × {cell_s}."
    return f"Thin coverage for {gel} × {cell_s}."


def n_papers(row: dict | None) -> int:
    return 0 if row is None else int(row.get("n_papers") or 0)


def product_gap_boost(materials: set[str], cells: set[str], holes: list[dict] | None = None) -> tuple[float, list[str]]:
    """Bump a harvested paper that would close a buyer hole. Reading-list only.

    Prefer an exact gel×cell hit over a gel-only hit, including when a higher-scored
    missing pair (fibrin×MSC) sits above a hunted print hole (fibrin×articular).
    Silk fibroin tagged silk_fibrin is not a fibrin-print fill.
    """
    holes = holes if holes is not None else research_queue(limit=12)
    mats = set(materials or ())
    exact = None
    gel_only = None
    for hole in holes:
        banned = set(hole.get("not_this_material") or ())
        hunted = hole.get("hunt_status") == "hunted_empty"
        if hunted and banned & mats:
            continue
        if hole["material_class"] in mats and hole["cell_type"] in cells:
            exact = hole
            break
        if gel_only is None and hole["material_class"] in mats and not hunted:
            gel_only = hole
    if exact is not None:
        hunted = exact.get("hunt_status") == "hunted_empty"
        if hunted:
            return 6.0, [
                f"product_gap_open:{exact['material_class']}×{exact['cell_type']}:hunted_empty"
            ]
        return 22.0, [f"product_gap:{exact['material_class']}×{exact['cell_type']}"]
    if gel_only is not None:
        return 8.0, [f"product_gap_gel:{gel_only['material_class']}"]
    return 0.0, []


def honesty_notes(cell_type: str, how: str, coverage: list[dict], lang: str = "en") -> list[str]:
    """Buyer-facing holes for this job — not model caveats."""
    pt = lang == "pt"
    by = {row["material_class"]: row for row in coverage}
    notes: list[str] = []
    gelma = by.get("GelMA")
    fibrin = by.get("fibrin")
    if gelma and int(gelma.get("n_papers") or 0) < 3:
        notes.append(
            "O GelMA articular ainda tem menos de 3 papers — o ranking vs fibrina pode inverter."
            if pt
            else "GelMA articular live/dead is still from fewer than 3 papers — ranking vs fibrin can flip."
        )
    if how != "print" and gelma and gelma.get("n_rows") and int(gelma.get("n_encap") or 0) == 0:
        notes.append(
            "O GelMA extraído nestas células é só print — keep-alive não cita encapsulação GelMA."
            if pt
            else "Extracted GelMA for these cells is print-only — keep-alive cannot cite an encapsulate GelMA paper."
        )
    if how == "print" and fibrin and fibrin.get("n_rows") and int(fibrin.get("n_print") or 0) == 0:
        notes.append(
            "A fibrina tem live/dead extraído mas 0 linhas impressas — o job print não a pode citar."
            if pt
            else "Fibrin has extracted live/dead but 0 printed rows — the print job cannot cite it."
        )
        hunt = HUNT_LOG.get(("fibrin", cell_type))
        if hunt and hunt.get("status") == "hunted_empty":
            notes.append(
                "A caça OA a fibrin print não encontrou live/dead numérico (Couto 2024 é qualitativo). "
                "O buraco fica visível; não inventámos %."
                if pt
                else "OA hunt for fibrin print found no numeric live/dead (Couto 2024 is qualitative). "
                "The hole stays; no invented %."
            )
    return notes


def lab_decision(
    *,
    cell_type: str = "articular_chondrocyte",
    goal: str = "alive",
    how: str = "encapsulate",
    tgf: str = "either",
    stock: str = "any",
    site: str = "any",
    lang: str = "en",
    path=DB_PATH,
) -> dict:
    """JSON a PI (or a script) can act on this week."""
    proto = find_protocol(
        cell_type=cell_type,
        goal=goal,
        how=how,
        tgf=tgf,
        stock=stock,
        site=site,
        lang=lang,
        path=path,
    )
    cell = proto["intent"]["cell_type"]
    card = honest_model_card()
    # Fill prior count from gold if the benchmark JSON omitted it.
    if not card.get("served_empirical_priors"):
        cov = coverage_table(path)
        card["served_empirical_priors"] = len(cov)
        card["served_parameters"] = N_LOCKED_HYPERPARAMETERS + len(cov)
    else:
        card["served_parameters"] = N_LOCKED_HYPERPARAMETERS + int(card["served_empirical_priors"])
    board = avoid_board(cell, path)
    cov = coverage_for_cell(cell, path)
    pt = lang == "pt"
    return {
        **proto,
        "offer": {k: v for k, v in OFFER.items() if not k.endswith("_pt")}
        | {
            "headline": OFFER["headline_pt"] if pt else OFFER["headline"],
            "sell": OFFER["sell_pt"] if pt else OFFER["sell"],
        },
        "avoid_board": board,
        "coverage": cov,
        "honesty": honesty_notes(cell, proto["intent"]["how"], cov, lang=lang),
        "model_card": card,
        "research_queue": research_queue(path, limit=8),
        "never_extract": NEVER_EXTRACT,
        "not_a_prediction": True,
    }


def main() -> None:
    import argparse

    parser = argparse.ArgumentParser(description="TissueLab Friday decision pack (JSON).")
    parser.add_argument("--cell", default="articular_chondrocyte")
    parser.add_argument("--goal", default="alive")
    parser.add_argument("--how", default="encapsulate")
    parser.add_argument("--tgf", default="either")
    parser.add_argument("--stock", default="any")
    parser.add_argument("--site", default="any")
    parser.add_argument("--lang", default="en")
    parser.add_argument("--queue", action="store_true", help="Print research queue only")
    args = parser.parse_args()
    if args.queue:
        print(json.dumps(research_queue(), indent=2))
        return
    print(
        json.dumps(
            lab_decision(
                cell_type=args.cell,
                goal=args.goal,
                how=args.how,
                tgf=args.tgf,
                stock=args.stock,
                site=args.site,
                lang=args.lang,
            ),
            indent=2,
        )
    )


if __name__ == "__main__":
    main()

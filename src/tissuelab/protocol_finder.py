"""Rank extracted protocols for a PI's cells and job. Not a language model."""

from __future__ import annotations

from statistics import median

import pandas as pd

from tissuelab.benchmark import load_viability
from tissuelab.db import connect
from tissuelab.literature_model import list_viability_evidence
from tissuelab.paths import DB_PATH
from tissuelab.shrinkage import shrinkage_estimate

GOALS = ("alive", "print", "matrix")
HOW = ("encapsulate", "print", "either")
TGF_CHOICES = ("either", "none", "TGF_b3")
SITES = ("any", "nasal", "osteoarthritis", "auricular", "bioprinting")

LAB_GELS = [
    "fibrin",
    "GelMA",
    "HA",
    "alginate",
    "chitosan",
    "collagen",
    "gelatin_alginate",
    "GelMA_HA",
    "GelMA_alginate",
    "silk_fibrin",
    "agarose",
    "PEG",
    "chitosan_HA",
    "alginate_dECM",
    "cellulose_alginate",
    "fibrin_dECM",
    "chitosan_gelatin_PVA",
    "PDLLA_PEG_HA",
    "GelMA_chitosan",
    "gellan",
]

FIELD_DEFAULT = "GelMA"


def _median(values: list[float], default: float) -> float:
    clean = [float(v) for v in values if v is not None]
    return float(median(clean)) if clean else default


def _sgag_index(path=DB_PATH) -> dict[tuple[str, str], dict]:
    conn = connect(path)
    rows = conn.execute(
        """
        SELECT e.material_class, e.cell_type,
               COUNT(*) AS n, COUNT(DISTINCT e.study_id) AS papers
        FROM experiments e
        JOIN measurements m ON m.experiment_id = e.experiment_id
        WHERE m.assay = 'sgag_histology'
          AND e.study_id NOT LIKE 'pmid%'
        GROUP BY 1, 2
        """
    ).fetchall()
    conn.close()
    return {(r[0], r[1]): {"n": int(r[2]), "papers": int(r[3])} for r in rows}


def _same(rows: list[dict], material: str, cell: str) -> list[dict]:
    return [r for r in rows if r.get("material_class") == material and r.get("cell_type") == cell]


def _candidate_stats(
    material: str,
    cell: str,
    evidence: list[dict],
    numeric: pd.DataFrame,
    sgag: dict,
) -> dict:
    same = _same(evidence, material, cell)
    num = [r for r in same if r.get("viability_pct") is not None]
    qual = [r for r in same if r.get("viability_pct") is None]
    print_rows = [r for r in same if r.get("culture_model") == "3D_bioprint"]
    two_d = [r for r in same if r.get("culture_model") == "2D"]
    values = [float(r["viability_pct"]) for r in num]
    kpas = [float(r["stiffness_kpa"]) for r in same if r.get("stiffness_kpa") is not None]
    papers = {r.get("study_id") for r in same}
    sg = sgag.get((material, cell), {"n": 0, "papers": 0})
    mean = round(sum(values) / len(values), 1) if values else None
    return {
        "material_class": material,
        "cell_type": cell,
        "n_same_numeric": len(num),
        "n_same_qual": len(qual),
        "n_same": len(same),
        "n_papers_same": len(papers),
        "n_print_same": len(print_rows),
        "n_2d_same": len(two_d),
        "same_mean": mean,
        "same_min": round(min(values), 1) if values else None,
        "kpas": kpas,
        "n_sgag": int(sg["n"]),
        "n_sgag_papers": int(sg["papers"]),
        "numeric_rows": num,
        "all_rows": same,
    }


def _score(stats: dict, goal: str, how: str) -> float:
    n = stats["n_same_numeric"]
    mean = stats["same_mean"]
    n_qual = stats["n_same_qual"]
    if n == 0 and n_qual == 0:
        base = -80.0
    elif n == 0:
        base = 18.0 + min(n_qual, 5) * 2.0
    else:
        base = float(mean)
        if n >= 2:
            base += 4.0
        if n >= 4:
            base += 2.0
        if stats["n_papers_same"] == 1:
            base -= 1.0
    if mean is not None and mean < 55:
        base -= 40.0
    if stats["n_2d_same"] and stats["n_2d_same"] >= stats["n_same"] / 2:
        base -= 12.0
    if goal == "print" or how == "print":
        base += 12.0 if stats["n_print_same"] else -8.0
    if goal == "matrix":
        if stats["n_sgag_papers"]:
            base += 8.0 + min(stats["n_sgag_papers"], 5)
        else:
            base -= 4.0
    if stats["material_class"] == FIELD_DEFAULT:
        base += 1.2
    if goal == "alive" and "_" in str(stats["material_class"]):
        base -= 6.0
    return round(base, 2)


def _typical_kpa(stats: dict, how: str) -> float | None:
    kpas = stats.get("kpas") or []
    if kpas:
        return round(_median(kpas, kpas[0]), 1)
    return None


def _typical_days(how: str) -> int:
    return 7 if how == "print" else 14


def _pick_recipe(stats: dict, how: str) -> dict | None:
    """The extracted condition a PI can actually open — not a median of the gel family."""
    rows = list(stats.get("numeric_rows") or []) or list(stats.get("all_rows") or [])
    if not rows:
        return None
    want_print = how == "print"

    def key(row: dict):
        printed = row.get("culture_model") == "3D_bioprint"
        return (
            0 if row.get("viability_pct") is not None else 1,
            0 if printed == want_print else 1,
            0 if row.get("polymer_concentration_wt_pct") is not None else 1,
            0 if row.get("stiffness_kpa") is not None else 1,
            -(row.get("year") or 0),
        )

    row = sorted(rows, key=key)[0]
    return {
        "experiment_id": row.get("experiment_id"),
        "study_id": row.get("study_id"),
        "citation": row.get("citation") or row.get("study_id"),
        "doi": row.get("doi"),
        "material_class": row.get("material_class"),
        "material_detail": row.get("material_detail"),
        "polymer_concentration_wt_pct": row.get("polymer_concentration_wt_pct"),
        "crosslinking": row.get("crosslinking"),
        "cell_density_million_per_ml": row.get("cell_density_million_per_ml"),
        "architecture": row.get("architecture"),
        "application": row.get("application"),
        "chemical_modification": row.get("chemical_modification"),
        "stiffness_kpa": row.get("stiffness_kpa"),
        "growth_factor": row.get("growth_factor") or "none",
        "culture_time_days": row.get("culture_time_days"),
        "culture_model": row.get("culture_model"),
        "viability_pct": row.get("viability_pct"),
        "qualitative_label": row.get("qualitative_label"),
    }


def _pick_gf(stats: dict, tgf: str) -> str:
    if tgf in {"none", "TGF_b3"}:
        return tgf
    rows = stats.get("numeric_rows") or []
    if not rows:
        return "none"
    by = {}
    for row in rows:
        gf = row.get("growth_factor") or "none"
        by.setdefault(gf, []).append(float(row["viability_pct"]))
    best = max(by.items(), key=lambda kv: sum(kv[1]) / len(kv[1]))
    return str(best[0] or "none")


def _avoid(stats: dict) -> bool:
    """Do not serve a gel whose extracted live/dead mean is a death for these cells."""
    mean = stats.get("same_mean")
    return bool(mean is not None and mean < 60)


def _why(winner: dict, field: dict | None, intent: dict, lang: str = "en") -> str:
    cell = intent["cell_type"].replace("_", " ")
    mat = winner["material_class"]
    n = winner["n_same_numeric"]
    papers = winner["n_papers_same"]
    mean = winner["same_mean"]
    pt = lang == "pt"
    if n:
        core = (
            f"Para {cell}, {mat} tem o live/dead extraído mais sólido: {mean:.0f}% "
            f"({n} condições, {papers} papers)."
            if pt
            else f"For {cell}, {mat} has the strongest extracted live/dead: {mean:.0f}% "
            f"({n} conditions, {papers} papers)."
        )
    elif winner["n_same_qual"]:
        core = (
            f"Para {cell}, {mat} só tem floors/‘high’ extraídos — não há média live/dead."
            if pt
            else f"For {cell}, {mat} only has extracted floors/‘high’ — no live/dead mean."
        )
    else:
        core = (
            f"Não há linhas extraídas de {mat} nestas células. O número seria emprestado."
            if pt
            else f"No extracted rows of {mat} in these cells. Any number would be borrowed."
        )
    extra = ""
    if field and field["material_class"] != mat:
        if field["n_same_numeric"] == 0:
            extra = (
                " GelMA é o que a maior parte dos labs corre; nesta tabela não há live/dead numérico "
                "de condrócitos articulares em GelMA — só MSC ~80% pós-print e papers com kPa qualitativo."
                if pt
                else " GelMA is what most labs run; this table has no numeric articular live/dead in GelMA "
                "— only MSC ~80% post-print and qualitative kPa papers."
            )
        elif field["same_mean"] is not None:
            extra = (
                f" O default do campo (GelMA) está extraído a {field['same_mean']:.0f}% nestas células."
                if pt
                else f" The field default (GelMA) is extracted at {field['same_mean']:.0f}% in these cells."
            )
    job = ""
    if intent["goal"] == "print":
        job = (
            f" {winner['n_print_same']} condições impressas extraídas nestas células."
            if pt
            else f" {winner['n_print_same']} extracted printed conditions in these cells."
        )
    if intent["goal"] == "matrix":
        job = (
            f" sGAG/histologia em {winner['n_sgag_papers']} papers destas células — ranking dentro do paper, não um score 0–100."
            if pt
            else f" sGAG/histology in {winner['n_sgag_papers']} papers of these cells — within-paper rank, not a 0–100 score."
        )
    tail = (
        " Isto não substitui o próximo frasco."
        if pt
        else " This does not replace the next flask."
    )
    return core + extra + job + tail


def _paper_payload(rows: list[dict], limit: int = 3) -> list[dict]:
    ranked = sorted(
        rows,
        key=lambda r: (
            0 if r.get("viability_pct") is not None else 1,
            0 if r.get("stiffness_kpa") is not None else 1,
            -(r.get("year") or 0),
        ),
    )
    out = []
    seen = set()
    for row in ranked:
        key = row.get("study_id") or row.get("doi")
        if key in seen:
            continue
        seen.add(key)
        out.append(
            {
                "study_id": row.get("study_id"),
                "citation": row.get("citation") or row.get("study_id"),
                "doi": row.get("doi"),
                "year": row.get("year"),
                "material_class": row.get("material_class"),
                "material_detail": row.get("material_detail"),
                "cell_type": row.get("cell_type"),
                "stiffness_kpa": row.get("stiffness_kpa"),
                "growth_factor": row.get("growth_factor") or "none",
                "culture_time_days": row.get("culture_time_days"),
                "culture_model": row.get("culture_model"),
                "architecture": row.get("architecture"),
                "application": row.get("application"),
                "polymer_concentration_wt_pct": row.get("polymer_concentration_wt_pct"),
                "viability_pct": row.get("viability_pct"),
                "qualitative_label": row.get("qualitative_label"),
            }
        )
        if len(out) >= limit:
            break
    return out


def find_protocol(
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
    if goal not in GOALS:
        goal = "alive"
    if how not in HOW:
        how = "encapsulate"
    if tgf not in TGF_CHOICES:
        tgf = "either"
    if site not in SITES:
        site = "any"
    if cell_type not in {
        "articular_chondrocyte",
        "auricular_chondrocyte",
        "nasal_chondrocyte",
        "MSC",
        "adipose_MSC",
    }:
        cell_type = "articular_chondrocyte"

    evidence = list_viability_evidence(path)
    if site != "any":
        evidence = [r for r in evidence if r.get("application") == site]
    numeric = load_viability(path)
    sgag = _sgag_index(path)

    present = {r.get("material_class") for r in evidence}
    if stock and stock not in {"", "any"}:
        pool = [stock] if stock in LAB_GELS else [FIELD_DEFAULT]
        if FIELD_DEFAULT not in pool:
            pool.append(FIELD_DEFAULT)
    else:
        pool = [g for g in LAB_GELS if g in present]
        if FIELD_DEFAULT not in pool:
            pool.insert(0, FIELD_DEFAULT)

    ranked = []
    for material in pool:
        stats = _candidate_stats(material, cell_type, evidence, numeric, sgag)
        stats["avoid"] = _avoid(stats)
        stats["score"] = _score(stats, goal, how)
        ranked.append(stats)
    ranked.sort(key=lambda s: (s["avoid"], -s["score"], s["material_class"]))

    usable = [s for s in ranked if not s["avoid"] and s["n_same"] > 0]
    winner = usable[0] if usable else ranked[0]
    stock_warning = None
    if stock and stock not in {"", "any"}:
        held = next((s for s in ranked if s["material_class"] == stock), None)
        if held and held["avoid"] and usable and winner["material_class"] != stock:
            mean_s = "n/d" if held["same_mean"] is None else f"{held['same_mean']:.0f}%"
            stock_warning = (
                f"Tens {stock} no frigorífico, mas o live/dead extraído nestas células é {mean_s} — não comeces por aí."
                if lang == "pt"
                else f"You stock {stock}, but extracted live/dead in these cells is {mean_s} — do not start there."
            )
    field = next((s for s in ranked if s["material_class"] == FIELD_DEFAULT), None)

    gf = _pick_gf(winner, tgf)
    recipe = _pick_recipe(winner, how)
    if recipe:
        if tgf == "either":
            gf = recipe.get("growth_factor") or gf
        kpa = recipe.get("stiffness_kpa")
        days = recipe.get("culture_time_days") or _typical_days(how)
        culture_model = recipe.get("culture_model") or (
            "3D_bioprint" if how == "print" else "3D_encapsulation"
        )
    else:
        kpa = _typical_kpa(winner, how)
        days = _typical_days(how)
        culture_model = "3D_bioprint" if how == "print" else "3D_encapsulation"
    query = {
        "material_class": winner["material_class"],
        "cell_type": cell_type,
        "growth_factor": gf,
        "stiffness_kpa": kpa,
        "culture_time_days": days,
        "culture_model": culture_model,
    }
    est = shrinkage_estimate(query, numeric) if not numeric.empty else {"mean": None, "n_eff_same": 0}

    others = []
    for stats in ranked:
        if stats["material_class"] == winner["material_class"]:
            continue
        others.append(
            {
                "material_class": stats["material_class"],
                "same_mean": stats["same_mean"],
                "n_same_numeric": stats["n_same_numeric"],
                "n_same_qual": stats["n_same_qual"],
                "n_papers_same": stats["n_papers_same"],
                "n_print_same": stats["n_print_same"],
                "n_sgag_papers": stats["n_sgag_papers"],
                "avoid": stats["avoid"],
                "typical_kpa": _typical_kpa(stats, how),
            }
        )
        if len(others) >= 5:
            break

    intent = {
        "cell_type": cell_type,
        "goal": goal,
        "how": how,
        "tgf": tgf,
        "stock": stock or "any",
        "site": site,
    }
    return {
        "intent": intent,
        "protocol": {
            "material_class": winner["material_class"],
            "stiffness_kpa": kpa,
            "culture_time_days": days,
            "growth_factor": gf,
            "cell_type": cell_type,
            "culture_model": culture_model,
        },
        "recipe": recipe,
        "same_mean": winner["same_mean"],
        "same_min": winner["same_min"],
        "n_same_numeric": winner["n_same_numeric"],
        "n_same_qual": winner["n_same_qual"],
        "n_papers_same": winner["n_papers_same"],
        "n_print_same": winner["n_print_same"],
        "n_sgag_papers": winner["n_sgag_papers"],
        "avoid": winner["avoid"],
        "shrinkage_mean": None if est.get("mean") is None else round(float(est["mean"]), 1),
        "n_eff_same": round(float(est.get("n_eff_same") or 0), 1),
        "why": _why(winner, field, intent, lang=lang),
        "stock_warning": stock_warning,
        "papers": _paper_payload(winner.get("all_rows") or []),
        "alternatives": others,
        "field_default": None
        if field is None
        else {
            "material_class": field["material_class"],
            "same_mean": field["same_mean"],
            "n_same_numeric": field["n_same_numeric"],
            "n_same_qual": field["n_same_qual"],
            "n_papers_same": field["n_papers_same"],
        },
    }

"""Search harvested papers, then Europe PMC, for the PI's question.

Retrieval only. Does not extract numbers or write a protocol.
"""

from __future__ import annotations

import re
from functools import lru_cache

from tissuelab.db import connect
from tissuelab.europepmc import hit_to_record, search as epmc_search
from tissuelab.paths import DB_PATH

CELL_TERMS = {
    "articular_chondrocyte": ("chondrocyte", "articular cartilage"),
    "auricular_chondrocyte": ("auricular chondrocyte", "chondrocyte"),
    "MSC": ("mesenchymal stem", "MSC chondrogen"),
    "adipose_MSC": ("adipose stem", "ADSC", "ASC chondro"),
}

GOAL_TERMS = {
    "alive": ("viability", "live/dead"),
    "print": ("bioprint", "bioink"),
    "matrix": ("chondrogenesis", "sGAG", "glycosaminoglycan"),
}

GEL_TERMS = {
    "GelMA": "GelMA",
    "fibrin": "fibrin",
    "HA": "hyaluronic",
    "alginate": "alginate",
    "chitosan": "chitosan",
    "collagen": "collagen",
    "gelatin_alginate": "gelatin alginate",
    "GelMA_HA": "GelMA hyaluronic",
    "silk_fibrin": "silk fibrin",
    "agarose": "agarose",
    "PEG": "PEG hydrogel",
}


def _extracted_keys(path=DB_PATH) -> tuple[set[str], set[str]]:
    conn = connect(path)
    dois = {
        str(r[0]).lower()
        for r in conn.execute(
            "SELECT doi FROM studies WHERE doi IS NOT NULL AND study_id NOT LIKE 'pmid%'"
        ).fetchall()
    }
    pmids = {
        str(r[0])
        for r in conn.execute(
            "SELECT pmid FROM studies WHERE pmid IS NOT NULL AND study_id NOT LIKE 'pmid%'"
        ).fetchall()
    }
    conn.close()
    return dois, pmids


def build_query(cell_type: str, goal: str, material: str | None = None) -> str:
    cell = CELL_TERMS.get(cell_type, ("chondrocyte",))[0]
    goal_t = GOAL_TERMS.get(goal, ("hydrogel",))[0]
    gel = GEL_TERMS.get(material or "", "") or "hydrogel"
    return f"{cell} {gel} {goal_t}"


def _like_clause(terms: list[str]) -> tuple[str, list[str]]:
    parts = []
    params: list[str] = []
    for term in terms:
        token = re.sub(r"[^a-zA-Z0-9 /+-]", "", term).strip()
        if len(token) < 3:
            continue
        parts.append("(LOWER(COALESCE(title,'')) LIKE ? OR LOWER(COALESCE(abstract,'')) LIKE ?)")
        needle = f"%{token.lower()}%"
        params.extend([needle, needle])
    if not parts:
        parts = ["LOWER(COALESCE(title,'')) LIKE ?"]
        params = ["%chondrocyte%"]
    return " AND ".join(parts), params


def search_harvested(
    *,
    cell_type: str,
    goal: str,
    material: str | None = None,
    limit: int = 8,
    path=DB_PATH,
) -> list[dict]:
    cell_terms = list(CELL_TERMS.get(cell_type, ("chondrocyte",)))[:1]
    goal_terms = list(GOAL_TERMS.get(goal, ("viability",)))[:1]
    gel = GEL_TERMS.get(material or "", "")
    terms = cell_terms + ([gel] if gel else ["hydrogel"]) + goal_terms
    where, params = _like_clause(terms)
    conn = connect(path)
    sql = f"""
        SELECT pmid, doi, title, journal, year, citation_count, has_fulltext
        FROM papers
        WHERE COALESCE(is_retracted, 0) = 0
          AND {where}
        ORDER BY COALESCE(citation_count, 0) DESC, COALESCE(year, 0) DESC
        LIMIT ?
    """
    rows = conn.execute(sql, [*params, int(limit)]).fetchall()
    conn.close()
    dois, pmids = _extracted_keys(path)
    out = []
    for pmid, doi, title, journal, year, cites, ft in rows:
        doi_s = None if doi is None else str(doi)
        pmid_s = None if pmid is None else str(pmid)
        out.append(
            {
                "pmid": pmid_s,
                "doi": doi_s,
                "title": title,
                "journal": journal,
                "year": year,
                "citation_count": cites,
                "has_fulltext": bool(ft),
                "extracted": (doi_s or "").lower() in dois or (pmid_s or "") in pmids,
                "source": "harvest",
            }
        )
    return out


def search_europepmc(query: str, limit: int = 8, path=DB_PATH) -> list[dict]:
    payload = epmc_search(query, page_size=limit)
    hits = ((payload.get("resultList") or {}).get("result")) or []
    dois, pmids = _extracted_keys(path)
    out = []
    for hit in hits[:limit]:
        rec = hit_to_record(hit)
        doi = rec.get("doi")
        pmid = rec.get("pmid")
        year = rec.get("publicationDate")
        out.append(
            {
                "pmid": pmid,
                "doi": doi,
                "title": rec.get("title"),
                "journal": rec.get("journal"),
                "year": None if not year else str(year)[:4],
                "citation_count": rec.get("citationCount"),
                "has_fulltext": bool(rec.get("hasFulltext") or rec.get("pmcid")),
                "extracted": (str(doi).lower() if doi else "") in dois or (pmid or "") in pmids,
                "source": "europepmc",
            }
        )
    return out


@lru_cache(maxsize=32)
def search_question(
    cell_type: str,
    goal: str,
    material: str | None,
    live: bool = False,
    limit: int = 8,
) -> dict:
    query = build_query(cell_type, goal, material)
    harvested = search_harvested(cell_type=cell_type, goal=goal, material=material, limit=limit)
    live_hits: list[dict] = []
    live_error = None
    if live:
        try:
            live_hits = search_europepmc(query + " AND (hydrogel OR bioink)", limit=limit)
        except Exception as exc:  # noqa: BLE001 — surface a search miss, do not crash the page
            live_error = str(exc)[:200]
    return {
        "query": query,
        "harvested": harvested,
        "europepmc": live_hits,
        "live_error": live_error,
    }

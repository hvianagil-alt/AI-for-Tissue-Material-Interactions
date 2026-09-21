"""Promote high-signal Amass papers into low-confidence experimental rows.

Uses title+abstract always. Optionally pulls Amass fulltext for the best
candidates, extracts numbers, then discards the article body (not stored).
Does not overwrite hand-curated studies.
"""

from __future__ import annotations

import json
import time
import urllib.error
import urllib.request
from datetime import datetime, timezone

from tissuelab.curated import STUDIES
from tissuelab.db import VOCAB_MATERIALS, connect, init_schema
from tissuelab.extract import extract_conditions
from tissuelab.harvest_amass import api_key, load_dotenv
from tissuelab.paths import DATA_DIR, DB_PATH, PROMOTED_PATH
from tissuelab.rank_papers import is_review, normalize_doi

GET_URL = "https://api.amass.tech/api/v1/cores/biomedcore/records/{amass_id}?include=fulltext"
MAX_FULLTEXT = 90
FULLTEXT_SLEEP = 1.15
ALLOWED_MATERIALS = {row[0] for row in VOCAB_MATERIALS}


def _citation(paper: dict) -> str:
    authors = paper.get("authors")
    names = []
    if authors:
        try:
            names = json.loads(authors) if isinstance(authors, str) else authors
        except json.JSONDecodeError:
            names = []
    first = names[0] if names else "Unknown"
    year = paper.get("year") or ""
    journal = paper.get("journal") or "journal"
    return f"{first} et al., {journal} {year}".strip()


def _curated_dois() -> set[str]:
    out = set()
    for study in STUDIES:
        doi = normalize_doi(study.get("doi"))
        if doi:
            out.add(doi)
    return out


def _candidate_ids(conn) -> list[str]:
    sql = """
    SELECT p.amass_id, p.has_fulltext, COALESCE(s.score, 0) AS score
    FROM papers p
    LEFT JOIN paper_scores s ON s.amass_id = p.amass_id
    LEFT JOIN paper_extractions v
      ON v.amass_id = p.amass_id AND v.field = 'viability_pct' AND v.value_num BETWEEN 40 AND 99.5
    WHERE p.pmid IS NOT NULL
      AND p.abstract IS NOT NULL
      AND length(p.abstract) > 80
      AND COALESCE(s.is_review, 0) = 0
      AND COALESCE(s.already_curated, 0) = 0
      AND v.extraction_id IS NOT NULL
    GROUP BY p.amass_id
    ORDER BY (p.has_fulltext = 1) DESC, score DESC
    """
    return [row[0] for row in conn.execute(sql).fetchall()]


CACHE_DIR = DATA_DIR / "fulltext_cache"


def fetch_fulltext(key: str, amass_id: str) -> str | None:
    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    cached = CACHE_DIR / f"{amass_id}.txt"
    if cached.exists():
        text = cached.read_text(errors="replace")
        return text[:80000] if len(text) >= 200 else None
    url = GET_URL.format(amass_id=amass_id)
    req = urllib.request.Request(url, headers={"Authorization": f"Bearer {key}"})
    try:
        with urllib.request.urlopen(req, timeout=90) as resp:
            body = json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        if exc.code == 429:
            retry = exc.headers.get("Retry-After", "8")
            wait = int(float(retry)) if str(retry).replace(".", "", 1).isdigit() else 8
            time.sleep(wait + 1)
            return fetch_fulltext(key, amass_id)
        return None
    rec = body.get("data") or {}
    text = rec.get("fulltext")
    if not text or len(text) < 200:
        return None
    text = text[:80000]
    cached.write_text(text)
    return text


def promote_paper(paper: dict, extra: str | None) -> dict | None:
    if is_review(paper.get("publication_types")):
        return None
    pmid = paper.get("pmid")
    if not pmid:
        return None
    conditions = extract_conditions(paper.get("title"), paper.get("abstract"), extra)
    usable = [c for c in conditions if c["material_class"] in ALLOWED_MATERIALS]
    paired = [c for c in usable if c.get("paired_stiffness")]
    if extra and paired:
        usable = paired[:6]
    elif extra:
        usable = usable[:3]
    else:
        usable = usable[:2]
    if not usable:
        return None
    study_id = f"pmid{pmid}"
    source = "abstract+fulltext" if extra else "abstract"
    study = {
        "study_id": study_id,
        "citation": _citation(paper),
        "doi": paper.get("doi"),
        "year": paper.get("year"),
        "journal": paper.get("journal"),
        "pmcid": paper.get("pmcid"),
        "license": "amass_index",
        "tissue_focus": "cartilage",
        "notes": f"Auto-promoted from {source}; numbers need human review.",
    }
    experiments = []
    for i, cond in enumerate(usable, start=1):
        exp_id = f"{study_id}-c{i}"
        span = (cond.get("evidence_span") or "")[:180]
        experiments.append(
            {
                "experiment_id": exp_id,
                "study_id": study_id,
                "material_class": cond["material_class"],
                "material_detail": cond.get("material_detail"),
                "stiffness_kpa": cond.get("stiffness_kpa"),
                "stiffness_method": "text_kPa" if cond.get("stiffness_kpa") else None,
                "tissue": "cartilage",
                "cell_type": cond["cell_type"],
                "species": cond.get("species"),
                "culture_model": cond.get("culture_model"),
                "growth_factor": cond.get("growth_factor") or "none",
                "culture_time_days": cond.get("culture_time_days"),
                "extracted_from": source,
                "curator_confidence": "medium" if cond.get("paired_stiffness") else "low",
                "notes": span,
                "amass_id": paper.get("amass_id"),
                "measurements": [
                    {
                        "assay": "viability_pct",
                        "value": cond["viability_pct"],
                        "unit": "%",
                        "evidence": "numeric_text",
                        "notes": f"{source}: {span}",
                    }
                ],
            }
        )
    return {"study": study, "experiments": experiments}


def ingest(path=DB_PATH, fetch=True) -> dict:
    load_dotenv()
    conn = connect(path)
    init_schema(conn)
    curated = _curated_dois()
    ids = _candidate_ids(conn)
    papers = {
        row["amass_id"]: dict(row)
        for row in conn.execute("SELECT * FROM papers").fetchall()
    }
    want_fulltext = []
    for amass_id in ids:
        paper = papers.get(amass_id)
        if not paper:
            continue
        if paper.get("has_fulltext") and fetch:
            want_fulltext.append(amass_id)
        if len(want_fulltext) >= MAX_FULLTEXT:
            break

    key = api_key() if fetch and want_fulltext else None
    fulltexts: dict[str, str] = {}
    for i, amass_id in enumerate(want_fulltext, start=1):
        text = fetch_fulltext(key, amass_id)
        if text:
            fulltexts[amass_id] = text
        print(f"fulltext [{i}/{len(want_fulltext)}] {amass_id} chars={len(text or '')}", flush=True)
        time.sleep(FULLTEXT_SLEEP)

    promoted_studies = []
    promoted_experiments = []
    seen_study = set()
    for amass_id in ids:
        paper = papers.get(amass_id)
        if not paper:
            continue
        doi = normalize_doi(paper.get("doi"))
        if doi and doi in curated:
            continue
        bundle = promote_paper(paper, fulltexts.get(amass_id))
        if not bundle:
            continue
        study_id = bundle["study"]["study_id"]
        if study_id in seen_study:
            continue
        seen_study.add(study_id)
        promoted_studies.append(bundle["study"])
        promoted_experiments.extend(bundle["experiments"])

    payload = {
        "generated_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "n_candidates": len(ids),
        "n_fulltext_fetched": len(fulltexts),
        "n_studies": len(promoted_studies),
        "n_experiments": len(promoted_experiments),
        "n_with_stiffness": sum(1 for e in promoted_experiments if e.get("stiffness_kpa") is not None),
        "studies": promoted_studies,
        "experiments": promoted_experiments,
        "notes": [
            "Low/medium confidence auto-promotion from abstracts and selected fulltext.",
            "Do not treat as a hand-curated table. Leave-one-paper-out still required.",
            "Full article text was not written to disk.",
        ],
    }
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    PROMOTED_PATH.write_text(json.dumps(payload, indent=2, ensure_ascii=False))
    conn.close()
    return {k: v for k, v in payload.items() if k not in {"studies", "experiments"}}


def load_promoted() -> tuple[list[dict], list[dict]]:
    if not PROMOTED_PATH.exists():
        return [], []
    payload = json.loads(PROMOTED_PATH.read_text())
    return payload.get("studies") or [], payload.get("experiments") or []


def main() -> None:
    report = ingest()
    print(json.dumps(report, indent=2))
    print(f"Wrote {PROMOTED_PATH}")


if __name__ == "__main__":
    main()

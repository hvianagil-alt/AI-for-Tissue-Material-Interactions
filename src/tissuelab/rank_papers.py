"""Rank harvested papers for the next human extraction pass.

8k abstracts are a retrieval index. The model needs labeled experiments.
This module scores papers for extractability and writes extraction_queue.
It never copies regex numbers into measurements.
"""

from __future__ import annotations

import json
from datetime import datetime, timezone

import pandas as pd

from tissuelab.db import connect, init_schema
from tissuelab.paths import DATA_DIR, DB_PATH, EXTRACTION_QUEUE_PATH, QUALITY_REPORT_PATH

REVIEW_MARKERS = ("review", "systematic review", "meta-analysis")
QUEUE_SIZE = 250


def normalize_doi(value: str | None) -> str | None:
    if not value:
        return None
    doi = value.strip().lower()
    for prefix in ("https://doi.org/", "http://doi.org/", "https://dx.doi.org/", "http://dx.doi.org/"):
        if doi.startswith(prefix):
            doi = doi[len(prefix) :]
    doi = doi.strip().strip("/")
    return doi or None


def is_review(publication_types: object) -> bool:
    raw = publication_types
    if isinstance(raw, str):
        try:
            raw = json.loads(raw)
        except json.JSONDecodeError:
            raw = [raw]
    blob = " ".join(str(item) for item in (raw or [])).lower()
    return any(marker in blob for marker in REVIEW_MARKERS)


def score_paper(
    *,
    is_rev: bool,
    already_curated: bool,
    cells: set[str],
    materials: set[str],
    has_scaffold: bool,
    has_cartilage: bool,
    has_viability_number: bool,
    has_stiffness_number: bool,
    has_fulltext: bool,
    citation_count: int | None,
    has_culture_days: bool,
    has_tgf: bool,
) -> tuple[float, list[str], bool]:
    score = 0.0
    reasons: list[str] = []
    if already_curated:
        score -= 50
        reasons.append("already_curated")
    if is_rev:
        score -= 18
        reasons.append("review")
    if "articular_chondrocyte" in cells or "nasal_chondrocyte" in cells:
        score += 25
        reasons.append("chondrocyte")
    if "MSC" in cells:
        score += 12
        reasons.append("MSC")
    if materials:
        score += 15 + min(9.0, 3.0 * (len(materials) - 1))
        reasons.append("material:" + ",".join(sorted(materials)[:4]))
    if has_scaffold:
        score += 8
        reasons.append("hydrogel_or_bioink")
    if has_cartilage:
        score += 8
        reasons.append("cartilage")
    if has_viability_number:
        score += 32
        reasons.append("abstract_viability_%")
    if has_stiffness_number:
        score += 22
        reasons.append("abstract_kPa")
    if has_culture_days:
        score += 4
        reasons.append("culture_days")
    if has_tgf:
        score += 6
        reasons.append("TGF_b3")
    if has_fulltext:
        score += 10
        reasons.append("amass_fulltext_flag")
    if citation_count and citation_count >= 80:
        score += 5
        reasons.append("well_cited")
    mvp = (
        not is_rev
        and not already_curated
        and has_scaffold
        and (
            has_cartilage
            or "articular_chondrocyte" in cells
            or "nasal_chondrocyte" in cells
            or "auricular_chondrocyte" in cells
            or "MSC" in cells
        )
        and bool(materials or has_viability_number or has_stiffness_number)
    )
    if mvp:
        reasons.append("mvp_relevant")
    return score, reasons, mvp


def link_curated_studies(conn) -> int:
    conn.execute("DELETE FROM study_paper_links")
    doi_index = {}
    pmc_index = {}
    pmid_index = {}
    for paper in conn.execute("SELECT amass_id, doi, pmcid, pmid FROM papers"):
        doi = normalize_doi(paper["doi"])
        if doi:
            doi_index[doi] = paper["amass_id"]
        if paper["pmcid"]:
            pmc_index[str(paper["pmcid"]).upper()] = paper["amass_id"]
        if paper["pmid"]:
            pmid_index[str(paper["pmid"])] = paper["amass_id"]
    n = 0
    study_cols = {row[1] for row in conn.execute("PRAGMA table_info(studies)")}
    select_pmid = ", pmid" if "pmid" in study_cols else ""
    for study in conn.execute(
        f"SELECT study_id, doi, pmcid{select_pmid} FROM studies WHERE study_id NOT LIKE 'pmid%'"
    ):
        amass_id = None
        matched_on = None
        doi = normalize_doi(study["doi"])
        if doi and doi in doi_index:
            amass_id = doi_index[doi]
            matched_on = "doi"
        elif study["pmcid"] and str(study["pmcid"]).upper() in pmc_index:
            amass_id = pmc_index[str(study["pmcid"]).upper()]
            matched_on = "pmcid"
        elif "pmid" in study_cols and study["pmid"] and str(study["pmid"]) in pmid_index:
            amass_id = pmid_index[str(study["pmid"])]
            matched_on = "pmid"
        if not amass_id:
            continue
        conn.execute(
            "INSERT OR REPLACE INTO study_paper_links (study_id, amass_id, matched_on) VALUES (?, ?, ?)",
            (study["study_id"], amass_id, matched_on),
        )
        n += 1
    return n


def rank(path=DB_PATH) -> dict:
    conn = connect(path)
    init_schema(conn)
    n_links = link_curated_studies(conn)
    curated_ids = {
        r[0] for r in conn.execute("SELECT amass_id FROM study_paper_links").fetchall()
    }

    by_paper: dict[str, list] = {}
    for row in conn.execute(
        "SELECT amass_id, field, value_text, value_num FROM paper_extractions"
    ):
        by_paper.setdefault(row["amass_id"], []).append(row)

    analyses: dict[str, dict] = {}
    holes: list[dict] = []
    gap_boost = None
    try:
        from tissuelab.product import product_gap_boost, research_queue

        holes = research_queue(path, limit=12)
        gap_boost = product_gap_boost
    except Exception:
        holes = []
    tables = {r[0] for r in conn.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()}
    if "paper_analyses" in tables:
        for row in conn.execute("SELECT * FROM paper_analyses"):
            analyses[row["amass_id"]] = dict(row)

    conn.execute("DELETE FROM paper_scores")
    conn.execute("DELETE FROM extraction_queue")
    now = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    scored_rows = []
    for paper in conn.execute(
        """
        SELECT amass_id, pmid, doi, title, year, journal, citation_count,
               has_fulltext, publication_types
        FROM papers
        """
    ):
        ext = by_paper.get(paper["amass_id"], [])
        cells = {e["value_text"] for e in ext if e["field"] == "cell_type" and e["value_text"]}
        materials = {e["value_text"] for e in ext if e["field"] == "material_class" and e["value_text"]}
        fields = {e["field"] for e in ext}
        has_viab = any(e["field"] == "viability_pct" and e["value_num"] is not None for e in ext)
        has_stiff = any(e["field"] == "stiffness_kpa" and e["value_num"] is not None for e in ext)
        review = is_review(paper["publication_types"])
        score, reasons, mvp = score_paper(
            is_rev=review,
            already_curated=paper["amass_id"] in curated_ids,
            cells=cells,
            materials=materials,
            has_scaffold="scaffold_class" in fields,
            has_cartilage="tissue" in fields,
            has_viability_number=has_viab,
            has_stiffness_number=has_stiff,
            has_fulltext=bool(paper["has_fulltext"]),
            citation_count=paper["citation_count"],
            has_culture_days="culture_time_days" in fields,
            has_tgf="growth_factor" in fields,
        )
        if gap_boost and (cells or materials):
            bonus, gap_reasons = gap_boost(materials, cells, holes)
            score += bonus
            reasons.extend(gap_reasons)
        analysis = analyses.get(paper["amass_id"])
        if analysis:
            if int(analysis["training_relevant"] or 0):
                score += 8
                reasons.append("uniform_training_relevant")
            chem = analysis["chemical_modification"]
            if chem and chem not in {"unmodified", "unspecified"}:
                score += 3
                reasons.append("chem:" + str(chem))
            arch = analysis["architecture"]
            if arch and arch not in {"bulk_hydrogel"}:
                score += 3
                reasons.append("arch:" + str(arch))
            app = analysis["application"]
            if app and app not in {"unspecified", "in_vitro_cartilage"}:
                score += 2
                reasons.append("app:" + str(app))
        conn.execute(
            """
            INSERT INTO paper_scores (
                amass_id, score, is_review, is_mvp_relevant, already_curated,
                has_chondrocyte, has_msc, has_mapped_material, has_viability_number,
                has_stiffness_number, n_materials, reasons, scored_at
            ) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?)
            """,
            (
                paper["amass_id"],
                score,
                1 if review else 0,
                1 if mvp else 0,
                1 if paper["amass_id"] in curated_ids else 0,
                1 if "articular_chondrocyte" in cells else 0,
                1 if "MSC" in cells else 0,
                1 if materials else 0,
                1 if has_viab else 0,
                1 if has_stiff else 0,
                len(materials),
                json.dumps(reasons),
                now,
            ),
        )
        if mvp and paper["amass_id"] not in curated_ids:
            scored_rows.append((score, paper, reasons))

    scored_rows.sort(key=lambda item: (-item[0], -(item[1]["citation_count"] or 0)))
    for rank_i, (score, paper, reasons) in enumerate(scored_rows[:QUEUE_SIZE], start=1):
        conn.execute(
            """
            INSERT INTO extraction_queue (
                amass_id, rank, score, status, why, pmid, doi, title, year,
                journal, citation_count, has_fulltext
            ) VALUES (?,?,?,?,?,?,?,?,?,?,?,?)
            """,
            (
                paper["amass_id"],
                rank_i,
                score,
                "queued",
                json.dumps(reasons),
                paper["pmid"],
                paper["doi"],
                paper["title"],
                paper["year"],
                paper["journal"],
                paper["citation_count"],
                paper["has_fulltext"],
            ),
        )
    conn.commit()

    report = {
        "n_papers_scored": conn.execute("SELECT COUNT(*) FROM paper_scores").fetchone()[0],
        "n_mvp_relevant": conn.execute(
            "SELECT COUNT(*) FROM paper_scores WHERE is_mvp_relevant = 1"
        ).fetchone()[0],
        "n_reviews": conn.execute("SELECT COUNT(*) FROM paper_scores WHERE is_review = 1").fetchone()[0],
        "n_already_curated_linked": n_links,
        "n_queued": conn.execute("SELECT COUNT(*) FROM extraction_queue").fetchone()[0],
        "n_extracted_excluded_from_queue": n_links,
        "n_queue_with_viability_number": conn.execute(
            """
            SELECT COUNT(*) FROM extraction_queue q
            JOIN paper_scores s USING (amass_id)
            WHERE s.has_viability_number = 1
            """
        ).fetchone()[0],
        "n_queue_with_stiffness_number": conn.execute(
            """
            SELECT COUNT(*) FROM extraction_queue q
            JOIN paper_scores s USING (amass_id)
            WHERE s.has_stiffness_number = 1
            """
        ).fetchone()[0],
        "note": "Queue is a reading list. Extract into experiments/measurements by hand; do not promote regex hits.",
    }
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    queue = pd.read_sql_query(
        """
        SELECT q.rank, q.score, q.status, q.pmid, q.doi, q.year, q.journal,
               q.citation_count, q.has_fulltext, q.title, q.why, q.amass_id
        FROM extraction_queue q
        ORDER BY q.rank
        """,
        conn,
    )
    queue.to_csv(EXTRACTION_QUEUE_PATH, index=False)
    if QUALITY_REPORT_PATH.exists():
        quality = json.loads(QUALITY_REPORT_PATH.read_text())
        quality.update({"extraction_queue": report})
        QUALITY_REPORT_PATH.write_text(json.dumps(quality, indent=2))
    conn.close()
    return report


def main() -> None:
    report = rank()
    print(json.dumps(report, indent=2))
    print(f"Wrote {EXTRACTION_QUEUE_PATH}")


if __name__ == "__main__":
    main()

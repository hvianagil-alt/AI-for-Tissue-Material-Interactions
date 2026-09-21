"""Harvest BiomedCore papers into SQLite via the Amass HTTP API.

Does not print or log the API key. Does not overwrite curated experiments.
Regex extractions stay in paper_extractions, never copied into measurements.
"""

from __future__ import annotations

import json
import os
import sqlite3
import time
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime, timezone
from typing import Any

from tissuelab.db import connect, init_schema
from tissuelab.extract import extract_from_abstract
from tissuelab.paths import DATA_DIR, DB_PATH, ROOT

BASE = "https://api.amass.tech/api/v1/cores/biomedcore/records"
SEARCH_LIMIT = 300
TARGET_UNIQUE = 8000
MAX_REQUESTS = 40
MIN_SLEEP_S = 1.15


def load_dotenv() -> None:
    path = ROOT / ".env"
    if not path.exists():
        return
    for line in path.read_text().splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        os.environ.setdefault(key.strip(), value.strip().strip("'").strip('"'))


def api_key() -> str:
    load_dotenv()
    key = os.environ.get("AMASS_API_KEY", "").strip()
    if not key or not key.startswith("amass_") or "cole_aqui" in key:
        raise SystemExit("AMASS_API_KEY missing or still a placeholder. Put it in .env.")
    return key


def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _year(date: str | None) -> int | None:
    if not date:
        return None
    try:
        return int(date[:4])
    except ValueError:
        return None


def _dumps(value: Any) -> str | None:
    if value is None:
        return None
    return json.dumps(value, ensure_ascii=False)


YEAR_WINDOWS: list[tuple[str, str]] = [
    ("2004-01-01", "2007-12-31"),
    ("2008-01-01", "2010-12-31"),
    ("2011-01-01", "2013-12-31"),
    ("2014-01-01", "2015-12-31"),
    ("2016-01-01", "2017-12-31"),
    ("2018-01-01", "2019-12-31"),
    ("2020-01-01", "2020-12-31"),
    ("2021-01-01", "2021-12-31"),
    ("2022-01-01", "2022-12-31"),
    ("2023-01-01", "2023-12-31"),
    ("2024-01-01", "2024-12-31"),
    ("2025-01-01", "2025-12-31"),
    ("2026-01-01", "2026-12-31"),
]

CORE_QUERIES = [
    "chondrocyte hydrogel",
    "cartilage hydrogel tissue engineering",
    "MSC chondrogenesis hydrogel",
    "chondrocyte live dead hydrogel",
]

MATERIAL_QUERIES = [
    "GelMA chondrocyte",
    "alginate hydrogel chondrocyte",
    "hyaluronic acid hydrogel chondrocyte",
    "PEG hydrogel chondrocyte cartilage",
    "collagen hydrogel chondrocyte",
    "fibrin hydrogel chondrocyte",
    "chitosan hydrogel cartilage",
    "agarose chondrocyte hydrogel",
    "silk fibroin cartilage hydrogel",
    "cartilage bioink hydrogel",
]


def search_plan() -> list[dict[str, str | None]]:
    plan: list[dict[str, str | None]] = []
    for query in CORE_QUERIES:
        for lo, hi in YEAR_WINDOWS:
            plan.append(
                {
                    "query": query,
                    "minPublicationDate": lo,
                    "maxPublicationDate": hi,
                }
            )
    for query in MATERIAL_QUERIES:
        plan.append({"query": query, "minPublicationDate": None, "maxPublicationDate": None})
    return plan


def search(key: str, query: str, min_date: str | None, max_date: str | None, limit: int) -> tuple[list[dict], int, int | None]:
    params: list[tuple[str, str]] = [
        ("query", query),
        ("limit", str(limit)),
        ("isRetracted", "false"),
    ]
    if min_date:
        params.append(("minPublicationDate", min_date))
    if max_date:
        params.append(("maxPublicationDate", max_date))
    url = BASE + "?" + urllib.parse.urlencode(params)
    req = urllib.request.Request(url, headers={"Authorization": f"Bearer {key}"})
    try:
        with urllib.request.urlopen(req, timeout=90) as resp:
            body = json.loads(resp.read().decode("utf-8"))
            cost_h = resp.headers.get("X-Amass-Credit-Cost")
            cost = int(cost_h) if cost_h and str(cost_h).isdigit() else None
            remaining = resp.headers.get("X-RateLimit-Remaining")
            status = resp.status
    except urllib.error.HTTPError as exc:
        payload = exc.read().decode("utf-8", errors="replace")
        if exc.code == 429:
            retry = exc.headers.get("Retry-After", "8")
            wait = int(float(retry)) if str(retry).replace(".", "", 1).isdigit() else 8
            time.sleep(wait + 1)
            return search(key, query, min_date, max_date, limit)
        raise SystemExit(f"Amass HTTP {exc.code}: {payload[:400]}") from exc
    if "error" in body:
        raise SystemExit(f"Amass error: {body['error']}")
    records = body.get("data") or []
    remaining_n = int(remaining) if remaining and str(remaining).isdigit() else None
    if remaining_n is not None and remaining_n < 8:
        time.sleep(8)
    return records, status, cost


def upsert_paper(conn: sqlite3.Connection, rec: dict, query_key: str) -> bool:
    amass_id = rec.get("amassId")
    if not amass_id:
        return False
    existing = conn.execute(
        "SELECT query_hits FROM papers WHERE amass_id = ?", (amass_id,)
    ).fetchone()
    if existing:
        hits = []
        if existing["query_hits"]:
            try:
                hits = json.loads(existing["query_hits"])
            except json.JSONDecodeError:
                hits = []
        if query_key not in hits:
            hits.append(query_key)
            conn.execute(
                "UPDATE papers SET query_hits = ? WHERE amass_id = ?",
                (json.dumps(hits), amass_id),
            )
        return False
    conn.execute(
        """
        INSERT INTO papers (
            amass_id, pmid, pmcid, doi, title, abstract, journal, publication_date,
            year, citation_count, journal_quality_jufo, has_fulltext, is_retracted,
            publication_types, mesh_terms, keywords, substances, authors, language,
            query_hits, harvested_at
        ) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)
        """,
        (
            amass_id,
            rec.get("pmid"),
            rec.get("pmcid"),
            rec.get("doi"),
            rec.get("title"),
            rec.get("abstract"),
            rec.get("journal"),
            rec.get("publicationDate"),
            _year(rec.get("publicationDate")),
            rec.get("citationCount"),
            rec.get("journalQualityJufo"),
            1 if rec.get("hasFulltext") else 0,
            1 if rec.get("isRetracted") else 0,
            _dumps(rec.get("publicationTypes")),
            _dumps(rec.get("meshTerms")),
            _dumps(rec.get("keywords")),
            _dumps(rec.get("substances")),
            _dumps(rec.get("authors")),
            rec.get("language"),
            json.dumps([query_key]),
            _now(),
        ),
    )
    for row in extract_from_abstract(rec.get("abstract"), rec.get("title")):
        conn.execute(
            """
            INSERT INTO paper_extractions (
                amass_id, field, value_text, value_num, unit, evidence_span, extractor, confidence
            ) VALUES (?, ?, ?, ?, ?, ?, 'regex_abstract', ?)
            """,
            (
                amass_id,
                row["field"],
                row["value_text"],
                row["value_num"],
                row["unit"],
                row["evidence_span"],
                row["confidence"],
            ),
        )
    return True


def harvest_report(conn: sqlite3.Connection) -> dict[str, Any]:
    n_papers = conn.execute("SELECT COUNT(*) FROM papers").fetchone()[0]
    n_abs = conn.execute(
        "SELECT COUNT(*) FROM papers WHERE abstract IS NOT NULL AND length(abstract) > 40"
    ).fetchone()[0]
    n_ext = conn.execute("SELECT COUNT(*) FROM paper_extractions").fetchone()[0]
    by_year = dict(
        conn.execute(
            "SELECT year, COUNT(*) FROM papers WHERE year IS NOT NULL GROUP BY year ORDER BY year"
        ).fetchall()
    )
    by_field = dict(
        conn.execute("SELECT field, COUNT(*) FROM paper_extractions GROUP BY field").fetchall()
    )
    n_viab = conn.execute(
        "SELECT COUNT(DISTINCT amass_id) FROM paper_extractions WHERE field = 'viability_pct' AND value_num IS NOT NULL"
    ).fetchone()[0]
    n_stiff = conn.execute(
        "SELECT COUNT(DISTINCT amass_id) FROM paper_extractions WHERE field = 'stiffness_kpa'"
    ).fetchone()[0]
    n_chond = conn.execute(
        "SELECT COUNT(DISTINCT amass_id) FROM paper_extractions WHERE field = 'cell_type' AND value_text = 'articular_chondrocyte'"
    ).fetchone()[0]
    n_mat = conn.execute(
        "SELECT COUNT(DISTINCT amass_id) FROM paper_extractions WHERE field = 'material_class'"
    ).fetchone()[0]
    top_journals = [
        {"journal": j, "n": n}
        for j, n in conn.execute(
            """
            SELECT COALESCE(journal, '(unknown)'), COUNT(*) AS n
            FROM papers GROUP BY journal ORDER BY n DESC LIMIT 15
            """
        ).fetchall()
    ]
    return {
        "n_papers": n_papers,
        "n_with_abstract": n_abs,
        "n_extractions": n_ext,
        "n_papers_with_viability_mention": n_viab,
        "n_papers_with_stiffness_mention": n_stiff,
        "n_papers_mentioning_chondrocyte": n_chond,
        "n_papers_with_mapped_material": n_mat,
        "papers_per_year": by_year,
        "extractions_per_field": by_field,
        "top_journals": top_journals,
        "notes": [
            "papers are Amass BiomedCore search hits, not curated experiments.",
            "paper_extractions are regex candidates from title+abstract; confidence is low for numbers.",
            "Do not train the viability model on paper_extractions.",
            "Curated numeric outcomes remain in experiments/measurements.",
        ],
    }


def export_tables(conn: sqlite3.Connection) -> None:
    import pandas as pd

    DATA_DIR.mkdir(parents=True, exist_ok=True)
    papers = pd.read_sql_query(
        """
        SELECT amass_id, pmid, pmcid, doi, title, journal, publication_date, year,
               citation_count, journal_quality_jufo, has_fulltext, is_retracted, language
        FROM papers
        ORDER BY year DESC, citation_count DESC
        """,
        conn,
    )
    papers.to_csv(DATA_DIR / "amass_papers.csv", index=False)
    ext = pd.read_sql_query("SELECT * FROM paper_extractions", conn)
    ext.to_csv(DATA_DIR / "amass_extractions.csv", index=False)
    (DATA_DIR / "amass_harvest_report.json").write_text(
        json.dumps(harvest_report(conn), indent=2)
    )


def already_ran(conn, query: str, lo: str | None, hi: str | None) -> bool:
    row = conn.execute(
        """
        SELECT 1 FROM harvest_log
        WHERE query = ?
          AND COALESCE(min_publication_date, '') = COALESCE(?, '')
          AND COALESCE(max_publication_date, '') = COALESCE(?, '')
        LIMIT 1
        """,
        (query, lo, hi),
    ).fetchone()
    return row is not None


def run(path=DB_PATH) -> dict[str, Any]:
    key = api_key()
    conn = connect(path)
    init_schema(conn)
    plan = search_plan()
    requests_done = 0
    for item in plan:
        n_unique = conn.execute("SELECT COUNT(*) FROM papers").fetchone()[0]
        if n_unique >= TARGET_UNIQUE or requests_done >= MAX_REQUESTS:
            break
        query = str(item["query"])
        lo = item.get("minPublicationDate")
        hi = item.get("maxPublicationDate")
        if already_ran(conn, query, lo, hi):
            continue
        query_key = f"{query}|{lo or '*'}|{hi or '*'}"
        records, status, cost = search(key, query, lo, hi, SEARCH_LIMIT)
        n_new = 0
        for rec in records:
            if rec.get("isRetracted"):
                continue
            if upsert_paper(conn, rec, query_key):
                n_new += 1
        conn.execute(
            """
            INSERT INTO harvest_log (
                query, min_publication_date, max_publication_date, limit_requested,
                n_returned, n_new, http_status, credit_cost, requested_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (query, lo, hi, SEARCH_LIMIT, len(records), n_new, status, cost, _now()),
        )
        conn.commit()
        requests_done += 1
        print(
            f"[{requests_done}] {query_key} returned={len(records)} new={n_new} "
            f"unique={conn.execute('SELECT COUNT(*) FROM papers').fetchone()[0]}",
            flush=True,
        )
        time.sleep(MIN_SLEEP_S)
    report = harvest_report(conn)
    export_tables(conn)
    conn.close()
    return report


def main() -> None:
    report = run()
    print(json.dumps({k: v for k, v in report.items() if k != "papers_per_year"}, indent=2))
    print(f"n_papers={report['n_papers']}")


if __name__ == "__main__":
    main()

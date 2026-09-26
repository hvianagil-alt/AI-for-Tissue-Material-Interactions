"""Uniformize every harvested paper: chemistry, architecture, application.

Writes paper_analyses. Does not copy numbers into measurements.
"""

from __future__ import annotations

import json
from datetime import datetime, timezone

import pandas as pd

from tissuelab.db import connect, init_schema
from tissuelab.extract import CARTILAGE_RE, HYDROGEL_RE, cells_in, materials_in, pick_culture_model, pick_species
from tissuelab.ontology import analyze_text, training_relevant
from tissuelab.paths import DATA_DIR, DB_PATH

ANALYSES_CSV = DATA_DIR / "paper_analyses.csv"


def analyze_paper(paper: dict, extraction_fields: dict[str, list]) -> dict:
    title = paper.get("title")
    abstract = paper.get("abstract")
    tags = analyze_text(title, abstract)
    blob = " ".join(p for p in (title, abstract) if p)
    materials = materials_in(blob)
    cells = cells_in(blob)
    viab = extraction_fields.get("viability_pct") or []
    has_hydrogel = bool(HYDROGEL_RE.search(blob) or materials)
    has_cell = bool(cells) or bool(CARTILAGE_RE.search(blob))
    has_viab = bool(viab)
    return {
        "amass_id": paper["amass_id"],
        "chemical_modification": tags["chemical_modification"],
        "chemical_modifications": json.dumps(tags["chemical_modifications"]),
        "architecture": tags["architecture"],
        "architectures": json.dumps(tags["architectures"]),
        "application": tags["application"],
        "applications": json.dumps(tags["applications"]),
        "materials": json.dumps(materials),
        "cells": json.dumps(cells),
        "culture_model": pick_culture_model(blob) if blob else None,
        "species": pick_species(blob),
        "growth_factor": (extraction_fields.get("growth_factor") or [None])[0],
        "is_review_like": 1 if tags["is_review_like"] else 0,
        "has_hydrogel": 1 if has_hydrogel else 0,
        "has_cartilage_cell": 1 if has_cell else 0,
        "has_viability_number": 1 if has_viab else 0,
        "training_relevant": 1
        if training_relevant(tags, has_hydrogel=has_hydrogel, has_cartilage_cell=has_cell, has_viability=has_viab)
        else 0,
        "n_viability_hits": len(viab),
        "analyzed_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
    }


def run(path=DB_PATH) -> dict:
    conn = connect(path)
    init_schema(conn)
    fields: dict[str, dict[str, list]] = {}
    for row in conn.execute("SELECT amass_id, field, value_text, value_num FROM paper_extractions"):
        bucket = fields.setdefault(row["amass_id"], {})
        val = row["value_text"] if row["value_text"] is not None else row["value_num"]
        bucket.setdefault(row["field"], []).append(val)
    papers = list(conn.execute("SELECT amass_id, title, abstract FROM papers"))
    conn.execute("DELETE FROM paper_analyses")
    n = 0
    relevant = 0
    for paper in papers:
        rec = analyze_paper(dict(paper), fields.get(paper["amass_id"]) or {})
        conn.execute(
            """
            INSERT INTO paper_analyses (
                amass_id, chemical_modification, chemical_modifications,
                architecture, architectures, application, applications,
                materials, cells, culture_model, species, growth_factor,
                is_review_like, has_hydrogel, has_cartilage_cell, has_viability_number,
                training_relevant, n_viability_hits, analyzed_at
            ) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)
            """,
            (
                rec["amass_id"],
                rec["chemical_modification"],
                rec["chemical_modifications"],
                rec["architecture"],
                rec["architectures"],
                rec["application"],
                rec["applications"],
                rec["materials"],
                rec["cells"],
                rec["culture_model"],
                rec["species"],
                rec["growth_factor"],
                rec["is_review_like"],
                rec["has_hydrogel"],
                rec["has_cartilage_cell"],
                rec["has_viability_number"],
                rec["training_relevant"],
                rec["n_viability_hits"],
                rec["analyzed_at"],
            ),
        )
        n += 1
        relevant += rec["training_relevant"]
    conn.commit()
    by_app = dict(conn.execute("SELECT application, COUNT(*) FROM paper_analyses GROUP BY 1 ORDER BY 2 DESC").fetchall())
    by_chem = dict(
        conn.execute("SELECT chemical_modification, COUNT(*) FROM paper_analyses GROUP BY 1 ORDER BY 2 DESC").fetchall()
    )
    by_arch = dict(conn.execute("SELECT architecture, COUNT(*) FROM paper_analyses GROUP BY 1 ORDER BY 2 DESC").fetchall())
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    frame = pd.read_sql_query(
        """
        SELECT a.*, p.pmid, p.doi, p.year, p.title, p.journal
        FROM paper_analyses a
        JOIN papers p USING (amass_id)
        ORDER BY a.training_relevant DESC, a.has_viability_number DESC, p.year DESC
        """,
        conn,
    )
    frame.to_csv(ANALYSES_CSV, index=False)
    relevant_frame = frame[frame["training_relevant"] == 1] if not frame.empty else frame
    relevant_frame.to_csv(DATA_DIR / "paper_analyses_train_relevant.csv", index=False)
    conn.close()
    return {
        "n_analyzed": n,
        "n_training_relevant": relevant,
        "by_application": by_app,
        "by_chemistry": by_chem,
        "by_architecture": by_arch,
        "csv": str(ANALYSES_CSV),
    }


def main() -> None:
    report = run()
    print(json.dumps(report, indent=2, default=str))


if __name__ == "__main__":
    main()

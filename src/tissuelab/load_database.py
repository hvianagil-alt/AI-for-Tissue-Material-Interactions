"""Load curated literature into SQLite and export a native CSV."""

from __future__ import annotations

import json
import sqlite3
from pathlib import Path

import pandas as pd

from tissuelab.curated import EXPERIMENTS, STUDIES
from tissuelab.db import connect, init_schema
from tissuelab.ingest_literature import load_promoted
from tissuelab.ontology import tag_experiment
from tissuelab.paths import DATA_DIR, DB_PATH, NATIVE_EXPORT_PATH, QUALITY_REPORT_PATH, VIABILITY_EXPORT_PATH
from tissuelab.rank_papers import normalize_doi

STUDY_SKIP_KEYS = {"amass_id"}

HARVEST_TABLES = (
    "papers",
    "paper_extractions",
    "harvest_log",
    "paper_scores",
    "extraction_queue",
    "study_paper_links",
    "paper_analyses",
)

EXP_COLUMNS = [
    "experiment_id",
    "study_id",
    "material_class",
    "material_detail",
    "crosslinking",
    "polymer_concentration_wt_pct",
    "stiffness_kpa",
    "stiffness_sd_kpa",
    "stiffness_method",
    "porosity_pct",
    "degradation_half_life_days",
    "surface_chemistry",
    "has_adhesion_ligand",
    "tissue",
    "cell_type",
    "species",
    "culture_model",
    "growth_factor",
    "culture_time_days",
    "cell_density_million_per_ml",
    "passage",
    "chemical_modification",
    "architecture",
    "application",
    "live_dead_kit",
    "modification_degree_pct",
    "n_replicates",
    "extracted_from",
    "curator_confidence",
    "notes",
]


def quality_report(conn) -> dict:
    n_studies = conn.execute("SELECT COUNT(*) FROM studies").fetchone()[0]
    n_exp = conn.execute("SELECT COUNT(*) FROM experiments").fetchone()[0]
    n_meas = conn.execute("SELECT COUNT(*) FROM measurements").fetchone()[0]
    n_viab = conn.execute("SELECT COUNT(*) FROM v_model_viability").fetchone()[0]
    n_auto_viab = 0
    tables = {r[0] for r in conn.execute("SELECT name FROM sqlite_master WHERE type='view'").fetchall()}
    if "v_auto_viability" in tables:
        n_auto_viab = conn.execute("SELECT COUNT(*) FROM v_auto_viability").fetchone()[0]
    n_hand = conn.execute("SELECT COUNT(*) FROM studies WHERE study_id NOT LIKE 'pmid%'").fetchone()[0]
    n_hand_viab_studies = conn.execute("SELECT COUNT(DISTINCT study_id) FROM v_model_viability").fetchone()[0]
    n_stiff = conn.execute("SELECT COUNT(*) FROM experiments WHERE stiffness_kpa IS NOT NULL").fetchone()[0]
    by_study = dict(conn.execute("SELECT study_id, COUNT(*) FROM experiments GROUP BY study_id").fetchall())
    by_cell = dict(conn.execute("SELECT cell_type, COUNT(*) FROM experiments GROUP BY cell_type").fetchall())
    by_assay = dict(conn.execute("SELECT assay, COUNT(*) FROM measurements GROUP BY assay").fetchall())
    by_evidence = dict(conn.execute("SELECT evidence, COUNT(*) FROM measurements GROUP BY evidence").fetchall())
    missing = {}
    for col in ("stiffness_kpa", "polymer_concentration_wt_pct", "species", "passage", "porosity_pct"):
        missing[col] = conn.execute(
            f"SELECT ROUND(100.0 * AVG({col} IS NULL), 1) FROM experiments"
        ).fetchone()[0]
    # Leakage warning: small n_studies means study-level CV is the only honest split.
    report = {
        "n_studies": n_studies,
        "n_experiments": n_exp,
        "n_measurements": n_meas,
        "n_numeric_viability": n_viab,
        "n_auto_promoted_viability": n_auto_viab,
        "n_hand_studies": n_hand,
        "n_hand_viability_studies": n_hand_viab_studies,
        "n_with_stiffness_kpa": n_stiff,
        "experiments_per_study": by_study,
        "experiments_per_cell_type": by_cell,
        "measurements_per_assay": by_assay,
        "measurements_per_evidence": by_evidence,
        "percent_missing": missing,
        "modeling_notes": [
            "Split by study_id (leave-one-paper-out), never by random row — conditions from one paper leak.",
            "Train viability models only on v_model_viability (hand-curated numeric live/dead).",
            "Do not impute missing stiffness as 0; keep NA and use models that allow missing values or restrict to complete cases.",
            "Ordinal histology is within-paper rank, not a universal 0–1 scale — do not pool as if it were sGAG/DNA.",
            "New cell types add vocab_cell_types + assays; they do not get new columns on experiments.",
            "Amass papers live in `papers`; regex hits in `paper_extractions` are not training labels.",
            "Auto-promoted pmid* studies are inventory only; they are excluded from v_model_viability.",
        ],
    }
    tables = {
        r[0] for r in conn.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()
    }
    if "papers" in tables:
        report["n_amass_papers"] = conn.execute("SELECT COUNT(*) FROM papers").fetchone()[0]
        report["n_amass_extractions"] = conn.execute("SELECT COUNT(*) FROM paper_extractions").fetchone()[0]
    if "extraction_queue" in tables:
        report["n_extraction_queue"] = conn.execute("SELECT COUNT(*) FROM extraction_queue").fetchone()[0]
        report["n_mvp_relevant_papers"] = conn.execute(
            "SELECT COUNT(*) FROM paper_scores WHERE is_mvp_relevant = 1"
        ).fetchone()[0]
    if "paper_analyses" in tables:
        report["n_paper_analyses"] = conn.execute("SELECT COUNT(*) FROM paper_analyses").fetchone()[0]
        report["n_training_relevant_papers"] = conn.execute(
            "SELECT COUNT(*) FROM paper_analyses WHERE training_relevant = 1"
        ).fetchone()[0]
        report["analyses_per_application"] = dict(
            conn.execute(
                "SELECT COALESCE(application,'(none)'), COUNT(*) FROM paper_analyses GROUP BY 1"
            ).fetchall()
        )
        report["analyses_per_chemistry"] = dict(
            conn.execute(
                "SELECT COALESCE(chemical_modification,'(none)'), COUNT(*) FROM paper_analyses GROUP BY 1"
            ).fetchall()
        )
    report["n_auto_promoted_studies"] = conn.execute(
        "SELECT COUNT(*) FROM studies WHERE study_id LIKE 'pmid%'"
    ).fetchone()[0]
    return report


def snapshot_harvest(path) -> dict | None:
    if not path.exists():
        return None
    raw = sqlite3.connect(path)
    raw.row_factory = sqlite3.Row
    try:
        names = {r[0] for r in raw.execute("SELECT name FROM sqlite_master WHERE type='table'")}
        if "papers" not in names:
            return None
        snap = {}
        for table in HARVEST_TABLES:
            if table in names:
                snap[table] = [dict(row) for row in raw.execute(f"SELECT * FROM {table}").fetchall()]
            else:
                snap[table] = []
        return snap
    except sqlite3.Error:
        return None
    finally:
        raw.close()


def restore_harvest(conn, snap: dict | None) -> None:
    if not snap:
        return
    conn.execute("PRAGMA foreign_keys = OFF")
    for table in HARVEST_TABLES:
        rows = snap.get(table) or []
        for row in rows:
            cols = ",".join(row.keys())
            placeholders = ",".join(["?"] * len(row))
            conn.execute(
                f"INSERT OR REPLACE INTO {table} ({cols}) VALUES ({placeholders})",
                tuple(row.values()),
            )
    conn.execute("PRAGMA foreign_keys = ON")


def _hand_curated_keys() -> tuple[set[str], set[str], set[str]]:
    dois: set[str] = set()
    pmcids: set[str] = set()
    pmids: set[str] = set()
    for study in STUDIES:
        doi = normalize_doi(study.get("doi"))
        if doi:
            dois.add(doi)
        if study.get("pmcid"):
            pmc = str(study["pmcid"]).upper()
            if not pmc.startswith("PMC"):
                pmc = "PMC" + pmc
            pmcids.add(pmc)
        if study.get("pmid"):
            pmids.add(str(study["pmid"]))
    return dois, pmcids, pmids


def _normalize_pmcid(value) -> str | None:
    if not value:
        return None
    pmc = str(value).upper()
    if not pmc.startswith("PMC"):
        pmc = "PMC" + pmc
    return pmc


def overlaps_hand_curated(study: dict, dois: set[str], pmcids: set[str], pmids: set[str]) -> bool:
    """True when an auto-promoted pmid* row is the same paper as a hand study."""
    sid = str(study.get("study_id") or "")
    if sid.startswith("pmid") and sid[4:] in pmids:
        return True
    doi = normalize_doi(study.get("doi"))
    if doi and doi in dois:
        return True
    pmc = _normalize_pmcid(study.get("pmcid"))
    return bool(pmc and pmc in pmcids)


def drop_hand_overlapped_promoted(studies: list[dict], experiments: list[dict]) -> tuple[list[dict], list[dict]]:
    dois, pmcids, pmids = _hand_curated_keys()
    kept_studies = []
    skip_ids = set()
    for study in studies:
        if overlaps_hand_curated(study, dois, pmcids, pmids):
            skip_ids.add(study["study_id"])
            continue
        kept_studies.append(study)
    kept_experiments = [exp for exp in experiments if exp.get("study_id") not in skip_ids]
    return kept_studies, kept_experiments


def load(path=DB_PATH):
    snap = snapshot_harvest(path)
    if path.exists():
        path.unlink()
    conn = connect(path)
    init_schema(conn)
    promoted_studies, promoted_experiments = drop_hand_overlapped_promoted(*load_promoted())
    all_studies = list(STUDIES) + promoted_studies
    all_experiments = list(EXPERIMENTS) + promoted_experiments
    seen_study = set()
    for study in all_studies:
        if study["study_id"] in seen_study:
            continue
        seen_study.add(study["study_id"])
        payload = {k: v for k, v in study.items() if k not in STUDY_SKIP_KEYS}
        cols = ",".join(payload.keys())
        placeholders = ",".join(["?"] * len(payload))
        conn.execute(f"INSERT INTO studies ({cols}) VALUES ({placeholders})", tuple(payload.values()))
    seen_exp = set()
    study_index = {study["study_id"]: study for study in all_studies}
    for exp in all_experiments:
        if exp["experiment_id"] in seen_exp:
            continue
        seen_exp.add(exp["experiment_id"])
        tagged = tag_experiment(exp, study_index.get(exp.get("study_id")))
        payload = {key: tagged.get(key) for key in EXP_COLUMNS}
        payload["tissue"] = payload.get("tissue") or "cartilage"
        cols = ",".join(payload.keys())
        placeholders = ",".join(["?"] * len(payload))
        conn.execute(f"INSERT INTO experiments ({cols}) VALUES ({placeholders})", tuple(payload.values()))
        for meas in exp["measurements"]:
            conn.execute(
                """
                INSERT INTO measurements (experiment_id, assay, value, value_sd, unit, qualitative_label, evidence, n, notes)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    exp["experiment_id"],
                    meas["assay"],
                    meas.get("value"),
                    meas.get("value_sd"),
                    meas["unit"],
                    meas.get("qualitative_label"),
                    meas["evidence"],
                    meas.get("n"),
                    meas.get("notes"),
                ),
            )
    restore_harvest(conn, snap)
    conn.commit()
    report = quality_report(conn)
    if Path(path).resolve() == DB_PATH.resolve():
        DATA_DIR.mkdir(parents=True, exist_ok=True)
        QUALITY_REPORT_PATH.write_text(json.dumps(report, indent=2))
        native = pd.read_sql_query(
            """
            SELECT e.*, m.assay, m.value, m.value_sd, m.unit, m.qualitative_label, m.evidence
            FROM experiments e
            JOIN measurements m USING (experiment_id)
            """,
            conn,
        )
        native.to_csv(NATIVE_EXPORT_PATH, index=False)
        viability = pd.read_sql_query("SELECT * FROM v_model_viability", conn)
        viability.to_csv(VIABILITY_EXPORT_PATH, index=False)
        from tissuelab.training_pack import export_pack

        export_pack(path)
    conn.close()
    return report


def main() -> None:
    report = load()
    print(f"Wrote {DB_PATH}")
    print(f"Wrote {NATIVE_EXPORT_PATH}")
    print(f"Wrote {VIABILITY_EXPORT_PATH}")
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()

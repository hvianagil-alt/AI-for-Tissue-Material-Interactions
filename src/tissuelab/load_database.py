"""Load curated literature into SQLite and export a native CSV."""

from __future__ import annotations

import json

import pandas as pd

from tissuelab.curated import EXPERIMENTS, STUDIES
from tissuelab.db import connect, init_schema
from tissuelab.paths import DATA_DIR, DB_PATH, NATIVE_EXPORT_PATH, QUALITY_REPORT_PATH

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
    return {
        "n_studies": n_studies,
        "n_experiments": n_exp,
        "n_measurements": n_meas,
        "n_numeric_viability": n_viab,
        "n_with_stiffness_kpa": n_stiff,
        "experiments_per_study": by_study,
        "experiments_per_cell_type": by_cell,
        "measurements_per_assay": by_assay,
        "measurements_per_evidence": by_evidence,
        "percent_missing": missing,
        "modeling_notes": [
            "Split by study_id (leave-one-paper-out), never by random row — conditions from one paper leak.",
            "Train viability models only on v_model_viability (numeric live/dead).",
            "Do not impute missing stiffness as 0; keep NA and use models that allow missing values or restrict to complete cases.",
            "Ordinal histology is within-paper rank, not a universal 0–1 scale — do not pool as if it were sGAG/DNA.",
            "New cell types add vocab_cell_types + assays; they do not get new columns on experiments.",
        ],
    }


def load(path=DB_PATH):
    if path.exists():
        path.unlink()
    conn = connect(path)
    init_schema(conn)
    for study in STUDIES:
        cols = ",".join(study.keys())
        placeholders = ",".join(["?"] * len(study))
        conn.execute(f"INSERT INTO studies ({cols}) VALUES ({placeholders})", tuple(study.values()))
    for exp in EXPERIMENTS:
        payload = {key: exp.get(key) for key in EXP_COLUMNS}
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
    conn.commit()
    report = quality_report(conn)
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
    conn.close()
    return report


def main() -> None:
    report = load()
    print(f"Wrote {DB_PATH}")
    print(f"Wrote {NATIVE_EXPORT_PATH}")
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()

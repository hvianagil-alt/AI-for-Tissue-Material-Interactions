"""Write a clean, documented pack the next model can actually train on.

Gold = hand-curated live/dead (`v_model_viability`). Silver = auto-promoted
regex rows (`v_auto_viability`) — inventory only. Paper tags are features
for retrieval, not viability labels.
"""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd

from tissuelab.db import connect
from tissuelab.ontology import APP_PRIORITY, ARCH_PRIORITY, CHEM_PRIORITY
from tissuelab.paths import (
    DATA_DIR,
    DB_PATH,
    FEATURE_CODEBOOK_PATH,
    GOLD_TRAIN_PATH,
    PAPERS_UNIFORM_PATH,
    SILVER_TRAIN_PATH,
    TRAINING_PACK_README,
)

GOLD_COLUMNS = [
    "experiment_id",
    "study_id",
    "citation",
    "doi",
    "material_class",
    "chemical_modification",
    "architecture",
    "application",
    "stiffness_kpa",
    "polymer_concentration_wt_pct",
    "cell_type",
    "species",
    "culture_model",
    "growth_factor",
    "culture_time_days",
    "cell_density_million_per_ml",
    "passage",
    "has_adhesion_ligand",
    "live_dead_kit",
    "curator_confidence",
    "viability_pct",
    "viability_sd",
    "viability_evidence",
    "label_source",
    "split_group",
]

UNIFORM_COLUMNS = [
    "amass_id",
    "pmid",
    "doi",
    "year",
    "title",
    "journal",
    "chemical_modification",
    "architecture",
    "application",
    "culture_model",
    "species",
    "growth_factor",
    "materials",
    "cells",
    "is_review_like",
    "has_hydrogel",
    "has_cartilage_cell",
    "has_viability_number",
    "training_relevant",
    "n_viability_hits",
]


def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _table_exists(conn, name: str) -> bool:
    row = conn.execute(
        "SELECT 1 FROM sqlite_master WHERE type IN ('table','view') AND name = ?",
        (name,),
    ).fetchone()
    return row is not None


def _clean_gold(frame: pd.DataFrame) -> pd.DataFrame:
    if frame.empty:
        return pd.DataFrame(columns=GOLD_COLUMNS)
    out = frame.copy()
    out["label_source"] = "hand_curated"
    out["split_group"] = out["study_id"].astype(str)
    out = out[~out["study_id"].astype(str).str.startswith("pmid")]
    out["viability_pct"] = pd.to_numeric(out["viability_pct"], errors="coerce")
    out = out[out["viability_pct"].notna() & out["viability_pct"].between(0, 100)]
    for col in ("chemical_modification", "architecture", "application", "growth_factor", "culture_model"):
        if col not in out.columns:
            out[col] = None
        out[col] = out[col].fillna("unspecified" if col == "application" else "unmodified" if col == "chemical_modification" else "")
    out["growth_factor"] = out["growth_factor"].replace({"": "none", "nan": "none"})
    present = [c for c in GOLD_COLUMNS if c in out.columns]
    return out[present].sort_values(["study_id", "experiment_id"]).reset_index(drop=True)


def _clean_silver(frame: pd.DataFrame) -> pd.DataFrame:
    if frame.empty:
        return pd.DataFrame(
            columns=["experiment_id", "study_id", "material_class", "stiffness_kpa", "viability_pct", "label_source"]
        )
    out = frame.copy()
    out["label_source"] = "auto_regex_do_not_train"
    out["viability_pct"] = pd.to_numeric(out["viability_pct"], errors="coerce")
    out = out[out["viability_pct"].notna() & out["viability_pct"].between(0, 100)]
    return out.sort_values(["study_id", "experiment_id"]).reset_index(drop=True)


def codebook() -> dict:
    return {
        "generated_at": _now(),
        "gold_path": str(GOLD_TRAIN_PATH.name),
        "silver_path": str(SILVER_TRAIN_PATH.name),
        "papers_uniform_path": str(PAPERS_UNIFORM_PATH.name),
        "split": "Leave-one-paper-out on split_group (= study_id). Never random row split.",
        "target": "viability_pct",
        "features": {
            "categorical": [
                "material_class",
                "cell_type",
                "growth_factor",
                "culture_model",
                "chemical_modification",
                "architecture",
                "application",
                "species",
            ],
            "numeric": [
                "stiffness_kpa",
                "polymer_concentration_wt_pct",
                "culture_time_days",
                "cell_density_million_per_ml",
                "passage",
                "has_adhesion_ligand",
            ],
            "do_not_impute_as_zero": ["stiffness_kpa", "polymer_concentration_wt_pct", "porosity_pct"],
        },
        "chemical_modification": ["unmodified", *CHEM_PRIORITY, "enzymatic"],
        "architecture": ["bulk_hydrogel", *ARCH_PRIORITY],
        "application": ["unspecified", *APP_PRIORITY],
        "notes": [
            "Gold labels are hand-typed live/dead percents from the paper.",
            "Silver (pmid*) is regex from abstracts/fulltext. Do not fit a viability model on it.",
            "papers_uniform.csv tags every harvested paper with the same chemistry/structure/application vocab.",
            "training_relevant=1 on a paper is a retrieval flag, not a viability label.",
        ],
    }


def _readme(gold: pd.DataFrame, silver: pd.DataFrame, papers: pd.DataFrame) -> str:
    n_studies = int(gold["study_id"].nunique()) if not gold.empty else 0
    n_chem = int((gold["chemical_modification"] != "").sum()) if not gold.empty and "chemical_modification" in gold.columns else 0
    n_rel = int(papers["training_relevant"].sum()) if not papers.empty and "training_relevant" in papers.columns else 0
    return f"""# Training pack

Generated {_now()}.

| File | Rows | Use |
|---|---|---|
| `train_gold.csv` | {len(gold)} conditions / {n_studies} papers | **Train** viability. Split by `split_group`. |
| `train_silver.csv` | {len(silver)} auto rows | Review queue only. **Do not train.** |
| `papers_uniform.csv` | {len(papers)} papers ({n_rel} training_relevant) | Chemistry / architecture / application tags. |
| `feature_codebook.json` | vocab | Same labels the analyzer used. |

Gold chemistry filled on {n_chem}/{len(gold)} rows.

```python
import pandas as pd
from sklearn.model_selection import LeaveOneGroupOut

gold = pd.read_csv("data/train_gold.csv")
y = gold["viability_pct"]
groups = gold["split_group"]
# LeaveOneGroupOut().split(gold, y, groups)
```

Amass abstracts without a typed live/dead number never enter `train_gold.csv`.
"""


def export_pack(path=DB_PATH, out_dir=None) -> dict:
    dest = Path(out_dir) if out_dir else DATA_DIR
    dest.mkdir(parents=True, exist_ok=True)
    gold_path = dest / GOLD_TRAIN_PATH.name
    silver_path = dest / SILVER_TRAIN_PATH.name
    papers_path = dest / PAPERS_UNIFORM_PATH.name
    codebook_path = dest / FEATURE_CODEBOOK_PATH.name
    readme_path = dest / TRAINING_PACK_README.name
    conn = connect(path)
    gold = pd.read_sql_query("SELECT * FROM v_model_viability", conn) if _table_exists(conn, "v_model_viability") else pd.DataFrame()
    silver = (
        pd.read_sql_query("SELECT * FROM v_auto_viability", conn)
        if _table_exists(conn, "v_auto_viability")
        else pd.DataFrame()
    )
    if _table_exists(conn, "paper_analyses") and _table_exists(conn, "papers"):
        papers = pd.read_sql_query(
            """
            SELECT a.amass_id, p.pmid, p.doi, p.year, p.title, p.journal,
                   a.chemical_modification, a.architecture, a.application,
                   a.culture_model, a.species, a.growth_factor, a.materials, a.cells,
                   a.is_review_like, a.has_hydrogel, a.has_cartilage_cell,
                   a.has_viability_number, a.training_relevant, a.n_viability_hits
            FROM paper_analyses a
            JOIN papers p USING (amass_id)
            ORDER BY a.training_relevant DESC, a.has_viability_number DESC, p.year DESC
            """,
            conn,
        )
    else:
        papers = pd.DataFrame(columns=UNIFORM_COLUMNS)
    conn.close()

    gold = _clean_gold(gold)
    silver = _clean_silver(silver)
    if not papers.empty:
        keep = [c for c in UNIFORM_COLUMNS if c in papers.columns]
        papers = papers[keep]

    gold.to_csv(gold_path, index=False)
    silver.to_csv(silver_path, index=False)
    papers.to_csv(papers_path, index=False)
    book = codebook()
    book["n_gold_rows"] = int(len(gold))
    book["n_gold_studies"] = int(gold["study_id"].nunique()) if not gold.empty else 0
    book["n_silver_rows"] = int(len(silver))
    book["n_papers_tagged"] = int(len(papers))
    book["n_training_relevant_papers"] = (
        int(papers["training_relevant"].sum()) if not papers.empty and "training_relevant" in papers.columns else 0
    )
    codebook_path.write_text(json.dumps(book, indent=2))
    readme_path.write_text(_readme(gold, silver, papers))
    return {
        "n_gold_rows": book["n_gold_rows"],
        "n_gold_studies": book["n_gold_studies"],
        "n_silver_rows": book["n_silver_rows"],
        "n_papers_tagged": book["n_papers_tagged"],
        "n_training_relevant_papers": book["n_training_relevant_papers"],
        "gold": str(gold_path),
        "silver": str(silver_path),
        "papers_uniform": str(papers_path),
        "codebook": str(codebook_path),
    }


def run(path=DB_PATH) -> dict:
    return export_pack(path)


def main() -> None:
    report = run()
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()

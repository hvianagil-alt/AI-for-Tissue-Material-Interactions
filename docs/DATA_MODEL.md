# Experimental database

## Decision

SQLite file: `data/tissuelab.sqlite`.

Not PostgreSQL. The blocker is **labeled experiments**, not a server. SQLite is a real relational database, portable, and enough until a lab is uploading rows daily.

## Layout (star / tidy)

```text
studies 1──* experiments 1──* measurements
              │
              ├── vocab_materials
              ├── vocab_cell_types
              └── vocab_assays
```

- **studies** — one paper. Split the ML data here (leave-one-paper-out). Random 80/20 on rows leaks the same gel series into train and test.
- **experiments** — one published condition. Features that the paper omitted are `NULL`, never `0`, never a guessed porosity.
- **measurements** — long form: `(assay, value, unit, evidence)`. Viability, sGAG, COL2/COL1, ALP (bone, later) are rows, not columns.
- **papers** — Amass BiomedCore harvest (title, abstract, identifiers). Not a training table.
- **paper_extractions** — regex candidates from title+abstract. Low-confidence numbers stay here; they are **not** copied into `measurements`.
- **paper_analyses** — one uniform tag set per paper (chemical modification, architecture, application). Not training labels.
- **paper_scores / extraction_queue** — which harvested papers to read next. A rank, not a measurement.
- **study_paper_links** — curated `study_id` ↔ Amass `amass_id` when DOI/PMCID matches.

That last point is the answer to “later we add more cell variables”. Osteoblast ALP is a new **assay + cell_type**, not a new column that breaks chondrocyte models. Filter `cell_type = articular_chondrocyte` and `assay = viability_pct` for the MVP.

## What is allowed into a model

| Use | Table / view | Why |
|---|---|---|
| Viability regressor | `v_model_viability` / `data/train_gold.csv` | Hand-curated numeric live/dead % only (`study_id NOT LIKE 'pmid%'`) |
| Uniform paper tags | `paper_analyses` / `data/papers_uniform.csv` | Chemistry, architecture, application. Not y. |
| Inventory of auto-promoted abstracts | `v_auto_viability` | pmid* rows; **not** training labels |
| Stiffness as a feature | experiments with `stiffness_kpa IS NOT NULL` | Complete-case or a missingness indicator |
| Histology ordinals | measurements `*_histology` | Within-paper rank only; do not treat as µg/µg |
| Simulated rows | **not in this database** | They are a software prior, not observations |
| Amass `papers` | literature index / retrieval | Abstracts + identifiers |
| `paper_extractions` | **not a model table** | Regex from abstracts; numbers are low-confidence |

CSV exports: `data/train_gold.csv` (and `literature_viability.csv`) is the training table. `data/papers_uniform.csv` is the tagged library. `data/literature_native.csv` is the long-form dump (includes inventory rows). Build them with `python3 -m tissuelab.training_pack`.

## How to start using it

1. Open `data/tissuelab.sqlite` (or the viability CSV) as the evidence table.
2. Predict published live/dead from a gel in Streamlit **Predict** — that number comes from `v_model_viability`, with ± LOPO MAE.
3. Read the nearest extracted papers, not the four-outcome radar, to pick the next gel.
4. Keep extracting `data/extraction_queue.csv` into `src/tissuelab/curated.py`. Harvested abstracts are already in SQLite; do not harvest more.

```bash
pip install -e .
tissuelab-app
```

Rebuild only if you changed `curated.py`:

```bash
python3 -m tissuelab.load_database
python3 -m tissuelab.rank_papers
python3 -m tissuelab.benchmark
```

## Evidence field

- `numeric_text` — a number in the paper (prefer this)
- `numeric_table` — a table
- `qualitative_text` — “high viability”, safranin-O ranking
- `figure_estimated` — read off a plot (must be flagged; we almost never use this)

## Leakage and confounding the schema is built to survive

1. **Study leakage** — several rows share a protocol, media, donor. Cross-validation grouping = `study_id`.
2. **Unit leakage** — sGAG/DNA from two kits are not one column without a `unit` and assay name.
3. **Missingness** — porosity was ~never reported; putting 80% everywhere would teach the model a fake feature.
4. **Target leakage** — do not put COL2A1 fold and “differentiation_score” derived from it in the same model as both X and y.

## MVP target

For now: **viability %** on cartilage hydrogels, because it is the only outcome with a shared unit and enough numeric rows. Differentiation/ECM stay in the DB as paper-native assays until there are enough `sgag_per_dna` values with the same kit, or we model ranks *within* a study.

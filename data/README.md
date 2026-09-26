# Data

| File | Role |
|---|---|
| `tissuelab.sqlite` | Source of truth. Curated studies/experiments/measurements plus Amass `papers`. |
| `literature_viability.csv` | Hand-curated numeric live/dead % (`v_model_viability`). Start here. |
| `train_gold.csv` | Same gold labels plus chemistry / architecture / application. **Train on this.** |
| `train_silver.csv` | Auto-promoted regex rows. Do not train. |
| `papers_uniform.csv` | Harvested papers tagged with one chemistry / structure / application vocab. |
| `paper_analyses.csv` | Full analyzer dump (all papers). |
| `literature_native.csv` | Long-form export of all measurements (hand + auto-promoted inventory). |
| `amass_papers.csv` | Harvest index (no abstracts — those stay in SQLite). |
| `amass_extractions.csv` | Regex candidates from abstracts. Not ground truth. |
| `amass_harvest_report.json` | Paper counts, year coverage, extraction tallies. |
| `promoted_literature.json` | Auto-extracted conditions from abstracts/fulltext. Low confidence. |
| `quality_report.json` | Counts, missingness, modeling notes. |
| `hydrogel_chondrocyte_records.csv` | Older mixed literature+simulator table for the v0.1 ML demo. Not scientific ground truth. |

Rebuild curated tables (keeps any Amass harvest already in the sqlite file):

```bash
python -m tissuelab.pipeline          # harvest → uniformize → ingest → gold CSV → LOPO
python -m tissuelab.load_database     # curated rebuild only
python -m tissuelab.training_pack     # rewrite train_gold.csv / papers_uniform.csv
python -m tissuelab.benchmark
```

Harvest BiomedCore (needs `AMASS_API_KEY` in `.env` or `.env.example`; billed search):

```bash
python -m tissuelab.harvest_amass
python -m tissuelab.europepmc
python -m tissuelab.rank_papers
python -m tissuelab.ingest_literature
```

```bash
python -m tissuelab.harvest_amass
```

See `docs/DATA_MODEL.md`.

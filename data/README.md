# Data

| File | Role |
|---|---|
| `tissuelab.sqlite` | Source of truth. Curated studies/experiments/measurements plus Amass `papers`. |
| `literature_viability.csv` | Hand-curated numeric live/dead % (`v_model_viability`). Start here. |
| `literature_native.csv` | Long-form export of all measurements (hand + auto-promoted inventory). |
| `amass_papers.csv` | Harvest index (no abstracts — those stay in SQLite). |
| `amass_extractions.csv` | Regex candidates from abstracts. Not ground truth. |
| `amass_harvest_report.json` | Paper counts, year coverage, extraction tallies. |
| `promoted_literature.json` | Auto-extracted conditions from abstracts/fulltext. Low confidence. |
| `quality_report.json` | Counts, missingness, modeling notes. |
| `hydrogel_chondrocyte_records.csv` | Older mixed literature+simulator table for the v0.1 ML demo. Not scientific ground truth. |

Rebuild curated tables (keeps any Amass harvest already in the sqlite file):

```bash
python -m tissuelab.load_database
python -m tissuelab.rank_papers
python -m tissuelab.benchmark
python -m tissuelab.train
```

Harvest BiomedCore (needs `AMASS_API_KEY` in `.env`; billed search):

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

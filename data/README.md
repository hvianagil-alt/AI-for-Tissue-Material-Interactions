# Data

| File | Role |
|---|---|
| `tissuelab.sqlite` | Source of truth. Studies, experiments, measurements. |
| `literature_native.csv` | Long-form export of the same measurements. |
| `quality_report.json` | Counts, missingness, modeling notes. |
| `hydrogel_chondrocyte_records.csv` | Older mixed literature+simulator table for the v0.1 ML demo. Not scientific ground truth. |

Rebuild the database:

```bash
python -m tissuelab.load_database
```

See `docs/DATA_MODEL.md`.

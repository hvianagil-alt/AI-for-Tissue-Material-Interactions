from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
DATA_DIR = ROOT / "data"
ARTIFACTS_DIR = ROOT / "artifacts"
DOCS_DIR = ROOT / "docs"

DATASET_PATH = DATA_DIR / "hydrogel_chondrocyte_records.csv"
DB_PATH = DATA_DIR / "tissuelab.sqlite"
SCHEMA_SQL_PATH = ROOT / "src" / "tissuelab" / "sql" / "schema.sql"
NATIVE_EXPORT_PATH = DATA_DIR / "literature_native.csv"
QUALITY_REPORT_PATH = DATA_DIR / "quality_report.json"
METRICS_PATH = ARTIFACTS_DIR / "metrics.json"
MODEL_PATH = ARTIFACTS_DIR / "tissue_interaction_model.joblib"

from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
DATA_DIR = ROOT / "data"
ARTIFACTS_DIR = ROOT / "artifacts"
DOCS_DIR = ROOT / "docs"

DATASET_PATH = DATA_DIR / "hydrogel_chondrocyte_records.csv"
DB_PATH = DATA_DIR / "tissuelab.sqlite"
SCHEMA_SQL_PATH = ROOT / "src" / "tissuelab" / "sql" / "schema.sql"
NATIVE_EXPORT_PATH = DATA_DIR / "literature_native.csv"
VIABILITY_EXPORT_PATH = DATA_DIR / "literature_viability.csv"
GOLD_TRAIN_PATH = DATA_DIR / "train_gold.csv"
SILVER_TRAIN_PATH = DATA_DIR / "train_silver.csv"
PAPERS_UNIFORM_PATH = DATA_DIR / "papers_uniform.csv"
FEATURE_CODEBOOK_PATH = DATA_DIR / "feature_codebook.json"
TRAINING_PACK_README = DATA_DIR / "TRAINING_PACK.md"
QUALITY_REPORT_PATH = DATA_DIR / "quality_report.json"
EXTRACTION_QUEUE_PATH = DATA_DIR / "extraction_queue.csv"
PROMOTED_PATH = DATA_DIR / "promoted_literature.json"
METRICS_PATH = ARTIFACTS_DIR / "metrics.json"
HONEST_METRICS_PATH = ARTIFACTS_DIR / "honest_benchmark.json"
MODEL_PATH = ARTIFACTS_DIR / "tissue_interaction_model.joblib"
LITERATURE_MODEL_PATH = ARTIFACTS_DIR / "literature_viability_model.joblib"

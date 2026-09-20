"""Train, evaluate, and serialize the Tissue Interaction Engine."""

from __future__ import annotations

import json

import joblib
import pandas as pd

from tissuelab.models import train_tissue_model
from tissuelab.paths import ARTIFACTS_DIR, DATASET_PATH, METRICS_PATH, MODEL_PATH
from tissuelab.schema import TARGETS


def load_dataset() -> pd.DataFrame:
    if not DATASET_PATH.exists():
        from tissuelab.build_dataset import main as build

        build()
    return pd.read_csv(DATASET_PATH)


def save_model(model, path=MODEL_PATH) -> None:
    ARTIFACTS_DIR.mkdir(parents=True, exist_ok=True)
    joblib.dump(model, path)


def load_model(path=MODEL_PATH):
    return joblib.load(path)


def main() -> None:
    frame = load_dataset()
    model = train_tissue_model(frame)
    save_model(model)
    METRICS_PATH.write_text(json.dumps(model.metrics, indent=2))
    print(f"Saved model to {MODEL_PATH}")
    print(f"Saved metrics to {METRICS_PATH}")
    print("\nHoldout XGBoost")
    for target, scores in model.metrics["xgboost_holdout"].items():
        print(f"  {target:24s}  MAE={scores['mae']:.2f}  R2={scores['r2']:.3f}")
    print("\nBaseline overall MAE")
    for name, report in model.metrics["baselines"].items():
        overall = report.get("overall") or report
        if "mae" in overall:
            extra = ""
            if name == "xgboost_sim_to_literature":
                extra = "  (train simulated → test literature)"
            print(f"  {name:28s}  MAE={overall['mae']:.2f}  R2={overall['r2']:.3f}{extra}")
        else:
            maes = [report[t]["mae"] for t in TARGETS if t in report]
            print(f"  {name:28s}  MAE={sum(maes)/len(maes):.2f}")


if __name__ == "__main__":
    main()

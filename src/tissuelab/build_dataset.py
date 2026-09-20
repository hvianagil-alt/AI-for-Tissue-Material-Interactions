"""Assemble the mixed literature + simulated dataset."""

from __future__ import annotations

import json

import pandas as pd

from tissuelab.features import records_to_frame
from tissuelab.literature import LITERATURE_RECORDS
from tissuelab.paths import DATA_DIR, DATASET_PATH
from tissuelab.schema import ExperimentRecord, FEATURE_COLUMNS, TARGETS
from tissuelab.simulator import simulate_dataframe

META_COLUMNS = ["record_id", "source", "citation", "doi", "year", "notes", "imputed_fields"]


def _validate_literature() -> pd.DataFrame:
    validated = [ExperimentRecord.model_validate(row).model_dump() for row in LITERATURE_RECORDS]
    frame = records_to_frame(validated)
    frame["imputed_fields"] = frame["imputed_fields"].apply(
        lambda value: json.dumps(value) if isinstance(value, list) else value
    )
    return frame


def build_dataset(n_simulated: int = 650, seed: int = 42) -> pd.DataFrame:
    literature = _validate_literature()
    simulated = simulate_dataframe(n=n_simulated, seed=seed)
    columns = FEATURE_COLUMNS + TARGETS + META_COLUMNS
    combined = pd.concat([literature[columns], simulated[columns]], ignore_index=True)
    return combined


def main() -> None:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    frame = build_dataset()
    frame.to_csv(DATASET_PATH, index=False)
    n_lit = int((frame["source"] == "literature").sum())
    n_sim = int((frame["source"] == "simulated_literature_informed").sum())
    print(f"Wrote {len(frame)} records to {DATASET_PATH} ({n_lit} literature, {n_sim} simulated).")


if __name__ == "__main__":
    main()

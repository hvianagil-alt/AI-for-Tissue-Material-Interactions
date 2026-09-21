# MVP notes

## Chosen MVP

```text
ONE tissue          cartilage
ONE material class  hydrogels
ONE cell context    articular chondrocytes (MSCs allowed as a feature)
ONE training label  numeric viability %  (other assays stay in the DB)
SUCCESS TEST        leave-one-paper-out vs dummy mean  (see docs/ROADMAP.md)
```

The Streamlit app already demos predict / inverse / next experiment. That is a **UI MVP**. The scientific MVP is a labeled table large enough that inverse design is not just the simulator talking to itself.

## User flow implemented

1. Researcher specifies hydrogel properties + biological context.
2. Model predicts four outcomes with 10–90% quantile intervals.
3. Nearest dataset rows (literature first when they are close) are shown as evidence.
4. Inverse design samples the feasible space under constraints.
5. “Next experiment” ranks designs by expected improvement on a chosen objective.

## What we are not building yet

- Virtual organ / multi-scale simulation
- Microscopy-native models
- Laboratory robot closed loop
- LLM-only extraction in production (seed records were curated)
- Training on Amass abstracts or regex percentages

## Data policy

Curated rows live in `experiments` / `measurements`. Amass hits live in `papers`. Regex lives in `paper_extractions`. Simulator rows are **not** in SQLite.

The next 200 rows come from `data/extraction_queue.csv`, typed by a human into `curated.py`. The queue excludes papers already linked to a hand-curated `study_id`.

Train viability only on `v_model_viability` / `data/literature_viability.csv`. Auto-promoted `pmid*` rows are inventory.

## Model policy

Start tabular (Ridge, RF, XGBoost). Quantile XGBoost for uncertainty.
The number on the box is **LOPO viability**, not simulated holdout R².
Gaussian Processes and mechanistic residuals are the Phase 4/physics+data step, not v0.1.

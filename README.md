# TissueLab AI

A first working prototype of a **Tissue Interaction Engine**: predict how a hydrogel will interact with chondrocytes, then invert that model to propose designs and the next experiment.

This repo starts the project described in *AI for Tissue–Material Interactions*. It follows the brief on purpose:

- one tissue (cartilage)
- one material class (hydrogels)
- four measurable outcomes (viability, proliferation, differentiation, ECM deposition)
- no attempt to simulate a whole organ

The point of the MVP is not “AI for biology”. It is:

> **Can this system change which hydrogel experiment a cartilage researcher runs next?**

## What is in v0.1

| Piece | Status |
|---|---|
| SQLite experimental DB (`studies` / `experiments` / `measurements`) | Done — `data/tissuelab.sqlite` |
| Native literature measurements (no fake porosity) | Done |
| Mapped 0–100 scores + simulator (software prior only) | Still in the old CSV/ML path |
| Literature-informed simulator (~650 records) | Done |
| Baseline models (mean, Ridge, Random Forest, XGBoost) | Done |
| Quantile uncertainty (10–90%) | Done |
| Inverse design (desired response → candidate gels) | Done |
| Next-experiment recommendation (expected improvement) | Done |
| Streamlit app + FastAPI | Done |
| Competitor / dataset landscape | `docs/LANDSCAPE.md` |

The **source of truth for science** is `data/tissuelab.sqlite` (see `docs/DATA_MODEL.md`). Curated measurements stay in `experiments` / `measurements`. Amass harvest lives in `papers` (~8k BiomedCore records). Regex candidates in `paper_extractions` are **not** training labels. The mixed CSV + simulator is only a software prior.

## Quick start

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"

python -m tissuelab.load_database
# optional: Amass literature harvest (requires AMASS_API_KEY in .env)
python -m tissuelab.harvest_amass
python -m tissuelab.europepmc
python -m tissuelab.rank_papers
python -m tissuelab.ingest_literature
python -m tissuelab.load_database
python -m tissuelab.benchmark
python -m tissuelab.build_dataset
python -m tissuelab.train
pytest -q

streamlit run app/streamlit_app.py
# API
uvicorn app.api:app --reload --port 8000
```

Open the app, go to **Predict**, keep the default GelMA ~25 kPa chondrocyte encapsulation, and run a prediction. Then try **Inverse design** with high differentiation + high ECM.

## How to read the numbers

Outcomes are on a 0–100 scale.

- **Viability** is closest to a real assay (live/dead %).
- **Proliferation / differentiation / ECM** are indices. When a paper reported sGAG/DNA or COL2A1, the value is a mapped relative score, not a literal µg/µg.

Quantile bands are the model saying it does not know. Wide intervals should change the experiment you run, not be ignored.

### Current baseline (v0.1)

| Model | Holdout MAE | Holdout R² |
|---|---|---|
| Dummy mean | 16.9 | ~0 |
| Ridge | 6.9 | 0.84 |
| Random Forest | 6.4 | 0.84 |
| **XGBoost** | **4.6** | **0.92** |

That holdout is mostly simulated data, so it only proves the pipeline learned the prior. The honest test is `python -m tissuelab.benchmark` (leave-one-paper-out on numeric viability). Simulated holdout **MAE 13.4 / R² 0.11** on 31 mapped literature rows is the old mixed-CSV check — still not the product metric.

## Project layout

```text
src/tissuelab/     schema, literature records, simulator, models, inverse design
app/               Streamlit UI and FastAPI
data/              generated experimental table
docs/              landscape, MVP notes
tests/             schema, simulator biology checks, model vs dummy, inverse design
```

## Next (the actual MVP)

See `docs/ROADMAP.md`. In short: **do not grow the paper harvest**. Extract the ranked queue into labeled experiments, then beat a dummy model under leave-one-paper-out on live/dead %.

```bash
python -m tissuelab.europepmc
python -m tissuelab.rank_papers
python -m tissuelab.ingest_literature
python -m tissuelab.load_database
python -m tissuelab.benchmark
```

| Horizon | Bar |
|---|---|
| 4 weeks | ≥ 25 papers, ≥ 80 numeric viability rows, LOPO MAE 15% better than dummy |
| 3 months | one wet-lab stiffness series held out |
| 12 months | paid pilots only if a PI changed the next gel |

Commands for the current stack stay below. The mixed CSV + simulator is only a software prior.


## Working thesis

Biological material design can be accelerated by combining literature-derived experiments, a constrained prior, tabular ML, and Bayesian experimental design — if and only if the recommendations beat a scientist working from papers and intuition. That is the hypothesis this codebase is set up to test.

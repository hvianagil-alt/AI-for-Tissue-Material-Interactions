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
| Hand-curated live/dead training view (`v_model_viability`) | Done — `data/literature_viability.csv` |
| Literature viability (empirical Bayes ± adaptive LOPO band) | Done (beats dummy; R² still < 0) |
| HTML product: Predict / Table / Compare / CSV | Done — English default |
| Buyable-minimal plan | `docs/BMP.md` |
| Native literature measurements (no fake porosity) | Done |
| Mapped 0–100 scores + simulator (software prior only) | Still in the old CSV/ML path |
| Literature-informed simulator (~650 records) | Done |
| Baseline models (mean, Ridge, Random Forest, XGBoost) | Done |
| Quantile uncertainty (10–90%) | Done |
| Inverse design (desired response → candidate gels) | Done |
| Next-experiment recommendation (expected improvement) | Done |
| Streamlit app + FastAPI | Done |
| Competitor / dataset landscape | `docs/LANDSCAPE.md` |

The **source of truth for science** is `data/tissuelab.sqlite` (see `docs/DATA_MODEL.md`). Start with `data/literature_viability.csv` (`v_model_viability`: hand-curated live/dead % only). Amass harvest lives in `papers` (~8.5k BiomedCore records). Regex candidates in `paper_extractions` and auto-promoted `pmid*` rows are **not** training labels. The mixed CSV + simulator is only a software prior.

## Use it now

You do **not** need an Amass key, and you do **not** need to train anything. The labeled SQLite table is already in the repo. Step-by-step: [`docs/USE.md`](docs/USE.md).

```bash
python3 -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate
pip install -e .
tissuelab-app
```

Opens [http://localhost:8501](http://localhost:8501) as a **plain HTML** product (Predict, Table, Compare, CSV). English by default; `?lang=pt` for Portuguese chrome. Leave GelMA ~25 kPa and read the evidence card plus the nearest extracted papers. Open `/table` — that CSV is what you would email a colleague.

Optional:

```bash
streamlit run app/streamlit_app.py --server.port 8502   # radar demo; needs websocket
uvicorn app.api:app --host 0.0.0.0 --port 8501          # same UI as tissuelab-app
pip install -e ".[dev]" && pytest -q
```

## How to read the numbers

- The kernel’s global n_eff is ~30 for every query — the number that matters is **effective n on this gel**.
- **Proliferation / differentiation / ECM** in the radar are mapped 0–100 scores plus a simulator prior. Do not cite them as measurements.
- Shrinkage **beats** a dummy mean under LOPO (~15.8 vs 16.5). Ridge loses and is **not** served. The MVP bar (15% better than dummy, R²>0) is still unmet. Use nearest extracted papers to choose the next gel.

### Current baseline

| Check | Value |
|---|---|
| Hand-curated studies | 54 |
| Hand experiments | ~205 |
| Numeric live/dead (training) | 42 rows / 15 papers |
| Viability evidence in `/table` | numeric + qualitative floors |
| Dummy LOPO MAE | 16.5 |
| Shrinkage LOPO MAE | ~15.8 (deployed) |
| Material-mean LOPO MAE | 16.4 |
| Ridge LOPO MAE | 22.6 (not deployed) |
| Simulated XGBoost holdout R² | ~0.92 — **ignore** for science |

The product is ready to **use as Predict**: literature viability + nearest extracted papers. It is not ready to claim a model that beats “GelMA ~25 kPa + TGF-β3”.

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

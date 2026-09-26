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
| Literature viability (empirical Bayes ± adaptive LOPO band) | Done (served; 61 papers, shrinkage LOPO MAE 11.36 vs dummy 11.27, R² −0.028; MVP 15% bar still unmet) |
| HTML product: Protocol / Lookup / Table / Compare / CSV | Done — English default |
| Buyable-minimal plan | `docs/BMP.md` |
| How to train the viability model (videos → this table) | `docs/ML_PLAN.md` |
| First training lesson (never trained a model) | `docs/TRAIN.md` → `python3 -m tissuelab.teach_model` |
| Uniform paper tags + training pack | `python3 -m tissuelab.pipeline` → `data/train_gold.csv` |
| Native literature measurements (no fake porosity) | Done |
| Mapped 0–100 scores + simulator (software prior only) | Still in the old CSV/ML path |
| Literature-informed simulator (~650 records) | Done |
| Baseline models (mean, Ridge, Random Forest, XGBoost) | Done |
| Quantile uncertainty (10–90%) | Done |
| Inverse design (desired response → candidate gels) | Done |
| Next-experiment recommendation (expected improvement) | Done |
| Streamlit app + FastAPI | Done |
| Competitor / dataset landscape | `docs/LANDSCAPE.md` |

The **source of truth for science** is `data/tissuelab.sqlite` (see `docs/DATA_MODEL.md`). Train on `data/train_gold.csv` (hand-curated live/dead % plus chemistry / architecture / application). Harvested papers live in `papers` (~12k records, tagged in `data/papers_uniform.csv`) — that is the searchable library, not the model’s n. Regex candidates and auto-promoted `pmid*` rows are **not** training labels. There is no 2000-study model to turn on.

## Use it now

You do **not** need an Amass key, and you do **not** need to train anything. The labeled SQLite table is already in the repo. Step-by-step: [`docs/USE.md`](docs/USE.md).

```bash
python3 -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate
pip install -e .
tissuelab-app
```

Opens [http://127.0.0.1:8501](http://127.0.0.1:8501) as a **plain HTML** product. Say which cells you have and what you want this week; it ranks extracted protocols and searches papers. English by default; `?lang=pt` for Portuguese. If Chrome refuses `localhost`, that is IPv6 — use 127.0.0.1. `/lookup` is the old evidence card if you already picked a gel. `/table` is the CSV you would email a colleague.

Optional:

```bash
streamlit run app/streamlit_app.py --server.port 8502   # radar demo; needs websocket
uvicorn app.api:app --host :: --port 8501          # prefer: tissuelab-app (IPv4+IPv6)
pip install -e ".[dev]" && pytest -q
```

## How to read the numbers

- The kernel’s global n_eff is ~30 for every query — the number that matters is **effective n on this gel**.
- **Proliferation / differentiation / ECM** in the radar are mapped 0–100 scores plus a simulator prior. Do not cite them as measurements.
- Lookup serves **empirical-Bayes shrinkage** (**57 parameters**: 11 locked kernel hyperparameters + 46 gel×cell means), never a dummy mean and never a tree. HGB is eligible at ≥40 papers and still loses LOPO, so it stays report-only. Beginning target is **100 papers**. The MVP bar (15% better than dummy, R²>0) is still unmet.

### Current baseline

| Check | Value |
|---|---|
| Hand-curated studies | 100 |
| Hand experiments | 289 |
| Numeric live/dead (training) | 169 rows / 61 papers |
| Served model parameters | 57 (11 locked kernel + 46 gel×cell means) |
| Beginning target | 100 independent live/dead papers |
| Harvested papers tagged | 12024 (2317 training-relevant) |
| Dummy LOPO MAE | 11.27 |
| Shrinkage LOPO MAE | 11.36 (deployed; dummy slightly ahead this snapshot, R² −0.028) |
| Material-mean LOPO MAE | 12.52 |
| Ridge LOPO MAE | 12.21 (not deployed) |
| HGB LOPO MAE | 12.75 (eligible at ≥40 papers; still not served) |
| Simulated XGBoost holdout R² | ~0.92 — **ignore** for science |

The product is ready to **use as Protocol**: cells + job → extracted protocol + papers. Lookup is the evidence card. It is not ready to claim a model that beats “GelMA ~25 kPa + TGF-β3”.

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

# How the MVP becomes a business

The product question is unchanged:

> Can this system change which hydrogel experiment a cartilage researcher runs next?

8000 Amass papers are a **library**. They do not make the model work. A model that “works” needs labeled conditions: material × stiffness × cells × time → a number the lab actually measured. That table is now **101 hand-curated studies / 291 experiments / 171 numeric live/dead rows from 62 papers**. Auto-promoted `pmid*` rows stay in SQLite as inventory and are **not** in the training view.

## What “MVP” means here (and what it does not)

**MVP (scientific):** a viability model that beats a dummy mean under **leave-one-paper-out** on real live/dead %, with enough papers that a PI would not laugh at the split (`n_studies ≥ 15` is the first bar; `≥ 40` is the useful bar).

**MVP (product):** inverse design + next-experiment that cites 3–5 extracted papers and proposes a protocol a cartilage lab would actually run this quarter (GelMA or fibrin, 1–30 kPa, TGF-β3 on/off).

**Not the MVP:** more tissues, a virtual joint, an LLM that invents sGAG numbers from abstracts, Postgres, or a neural net on 13 points.

## What to add to the database (in order)

| Priority | Add | Why | Do not |
|---|---|---|---|
| 1 | Labeled **experiments** from the extraction queue (this week’s work) | Training rows | Promote regex `%` from abstracts |
| 2 | Assay method (`live_dead_kit`, `sgag_kit`, `qpcr_reference`) | Stops unit leakage | Pool all sGAG as one column |
| 3 | `2D` vs `3D` already exists — fill it on every new row | Largest confounder after material | Mix monolayer with encapsulation |
| 4 | Donor/passage when published | Biology batch effects | Impute passage = 2 |
| 5 | Fulltext extraction **off-repo**, only for queued PMIDs | Figures hold the numbers | Dump copyrighted fulltext into git |
| 6 | One wet-lab stiffness series (your own `study_id`) | External test set | Train on the same series you claim as validation |
| later | Bone ALP, nanoparticle uptake | New `cell_type` + `assay` rows | New columns on `experiments` |
| never as labels | Simulator rows, mapped 0–100 scores, Amass abstracts | Prior / retrieval only | Hide `source=simulated` |

Harvest more papers only after the top 250 queued items are extracted or rejected. Extra abstracts without labels are search quality, not model quality.

There is **no** public `material × chondrocyte × outcome` CSV. BIOMATDB and OOCDB are search portals. The better source we added is **Europe PMC open fulltext** (free XML), used before paid Amass fulltext.

Current snapshot: hand-curated live/dead in `data/train_gold.csv` (**171 numeric rows / 62 papers**); harvested papers tagged in `data/papers_uniform.csv` (**12 024**, library not labels). Deployed estimator is **empirical-Bayes shrinkage** — not Ridge, not HGB, not a neural net. There is no 2000-study model. R² is still ~−0.028, `mvp_pass` false. The 15% MAE bar needs more independent live/dead papers, not more AI.

How to grow that estimator without copying a random-split materials notebook: `docs/ML_PLAN.md` (mixed models + LOPO + Afflerbach workflow, mapped onto this table). If you have never trained a model, start with `docs/TRAIN.md` (`python3 -m tissuelab.teach_model`).

## Step by step

### Now (week 0) — done in this commit

1. Keep curated measurements as the only training labels.
2. Score the 8k papers for extractability (`paper_scores`, `extraction_queue`).
3. Lock the honest metric: leave-one-paper-out viability (`python -m tissuelab.benchmark`).
4. Link curated DOIs to Amass IDs.

### Weeks 1–4 — extract, do not model-shop

Work the queue top-down (`data/extraction_queue.csv`), preferring papers in the same gel×cell neighborhood as existing gold. Target **100 papers as the beginning of a working predictor** (~Ridge-scale). 40 papers is only the tree report gate. One paper is one `studies` row; each gel/timepoint is an `experiments` row. Missing values stay `NULL`.

Time: ~1.5–3 h per paper if you only take tables/text (not figure-digitizing). 40 papers ≈ **two focused weeks**.

Exit: `n_studies ≥ 25`, `n_numeric_viability ≥ 80`. Re-run LOPO. **Pass bar v1:** deployed tabular estimator LOPO MAE ≤ 85% of dummy MAE and R² > 0.

### Months 2–3 — one lab loop

Pick GelMA or fibrin, 4 stiffnesses, same cells, same media, live/dead at day 1 and 7. That series is `study_id = labpilot_YYYY`. Train without it; test on it. If the model loses to “use 10–25 kPa GelMA + TGF-β3”, the product is not ready.

Exit: one protocol the lab ran because of the tool, written up with predicted vs measured.

### Months 4–6 — product-shaped MVP

- Evidence card: prediction + 3 nearest **extracted** papers (not simulated neighbors).
- Inverse design constrained to physiological stiffness and materials the lab stocks.
- Paid conversation with 3 PIs: would they change next week’s gel? Price a pilot (£ / lab / quarter), not a hydrogel SKU.

### Months 6–12 — business if the metric moved

Customer is the **researcher / core facility / bioink applications team**, not a patient. You sell experiment recommendation and a living labeled table, not MCOLGEL. Three design partners. Only then consider bone (ALP) as a second assay family in the same schema.

## Benchmarks (the numbers that matter)

| Metric | Today | 4 weeks | 3 months | 12 months |
|---|---|---|---|---|
| Harvested papers | ~8000 | same is enough | same | same |
| Curated studies | 11 | ≥ 25 | ≥ 40 | ≥ 80 |
| Experiments | 47 | ~200 | ~400 | ~1000 |
| Numeric viability | 13 | ≥ 80 | ≥ 150 | ≥ 400 |
| **LOPO viability R²** | lock baseline now (likely ≤ 0) | > 0 and beat dummy 15% MAE | > 0.25 | > 0.4 on a held-out lab series |
| Simulated holdout R² ~0.92 | ignore | ignore | ignore | ignore |
| Lab series predicted | 0 | 0 | 1 | 2–3 labs |
| PI would change next gel | no | maybe | first yes | paid pilots |

Dummy LOPO is the competitor. A scientist using “GelMA ~25 kPa + TGF-β3” is the other competitor. If you cannot beat those, there is no company.

## How this is a business (only if the table grows)

1. **Wedge:** cartilage hydrogels, viability then sGAG — one buyer (biomaterials PI), one decision (which gel this week).
2. **Moat:** the labeled tidy table + LOPO discipline, not the XGBoost.
3. **Not the company:** selling a proprietary gel (E&M BioLab already does that); selling a bioprinter (BICO).
4. **Failure modes:** extracting 200 messy rows with mixed kits; training on abstracts; expanding to bone before cartilage LOPO works; claiming the simulator R² in a deck.

## Commands

```bash
python -m tissuelab.load_database    # curated + keep harvest
python -m tissuelab.rank_papers      # fill extraction_queue (skips extracted)
python -m tissuelab.benchmark        # honest LOPO on v_model_viability
python -m tissuelab.train            # optional demo XGBoost; literature predictor does not need it
```

Read the queue: `data/extraction_queue.csv`. Put new numbers only in `src/tissuelab/curated.py` (or a future curator UI), never in `paper_extractions`.

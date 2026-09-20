# Experimental database

## Decision

SQLite file: `data/tissuelab.sqlite`.

Not PostgreSQL. The blocker is **labeled experiments**, not a server. SQLite is a real relational database, portable, and enough until a lab is uploading rows daily.

## Layout (star / tidy)

```text
studies 1──* experiments 1──* measurements
              │
              ├── vocab_materials
              ├── vocab_cell_types
              └── vocab_assays
```

- **studies** — one paper. Split the ML data here (leave-one-paper-out). Random 80/20 on rows leaks the same gel series into train and test.
- **experiments** — one published condition. Features that the paper omitted are `NULL`, never `0`, never a guessed porosity.
- **measurements** — long form: `(assay, value, unit, evidence)`. Viability, sGAG, COL2/COL1, ALP (bone, later) are rows, not columns.

That last point is the answer to “later we add more cell variables”. Osteoblast ALP is a new **assay + cell_type**, not a new column that breaks chondrocyte models. Filter `cell_type = articular_chondrocyte` and `assay = viability_pct` for the MVP.

## What is allowed into a model

| Use | Table / view | Why |
|---|---|---|
| Viability regressor | `v_model_viability` | Only numeric live/dead % |
| Stiffness as a feature | experiments with `stiffness_kpa IS NOT NULL` | Complete-case or a missingness indicator |
| Histology ordinals | measurements `*_histology` | Within-paper rank only; do not treat as µg/µg |
| Simulated rows | **not in this database** | They are a software prior, not observations |

## Evidence field

- `numeric_text` — a number in the paper (prefer this)
- `numeric_table` — a table
- `qualitative_text` — “high viability”, safranin-O ranking
- `figure_estimated` — read off a plot (must be flagged; we almost never use this)

## Leakage and confounding the schema is built to survive

1. **Study leakage** — several rows share a protocol, media, donor. Cross-validation grouping = `study_id`.
2. **Unit leakage** — sGAG/DNA from two kits are not one column without a `unit` and assay name.
3. **Missingness** — porosity was ~never reported; putting 80% everywhere would teach the model a fake feature.
4. **Target leakage** — do not put COL2A1 fold and “differentiation_score” derived from it in the same model as both X and y.

## MVP target

For now: **viability %** on cartilage hydrogels, because it is the only outcome with a shared unit and enough numeric rows. Differentiation/ECM stay in the DB as paper-native assays until there are enough `sgag_per_dna` values with the same kit, or we model ranks *within* a study.

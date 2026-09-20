# MVP notes

## Chosen MVP

```text
ONE tissue          cartilage
ONE material class  hydrogels
ONE cell context    articular chondrocytes (MSCs allowed as a feature)
FOUR outcomes       viability, proliferation, differentiation, ECM
```

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

## Data policy

Every row has `source` ∈ {`literature`, `simulated_literature_informed`}.
Literature rows list `imputed_fields` when a value was mapped from text or a typical protocol default (e.g. porosity rarely reported).

Do not train a “production” model on simulator labels and then hide that fact.

## Model policy

Start tabular (Ridge, RF, XGBoost). Quantile XGBoost for uncertainty.
Gaussian Processes and mechanistic residuals are the Phase 4/physics+data step, not v0.1.

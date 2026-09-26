# Protocol finder — how a PI actually decides

The previous Predict page asked the PI to already know the gel. That is not how Friday works. A PI walks in with **cells**, a **job**, and a fridge. They google. Then they run GelMA because the last student did.

This page inverts that. TissueLab asks what they have and what they want, ranks **extracted** protocols, then **searches** harvested papers (and optionally Europe PMC). It does not write a protocol with a language model.

## What the PI is thinking

1. What cells do I actually have this week? (articular / MSC / ADSC)
2. What is the job? Keep them alive, print without a dead construct, or make matrix.
3. Encapsulate or print? TGF-β3 in the freezer or not?
4. Which gels do we stock? (often GelMA + one other)
5. They open 3 papers, screenshot a figure, pick something close to last month.

SciFinder answers “papers about GelMA”. It does not answer “for *my* articular chondrocytes, should I run fibrin or GelMA?”

## Product rules

- Home = that question. One recommended protocol, 2–3 papers, what not to run.
- Lookup (`/lookup`) = the old evidence card, for when they already picked a gel. Charts and LOPO live behind `<details>`.
- Search = keyword retrieval over the harvested paper library (~12k), then Europe PMC if they ask. Hits are tagged *already extracted* or *not in the table*. No generated methods. The viability model trains only on the extracted live/dead gold table — not on the 12k harvest, and there is no 2000-study model to turn on.
- Rank only on hand-curated rows. Do not average ordinal sGAG. Do not promote `pmid*` regex. Do not use the simulator recommender.
- GelMA stays on the page as the **field default**, even when it loses. That is the decision a PI is actually making.

## Ranking (locked, not an LLM)

For the chosen cells:

- **Keep alive:** same-cell numeric live/dead mean, more papers better, mean < 55% is “don’t start here”. Qualitative-only gels (GelMA articular) sit below numeric gels and say so.
- **Print:** bonus if we extracted a `3D_bioprint` row for those cells. Penalise 2D seedings.
- **Matrix:** bonus if we extracted sGAG/histology for those cells — count of papers, not a pooled score. A dead gel that made GAG still loses.

Typical kPa = median published kPa on that gel × cell. Days = 14 (encapsulate) or 7 (print). TGF = the factor on the best same-cell rows, unless the PI locked it.

## When to grow the table

Grow the gold table by extracting neighborhood papers (same gels/cells as rows you already have), not a random harvest. Beginning target is **100 independent live/dead papers**. 40 is only the HGB report gate. Do not harvest more Amass abstracts to move a viability number, and do not promote regex/silver into gold.

## Not this pass

- ChatGPT methods section
- Stripe / accounts
- Training a net on 42 rows
- Inverse design as the home screen

# TissueLab product

The scientific MVP (LOPO MAE ≤ 85% of dummy, R² > 0) is **not** the product. Dummy still slightly beats shrinkage (MAE 11.56 vs 11.69, R² −0.049). A PI will not pay for a viability predictor that loses to the mean.

They will pay for **Friday’s decision**.

## The job people already have

Every Friday a cartilage / bioink PI or postdoc decides: GelMA or fibrin? Encapsulate or print? TGF-β3 on or off? They spend half a day in PubMed, screenshot figures into a slide, then run GelMA because the last paper in the lab used GelMA. PEG deaths stay in the fridge. One-paper “91%” gels get treated as a law.

PubMed / SciFinder rank by citation. BIOMATDB and OOCDB are search portals. Benchling stores the notebook after the gel is picked. CELLINK / BICO sell the ink. **Nobody sells a comparable `gel × chondrocyte × in-gel live/dead` table with an avoid list.** That absence is the SKU.

## Who pays

| Buyer | Job | Why they pay |
|---|---|---|
| Cartilage / bioink PI | Next encapsulation this month | 2–4 h of extraction saved; do not start on PEG |
| Core facility / bioink applications | “What has anyone measured in GelMA 25 kPa?” | A living table they can send a customer |
| PhD student | First protocol | Papers ranked by protocol match, not h-index |

Not the buyer: a patient, a bioprinter OEM, a hydrogel SKU company. Price a **lab seat**. Pilot: **£80–150 / lab / month**.

Sell: *the labeled live/dead table for cartilage hydrogels, this week’s protocol, three DOIs, and what to skip.* Do **not** sell “AI that predicts viability”.

## What ships (the BMP)

| Surface | Paid job |
|---|---|
| `/` Protocol | Cells + job → gel, extracted recipe, 3 DOIs |
| `/avoid` | Mean &lt; 60% for these cells. Coverage. Next extraction holes |
| `/table` + `/export.csv` | The thing they email a colleague |
| `/api/decision` | Same pack as JSON |
| `/lookup` | Evidence card **if they already picked a gel** — table mean, not a flask forecast |

Honest LOPO stays on the page. If dummy is ahead, the page says dummy is ahead.

## How we research (and how we order data)

Harvest (~12k papers) is a **library**. Gold (`v_model_viability`) is the only training table. Regex hits, floors, MTT, 2D, wrong cells never become means.

Order the next read by **product hole**, not by abstract `%`:

1. **Fragile competitor** — GelMA × articular (labs already run this; gold has 1 paper). Ranking vs fibrin is one paper from flipping.
2. **Death confirm** — mean &lt; 60% with &lt; 3 papers (lock the avoid board).
3. **Fragile winner** — mean ≥ 90% from 1 paper (do not let a singleton rank the week).
4. **Missing commercial pair** — GelMA × nasal, fibrin × auricular, collagen × MSC… a buyer will type these.
5. **Missing kPa** — live/dead without an encapsulation modulus; lookup looks empty.

Demote: reviews, citation-of-citation, floors, extract cytotoxicity, week-3+ ECM kPa, print pressure as Young’s, post-thaw, PRP-as-TGF.

`python -m tissuelab.product --queue` prints the ranked holes. `rank_papers` boosts harvested hits that close those holes (`product_gap:GelMA×articular_chondrocyte`). Still a reading list — a human extracts.

## Which model we serve (and which we refuse)

| Estimator | Role |
|---|---|
| Empirical-Bayes **shrinkage** | Served on `/lookup`. 11 locked kernel knobs + empirical gel×cell priors |
| Dummy mean | LOPO baseline. Currently slightly **ahead**. Never served as the product number |
| Material-class mean / Ridge / HGB | Reported. HGB eligible only at ≥ 40 papers; still loses LOPO |
| Neural net | Never on this n |

The “AI” a lab pays for is **ranking + retrieval + avoid**, not a net:

- Rank extracted protocols for *these* cells and *this* job (`find_protocol`).
- Skip gels whose extracted mean is a death (`avoid_board`, threshold 60%).
- Return the actual published condition (wt%, crosslink, density, DOI), not a family median.
- Show coverage so the PI sees what is a singleton.

When shrinkage beats dummy by 15% **and** R² > 0 **and** n_studies ≥ 15, the evidence card may lead with the number. Until then the number stays behind the papers.

## Failure modes that kill the company

- Selling a predicted % while dummy wins LOPO
- Promoting floors / MTT / `pmid*` regex into gold
- Growing the 12k harvest and calling it n
- Inverse design / radar as the homepage
- Hiding 5% live/dead outliers to make MAE prettier
- Name-collision theatre with TissueLabs (hardware)

## Done looks like

A cold PI, no account, no install:

1. Opens `/`. Articular, keep alive → **fibrin**, recipe, three DOIs.
2. Sees **Do not start here: PEG**.
3. Switches job to **print**. The gel changes.
4. Downloads CSV. Posts `/api/decision` from a script.
5. Reads, in English, that this is not a flask forecast and that dummy still slightly beats shrinkage.

`pytest -q` green. LOPO JSON still reports `mvp_pass: false`.

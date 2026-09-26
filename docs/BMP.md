# Buyable Minimal Product (BMP)

This is not the scientific MVP (LOPO MAE ≤ 85% of dummy). That bar still needs more labeled rows. This is the thing a cartilage PI would **pay for this quarter** even if R² is ~0.

## The job a lab already has

Every Friday a biomaterials PI or postdoc decides: GelMA or fibrin? 10 or 25 kPa? TGF-β3 on or off? They spend half a day in PubMed, screenshot figures into a slide, and then run GelMA because the last paper in the lab used GelMA.

SciFinder / PubMed / Benchling do not answer that. BIOMATDB and OOCDB are search portals. There is no public `material × chondrocyte × live/dead` table. **That absence is the product.**

## Who buys

| Buyer | Why they open it | Why they pay |
|---|---|---|
| Cartilage / bioink PI | Next encapsulation this month | 2–4 h of extraction saved, comparable numbers |
| Core facility / bioink applications | “What has anyone actually measured in GelMA 25 kPa?” | Living table they can send a customer |
| PhD student | First protocol, afraid of picking a dead gel | Papers ranked by protocol match, not citation count |

Not the buyer: a patient, a bioprinter OEM, a hydrogel SKU company (E&M BioLab already sells gel). Price a **lab seat**, not a material.

Pilot price to say out loud: **£80–150 / lab / month** for the extracted table + evidence card. Do not sell “AI that predicts viability”. Sell “the labeled live/dead table for cartilage hydrogels, with an honest lookup”.

## What “good enough to buy” means (gates)

A PI can do this in **one sitting, no install, no account**:

1. Open the app. In 30 seconds see an evidence card for **GelMA ~25 kPa, articular chondrocyte, 14 d**.
2. Switch to **fibrin** and **chitosan**. The papers, trust badge, and band actually change. DOIs open.
3. Open **the table**: every hand-extracted live/dead row, filter by gel, download CSV.
4. **Compare** two protocols side by side (their gel vs GelMA + TGF-β3).
5. Read, in plain language, that this is literature lookup, not a virtual flask. Weak evidence is labeled weak.
6. English by default (international labs). Portuguese still available.

Scientific honesty stays on the page: shrinkage vs dummy LOPO, n papers, % kPa missing. If LOPO is still short of the 15% bar, say so. A PI will pay for the table; they will not pay for a fake R².

## What is *not* in the BMP

- Neural nets on n≈40–80 rows
- Auto-promoted `pmid*` regex as labels
- Invented live/dead or imputed kPa
- Streamlit websocket as the product
- Multi-tissue, inverse design, or “next experiment” from the simulator
- Stripe / auth this week (the *offer* is buyable; billing is a later week)

## Data work that makes it sellable (this pass)

The product lies when GelMA has **one** numeric row and **zero** kPa. A buyer will type GelMA, see “evidence weak”, and bounce.

Priority extraction (hand-curated only, numbers that appear in OA fulltext or a methods table):

1. **GelMA** with a live/dead % **and** a modulus if published. This is the competitor protocol.
2. **HA / fibrin / alginate / collagen / chitosan** with % + kPa when both exist.
3. Reject: cytotoxicity MTT on extracts, impact-injury explants, heart-valve-only, osteogenic-only, reviews.

Stop rule: do not promote regex hits. Missing stays `NULL`. One paper = one `study_id`. Floor statements (“>70%”) stay qualitative unless the paper also gives a mean.

After each extraction batch: `python -m tissuelab.load_database` then `python -m tissuelab.benchmark`. Record n_rows, n_studies, dummy MAE, shrinkage MAE, R². Do not retune kernel hyperparameters to chase the bar.

## Product work that makes it sellable (this pass)

| Surface | Why a PI uses it |
|---|---|
| `/` evidence card | The decision. GelMA also shows **Also extracted** floors/kPa the number ignores. |
| `/table` | The thing they email a colleague. Filter keeps every gel in the dropdown. |
| `/export.csv` | Drops into GraphPad / Excel |
| `/compare` | “Is fibrin actually better than GelMA+TGF for *this*?” A minus B in plain English. |
| `?lang=pt` | The founding lab |

Navigation, onboarding strip, English copy, human gel names, next-DOI, trust, borrowed-kPa flags stay.

## Test as if you were the customer

Walkthrough (must pass before calling it buyable):

1. Cold open `/`. Title in English. Form labeled. GelMA 25 kPa 14 d.
2. Big number + band + trust + “open this next” with a working DOI. For GelMA this is a **kPa paper** (Levett / Li), not only Daly.
3. **Also extracted for this gel** lists Li 2016 / Levett 2014 / Paul 2023 floors with kPa.
4. Change hydrogel to fibrin, then chitosan, without a blank page.
5. `/table` lists only hand-curated live/dead (no `pmid*`). Filter chitosan — other gels stay in the dropdown. CSV downloads.
6. `/compare` GelMA vs fibrin shows two estimates, two paper lists, and A minus B in points.
7. `pytest -q` green. LOPO JSON still reports `mvp_pass` honestly.

If the walkthrough fails because GelMA is empty of kPa, go back to extraction — not to XGBoost.

## After this pass (not this week)

- 3 PI conversations: would they change next week’s gel? Would they pay for the table?
- One lab stiffness series as an external test (`labpilot_YYYY`), never trained on.
- sGAG as a second assay on the same experiments, not a new tissue.
- Auth + seat license only after a PI says yes.

## Failure modes that kill the company

- Extracting 200 messy MTT rows and calling it live/dead
- Training on abstracts
- Claiming simulator R² 0.92 in a deck
- Shipping inverse design as the product
- Hiding 5% viability outliers to make MAE look better

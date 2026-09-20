# Week 1 landscape — TissueLab AI

Status: first pass, 2026-03-20. This is the Phase 1 deliverable from the project brief (competitor + literature + data), plus an MVP choice.

## 1. Three candidate application areas

| | MVP 1 (selected) | MVP 2 | MVP 3 |
|---|---|---|---|
| Vertical | Hydrogel → chondrocyte / cartilage | Scaffold → bone regeneration | Nanoparticle → tumour penetration |
| Why it is attractive | Simplest biology, standard assays, dense literature, stiffness is a shared quantitative feature | Clear clinical pull (orthopaedics), mineralisation is measurable | Strong drug-delivery spend, clear PK endpoints |
| Why it is hard | Lab-to-lab protocol drift; ECM often qualitative | In vivo confounding, multiple cell types | Multi-step transport physics, imaging-heavy labels |
| Data available now | Dozens of comparable 3D hydrogel papers; no unified table | More heterogeneous scaffolds; fewer matched property vectors | Nano–bio datasets exist but not tissue-interaction tables |
| Easiest consistent outcome | Live/dead viability, then sGAG / COL2A1 | ALP / calcium / live-dead | Uptake %, not true penetration depth |

**Selection:** MVP 1. The brief already flags it as the easiest starting point. Cartilage has one resident cell type, hydrogels have tunable stiffness, and several papers isolate stiffness from biochemistry (Li 2016 GelMA; Bachmann 2020 fibrin vs PEG-dextran). That is enough structure to train a baseline and enough biology to be meaningful.

MVP 3 remains the best *commercial* long-term fit if the founding team is drug-delivery native. Do not start there until the data schema and closed loop work on a simpler tissue.

## 2. What “predictable” looks like in this vertical

Repeated, directional findings (not a universal law):

- In 3D **protein gels**, chondrogenic phenotype and matrix often improve as stiffness moves from ~1 kPa toward ~30 kPa (Li 2016 GelMA 3.8 → 29.9 kPa; Bachmann 2020 fibrin 1 → 30 kPa + TGF-β3).
- **Bioinert dense PEG-dextran** does the opposite: viability falls from ~67% at 1 kPa to undetectable at 30 kPa (Bachmann 2020). Material class dominates stiffness.
- **TGF-β3** is a large, reliable lever for redifferentiation and sGAG / collagen II.
- **Degradable PEG** distributes GAG/collagen better than non-degradable PEG at similar modulus (Bryant/Anseth; Sridhar 2015).
- **Alginate** keeps a round morphology and high COL2A1 relative to spreading PEG gels (Appelman 2011).
- **Very high polymer content** in bioprinted gelatin–alginate drops viability (93% → 88%) and chondrogenic genes (Zhang 2024).
- 2D vs 3D is not a small effect. Do not mix them without a culture-model feature.

These are the relationships encoded in `tissuelab.simulator`. They are priors for a small-data model, not a virtual cartilage.

## 3. Datasets investigated

| Source | What it actually contains | Useful for this MVP? |
|---|---|---|
| **OOCDB / KLOCD** (organchip.cn) | Organ-on-chip literature, patents, GEO-like transcriptomics, a knowledge graph (~76k nodes). Lab models are mostly the host institute’s chips. | Poor fit as a training table. Useful later for literature retrieval and cartilage-on-chip expansion. Licensing and bulk download of a material–outcome matrix were not evident. |
| Materials Project / NIST / MatWeb / PoLyInfo | Solid-state / polymer **material** properties (modulus, Tg, strength). | Useful for inverse *polymer* selection (see Sahu 2022 cartilage polymer blends). Not cell-response data. |
| GEO / ArrayExpress | Transcriptomics, including some organoid and chondrocyte datasets. | Later multimodal feature, not an MVP label. |
| Published hydrogel papers | The real training data. Properties and outcomes live in figures, not tables. | Yes — this is the corpus to mine. Seed extraction is in `src/tissuelab/literature.py` (30 records, 10 papers). |
| Unified public `material × tissue × outcome` database | Does not exist. | This absence is the product opportunity. |

**Estimate:** a careful extraction of cartilage-hydrogel papers can yield on the order of **300–1,500 high-quality rows** (multiple conditions per figure). 5,000 is possible only if organoid / MSC / mixed-tissue gels are included and endpoints are aggressively normalised. The MVP trains on 30 real + 650 simulated rows to prove the pipeline, not to claim a production model.

## 4. Companies and groups (15+)

### Direct-ish (AI for biomaterial / hydrogel design)

| Name | What they do | Overlap |
|---|---|---|
| E&M BioLab | AI-optimised regenerative biomaterials (MCOLGEL / MCOLBONE) | Closest narrative overlap; product is a material, not a researcher tool |
| NanoModus | Generative molecules/polymers + GPU MD | Adjacent materials informatics, not tissue response |
| Aspect Biosystems | Bioprinted tissue therapeutics, “AI-powered bioprinting” | Downstream tissue product, not experiment recommendation |
| BICO / CELLINK | Bioprinters, bioinks, lab automation | Workflow integration target, not a predictor |
| TissueLabs (Liguori) | Bioprinters + tissue-specific hydrogels | Name collision risk; hardware/materials, not this software |

### Adjacent (could buy or block)

| Name | Notes |
|---|---|
| Inventia Life Science | RASTRUM 3D cell culture platform |
| Allevi / ROKIT | Bioprinting hardware |
| Organovo / VivoSim | 3D tissue models for drug risk |
| Recursion, Insitro, Ginkgo | AI biology platforms — different buyer, huge capital |
| Benchling | ELN/LIMS — integration surface, not a competitor |
| Schrödinger / Citrine / Kebotix | Materials/chem informatics playbooks to copy, wrong domain |

### Academic groups to read, cite, and eventually partner with

| Group | Why they matter |
|---|---|
| Kristi Anseth (Colorado) | Degradable PEG, chondrocyte ECM distribution |
| Jason Burdick + Robert Mauck (Penn / now Columbia/Penn lineage) | HA hydrogels, cartilage, MSC chondrogenesis |
| Stephanie Bryant (Colorado) | PEG modulus × chondrocyte matrix |
| David Mooney (Harvard) | Hydrogel mechanobiology |
| Jennifer Elisseeff (Johns Hopkins) | Cartilage biomaterials, immunoengineering |
| Ali Khademhosseini | GelMA, biofabrication |
| Matthias Lutolf (EPFL / Roche) | Designer PEG, organoids |
| Jason Burdick reviews on hydrogel design for cartilage | Design-variable language this schema copies |

There is **no obvious funded company** whose product is “predict hydrogel–tissue response and recommend the next experiment.” Papers do inverse-design **mechanical** polymer blends for cartilage (Sahu et al., Polymers 2022, PoLyInfo + MNLR) or ML for **printability/rheology**, not chondrocyte ECM. That is the gap.

## 5. Who would pay, if this works

First buyer is not a pharma cartilage franchise. It is:

1. Academic and translational labs running expensive hydrogel DOE (GelMA/HA/PEG stiffness × TGF × degradation).
2. Bioink companies that need fewer printability × viability iterations.
3. Later: drug-delivery formulation groups, if the schema generalises.

The value proposition from the brief still holds: **reduce the number of experiments needed to design a biomaterial**, not “analyse your images with AI.”

Trust requirement: uncertainty intervals, citations next to predictions, and at least one prospective wet-lab confirmation. An LLM chat over papers will not clear that bar.

## 6. Easiest measurable outcome

**Ranked for MVP quality:**

1. **Viability %** — almost always reported, same units, live/dead or LDH.
2. **sGAG / DNA** — common but assay kits differ; needs a normalisation rule.
3. **COL2A1 / SOX9 qPCR** — fold-change relative to a local control; not comparable across papers without a baseline policy.
4. **Histology scores** — last resort.

v0.1 predicts viability in % and the other three as 0–100 indices. That is a modelling convenience and a scientific debt. Week 2–3 should split native units out of the index.

## 7. Is a useful baseline feasible?

Yes, with a caveat.

- On **simulated** data that follows literature relationships, tree models should beat a mean baseline by a wide margin (this is a pipeline test). **Measured:** XGBoost holdout MAE 5.1 / R² 0.90 vs Dummy MAE 17.1.
- On **held-out papers**, performance is much weaker because of mapped labels and missing confounders (media, hypoxia, mechanical loading, donor age). **Measured:** train on simulator, test on 31 literature rows → MAE 13.5 / R² 0.08. That is the number that matters, and it is why the next milestone is more real records, not a deeper network.
- A model that is honest about that gap — and uses it to pick informative experiments — is still useful. A model that reports a single viability number with no interval is not.

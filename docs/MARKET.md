# Is anyone paying for this?

Sourced demand check, 2026-09. Not a pitch deck. The question is whether TissueLab is a toy, or a job labs already spend money on.

**Short answer:** the scientific problem is real and repeatedly published. A viability *predictor* is not what they will pay for — our own leave-one-paper-out still loses to a dummy mean. What they already pay for is **comparable extracted evidence** (protocols, screening tables, skip lists). Sell that. Use AI for retrieval and draft extraction, not a net on 65 papers.

## 1. The problem is not imaginary

| Claim | Source | What it actually says |
|---|---|---|
| Bioink design is one of the most challenging and time-consuming tasks in 3D bioprinting | Gnatowski et al., *J. Mater. Chem. B* 2025, [doi:10.1039/D5TB00737B](https://pubs.rsc.org/en/content/articlelanding/2025/tb/d5tb00737b) | Formulation is a multi-objective grind (printability vs mechanics vs cells). Labs do not have a table; they have trial-and-error. |
| Hydrogel optimisation by one-factor-at-a-time is time-consuming, costly, and delays translation | *Mater. Adv.* 2026, [doi:10.1039/D6MA00268D](https://pubs.rsc.org/en/content/articlehtml/2026/ma/d6ma00268d) | The paid pain is **fewer wet iterations**, not a prettier R². |
| GelMA for cartilage is “frequently criticized for its perceived lack of reproducibility” | Aksu et al. (BIO INX), Bone & Joint / EORS 2025, [doi:10.1302/1358-992X.2025.8.039](https://boneandjoint.org.uk/Article/10.1302/1358-992X.2025.8.039) | Industry (a bioink company) is writing abstracts about GelMA lot/protocol drift. OA + cartilage + GelMA is not a niche hobby. |
| Same GelMA “spec” ≠ same gel | LinkedIn, Stefan Schrüfer, 3 Jun 2026, [post](https://www.linkedin.com/posts/stefan-schr%C3%BCfer-707367161_gelma-ships-with-a-spec-sheet-same-number-activity-7467927677593731072-9hhd) (63 reactions) | “The published storyline is we used GelMA at X percent. The unpublished storyline is re-measurements after every new lot.” Practitioner language for the Friday decision. |
| Cartilage hydrogels stall in a “valley of death” between papers and clinic | *Gels* 2026, [Challenges and Strategies in Hydrogel-Based Cartilage Regeneration](https://www.mdpi.com/2310-2861/12/5/350) | Protocol standardisation is listed as a translation blocker, not a nice-to-have. |
| OA is a large clinical sink | Same Bone & Joint abstract: >500 million people, >€7.2bn/year | Clinical TAM is huge. **It is not the buyer.** The buyer is the lab that will still be encapsulating chondrocytes next month. |

Rheology companies (Rheolution) and characterisation groups (Polbionica) post on LinkedIn about GelMA measurement being hard. That is adjacent pain (characterise *this* vial), not our SKU (what did *other labs* measure in-gel). It still shows the industry talks about GelMA unreliability in public, not only in reviews.

## 2. Public money already went into “unstructured biomaterial literature”

| Signal | Number | Source |
|---|---|---|
| EU BIOMATDB (database + marketplace + “digital advisors”) | **€2.80m**, Jun 2022–Feb 2025 | CORDIS [101058779](https://cordis.europa.eu/project/id/101058779) |
| Why it was funded | “Practitioners … face challenges due to the lack of a well-structured and easily accessible advanced biomaterials database” | Same CORDIS fact sheet |
| Predecessor DEBBIE | Text-mining pipeline because PubMed/Scopus biomaterials hits are unusable as a table | CORDIS [751277](https://cordis.europa.eu/project/id/751277/reporting); Hakimi et al. |
| AI cannot extract biocompatibility until the *definition* is computable | Mateu-Sanz et al., *Trends in Biotechnology* 2024, [doi:10.1016/j.tibtech.2023.09.015](https://www.cell.com/trends/biotechnology/article/S0167-7799(23)00289-5/fulltext) | The bottleneck they name is **annotation + terminology**, not a bigger neural net. |

BIOMATDB shipped a **search portal + SME marketplace + ISO 10993-style biocompatibility label** ([biomaterialdatabase.com](https://biomaterialdatabase.com/about), [marketplace brochure](https://www.biomaterialmarketplace.com/download/BIOMATERIAL-MARKETPLACE-Brochure-%28A4%29-Modules.pdf)). It is free search. It is **not** `gel × chondrocyte × in-gel live/dead %`. That hole is still the SKU. Do not compete with their marketplace; do not claim their grant as our revenue.

## 3. Machine-learning papers say the same thing we already measured

Xia, Leng, García, de la Fuente-Nunez, *Nat. Rev. Bioeng.* 25 Aug 2026, [doi:10.1038/s44222-026-00476-w](https://www.nature.com/articles/s44222-026-00476-w):

> Key barriers: **scarce and heterogeneous datasets, inconsistent experimental protocols**, black-box models, weak multi-scale coupling.

That is a 2026 Nature Reviews paper, not a blog. Inverse design / “AI hydrogel” reviews keep appearing (*ScienceDirect* 2026 hydrogel AI review; Bayesian optimisation of viscosity on **n ≈ 47** compositions, IOP 2024 [doi:10.1088/1758-5090/ad716e](https://iopscience.iop.org/article/10.1088/1758-5090/ad716e/meta)). Those models predict **rheology**, on data the authors generated themselves. They do not replace a cartilage live/dead table.

Our LOPO (dummy MAE 11.56 vs shrinkage 11.69, R² −0.049, `mvp_pass: false`) is consistent with that literature. A PI who has read the Nature review will not buy a viability forecast from 65 papers. They might buy the **FAIR table** the same review says is missing.

## 4. What labs already pay — the real comps

| They already buy | Price grain | Why it is a comp |
|---|---|---|
| Covidence (systematic review screening) | **$339 / year** for one review; $907 / 3 reviews; 450+ institutional licences | [covidence.org/pricing](https://www.covidence.org/pricing/). PI / library signs. Same job shape: stop drowning in papers. |
| DistillerSR | Quote-only enterprise; GenAI extraction with human-in-the-loop | Pharma/device literature reviews. Proof that **extracted tables** are a budget line. |
| Elicit | ~$49–169 / month for structured extraction | Generic papers → columns. No cartilage ontology, no avoid-board, no live/dead QC. |
| SpringerProtocols | Library subscription, 75k+ protocols | [Springer Nature](https://www.springernature.com/gp/librarians/products/databases-solutions/springerprotocols). Labs pay for *recipes*, not predictions. |
| UVA IFAB CellInk BioX | **$15 / h internal, $24 / h external** | [UVA fees](https://engineering.virginia.edu/facilities-equipment/innovations-fabrication/biomanufacturing/biomanufacturing-fees-and-reservations) |
| Innsbruck 3D-BCF consultation | **€50 / h** | [i-med 3D-BCF](https://www1.i-med.ac.at/en/forschung/core-facilities/3d-bioprinting-core-facility/) |
| Montana bioprinting staff | **$75–150 / h** labour + print surcharge | [UM fee structure](https://www.umt.edu/montana-biotechnology-center/facilities/protech/fee-structure/default.php) |

One wasted Friday + one dead GelMA print is already more than **£400**. That is the pilot price in `OFFER` (`£400–1,200 / lab / quarter`), billed like Covidence or a TGF vial, not monthly SaaS. PhDs do not sign POs. PIs and cores do.

## 5. Demand that looks large and is the wrong customer

Analyst notes put 3D bioprinting around **USD 2.1–2.9bn in 2025** (treat as marketing numbers). Academic institutes are often the majority end-user in those reports.

BICO (CELLINK) is the adult in the room:

- Bioprinting **−12% sales in 2024**, “soft demand … Academia & Research” ([Annual Report 2024](https://storage.mfn.se/42b1d942-9eec-4bfa-8269-958277e3d9d9/bico-group-ab-publ-annual-report-2024.pdf)).
- Strategy is to **sell more to pharma/biotech at the expense of academia**; NIH cuts keep US academic instrument spend soft through 2025 ([Q4 2025](https://storage.mfn.se/40e2ffc0-e873-4e7b-9f80-5f32fe52754c/bico-q4-2025-eng.pdf)).
- Consumables held up better than printers.

Read that twice. Hardware CapEx is what academia is cutting. A **£400/quarter literature table** is supplies, not a BIO X. It can still sell in a down printer market — but **do not pitch TissueLab to CELLINK as a printer upsell**, and do not count “the 3D bioprinting market” as addressable revenue.

Who is **not** the buyer: patients, OA payers, a hydrogel SKU company, a PhD with a card. Who might be, in order: cartilage/bioink PI (PO), core facility (send the table to users), later a bioink applications scientist (what has anyone measured in GelXA / fibrin).

## 6. Competitors — none sell this table; several sell the wrong sibling

| Player | Job they sell | Collision |
|---|---|---|
| BIOMATDB | Search + SME catalogue + ISO-ish label | Portal, not experiment rows |
| DEBBIE | NER on biomaterials abstracts | Entities, not live/dead % |
| PoLyInfo (NIMS) | Polymer properties from literature | No cell outcome |
| Benchling | ELN after the gel is picked | Too late |
| CELLINK / BICO | Printers and inks | They need fewer failed prints; they will not pay to replace GelXA |
| TissueLabs (hardware) | Printers + gels | Name collision only |
| Elicit / Consensus / Covidence | Generic review | No `gel × cell × assay` schema |
| “AI bioink Bayesian opt.” papers | Viscosity on n=47 | Different y |

Absence of a competitor is **not** proof of demand. It is consistent with a real gap *or* a market too small to fund a company. The BIOMATDB grant and Covidence comps argue gap. The BICO academic slump and our untested PO argue small. Both can be true: important for ~a few hundred cartilage labs, not a unicorn.

## 7. How to resolve it (what to build, what to refuse)

**Do:** Friday pack — cells + job → extracted gel, recipe, three DOIs, avoid board (mean < 60%), coverage so singletons are labeled, CSV. That is `/`, `/pack`, `/avoid`, `/api/decision`, `/export.avoid.csv`.

**Do not:** sell “AI that predicts viability”; inverse design as homepage; auto-promote regex/MTT/floors into gold; grow the 12k harvest and call it n.

**Willingness-to-pay test (not more papers):** three PI conversations. Would they change next week’s gel? Would they sign a supplies PO at £400/quarter? Year-1 seat (£1k–2.5k) only after one gel actually changed. Until then this is a lab tool with a price tag, not a business.

## 8. Where AI belongs (and where it does not)

| Job | AI that fits | AI that does not |
|---|---|---|
| Find the next paper that closes a product hole | Ranker + `research_queue` + `product_gap_boost` (already shipped) | Embedding search over 12k abstracts as if they were labels |
| Turn a PDF into a candidate row | LLM **draft** extraction, human quotes the %, KEEP only if numeric in-gel live/dead | End-to-end auto-curation; floors as means |
| Friday decision | Retrieve / rank extracted protocols (`find_protocol`) | Neural net on n=65 |
| Avoid deaths | Threshold on extracted mean (60%) | Classifier that “learns” PEG is bad from three papers |
| When n_studies ≥ 40 **and** estimator beats dummy LOPO by 15% with R²>0 | Then, and only then, lead the evidence card with shrinkage/HGB | HGB/net as the product while dummy wins |

This matches the Nature review (data scarcity + protocol heterogeneity) and the BIOMATDB *Trends in Biotechnology* paper (AI for extraction needs a computable schema and expert-in-the-loop). Our schema is the schema: `material_class × cell_type × culture_model × viability_pct` with NEVER_EXTRACT rules.

Active learning, if any, is **which paper a human reads next** (`python -m tissuelab.product --queue`), not a self-driving GelMA robot.

## 9. Verdict

| Question | Answer |
|---|---|
| Are you only making something cute? | The **predictor** is cute. Dummy still wins. |
| Is the underlying job important? | Yes. Published as bioink-design time, GelMA irreproducibility, translation valley-of-death, and a €2.8m EU database grant. Practitioners say it on LinkedIn. |
| Will someone pay? | For the **table + avoid + DOIs**, there are comps (Covidence, protocols, core hours). For a flask forecast, no. Unproven until a PI changes a gel. |
| How do you resolve it? | Keep extracting the holes that make Friday’s pack honest (GelMA encapsulate, GelMA kPa). Do not invent fibrin-print %. Talk to three PIs. Price as supplies. |
| How do you implement AI? | Retrieval, ranking, LLM-draft + human KEEP. Not a net. |

Fibrin × articular × print was hunted against OA fulltext: **no numeric live/dead**. Closest miss Couto 2024 (qualitative). The hole stays on the board; it is not filled with a made-up %. That is the same honesty a paying PI would check in five minutes.

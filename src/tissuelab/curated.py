"""Curated literature records for the SQLite database.

Rules
-----
- One experiment = one published condition (material × cells × time × growth factor).
- Store a number only if the paper reported it. Missing = omit the measurement.
- Do not fill porosity or degradation just to complete a wide table.
- Qualitative histology can be stored as ordinal 0–3 with evidence=qualitative_text.
"""

from __future__ import annotations

STUDIES: list[dict] = [
    {
        "study_id": "bachmann2020",
        "citation": "Bachmann et al., Front. Bioeng. Biotechnol. 2020",
        "doi": "10.3389/fbioe.2020.00373",
        "year": 2020,
        "journal": "Frontiers in Bioengineering and Biotechnology",
        "pmcid": "PMC7203471",
        "license": "CC-BY",
        "notes": "Human P2 chondrocytes, 21 d, n=9 viability. Young's moduli from rheology (E=3G, nu=0.5).",
    },
    {
        "study_id": "li2016",
        "citation": "Li et al., Polymers 2016",
        "doi": "10.3390/polym8080269",
        "year": 2016,
        "journal": "Polymers",
        "pmcid": "PMC6431958",
        "license": "CC-BY",
        "notes": "Bovine P2 chondrocytes in 10 wt% GelMA; stiffness via AFM. Viability described as high, not as a percent.",
    },
    {
        "study_id": "zhang2024",
        "citation": "Zhang et al., Front. Mater. 2024",
        "doi": "10.3389/fmats.2024.1501505",
        "year": 2024,
        "journal": "Frontiers in Materials",
        "license": "CC-BY",
        "notes": "Gelatin–alginate bioprinted chondrocyte scaffolds; viability reported as mean ± SD.",
    },
    {
        "study_id": "dekosky2010",
        "citation": "DeKosky et al., Tissue Eng. Part A 2010",
        "doi": "10.1089/ten.tea.2010.0159",
        "year": 2010,
        "journal": "Tissue Engineering Part A",
        "pmcid": "PMC2988644",
        "license": "NIH public access",
        "notes": "Agarose / PEG / IPN mechanical table; viability reported as surviving 1 week, not a percent.",
    },
    {
        "study_id": "bryant2004",
        "citation": "Bryant et al., Biotechnol. Bioeng. 2004",
        "doi": "10.1002/bit.20160",
        "year": 2004,
        "journal": "Biotechnology and Bioengineering",
        "license": "publisher",
        "notes": "Degradable PEG; compressive modulus 60–500 kPa from 10–20% macromer.",
    },
    {
        "study_id": "sridhar2015",
        "citation": "Sridhar et al., Adv. Healthcare Mater. 2015",
        "doi": "10.1002/adhm.201400695",
        "year": 2015,
        "journal": "Advanced Healthcare Materials",
        "license": "publisher",
        "notes": "MMP-degradable PEG-norbornene vs non-degradable; GAG/collagen higher when degradable.",
    },
    {
        "study_id": "thomas2017",
        "citation": "Thomas et al., Int. J. Biol. Macromol. 2017",
        "doi": "10.1016/j.ijbiomac.2017.05.116",
        "year": 2017,
        "journal": "International Journal of Biological Macromolecules",
        "license": "publisher",
        "notes": "Chitosan–HA dialdehyde; stiffness values from Bachmann 2020 Table 1 summary.",
    },
    {
        "study_id": "schuh2012",
        "citation": "Schuh et al., 2012 (values as cited in Bachmann 2020 Table 1)",
        "doi": "10.1002/jbm.a.33250",
        "year": 2012,
        "journal": "J Biomed Mater Res A",
        "license": "publisher",
        "notes": "Porcine chondrocytes in agarose 0.75% vs 3.5%.",
    },
    {
        "study_id": "ma2012",
        "citation": "Ma et al., Acta Biomater. 2012",
        "doi": "10.1016/j.actbio.2012.05.005",
        "year": 2012,
        "journal": "Acta Biomaterialia",
        "pmcid": "PMC3429695",
        "license": "NIH public access",
        "notes": "Human BM-MSC in fibrin/alginate blends + TGF-β3, 28 d. Stiffness not reported as Young's modulus.",
    },
    {
        "study_id": "daly2016",
        "citation": "Daly et al., Biofabrication 2016",
        "doi": "10.1088/1758-5090/8/4/045002",
        "year": 2016,
        "journal": "Biofabrication",
        "license": "publisher",
        "notes": "MSC-laden bioinks, 28 d + TGF-β3; post-print viability ~80% in all inks.",
    },
    {
        "study_id": "chung2009",
        "citation": "Chung et al., Biomaterials 2009",
        "doi": "10.1016/j.biomaterials.2009.04.040",
        "year": 2009,
        "journal": "Biomaterials",
        "license": "publisher",
        "notes": "HA hydrogel degradation vs MSC neocartilage; stiffness not isolated.",
    },
    {
        "study_id": "paul2023",
        "citation": "Paul et al., APL Bioeng. 2023",
        "doi": "10.1063/5.0160472",
        "pmid": "37692373",
        "year": 2023,
        "journal": "APL Bioengineering",
        "pmcid": "PMC10492648",
        "license": "CC-BY",
        "notes": "Bovine P1 chondrocytes in 15% GelMA ± 1% glycol chitosan, TGF-β3 28 d. Live/dead >70% in text, no percent. Day-1 cell-laden E used as gel stiffness; day-28 E includes ECM.",
    },
    {
        "study_id": "perezdiaz2023",
        "citation": "Pérez-Díaz et al., Polymers 2023",
        "doi": "10.3390/polym15193938",
        "pmid": "37835986",
        "year": 2023,
        "journal": "Polymers",
        "pmcid": "PMC10574893",
        "license": "CC-BY",
        "notes": "AD-hMSC seeded onto steam-sterilized Gel/CS/PVA 1:1:1, not 3D encapsulation. 87.16% is construct calcein at day 15. Monolayer 90/96% and autoclave 103.4 kPa are not gel modulus/viability.",
    },
    {
        "study_id": "ortega2024",
        "citation": "Ortega-Sánchez et al., Polymers 2024",
        "doi": "10.3390/polym16040479",
        "pmid": "38399857",
        "year": 2024,
        "journal": "Polymers",
        "pmcid": "PMC10892533",
        "license": "CC-BY",
        "notes": "Human auricular chondrocytes injected into CS/Gel/PVA. Live/dead percents are 3D; MTT 100% is extract cytotoxicity and is not stored as viability.",
    },
    {
        "study_id": "aitchison2024",
        "citation": "Aitchison et al., Bioengineering 2024",
        "doi": "10.3390/bioengineering11040329",
        "pmid": "38671751",
        "year": 2024,
        "journal": "Bioengineering",
        "pmcid": "PMC11048018",
        "license": "CC-BY",
        "notes": "C20A4 human chondrocyte line in alginate/PVA/gum arabic/hACM bioink. Live/dead intensity n=5. No Young's modulus in the paper.",
    },
    {
        "study_id": "demori2025",
        "citation": "De Mori et al., Gels 2025",
        "doi": "10.3390/gels11030213",
        "pmid": "40136918",
        "year": 2025,
        "journal": "Gels",
        "pmcid": "PMC11941925",
        "license": "CC-BY",
        "notes": "hAdMSC in collagen I/alginate, no exogenous GF. Stiffness 5.75 vs 6.85 kPa from CaCl2. Viability given only as >95% or >75% floors, not a live/dead mean.",
    },
    {
        "study_id": "rojas2025",
        "citation": "Rojas-Murillo et al., Gels 2025",
        "doi": "10.3390/gels12010035",
        "pmid": "41590061",
        "year": 2025,
        "journal": "Gels",
        "pmcid": "PMC12841122",
        "license": "CC-BY",
        "notes": "Human articular chondrocytes, fibrin vs fibrin+dACM+dAMM, 28 d Live/Dead. Percents published with tildes. No Young's modulus.",
    },
    {
        "study_id": "levett2014",
        "citation": "Levett et al., PLoS ONE 2014",
        "doi": "10.1371/journal.pone.0113216",
        "pmid": "25438040",
        "year": 2014,
        "journal": "PLoS ONE",
        "pmcid": "PMC4249877",
        "license": "CC-BY",
        "notes": "Human OA P1 chondrocytes in 10% Gel-MA ± HA-MA, TGF-β3. Day-1 cell-laden compressive moduli stored as gel stiffness. Viability high at 28 d, no percent. Week-8 moduli are ECM-matured constructs.",
    },
    {
        "study_id": "sun2015",
        "citation": "Sun et al., Front. Bioeng. Biotechnol. 2015",
        "doi": "10.3389/fbioe.2015.00115",
        "pmid": "26347860",
        "year": 2015,
        "journal": "Frontiers in Bioengineering and Biotechnology",
        "pmcid": "PMC4539543",
        "license": "CC-BY",
        "notes": "hASC in PSL mPDLLA-PEG/HA. Figure Live/Dead post-fab 81% (abstract 84% not used). Day-28 modulus is remaining scaffold after degradation, not ECM gain.",
    },
    {
        "study_id": "zigon2019",
        "citation": "Žigon-Branc et al., Tissue Eng. Part A 2019",
        "doi": "10.1089/ten.tea.2018.0237",
        "pmid": "30632465",
        "year": 2019,
        "journal": "Tissue Engineering Part A",
        "pmcid": "PMC6784494",
        "license": "NIH public access",
        "notes": "hASC/hTERT microspheroids in Gel-MOD. Stiffness is rheology G′ (Pa→kPa), not Young's. Viability preserved 3–5 weeks, no percent.",
    },
    {
        "study_id": "scalzone2019",
        "citation": "Scalzone et al., Sci. Rep. 2019",
        "doi": "10.1038/s41598-019-51070-7",
        "pmid": "31601910",
        "year": 2019,
        "journal": "Scientific Reports",
        "pmcid": "PMC6787336",
        "license": "CC-BY",
        "notes": "MSC in chitosan/BGP. Compressive E 36±4.0 kPa; equilibrium 17.4±0.8 kPa noted, not used as Young's substitute. Live/Dead day 1/3 qualitative.",
    },
    {
        "study_id": "kessel2020",
        "citation": "Kessel et al., Adv. Sci. 2020",
        "doi": "10.1002/advs.202001419",
        "pmid": "32999847",
        "year": 2020,
        "journal": "Advanced Science",
        "pmcid": "PMC7509724",
        "license": "CC-BY",
        "notes": "Bovine chondrocytes mixed outside HA-MA microstrands and bioprinted. Starting compression modulus 2.7 kPa. Myoblast-in-GelMA viabilities are a different cell type and are not stored. Day-21/42 moduli are ECM, not the starting gel.",
    },
    {
        "study_id": "hu2012",
        "citation": "Hu et al., Acta Biomater. 2012",
        "doi": "10.1016/j.actbio.2012.01.029",
        "pmid": "22330279",
        "year": 2012,
        "journal": "Acta Biomaterialia",
        "license": "publisher",
        "notes": "Visible-light MeGC. Abstract pairs compressive modulus with encapsulated chondrocyte viability. Fulltext not OA.",
    },
    {
        "study_id": "markstedt2015",
        "citation": "Markstedt et al., Biomacromolecules 2015",
        "doi": "10.1021/acs.biomac.5b00188",
        "pmid": "25806996",
        "year": 2015,
        "journal": "Biomacromolecules",
        "license": "publisher",
        "notes": "Human chondrocytes in nanocellulose–alginate bioink. Abstract live/dead 73% day 1 and 86% day 7. Fulltext not OA.",
    },
    {
        "study_id": "lindborg2015",
        "citation": "Lindborg et al., Tissue Eng. Part A 2015",
        "doi": "10.1089/ten.TEA.2014.0335",
        "pmid": "25748146",
        "year": 2015,
        "journal": "Tissue Engineering Part A",
        "license": "publisher",
        "notes": "hMSC in chitosan–HA hydrocolloid. Elastic modulus 264±38 Pa. 48% viability in the first 24 h. Fulltext not OA.",
    },
    {
        "study_id": "yang2020",
        "citation": "Yang et al., J. Funct. Biomater. 2020",
        "doi": "10.3390/jfb11010005",
        "pmid": "31963629",
        "year": 2020,
        "journal": "Journal of Functional Biomaterials",
        "pmcid": "PMC7151603",
        "license": "CC-BY",
        "notes": "Human P2 chondrocytes, agarose MACT. Young's from Table 1. No live/dead percent in text.",
    },
    {
        "study_id": "snyder2014",
        "citation": "Snyder et al., J. Biol. Eng. 2014",
        "doi": "10.1186/1754-1611-8-10",
        "pmid": "25061479",
        "year": 2014,
        "journal": "Journal of Biological Engineering",
        "pmcid": "PMC4109069",
        "license": "CC-BY",
        "notes": "BMSC in fibrin/HA-MA. Compressive moduli vs fibrinogen and HA-MA. Live/dead qualitative only.",
    },
    {
        "study_id": "kim2015",
        "citation": "Kim et al., J. Biol. Eng. 2015",
        "doi": "10.1186/1754-1611-9-1",
        "pmid": "25745515",
        "year": 2015,
        "journal": "Journal of Biological Engineering",
        "pmcid": "PMC4350967",
        "license": "CC-BY",
        "notes": "hSMSC in MeGC ± collagen II + conjugated TGF-β1. Live/dead >90% all gels at day 21; no mean percent.",
    },
    {
        "study_id": "ingavle2012",
        "citation": "Ingavle et al., J. Mater. Sci. Mater. Med. 2012",
        "doi": "10.1007/s10856-011-4499-9",
        "pmid": "22116661",
        "year": 2012,
        "journal": "Journal of Materials Science: Materials in Medicine",
        "pmcid": "PMC3729881",
        "license": "NIH public access",
        "notes": "Agarose–PEGDA IPN ± methacrylated CS. Abstract: unmodified 35% viable at 6 weeks; CS-IPN more than 50%. Fulltext XML not available.",
    },
    {
        "study_id": "zignego2014",
        "citation": "Zignego et al., J. Biomech. 2014",
        "doi": "10.1016/j.jbiomech.2013.10.051",
        "pmid": "24275437",
        "year": 2014,
        "journal": "Journal of Biomechanics",
        "pmcid": "PMC4014520",
        "license": "publisher",
        "notes": "4.5% agarose, primary human chondrocytes. Abstract: viability >95%. Native PCM 25–200 kPa is not the gel modulus.",
    },
    {
        "study_id": "maneechan2026",
        "citation": "Maneechan et al., Polymers 2026",
        "doi": "10.3390/polym18111406",
        "pmid": "42280615",
        "year": 2026,
        "journal": "Polymers",
        "pmcid": "PMC13259354",
        "license": "CC-BY",
        "notes": "Chitosan–silk fibroin + Aloe/Mimosa, TGF-β3 loaded. Hydrated compressive 5.40±3.73 kPa. MTT 98.8% is transwell extract, not 3D live/dead, and is not stored as viability.",
    },
    {
        "study_id": "lee2025",
        "citation": "Lee et al., Gels 2025",
        "doi": "10.3390/gels11110850",
        "pmid": "41294535",
        "year": 2025,
        "journal": "Gels",
        "pmcid": "PMC12652762",
        "license": "CC-BY",
        "notes": "DAS–collagen–heparin. Young's ~3 / ~30 / ~125 kPa by NaOH reconstitution. Live/dead qualitative with TGF-β3.",
    },
    {
        "study_id": "rouillard2011",
        "citation": "Rouillard et al., Tissue Eng. Part C 2011",
        "doi": "10.1089/ten.TEC.2009.0582",
        "pmid": "20704471",
        "year": 2011,
        "journal": "Tissue Engineering Part C",
        "license": "publisher",
        "notes": "Methacrylated alginate, bovine chondrocytes. VA-086 >85% viability; Irgacure 2959 below 70%. Aggregate moduli 10–20 kPa are a range, not paired to each initiator.",
    },
    {
        "study_id": "nicodemus2011",
        "citation": "Nicodemus, Skaalure & Bryant, Acta Biomater. 2011",
        "doi": "10.1016/j.actbio.2010.08.021",
        "pmid": "20804868",
        "year": 2011,
        "journal": "Acta Biomaterialia",
        "pmcid": "PMC3014397",
        "license": "NIH public access",
        "notes": "Bovine chondrocytes in PEG, 25 d. Compressive moduli 60 / 320 / 590 kPa. GAG highest at lowest crosslinking. No live/dead percent in the abstract.",
    },
    {
        "study_id": "park2013",
        "citation": "Park, Choi, Hu & Lee, Acta Biomater. 2013",
        "doi": "10.1016/j.actbio.2012.08.033",
        "pmid": "22935326",
        "year": 2013,
        "journal": "Acta Biomaterialia",
        "license": "publisher",
        "notes": "Visible-light MeGC ± HA, riboflavin. Abstract pairs irradiation time with viability and compressive modulus. 87–90 / 60–65 / ~80–87 stored as midpoints of the stated ranges.",
    },
    {
        "study_id": "salinas2007",
        "citation": "Salinas, Cole, Kasko & Anseth, Tissue Eng. 2007",
        "doi": "10.1089/ten.2006.0126",
        "pmid": "17417949",
        "year": 2007,
        "journal": "Tissue Engineering",
        "license": "publisher",
        "notes": "hMSC in PEG thiol-ene ± 5 mM RGDS. 75% is ATP viability in control (non-chondrogenic) medium, not live/dead. 0 mM RGDS viability fell without a percent.",
    },
    {
        "study_id": "mouser2017",
        "citation": "Mouser et al., Biofabrication 2017",
        "doi": "10.1088/1758-5090/aa6265",
        "pmid": "28229956",
        "year": 2017,
        "journal": "Biofabrication",
        "pmcid": "PMC7116181",
        "license": "publisher",
        "notes": "Chondrocytes in pHPMA-lac-PEG ± HAMA 28 d. Young's 14–31 kPa increased with HAMA. 0.5% HAMA optimal for GAG/COL2. No live/dead percent. PCL co-print 3.5–4.6 MPa is the composite, not the gel.",
    },
    {
        "study_id": "schneider2017",
        "citation": "Schneider, Barnes & Bryant, Biotechnol. Bioeng. 2017",
        "doi": "10.1002/bit.26320",
        "pmid": "28436002",
        "year": 2017,
        "journal": "Biotechnology and Bioengineering",
        "pmcid": "PMC5555637",
        "license": "publisher",
        "notes": "Bovine chondrocytes in photoclick PEG, 8 vs 46 kPa. Secretome paper; no live/dead percent.",
    },
    {
        "study_id": "wang2014",
        "citation": "Wang, Du & Toh, Biomaterials 2014",
        "doi": "10.1016/j.biomaterials.2013.11.070",
        "pmid": "24333028",
        "year": 2014,
        "journal": "Biomaterials",
        "license": "publisher",
        "notes": "Injectable gelatin-HPA. G′ 570–2750 Pa. Medium 1000 Pa highest sGAG and Col2/Col1. Stiffness stored as G′ in kPa, not Young's.",
    },
    {
        "study_id": "xu2013",
        "citation": "Xu et al., Biofabrication 2013",
        "doi": "10.1088/1758-5082/5/1/015001",
        "pmid": "23172542",
        "year": 2013,
        "journal": "Biofabrication",
        "license": "publisher",
        "notes": "Rabbit elastic chondrocytes inkjet-printed in fibrin-collagen, alternating PCL electrospin. >80% viable at 1 week — floor, not a mean.",
    },
    {
        "study_id": "ye2026",
        "citation": "Ye et al., Biofabrication 2026",
        "doi": "10.1088/1758-5090/ae59b5",
        "pmid": "41916393",
        "year": 2026,
        "journal": "Biofabrication",
        "license": "publisher",
        "notes": "GelMA reinforced with MEW PLCL-500. Viability remains above 90%. 72.6 MPa is the dry PLCL mesh, not gel Young's; 0.5 MPa tensile of the composite is not stored as stiffness_kpa.",
    },
    {
        "study_id": "fathi2020",
        "citation": "Fathi-Achachelouei, Keskin & Bat, J. Biomed. Mater. Res. B 2020",
        "doi": "10.1002/jbm.b.34544",
        "pmid": "31872975",
        "year": 2020,
        "journal": "Journal of Biomedical Materials Research Part B",
        "license": "publisher",
        "notes": "DPSC in silk fibroin/PEGDMA. Compressive 95.70±17.82 to 338.05±38.24 kPa. Highest viability in PEG10-SF8(1:1) without a percent. TGF-β1 + bFGF via PLGA NPs.",
    },
    {
        "study_id": "lin2017",
        "citation": "Sun, Lin et al., Acta Biomater. 2017",
        "doi": "10.1016/j.actbio.2017.06.016",
        "pmid": "28611002",
        "year": 2017,
        "journal": "Acta Biomaterialia",
        "pmcid": "PMC5813286",
        "license": "NIH public access",
        "notes": "hBM-MSC in PLLA-PEG / PDLLA-PEG. >80% viability post fabrication is a floor. Young's series ~150 to ~1500 kPa is not paired to a per-gel percent. ~1500–1800 kPa is the high-modulus pair.",
    },
    {
        "study_id": "galarraga2021",
        "citation": "Galarraga et al., Biofabrication 2021",
        "doi": "10.1088/1758-5090/ac3acb",
        "pmid": "34788748",
        "year": 2021,
        "journal": "Biofabrication",
        "pmcid": "PMC8943711",
        "license": "publisher",
        "notes": "MSC in NorHA. Starting gel ~2 kPa vs denser ~6–60 kPa. Day-56 ~350 kPa is ECM-matured and is not stored.",
    },
    {
        "study_id": "smith2013",
        "citation": "Smith Callahan et al., Acta Biomater. 2013",
        "doi": "10.1016/j.actbio.2012.12.028",
        "pmid": "23291491",
        "year": 2013,
        "journal": "Acta Biomaterialia",
        "pmcid": "PMC3799765",
        "license": "NIH public access",
        "notes": "Human OA chondrocytes in RGD-PEGDM with a G′ gradient ~3.8–27 kPa. Lower modulus maintained cell number and phenotype. No live/dead percent.",
    },
    {
        "study_id": "jooybar2019",
        "citation": "Jooybar et al., Acta Biomater. 2019",
        "doi": "10.1016/j.actbio.2018.10.031",
        "pmid": "30366137",
        "year": 2019,
        "journal": "Acta Biomaterialia",
        "license": "publisher",
        "notes": "hMSC in injectable HA-tyramine. G′ 500–2000 Pa with polymer concentration. Platelet lysate made cells attach and deposit COL2/proteoglycan. No live/dead percent.",
    },
    {
        "study_id": "kudva2018",
        "citation": "Kudva, Luyten & Patterson, Int. J. Mol. Sci. 2018",
        "doi": "10.3390/ijms19113341",
        "pmid": "30373138",
        "year": 2018,
        "journal": "International Journal of Molecular Sciences",
        "pmcid": "PMC6274881",
        "license": "CC-BY",
        "notes": "hPDC and ATDC5 in 4-arm PEG-VS. 6.5% + GPQGIWGQ + RGD selected. G′ 1.2±0.13 kPa for that 6.5% gel. Initial hPDC viability not less than 75% (floor). No-RGD arms dropped toward ~50% by week 4 — not stored as a single-gel mean.",
    },
    {
        "study_id": "choy2017",
        "citation": "Choy et al., Biomater. Res. 2017",
        "doi": "10.1186/s40824-017-0105-7",
        "pmid": "29075508",
        "year": 2017,
        "journal": "Biomaterials Research",
        "pmcid": "PMC5646124",
        "license": "CC-BY",
        "notes": "hADSC:nasal chondrocyte 2:1 in 1.0/1.2/1.5% alginate, 7 d. Trypan blue viability 66–72% across groups; 1.5% highest. Per-concentration means are only in the figure, not stored.",
    },
    {
        "study_id": "levato2017",
        "citation": "Levato et al., Acta Biomater. 2017",
        "doi": "10.1016/j.actbio.2017.08.005",
        "pmid": "28782725",
        "year": 2017,
        "journal": "Acta Biomaterialia",
        "pmcid": "PMC7116023",
        "license": "publisher",
        "notes": "GelMA with ACPC vs MSC vs chondrocytes. ACPCs made more neo-cartilage, lowest COL10, highest PRG4. No live/dead percent or starting modulus in the abstract.",
    },
    {
        "study_id": "cigan2016",
        "citation": "Cigan et al., J. Biomech. 2016",
        "doi": "10.1016/j.jbiomech.2016.04.039",
        "pmid": "27198889",
        "year": 2016,
        "journal": "Journal of Biomechanics",
        "pmcid": "PMC4920373",
        "license": "NIH public access",
        "notes": "Human chondrocytes in 2% agarose, 15–90 million/mL. Day-later Young's ~250 kPa is ECM-matured and is not stored as gel stiffness. High seeding density improved nearly all measured properties.",
    },
    {
        "study_id": "byers2008",
        "citation": "Byers, Mauck, Chiang & Tuan, Tissue Eng. Part A 2008",
        "doi": "10.1089/ten.tea.2007.0222",
        "pmid": "18611145",
        "year": 2008,
        "journal": "Tissue Engineering Part A",
        "pmcid": "PMC2656914",
        "license": "NIH public access",
        "notes": "Bovine chondrocytes in agarose. Transient TGF-β3 (2 weeks, 2.5–5 ng/mL) in serum-free medium reached ~0.8 MPa and 6–7% ww GAG after <2 months — ECM-matured, not starting gel modulus.",
    },
    {
        "study_id": "pahoff2019",
        "citation": "Pahoff et al., J. Mater. Chem. B 2019",
        "doi": "10.1039/c8tb02607f",
        "pmid": "32254918",
        "year": 2019,
        "journal": "Journal of Materials Chemistry B",
        "license": "publisher",
        "notes": "Human chondrocytes in GelMA/HAMA, LAP vs Irgacure 2959, bovine vs porcine GelMA. Day-28 ~1.5 MPa is ECM-matured. Viability measured, no percent in the abstract.",
    },
    {
        "study_id": "chawla2012",
        "citation": "Chawla et al., Biomaterials 2012",
        "doi": "10.1016/j.biomaterials.2012.04.058",
        "pmid": "22672831",
        "year": 2012,
        "journal": "Biomaterials",
        "pmcid": "PMC3387337",
        "license": "NIH public access",
        "notes": "Chondrocytes in saccharide-peptide gels, V vs Y amino acid. Viable 21 d. Day-21 193±46 vs 44±21 kPa is ECM-matured, not starting gel modulus.",
    },
    {
        "study_id": "duchi2017",
        "citation": "Duchi et al., Sci. Rep. 2017",
        "doi": "10.1038/s41598-017-05699-x",
        "pmid": "28724980",
        "year": 2017,
        "journal": "Scientific Reports",
        "pmcid": "PMC5517463",
        "license": "CC-BY",
        "notes": "Handheld co-axial Biopen: ADSC in GelMA/HAMA 10%/2%. Core/shell 200 kPa after 10 s 365 nm. Abstract live/dead is a >90% floor, not a mean. 2D CellTiter-Blue LAP toxicity is not stored as gel viability.",
    },
    {
        "study_id": "martyniak2023",
        "citation": "Martyniak et al., Bioengineering 2023",
        "doi": "10.3390/bioengineering10090997",
        "pmid": "37760099",
        "year": 2023,
        "journal": "Bioengineering",
        "pmcid": "PMC10526043",
        "license": "CC-BY",
        "notes": "Human PRG4-reporter chondrocytes in GelMA ± oxidized methacrylated alginate bioinks. Live/dead percents from printed constructs days 0–7. Storage modulus ~30 or ~60 kPa at day 0.",
    },
    {
        "study_id": "xie2022",
        "citation": "Xie et al., Adv. Healthcare Mater. 2022",
        "doi": "10.1002/adhm.202201877",
        "pmid": "36085440",
        "year": 2022,
        "journal": "Advanced Healthcare Materials",
        "pmcid": "PMC11468467",
        "license": "CC-BY",
        "notes": "Microtia auricular chondrocytes in GelMA DLP prints ± chondrocyte microtissues. Live/dead means at day 1/10/20. No starting Young's modulus for the GelMA control.",
    },
    {
        "study_id": "gatenholm2020",
        "citation": "Gatenholm et al., Cartilage 2020",
        "doi": "10.1177/1947603520903788",
        "pmid": "32070108",
        "year": 2020,
        "journal": "Cartilage",
        "pmcid": "PMC8721610",
        "license": "CC-BY",
        "notes": "Human articular P1 chondrocytes in 80:20 NFC:A, INKREDIBLE, NC-200. 98% is before printing. Printed d3/d5/d7/d14. Pellet 72% is not a hydrogel and is not stored. Printing pressure 5 kPa is not Young's modulus.",
    },
    {
        "study_id": "jovic2026",
        "citation": "Jovic et al., J. Funct. Biomater. 2026",
        "doi": "10.3390/jfb17040163",
        "pmid": "42042269",
        "year": 2026,
        "journal": "Journal of Functional Biomaterials",
        "pmcid": "PMC13117296",
        "license": "CC-BY",
        "notes": "Human nasoseptal chondrocytes in 75:25 NCA bioink, 22G INKREDIBLE. Live/dead: printed 1 h 81.9%, printed 24 h 61%, unprinted-in-gel 24 h 79.6%. E=52.6 kPa from prior NCA characterization, not DMA in this paper. Density 3e6/ml.",
    },
    {
        "study_id": "poldervaart2017",
        "citation": "Poldervaart et al., PLoS ONE 2017",
        "doi": "10.1371/journal.pone.0177628",
        "pmid": "28586346",
        "year": 2017,
        "journal": "PLoS ONE",
        "pmcid": "PMC5460858",
        "license": "CC-BY",
        "notes": "Human BM-MSC in 1–3% w/v MeHA (Irgacure 2959). Fig 3A live/dead averages 73.6±6.4% d1 and 64.4±12.2% d21 across concentrations; 1% gels disintegrated before d21. Per-% means only in the figure — not stored. Bone/osteogenicity protocol; viability is MSC in MeHA molds, not cartilage. Table 1 E after UV is not attached to the mixed viability rows.",
    },
]


def _m(assay: str, value=None, unit="", sd=None, qualitative=None, evidence="numeric_text", n=None, notes=None):
    row = {
        "assay": assay,
        "value": value,
        "value_sd": sd,
        "unit": unit,
        "qualitative_label": qualitative,
        "evidence": evidence,
        "n": n,
        "notes": notes,
    }
    return {k: v for k, v in row.items() if v is not None}


def _bachmann_experiments() -> list[dict]:
    """Full factorial from Bachmann 2020 methods + reported viability numbers."""
    stiffness = {
        "fibrin": {
            1: {"kpa": 1.1, "sd": 0.3, "conc": 1.5, "detail": "15 mg/mL fibrinogen + 1 U/mL thrombin"},
            15: {"kpa": 13.8, "sd": 1.3, "conc": 2.7, "detail": "27 mg/mL fibrinogen + 1 U/mL thrombin"},
            30: {"kpa": 31.8, "sd": 2.8, "conc": 5.0, "detail": "50 mg/mL fibrinogen + 1 U/mL thrombin"},
        },
        "silk_fibrin": {
            1: {"kpa": 1.1, "sd": 0.3, "conc": 1.5, "detail": "fibrin 15 mg/mL + 25% silk fibroin"},
            15: {"kpa": 13.8, "sd": 1.3, "conc": 2.7, "detail": "fibrin 27 mg/mL + 25% silk fibroin"},
            30: {"kpa": 31.8, "sd": 2.8, "conc": 5.0, "detail": "fibrin 50 mg/mL + 25% silk fibroin"},
        },
        "PEG_dextran": {
            1: {"kpa": 1.0, "sd": 0.3, "conc": None, "detail": "2.3 mM PEG-linker, 3 mM SG-dextran"},
            15: {"kpa": 16.2, "sd": 1.8, "conc": None, "detail": "5 mM PEG-linker, 5.8 mM SG-dextran"},
            30: {"kpa": 29.6, "sd": 3.0, "conc": None, "detail": "7.5 mM PEG-linker, 8.2 mM SG-dextran"},
        },
    }
    xl = {"fibrin": "enzymatic", "silk_fibrin": "enzymatic", "PEG_dextran": "chemical"}
    ligand = {"fibrin": 1.0, "silk_fibrin": 1.0, "PEG_dextran": 0.0}
    surface = {"fibrin": "native", "silk_fibrin": "native", "PEG_dextran": "none"}

    # Only numeric viability that the paper states in text.
    viability = {
        ("fibrin", 1, "TGF_b3"): (92.0, 6.0),
        ("fibrin", 30, "TGF_b3"): (99.0, 1.0),
        ("silk_fibrin", 1, "TGF_b3"): (89.0, 9.0),
        ("silk_fibrin", 30, "TGF_b3"): (98.0, 1.0),
        ("PEG_dextran", 1, "none"): (67.0, 1.0),
        ("PEG_dextran", 30, "none"): (5.0, None),  # "no measurable viability"; store a floor with note
    }
    morphology = {
        (1, "none"): (0.2, "fibroblastic / elongated"),
        (1, "TGF_b3"): (0.2, "fibroblastic even with TGF"),
        (15, "none"): (0.4, "mixed"),
        (15, "TGF_b3"): (0.5, "mixed, more cells"),
        (30, "none"): (0.8, "mostly spherical"),
        (30, "TGF_b3"): (0.95, "spherical clusters / chondron-like"),
    }
    rows = []
    for material in ("fibrin", "silk_fibrin", "PEG_dextran"):
        for nominal in (1, 15, 30):
            for gf in ("none", "TGF_b3"):
                meta = stiffness[material][nominal]
                exp_id = f"bachmann2020-{material}-{nominal}kpa-{gf}"
                meas = []
                key = (material, nominal, gf)
                # PEG viability numbers given without specifying TGF; attach to none,
                # and also to TGF if the text says decline is stiffness-driven.
                if key in viability:
                    val, sd = viability[key]
                    extra = None
                    if material == "PEG_dextran" and nominal == 30:
                        extra = "Paper: no measurable viability at 30 kPa; coded 5% floor, not a live/dead mean."
                    meas.append(_m("viability_pct", val, "%", sd=sd, evidence="numeric_text", n=9, notes=extra))
                if material == "PEG_dextran" and not any(m.get("assay") == "viability_pct" for m in meas):
                    label = "undetectable_like_30kPa" if nominal == 30 else "intermediate_decline"
                    meas.append(
                        _m(
                            "viability_pct",
                            None,
                            "%",
                            qualitative=label,
                            evidence="qualitative_text",
                            notes="TGF condition not given a separate live/dead %; stiffness effect is the reported result.",
                        )
                    )
                    meas.append(
                        _m(
                            "viability_pct",
                            None,
                            "%",
                            qualitative="declining_vs_1kPa",
                            evidence="qualitative_text",
                            notes="Paper: viability declines steeply between 1 kPa (67%) and 30 kPa (undetectable); 15 kPa not given as a percent.",
                        )
                    )
                if material in {"fibrin", "silk_fibrin"}:
                    morph_val, morph_note = morphology[(nominal, gf)]
                    meas.append(
                        _m(
                            "morphology_spherical",
                            morph_val,
                            "ordinal",
                            evidence="qualitative_text",
                            notes=morph_note,
                        )
                    )
                    ecm_ord = 0.3 + 0.25 * (nominal / 15) + (0.3 if gf == "TGF_b3" else 0)
                    if nominal == 1 and gf != "TGF_b3":
                        ecm_ord = 0.3
                    meas.append(
                        _m(
                            "sgag_histology",
                            min(ecm_ord, 1.0),
                            "ordinal",
                            evidence="qualitative_text",
                            notes="Mapped from alcian-blue description; not a µg assay.",
                        )
                    )
                if material == "fibrin" and gf == "none" and nominal == 1:
                    meas.append(_m("col2_col1_ratio", 0.71, "ratio", sd=0.05, evidence="numeric_text", n=9))
                if material == "fibrin" and gf == "none" and nominal == 30:
                    meas.append(_m("col2_col1_ratio", 1.75, "ratio", sd=1.15, evidence="numeric_text", n=9))
                rows.append(
                    {
                        "experiment_id": exp_id,
                        "study_id": "bachmann2020",
                        "material_class": material,
                        "material_detail": meta["detail"],
                        "crosslinking": xl[material],
                        "polymer_concentration_wt_pct": meta["conc"],
                        "stiffness_kpa": meta["kpa"],
                        "stiffness_sd_kpa": meta["sd"],
                        "stiffness_method": "rheology_youngs_affine_nu0.5",
                        "surface_chemistry": surface[material],
                        "has_adhesion_ligand": ligand[material],
                        "cell_type": "articular_chondrocyte",
                        "species": "human",
                        "culture_model": "3D_encapsulation",
                        "growth_factor": gf,
                        "culture_time_days": 21,
                        "cell_density_million_per_ml": 4.0,
                        "passage": 2,
                        "n_replicates": 9,
                        "extracted_from": "methods Table 2 + viability paragraph + Fig 2/5",
                        "curator_confidence": "high" if key in viability or (material == "fibrin" and gf == "none") else "medium",
                        "notes": f"Nominal {nominal} kPa series.",
                        "measurements": meas,
                    }
                )
    return rows


def _other_experiments() -> list[dict]:
    rows = []
    # Li 2016 — three AFM stiffnesses, same 10 wt% GelMA.
    for kpa, dof, ecm_ord, morph, note in [
        (3.8, "DoF 25.8%", 0.25, 0.2, "Elongated; weak safranin-O"),
        (17.1, "DoF intermediate", 0.45, 0.5, "Mixed morphology; partial proteoglycan"),
        (29.9, "DoF 91.7%", 0.85, 0.9, "Round clusters; strongest sGAG/DNA and Col2a1/Acan"),
    ]:
        rows.append(
            {
                "experiment_id": f"li2016-gelma-{kpa}",
                "study_id": "li2016",
                "material_class": "GelMA",
                "material_detail": f"10 wt% GelMA, {dof}",
                "crosslinking": "photocrosslink",
                "polymer_concentration_wt_pct": 10.0,
                "stiffness_kpa": kpa,
                "stiffness_method": "AFM_hertz",
                "surface_chemistry": "native",
                "has_adhesion_ligand": 1.0,
                "cell_type": "articular_chondrocyte",
                "species": "bovine",
                "culture_model": "3D_encapsulation",
                "growth_factor": "none",
                "culture_time_days": 14,
                "cell_density_million_per_ml": 20.0,
                "passage": 2,
                "extracted_from": "text + Fig 3/5/8",
                "curator_confidence": "high",
                "notes": note,
                "measurements": [
                    _m("viability_pct", None, "%", qualitative="high", evidence="qualitative_text", notes="Live/dead: mostly live, no percent reported."),
                    _m("morphology_spherical", morph, "ordinal", evidence="qualitative_text"),
                    _m("sgag_histology", ecm_ord, "ordinal", evidence="qualitative_text", notes="Relative safranin-O / sGAG/DNA ranking inside the paper."),
                ],
            }
        )

    # Zhang 2024 — three concentrations with numeric viability.
    for label, conc, kpa_est, viab, sd, gene, note in [
        ("low", 6.0, None, 93.24, 0.99, 0.8, "Highest viability; high SOX9/Agg/Col2 vs high group"),
        ("med", 9.0, None, 92.04, 1.49, 0.85, "Best chondrospheres; high chondrogenic genes"),
        ("high", 12.0, None, 88.46, 1.53, 0.45, "Significantly lower SOX9/Agg/Col2"),
    ]:
        meas = [
            _m("viability_pct", viab, "%", sd=sd, evidence="numeric_text"),
            _m("sgag_histology", gene, "ordinal", evidence="qualitative_text", notes="Gene/histology ranking, not µg."),
        ]
        rows.append(
            {
                "experiment_id": f"zhang2024-gelalg-{label}",
                "study_id": "zhang2024",
                "material_class": "gelatin_alginate",
                "material_detail": f"{label} concentration gelatin–alginate bioink",
                "crosslinking": "ionic",
                "polymer_concentration_wt_pct": conc,
                "stiffness_kpa": kpa_est,
                "stiffness_method": None,
                "surface_chemistry": "native",
                "has_adhesion_ligand": 1.0,
                "cell_type": "articular_chondrocyte",
                "culture_model": "3D_bioprint",
                "growth_factor": "none",
                "culture_time_days": 21,
                "extracted_from": "viability sentence + RT-PCR ranking",
                "curator_confidence": "high",
                "notes": note + " Stiffness not reported as Young's modulus; left NULL.",
                "measurements": meas,
            }
        )

    # DeKosky mechanical + qualitative viability.
    for name, material, kpa, conc, xl in [
        ("agarose", "agarose", 28.0, 2.0, "thermal"),
        ("peg", "PEG", 36.0, 10.0, "photocrosslink"),
        ("ipn-cells", "PEG", 100.0, 12.0, "photocrosslink"),
    ]:
        rows.append(
            {
                "experiment_id": f"dekosky2010-{name}",
                "study_id": "dekosky2010",
                "material_class": material,
                "material_detail": name,
                "crosslinking": xl,
                "polymer_concentration_wt_pct": conc,
                "stiffness_kpa": kpa,
                "stiffness_method": "unconfined_compression_youngs",
                "surface_chemistry": "none",
                "has_adhesion_ligand": 0.0,
                "cell_type": "articular_chondrocyte",
                "species": "bovine",
                "culture_model": "3D_encapsulation",
                "growth_factor": "none",
                "culture_time_days": 21,
                "extracted_from": "mechanical table + viability sentence",
                "curator_confidence": "medium",
                "notes": "Young's from paper table (IPN+cells 100±25 kPa). Viability: majority alive at 1 week, no %.",
                "measurements": [
                    _m("viability_pct", None, "%", qualitative="majority_alive_week1", evidence="qualitative_text"),
                ],
            }
        )

    # Bryant 2004 degradable PEG series.
    for conc, kpa in [(10.0, 60.0), (15.0, 180.0), (20.0, 500.0)]:
        rows.append(
            {
                "experiment_id": f"bryant2004-peg-{int(conc)}pct",
                "study_id": "bryant2004",
                "material_class": "PEG",
                "material_detail": f"{conc:.0f}% macromer, fast-degrading + slow crosslinks",
                "crosslinking": "photocrosslink",
                "polymer_concentration_wt_pct": conc,
                "stiffness_kpa": kpa,
                "stiffness_method": "compressive_modulus",
                "surface_chemistry": "MMP_degradable",
                "has_adhesion_ligand": 0.0,
                "cell_type": "articular_chondrocyte",
                "species": "bovine",
                "culture_model": "3D_encapsulation",
                "growth_factor": "none",
                "culture_time_days": 28,
                "extracted_from": "abstract + methods (10/15/20% → 60–500 kPa)",
                "curator_confidence": "medium",
                "notes": "15% described as best match of mass loss to tissue secretion. No live/dead % in abstract.",
                "measurements": [
                    _m("sgag_histology", 0.7, "ordinal", evidence="qualitative_text", notes="GAG and collagen produced in all three gels."),
                ],
            }
        )

    for deg, half, ecm in [("mmp", 12.0, 0.85), ("nondeg", 200.0, 0.45)]:
        rows.append(
            {
                "experiment_id": f"sridhar2015-peg-{deg}",
                "study_id": "sridhar2015",
                "material_class": "PEG",
                "material_detail": "PEG-norbornene ± MMP peptide, tethered TGF-β1",
                "crosslinking": "chemical",
                "polymer_concentration_wt_pct": 10.0,
                "surface_chemistry": "MMP_degradable" if deg == "mmp" else "none",
                "has_adhesion_ligand": 0.0,
                "degradation_half_life_days": half,
                "cell_type": "articular_chondrocyte",
                "species": "human",
                "culture_model": "3D_encapsulation",
                "growth_factor": "TGF_b1",
                "culture_time_days": 14,
                "extracted_from": "abstract",
                "curator_confidence": "medium",
                "notes": "Degradable gels: significantly more GAG and collagen, more distributed matrix. Stiffness not in abstract.",
                "measurements": [
                    _m("viability_pct", None, "%", qualitative="high", evidence="qualitative_text"),
                    _m("sgag_histology", ecm, "ordinal", evidence="qualitative_text"),
                ],
            }
        )

    for tag, kpa, ecm, morph in [
        ("130kpa", 130.78, 0.45, 0.5),
        ("199kpa", 199.35, 0.75, 0.85),
    ]:
        rows.append(
            {
                "experiment_id": f"thomas2017-chitosan-{tag}",
                "study_id": "thomas2017",
                "material_class": "chitosan_HA",
                "crosslinking": "chemical",
                "stiffness_kpa": kpa,
                "stiffness_method": "youngs",
                "surface_chemistry": "native",
                "has_adhesion_ligand": 0.5,
                "cell_type": "articular_chondrocyte",
                "species": "rabbit",
                "culture_model": "3D_encapsulation",
                "growth_factor": "none",
                "culture_time_days": 28,
                "cell_density_million_per_ml": 5.0,
                "extracted_from": "Bachmann 2020 Table 1 + original DOI",
                "curator_confidence": "medium",
                "notes": "Stiffer gels: spherical morphology and increased matrix synthesis.",
                "measurements": [
                    _m("morphology_spherical", morph, "ordinal", evidence="qualitative_text"),
                    _m("sgag_histology", ecm, "ordinal", evidence="qualitative_text"),
                ],
            }
        )

    for tag, conc, kpa, prolif in [("soft", 0.75, 3.7, 0.8), ("stiff", 3.5, 53.2, 0.4)]:
        rows.append(
            {
                "experiment_id": f"schuh2012-agarose-{tag}",
                "study_id": "schuh2012",
                "material_class": "agarose",
                "crosslinking": "thermal",
                "polymer_concentration_wt_pct": conc,
                "stiffness_kpa": kpa,
                "stiffness_method": "equilibrium_modulus",
                "surface_chemistry": "none",
                "has_adhesion_ligand": 0.0,
                "cell_type": "articular_chondrocyte",
                "species": "porcine",
                "culture_model": "3D_encapsulation",
                "growth_factor": "none",
                "culture_time_days": 14,
                "cell_density_million_per_ml": 0.6,
                "passage": 2,
                "extracted_from": "Bachmann 2020 Table 1",
                "curator_confidence": "medium",
                "notes": "Increased proliferation in softer gels; no phenotype difference reported.",
                "measurements": [
                    _m("dna_fold_vs_day0", None, "fold", qualitative="higher_in_soft", evidence="qualitative_text"),
                ],
            }
        )

    # Ma 2012 fibrin/alginate — no Young's modulus; do not invent one.
    for name, material, fib_mg, alg_mg, prolif, ecm in [
        ("fibrin", "fibrin", None, None, 0.9, 0.25),
        ("FA45-4", "fibrin_alginate", 45.0, 4.0, 0.8, 0.45),
        ("FA40-8", "fibrin_alginate", 40.0, 8.0, 0.75, 0.8),
        ("FA30-16", "fibrin_alginate", 30.0, 16.0, 0.45, 0.65),
        ("alginate", "alginate", None, 20.0, 0.35, 0.75),
    ]:
        conc = None
        if fib_mg is not None or alg_mg is not None:
            conc = ((fib_mg or 0) + (alg_mg or 0)) / 10.0
        detail = name
        if fib_mg is not None:
            detail = f"{fib_mg:g} mg/mL fibrin / {alg_mg:g} mg/mL alginate"
        rows.append(
            {
                "experiment_id": f"ma2012-{name}-d28",
                "study_id": "ma2012",
                "material_class": material,
                "material_detail": detail,
                "crosslinking": "ionic" if material == "alginate" else "enzymatic",
                "polymer_concentration_wt_pct": conc,
                "surface_chemistry": "none" if material == "alginate" else "native",
                "has_adhesion_ligand": 0.0 if material == "alginate" else 1.0,
                "cell_type": "MSC",
                "species": "human",
                "culture_model": "3D_encapsulation",
                "growth_factor": "TGF_b3",
                "culture_time_days": 28,
                "extracted_from": "results 3.4 DNA/sGAG rankings",
                "curator_confidence": "medium",
                "notes": "FA 40:8 highest total sGAG. DNA higher in fibrin-rich gels. Young's modulus not reported.",
                "measurements": [
                    _m("dna_fold_vs_day0", None, "fold", qualitative=f"rank_{prolif}", evidence="qualitative_text"),
                    _m("sgag_histology", ecm, "ordinal", evidence="qualitative_text", notes="Relative total sGAG ranking."),
                ],
            }
        )

    for ink, material, hyaline in [
        ("agarose", "agarose", 0.85),
        ("alginate", "alginate", 0.85),
        ("GelMA", "GelMA", 0.4),
        ("BioINK-PEGMA", "PEGMA", 0.4),
    ]:
        rows.append(
            {
                "experiment_id": f"daly2016-{ink}",
                "study_id": "daly2016",
                "material_class": material,
                "material_detail": ink,
                "cell_type": "MSC",
                "culture_model": "3D_bioprint",
                "growth_factor": "TGF_b3",
                "culture_time_days": 28,
                "extracted_from": "abstract",
                "curator_confidence": "medium",
                "notes": "Alginate/agarose → hyaline-like (collagen II). GelMA/PEGMA → fibrocartilage (I+II). Stiffness not given.",
                "measurements": [
                    _m("viability_pct", 80.0, "%", evidence="numeric_text", notes="Abstract: high viability in all bioinks post-printing (~80%)."),
                    _m("sgag_histology", hyaline, "ordinal", evidence="qualitative_text", notes="Collagen II vs I+II ranking."),
                ],
            }
        )

    for tag, conc, half, ecm in [("fast", 2.0, 7.0, 0.55), ("slow", 5.0, 28.0, 0.75)]:
        rows.append(
            {
                "experiment_id": f"chung2009-ha-{tag}",
                "study_id": "chung2009",
                "material_class": "HA",
                "crosslinking": "photocrosslink",
                "polymer_concentration_wt_pct": conc,
                "degradation_half_life_days": half,
                "surface_chemistry": "native",
                "has_adhesion_ligand": 0.7,
                "cell_type": "MSC",
                "species": "human",
                "culture_model": "3D_encapsulation",
                "growth_factor": "TGF_b3",
                "culture_time_days": 14,
                "extracted_from": "abstract + related HA design papers",
                "curator_confidence": "low",
                "notes": "Degradation timing vs matrix distribution. Stiffness not isolated from concentration.",
                "measurements": [
                    _m("sgag_histology", ecm, "ordinal", evidence="qualitative_text"),
                ],
            }
        )
    return rows


def _queue_pass_experiments() -> list[dict]:
    """Hand extraction of OA fulltext from the ranked queue. Missing = omit."""
    rows = []

    # Paul 2023 — GelMA vs GelMA-GC. Live/dead >70% only; day-1 cell-laden E as gel stiffness.
    for tag, material, detail, conc, kpa, sd, d28_e in [
        ("gelma", "GelMA", "15% w/v GelMA, Ru/SPS 405 nm, free-swelling", 15.0, 118.1, 11.3, "166.8±20.2 kPa at day 28 (ECM-included, not stored as gel E)"),
        ("gelma-gc", "GelMA_chitosan", "15% w/v GelMA + 1% w/v glycol chitosan, Ru/SPS 405 nm, free-swelling", 16.0, 148.3, 16.4, "283.7±10.9 kPa at day 28 (ECM-included, not stored as gel E)"),
    ]:
        rows.append(
            {
                "experiment_id": f"paul2023-{tag}-d28",
                "study_id": "paul2023",
                "material_class": material,
                "material_detail": detail,
                "crosslinking": "photocrosslink",
                "polymer_concentration_wt_pct": conc,
                "stiffness_kpa": kpa,
                "stiffness_sd_kpa": sd,
                "stiffness_method": "microindentation_youngs_day1_cell_laden",
                "surface_chemistry": "native",
                "has_adhesion_ligand": 1.0,
                "cell_type": "articular_chondrocyte",
                "species": "bovine",
                "culture_model": "3D_encapsulation",
                "growth_factor": "TGF_b3",
                "culture_time_days": 28,
                "cell_density_million_per_ml": 8.3,
                "passage": 1,
                "n_replicates": 4,
                "extracted_from": "PMC10492648 methods + Fig 1/2 text",
                "curator_confidence": "medium",
                "notes": f"Viability described as >70% for embedded chondrocytes; no live/dead mean in text. {d28_e}",
                "measurements": [
                    _m(
                        "viability_pct",
                        None,
                        "%",
                        qualitative="high_>70",
                        evidence="qualitative_text",
                        notes="Abstract/results: >70% viability of embedded chondrocytes; figure has a percent panel without a number in text.",
                    ),
                ],
            }
        )

    # Pérez-Díaz 2023 — surface-seeded AD-hMSC; only the 3D-construct calcein number.
    rows.append(
        {
            "experiment_id": "perezdiaz2023-gelcspva-d15",
            "study_id": "perezdiaz2023",
            "material_class": "chitosan_gelatin_PVA",
            "material_detail": "Gel/CS/PVA 1:1:1, freeze-dried, steam sterilized; cells seeded onto the hydrogel",
            "crosslinking": "chemical",
            "surface_chemistry": "native",
            "has_adhesion_ligand": 1.0,
            "cell_type": "adipose_MSC",
            "species": "human",
            "culture_model": "2D",
            "growth_factor": "none",
            "culture_time_days": 15,
            "extracted_from": "PMC10574893 results 3.4 calcein on construct",
            "curator_confidence": "high",
            "notes": "Not 3D encapsulation. Monolayer 95.78/96% and autoclave 103.4 kPa omitted.",
            "measurements": [
                _m(
                    "viability_pct",
                    87.16,
                    "%",
                    evidence="numeric_text",
                    notes="Calcein-AM on Gel/CS/PVA construct; 12.83% dead. Discussion also says 87%.",
                ),
            ],
        }
    )

    # Ortega 2024 — auricular chondrocytes in CS/Gel/PVA; individual-cell Live/Dead.
    for days, viab, cluster in [
        (7, 98.8, 99.21),
        (14, 98.69, 98.96),
    ]:
        rows.append(
            {
                "experiment_id": f"ortega2024-csgelpva-d{days}",
                "study_id": "ortega2024",
                "material_class": "chitosan_gelatin_PVA",
                "material_detail": "CS/Gel/PVA 1:1:1 w/w, 2 wt%, freeze–thaw/freeze-dried, autoclaved; 5e5 cells injected into 8 mm discs",
                "crosslinking": "chemical",
                "polymer_concentration_wt_pct": 2.0,
                "surface_chemistry": "native",
                "has_adhesion_ligand": 1.0,
                "cell_type": "auricular_chondrocyte",
                "species": "human",
                "culture_model": "3D_encapsulation",
                "growth_factor": "none",
                "culture_time_days": days,
                "extracted_from": "PMC10892533 Fig 6 Live/Dead text",
                "curator_confidence": "high",
                "notes": f"Individual-cell Live/Dead {viab}%. Clusters {cluster}% (not a separate gel). MTT extract 100% at 72 h not stored.",
                "measurements": [
                    _m("viability_pct", viab, "%", evidence="numeric_text", notes=f"Individual cells; clusters {cluster}%."),
                ],
            }
        )

    # Aitchison 2024 — C20A4 in alginate + cartilage matrix bioink.
    for days, viab in [(1, 87.2), (7, 76.4), (14, 85.9)]:
        rows.append(
            {
                "experiment_id": f"aitchison2024-alginate-decm-d{days}",
                "study_id": "aitchison2024",
                "material_class": "alginate_dECM",
                "material_detail": "20% w/v alginate + 5% gum arabic + 5% PVA + 5% human articular cartilage matrix powder",
                "crosslinking": "ionic",
                "polymer_concentration_wt_pct": 20.0,
                "surface_chemistry": "native",
                "has_adhesion_ligand": 1.0,
                "cell_type": "articular_chondrocyte",
                "species": "human",
                "culture_model": "3D_bioprint",
                "growth_factor": "none",
                "culture_time_days": days,
                "n_replicates": 5,
                "extracted_from": "PMC11048018 results Live/Dead + Fig 4A",
                "curator_confidence": "high",
                "notes": "C20A4 immortalized human articular chondrocytes, not primary. Day 14 is 85.9% in results (abstract rounded 86%). Stiffness not reported.",
                "measurements": [
                    _m("viability_pct", viab, "%", evidence="numeric_text", n=5),
                ],
            }
        )

    # De Mori 2025 — two stiffnesses × four densities; viability only as floors.
    for kpa, cacl2 in [(5.75, 60), (6.85, 100)]:
        for dens in (1.0, 2.0, 4.0, 16.0):
            if dens == 4.0:
                qual, note = "high_>75", "Paper: 4e6/mL viability significantly lower in both gels but always higher than 75%."
            else:
                qual, note = "high_>95", "Paper: viability always above 95% except the 4e6/mL condition. 2D >98% not stored."
            dens_tag = str(int(dens)) if dens != 1.0 else "1"
            rows.append(
                {
                    "experiment_id": f"demori2025-{cacl2}mM-{dens_tag}e6",
                    "study_id": "demori2025",
                    "material_class": "collagen_alginate",
                    "material_detail": f"Collagen I 0.5% mixed 1:1 with 5% alginate, crosslinked in {cacl2} mM CaCl2",
                    "crosslinking": "ionic",
                    "polymer_concentration_wt_pct": 2.75,
                    "stiffness_kpa": kpa,
                    "stiffness_method": "youngs_from_cacl2_formulation",
                    "surface_chemistry": "native",
                    "has_adhesion_ligand": 1.0,
                    "cell_type": "adipose_MSC",
                    "species": "human",
                    "culture_model": "3D_encapsulation",
                    "growth_factor": "none",
                    "culture_time_days": 7,
                    "cell_density_million_per_ml": dens,
                    "passage": 3,
                    "extracted_from": "PMC11941925 stiffness + viability paragraph",
                    "curator_confidence": "medium",
                    "notes": "No exogenous GF. 0.82 kPa formulation is from the prior paper, not this experiment. Live/Dead timepoint not given as a single day; day 7 is the morphology assay point.",
                    "measurements": [
                        _m("viability_pct", None, "%", qualitative=qual, evidence="qualitative_text", notes=note),
                    ],
                }
            )

    # Rojas 2025 — fibrin vs tricomposite Live/Dead (tildes in the paper).
    for tag, material, detail, days, viab, sd, extra in [
        ("fibrin", "fibrin", "Tisseel fibrin, 220 mg/mL fibrinogen chamber then 1:1 thrombin, 200 µL constructs", 14, 90.0, 3.2, "Paper: ~90 ± 3.2% through day 14."),
        ("fibrin", "fibrin", "Tisseel fibrin, 220 mg/mL fibrinogen chamber then 1:1 thrombin, 200 µL constructs", 28, 95.0, None, "Paper: rose slightly to ~95% between days 14 and 28."),
        ("tricomposite", "fibrin_dECM", "Fibrin + 1.5 mg dACM + 6 mg dAMM per fibrinogen chamber, 200 µL constructs", 14, 99.0, None, "Paper: ~99% throughout 28 days; also >98%."),
        ("tricomposite", "fibrin_dECM", "Fibrin + 1.5 mg dACM + 6 mg dAMM per fibrinogen chamber, 200 µL constructs", 28, 99.0, None, "Paper: ~99% at all time points."),
    ]:
        rows.append(
            {
                "experiment_id": f"rojas2025-{tag}-d{days}",
                "study_id": "rojas2025",
                "material_class": material,
                "material_detail": detail,
                "crosslinking": "enzymatic",
                "polymer_concentration_wt_pct": 11.0,
                "surface_chemistry": "native",
                "has_adhesion_ligand": 1.0,
                "cell_type": "articular_chondrocyte",
                "species": "human",
                "culture_model": "3D_encapsulation",
                "growth_factor": "none",
                "culture_time_days": days,
                "extracted_from": "PMC12841122 Fig 2k Live/Dead text",
                "curator_confidence": "medium",
                "notes": extra + " 1e6 cells added to fibrinogen chamber; final density after 1:1 mix not uniquely stated.",
                "measurements": [
                    _m("viability_pct", viab, "%", sd=sd, evidence="numeric_text", notes=extra),
                ],
            }
        )

    # Levett 2014 — Gel-MA ± 1% HA-MA; high viability, no percent; day-1 cell-laden E.
    for ha, kpa, d56_note in [
        (0, 29.0, "0% HA-MA cell-laden compressive modulus 66 kPa after 8 weeks (ECM; not stored as gel E)."),
        (1, 41.0, "1% HA-MA cell-laden compressive modulus 147 kPa after 8 weeks (ECM; not stored as gel E)."),
    ]:
        rows.append(
            {
                "experiment_id": f"levett2014-gelma-ha{ha}-d28",
                "study_id": "levett2014",
                "material_class": "GelMA" if ha == 0 else "GelMA_HA",
                "material_detail": f"10% w/v total polymer Gel-MA with {ha}% HA-MA, Irgacure 2959, 365 nm",
                "crosslinking": "photocrosslink",
                "polymer_concentration_wt_pct": 10.0,
                "stiffness_kpa": kpa,
                "stiffness_method": "unconfined_compression_day1_cell_laden",
                "surface_chemistry": "native",
                "has_adhesion_ligand": 1.0,
                "cell_type": "articular_chondrocyte",
                "species": "human",
                "culture_model": "3D_encapsulation",
                "growth_factor": "TGF_b3",
                "culture_time_days": 28,
                "cell_density_million_per_ml": 10.0,
                "passage": 1,
                "extracted_from": "PMC4249877 abstract moduli + viability paragraph",
                "curator_confidence": "medium",
                "notes": d56_note,
                "measurements": [
                    _m(
                        "viability_pct",
                        None,
                        "%",
                        qualitative="high",
                        evidence="qualitative_text",
                        notes="Viability not dependent on HA-MA concentration and was high in all groups after 28 days; no percent.",
                    ),
                ],
            }
        )

    # Sun 2015 — PSL PDLLA-PEG/HA. Figure 81% post-fab, not abstract 84%.
    for tag, gf, days, viab, kpa, kpa_sd, extra in [
        ("postfab", "none", 0, 81.0, 780.0, 23.0, "Figure Live/Dead 81% after fabrication; abstract 84% not used. Modulus 780±23 kPa."),
        ("ctrl-d28", "none", 28, 65.0, 240.0, 20.0, "Control medium day 28. Modulus fell with scaffold degradation, not ECM gain."),
        ("tgf-d28", "TGF_b3", 28, 77.0, 238.0, 25.0, "TGF-β3 group day 28. Abstract rounded modulus to 240 kPa; figure 238±25 kPa used."),
    ]:
        rows.append(
            {
                "experiment_id": f"sun2015-pdlapegha-{tag}",
                "study_id": "sun2015",
                "material_class": "PDLLA_PEG_HA",
                "material_detail": "mPDLLA-PEG 30% w/v + mHA 0.5% w/v, LAP 0.6%, visible-light PSL",
                "crosslinking": "photocrosslink",
                "polymer_concentration_wt_pct": 30.0,
                "stiffness_kpa": kpa,
                "stiffness_sd_kpa": kpa_sd,
                "stiffness_method": "unconfined_compression_10pct",
                "surface_chemistry": "native",
                "has_adhesion_ligand": 1.0,
                "cell_type": "adipose_MSC",
                "species": "human",
                "culture_model": "3D_encapsulation",
                "growth_factor": gf,
                "culture_time_days": days,
                "cell_density_million_per_ml": 4.0,
                "extracted_from": "PMC4539543 Fig 3I/Fig 8 + results text",
                "curator_confidence": "high",
                "notes": extra,
                "measurements": [
                    _m("viability_pct", viab, "%", evidence="numeric_text", notes=extra),
                ],
            }
        )

    # Žigon-Branc 2019 — Gel-MOD G′ as kPa (storage modulus, not Young's).
    for conc, gprime, sd in [
        (5.0, 0.538, 0.091),
        (7.5, 3.584, 0.146),
        (10.0, 7.263, 0.287),
    ]:
        tag = str(conc).replace(".", "p")
        rows.append(
            {
                "experiment_id": f"zigon2019-gelmod-{tag}pct",
                "study_id": "zigon2019",
                "material_class": "GelMA",
                "material_detail": f"{conc:g} wt% Gel-MOD (methacrylated gelatin), photoencapsulated hASC/hTERT microspheroids",
                "crosslinking": "photocrosslink",
                "polymer_concentration_wt_pct": conc,
                "stiffness_kpa": gprime,
                "stiffness_sd_kpa": sd,
                "stiffness_method": "rheology_storage_modulus_Gprime",
                "surface_chemistry": "native",
                "has_adhesion_ligand": 1.0,
                "cell_type": "adipose_MSC",
                "species": "human",
                "culture_model": "3D_encapsulation",
                "growth_factor": "none",
                "culture_time_days": 21,
                "extracted_from": "PMC6784494 Table 2 G′ + Live/Dead paragraph",
                "curator_confidence": "medium",
                "notes": "G′ stored in kPa; do not treat as Young's modulus (paper does not convert). Chondrogenic-medium arm is gene/histology; viability is qualitative in all media.",
                "measurements": [
                    _m(
                        "viability_pct",
                        None,
                        "%",
                        qualitative="preserved_3to5_weeks",
                        evidence="qualitative_text",
                        notes="Confocal Live/Dead: all tested hydrogels supported viability over 3–5 weeks; no percent.",
                    ),
                ],
            }
        )

    # Scalzone 2019 — chitosan/BGP MSC-laden gel.
    rows.append(
        {
            "experiment_id": "scalzone2019-chbgp-msc-d3",
            "study_id": "scalzone2019",
            "material_class": "chitosan",
            "material_detail": "Chitosan 2.5% w/v ionically crosslinked with β-glycerophosphate",
            "crosslinking": "ionic",
            "polymer_concentration_wt_pct": 2.5,
            "stiffness_kpa": 36.0,
            "stiffness_sd_kpa": 4.0,
            "stiffness_method": "unconfined_compression_youngs",
            "surface_chemistry": "native",
            "has_adhesion_ligand": 0.5,
            "cell_type": "MSC",
            "species": "human",
            "culture_model": "3D_encapsulation",
            "growth_factor": "none",
            "culture_time_days": 3,
            "cell_density_million_per_ml": 2.0,
            "extracted_from": "PMC6787336 mechanical + Live/Dead day 1/3",
            "curator_confidence": "medium",
            "notes": "Equilibrium Young's 17.4±0.8 kPa after 1000 s; compressive E stored. Chondrocyte spheroids were seeded on top in a co-culture arm, not this row.",
            "measurements": [
                _m(
                    "viability_pct",
                    None,
                    "%",
                    qualitative="high",
                    evidence="qualitative_text",
                    notes="Live/Dead day 1 and 3: encapsulated MSCs viable with round morphology; no percent.",
                ),
            ],
        }
    )

    # Kessel 2020 — bovine chondrocytes outside HA-MA microstrands. Starting gel 2.7 kPa.
    for days, viab, sd, stiff, stiff_sd, extra in [
        (1, 90.1, 0.6, 2.7, 0.3, "Day 1 after printing. Starting compression modulus 2.7±0.3 kPa."),
        (7, 92.3, 1.1, 2.7, 0.3, "Starting gel modulus retained as the material property; construct E not yet the 212 kPa ECM value."),
        (21, 92.6, 2.0, None, None, "Construct compression modulus 212±83.7 kPa at day 21 is ECM, not stored as gel stiffness. Day 42 780.2±218.4 kPa likewise omitted."),
    ]:
        rows.append(
            {
                "experiment_id": f"kessel2020-hama-microstrands-d{days}",
                "study_id": "kessel2020",
                "material_class": "HA",
                "material_detail": "2% w/v HA-MA entangled microstrands (Med, 40 µm); chondrocytes in the interstitial phase, bioprinted",
                "crosslinking": "photocrosslink",
                "polymer_concentration_wt_pct": 2.0,
                "stiffness_kpa": stiff,
                "stiffness_sd_kpa": stiff_sd,
                "stiffness_method": None if stiff is None else "unconfined_compression_fresh_print",
                "surface_chemistry": "native",
                "has_adhesion_ligand": 0.7,
                "cell_type": "articular_chondrocyte",
                "species": "bovine",
                "culture_model": "3D_bioprint",
                "growth_factor": "none",
                "culture_time_days": days,
                "passage": 3,
                "n_replicates": 3,
                "extracted_from": "PMC7509724 Fig 6A/7C chondrocyte arm",
                "curator_confidence": "high",
                "notes": extra + " Myoblast-in-GelMA 93% numbers not stored. Pre-print 95.3±0.5% is the unprinted cell mix, not a gel condition.",
                "measurements": [
                    _m("viability_pct", viab, "%", sd=sd, evidence="numeric_text", n=3, notes=extra),
                ],
            }
        )
    return rows


def _queue_pass_more() -> list[dict]:
    """Second OA/abstract pass: published numbers only."""
    rows = []

    # Hu 2012 — visible-light MeGC, abstract pairs modulus with viability.
    for tag, kpa, viab, extra in [
        ("cq-600s", 2.8, 5.0, "CQ initiator, 600 s irradiation. Abstract: viability reduced to 5%."),
        ("fr-600s", 4.4, 25.0, "FR initiator, 600 s. Abstract: viability reduced to 25%."),
        ("rf-40s", None, 85.0, "RF initiator, 40 s. Abstract: 80–90% viability; stored as 85% midpoint of the stated range."),
        ("rf-300s", 8.5, 85.0, "RF initiator, 300 s. Abstract: 8.5 kPa without reducing viability vs 40 s."),
    ]:
        rows.append(
            {
                "experiment_id": f"hu2012-megc-{tag}",
                "study_id": "hu2012",
                "material_class": "chitosan",
                "material_detail": "Methacrylated glycol chitosan (MeGC), visible-light photocrosslink",
                "crosslinking": "photocrosslink",
                "stiffness_kpa": kpa,
                "stiffness_method": None if kpa is None else "compressive_modulus_abstract",
                "surface_chemistry": "native",
                "has_adhesion_ligand": 0.5,
                "cell_type": "articular_chondrocyte",
                "culture_model": "3D_encapsulation",
                "growth_factor": "none",
                "extracted_from": "abstract",
                "curator_confidence": "medium",
                "notes": extra,
                "measurements": [
                    _m("viability_pct", viab, "%", evidence="numeric_text", notes=extra),
                ],
            }
        )

    # Markstedt 2015 — nanocellulose–alginate bioink.
    for days, viab in [(1, 73.0), (7, 86.0)]:
        rows.append(
            {
                "experiment_id": f"markstedt2015-nfc-alg-d{days}",
                "study_id": "markstedt2015",
                "material_class": "cellulose_alginate",
                "material_detail": "Nanocellulose–alginate bioink, human chondrocytes bioprinted",
                "crosslinking": "ionic",
                "surface_chemistry": "native",
                "has_adhesion_ligand": 0.5,
                "cell_type": "articular_chondrocyte",
                "species": "human",
                "culture_model": "3D_bioprint",
                "growth_factor": "none",
                "culture_time_days": days,
                "extracted_from": "abstract",
                "curator_confidence": "high",
                "notes": "Abstract live/dead after 1 and 7 days of 3D culture. Stiffness not in abstract.",
                "measurements": [
                    _m("viability_pct", viab, "%", evidence="numeric_text"),
                ],
            }
        )

    # Lindborg 2015 — chitosan–HA hydrocolloid.
    rows.append(
        {
            "experiment_id": "lindborg2015-chitosan-ha-d1",
            "study_id": "lindborg2015",
            "material_class": "chitosan_HA",
            "material_detail": "Chitosan–hyaluronan hydrogel-hydrocolloid hydrated with serum",
            "crosslinking": "ionic",
            "stiffness_kpa": 0.264,
            "stiffness_sd_kpa": 0.038,
            "stiffness_method": "elastic_modulus_Pa_to_kPa",
            "surface_chemistry": "native",
            "has_adhesion_ligand": 1.0,
            "cell_type": "MSC",
            "species": "human",
            "culture_model": "3D_encapsulation",
            "growth_factor": "none",
            "culture_time_days": 1,
            "extracted_from": "abstract",
            "curator_confidence": "high",
            "notes": "Abstract: 264±38 Pa formed in seconds; 48% viability during the first 24 h, then a steady state to day 14 (no later percent).",
            "measurements": [
                _m("viability_pct", 48.0, "%", evidence="numeric_text", notes="First 24 h only."),
            ],
        }
    )

    # Yang 2020 — agarose Young's series, MACT, no live/dead %.
    for conc, kpa in [
        (0.5, 0.49),
        (1.0, 0.93),
        (2.5, 3.30),
        (5.0, 8.78),
        (7.5, 14.60),
        (10.0, 23.08),
    ]:
        tag = str(conc).replace(".", "p")
        rows.append(
            {
                "experiment_id": f"yang2020-agarose-{tag}pct",
                "study_id": "yang2020",
                "material_class": "agarose",
                "material_detail": f"{conc:g}% w/v agarose, matrix-assisted chondrocyte transplantation interface",
                "crosslinking": "thermal",
                "polymer_concentration_wt_pct": conc,
                "stiffness_kpa": kpa,
                "stiffness_method": "youngs_table1",
                "surface_chemistry": "none",
                "has_adhesion_ligand": 0.0,
                "cell_type": "articular_chondrocyte",
                "species": "human",
                "culture_model": "3D_encapsulation",
                "growth_factor": "none",
                "passage": 2,
                "extracted_from": "PMC7151603 Table 1 + results",
                "curator_confidence": "high",
                "notes": "Paper identifies 3.30 kPa (2.5%) as optimal integration. No live/dead percent in text.",
                "measurements": [
                    _m(
                        "sgag_histology",
                        0.8 if conc == 2.5 else (0.6 if conc <= 1.0 else 0.35),
                        "ordinal",
                        evidence="qualitative_text",
                        notes="Relative cartilage–hydrogel integration ranking from the text, not µg.",
                    ),
                ],
            }
        )

    # Snyder 2014 — fibrin/HA-MA compressive moduli.
    for fib, ha, kpa, sd in [
        (4.0, 0.0, 1.62, 0.6),
        (4.0, 1.5, 4.19, 0.28),
        (6.0, 0.0, 3.39, 0.91),
        (6.0, 1.5, 6.76, 0.52),
    ]:
        ha_tag = "ha0" if ha == 0 else "ha15"
        rows.append(
            {
                "experiment_id": f"snyder2014-fib{int(fib)}-{ha_tag}",
                "study_id": "snyder2014",
                "material_class": "fibrin_HA" if ha else "fibrin",
                "material_detail": f"{fib:g} mg/mL fibrinogen + {ha:g} mg/mL HA-MA",
                "crosslinking": "photocrosslink" if ha else "enzymatic",
                "polymer_concentration_wt_pct": fib / 10.0,
                "stiffness_kpa": kpa,
                "stiffness_sd_kpa": sd,
                "stiffness_method": "compressive_modulus",
                "surface_chemistry": "native",
                "has_adhesion_ligand": 1.0,
                "cell_type": "MSC",
                "species": "human",
                "culture_model": "3D_encapsulation",
                "growth_factor": "none",
                "culture_time_days": 6,
                "extracted_from": "PMC4109069 mechanical paragraph + live/dead",
                "curator_confidence": "medium",
                "notes": "Live/dead and PrestoBlue show a suitable 3D environment; no percent. HA-MA 0 vs 1.5 mg/mL from the reported range.",
                "measurements": [
                    _m(
                        "viability_pct",
                        None,
                        "%",
                        qualitative="high",
                        evidence="qualitative_text",
                        notes="Live/dead: increasing numbers of viable cells; no percent.",
                    ),
                ],
            }
        )

    # Kim 2015 — MeGC ± Col II + TGF-β1, >90% at day 21.
    for tag, gf, extra in [
        ("megc", "none", "MeGC only."),
        ("megc-col-tgf", "TGF_b1", "MeGC + collagen II + conjugated TGF-β1."),
    ]:
        rows.append(
            {
                "experiment_id": f"kim2015-{tag}-d21",
                "study_id": "kim2015",
                "material_class": "chitosan",
                "material_detail": extra,
                "crosslinking": "photocrosslink",
                "surface_chemistry": "native",
                "has_adhesion_ligand": 1.0 if "col" in tag else 0.5,
                "cell_type": "MSC",
                "species": "human",
                "culture_model": "3D_encapsulation",
                "growth_factor": gf,
                "culture_time_days": 21,
                "extracted_from": "PMC4350967 Live/Dead paragraph",
                "curator_confidence": "medium",
                "notes": "hSMSC. Live/dead >90% in all tested hydrogels at day 21; figure has a percent panel without a number in text.",
                "measurements": [
                    _m(
                        "viability_pct",
                        None,
                        "%",
                        qualitative="high_>90",
                        evidence="qualitative_text",
                    ),
                ],
            }
        )

    # Ingavle 2012 — agarose–PEGDA IPN ± CS.
    rows.append(
        {
            "experiment_id": "ingavle2012-ipn-d42",
            "study_id": "ingavle2012",
            "material_class": "PEG",
            "material_detail": "Agarose–PEGDA IPN unmodified",
            "crosslinking": "photocrosslink",
            "surface_chemistry": "none",
            "has_adhesion_ligand": 0.0,
            "cell_type": "articular_chondrocyte",
            "culture_model": "3D_encapsulation",
            "growth_factor": "none",
            "culture_time_days": 42,
            "extracted_from": "abstract",
            "curator_confidence": "medium",
            "notes": "Abstract: 35% of encapsulated chondrocytes remained viable at 6 weeks in the unmodified IPN.",
            "measurements": [
                _m("viability_pct", 35.0, "%", evidence="numeric_text", notes="Below the 40% regex harvest floor; this is a published live fraction."),
            ],
        }
    )
    rows.append(
        {
            "experiment_id": "ingavle2012-cs-ipn-d42",
            "study_id": "ingavle2012",
            "material_class": "PEG",
            "material_detail": "Agarose–PEGDA IPN + ~0.5 wt% methacrylated chondroitin sulfate",
            "crosslinking": "photocrosslink",
            "surface_chemistry": "native",
            "has_adhesion_ligand": 0.3,
            "cell_type": "articular_chondrocyte",
            "culture_model": "3D_encapsulation",
            "growth_factor": "none",
            "culture_time_days": 42,
            "extracted_from": "abstract",
            "curator_confidence": "medium",
            "notes": "Abstract: more than 50% viable at 6 weeks. Stored as a floor label, not a live/dead mean.",
            "measurements": [
                _m(
                    "viability_pct",
                    None,
                    "%",
                    qualitative="floor_>50",
                    evidence="qualitative_text",
                    notes="Paper: more than 50%; not coded as 50% because it is a floor, not a mean.",
                ),
            ],
        }
    )

    # Zignego 2014 — 4.5% agarose, >95%.
    rows.append(
        {
            "experiment_id": "zignego2014-agarose-4p5-d3",
            "study_id": "zignego2014",
            "material_class": "agarose",
            "material_detail": "4.5% agarose, high-stiffness gel for 10% compression of primary human chondrocytes",
            "crosslinking": "thermal",
            "polymer_concentration_wt_pct": 4.5,
            "surface_chemistry": "none",
            "has_adhesion_ligand": 0.0,
            "cell_type": "articular_chondrocyte",
            "species": "human",
            "culture_model": "3D_encapsulation",
            "growth_factor": "none",
            "culture_time_days": 3,
            "extracted_from": "abstract",
            "curator_confidence": "medium",
            "notes": "Abstract: >95% viability at 24 and 72 h. Native PCM 25–200 kPa is not stored as gel stiffness.",
            "measurements": [
                _m(
                    "viability_pct",
                    None,
                    "%",
                    qualitative="high_>95",
                    evidence="qualitative_text",
                ),
            ],
        }
    )

    # Maneechan 2026 — hydrated 5.40 kPa; MTT extract not stored as 3D viability.
    rows.append(
        {
            "experiment_id": "maneechan2026-cs-silk-hydrated",
            "study_id": "maneechan2026",
            "material_class": "chitosan_silk",
            "material_detail": "Chitosan–silk fibroin with Aloe vera and Mimosa, TGF-β3 adsorbed, freeze-dried then hydrated",
            "crosslinking": "chemical",
            "stiffness_kpa": 5.40,
            "stiffness_sd_kpa": 3.73,
            "stiffness_method": "unconfined_compression_hydrated",
            "surface_chemistry": "native",
            "has_adhesion_ligand": 1.0,
            "cell_type": "articular_chondrocyte",
            "culture_model": "3D_encapsulation",
            "growth_factor": "TGF_b3",
            "extracted_from": "PMC13259354 mechanical + MTT paragraphs",
            "curator_confidence": "medium",
            "notes": "Dry E 46.63 kPa not stored. MTT 98.8±1.5% at 24 h is transwell extract cytocompatibility, not 3D live/dead.",
            "measurements": [
                _m(
                    "viability_pct",
                    None,
                    "%",
                    qualitative="noncytotoxic_extract",
                    evidence="qualitative_text",
                    notes="Indirect MTT not different from control at 24 h; 72 h 112.9% is proliferation, not stored as viability.",
                ),
            ],
        }
    )

    # Lee 2025 — DAS-collagen Young's ~3 / 30 / 125 kPa.
    for tag, kpa, naoh in [("soft", 3.0, "0.25 N"), ("mid", 30.0, "0.5 N"), ("stiff", 125.0, "0.75 N")]:
        rows.append(
            {
                "experiment_id": f"lee2025-dascol-{tag}",
                "study_id": "lee2025",
                "material_class": "collagen",
                "material_detail": f"Dialdehyde starch cross-linked collagen–heparin, reconstituted with {naoh} NaOH",
                "crosslinking": "chemical",
                "stiffness_kpa": kpa,
                "stiffness_method": "youngs_compression_approx",
                "surface_chemistry": "native",
                "has_adhesion_ligand": 1.0,
                "cell_type": "articular_chondrocyte",
                "culture_model": "3D_encapsulation",
                "growth_factor": "TGF_b3",
                "cell_density_million_per_ml": 2.0,
                "extracted_from": "PMC12652762 compression + live/dead",
                "curator_confidence": "medium",
                "notes": "Paper reports ~3 / ~30 / ~125 kPa. Live/dead qualitative; TGF-β3 arm has more cells, no percent.",
                "measurements": [
                    _m(
                        "viability_pct",
                        None,
                        "%",
                        qualitative="high",
                        evidence="qualitative_text",
                    ),
                ],
            }
        )

    # Rouillard 2011 — photocrosslinked alginate, initiator-dependent viability floors.
    rows.append(
        {
            "experiment_id": "rouillard2011-alg-va086",
            "study_id": "rouillard2011",
            "material_class": "alginate",
            "material_detail": "Methacrylated alginate photocrosslinked with VA-086",
            "crosslinking": "photocrosslink",
            "stiffness_method": "aggregate_modulus_range_not_paired",
            "surface_chemistry": "native",
            "has_adhesion_ligand": 0.5,
            "cell_type": "articular_chondrocyte",
            "species": "bovine",
            "culture_model": "3D_encapsulation",
            "growth_factor": "none",
            "extracted_from": "abstract",
            "curator_confidence": "medium",
            "notes": "Abstract: >85% viability with VA-086. Construct aggregate moduli 10–20 kPa are a range across 3D gels, not stored as a single Young's modulus.",
            "measurements": [
                _m(
                    "viability_pct",
                    None,
                    "%",
                    qualitative="high_>85",
                    evidence="qualitative_text",
                    notes="Paper: hydrogels with encapsulated bovine chondrocytes constructed with >85% viability using VA-086.",
                ),
            ],
        }
    )
    rows.append(
        {
            "experiment_id": "rouillard2011-alg-irg2959",
            "study_id": "rouillard2011",
            "material_class": "alginate",
            "material_detail": "Methacrylated alginate photocrosslinked with Irgacure 2959",
            "crosslinking": "photocrosslink",
            "surface_chemistry": "native",
            "has_adhesion_ligand": 0.5,
            "cell_type": "articular_chondrocyte",
            "species": "bovine",
            "culture_model": "3D_encapsulation",
            "growth_factor": "none",
            "extracted_from": "abstract",
            "curator_confidence": "medium",
            "notes": "Abstract: IRG2959 photogenerated radical leads to viabilities below 70% in the conditions tested. Not stored as 70% because it is a ceiling, not a mean.",
            "measurements": [
                _m(
                    "viability_pct",
                    None,
                    "%",
                    qualitative="below_70",
                    evidence="qualitative_text",
                ),
            ],
        }
    )

    # Nicodemus 2011 — PEG crosslinking density / compressive modulus series.
    for tag, kpa, gag_rank, extra in [
        ("soft", 60.0, 1.0, "Lowest crosslinking. GAG production greatest in this arm."),
        ("mid", 320.0, 0.55, "Intermediate crosslinking. Matrix more pericellular."),
        ("stiff", 590.0, 0.35, "Highest crosslinking. Collagen II / aggrecan staining decreased; MMP-1/13 elevated."),
    ]:
        rows.append(
            {
                "experiment_id": f"nicodemus2011-peg-{tag}",
                "study_id": "nicodemus2011",
                "material_class": "PEG",
                "material_detail": f"PEG hydrogel, compressive modulus {kpa:g} kPa",
                "crosslinking": "photocrosslink",
                "stiffness_kpa": kpa,
                "stiffness_method": "compressive_modulus",
                "surface_chemistry": "none",
                "has_adhesion_ligand": 0.0,
                "cell_type": "articular_chondrocyte",
                "species": "bovine",
                "culture_model": "3D_encapsulation",
                "growth_factor": "none",
                "culture_time_days": 25,
                "extracted_from": "abstract",
                "curator_confidence": "high",
                "notes": extra + " No live/dead percent in the abstract.",
                "measurements": [
                    _m(
                        "sgag_histology",
                        gag_rank,
                        "ordinal",
                        evidence="qualitative_text",
                        notes="Within-paper GAG ranking from crosslinking, not µg.",
                    ),
                ],
            }
        )
    return rows


def _queue_pass_three() -> list[dict]:
    """Third queue pass: published numbers only, including two new live/dead means."""
    rows = []

    # Park 2013 — MeGC ± HA, irradiation time pairs modulus with viability.
    rows.append(
        {
            "experiment_id": "park2013-megc-40s",
            "study_id": "park2013",
            "material_class": "chitosan",
            "material_detail": "Methacrylated glycol chitosan, riboflavin, 40 s visible light",
            "crosslinking": "photocrosslink",
            "surface_chemistry": "native",
            "has_adhesion_ligand": 0.5,
            "cell_type": "articular_chondrocyte",
            "culture_model": "3D_encapsulation",
            "growth_factor": "none",
            "extracted_from": "abstract",
            "curator_confidence": "high",
            "notes": "Minimum irradiation for stable gels. Abstract: 87–90% encapsulated chondrocyte viability. Modulus not given at 40 s.",
            "measurements": [
                _m(
                    "viability_pct",
                    88.5,
                    "%",
                    evidence="numeric_text",
                    notes="Abstract 87–90%; stored as midpoint of the stated range.",
                ),
            ],
        }
    )
    rows.append(
        {
            "experiment_id": "park2013-megc-600s",
            "study_id": "park2013",
            "material_class": "chitosan",
            "material_detail": "MeGC, riboflavin, 600 s visible light",
            "crosslinking": "photocrosslink",
            "stiffness_kpa": 11.0,
            "stiffness_method": "compressive_modulus",
            "surface_chemistry": "native",
            "has_adhesion_ligand": 0.5,
            "cell_type": "articular_chondrocyte",
            "culture_model": "3D_encapsulation",
            "growth_factor": "none",
            "extracted_from": "abstract",
            "curator_confidence": "high",
            "notes": "Long irradiation raised modulus to 11 kPa and dropped viability to 60–65%.",
            "measurements": [
                _m(
                    "viability_pct",
                    62.5,
                    "%",
                    evidence="numeric_text",
                    notes="Abstract 60–65% at 600 s; stored as midpoint.",
                ),
            ],
        }
    )
    rows.append(
        {
            "experiment_id": "park2013-megc-ha-600s",
            "study_id": "park2013",
            "material_class": "chitosan_HA",
            "material_detail": "MeGC plus hyaluronic acid, riboflavin, 600 s",
            "crosslinking": "photocrosslink",
            "stiffness_kpa": 17.0,
            "stiffness_method": "compressive_modulus",
            "surface_chemistry": "native",
            "has_adhesion_ligand": 1.0,
            "cell_type": "articular_chondrocyte",
            "culture_model": "3D_encapsulation",
            "growth_factor": "none",
            "extracted_from": "abstract",
            "curator_confidence": "high",
            "notes": "MeGC/HA 600 s: 17 kPa, viability 60–65% (same viability sentence as MeGC 600 s).",
            "measurements": [
                _m(
                    "viability_pct",
                    62.5,
                    "%",
                    evidence="numeric_text",
                    notes="Abstract 60–65% at 600 s; stored as midpoint.",
                ),
            ],
        }
    )
    rows.append(
        {
            "experiment_id": "park2013-megc-300s-d21",
            "study_id": "park2013",
            "material_class": "chitosan",
            "material_detail": "MeGC, riboflavin, 300 s visible light",
            "crosslinking": "photocrosslink",
            "surface_chemistry": "native",
            "has_adhesion_ligand": 0.5,
            "cell_type": "articular_chondrocyte",
            "culture_model": "3D_encapsulation",
            "growth_factor": "none",
            "culture_time_days": 21,
            "extracted_from": "abstract",
            "curator_confidence": "medium",
            "notes": "300 s: rounded morphology and ~80–87% viability over 21 d. Modulus not reported for this arm.",
            "measurements": [
                _m(
                    "viability_pct",
                    83.5,
                    "%",
                    evidence="numeric_text",
                    notes="Abstract ~80–87% over 21 days; stored as midpoint. Tilde in the paper.",
                ),
            ],
        }
    )

    # Salinas 2007 — PEG ± RGDS, ATP viability.
    rows.append(
        {
            "experiment_id": "salinas2007-peg-norgds",
            "study_id": "salinas2007",
            "material_class": "PEG",
            "material_detail": "PEG mixed-mode thiol-ene, no RGDS",
            "crosslinking": "photocrosslink",
            "surface_chemistry": "none",
            "has_adhesion_ligand": 0.0,
            "cell_type": "MSC",
            "species": "human",
            "culture_model": "3D_encapsulation",
            "growth_factor": "none",
            "culture_time_days": 14,
            "extracted_from": "abstract",
            "curator_confidence": "medium",
            "notes": "No cell–polymer interactions; ATP viability decreased over 14 d without a percent.",
            "measurements": [
                _m(
                    "viability_pct",
                    None,
                    "%",
                    qualitative="decreasing",
                    evidence="qualitative_text",
                    notes="ATP, not live/dead. Percent not published for 0 mM RGDS.",
                ),
            ],
        }
    )
    rows.append(
        {
            "experiment_id": "salinas2007-peg-rgds-ctrl",
            "study_id": "salinas2007",
            "material_class": "PEG",
            "material_detail": "PEG mixed-mode thiol-ene + 5 mM RGDS",
            "crosslinking": "photocrosslink",
            "surface_chemistry": "RGD",
            "has_adhesion_ligand": 1.0,
            "cell_type": "MSC",
            "species": "human",
            "culture_model": "3D_encapsulation",
            "growth_factor": "none",
            "culture_time_days": 14,
            "extracted_from": "abstract",
            "curator_confidence": "high",
            "notes": "75% ATP viability in hMSC control medium, not chondrogenic medium.",
            "measurements": [
                _m(
                    "viability_pct",
                    75.0,
                    "%",
                    evidence="numeric_text",
                    notes="ATP-based viability in control cultures, not live/dead.",
                ),
            ],
        }
    )
    rows.append(
        {
            "experiment_id": "salinas2007-peg-rgds-chondro",
            "study_id": "salinas2007",
            "material_class": "PEG",
            "material_detail": "PEG + 5 mM RGDS, chondrogenic medium + 5 ng/mL TGF-β",
            "crosslinking": "photocrosslink",
            "surface_chemistry": "RGD",
            "has_adhesion_ligand": 1.0,
            "cell_type": "MSC",
            "species": "human",
            "culture_model": "3D_encapsulation",
            "growth_factor": "TGF_b1",
            "culture_time_days": 14,
            "extracted_from": "abstract",
            "curator_confidence": "medium",
            "notes": "Abstract: transforming growth factor beta, isoform not named. GAG twice 0 mM chondrogenic cultures. No viability percent for this arm.",
            "measurements": [
                _m(
                    "sgag_histology",
                    1.0,
                    "ordinal",
                    evidence="qualitative_text",
                    notes="Within-paper: 2× GAG vs 0 mM RGDS chondrogenic; 7× vs control.",
                ),
            ],
        }
    )

    # Mouser 2017 — pHPMA-lac-PEG ± HAMA, 14–31 kPa.
    for tag, hama, kpa, gag, extra in [
        ("hama0", 0.0, 14.0, 0.45, "HAMA-free. 14 kPa is the low end of the Young's range, which increased with HAMA."),
        ("hama05", 0.5, None, 1.0, "0.5% HAMA optimal for GAG and collagen II. Stiffness between 14 and 31 kPa, not interpolated."),
        ("hama1", 1.0, 31.0, 0.4, "1% HAMA increased fibrocartilage. 31 kPa is the high end of the Young's range."),
    ]:
        rows.append(
            {
                "experiment_id": f"mouser2017-phpma-{tag}-d28",
                "study_id": "mouser2017",
                "material_class": "PEG" if hama == 0 else "PEG_HA",
                "material_detail": f"pHPMA-lac-PEG triblock + {hama:g}% w/w HAMA",
                "crosslinking": "photocrosslink",
                "stiffness_kpa": kpa,
                "stiffness_method": None if kpa is None else "youngs_range_endpoint",
                "surface_chemistry": "native" if hama else "none",
                "has_adhesion_ligand": 1.0 if hama else 0.3,
                "cell_type": "articular_chondrocyte",
                "culture_model": "3D_encapsulation",
                "growth_factor": "none",
                "culture_time_days": 28,
                "extracted_from": "abstract",
                "curator_confidence": "medium",
                "notes": extra + " PCL co-print 3.5–4.6 MPa not stored as gel modulus.",
                "measurements": [
                    _m(
                        "sgag_histology",
                        gag,
                        "ordinal",
                        evidence="qualitative_text",
                        notes="Within-paper matrix ranking from HAMA dose, not µg.",
                    ),
                ],
            }
        )

    # Schneider 2017 — PEG 8 vs 46 kPa.
    for tag, kpa in [("soft", 8.0), ("stiff", 46.0)]:
        rows.append(
            {
                "experiment_id": f"schneider2017-peg-{tag}",
                "study_id": "schneider2017",
                "material_class": "PEG",
                "material_detail": f"Photoclickable PEG, compressive modulus {kpa:g} kPa",
                "crosslinking": "photocrosslink",
                "stiffness_kpa": kpa,
                "stiffness_method": "compressive_modulus",
                "surface_chemistry": "none",
                "has_adhesion_ligand": 0.0,
                "cell_type": "articular_chondrocyte",
                "species": "bovine",
                "culture_model": "3D_encapsulation",
                "growth_factor": "none",
                "extracted_from": "abstract",
                "curator_confidence": "high",
                "notes": "Secretome study. Free swelling vs loaded not split here. No live/dead percent.",
                "measurements": [
                    _m(
                        "sgag_histology",
                        0.7,
                        "ordinal",
                        evidence="qualitative_text",
                        notes="Cartilage ECM including aggrecan and collagens II/VI increased with time; no µg.",
                    ),
                ],
            }
        )

    # Wang 2014 — gelatin-HPA G′ series.
    for tag, gpa, gag, extra in [
        ("soft", 0.57, 0.45, "Low stiffness G′ = 570 Pa."),
        ("mid", 1.0, 1.0, "Medium G′ = 1000 Pa: highest sGAG and Col2/Col1."),
        ("stiff", 2.75, 0.4, "High stiffness G′ = 2750 Pa."),
    ]:
        rows.append(
            {
                "experiment_id": f"wang2014-gtnhpa-{tag}",
                "study_id": "wang2014",
                "material_class": "gelatin",
                "material_detail": f"Gelatin-hydroxyphenylpropionic acid, G′ {gpa} kPa",
                "crosslinking": "enzymatic",
                "stiffness_kpa": gpa,
                "stiffness_method": "rheology_G_prime",
                "surface_chemistry": "native",
                "has_adhesion_ligand": 1.0,
                "cell_type": "articular_chondrocyte",
                "culture_model": "3D_encapsulation",
                "growth_factor": "none",
                "extracted_from": "abstract",
                "curator_confidence": "high",
                "notes": extra + " G′ stored as kPa, not converted to Young's.",
                "measurements": [
                    _m(
                        "sgag_histology",
                        gag,
                        "ordinal",
                        evidence="qualitative_text",
                        notes="Within-paper sGAG ranking from hydrogel stiffness.",
                    ),
                ],
            }
        )

    # Xu 2013 — fibrin-collagen inkjet + PCL electrospin.
    rows.append(
        {
            "experiment_id": "xu2013-fibrin-col-pcl-d7",
            "study_id": "xu2013",
            "material_class": "fibrin",
            "material_detail": "Fibrin-collagen inkjet with alternating PCL electrospun fibers, 5-layer 1 mm construct",
            "crosslinking": "enzymatic",
            "surface_chemistry": "native",
            "has_adhesion_ligand": 1.0,
            "cell_type": "auricular_chondrocyte",
            "species": "rabbit",
            "culture_model": "3D_bioprint",
            "growth_factor": "none",
            "culture_time_days": 7,
            "extracted_from": "abstract",
            "curator_confidence": "medium",
            "notes": "Rabbit elastic chondrocytes. >80% viable one week after printing. PCL fiber mechanics not stored as gel stiffness.",
            "measurements": [
                _m(
                    "viability_pct",
                    None,
                    "%",
                    qualitative="floor_>80",
                    evidence="qualitative_text",
                    notes="Paper: more than 80% viability at 1 week; not a live/dead mean.",
                ),
            ],
        }
    )

    # Ye 2026 — GelMA + PLCL MEW, viability floor.
    rows.append(
        {
            "experiment_id": "ye2026-gelma-plcl500",
            "study_id": "ye2026",
            "material_class": "GelMA",
            "material_detail": "GelMA reinforced with melt-electrowritten PLCL, 500 µm pores",
            "crosslinking": "photocrosslink",
            "surface_chemistry": "native",
            "has_adhesion_ligand": 1.0,
            "cell_type": "articular_chondrocyte",
            "culture_model": "3D_encapsulation",
            "growth_factor": "none",
            "extracted_from": "abstract",
            "curator_confidence": "medium",
            "notes": "Viability remains above 90%. 72.6 MPa elastic modulus is the PLCL mesh. Composite 0.5 MPa tensile not stored as stiffness_kpa.",
            "measurements": [
                _m(
                    "viability_pct",
                    None,
                    "%",
                    qualitative="high_>90",
                    evidence="qualitative_text",
                ),
                _m(
                    "morphology_spherical",
                    1.0,
                    "ordinal",
                    evidence="qualitative_text",
                    notes="Chondrocytes maintained a spherical phenotype.",
                ),
            ],
        }
    )

    # Fathi 2020 — silk/PEGDMA modulus endpoints + PEG10-SF8 viability group.
    for tag, kpa, sd, extra in [
        ("soft", 95.70, 17.82, "Low end of the reported compressive-modulus range."),
        ("stiff", 338.05, 38.24, "High end of the reported compressive-modulus range."),
    ]:
        rows.append(
            {
                "experiment_id": f"fathi2020-sf-pegdma-{tag}",
                "study_id": "fathi2020",
                "material_class": "PEG_silk",
                "material_detail": "Silk fibroin 8% blended with PEGDMA (concentration varied)",
                "crosslinking": "photocrosslink",
                "stiffness_kpa": kpa,
                "stiffness_sd_kpa": sd,
                "stiffness_method": "compressive_modulus",
                "surface_chemistry": "native",
                "has_adhesion_ligand": 1.0,
                "cell_type": "MSC",
                "culture_model": "3D_encapsulation",
                "growth_factor": "TGF_b1",
                "extracted_from": "abstract",
                "curator_confidence": "medium",
                "notes": extra + " Dental pulp stem cells coded as MSC. Which PEGDMA/SF ratio produced each modulus is not in the abstract.",
                "measurements": [
                    _m(
                        "viability_pct",
                        None,
                        "%",
                        qualitative="not_reported_for_this_modulus",
                        evidence="qualitative_text",
                    ),
                ],
            }
        )
    rows.append(
        {
            "experiment_id": "fathi2020-peg10-sf8",
            "study_id": "fathi2020",
            "material_class": "PEG_silk",
            "material_detail": "PEGDMA 10%–silk fibroin 8% (1:1), dual bFGF + TGF-β1 PLGA nanoparticles",
            "crosslinking": "photocrosslink",
            "surface_chemistry": "native",
            "has_adhesion_ligand": 1.0,
            "cell_type": "MSC",
            "culture_model": "3D_encapsulation",
            "growth_factor": "TGF_b1",
            "extracted_from": "abstract",
            "curator_confidence": "medium",
            "notes": "Highest cell viability of the series; no percent. Dual GF increased DNA and GAG. Stiffness of this exact ratio not given.",
            "measurements": [
                _m(
                    "viability_pct",
                    None,
                    "%",
                    qualitative="highest_in_series",
                    evidence="qualitative_text",
                ),
            ],
        }
    )

    # Lin/Sun 2017 — PDLLA-PEG stiffness series, viability floor.
    for tag, kpa, extra in [
        ("150kpa", 150.0, "Low end of the Young's series studied (~150 kPa)."),
        ("1500kpa", 1500.0, "High end of the Young's series (~1500 kPa). The 1500–1800 kPa pair is the high-modulus PLLA-PEG / PDLLA-PEG 1000 materials."),
    ]:
        rows.append(
            {
                "experiment_id": f"lin2017-pdlla-peg-{tag}",
                "study_id": "lin2017",
                "material_class": "PEG",
                "material_detail": "Photocrosslinked PLLA-PEG / PDLLA-PEG 1000",
                "crosslinking": "photocrosslink",
                "stiffness_kpa": kpa,
                "stiffness_method": "youngs_series_endpoint",
                "surface_chemistry": "none",
                "has_adhesion_ligand": 0.0,
                "cell_type": "MSC",
                "species": "human",
                "culture_model": "3D_encapsulation",
                "growth_factor": "none",
                "extracted_from": "abstract",
                "curator_confidence": "medium",
                "notes": extra + " >80% viability post fabrication is a floor for the materials, not paired to each stiffness.",
                "measurements": [
                    _m(
                        "viability_pct",
                        None,
                        "%",
                        qualitative="floor_>80_post_fab",
                        evidence="qualitative_text",
                    ),
                ],
            }
        )

    # Galarraga 2021 — NorHA starting stiffness.
    for tag, kpa, extra in [
        ("soft", 2.0, "Loosely crosslinked NorHA. Abstract: enhanced cartilage formation vs denser gels."),
        ("mid", 6.0, "Low end of the denser crosslinking range ~6–60 kPa."),
        ("stiff", 60.0, "High end of the denser crosslinking range. Day-56 ~350 kPa is ECM and is not stored."),
    ]:
        rows.append(
            {
                "experiment_id": f"galarraga2021-norha-{tag}",
                "study_id": "galarraga2021",
                "material_class": "HA",
                "material_detail": f"Norbornene-modified hyaluronic acid, starting ~{kpa:g} kPa",
                "crosslinking": "photocrosslink",
                "stiffness_kpa": kpa,
                "stiffness_method": "compressive_modulus_approx",
                "surface_chemistry": "native",
                "has_adhesion_ligand": 1.0,
                "cell_type": "MSC",
                "culture_model": "3D_encapsulation",
                "growth_factor": "none",
                "extracted_from": "abstract",
                "curator_confidence": "medium",
                "notes": extra,
                "measurements": [
                    _m(
                        "sgag_histology",
                        1.0 if kpa == 2.0 else 0.35,
                        "ordinal",
                        evidence="qualitative_text",
                        notes="Soft gels supported more cartilage than densely crosslinked gels.",
                    ),
                ],
            }
        )

    # Smith Callahan 2013 — PEGDM G′ gradient endpoints.
    for tag, kpa, extra in [
        ("soft", 3.8, "Low-G′ end (~3800 Pa). Maintained cell number and CD14:CD90 phenotype; ECM ~200% higher."),
        ("stiff", 27.0, "High-G′ end (~27000 Pa). Cell number and chondrogenic phenotype declined above 13.1 kPa."),
    ]:
        rows.append(
            {
                "experiment_id": f"smith2013-pegdm-{tag}",
                "study_id": "smith2013",
                "material_class": "PEG",
                "material_detail": f"PEGDM + uniform RGD, G′ {kpa:g} kPa",
                "crosslinking": "photocrosslink",
                "stiffness_kpa": kpa,
                "stiffness_method": "rheology_G_prime",
                "surface_chemistry": "RGD",
                "has_adhesion_ligand": 1.0,
                "cell_type": "articular_chondrocyte",
                "species": "human",
                "culture_model": "3D_encapsulation",
                "growth_factor": "none",
                "culture_time_days": 21,
                "extracted_from": "abstract",
                "curator_confidence": "medium",
                "notes": extra + " Human osteoarthritic chondrocytes. G′ stored as kPa.",
                "measurements": [
                    _m(
                        "sgag_histology",
                        1.0 if kpa < 10 else 0.4,
                        "ordinal",
                        evidence="qualitative_text",
                        notes="Lower modulus: more ECM; not µg.",
                    ),
                ],
            }
        )
    return rows


def _queue_pass_four() -> list[dict]:
    """Fourth queue pass: published 3D hydrogel conditions; no invented live/dead means."""
    rows = []

    # Jooybar 2019 — HA-tyramine G′ endpoints ± platelet lysate.
    rows.append(
        {
            "experiment_id": "jooybar2019-hata-low-nopl",
            "study_id": "jooybar2019",
            "material_class": "HA",
            "material_detail": "HA-tyramine, HRP/H2O2, no platelet lysate",
            "crosslinking": "enzymatic",
            "stiffness_kpa": 0.5,
            "stiffness_method": "rheology_G_prime",
            "surface_chemistry": "native",
            "has_adhesion_ligand": 0.3,
            "cell_type": "MSC",
            "species": "human",
            "culture_model": "3D_encapsulation",
            "growth_factor": "none",
            "extracted_from": "abstract",
            "curator_confidence": "medium",
            "notes": "Low end of G′ 500–2000 Pa. Cells stayed round in pure HA-TA. G′ stored as kPa.",
            "measurements": [
                _m(
                    "morphology_spherical",
                    1.0,
                    "ordinal",
                    evidence="qualitative_text",
                    notes="Retained round shape without platelet lysate.",
                ),
            ],
        }
    )
    rows.append(
        {
            "experiment_id": "jooybar2019-hata-high-pl",
            "study_id": "jooybar2019",
            "material_class": "HA",
            "material_detail": "HA-tyramine enriched with platelet lysate",
            "crosslinking": "enzymatic",
            "stiffness_kpa": 2.0,
            "stiffness_method": "rheology_G_prime",
            "surface_chemistry": "native",
            "has_adhesion_ligand": 1.0,
            "cell_type": "MSC",
            "species": "human",
            "culture_model": "3D_encapsulation",
            "growth_factor": "none",
            "extracted_from": "abstract",
            "curator_confidence": "medium",
            "notes": "High end of G′ range. PL is a mixed GF source, not stored as TGF-β3. Cells attached and deposited COL2/proteoglycan.",
            "measurements": [
                _m(
                    "sgag_histology",
                    0.85,
                    "ordinal",
                    evidence="qualitative_text",
                    notes="Increasing collagen II and proteoglycan with PL; not µg.",
                ),
                _m(
                    "morphology_spherical",
                    0.2,
                    "ordinal",
                    evidence="qualitative_text",
                    notes="hMSCs attached and spread in PL-enriched matrix.",
                ),
            ],
        }
    )

    # Kudva 2018 — 6.5% PEG-VS ± RGD, G′ 1.2 kPa on the selected gel.
    rows.append(
        {
            "experiment_id": "kudva2018-peg65-rgd-hpdc",
            "study_id": "kudva2018",
            "material_class": "PEG",
            "material_detail": "6.5% 4-arm PEG-VS, GPQGIWGQ peptide cross-linker, RGD",
            "crosslinking": "chemical",
            "polymer_concentration_wt_pct": 6.5,
            "stiffness_kpa": 1.2,
            "stiffness_sd_kpa": 0.13,
            "stiffness_method": "rheology_G_prime",
            "surface_chemistry": "RGD",
            "has_adhesion_ligand": 1.0,
            "cell_type": "MSC",
            "species": "human",
            "culture_model": "3D_encapsulation",
            "growth_factor": "none",
            "extracted_from": "PMC6274881 results + methods",
            "curator_confidence": "high",
            "notes": "Selected composition. hPDC coded as MSC. Initial live/dead not less than 75% (floor, not stored as 75).",
            "measurements": [
                _m(
                    "viability_pct",
                    None,
                    "%",
                    qualitative="high_>75_initial",
                    evidence="qualitative_text",
                    notes="No composition displayed a viability percentage of less than 75% at the first time point.",
                ),
            ],
        }
    )
    rows.append(
        {
            "experiment_id": "kudva2018-peg65-norgd-hpdc-w4",
            "study_id": "kudva2018",
            "material_class": "PEG",
            "material_detail": "PEG-VS without RGD, growth medium, 4 weeks",
            "crosslinking": "chemical",
            "surface_chemistry": "none",
            "has_adhesion_ligand": 0.0,
            "cell_type": "MSC",
            "species": "human",
            "culture_model": "3D_encapsulation",
            "growth_factor": "none",
            "culture_time_days": 28,
            "extracted_from": "PMC6274881 Fig 1C text",
            "curator_confidence": "medium",
            "notes": "No-RGD gels dropped; paper says as low as approximately 50% across those compositions, not a single-gel mean.",
            "measurements": [
                _m(
                    "viability_pct",
                    None,
                    "%",
                    qualitative="drop_toward_50",
                    evidence="qualitative_text",
                ),
            ],
        }
    )
    rows.append(
        {
            "experiment_id": "kudva2018-peg65-rgd-atdc5",
            "study_id": "kudva2018",
            "material_class": "PEG",
            "material_detail": "6.5% PEG-VS + RGD, ATDC5 in chondrogenic medium",
            "crosslinking": "chemical",
            "polymer_concentration_wt_pct": 6.5,
            "stiffness_kpa": 1.2,
            "stiffness_sd_kpa": 0.13,
            "stiffness_method": "rheology_G_prime",
            "surface_chemistry": "RGD",
            "has_adhesion_ligand": 1.0,
            "cell_type": "ATDC5",
            "species": "murine",
            "culture_model": "3D_encapsulation",
            "growth_factor": "none",
            "extracted_from": "PMC6274881 ATDC5 paragraph",
            "curator_confidence": "medium",
            "notes": "ATDC5 ~75% or higher at week 0; no drop over 4 weeks. Floor, not a mean.",
            "measurements": [
                _m(
                    "viability_pct",
                    None,
                    "%",
                    qualitative="high_>75",
                    evidence="qualitative_text",
                ),
            ],
        }
    )

    # Choy 2017 — alginate concentration series, co-culture.
    for conc, gag, extra in [
        (1.0, 0.55, "Lowest alginate. Viability mid of the 66–72% band."),
        (1.2, 1.0, "Paper: relatively most effective for chondrocytic differentiation."),
        (1.5, 0.7, "Highest trypan-blue viability of the three; more cell clusters."),
    ]:
        rows.append(
            {
                "experiment_id": f"choy2017-alg-{str(conc).replace('.', 'p')}-d7",
                "study_id": "choy2017",
                "material_class": "alginate",
                "material_detail": f"{conc:g}% alginate, hADSC:nasal chondrocyte co-culture 2:1",
                "crosslinking": "ionic",
                "polymer_concentration_wt_pct": conc,
                "surface_chemistry": "native",
                "has_adhesion_ligand": 0.5,
                "cell_type": "adipose_MSC",
                "species": "human",
                "culture_model": "3D_encapsulation",
                "growth_factor": "none",
                "culture_time_days": 7,
                "extracted_from": "PMC5646124 results",
                "curator_confidence": "medium",
                "notes": extra + " Trypan blue 66–72% across groups; per-gel means only in Fig. 2, not stored.",
                "measurements": [
                    _m(
                        "viability_pct",
                        None,
                        "%",
                        qualitative="band_66_72",
                        evidence="qualitative_text",
                    ),
                    _m(
                        "sgag_histology",
                        gag,
                        "ordinal",
                        evidence="qualitative_text",
                        notes="Within-paper chondrogenesis ranking, not µg.",
                    ),
                    _m(
                        "morphology_spherical",
                        1.0,
                        "ordinal",
                        evidence="qualitative_text",
                    ),
                ],
            }
        )

    # Levato 2017 — GelMA, three cell types.
    for tag, cell, extra in [
        ("acpc", "cartilage_progenitor", "ACPCs outperformed chondrocytes in neo-cartilage; highest PRG4, lowest COL10."),
        ("msc", "MSC", "MSCs more hypertrophic (COL10) than ACPCs."),
        ("chondrocyte", "articular_chondrocyte", "Less neo-cartilage than ACPCs in the same GelMA."),
    ]:
        rows.append(
            {
                "experiment_id": f"levato2017-gelma-{tag}",
                "study_id": "levato2017",
                "material_class": "GelMA",
                "material_detail": "GelMA hydrogel / bioink",
                "crosslinking": "photocrosslink",
                "surface_chemistry": "native",
                "has_adhesion_ligand": 1.0,
                "cell_type": cell,
                "culture_model": "3D_encapsulation",
                "growth_factor": "none",
                "extracted_from": "abstract",
                "curator_confidence": "medium",
                "notes": extra + " Starting modulus not in the abstract.",
                "measurements": [
                    _m(
                        "sgag_histology",
                        1.0 if cell == "cartilage_progenitor" else (0.55 if cell == "MSC" else 0.4),
                        "ordinal",
                        evidence="qualitative_text",
                        notes="Within-paper neo-cartilage ranking.",
                    ),
                ],
            }
        )

    # Cigan 2016 — 2% agarose, seeding density.
    for dens, extra in [
        (15.0, "Low end of the 15–90 million/mL series."),
        (90.0, "High seeding density significantly increased nearly all measured properties."),
    ]:
        rows.append(
            {
                "experiment_id": f"cigan2016-agarose-2pct-{int(dens)}m",
                "study_id": "cigan2016",
                "material_class": "agarose",
                "material_detail": "2% agarose, expanded human chondrocytes from allografts",
                "crosslinking": "thermal",
                "polymer_concentration_wt_pct": 2.0,
                "surface_chemistry": "none",
                "has_adhesion_ligand": 0.0,
                "cell_type": "articular_chondrocyte",
                "species": "human",
                "culture_model": "3D_encapsulation",
                "growth_factor": "TGF_b3",
                "cell_density_million_per_ml": dens,
                "extracted_from": "abstract",
                "curator_confidence": "high",
                "notes": extra + " Construct Young's ~250 kPa is ECM-matured and is not stored.",
                "measurements": [
                    _m(
                        "sgag_histology",
                        0.45 if dens < 50 else 1.0,
                        "ordinal",
                        evidence="qualitative_text",
                        notes="High density reached 5.7% ww GAG; ranking only, not µg/µg.",
                    ),
                ],
            }
        )

    # Byers 2008 — agarose ± transient TGF-β3.
    rows.append(
        {
            "experiment_id": "byers2008-agarose-tgf-transient",
            "study_id": "byers2008",
            "material_class": "agarose",
            "material_detail": "Agarose, serum-free, TGF-β3 2.5–5 ng/mL for 2 weeks then withdrawn",
            "crosslinking": "thermal",
            "surface_chemistry": "none",
            "has_adhesion_ligand": 0.0,
            "cell_type": "articular_chondrocyte",
            "species": "bovine",
            "culture_model": "3D_encapsulation",
            "growth_factor": "TGF_b3",
            "culture_time_days": 14,
            "extracted_from": "abstract",
            "curator_confidence": "high",
            "notes": "Transient TGF-β3. Later 0.8 MPa / 6–7% ww GAG is ECM after <2 months, not starting gel stiffness.",
            "measurements": [
                _m(
                    "sgag_histology",
                    1.0,
                    "ordinal",
                    evidence="qualitative_text",
                    notes="Far superior maturation vs continuous TGF or serum + transient TGF.",
                ),
            ],
        }
    )
    rows.append(
        {
            "experiment_id": "byers2008-agarose-no-tgf",
            "study_id": "byers2008",
            "material_class": "agarose",
            "material_detail": "Agarose without the transient TGF-β3 protocol",
            "crosslinking": "thermal",
            "surface_chemistry": "none",
            "has_adhesion_ligand": 0.0,
            "cell_type": "articular_chondrocyte",
            "species": "bovine",
            "culture_model": "3D_encapsulation",
            "growth_factor": "none",
            "extracted_from": "abstract",
            "curator_confidence": "medium",
            "notes": "Comparator: continuous GF or serum-containing arms were inferior; this row is the no-transient protocol.",
            "measurements": [
                _m(
                    "sgag_histology",
                    0.35,
                    "ordinal",
                    evidence="qualitative_text",
                ),
            ],
        }
    )

    # Pahoff 2019 — GelMA/HAMA photoinitiator.
    for tag, xl, extra in [
        ("lap", "photocrosslink", "LAP + 405 nm. Dedifferentiation genes upregulated vs Irgacure."),
        ("irgacure", "photocrosslink", "Irgacure 2959 + 365 nm. Chondrogenic marker genes upregulated. Day-28 B-IC ~1.5 MPa is ECM, not stored."),
    ]:
        rows.append(
            {
                "experiment_id": f"pahoff2019-gelma-hama-{tag}",
                "study_id": "pahoff2019",
                "material_class": "GelMA_HA",
                "material_detail": f"GelMA/HAMA, {'LAP 405 nm' if tag == 'lap' else 'Irgacure 2959 365 nm'}, mPCL MEW reinforcement present in the paper",
                "crosslinking": xl,
                "surface_chemistry": "native",
                "has_adhesion_ligand": 1.0,
                "cell_type": "articular_chondrocyte",
                "species": "human",
                "culture_model": "3D_encapsulation",
                "growth_factor": "none",
                "culture_time_days": 1,
                "extracted_from": "abstract",
                "curator_confidence": "medium",
                "notes": extra + " Viability assayed at day 1 and 28; no percent in the abstract. Starting gel modulus not given.",
                "measurements": [
                    _m(
                        "viability_pct",
                        None,
                        "%",
                        qualitative="assayed_no_percent",
                        evidence="qualitative_text",
                    ),
                ],
            }
        )

    # Chawla 2012 — V vs Y saccharide-peptide.
    for tag, gag, extra in [
        ("valine", 0.4, "V-functionalized. Day-21 44±21 kPa is ECM-matured, not stored as gel stiffness."),
        ("tyrosine", 1.0, "Y-functionalized: higher GAG and collagen. Day-21 193±46 kPa is ECM-matured, not stored."),
    ]:
        rows.append(
            {
                "experiment_id": f"chawla2012-saccpep-{tag}-d21",
                "study_id": "chawla2012",
                "material_class": "saccharide_peptide",
                "material_detail": f"Saccharide-peptide copolymer hydrogel, {tag} amino-acid moiety",
                "crosslinking": "chemical",
                "surface_chemistry": "native",
                "has_adhesion_ligand": 0.5,
                "cell_type": "articular_chondrocyte",
                "culture_model": "3D_encapsulation",
                "growth_factor": "none",
                "culture_time_days": 21,
                "extracted_from": "abstract",
                "curator_confidence": "medium",
                "notes": extra + " Encapsulated chondrocytes remained viable 21 d.",
                "measurements": [
                    _m(
                        "viability_pct",
                        None,
                        "%",
                        qualitative="viable_21d",
                        evidence="qualitative_text",
                    ),
                    _m(
                        "sgag_histology",
                        gag,
                        "ordinal",
                        evidence="qualitative_text",
                    ),
                ],
            }
        )
    return rows


def _bmp_pass_experiments() -> list[dict]:
    """Open-fulltext conditions that a PI would open next to GelMA 25 kPa. Floors stay qualitative."""
    rows = []
    rows.append(
        {
            "experiment_id": "duchi2017-gelma-hama-coaxial-d1",
            "study_id": "duchi2017",
            "material_class": "GelMA_HA",
            "material_detail": "Core/shell GelMA/HAMA 10%/2% w/v, LAP 0.1% in the shell, 10 s 365 nm 700 mW/cm²",
            "crosslinking": "photocrosslink",
            "polymer_concentration_wt_pct": 12.0,
            "stiffness_kpa": 200.0,
            "stiffness_method": "unconfined_compression_core_shell",
            "surface_chemistry": "native",
            "has_adhesion_ligand": 1.0,
            "cell_type": "adipose_MSC",
            "species": "human",
            "culture_model": "3D_bioprint",
            "growth_factor": "none",
            "culture_time_days": 1,
            "extracted_from": "PMC5517463 abstract + results (200 kPa; >90% viable ADSC)",
            "curator_confidence": "high",
            "notes": "Infrapatellar ADSCs in the core (no PI). 200 kPa is the printed core/shell modulus, not native cartilage (MPa). >90% is a floor.",
            "measurements": [
                _m(
                    "viability_pct",
                    None,
                    "%",
                    qualitative="floor_>90",
                    evidence="qualitative_text",
                    notes="Abstract: containing >90% viable stem cells. Not stored as 90%.",
                ),
            ],
        }
    )
    rows.append(
        {
            "experiment_id": "duchi2017-gelma-hama-monoaxial-d7",
            "study_id": "duchi2017",
            "material_class": "GelMA_HA",
            "material_detail": "Mono-axial GelMA/HAMA 10%/2% (PI mixed with cells), same UV dose",
            "crosslinking": "photocrosslink",
            "polymer_concentration_wt_pct": 12.0,
            "surface_chemistry": "native",
            "has_adhesion_ligand": 1.0,
            "cell_type": "adipose_MSC",
            "species": "human",
            "culture_model": "3D_bioprint",
            "growth_factor": "none",
            "culture_time_days": 7,
            "extracted_from": "PMC5517463 results Fig. 3D",
            "curator_confidence": "medium",
            "notes": "Mono-axial (cells mixed with LAP) lost ~30% viability vs starting count. No live/dead mean. Contrast for the core/shell row.",
            "measurements": [
                _m(
                    "viability_pct",
                    None,
                    "%",
                    qualitative="declined_~30pp_vs_start",
                    evidence="qualitative_text",
                    notes="Paper: mono-axial viability decreased by 30% along with more dead cells. Relative drop, not a 70% mean.",
                ),
            ],
        }
    )
    return rows


def _chemistry_pass_experiments() -> list[dict]:
    """OA fulltext papers that add methacrylation / print architecture with numeric live/dead."""
    rows = []
    for gel, conc, kpa, d0, d7, detail in [
        ("GelMA", 14.0, 30.0, 77.0, 61.0, "14% GelMA, 15 s photocrosslink, printed"),
        ("GelMA_alginate", 16.0, 30.0, 72.0, 72.0, "14% GelMA + 2% oxidized methacrylated alginate, 15 s, printed"),
        ("GelMA", 16.0, 60.0, 54.0, 72.0, "16% GelMA, 15 s photocrosslink, printed"),
    ]:
        for day, val in ((0.0, d0), (7.0, d7)):
            rows.append(
                {
                    "experiment_id": f"martyniak2023-{gel.replace('_','')}-{int(conc)}wt-d{int(day)}",
                    "study_id": "martyniak2023",
                    "material_class": gel,
                    "material_detail": detail,
                    "crosslinking": "photocrosslink",
                    "polymer_concentration_wt_pct": conc,
                    "stiffness_kpa": kpa,
                    "stiffness_method": "storage_modulus_day0",
                    "surface_chemistry": "native",
                    "has_adhesion_ligand": 1.0,
                    "cell_type": "articular_chondrocyte",
                    "species": "human",
                    "culture_model": "3D_bioprint",
                    "growth_factor": "none",
                    "culture_time_days": day,
                    "cell_density_million_per_ml": 1.0,
                    "chemical_modification": "methacrylated" if gel == "GelMA" else "oxidized",
                    "architecture": "3d_printed",
                    "application": "bioprinting",
                    "live_dead_kit": "calcein_ethidium",
                    "extracted_from": "PMC10526043 results Fig. 8 text",
                    "curator_confidence": "high",
                    "notes": "Printed live/dead. OMA group held ~72% all 7 days (paper: around 72%).",
                    "measurements": [_m("viability_pct", val, "%", evidence="numeric_text", n=3)],
                }
            )
    for day, val, sd in ((1.0, 95.68, 0.71),):
        rows.append(
            {
                "experiment_id": "xie2022-gelma-dlp-d1",
                "study_id": "xie2022",
                "material_class": "GelMA",
                "material_detail": "DLP GelMA + microtia chondrocytes, no microtissue",
                "crosslinking": "photocrosslink",
                "surface_chemistry": "native",
                "has_adhesion_ligand": 1.0,
                "cell_type": "auricular_chondrocyte",
                "species": "human",
                "culture_model": "3D_bioprint",
                "growth_factor": "none",
                "culture_time_days": day,
                "chemical_modification": "methacrylated",
                "architecture": "3d_printed",
                "application": "auricular",
                "live_dead_kit": "calcein_ethidium",
                "extracted_from": "PMC11468467 Fig. 7D day 1",
                "curator_confidence": "high",
                "notes": "Control GelMA+chondrocytes 1 d post-print.",
                "measurements": [_m("viability_pct", val, "%", sd=sd, evidence="numeric_text")],
            }
        )
    for day, val, sd in ((1.0, 98.25, 0.43), (10.0, 95.96, 0.28), (20.0, 92.36, 1.91)):
        rows.append(
            {
                "experiment_id": f"xie2022-gelma-microtissue-d{int(day)}",
                "study_id": "xie2022",
                "material_class": "GelMA",
                "material_detail": "DLP GelMA + chondrocyte microtissues (microshelter)",
                "crosslinking": "photocrosslink",
                "surface_chemistry": "native",
                "has_adhesion_ligand": 1.0,
                "cell_type": "auricular_chondrocyte",
                "species": "human",
                "culture_model": "3D_bioprint",
                "growth_factor": "none",
                "culture_time_days": day,
                "chemical_modification": "methacrylated",
                "architecture": "microgel",
                "application": "auricular",
                "live_dead_kit": "calcein_ethidium",
                "extracted_from": "PMC11468467 Fig. 7D",
                "curator_confidence": "high",
                "notes": "Microtissue bioink; viability stayed >90% through day 20.",
                "measurements": [_m("viability_pct", val, "%", sd=sd, evidence="numeric_text")],
            }
        )
    return rows


def _queue_pass_five() -> list[dict]:
    """OA fulltext live/dead: NFC:A articular print, NCA nasoseptal print, MeHA MSC molds."""
    rows = []
    rows.append(
        {
            "experiment_id": "gatenholm2020-nfc-alg-preprint",
            "study_id": "gatenholm2020",
            "material_class": "cellulose_alginate",
            "material_detail": "80:20 NFC:A bioink, cells mixed, NC-200 before extrusion",
            "crosslinking": "ionic",
            "surface_chemistry": "native",
            "has_adhesion_ligand": 0.5,
            "cell_type": "articular_chondrocyte",
            "species": "human",
            "culture_model": "3D_encapsulation",
            "growth_factor": "none",
            "culture_time_days": 0,
            "cell_density_million_per_ml": 20.0,
            "passage": 1,
            "chemical_modification": "unmodified",
            "architecture": "bulk_hydrogel",
            "application": "bioprinting",
            "live_dead_kit": "NC-200",
            "extracted_from": "PMC8721610 Fig. 5A + results (before printing)",
            "curator_confidence": "high",
            "notes": "NC-200 before printing, not post-print d0 live/dead. 20e6/ml, P1 articular.",
            "measurements": [_m("viability_pct", 98.0, "%", evidence="numeric_text")],
        }
    )
    for day, val in ((3.0, 88.0), (5.0, 81.0), (7.0, 81.0), (14.0, 72.0)):
        rows.append(
            {
                "experiment_id": f"gatenholm2020-nfc-alg-d{int(day)}",
                "study_id": "gatenholm2020",
                "material_class": "cellulose_alginate",
                "material_detail": "80:20 NFC:A, INKREDIBLE, 410 µm nozzle, 100 mM CaCl2 5 min",
                "crosslinking": "ionic",
                "surface_chemistry": "native",
                "has_adhesion_ligand": 0.5,
                "cell_type": "articular_chondrocyte",
                "species": "human",
                "culture_model": "3D_bioprint",
                "growth_factor": "TGF_b3",
                "culture_time_days": day,
                "cell_density_million_per_ml": 20.0,
                "passage": 1,
                "chemical_modification": "unmodified",
                "architecture": "3d_printed",
                "application": "bioprinting",
                "live_dead_kit": "NC-200",
                "extracted_from": "PMC8721610 Fig. 5A + results text",
                "curator_confidence": "high",
                "notes": "Printed NC-200. Chondrogenic medium (TGF-β1 + TGF-β3) after 2 d recovery. d5 and d7 both 81% (ns). Printing pressure 5 kPa is not stored as modulus.",
                "measurements": [_m("viability_pct", val, "%", evidence="numeric_text")],
            }
        )
    rows.append(
        {
            "experiment_id": "jovic2026-nca-printed-1h",
            "study_id": "jovic2026",
            "material_class": "cellulose_alginate",
            "material_detail": "75:25 nanocellulose–alginate (NCA), 22G CELLINK INKREDIBLE, 30 kPa",
            "crosslinking": "ionic",
            "stiffness_kpa": 52.6,
            "stiffness_method": "elastic_modulus_prior_NCA_paper",
            "surface_chemistry": "native",
            "has_adhesion_ligand": 0.5,
            "cell_type": "nasal_chondrocyte",
            "species": "human",
            "culture_model": "3D_bioprint",
            "growth_factor": "none",
            "culture_time_days": 0,
            "cell_density_million_per_ml": 3.0,
            "chemical_modification": "unmodified",
            "architecture": "3d_printed",
            "application": "nasal",
            "live_dead_kit": "calcein_ethidium",
            "extracted_from": "PMC13117296 Fig. 3B printed 1 h (Day 0)",
            "curator_confidence": "high",
            "n_replicates": 3,
            "notes": "Nasoseptal chondrocytes, not articular/auricular. 81.9% immediately post-print. E=52.6 kPa cited from prior NCA characterization. 30 kPa is extrusion pressure, not Young's modulus.",
            "measurements": [_m("viability_pct", 81.9, "%", evidence="numeric_text", n=3)],
        }
    )
    rows.append(
        {
            "experiment_id": "jovic2026-nca-printed-24h",
            "study_id": "jovic2026",
            "material_class": "cellulose_alginate",
            "material_detail": "75:25 NCA, 22G INKREDIBLE, same print as 1 h row",
            "crosslinking": "ionic",
            "stiffness_kpa": 52.6,
            "stiffness_method": "elastic_modulus_prior_NCA_paper",
            "surface_chemistry": "native",
            "has_adhesion_ligand": 0.5,
            "cell_type": "nasal_chondrocyte",
            "species": "human",
            "culture_model": "3D_bioprint",
            "growth_factor": "none",
            "culture_time_days": 1,
            "cell_density_million_per_ml": 3.0,
            "chemical_modification": "unmodified",
            "architecture": "3d_printed",
            "application": "nasal",
            "live_dead_kit": "calcein_ethidium",
            "extracted_from": "PMC13117296 Fig. 3B printed 24 h (Day 1)",
            "curator_confidence": "high",
            "n_replicates": 3,
            "notes": "Printed 61% at 24 h; delayed death after shear, not immediate post-print drop. 30 kPa is extrusion pressure, not Young's modulus.",
            "measurements": [_m("viability_pct", 61.0, "%", evidence="numeric_text", n=3)],
        }
    )
    rows.append(
        {
            "experiment_id": "jovic2026-nca-unprinted-24h",
            "study_id": "jovic2026",
            "material_class": "cellulose_alginate",
            "material_detail": "75:25 NCA hemisphere, 1 mL syringe no nozzle (unprinted control)",
            "crosslinking": "ionic",
            "stiffness_kpa": 52.6,
            "stiffness_method": "elastic_modulus_prior_NCA_paper",
            "surface_chemistry": "native",
            "has_adhesion_ligand": 0.5,
            "cell_type": "nasal_chondrocyte",
            "species": "human",
            "culture_model": "3D_encapsulation",
            "growth_factor": "none",
            "culture_time_days": 1,
            "cell_density_million_per_ml": 3.0,
            "chemical_modification": "unmodified",
            "architecture": "bulk_hydrogel",
            "application": "nasal",
            "live_dead_kit": "calcein_ethidium",
            "extracted_from": "PMC13117296 Fig. 3B unprinted 24 h",
            "curator_confidence": "high",
            "n_replicates": 3,
            "notes": "Same NCA gel without extrusion shear (1 mL syringe, no nozzle). Unprinted 1 h percent is not in the text.",
            "measurements": [_m("viability_pct", 79.6, "%", evidence="numeric_text", n=3)],
        }
    )
    for day, val, sd in ((1.0, 73.6, 6.4), (21.0, 64.4, 12.2)):
        rows.append(
            {
                "experiment_id": f"poldervaart2017-meha-encap-d{int(day)}",
                "study_id": "poldervaart2017",
                "material_class": "HA",
                "material_detail": "MeHA 1–3% w/v + 0.1% Irgacure 2959, UV mold (not the printed 3% scaffolds)",
                "crosslinking": "photocrosslink",
                "surface_chemistry": "native",
                "has_adhesion_ligand": 0.5,
                "tissue": "bone",
                "cell_type": "MSC",
                "species": "human",
                "culture_model": "3D_encapsulation",
                "growth_factor": "none",
                "culture_time_days": day,
                "cell_density_million_per_ml": 2.0,
                "chemical_modification": "methacrylated",
                "architecture": "bulk_hydrogel",
                "application": "bone",
                "live_dead_kit": "calcein_ethidium",
                "modification_degree_pct": 6.3,
                "n_replicates": 3,
                "extracted_from": "PMC5460858 Fig. 3A average across MeHA concentrations",
                "curator_confidence": "medium",
                "notes": (
                    "Average MSC live/dead across 1–3% w/v; concentration not stored as a single mean. "
                    "1% gels disintegrated by d21 so that timepoint excludes 1%. "
                    "Per-% means only in the figure. Bone/osteogenicity protocol. "
                    "Table 1 E after UV is stored on separate acellular rows, not attached here."
                ),
                "measurements": [
                    _m("viability_pct", val, "%", sd=sd, evidence="numeric_text", n=3)
                ],
            }
        )
    # Table 1 DMA E after UV — acellular; do not pair with Fig 3 mixed live/dead.
    for conc, kpa, sd in ((1.0, 1.3, 0.1), (2.0, 6.3, 1.2), (2.5, 6.8, 1.2)):
        tag = f"{conc:g}".replace(".", "p")
        rows.append(
            {
                "experiment_id": f"poldervaart2017-meha-{tag}pct-E",
                "study_id": "poldervaart2017",
                "material_class": "HA",
                "material_detail": f"{conc:g}% w/v MeHA + 0.1% Irgacure 2959, DMA after UV",
                "crosslinking": "photocrosslink",
                "polymer_concentration_wt_pct": conc,
                "stiffness_kpa": kpa,
                "stiffness_sd_kpa": sd,
                "stiffness_method": "dma_elastic_modulus_after_UV",
                "surface_chemistry": "native",
                "has_adhesion_ligand": 0.5,
                "tissue": "bone",
                "cell_type": "MSC",
                "species": "human",
                "culture_model": "3D_encapsulation",
                "growth_factor": "none",
                "chemical_modification": "methacrylated",
                "architecture": "bulk_hydrogel",
                "application": "bone",
                "modification_degree_pct": 6.3,
                "n_replicates": 3,
                "extracted_from": "PMC5460858 Table 1 elastic modulus E after UV",
                "curator_confidence": "high",
                "notes": (
                    f"Acellular DMA E after UV, n=3. 3% E is 10.6±0.1 kPa in the same table, not stored here. "
                    "Not paired to Fig 3 mixed-concentration live/dead. 1% gels disintegrated in culture ~14 d."
                ),
                "measurements": [
                    _m(
                        "viability_pct",
                        None,
                        "%",
                        qualitative="unpaired_to_fig3_average",
                        evidence="qualitative_text",
                    )
                ],
            }
        )
    return rows


EXPERIMENTS: list[dict] = (
    _bachmann_experiments()
    + _other_experiments()
    + _queue_pass_experiments()
    + _queue_pass_more()
    + _queue_pass_three()
    + _queue_pass_four()
    + _bmp_pass_experiments()
    + _chemistry_pass_experiments()
    + _queue_pass_five()
)

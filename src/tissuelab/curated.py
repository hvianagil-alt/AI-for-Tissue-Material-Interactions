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


EXPERIMENTS: list[dict] = _bachmann_experiments() + _other_experiments() + _queue_pass_experiments()

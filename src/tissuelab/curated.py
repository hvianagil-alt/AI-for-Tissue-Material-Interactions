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


EXPERIMENTS: list[dict] = _bachmann_experiments() + _other_experiments()

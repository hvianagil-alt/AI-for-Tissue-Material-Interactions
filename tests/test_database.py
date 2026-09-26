from tissuelab.curated import EXPERIMENTS, STUDIES
from tissuelab.load_database import load
from tissuelab.paths import DB_PATH


def test_curated_ids_unique():
    assert len({s["study_id"] for s in STUDIES}) == len(STUDIES)
    ids = [e["experiment_id"] for e in EXPERIMENTS]
    assert len(ids) == len(set(ids))
    assert all(e["measurements"] for e in EXPERIMENTS)
    assert not any("porosity_pct" in e and e["porosity_pct"] is not None for e in EXPERIMENTS)


def test_no_fake_porosity():
    assert all("porosity_pct" not in e or e["porosity_pct"] is None for e in EXPERIMENTS)


def test_floors_are_not_training_labels():
    floors = [
        e for e in EXPERIMENTS
        if e["experiment_id"] in {"ingavle2012-cs-ipn-d42", "rouillard2011-alg-va086", "rouillard2011-alg-irg2959"}
    ]
    assert floors
    for exp in floors:
        for meas in exp["measurements"]:
            if meas["assay"] == "viability_pct":
                assert meas.get("value") is None
                assert meas.get("qualitative_label")


def test_hand_curated_replaces_auto_promoted():
    from tissuelab.ingest_literature import load_promoted
    from tissuelab.load_database import drop_hand_overlapped_promoted

    pmids = {str(s["pmid"]) for s in STUDIES if s.get("pmid")}
    studies, experiments = drop_hand_overlapped_promoted(*load_promoted())
    leftover = [
        s["study_id"]
        for s in studies
        if str(s["study_id"]).startswith("pmid") and str(s["study_id"])[4:] in pmids
    ]
    assert leftover == []
    leftover_exp = [
        e["study_id"]
        for e in experiments
        if str(e["study_id"]).startswith("pmid") and str(e["study_id"])[4:] in pmids
    ]
    assert leftover_exp == []
    require_pmid = {
        "paul2023", "perezdiaz2023", "ortega2024", "aitchison2024", "demori2025",
        "rojas2025", "levett2014", "sun2015", "zigon2019", "scalzone2019", "kessel2020",
        "hu2012", "markstedt2015", "lindborg2015", "yang2020", "snyder2014", "kim2015",
        "ingavle2012", "zignego2014", "maneechan2026", "lee2025", "rouillard2011",
        "nicodemus2011", "park2013", "salinas2007", "mouser2017", "schneider2017",
        "wang2014", "xu2013", "ye2026", "fathi2020", "lin2017", "galarraga2021",
        "smith2013", "jooybar2019", "kudva2018", "choy2017", "levato2017",
        "cigan2016", "byers2008", "pahoff2019", "chawla2012", "duchi2017",
        "martyniak2023", "xie2022",
        "gatenholm2020", "jovic2026", "poldervaart2017",
        "ziverec2026", "visscher2018", "mcmillan2025",
        "lan2022", "scalzone2022",
        "lan2021", "jovic2024", "hosseini2025", "boere2015",
        "ren2016", "zeng2023", "perriergroult2026",
        "setayeshmehr2021", "pei2023",
        "orabi2023", "pangjantuk2024", "kihara2026",
        "petta2024", "mckinney2019", "jodat2020",
        "kilian2020", "yin2023", "sarsenova2022",
        "garciaaponte2025", "chen2020",
        "gu2020", "carvalho2025", "yi2019",
        "liu2025", "akkineni2022", "lopezmarcial2022",
        "zielinska2023", "gvaramia2024", "galarraga2023", "weitkamp2023",
        "kudva2017", "diazpayno2022", "loveland2026",
        "windisch2023", "zhang2023pva",
        "fang2024",
    }
    assert all(s.get("pmid") for s in STUDIES if s["study_id"] in require_pmid)


def test_queue_pass_five_gold_is_numeric_and_honest():
    by_id = {e["experiment_id"]: e for e in EXPERIMENTS}
    pre = by_id["gatenholm2020-nfc-alg-preprint"]
    assert pre["measurements"][0]["value"] == 98.0
    assert "before printing" in pre["notes"].lower()
    assert by_id["gatenholm2020-nfc-alg-d5"]["measurements"][0]["value"] == 81.0
    printed = by_id["jovic2026-nca-printed-24h"]
    assert printed["cell_type"] == "nasal_chondrocyte"
    assert printed["measurements"][0]["value"] == 61.0
    assert printed["cell_density_million_per_ml"] == 3.0
    pold = by_id["poldervaart2017-meha-encap-d1"]
    assert pold["cell_type"] == "MSC"
    assert pold.get("polymer_concentration_wt_pct") is None
    assert pold.get("stiffness_kpa") is None
    assert pold["measurements"][0]["value"] == 73.6
    assert pold["application"] == "bone"
    e_row = by_id["poldervaart2017-meha-2pct-E"]
    assert e_row["stiffness_kpa"] == 6.3
    assert e_row["stiffness_sd_kpa"] == 1.2
    assert e_row["measurements"][0].get("value") is None


def test_queue_pass_six_gold_is_numeric_and_honest():
    by_id = {e["experiment_id"]: e for e in EXPERIMENTS}
    ziv = by_id["ziverec2026-alg-unmod-d7"]
    assert ziv["cell_type"] == "nasal_chondrocyte"
    assert ziv["measurements"][0]["value"] == 71.0
    thp = by_id["ziverec2026-alg-thp-d7"]
    assert thp["measurements"][0].get("value") is None
    vis = by_id["visscher2018-alg-bead-prolif-d21"]
    assert vis["cell_type"] == "auricular_chondrocyte"
    assert vis["measurements"][0]["value"] == 82.67
    assert vis.get("stiffness_kpa") is None
    mcm = by_id["mcmillan2025-gelma-d1"]
    assert mcm["measurements"][0]["value"] == 83.5
    assert mcm["species"] == "ferret"


def test_queue_pass_seven_gold_is_numeric_and_honest():
    by_id = {e["experiment_id"]: e for e in EXPERIMENTS}
    lan = by_id["lan2022-col-print-d1"]
    assert lan["cell_type"] == "nasal_chondrocyte"
    assert lan["measurements"][0]["value"] == 85.5
    assert lan["measurements"][0]["value_sd"] == 3.9
    assert lan.get("stiffness_kpa") is None
    assert lan["growth_factor"] == "none"
    assert by_id["lan2022-col-print-d21"]["measurements"][0]["value"] == 93.9
    ggma = by_id["scalzone2022-ggma-d1"]
    assert ggma["cell_type"] == "MSC"
    assert ggma["measurements"][0]["value"] == 98.0
    assert ggma.get("stiffness_kpa") is None
    mh = by_id["scalzone2022-ggma-mh-d3"]
    assert mh["measurements"][0]["value"] == 82.0
    assert mh["measurements"][0]["value_sd"] == 6.0
    assert "100−dead" in mh["notes"] or "100-dead" in mh["notes"]


def test_queue_pass_eight_gold_is_numeric_and_honest():
    by_id = {e["experiment_id"]: e for e in EXPERIMENTS}
    lan = by_id["lan2021-col-print-20g-d3"]
    assert lan["cell_type"] == "nasal_chondrocyte"
    assert lan["measurements"][0]["value"] == 95.0
    assert lan["growth_factor"] == "TGF_b3"
    assert lan.get("stiffness_kpa") is None
    assert by_id["lan2021-col-print-22g-d3"]["measurements"][0]["value"] == 81.0
    jov = by_id["jovic2024-nca-static-d1"]
    assert jov["cell_type"] == "nasal_chondrocyte"
    assert jov["culture_model"] == "3D_encapsulation"
    assert jov["measurements"][0]["value"] == 77.6
    assert jov["growth_factor"] == "none"
    assert by_id["jovic2024-nca-dynamic-d14"]["measurements"][0]["value"] == 94.0
    top = by_id["hosseini2025-nca-top-d1"]
    assert top["cell_type"] == "articular_chondrocyte"
    assert top["stiffness_kpa"] == 39.8
    assert top["measurements"][0]["value"] == 93.4
    assert by_id["hosseini2025-nca-bot-d1"]["stiffness_kpa"] == 60.6
    assert by_id["hosseini2025-nca-mid-d1"].get("stiffness_kpa") is None
    assert by_id["hosseini2025-nca-top-d28"].get("stiffness_kpa") is None
    ha = by_id["boere2015-pnc-ha-1p5h"]
    assert ha["species"] == "equine"
    assert ha["measurements"][0]["value"] == 90.0
    assert ha.get("stiffness_kpa") is None
    peg = by_id["boere2015-pnc-peg-1p5h"]
    assert peg["measurements"][0]["value"] == 43.0


def test_queue_pass_nine_neighborhood_gold_is_numeric_and_honest():
    by_id = {e["experiment_id"]: e for e in EXPERIMENTS}
    ren = by_id["ren2016-col2-print-d1"]
    assert ren["cell_type"] == "articular_chondrocyte"
    assert ren["species"] == "rabbit"
    assert ren["measurements"][0]["value"] == 93.0
    assert ren.get("stiffness_kpa") is None
    zeng = by_id["zeng2023-gelma-bnc-d1"]
    assert zeng["cell_type"] == "auricular_chondrocyte"
    assert zeng["stiffness_kpa"] == 49.94
    assert zeng["measurements"][0]["value"] == 96.81
    assert by_id["zeng2023-gelma-bnc-d7"].get("stiffness_kpa") is None
    fib = by_id["perriergroult2026-fibrin-nasal-d21"]
    assert fib["cell_type"] == "nasal_chondrocyte"
    assert fib["material_class"] == "fibrin"
    assert fib["growth_factor"] == "none"
    assert fib["measurements"][0]["value"] == 71.0
    assert "BIT" in fib["notes"]


def test_queue_pass_ten_gold_is_numeric_and_honest():
    by_id = {e["experiment_id"]: e for e in EXPERIMENTS}
    bulk = by_id["setayeshmehr2021-pva-nb-bulk-d1"]
    assert bulk["cell_type"] == "articular_chondrocyte"
    assert bulk["species"] == "mouse"
    assert bulk["measurements"][0]["value"] == 82.0
    assert bulk["stiffness_kpa"] == 21.43
    assert by_id["setayeshmehr2021-sdcm50-bulk-d1"]["measurements"][0]["value"] == 70.0
    assert by_id["setayeshmehr2021-sdcm50-bulk-d1"].get("stiffness_kpa") is None
    printed = by_id["setayeshmehr2021-sdcm50-print-d1"]
    assert printed["culture_model"] == "3D_bioprint"
    assert printed["measurements"][0]["value"] == 60.0
    assert printed.get("stiffness_kpa") is None
    pei = by_id["pei2023-gelma60-msc-d2"]
    assert pei["cell_type"] == "MSC"
    assert pei["species"] == "rabbit"
    assert pei["measurements"][0]["value"] == 81.2
    assert pei.get("stiffness_kpa") is None
    assert "95.5" in pei["notes"]


def test_queue_pass_eleven_gold_is_numeric_and_honest():
    by_id = {e["experiment_id"]: e for e in EXPERIMENTS}
    soft = by_id["orabi2023-alg-gel-4p8-p6-d21"]
    assert soft["cell_type"] == "MSC"
    assert soft["species"] == "human"
    assert soft["stiffness_kpa"] == 4.8
    assert soft["measurements"][0]["value"] == 63.0
    stiff = by_id["orabi2023-alg-gel-6p7-p4-d21"]
    assert stiff["stiffness_kpa"] == 6.7
    assert stiff["measurements"][0]["value"] == 77.6
    pang = by_id["pangjantuk2024-al-ha-d14"]
    assert pang["material_class"] == "alginate_HA"
    assert pang["measurements"][0]["value"] == 77.36
    assert pang.get("stiffness_kpa") is None
    hbss = by_id["kihara2026-mgl-mha-hbss-d21"]
    assert hbss["cell_type"] == "adipose_MSC"
    assert hbss["growth_factor"] == "none"
    assert hbss["measurements"][0]["value"] == 91.1
    assert hbss.get("stiffness_kpa") is None
    tgf = by_id["kihara2026-mgl-mha-tgf-d21"]
    assert tgf["growth_factor"] == "TGF_b3"
    assert tgf["measurements"][0]["value"] == 87.5
    petta = by_id["petta2024-ha-pegda-oa-d10"]
    assert petta["cell_type"] == "articular_chondrocyte"
    assert petta["measurements"][0]["value"] == 72.0
    assert petta.get("stiffness_kpa") is None
    mck = by_id["mckinney2019-alg-encap-d0"]
    assert mck["culture_time_days"] == 0.0
    assert mck["measurements"][0]["value"] == 96.0
    jodat = by_id["jodat2020-gelma-peg-print-d7"]
    assert jodat["material_class"] == "GelMA_PEG"
    assert jodat["stiffness_kpa"] == 20.3
    assert jodat["measurements"][0]["value"] == 95.0
    assert "orabi2023-alg-gel-4p8-p4-d21" in by_id
    assert "kihara2026-mgl-mha-prp-d21" not in by_id


def test_queue_pass_twelve_gold_is_numeric_and_honest():
    by_id = {e["experiment_id"]: e for e in EXPERIMENTS}
    iface = by_id["kilian2020-algmc-gel-cpc-d1"]
    assert iface["cell_type"] == "articular_chondrocyte"
    assert iface["species"] == "human"
    assert iface["culture_model"] == "3D_bioprint"
    assert iface["measurements"][0]["value"] == 46.5
    assert iface.get("stiffness_kpa") is None
    gel = by_id["kilian2020-algmc-gel-gel-d1"]
    assert gel["measurements"][0]["value"] == 53.8
    assert by_id["kilian2020-algmc-diff-d7"]["growth_factor"] == "TGF_b3"
    assert by_id["kilian2020-algmc-diff-d7"]["measurements"][0]["value"] == 48.0
    assert by_id["kilian2020-algmc-ctrl-d21"]["measurements"][0]["value"] == 45.0
    yin = by_id["yin2023-ga-ms-fresh-d1"]
    assert yin["material_class"] == "GelMA_alginate"
    assert yin["measurements"][0]["value"] == 89.4
    assert "yin2023-ga-ms-frozen-d1" not in by_id
    fib = by_id["sarsenova2022-hcf-sdmsc-d7"]
    assert fib["material_class"] == "fibrin"
    assert fib["growth_factor"] == "none"
    assert fib["measurements"][0]["value"] == 97.0
    low = by_id["garciaaponte2025-gelma-0p25e6-d0"]
    assert low["cell_type"] == "adipose_MSC"
    assert low["cell_density_million_per_ml"] == 0.25
    assert low["measurements"][0]["value"] == 68.5
    assert by_id["garciaaponte2025-gelma-2e6-d0"]["measurements"][0]["value"] == 84.7
    chen = by_id["chen2020-gel-bms-d1"]
    assert chen["species"] == "goat"
    assert chen["measurements"][0]["value"] == 86.0
    assert chen.get("stiffness_kpa") is None


def test_queue_pass_thirteen_gold_is_numeric_and_honest():
    by_id = {e["experiment_id"]: e for e in EXPERIMENTS}
    gu = by_id["gu2020-cana-print-d4"]
    assert gu["cell_type"] == "nasal_chondrocyte"
    assert gu["material_class"] == "agarose"
    assert gu["culture_model"] == "3D_bioprint"
    assert gu["measurements"][0]["value"] == 71.0
    assert gu.get("stiffness_kpa") is None
    assert by_id["gu2020-cana-print-d0"]["measurements"][0]["value"] == 83.0
    atdc = by_id["carvalho2025-cmc-nfc-atdc5-d1"]
    assert atdc["cell_type"] == "ATDC5"
    assert atdc["material_class"] == "cellulose"
    assert atdc["measurements"][0]["value"] == 81.0
    yi = by_id["yi2019-alg-hasc-d4"]
    assert yi["cell_type"] == "adipose_MSC"
    assert yi["measurements"][0]["value"] == 89.9
    assert yi.get("stiffness_kpa") is None


def test_queue_pass_fourteen_gold_is_numeric_and_honest():
    by_id = {e["experiment_id"]: e for e in EXPERIMENTS}
    algmc = by_id["liu2025-algmc-hMSC-d1"]
    assert algmc["cell_type"] == "MSC"
    assert algmc["culture_model"] == "3D_bioprint"
    assert algmc["measurements"][0]["value"] == 52.7
    assert algmc["stiffness_kpa"] == 62.3
    assert by_id["liu2025-ewp-hMSC-d1"]["measurements"][0]["value"] == 79.8
    assert "liu2025-nhdf" not in "".join(by_id)
    gg = by_id["akkineni2022-gg-330-d14"]
    assert gg["material_class"] == "gellan"
    assert gg["measurements"][0]["value"] == 68.82
    assert gg["stiffness_kpa"] == 55.02
    assert by_id["akkineni2022-gg-331-d14"]["measurements"][0]["value"] == 64.91
    assert by_id["akkineni2022-gg-331-d14"].get("stiffness_kpa") is None
    ctl = by_id["lopezmarcial2022-agarose-ctl-d21"]
    assert ctl["cell_type"] == "articular_chondrocyte"
    assert ctl["growth_factor"] == "TGF_b3"
    assert ctl["measurements"][0]["value"] == 75.8
    assert ctl["stiffness_kpa"] == 14.4
    assert "lopezmarcial2022-agarose-hicoll" not in by_id
    hatg = by_id["zielinska2023-hatg-haur-d1"]
    assert hatg["cell_type"] == "auricular_chondrocyte"
    assert hatg["measurements"][0]["value"] == 76.3
    assert hatg["stiffness_kpa"] == 2.0
    rab = by_id["gvaramia2024-hatg-raur-d1"]
    assert rab["species"] == "rabbit"
    assert rab["measurements"][0]["value"] == 75.0
    assert rab["stiffness_kpa"] == 9.0
    nor = by_id["galarraga2023-norha-pmsc-d7"]
    assert nor["species"] == "porcine"
    assert nor["measurements"][0]["value"] == 79.4
    assert nor.get("stiffness_kpa") is None
    inj = by_id["weitkamp2023-novocart-inject-d1"]
    assert inj["measurements"][0]["value"] == 93.0
    assert inj["stiffness_kpa"] == 2.77
    assert "weitkamp2023-novocart-3d" not in by_id


def test_queue_pass_fifteen_gold_is_numeric_and_honest():
    by_id = {e["experiment_id"]: e for e in EXPERIMENTS}
    peg = by_id["kudva2017-pegvs-hac-d7"]
    assert peg["cell_type"] == "articular_chondrocyte"
    assert peg["material_class"] == "PEG"
    assert peg["growth_factor"] == "TGF_b1"
    assert peg["measurements"][0]["value"] == 75.0
    assert peg.get("stiffness_kpa") is None
    assert by_id["kudva2017-pegvs-hac-d28"]["measurements"][0]["value"] == 70.0
    ahat = by_id["diazpayno2022-ahat-hmsc-d14"]
    assert ahat["material_class"] == "alginate_HA"
    assert ahat["culture_model"] == "3D_bioprint"
    assert ahat["measurements"][0]["value"] == 75.0
    assert ahat["stiffness_kpa"] == 6.7
    asg = by_id["loveland2026-asg-fast-hmsc-d7"]
    assert asg["cell_type"] == "MSC"
    assert asg["measurements"][0]["value"] == 60.0
    assert asg.get("stiffness_kpa") is None
    assert asg["growth_factor"] == "none"
    assert "loveland2026-asg-fast-blebb" not in by_id


def test_queue_pass_sixteen_gold_is_numeric_and_honest():
    by_id = {e["experiment_id"]: e for e in EXPERIMENTS}
    w = by_id["windisch2023-pbs-algmc-hmsc-d1"]
    assert w["cell_type"] == "MSC"
    assert w["material_class"] == "alginate"
    assert w["culture_model"] == "3D_bioprint"
    assert w["measurements"][0]["value"] == 60.0
    assert w.get("stiffness_kpa") is None
    assert w["growth_factor"] == "none"
    assert "windisch2023-plasma" not in by_id
    assert "windisch2023-saos" not in by_id
    z1 = by_id["zhang2023pva-algpba-pva-mchond-d1"]
    assert z1["cell_type"] == "articular_chondrocyte"
    assert z1["species"] == "mouse"
    assert z1["material_class"] == "alginate"
    assert z1["measurements"][0]["value"] == 83.0
    assert z1.get("stiffness_kpa") is None
    z7 = by_id["zhang2023pva-algpba-pva-mchond-d7"]
    assert z7["measurements"][0]["value"] == 80.0
    assert "zhang2023pva-l929" not in by_id


def test_queue_pass_seventeen_gold_is_numeric_and_honest():
    by_id = {e["experiment_id"]: e for e in EXPERIMENTS}
    g5 = by_id["fang2024-gelma-5pct-bms-d1"]
    assert g5["cell_type"] == "MSC"
    assert g5["material_class"] == "GelMA"
    assert g5["polymer_concentration_wt_pct"] == 5.0
    assert g5["measurements"][0]["value"] == 83.6
    assert g5.get("stiffness_kpa") is None
    assert g5.get("cell_density_million_per_ml") is None
    g10 = by_id["fang2024-gelma-10pct-bms-d1"]
    assert g10["measurements"][0]["value"] == 74.8
    assert g10["culture_model"] == "3D_encapsulation"
    assert by_id["fang2024-gelma-10pct-bms-d4"]["measurements"][0]["value"] == 87.7
    assert "fang2024-gelma-5pct-bms-d4" not in by_id
    assert "fang2024-ncg-cck8" not in by_id


def test_curated_viability_excludes_auto_promote():
    from tissuelab.db import connect

    report = load(DB_PATH)
    assert report["n_hand_studies"] >= 40
    assert report["n_numeric_viability"] >= 20
    assert report.get("n_hand_viability_studies", 0) >= 15
    assert report["n_experiments"] >= 40
    assert report["percent_missing"]["porosity_pct"] == 100.0
    assert report["n_with_stiffness_kpa"] >= 20
    assert report["n_numeric_viability"] < report["n_experiments"]
    conn = connect(DB_PATH)
    auto_in_view = conn.execute(
        "SELECT COUNT(*) FROM v_model_viability WHERE study_id LIKE 'pmid%'"
    ).fetchone()[0]
    conn.close()
    assert auto_in_view == 0

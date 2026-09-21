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
        "cigan2016", "byers2008", "pahoff2019", "chawla2012",
    }
    assert all(s.get("pmid") for s in STUDIES if s["study_id"] in require_pmid)


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

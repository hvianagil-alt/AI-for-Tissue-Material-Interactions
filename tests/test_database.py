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


def test_database_quality_gates():
    report = load(DB_PATH)
    assert report["n_studies"] >= 8
    assert report["n_experiments"] >= 40
    assert report["n_numeric_viability"] >= 10
    assert report["percent_missing"]["porosity_pct"] == 100.0
    assert report["n_with_stiffness_kpa"] >= 20
    # Honesty: most rows still lack a live/dead percent.
    assert report["n_numeric_viability"] < report["n_experiments"]

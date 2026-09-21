from tissuelab.benchmark import leave_one_paper_out
from tissuelab.rank_papers import is_review, normalize_doi, score_paper


def test_doi_normalize():
    assert normalize_doi("https://doi.org/10.3389/fbioe.2020.00373") == "10.3389/fbioe.2020.00373"


def test_review_flag():
    assert is_review(["Review", "Journal Article"]) is True
    assert is_review(["Journal Article"]) is False


def test_score_prefers_quantitative_chondrocyte_gels():
    high, reasons, mvp = score_paper(
        is_rev=False,
        already_curated=False,
        cells={"articular_chondrocyte"},
        materials={"GelMA"},
        has_scaffold=True,
        has_cartilage=True,
        has_viability_number=True,
        has_stiffness_number=True,
        has_fulltext=True,
        citation_count=120,
        has_culture_days=True,
        has_tgf=True,
    )
    low, _, mvp_low = score_paper(
        is_rev=True,
        already_curated=False,
        cells=set(),
        materials=set(),
        has_scaffold=True,
        has_cartilage=False,
        has_viability_number=False,
        has_stiffness_number=False,
        has_fulltext=False,
        citation_count=3,
        has_culture_days=False,
        has_tgf=False,
    )
    assert mvp is True
    assert mvp_low is False
    assert high > low
    assert "abstract_viability_%" in reasons


def test_lopo_too_few_studies():
    import pandas as pd

    frame = pd.DataFrame(
        {
            "study_id": ["a", "a"],
            "viability_pct": [90.0, 88.0],
            "stiffness_kpa": [10.0, 20.0],
            "polymer_concentration_wt_pct": [5.0, 5.0],
            "culture_time_days": [7.0, 7.0],
            "material_class": ["GelMA", "GelMA"],
            "cell_type": ["articular_chondrocyte", "articular_chondrocyte"],
        }
    )
    report = leave_one_paper_out(frame)
    assert report["status"] == "too_few_studies"


def test_material_mean_lopo_beats_dummy_when_materials_differ():
    import pandas as pd
    from tissuelab.benchmark import leave_one_paper_out

    rows = []
    for i, (study, material, value) in enumerate(
        [
            ("s1", "GelMA", 90.0),
            ("s1", "GelMA", 88.0),
            ("s2", "GelMA", 92.0),
            ("s2", "alginate", 40.0),
            ("s3", "alginate", 42.0),
            ("s3", "alginate", 38.0),
            ("s4", "GelMA", 91.0),
            ("s4", "alginate", 41.0),
        ]
    ):
        rows.append(
            {
                "study_id": study,
                "viability_pct": value,
                "stiffness_kpa": 20.0,
                "polymer_concentration_wt_pct": 8.0,
                "culture_time_days": 14.0,
                "material_class": material,
                "cell_type": "articular_chondrocyte",
                "experiment_id": f"e{i}",
            }
        )
    report = leave_one_paper_out(pd.DataFrame(rows))
    assert report["material_mean_lopo"]["mae"] < report["dummy_lopo"]["mae"]
    assert report["deployed_estimator"] == "material_mean"
    assert report["beats_dummy"] is True
    assert "ridge_lopo" in report

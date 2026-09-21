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

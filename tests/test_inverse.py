from tissuelab.build_dataset import build_dataset
from tissuelab.inverse import inverse_design
from tissuelab.models import train_tissue_model
from tissuelab.protocol import protocol_from_row
from tissuelab.recommend import recommend_experiments


def _small_model():
    frame = build_dataset(n_simulated=180, seed=3)
    return train_tissue_model(frame)


def test_inverse_design_returns_ranked_candidates():
    model = _small_model()
    ranked = inverse_design(
        model,
        targets={
            "viability_pct": 90,
            "proliferation_score": 50,
            "differentiation_score": 80,
            "ecm_deposition_score": 80,
        },
        constraints={"material_class": ["fibrin", "GelMA", "HA"], "stiffness_kpa_max": 60},
        n_candidates=400,
        top_k=5,
        seed=4,
    )
    assert len(ranked) == 5
    assert ranked["match_score"].is_monotonic_decreasing
    assert ranked["material_class"].isin(["fibrin", "GelMA", "HA"]).all()
    assert "Encapsulate" in protocol_from_row(ranked.iloc[0])


def test_recommend_experiments_has_acquisition():
    model = _small_model()
    recs = recommend_experiments(model, objective="ecm_deposition_score", n=4, n_candidates=300, seed=5)
    assert len(recs) == 4
    assert recs["acquisition"].is_monotonic_decreasing
    assert recs["culture_model"].ne("2D").all()

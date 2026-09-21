"""Knob-response and LOPO checks for the shrinkage estimator."""

from tissuelab.literature_model import predict_literature_viability
from tissuelab.shrinkage import shrinkage_estimate


def _q(**kwargs):
    base = {
        "material_class": "fibrin",
        "stiffness_kpa": 25.0,
        "cell_type": "articular_chondrocyte",
        "growth_factor": "none",
        "culture_time_days": 14,
    }
    base.update(kwargs)
    return base


def test_knobs_move_prediction_in_a_loop():
    base = predict_literature_viability(_q())
    assert base["mean"] is not None
    seen = {base["mean"]}
    for kpa in (2.0, 10.0, 40.0, 80.0):
        seen.add(predict_literature_viability(_q(stiffness_kpa=kpa))["mean"])
    assert len(seen) >= 3

    gf_none = predict_literature_viability(_q(growth_factor="none"))["mean"]
    gf_tgf = predict_literature_viability(_q(growth_factor="TGF_b3"))["mean"]
    assert gf_none != gf_tgf

    day7 = predict_literature_viability(_q(culture_time_days=7))["mean"]
    day28 = predict_literature_viability(_q(culture_time_days=28))["mean"]
    assert day7 != day28

    chitosan = predict_literature_viability(_q(material_class="chitosan"))["mean"]
    assert abs(chitosan - base["mean"]) > 3

    msc = predict_literature_viability(_q(cell_type="MSC"))["mean"]
    assert msc != base["mean"] or base["knob_deltas"]


def test_soft_gel_is_not_identical_to_stiff_gel():
    soft = predict_literature_viability(_q(stiffness_kpa=2.0))
    stiff = predict_literature_viability(_q(stiffness_kpa=50.0))
    assert soft["mean"] != stiff["mean"]
    soft_ids = [row["experiment_id"] for row in soft["similar"]]
    stiff_ids = [row["experiment_id"] for row in stiff["similar"]]
    assert soft_ids != stiff_ids or [row["match_score"] for row in soft["similar"]] != [
        row["match_score"] for row in stiff["similar"]
    ]


def test_shrinkage_falls_back_on_empty_frame():
    import pandas as pd

    out = shrinkage_estimate({"material_class": "GelMA"}, pd.DataFrame())
    assert out["mean"] is None
    assert out["estimator"] == "empty"

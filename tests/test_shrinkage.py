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


def test_gelma_print_numbers_exist_fibrin_still_cleaner():
    gelma = predict_literature_viability(_q(material_class="GelMA"))
    fibrin = predict_literature_viability(_q(material_class="fibrin"))
    assert gelma["n_eff_same"] >= 2
    assert fibrin["n_eff_same"] >= 2
    assert fibrin["mean"] > gelma["mean"]
    assert gelma["trust"]["level"] in {"weak", "heterogeneous", "useful"}
    assert gelma["coverage"]["n_table_material"] >= 4
    assert gelma["also_extracted"]
    assert any(a["id"] == "competitor" for a in gelma["alternatives"])
    assert gelma["interval_floor_is_lopo_mae"] is True
    stiff = next(d for d in gelma["knob_deltas"] if d.get("key") == "stiffness_kpa")
    assert stiff["n_observed"] >= 1


def test_unmatched_chemistry_is_not_penalized():
    import pandas as pd
    from tissuelab.shrinkage import kernel_weights

    train = pd.DataFrame(
        {
            "material_class": ["GelMA", "GelMA"],
            "cell_type": ["articular_chondrocyte", "articular_chondrocyte"],
            "growth_factor": ["none", "none"],
            "stiffness_kpa": [25.0, 25.0],
            "culture_time_days": [14.0, 14.0],
            "chemical_modification": ["methacrylated", "unmodified"],
            "viability_pct": [80.0, 80.0],
        }
    )
    matched = kernel_weights(
        {
            "material_class": "GelMA",
            "cell_type": "articular_chondrocyte",
            "chemical_modification": "methacrylated",
        },
        train,
    )
    assert matched[0] > matched[1]
    plain = kernel_weights(
        {"material_class": "GelMA", "cell_type": "articular_chondrocyte"},
        train,
    )
    assert abs(plain[0] - plain[1]) < 1e-9


def test_shrinkage_falls_back_on_empty_frame():
    import pandas as pd

    out = shrinkage_estimate({"material_class": "GelMA"}, pd.DataFrame())
    assert out["mean"] is None
    assert out["estimator"] == "empty"

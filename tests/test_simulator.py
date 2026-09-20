from tissuelab.simulator import simulate_dataframe, simulate_outcomes, sample_designs
import numpy as np


def test_simulator_outputs_in_range():
    frame = simulate_dataframe(n=80, seed=1)
    assert len(frame) == 80
    for column in ["viability_pct", "proliferation_score", "differentiation_score", "ecm_deposition_score"]:
        assert frame[column].between(0, 100).all()
    assert set(frame["source"].unique()) == {"simulated_literature_informed"}


def test_stiffer_fibrin_beats_soft_on_ecm():
    rng = np.random.default_rng(0)
    base = sample_designs(1, rng).iloc[0].to_dict()
    base.update(
        {
            "material_class": "fibrin",
            "growth_factor": "TGF_b3",
            "culture_model": "3D_encapsulation",
            "has_adhesion_ligand": 1.0,
            "porosity_pct": 82,
            "degradation_half_life_days": 14,
            "culture_time_days": 21,
            "passage": 2,
            "cell_type": "articular_chondrocyte",
        }
    )
    soft = dict(base, stiffness_kpa=1.0)
    stiff = dict(base, stiffness_kpa=30.0)
    # Mean over several noise draws
    soft_ecm = np.mean([simulate_outcomes(soft, np.random.default_rng(i))["ecm_deposition_score"] for i in range(20)])
    stiff_ecm = np.mean([simulate_outcomes(stiff, np.random.default_rng(i))["ecm_deposition_score"] for i in range(20)])
    assert stiff_ecm > soft_ecm


def test_peg_dextran_high_stiffness_kills_viability():
    rng = np.random.default_rng(2)
    row = sample_designs(1, rng).iloc[0].to_dict()
    row.update(
        {
            "material_class": "PEG_dextran",
            "stiffness_kpa": 30,
            "has_adhesion_ligand": 0.0,
            "surface_chemistry": "none",
            "porosity_pct": 45,
        }
    )
    out = simulate_outcomes(row, np.random.default_rng(3))
    assert out["viability_pct"] < 50

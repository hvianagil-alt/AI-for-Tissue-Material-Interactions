from tissuelab.literature_model import _material_mean_estimate, _notes, predict_literature_viability, similar_published


def test_notes_warn_when_dummy_wins():
    notes = _notes({"beats_dummy": False, "mvp_pass": False, "deployed_estimator": "dummy"})
    assert any("dummy" in note.lower() for note in notes)


def test_notes_mvp_pass():
    notes = _notes({"beats_dummy": True, "mvp_pass": True, "deployed_estimator": "material_mean"})
    assert any("meets the viability MVP bar" in note for note in notes)


def test_notes_barely_beats_dummy():
    notes = _notes({"beats_dummy": True, "mvp_pass": False, "deployed_estimator": "material_mean"})
    assert any("dummy" in note.lower() for note in notes)
    assert any("MVP" in note for note in notes)


def test_material_mean_estimate_falls_back():
    import pandas as pd

    frame = pd.DataFrame(
        {
            "material_class": ["GelMA", "GelMA", "alginate"],
            "viability_pct": [80.0, 90.0, 50.0],
        }
    )
    mean, source, n = _material_mean_estimate({"material_class": "GelMA"}, frame)
    assert source == "material_mean"
    assert n == 2
    assert mean == 85.0
    mean, source, n = _material_mean_estimate({"material_class": "PEG"}, frame)
    assert source == "global_mean"
    assert n == 3
    assert abs(mean - (80 + 90 + 50) / 3) < 1e-9


def test_similar_published_returns_hand_rows_only():
    from tissuelab.load_database import load
    from tissuelab.paths import DB_PATH

    load(DB_PATH)
    rows = similar_published(
        {"material_class": "GelMA", "stiffness_kpa": 25.0, "cell_type": "articular_chondrocyte"},
        k=5,
    )
    assert rows
    assert all(not str(row["study_id"]).startswith("pmid") for row in rows)
    assert all("viability_pct" in row for row in rows)


def test_predict_gelma_uses_shrinkage_and_beats_dummy():
    from tissuelab.literature_model import load_curated_viability
    from tissuelab.load_database import load
    from tissuelab.paths import DB_PATH

    load(DB_PATH)
    frame = load_curated_viability()
    gelma = frame.loc[frame["material_class"] == "GelMA", "viability_pct"].astype(float)
    out = predict_literature_viability(
        {
            "material_class": "GelMA",
            "stiffness_kpa": 25.0,
            "cell_type": "articular_chondrocyte",
            "growth_factor": "none",
            "culture_time_days": 14,
        }
    )
    assert out["mean"] is not None
    assert 55 <= out["mean"] <= 95
    assert out["estimator"] in {"shrinkage", "shrinkage_global_prior"}
    assert out["n_support"] == int(len(gelma))
    assert out["similar"]
    lopo = out["lopo"]
    assert lopo["deployed_estimator"] == "shrinkage"
    assert lopo["ridge_beats_dummy"] is False
    assert lopo["mvp_pass"] is False
    assert lopo["ridge_mae"] > lopo["dummy_mae"]

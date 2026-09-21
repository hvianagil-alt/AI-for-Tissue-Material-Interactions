from tissuelab.literature_model import _notes, similar_published


def test_notes_warn_when_dummy_wins():
    notes = _notes({"beats_dummy": False, "mvp_pass": False})
    assert any("dummy" in note.lower() for note in notes)


def test_notes_mvp_pass():
    notes = _notes({"beats_dummy": True, "mvp_pass": True})
    assert any("meets the viability MVP bar" in note for note in notes)


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

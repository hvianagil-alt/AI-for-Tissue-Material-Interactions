import pandas as pd

from tissuelab.load_database import load
from tissuelab.training_pack import export_pack


def test_training_pack_gold_has_no_pmid_rows(tmp_path):
    db = tmp_path / "t.sqlite"
    load(db)
    report = export_pack(db, out_dir=tmp_path)
    assert report["n_gold_rows"] >= 40
    assert report["n_gold_studies"] >= 15
    frame = pd.read_csv(report["gold"])
    assert "split_group" in frame.columns
    assert {"material_class", "cell_type", "chemical_modification", "architecture", "application"} <= set(frame.columns)
    assert frame["label_source"].eq("hand_curated").all()
    assert not frame["study_id"].astype(str).str.startswith("pmid").any()
    assert frame["viability_pct"].between(0, 100).all()
    assert frame["split_group"].eq(frame["study_id"]).all()

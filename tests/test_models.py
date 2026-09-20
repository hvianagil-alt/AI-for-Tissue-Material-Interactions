from tissuelab.build_dataset import build_dataset
from tissuelab.models import evaluate_baselines, train_tissue_model
from tissuelab.schema import TARGETS


def test_xgboost_beats_dummy_on_simulated_data():
    frame = build_dataset(n_simulated=220, seed=0)
    report = evaluate_baselines(frame, seed=0)
    dummy = report["dummy_mean"]["overall"]["mae"]
    boosted = report["xgboost"]["overall"]["mae"]
    forest = report["random_forest"]["overall"]["mae"]
    assert boosted < dummy * 0.65
    assert forest < dummy * 0.75


def test_trained_model_returns_intervals():
    frame = build_dataset(n_simulated=160, seed=1)
    model = train_tissue_model(frame)
    pred = model.predict_frame(frame.head(8))
    for target in TARGETS:
        assert (pred[f"{target}_low"] <= pred[target] + 1e-6).all()
        assert (pred[target] <= pred[f"{target}_high"] + 1e-6).all()

from tissuelab.teach_model import data_budget, predict_one_gel, run_lesson


def test_teach_model_runs_on_real_table():
    report = run_lesson(verbose=False)
    assert report["n_studies"] >= 15
    assert report["n_rows"] >= 40
    assert report["dummy_lopo"]["mae"] > 0
    assert report["ridge_lopo"]["mae"] > report["dummy_lopo"]["mae"]
    assert report["deployed_estimator"] != "dummy"
    assert report["what_to_add_first"].startswith("more independent papers")
    pred = report["example_prediction"]["predicted_viability_pct"]
    assert pred is not None
    assert 0 <= pred <= 100


def test_budget_says_studies_first():
    from tissuelab.benchmark import load_viability

    budget = data_budget(load_viability())
    assert budget["what_to_add_first"] == "studies"
    assert budget["have_enough_for_dummy"] is True
    assert budget["papers_needed_mixed"] == 25
    assert budget["papers_needed_trees"] == 40
    assert budget["have_enough_for_ridge"] is (budget["n_studies"] >= budget["papers_needed_ridge"])
    assert budget["have_enough_for_trees"] is (budget["n_studies"] >= budget["papers_needed_trees"])


def test_example_prediction_is_fibrin():
    from tissuelab.benchmark import load_viability

    out = predict_one_gel(load_viability())
    assert out["query"]["material_class"] == "fibrin"
    assert out["predicted_viability_pct"] is not None

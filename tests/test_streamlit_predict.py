from pathlib import Path

from streamlit.testing.v1 import AppTest

APP = Path(__file__).resolve().parents[1] / "app" / "streamlit_app.py"


def test_predict_tab_shows_literature_viability_without_a_button():
    at = AppTest.from_file(str(APP), default_timeout=90)
    at.run()
    assert not at.exception
    metrics = {m.label: m.value for m in at.metric}
    assert metrics.get("Literature viability") == "80%"
    assert "LOPO MAE (material mean)" in metrics
    assert metrics.get("Papers in split") == "15"

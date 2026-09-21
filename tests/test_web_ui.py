from fastapi.testclient import TestClient

from app.api import app


def test_home_shows_gelma_literature_without_javascript():
    client = TestClient(app)
    response = client.get("/")
    assert response.status_code == 200
    assert "text/html" in response.headers["content-type"]
    body = response.text
    assert "Literature viability" in body
    assert "80%" in body
    assert "Nearest extracted papers" in body
    assert "daly2016" in body or "Daly" in body


def test_home_fibrin_query():
    client = TestClient(app)
    response = client.get("/", params={"material_class": "fibrin", "stiffness_kpa": 25})
    assert response.status_code == 200
    assert "94%" in response.text

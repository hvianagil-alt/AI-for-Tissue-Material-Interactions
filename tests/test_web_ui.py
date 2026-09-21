from fastapi.testclient import TestClient

from app.api import app


def test_home_shows_gelma_literature_without_javascript():
    client = TestClient(app)
    response = client.get("/")
    assert response.status_code == 200
    assert "text/html" in response.headers["content-type"]
    body = response.text
    assert "Qual é o próximo gel" in body
    assert "<svg" in body
    assert "live/dead" in body.lower()


def test_home_fibrin_differs_from_gelma():
    client = TestClient(app)
    gelma = client.get("/", params={"material_class": "GelMA", "stiffness_kpa": 25})
    fibrin = client.get("/", params={"material_class": "fibrin", "stiffness_kpa": 25})
    assert gelma.status_code == 200
    assert fibrin.status_code == 200
    assert "<svg" in gelma.text
    assert gelma.text != fibrin.text
    assert "fibrin" in fibrin.text.lower()

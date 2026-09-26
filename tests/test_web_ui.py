from fastapi.testclient import TestClient

from app.api import app


def test_home_shows_gelma_literature_without_javascript():
    client = TestClient(app)
    response = client.get("/")
    assert response.status_code == 200
    assert "text/html" in response.headers["content-type"]
    body = response.text
    assert "Which gel next" in body
    assert "<svg" in body
    assert "live/dead" in body.lower()
    assert "What if you changed the protocol" in body
    assert "Articular chondrocyte" in body
    assert 'lang="en"' in body
    assert 'href="/table' in body
    assert 'href="/compare' in body
    assert "stiffness (kPa)" in body
    assert "rigidez" not in body
    assert "Also extracted for this gel" in body
    assert "Li et al" in body or "li2016" in body.lower()


def test_home_portuguese_still_available():
    client = TestClient(app)
    body = client.get("/", params={"lang": "pt"}).text
    assert 'lang="pt"' in body
    assert "Tabela" in body


def test_home_fibrin_differs_from_gelma():
    client = TestClient(app)
    gelma = client.get("/", params={"material_class": "GelMA", "stiffness_kpa": 25})
    fibrin = client.get("/", params={"material_class": "fibrin", "stiffness_kpa": 25})
    chitosan = client.get("/", params={"material_class": "chitosan", "stiffness_kpa": 25})
    assert gelma.status_code == 200
    assert fibrin.status_code == 200
    assert chitosan.status_code == 200
    assert "<svg" in gelma.text
    assert gelma.text != fibrin.text
    assert fibrin.text != chitosan.text
    assert "Fibrin" in fibrin.text
    assert "Chitosan" in chitosan.text


def test_home_lists_extracted_composites():
    client = TestClient(app)
    body = client.get("/").text
    assert 'value="fibrin_dECM"' in body
    assert 'value="chitosan_gelatin_PVA"' in body
    assert 'value="GelMA_HA"' in body
    assert "Weak evidence" in body or "borrowed" in body.lower()


def test_table_is_hand_curated_only():
    client = TestClient(app)
    response = client.get("/table")
    assert response.status_code == 200
    body = response.text
    assert "Extracted live/dead table" in body
    assert "pmid" not in body.lower() or "pmid*" in body  # caption may mention exclusion
    assert "Daly" in body or "daly" in body.lower() or "Biofabrication" in body
    csv_response = client.get("/export.csv")
    assert csv_response.status_code == 200
    assert "text/csv" in csv_response.headers["content-type"]
    text = csv_response.text
    assert "material_class" in text
    assert "pmid" not in text.splitlines()[0]
    assert any(line.startswith("2016") or ",daly2016," in line or "daly2016" in line for line in text.splitlines())


def test_table_filter_keeps_all_gels_in_dropdown():
    client = TestClient(app)
    body = client.get("/table", params={"material_class": "chitosan"}).text
    assert "Chitosan" in body
    assert 'value="fibrin"' in body
    assert 'value="GelMA"' in body
    assert "All gels" in body
    assert "pmid" not in body.lower() or "pmid*" in body


def test_compare_gelma_and_fibrin():
    client = TestClient(app)
    response = client.get("/compare", params={"a_material": "GelMA", "b_material": "fibrin"})
    assert response.status_code == 200
    assert "Compare two protocols" in response.text
    assert "GelMA" in response.text
    assert "Fibrin" in response.text
    assert "pp" in response.text
    assert "A is" in response.text

from fastapi.testclient import TestClient

from app.api import app


def test_home_is_a_protocol_for_my_cells():
    client = TestClient(app)
    response = client.get("/")
    assert response.status_code == 200
    body = response.text
    assert "This week, run" in body
    assert "Fibrin" in body
    assert "Find protocol" in body
    assert "Literature for this question" in body
    assert 'lang="en"' in body
    assert 'href="/lookup' in body
    assert 'href="/table' in body
    assert "Which gel next" not in body
    assert "effective n on this gel" not in body


def test_home_portuguese_decision_copy():
    client = TestClient(app)
    body = client.get("/", params={"lang": "pt"}).text
    assert 'lang="pt"' in body
    assert "Esta semana" in body
    assert "Protocolo" in body
    assert "Tabela" in body


def test_home_print_differs_from_alive():
    client = TestClient(app)
    alive = client.get("/", params={"goal": "alive"})
    printed = client.get("/", params={"goal": "print", "how": "print"})
    assert alive.status_code == 200
    assert printed.status_code == 200
    assert "Fibrin" in alive.text
    assert alive.text != printed.text


def test_lookup_still_looks_up_a_picked_gel():
    client = TestClient(app)
    response = client.get("/lookup")
    assert response.status_code == 200
    body = response.text
    assert "Look up this protocol" in body
    assert "<svg" in body
    assert "Also extracted for this gel" in body
    assert "Li et al" in body or "li2016" in body.lower()
    assert "stiffness (kPa)" in body
    assert "rigidez" not in body
    assert "How this number is made" in body


def test_lookup_fibrin_differs_from_gelma():
    client = TestClient(app)
    gelma = client.get("/lookup", params={"material_class": "GelMA", "stiffness_kpa": 25})
    fibrin = client.get("/lookup", params={"material_class": "fibrin", "stiffness_kpa": 25})
    chitosan = client.get("/lookup", params={"material_class": "chitosan", "stiffness_kpa": 25})
    assert gelma.status_code == 200
    assert fibrin.text != gelma.text
    assert "Fibrin" in fibrin.text
    assert "Chitosan" in chitosan.text
    assert 'value="GelMA_HA"' in gelma.text


def test_table_is_hand_curated_only():
    client = TestClient(app)
    response = client.get("/table")
    assert response.status_code == 200
    body = response.text
    assert "Extracted live/dead table" in body
    assert "pmid" not in body.lower() or "pmid*" in body
    csv_response = client.get("/export.csv")
    assert csv_response.status_code == 200
    assert "material_class" in csv_response.text.splitlines()[0]
    assert any("daly2016" in line or line.startswith("2016") for line in csv_response.text.splitlines())


def test_library_page_loads():
    client = TestClient(app)
    response = client.get("/library")
    assert response.status_code == 200
    assert "chemistry" in response.text.lower() or "química" in response.text.lower()
    assert "/library" in client.get("/").text


def test_table_filter_keeps_all_gels_in_dropdown():
    client = TestClient(app)
    body = client.get("/table", params={"material_class": "chitosan"}).text
    assert "Chitosan" in body
    assert 'value="fibrin"' in body
    assert 'value="GelMA"' in body
    assert "All gels" in body


def test_compare_gelma_and_fibrin():
    client = TestClient(app)
    response = client.get("/compare", params={"a_material": "GelMA", "b_material": "fibrin"})
    assert response.status_code == 200
    assert "Compare two protocols" in response.text
    assert "Fibrin" in response.text
    assert "A is" in response.text

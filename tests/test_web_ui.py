from fastapi.testclient import TestClient

from app.api import app


def test_home_is_a_protocol_for_my_cells():
    client = TestClient(app)
    response = client.get("/")
    assert response.status_code == 200
    body = response.text
    assert "This week, run" in body
    assert "Fibrin" in body
    assert "This week’s gel" in body
    assert "Find protocol" not in body
    assert "Literature for this question" in body
    assert "served model has" in body
    assert "Beginning target" in body
    assert "tree report gate" in body
    assert "harvested papers (library)" in body
    assert "extracted live/dead papers" in body
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
    assert "served parameters" in body
    assert "beginning target" in body


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
    assert "served shrinkage model" in body
    assert "Beginning target" in body
    csv_response = client.get("/export.csv")
    assert csv_response.status_code == 200
    assert "material_class" in csv_response.text.splitlines()[0]
    assert any("daly2016" in line or line.startswith("2016") for line in csv_response.text.splitlines())


def test_library_page_loads():
    client = TestClient(app)
    response = client.get("/library")
    assert response.status_code == 200
    body = response.text
    assert "chemistry" in body.lower() or "química" in body.lower()
    assert "Two tables:" in body
    assert "beginning target" in body.lower()
    assert "parameters" in body.lower()
    assert "harvested papers tagged" in body
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
    assert "not a prediction duel" in response.text


def test_avoid_page_lists_peg_for_articular():
    client = TestClient(app)
    response = client.get("/avoid")
    assert response.status_code == 200
    body = response.text
    assert "Do not start here" in body
    assert "PEG" in body
    assert "Never extract" in body
    assert "fragile_competitor" in body or "GelMA" in body
    assert "/avoid" in client.get("/").text


def test_home_is_not_a_prediction():
    client = TestClient(app)
    body = client.get("/").text
    assert "not a prediction of your flask" in body.lower()
    assert "Do not start here" in body
    assert "What labs run" in body
    assert "This week’s gel" in body
    assert "dummy MAE" in body or "LOPO" in body
    assert "print-only" in body.lower() or "encapsulate GelMA" in body
    assert "Friday pack" in body


def test_api_decision_json():
    client = TestClient(app)
    response = client.get("/api/decision", params={"cell_type": "articular_chondrocyte"})
    assert response.status_code == 200
    data = response.json()
    assert data["not_a_prediction"] is True
    assert data["protocol"]["material_class"] == "fibrin"
    assert data["avoid_board"]
    assert data["model_card"]["mvp_pass"] is False
    avoid = client.get("/api/avoid", params={"cell_type": "articular_chondrocyte"}).json()
    assert any(row["material_class"] == "PEG" for row in avoid["avoid"])
    health = client.get("/health").json()
    assert health["product"] == "friday_protocol"


def test_friday_pack_and_avoid_csv():
    client = TestClient(app)
    pack = client.get("/pack")
    assert pack.status_code == 200
    body = pack.text
    assert "Friday pack" in body
    assert "Fibrin" in body
    assert "PEG" in body
    assert "£400" in body
    csv_r = client.get("/export.avoid.csv", params={"cell_type": "articular_chondrocyte"})
    assert csv_r.status_code == 200
    assert "material_class" in csv_r.text.splitlines()[0]
    assert "PEG" in csv_r.text
    data = client.get("/api/decision").json()
    assert data.get("honesty")

from tissuelab.protocol_finder import find_protocol


def test_articular_alive_prefers_fibrin_over_gelma():
    out = find_protocol(cell_type="articular_chondrocyte", goal="alive", how="encapsulate")
    assert out["protocol"]["material_class"] == "fibrin"
    assert out["same_mean"] is not None and out["same_mean"] >= 90
    assert out["n_same_numeric"] >= 2
    assert out["papers"]
    assert any(p.get("doi") for p in out["papers"])
    gelma = out["field_default"]
    assert gelma["n_same_numeric"] >= 2
    assert gelma["same_mean"] is not None
    assert gelma["same_mean"] < out["same_mean"]
    assert "GelMA" in out["why"]


def test_print_uses_a_printed_gel():
    out = find_protocol(cell_type="articular_chondrocyte", goal="print", how="print")
    assert out["n_print_same"] >= 1
    assert out["protocol"]["material_class"] in {"HA", "gelatin_alginate", "alginate_dECM", "cellulose_alginate"}


def test_avoid_peg_and_stock_warning():
    out = find_protocol(cell_type="articular_chondrocyte", goal="alive", stock="PEG")
    assert out["protocol"]["material_class"] != "PEG"
    assert out["stock_warning"]
    alts = {a["material_class"]: a for a in out["alternatives"]}
    assert "PEG" in alts
    assert alts["PEG"]["avoid"] is True


def test_msc_does_not_crash():
    out = find_protocol(cell_type="MSC", goal="alive")
    assert out["protocol"]["material_class"]
    assert out["protocol"]["cell_type"] == "MSC"

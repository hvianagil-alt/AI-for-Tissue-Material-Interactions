from tissuelab.product import (
    AVOID_MEAN,
    NEVER_EXTRACT,
    avoid_board,
    coverage_table,
    honest_model_card,
    lab_decision,
    research_queue,
)
from tissuelab.protocol_finder import AVOID_MEAN as FINDER_AVOID


def test_avoid_threshold_is_shared():
    assert AVOID_MEAN == FINDER_AVOID == 60.0


def test_articular_avoid_board_includes_peg():
    board = avoid_board("articular_chondrocyte")
    gels = {row["material_class"] for row in board}
    assert "PEG" in gels
    peg = next(row for row in board if row["material_class"] == "PEG")
    assert peg["mean"] < 60
    assert peg["avoid"] is True
    assert peg["n_papers"] >= 1


def test_coverage_has_gelma_and_fibrin_articular():
    rows = {
        (r["material_class"], r["cell_type"]): r
        for r in coverage_table()
        if r["cell_type"] == "articular_chondrocyte"
    }
    assert ("fibrin", "articular_chondrocyte") in rows
    assert ("GelMA", "articular_chondrocyte") in rows
    fibrin = rows[("fibrin", "articular_chondrocyte")]
    gelma = rows[("GelMA", "articular_chondrocyte")]
    assert fibrin["mean"] > gelma["mean"]
    assert gelma["n_papers"] == 1
    assert gelma["fragile"] is True


def test_honest_card_does_not_claim_mvp():
    card = honest_model_card()
    assert card["mvp_pass"] is False
    assert card["n_studies"] >= 15
    assert "predictor" in card["sell"].lower() or "papers" in card["sell"].lower()
    assert card["dummy_mae"] is not None
    assert card["shrinkage_mae"] is not None


def test_research_queue_puts_gelma_articular_first():
    queue = research_queue(limit=15)
    assert queue
    top = {(h["material_class"], h["cell_type"]) for h in queue[:5]}
    assert ("GelMA", "articular_chondrocyte") in top
    gelma = next(h for h in queue if h["material_class"] == "GelMA" and h["cell_type"] == "articular_chondrocyte")
    assert gelma["kind"] in {"fragile_competitor", "missing_encap"}
    assert gelma["n_papers"] == 1
    assert gelma.get("n_encap", 1) == 0
    kinds = {h["kind"] for h in queue}
    assert "locked_avoid" not in kinds
    assert not any(h["material_class"] == "PEG" and h["cell_type"] == "articular_chondrocyte" for h in queue)
    fibrin = next(
        (h for h in queue if h["material_class"] == "fibrin" and h["cell_type"] == "articular_chondrocyte"),
        None,
    )
    assert fibrin is not None
    assert fibrin["kind"] == "missing_print"
    assert NEVER_EXTRACT
    assert any("MTT" in line for line in NEVER_EXTRACT)
    assert any("death gels" in line for line in NEVER_EXTRACT)


def test_lab_decision_is_friday_pack_not_a_predictor():
    out = lab_decision(cell_type="articular_chondrocyte", goal="alive", how="encapsulate")
    assert out["not_a_prediction"] is True
    assert out["protocol"]["material_class"] == "fibrin"
    assert out["recipe"]
    assert any(p.get("doi") for p in out["papers"])
    assert out["offer"]["job"] == "friday_protocol"
    assert "predict" in out["offer"]["sell"].lower() or "prevê" in out["offer"]["sell"].lower()
    assert any(d["material_class"] == "PEG" for d in out["avoid_board"])
    assert out["model_card"]["mvp_pass"] is False
    assert out["coverage"]
    assert out["research_queue"]
    assert out["offer"]["price_pilot"].startswith("£400")
    assert "quarter" in out["offer"]["price_pilot"]

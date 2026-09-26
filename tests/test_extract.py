from tissuelab.europepmc import xml_to_text
from tissuelab.extract import extract_conditions, extract_from_abstract
from tissuelab.load_database import load
from tissuelab.paths import DB_PATH


def test_extract_numeric_candidates_are_flagged_low():
    text = (
        "Chondrocytes encapsulated in a GelMA hydrogel showed 92% viability after 14 days. "
        "Young's modulus was 25 kPa. TGF-β3 was added."
    )
    rows = extract_from_abstract(text, "GelMA cartilage hydrogel")
    fields = {r["field"] for r in rows}
    assert "material_class" in fields
    assert "cell_type" in fields
    assert "viability_pct" in fields
    assert "stiffness_kpa" in fields
    viab = [r for r in rows if r["field"] == "viability_pct"]
    assert viab[0]["value_num"] == 92.0
    assert viab[0]["confidence"] == "low"
    mats = {r["value_text"] for r in rows if r["field"] == "material_class"}
    assert "GelMA" in mats


def test_off_target_cell_line_is_not_promoted():
    rows = extract_conditions(
        "H9c2 hydrogel viability",
        "H9c2 cardiomyocytes in GelMA showed 90% viability after 7 days.",
    )
    assert rows == []


def test_nasoseptal_is_not_mapped_to_articular():
    from tissuelab.extract import pick_cell, cells_in

    cells = cells_in("Human nasoseptal chondrocytes in a nanocellulose alginate bioink.")
    assert "nasal_chondrocyte" in cells
    assert pick_cell(cells) == "nasal_chondrocyte"


def test_placeholder_amass_key_is_rejected(monkeypatch):
    monkeypatch.setenv("AMASS_API_KEY", "amass_cole_aqui")
    from tissuelab.harvest_amass import api_key

    try:
        api_key()
    except SystemExit:
        return
    raise AssertionError("placeholder key must not be accepted")


def test_extract_conditions_pairs_sentence_numbers():
    rows = extract_conditions(
        "GelMA cartilage hydrogel",
        "Chondrocytes in GelMA showed 92% viability at 25 kPa after 14 days.",
    )
    assert len(rows) == 1
    assert rows[0]["viability_pct"] == 92.0
    assert rows[0]["stiffness_kpa"] == 25.0
    assert rows[0]["paired_stiffness"] is True
    assert rows[0]["material_class"] == "GelMA"
    assert rows[0]["cell_type"] == "articular_chondrocyte"


def test_europepmc_xml_to_text_strips_tags():
    text = xml_to_text("<article><p>Chondrocytes showed 90% viability</p></article>")
    assert "90%" in text
    assert "<p>" not in text


def test_load_preserves_amass_papers(tmp_path):
    db = tmp_path / "t.sqlite"
    load(db)
    from tissuelab.db import connect, init_schema

    conn = connect(db)
    init_schema(conn)
    conn.execute(
        """
        INSERT INTO papers (amass_id, pmid, title, abstract, harvested_at)
        VALUES ('AMBC_test', '1', 't', 'chondrocyte hydrogel', 'now')
        """
    )
    conn.commit()
    conn.close()
    load(db)
    conn = connect(db)
    n = conn.execute("SELECT COUNT(*) FROM papers WHERE amass_id = 'AMBC_test'").fetchone()[0]
    n_exp = conn.execute("SELECT COUNT(*) FROM experiments").fetchone()[0]
    conn.close()
    assert n == 1
    assert n_exp >= 40


def test_tmp_load_does_not_clobber_quality_report(tmp_path):
    from tissuelab.paths import QUALITY_REPORT_PATH

    before = QUALITY_REPORT_PATH.read_text() if QUALITY_REPORT_PATH.exists() else None
    load(tmp_path / "t.sqlite")
    after = QUALITY_REPORT_PATH.read_text() if QUALITY_REPORT_PATH.exists() else None
    assert after == before

from tissuelab.extract import extract_from_abstract
from tissuelab.ontology import analyze_text, tag_experiment


def test_gelma_is_methacrylated():
    tags = analyze_text("GelMA chondrocyte hydrogel", "Methacrylated gelatin photocrosslinked with Irgacure 2959.")
    assert tags["chemical_modification"] == "methacrylated"
    assert "photo_I2959" in tags["chemical_modifications"]
    assert tags["architecture"] in {"bulk_hydrogel", "3d_printed"}
    assert tags["application"] == "in_vitro_cartilage"


def test_bioprint_architecture_and_application():
    tags = analyze_text("Alginate bioink", "We bioprinted articular chondrocytes.")
    assert tags["architecture"] == "3d_printed"
    assert tags["application"] in {"bioprinting", "in_vitro_cartilage"}


def test_extract_abstract_emits_chemistry_fields():
    rows = extract_from_abstract(
        "Chondrocytes in methacrylated gelatin showed 90% viability after 7 days.",
        "GelMA cartilage hydrogel",
    )
    fields = {r["field"]: r["value_text"] for r in rows}
    assert fields.get("chemical_modification") == "methacrylated"
    assert "application" in fields


def test_tag_experiment_does_not_methacrylate_agarose_from_gelma_notes():
    tagged = tag_experiment(
        {
            "material_class": "agarose",
            "culture_model": "3D_bioprint",
            "cell_type": "MSC",
            "notes": "Alginate/agarose vs GelMA/PEGMA bioinks.",
        }
    )
    assert tagged["chemical_modification"] != "methacrylated"
    assert tagged["architecture"] == "3d_printed"
    tagged = tag_experiment(
        {
            "material_class": "GelMA",
            "culture_model": "3D_encapsulation",
            "cell_type": "articular_chondrocyte",
            "notes": "10 wt% GelMA",
        }
    )
    assert tagged["chemical_modification"] == "methacrylated"
    assert tagged["architecture"] == "bulk_hydrogel"
    assert tagged["application"] == "in_vitro_cartilage"


def test_nasal_chondrocyte_tags_nasal_application():
    tagged = tag_experiment(
        {
            "material_class": "cellulose_alginate",
            "culture_model": "3D_bioprint",
            "cell_type": "nasal_chondrocyte",
            "notes": "Nasoseptal chondrocytes in NCA bioink.",
        }
    )
    assert tagged["application"] == "nasal"
    assert tagged["architecture"] == "3d_printed"

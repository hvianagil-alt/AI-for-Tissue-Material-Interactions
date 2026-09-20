from tissuelab.literature import LITERATURE_RECORDS
from tissuelab.schema import ExperimentRecord, FEATURE_COLUMNS


def test_literature_records_validate():
    assert len(LITERATURE_RECORDS) >= 20
    for row in LITERATURE_RECORDS:
        parsed = ExperimentRecord.model_validate(row)
        assert parsed.source == "literature"
        assert parsed.viability_pct is not None
        assert 0 <= parsed.viability_pct <= 100
        assert parsed.doi


def test_feature_columns_cover_design_fields():
    required = {
        "material_class",
        "stiffness_kpa",
        "cell_type",
        "species",
        "culture_time_days",
    }
    assert required.issubset(set(FEATURE_COLUMNS))

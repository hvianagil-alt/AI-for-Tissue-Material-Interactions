-- TissueLab experimental database
-- One row in experiments = one published condition (material × biology × time).
-- Outcomes live in measurements (tidy / long form) so new cell-type assays
-- (ALP, mineralisation, uptake, …) can be added without altering columns.

PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS studies (
    study_id        TEXT PRIMARY KEY,
    citation        TEXT NOT NULL,
    doi             TEXT,
    year            INTEGER,
    journal         TEXT,
    pmcid           TEXT,
    license         TEXT,
    tissue_focus    TEXT NOT NULL DEFAULT 'cartilage',
    notes           TEXT
);

-- Controlled vocabularies. New cell types and assays are rows, not migrations.
CREATE TABLE IF NOT EXISTS vocab_cell_types (
    cell_type       TEXT PRIMARY KEY,
    tissue_family   TEXT NOT NULL,
    notes           TEXT
);

CREATE TABLE IF NOT EXISTS vocab_assays (
    assay           TEXT PRIMARY KEY,
    dimension       TEXT NOT NULL,  -- viability | proliferation | differentiation | ecm | other
    canonical_unit  TEXT,
    cell_family     TEXT,           -- NULL = shared across cell types
    notes           TEXT
);

CREATE TABLE IF NOT EXISTS vocab_materials (
    material_class  TEXT PRIMARY KEY,
    material_family TEXT,
    notes           TEXT
);

CREATE TABLE IF NOT EXISTS experiments (
    experiment_id                 TEXT PRIMARY KEY,
    study_id                      TEXT NOT NULL REFERENCES studies(study_id),
    material_class                TEXT NOT NULL REFERENCES vocab_materials(material_class),
    material_detail               TEXT,
    crosslinking                  TEXT,
    polymer_concentration_wt_pct  REAL,
    stiffness_kpa                 REAL,
    stiffness_sd_kpa              REAL,
    stiffness_method              TEXT,
    porosity_pct                  REAL,
    degradation_half_life_days    REAL,
    surface_chemistry             TEXT,
    has_adhesion_ligand           REAL,
    tissue                        TEXT NOT NULL DEFAULT 'cartilage',
    cell_type                     TEXT NOT NULL REFERENCES vocab_cell_types(cell_type),
    species                       TEXT,
    culture_model                 TEXT,
    growth_factor                 TEXT,
    culture_time_days             REAL,
    cell_density_million_per_ml   REAL,
    passage                       INTEGER,
    n_replicates                  INTEGER,
    extracted_from                TEXT,
    curator_confidence            TEXT NOT NULL DEFAULT 'medium',
    notes                         TEXT
);

CREATE TABLE IF NOT EXISTS measurements (
    measurement_id    INTEGER PRIMARY KEY AUTOINCREMENT,
    experiment_id     TEXT NOT NULL REFERENCES experiments(experiment_id) ON DELETE CASCADE,
    assay             TEXT NOT NULL REFERENCES vocab_assays(assay),
    value             REAL,
    value_sd          REAL,
    unit              TEXT NOT NULL,
    qualitative_label TEXT,
    evidence          TEXT NOT NULL, -- numeric_text | numeric_table | qualitative_text | figure_estimated
    n                 INTEGER,
    notes             TEXT,
    CHECK (value IS NOT NULL OR qualitative_label IS NOT NULL)
);

CREATE INDEX IF NOT EXISTS idx_exp_study ON experiments(study_id);
CREATE INDEX IF NOT EXISTS idx_exp_material ON experiments(material_class);
CREATE INDEX IF NOT EXISTS idx_exp_cell ON experiments(cell_type);
CREATE INDEX IF NOT EXISTS idx_meas_assay ON measurements(assay);

-- Modeling view: one row per experiment, viability only when a number was published.
CREATE VIEW IF NOT EXISTS v_model_viability AS
SELECT
    e.experiment_id,
    e.study_id,
    e.material_class,
    e.stiffness_kpa,
    e.polymer_concentration_wt_pct,
    e.cell_type,
    e.species,
    e.culture_model,
    e.growth_factor,
    e.culture_time_days,
    e.cell_density_million_per_ml,
    e.passage,
    e.has_adhesion_ligand,
    m.value AS viability_pct,
    m.value_sd AS viability_sd,
    m.evidence AS viability_evidence
FROM experiments e
JOIN measurements m ON m.experiment_id = e.experiment_id
WHERE m.assay = 'viability_pct'
  AND m.value IS NOT NULL;

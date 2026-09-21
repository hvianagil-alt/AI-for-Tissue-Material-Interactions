-- TissueLab experimental database
-- One row in experiments = one published condition (material × biology × time).
-- Outcomes live in measurements (tidy / long form) so new cell-type assays
-- (ALP, mineralisation, uptake, …) can be added without altering columns.

PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS studies (
    study_id        TEXT PRIMARY KEY,
    citation        TEXT NOT NULL,
    doi             TEXT,
    pmid            TEXT,
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

-- Amass BiomedCore harvest. Abstracts are observations of the literature,
-- not curated experiments. Do not copy regex hits into experiments.
CREATE TABLE IF NOT EXISTS papers (
    amass_id              TEXT PRIMARY KEY,
    pmid                  TEXT,
    pmcid                 TEXT,
    doi                   TEXT,
    title                 TEXT,
    abstract              TEXT,
    journal               TEXT,
    publication_date      TEXT,
    year                  INTEGER,
    citation_count        INTEGER,
    journal_quality_jufo  INTEGER,
    has_fulltext          INTEGER,
    is_retracted          INTEGER,
    publication_types     TEXT,
    mesh_terms            TEXT,
    keywords              TEXT,
    substances            TEXT,
    authors               TEXT,
    language              TEXT,
    query_hits            TEXT,
    harvested_at          TEXT
);

CREATE TABLE IF NOT EXISTS paper_extractions (
    extraction_id   INTEGER PRIMARY KEY AUTOINCREMENT,
    amass_id        TEXT NOT NULL REFERENCES papers(amass_id) ON DELETE CASCADE,
    field           TEXT NOT NULL,
    value_text      TEXT,
    value_num       REAL,
    unit            TEXT,
    evidence_span   TEXT,
    extractor       TEXT NOT NULL DEFAULT 'regex_abstract',
    confidence      TEXT NOT NULL DEFAULT 'low'
);

CREATE TABLE IF NOT EXISTS harvest_log (
    log_id                 INTEGER PRIMARY KEY AUTOINCREMENT,
    query                  TEXT NOT NULL,
    min_publication_date   TEXT,
    max_publication_date   TEXT,
    limit_requested        INTEGER,
    n_returned             INTEGER,
    n_new                  INTEGER,
    http_status            INTEGER,
    credit_cost            INTEGER,
    requested_at           TEXT
);

CREATE INDEX IF NOT EXISTS idx_papers_pmid ON papers(pmid);
CREATE INDEX IF NOT EXISTS idx_papers_year ON papers(year);
CREATE INDEX IF NOT EXISTS idx_papers_doi ON papers(doi);
CREATE INDEX IF NOT EXISTS idx_extract_amass ON paper_extractions(amass_id);
CREATE INDEX IF NOT EXISTS idx_extract_field ON paper_extractions(field);

-- Ranked work queue: which harvested papers to extract into experiments next.
-- Scores are retrieval ranks, not scientific measurements.
CREATE TABLE IF NOT EXISTS paper_scores (
    amass_id                 TEXT PRIMARY KEY REFERENCES papers(amass_id) ON DELETE CASCADE,
    score                    REAL NOT NULL,
    is_review                INTEGER NOT NULL DEFAULT 0,
    is_mvp_relevant          INTEGER NOT NULL DEFAULT 0,
    already_curated          INTEGER NOT NULL DEFAULT 0,
    has_chondrocyte          INTEGER NOT NULL DEFAULT 0,
    has_msc                  INTEGER NOT NULL DEFAULT 0,
    has_mapped_material      INTEGER NOT NULL DEFAULT 0,
    has_viability_number     INTEGER NOT NULL DEFAULT 0,
    has_stiffness_number     INTEGER NOT NULL DEFAULT 0,
    n_materials              INTEGER NOT NULL DEFAULT 0,
    reasons                  TEXT,
    scored_at                TEXT
);

CREATE TABLE IF NOT EXISTS extraction_queue (
    amass_id        TEXT PRIMARY KEY REFERENCES papers(amass_id) ON DELETE CASCADE,
    rank            INTEGER NOT NULL,
    score           REAL NOT NULL,
    status          TEXT NOT NULL DEFAULT 'queued',
    why             TEXT,
    pmid            TEXT,
    doi             TEXT,
    title           TEXT,
    year            INTEGER,
    journal         TEXT,
    citation_count  INTEGER,
    has_fulltext    INTEGER
);

CREATE TABLE IF NOT EXISTS study_paper_links (
    study_id    TEXT NOT NULL REFERENCES studies(study_id) ON DELETE CASCADE,
    amass_id    TEXT NOT NULL REFERENCES papers(amass_id) ON DELETE CASCADE,
    matched_on  TEXT NOT NULL,
    PRIMARY KEY (study_id, amass_id)
);

CREATE INDEX IF NOT EXISTS idx_queue_rank ON extraction_queue(rank);
CREATE INDEX IF NOT EXISTS idx_scores_mvp ON paper_scores(is_mvp_relevant, score);

-- Modeling view: published live/dead % from hand-curated studies only.
-- Auto-promoted pmid* rows stay in experiments; they are not training labels.
DROP VIEW IF EXISTS v_model_viability;
DROP VIEW IF EXISTS v_auto_viability;
CREATE VIEW IF NOT EXISTS v_model_viability AS
SELECT
    e.experiment_id,
    e.study_id,
    s.citation,
    s.doi,
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
    e.curator_confidence,
    m.value AS viability_pct,
    m.value_sd AS viability_sd,
    m.evidence AS viability_evidence
FROM experiments e
JOIN studies s ON s.study_id = e.study_id
JOIN measurements m ON m.experiment_id = e.experiment_id
WHERE m.assay = 'viability_pct'
  AND m.value IS NOT NULL
  AND e.study_id NOT LIKE 'pmid%';

CREATE VIEW IF NOT EXISTS v_auto_viability AS
SELECT
    e.experiment_id,
    e.study_id,
    e.material_class,
    e.stiffness_kpa,
    m.value AS viability_pct
FROM experiments e
JOIN measurements m ON m.experiment_id = e.experiment_id
WHERE m.assay = 'viability_pct'
  AND m.value IS NOT NULL
  AND e.study_id LIKE 'pmid%';

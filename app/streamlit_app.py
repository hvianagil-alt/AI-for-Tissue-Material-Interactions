"""TissueLab AI — Streamlit Tissue Interaction Engine."""

from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from tissuelab.inverse import candidate_rationale, inverse_design
from tissuelab.literature_model import predict_literature_viability
from tissuelab.paths import DATASET_PATH, HONEST_METRICS_PATH, EXTRACTION_QUEUE_PATH, MODEL_PATH, NATIVE_EXPORT_PATH, QUALITY_REPORT_PATH, VIABILITY_EXPORT_PATH
from tissuelab.predict import predict_design
from tissuelab.protocol import protocol_from_row
from tissuelab.recommend import recommend_experiments, recommendation_reason
from tissuelab.schema import TARGETS
from tissuelab.train import load_dataset, load_model, main as train_main

st.set_page_config(
    page_title="TissueLab AI",
    page_icon="🧬",
    layout="wide",
)

st.markdown(
    """
    <style>
      .stApp { background: #0b1220; color: #e8eef7; }
      h1, h2, h3 { color: #f4fbff !important; }
      [data-testid="stMetricValue"] { color: #3ecfb2; }
      .block-container { padding-top: 1.4rem; }
      div[data-testid="stCaptionContainer"] { color: #9db0c8; }
    </style>
    """,
    unsafe_allow_html=True,
)

TARGET_LABELS = {
    "viability_pct": "Viability %",
    "proliferation_score": "Proliferation",
    "differentiation_score": "Differentiation",
    "ecm_deposition_score": "ECM deposition",
}


@st.cache_resource
def get_model():
    if not MODEL_PATH.exists():
        train_main()
    return load_model()


@st.cache_data
def get_data():
    if not DATASET_PATH.exists():
        train_main()
    return load_dataset()


def radar_chart(values: dict, title: str, low: dict | None = None, high: dict | None = None) -> go.Figure:
    labels = [TARGET_LABELS[t] for t in TARGETS]
    fig = go.Figure()
    fig.add_trace(
        go.Scatterpolar(
            r=[values[t] for t in TARGETS] + [values[TARGETS[0]]],
            theta=labels + [labels[0]],
            fill="toself",
            name="Predicted",
            line=dict(color="#3ecfb2"),
        )
    )
    if low and high:
        fig.add_trace(
            go.Scatterpolar(
                r=[high[t] for t in TARGETS] + [high[TARGETS[0]]],
                theta=labels + [labels[0]],
                name="Upper 90%",
                line=dict(color="#3ecfb2", width=1, dash="dot"),
            )
        )
        fig.add_trace(
            go.Scatterpolar(
                r=[low[t] for t in TARGETS] + [low[TARGETS[0]]],
                theta=labels + [labels[0]],
                name="Lower 10%",
                line=dict(color="#7f8ea3", width=1, dash="dot"),
            )
        )
    fig.update_layout(
        polar=dict(radialaxis=dict(visible=True, range=[0, 100], gridcolor="#243044")),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color="#e8eef7"),
        title=title,
        showlegend=True,
        margin=dict(t=48, b=24),
        height=420,
    )
    return fig


def design_form(prefix: str, defaults: dict | None = None) -> dict:
    defaults = defaults or {}
    c1, c2, c3 = st.columns(3)
    with c1:
        material_class = st.selectbox(
            "Hydrogel",
            [
                "GelMA",
                "fibrin",
                "silk_fibrin",
                "HA",
                "alginate",
                "gelatin_alginate",
                "collagen",
                "agarose",
                "PEG",
                "PEG_dextran",
                "chitosan",
                "chitosan_HA",
                "chitosan_gelatin_PVA",
                "cellulose_alginate",
                "fibrin_HA",
                "GelMA_HA",
                "GelMA_chitosan",
                "collagen_alginate",
                "PEG_HA",
                "PEG_silk",
            ],
            index=0,
            key=f"{prefix}_material",
        )
        crosslinking = st.selectbox(
            "Crosslinking",
            ["photocrosslink", "enzymatic", "ionic", "thermal", "chemical"],
            key=f"{prefix}_xl",
        )
        polymer_concentration_wt_pct = st.slider("Polymer concentration (wt%)", 0.4, 22.0, float(defaults.get("polymer_concentration_wt_pct", 8.0)), key=f"{prefix}_conc")
        stiffness_kpa = st.slider("Stiffness (kPa)", 0.5, 200.0, float(defaults.get("stiffness_kpa", 25.0)), key=f"{prefix}_stiff")
    with c2:
        porosity_pct = st.slider("Porosity (%)", 30.0, 97.0, 80.0, key=f"{prefix}_por")
        degradation_half_life_days = st.slider("Degradation half-life (days)", 2.0, 200.0, 14.0, key=f"{prefix}_deg")
        surface_chemistry = st.selectbox("Surface chemistry", ["native", "RGD", "MMP_degradable", "none"], key=f"{prefix}_surf")
        has_adhesion_ligand = st.slider("Adhesion ligand (0–1)", 0.0, 1.0, 1.0, key=f"{prefix}_lig")
    with c3:
        cell_type = st.selectbox(
            "Cell type",
            ["articular_chondrocyte", "auricular_chondrocyte", "MSC", "adipose_MSC"],
            key=f"{prefix}_cell",
        )
        species = st.selectbox("Species", ["human", "bovine", "porcine", "rabbit"], key=f"{prefix}_sp")
        culture_model = st.selectbox("Culture model", ["3D_encapsulation", "3D_bioprint", "2D"], key=f"{prefix}_cult")
        growth_factor = st.selectbox("Growth factor", ["none", "TGF_b3", "TGF_b1"], key=f"{prefix}_gf")
        culture_time_days = st.slider("Culture time (days)", 7, 42, 14, key=f"{prefix}_time")
        cell_density_million_per_ml = st.slider("Cell density (10⁶/mL)", 0.5, 30.0, 5.0, key=f"{prefix}_dens")
        passage = st.slider("Passage", 0, 6, 2, key=f"{prefix}_pass")
    return {
        "material_class": material_class,
        "crosslinking": crosslinking,
        "polymer_concentration_wt_pct": polymer_concentration_wt_pct,
        "stiffness_kpa": stiffness_kpa,
        "porosity_pct": porosity_pct,
        "degradation_half_life_days": degradation_half_life_days,
        "surface_chemistry": surface_chemistry,
        "has_adhesion_ligand": has_adhesion_ligand,
        "cell_type": cell_type,
        "species": species,
        "culture_model": culture_model,
        "growth_factor": growth_factor,
        "culture_time_days": culture_time_days,
        "cell_density_million_per_ml": cell_density_million_per_ml,
        "passage": passage,
    }


def show_prediction(result, literature: dict | None = None) -> None:
    if literature and literature.get("mean") is not None:
        st.subheader("Published viability (hand-curated table)")
        c1, c2, c3 = st.columns(3)
        c1.metric("Literature viability", f"{literature['mean']:.0f}%", f"{literature['low']:.0f}–{literature['high']:.0f}")
        lopo = literature.get("lopo") or {}
        c2.metric("LOPO MAE (Ridge)", f"{lopo.get('ridge_mae', float('nan')):.1f}" if lopo.get("ridge_mae") is not None else "—")
        c3.metric("Papers in split", lopo.get("n_studies") or "—")
        st.caption("Interval is ± leave-one-paper-out MAE on numeric live/dead. Auto-promoted abstracts are not in this model.")
        if literature.get("similar"):
            st.markdown("Nearest **extracted** papers")
            st.dataframe(pd.DataFrame(literature["similar"]), hide_index=True, use_container_width=True)
        for note in literature.get("notes") or []:
            st.info(note)
    st.caption("The four scores below still include the simulator-informed demo model. Viability above is the scientific number.")
    cols = st.columns(4)
    for col, target in zip(cols, TARGETS):
        interval = result.outcomes[target]
        col.metric(TARGET_LABELS[target], f"{interval.mean:.0f}", f"{interval.low:.0f}–{interval.high:.0f}")
    means = {t: result.outcomes[t].mean for t in TARGETS}
    lows = {t: result.outcomes[t].low for t in TARGETS}
    highs = {t: result.outcomes[t].high for t in TARGETS}
    left, right = st.columns([1.1, 1])
    with left:
        st.plotly_chart(radar_chart(means, "Predicted chondrocyte response", lows, highs), use_container_width=True)
    with right:
        st.subheader("Why these numbers")
        st.caption("Global feature importance from the XGBoost model (not a local SHAP explanation).")
        st.dataframe(pd.DataFrame(result.influential_features), hide_index=True, use_container_width=True)
        for note in result.notes:
            st.warning(note)
    st.subheader("Suggested protocol")
    st.write(result.protocol)
    st.subheader("Similar published / simulated experiments")
    st.dataframe(pd.DataFrame(result.similar_experiments), hide_index=True, use_container_width=True)


model = get_model()
data = get_data()

st.title("TissueLab AI")
st.caption(
    "MVP 1 — Tissue Interaction Engine for **hydrogel → chondrocyte / cartilage**. "
    "Published live/dead numbers are the training labels. The four-outcome radar still uses a simulator-informed demo. "
    "Use nearest extracted papers to choose the next gel, not as a virtual human."
)

tab_predict, tab_inverse, tab_next, tab_data, tab_about = st.tabs(
    ["Predict", "Inverse design", "Next experiment", "Dataset", "About"]
)

with tab_predict:
    st.markdown("Enter a hydrogel and biological context. Published viability comes from hand-curated live/dead %. The four-outcome radar is still a demo prior.")
    design = design_form("predict")
    if st.button("Predict tissue interaction", type="primary"):
        lit = predict_literature_viability(design)
        show_prediction(predict_design(model, design), literature=lit)

with tab_inverse:
    st.markdown(
        "Describe the cartilage response you want. TissueLab samples feasible hydrogel designs and ranks those whose predicted profile is closest to the target."
    )
    t1, t2, t3, t4 = st.columns(4)
    targets = {
        "viability_pct": t1.slider("Target viability", 50, 100, 90),
        "proliferation_score": t2.slider("Target proliferation", 20, 100, 55),
        "differentiation_score": t3.slider("Target differentiation", 20, 100, 80),
        "ecm_deposition_score": t4.slider("Target ECM", 20, 100, 80),
    }
    allowed = st.multiselect(
        "Allowed hydrogels (optional)",
        ["GelMA", "fibrin", "silk_fibrin", "HA", "alginate", "gelatin_alginate", "collagen", "agarose", "PEG", "chitosan", "chitosan_HA", "cellulose_alginate"],
        default=["GelMA", "fibrin", "HA", "alginate"],
    )
    max_stiffness = st.slider("Max stiffness (kPa)", 10, 200, 50)
    if st.button("Propose candidate designs", type="primary"):
        constraints = {"stiffness_kpa_max": max_stiffness}
        if allowed:
            constraints["material_class"] = allowed
        ranked = inverse_design(model, targets=targets, constraints=constraints, top_k=5)
        st.success(f"Ranked {len(ranked)} candidate designs.")
        for _, row in ranked.iterrows():
            with st.expander(f"Candidate {int(row['rank'])}: {candidate_rationale(row)}", expanded=row["rank"] == 1):
                m1, m2, m3, m4 = st.columns(4)
                m1.metric("Viability", f"{row['pred_viability_pct']:.0f}", f"{row['pred_viability_pct_low']:.0f}–{row['pred_viability_pct_high']:.0f}")
                m2.metric("Proliferation", f"{row['pred_proliferation_score']:.0f}")
                m3.metric("Differentiation", f"{row['pred_differentiation_score']:.0f}")
                m4.metric("ECM", f"{row['pred_ecm_deposition_score']:.0f}")
                st.write(protocol_from_row(row))

with tab_next:
    st.markdown(
        "Bayesian-style experiment recommendation: sample the design space and pick conditions with high predicted performance **and** high information value (expected improvement + uncertainty)."
    )
    objective = st.selectbox(
        "Optimize for",
        TARGETS,
        format_func=lambda key: TARGET_LABELS[key],
        index=3,
    )
    n = st.slider("How many experiments to propose", 3, 8, 5)
    if st.button("Recommend next experiments", type="primary"):
        recs = recommend_experiments(model, objective=objective, n=n)
        st.dataframe(
            recs[
                [
                    "rank",
                    "material_class",
                    "stiffness_kpa",
                    "polymer_concentration_wt_pct",
                    "growth_factor",
                    "culture_time_days",
                    "acquisition",
                    "expected_improvement",
                    f"pred_{objective}",
                ]
            ],
            hide_index=True,
            use_container_width=True,
        )
        for _, row in recs.iterrows():
            st.markdown(f"**{int(row['rank'])}.** {recommendation_reason(row)}")
            st.caption(protocol_from_row(row))

with tab_data:
    n_lit = int((data["source"] == "literature").sum())
    n_sim = int((data["source"] == "simulated_literature_informed").sum())
    quality = json.loads(QUALITY_REPORT_PATH.read_text()) if QUALITY_REPORT_PATH.exists() else {}
    honest = json.loads(HONEST_METRICS_PATH.read_text()) if HONEST_METRICS_PATH.exists() else {}
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("SQLite papers", quality.get("n_amass_papers", "—"))
    c2.metric("Hand-curated studies", quality.get("n_hand_studies", "—"))
    c3.metric("Numeric viability (curated)", quality.get("n_numeric_viability", "—"))
    c4.metric("Extraction queue remaining", quality.get("n_extraction_queue", "—"))
    st.caption(
        "Papers are a library. The model only learns from curated numeric measurements. "
        "Simulator rows in the CSV below are a prior, not observations."
    )
    if honest:
        st.subheader("Honest metric (leave-one-paper-out viability)")
        d1, d2, d3 = st.columns(3)
        d1.metric("Dummy LOPO MAE", f"{honest['dummy_lopo']['mae']:.1f}" if "dummy_lopo" in honest else "—")
        d2.metric("Ridge LOPO MAE", f"{honest['ridge_lopo']['mae']:.1f}" if "ridge_lopo" in honest else "—")
        d3.metric("MVP pass", "yes" if honest.get("mvp_pass") else "not yet")
        st.caption(honest.get("pass_bar", {}).get("description", ""))
    if EXTRACTION_QUEUE_PATH.exists():
        queue = pd.read_csv(EXTRACTION_QUEUE_PATH)
        st.subheader("Next papers to extract")
        st.dataframe(queue.head(25), use_container_width=True, hide_index=True)
    if VIABILITY_EXPORT_PATH.exists():
        viability = pd.read_csv(VIABILITY_EXPORT_PATH)
        st.subheader("Training table — hand-curated live/dead %")
        st.caption("This is `v_model_viability`. Auto-promoted pmid* rows are excluded.")
        st.dataframe(viability, use_container_width=True, hide_index=True)
        st.download_button(
            "Download literature viability CSV",
            viability.to_csv(index=False),
            "literature_viability.csv",
            "text/csv",
            key="dl_viability",
        )
    if NATIVE_EXPORT_PATH.exists():
        native = pd.read_csv(NATIVE_EXPORT_PATH)
        st.subheader("All measurements (native units, includes inventory rows)")
        st.dataframe(native.head(80), use_container_width=True, hide_index=True)
    st.markdown("Mapped CSV used by the demo four-outcome model (includes simulator rows):")
    c1, c2, c3 = st.columns(3)
    c1.metric("CSV records", len(data))
    c2.metric("Literature-extracted", n_lit)
    c3.metric("Simulator-generated", n_sim)
    st.dataframe(data.head(50), use_container_width=True, hide_index=True)
    st.download_button("Download full CSV", data.to_csv(index=False), "hydrogel_chondrocyte_records.csv", "text/csv")
    left, right = st.columns(2)
    with left:
        counts = data.groupby("material_class").size().reset_index(name="n")
        fig = go.Figure(go.Bar(x=counts["material_class"], y=counts["n"], marker_color="#3ecfb2"))
        fig.update_layout(title="Records by hydrogel", paper_bgcolor="rgba(0,0,0,0)", font=dict(color="#e8eef7"), height=360)
        st.plotly_chart(fig, use_container_width=True)
    with right:
        lit = data[data["source"] == "literature"]
        fig = go.Figure(
            go.Scatter(
                x=lit["stiffness_kpa"],
                y=lit["ecm_deposition_score"],
                mode="markers",
                text=lit["material_class"] + " — " + lit["citation"].fillna(""),
                marker=dict(size=10, color="#f4b942"),
            )
        )
        fig.update_layout(
            title="Literature: stiffness vs ECM score",
            xaxis_title="kPa",
            yaxis_title="ECM score",
            paper_bgcolor="rgba(0,0,0,0)",
            font=dict(color="#e8eef7"),
            height=360,
        )
        st.plotly_chart(fig, use_container_width=True)

with tab_about:
    st.markdown(
        """
### What this prototype is testing

> Can a model of hydrogel–chondrocyte experiments change which experiment you run next?

That is the working thesis from the project brief. This MVP does **not** simulate a human joint.

**Chosen vertical:** cartilage / chondrocytes in hydrogels — the brief's easiest starting point,
with relatively consistent readouts (live/dead, DNA, sGAG, COL2A1).

**Pipeline**

1. Structured experimental records (literature + simulator)
2. Tabular ML (Ridge, Random Forest, XGBoost) with quantile uncertainty
3. Inverse design by constrained sampling
4. Next-experiment recommendation by expected improvement

**Do not over-interpret the numbers.** Many literature outcomes were mapped onto 0–100 scores
when papers reported qualitative histology or relative gene expression. The simulator is a
prior, not a replacement for wet-lab data. The number that matters is leave-one-paper-out
viability (`artifacts/honest_benchmark.json`), not simulated holdout R².

See `docs/ROADMAP.md` for the path from this table to a lab-changing product, and
`docs/LANDSCAPE.md` for competitors.
        """
    )
    if HONEST_METRICS_PATH.exists():
        st.subheader("Honest LOPO viability")
        st.json(json.loads(HONEST_METRICS_PATH.read_text()))
    holdout = model.metrics.get("xgboost_holdout", {})
    if holdout:
        st.subheader("Simulated-holdout metrics (not the product bar)")
        st.json(holdout)

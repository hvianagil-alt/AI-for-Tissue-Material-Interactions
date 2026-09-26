"""Viability lookup trained only on hand-curated published live/dead %."""

from __future__ import annotations

import json

import joblib
import numpy as np
import pandas as pd

from tissuelab.benchmark import FEATURES_CAT, FEATURES_NUM, PAPERS_NEEDED_TREES, leave_one_paper_out, load_viability
from tissuelab.db import connect
from tissuelab.paths import DB_PATH, HONEST_METRICS_PATH, LITERATURE_MODEL_PATH
from tissuelab.shrinkage import N0, N_LOCKED_HYPERPARAMETERS, PAPERS_NEEDED_BEGINNING, knob_deltas, shrinkage_estimate


def load_curated_viability(path=DB_PATH) -> pd.DataFrame:
    return load_viability(path)


def _material_mean_estimate(design: dict, frame: pd.DataFrame) -> tuple[float | None, str, int]:
    if frame.empty:
        return None, "empty", 0
    material = design.get("material_class")
    if material:
        subset = frame[frame["material_class"] == material]
        if not subset.empty:
            return float(subset["viability_pct"].mean()), "material_mean", int(len(subset))
    return float(frame["viability_pct"].mean()), "global_mean", int(len(frame))


def _lopo_cached(frame: pd.DataFrame) -> dict:
    if HONEST_METRICS_PATH.exists():
        try:
            report = json.loads(HONEST_METRICS_PATH.read_text())
        except json.JSONDecodeError:
            report = {}
        n_studies = int(frame["study_id"].nunique())
        stale_hgb = (
            report.get("deployed_estimator") == "hgb" and n_studies < PAPERS_NEEDED_TREES
        )
        fresh = (
            report.get("n_rows") == int(len(frame))
            and report.get("n_studies") == n_studies
            and "shrinkage_lopo" in report
            and "deployed_estimator" in report
            and not stale_hgb
        )
        if fresh:
            return report
    return leave_one_paper_out(frame)


def train_literature_viability(path=DB_PATH):
    frame = load_curated_viability(path)
    lopo = leave_one_paper_out(frame)
    material_means = (
        frame.groupby("material_class")["viability_pct"].mean().astype(float).to_dict()
        if not frame.empty
        else {}
    )
    payload = {
        "frame": frame,
        "pipeline": None,
        "lopo": lopo,
        "material_means": material_means,
        "global_mean": float(frame["viability_pct"].mean()) if not frame.empty else None,
        "deployed_estimator": lopo.get("deployed_estimator"),
        "features_num": FEATURES_NUM,
        "features_cat": FEATURES_CAT,
    }
    LITERATURE_MODEL_PATH.parent.mkdir(parents=True, exist_ok=True)
    joblib.dump(payload, LITERATURE_MODEL_PATH)
    HONEST_METRICS_PATH.write_text(json.dumps(lopo, indent=2))
    return payload


def load_literature_model():
    if LITERATURE_MODEL_PATH.exists():
        return joblib.load(LITERATURE_MODEL_PATH)
    return train_literature_viability()


def _query_from_design(design: dict) -> dict:
    kpa = design.get("stiffness_kpa")
    days = design.get("culture_time_days")
    return {
        "material_class": design.get("material_class"),
        "cell_type": design.get("cell_type"),
        "growth_factor": design.get("growth_factor") or "none",
        "stiffness_kpa": None if kpa in (None, "") else float(kpa),
        "culture_time_days": None if days in (None, "") else float(days),
        "culture_model": design.get("culture_model"),
        "chemical_modification": design.get("chemical_modification"),
        "architecture": design.get("architecture"),
    }


COMPETITOR = {
    "material_class": "GelMA",
    "stiffness_kpa": 25.0,
    "cell_type": "articular_chondrocyte",
    "growth_factor": "TGF_b3",
    "culture_time_days": 14,
}


def _coverage(frame: pd.DataFrame, material: str | None) -> dict:
    n_total = int(len(frame))
    n_kpa = int(frame["stiffness_kpa"].notna().sum()) if n_total else 0
    sub = frame[frame["material_class"] == material] if material else frame.iloc[0:0]
    stats = _material_stats(sub)
    return {
        "n_total": n_total,
        "n_studies": int(frame["study_id"].nunique()) if n_total else 0,
        "n_with_kpa": n_kpa,
        "pct_kpa_missing": round(100.0 * (1 - n_kpa / n_total), 0) if n_total else 100.0,
        "n_material": int(len(sub)),
        "n_material_with_kpa": int(sub["stiffness_kpa"].notna().sum()) if len(sub) else 0,
        "n_material_studies": int(sub["study_id"].nunique()) if len(sub) else 0,
        "material_mean": stats.get("mean"),
        "material_median": stats.get("median"),
        "material_sd": stats.get("sd"),
        "material_min": stats.get("min"),
        "material_max": stats.get("max"),
        "material_p10": stats.get("p10"),
    }


def _material_stats(sub: pd.DataFrame) -> dict:
    if sub is None or sub.empty:
        return {}
    values = sub["viability_pct"].astype(float)
    out = {
        "mean": round(float(values.mean()), 1),
        "median": round(float(values.median()), 1),
        "min": round(float(values.min()), 1),
        "max": round(float(values.max()), 1),
        "p10": round(float(np.percentile(values, 10)), 1),
    }
    if len(values) > 1:
        out["sd"] = round(float(values.std(ddof=1)), 1)
    return out


def _variance_split(frame: pd.DataFrame) -> dict:
    if frame.empty or frame["study_id"].nunique() < 2:
        return {"between_paper_sd": None, "within_paper_sd_median": None}
    paper_means = frame.groupby("study_id")["viability_pct"].mean()
    within = frame.groupby("study_id")["viability_pct"].std(ddof=1)
    return {
        "between_paper_sd": round(float(paper_means.std(ddof=1)), 1),
        "within_paper_sd_median": None
        if within.dropna().empty
        else round(float(within.median()), 1),
    }


def _chart_points(frame: pd.DataFrame, weights: np.ndarray, material: str | None) -> list[dict]:
    out = []
    w = weights if weights is not None and len(weights) == len(frame) else np.ones(len(frame))
    for i, row in enumerate(frame.itertuples(index=False)):
        kpa = getattr(row, "stiffness_kpa", None)
        citation = getattr(row, "citation", None)
        out.append(
            {
                "kpa": None if kpa is None or pd.isna(kpa) else float(kpa),
                "viability_pct": float(row.viability_pct),
                "material_class": row.material_class,
                "same_material": bool(material and row.material_class == material),
                "weight": round(float(w[i]), 3),
                "study_id": row.study_id,
                "citation": None if citation is None or pd.isna(citation) else str(citation),
            }
        )
    return out


def _adaptive_band(
    mae: float,
    coverage: dict,
    query: dict,
    n_eff_same: float,
    global_sd: float | None,
) -> tuple[float, list[str]]:
    """Widen ±LOPO MAE when this gel is thin, heterogeneous, or borrowing kPa.

    Never narrower than LOPO MAE: that is the honest error for a new paper.
    """
    reasons: list[str] = ["floor = leave-one-paper-out MAE"]
    half = float(mae)
    n_sup = int(coverage.get("n_material") or 0)
    n_kpa = int(coverage.get("n_material_with_kpa") or 0)
    material_sd = coverage.get("material_sd")
    gsd = float(global_sd) if global_sd else 23.0
    if material_sd is not None and n_sup >= 3 and gsd > 0:
        het = (float(material_sd) / gsd) ** 2
        if het > 1:
            half *= float(np.sqrt(1.0 + 0.5 * (het - 1.0)))
            reasons.append("this gel is more heterogeneous than the table")
    half *= float(np.sqrt(1.0 + 1.0 / max(n_sup, 1)))
    if n_sup <= 1:
        reasons.append("very few extracted conditions of this gel")
    kpa = query.get("stiffness_kpa")
    if kpa not in (None, "") and n_kpa == 0:
        half *= 1.2
        reasons.append("requested stiffness is borrowed from other materials")
    if n_eff_same is not None and float(n_eff_same) < 2:
        reasons.append("effective n on this gel < 2")
    half = float(np.clip(half, mae, 40.0))
    return half, reasons


def _trust(coverage: dict, n_eff_same: float) -> dict:
    n = int(coverage.get("n_material") or 0)
    n_kpa = int(coverage.get("n_material_with_kpa") or 0)
    sd = coverage.get("material_sd")
    if n == 0:
        return {
            "level": "no_data",
            "label": "No evidence for this gel",
            "fill": 0,
            "why": "No extracted live/dead for this material class.",
        }
    if n == 1 or n_eff_same < 2:
        extra = " If stiffness moves, it is borrowed from other gels." if n_kpa == 0 else ""
        return {
            "level": "weak",
            "label": "Weak evidence",
            "fill": 1,
            "why": f"Only {n} extracted condition of this gel.{extra}",
        }
    if sd is not None and float(sd) >= 20:
        return {
            "level": "heterogeneous",
            "label": "Heterogeneous evidence",
            "fill": 2,
            "why": f"{n} conditions, but live/dead on this gel spans ~{sd:.0f} points. Look at the published minimum, not just the mean.",
        }
    if n >= 4 and n_kpa >= 2:
        return {
            "level": "useful",
            "label": "Useful evidence (still small)",
            "fill": 3,
            "why": f"{n} conditions of this gel, {n_kpa} with kPa. Good for comparing papers, not a substitute for the flask.",
        }
    return {
        "level": "weak",
        "label": "Limited evidence",
        "fill": 1,
        "why": f"{n} extracted conditions; {n_kpa} with kPa.",
    }


def _verdict(
    design: dict,
    mean: float | None,
    coverage: dict,
    competitor_mean: float | None,
    band: float | None,
    trust: dict,
) -> str:
    material = design.get("material_class") or "this gel"
    kpa = design.get("stiffness_kpa")
    kpa_s = f" ~{float(kpa):.0f} kPa" if kpa not in (None, "") else ""
    n = coverage.get("n_material") or 0
    n_kpa = coverage.get("n_material_with_kpa") or 0
    if mean is None:
        return "No extracted live/dead yet to train a number."
    if n == 0:
        return (
            f"No extracted live/dead for {material}. The value shown is borrowed from other gels — "
            "do not use it to pick the next encapsulation."
        )
    floor = coverage.get("material_min")
    floor_s = f" The worst extracted live/dead on this gel is {floor:.0f}%." if floor is not None else ""
    band_s = f" (±{band:.0f} points; floor = error between papers)" if band else ""
    vs = ""
    if competitor_mean is not None:
        diff = mean - competitor_mean
        side = "above" if diff > 0 else "below" if diff < 0 else "level with"
        vs = (
            f" Versus GelMA 25 kPa + TGF-β3 ({competitor_mean:.0f}%), "
            f"this sits {abs(diff):.0f} points {side}."
        )
    borrow = ""
    if kpa not in (None, "") and n_kpa == 0:
        borrow = " The stiffness slider is borrowing kPa from other materials."
    n_qual = coverage.get("n_table_material_qual") or 0
    extra_s = ""
    if n_qual:
        extra_s = (
            f" The table also has {n_qual} extracted floors/‘high’ rows of this gel "
            "(with kPa when the paper published it) that are not in this number."
        )
    return (
        f"{trust.get('label')}. For {material}{kpa_s}, the literature points to {mean:.0f}% live/dead{band_s}, "
        f"from {n} extracted numeric conditions ({n_kpa} with kPa).{vs}{borrow}{floor_s}{extra_s} "
        "This does not replace your next flask."
    )


def _alternatives(query: dict, frame: pd.DataFrame) -> list[dict]:
    specs = [
        ("you", query, "Your protocol"),
        ("competitor", COMPETITOR, "GelMA 25 kPa + TGF-β3"),
    ]
    if (query.get("growth_factor") or "none") == "none":
        specs.append(("plus_tgf", {**query, "growth_factor": "TGF_b3"}, "Same gel + TGF-β3"))
    else:
        specs.append(("no_tgf", {**query, "growth_factor": "none"}, "Same gel without TGF"))
    specs.append(("soft", {**query, "stiffness_kpa": 2.0}, "Same gel at 2 kPa (soft)"))
    specs.append(("stiff", {**query, "stiffness_kpa": 40.0}, "Same gel at 40 kPa (stiff)"))
    seen = set()
    out = []
    for key, spec, label in specs:
        fingerprint = (
            spec.get("material_class"),
            spec.get("stiffness_kpa"),
            spec.get("cell_type"),
            spec.get("growth_factor"),
            spec.get("culture_time_days"),
        )
        if fingerprint in seen:
            continue
        seen.add(fingerprint)
        est = shrinkage_estimate(spec, frame)
        if est["mean"] is None:
            continue
        out.append(
            {
                "id": key,
                "label": label,
                "mean": round(float(est["mean"]), 1),
                "material_class": spec.get("material_class"),
                "stiffness_kpa": spec.get("stiffness_kpa"),
                "growth_factor": spec.get("growth_factor"),
            }
        )
    return out


def predict_literature_viability(design: dict) -> dict:
    """Empirical-Bayes point estimate. Does not need the XGBoost joblib."""
    frame = load_curated_viability()
    lopo = _lopo_cached(frame)
    query = _query_from_design(design)
    est = shrinkage_estimate(query, frame)
    mean = est["mean"]
    deployed_lopo = lopo.get("deployed_lopo") or {}
    dummy_lopo = lopo.get("dummy_lopo") or {}
    ridge_lopo = lopo.get("ridge_lopo") or {}
    material_lopo = lopo.get("material_mean_lopo") or {}
    shrinkage_lopo = lopo.get("shrinkage_lopo") or {}
    hgb_lopo = lopo.get("hgb_lopo") or {}
    mae = (shrinkage_lopo.get("mae") if shrinkage_lopo else None) or deployed_lopo.get("mae") or dummy_lopo.get("mae")
    coverage = _coverage(frame, design.get("material_class"))
    n_eff_same = float(est.get("n_eff_same") or 0.0)
    global_sd = lopo.get("viability_std")
    if mae is None:
        band, interval_reasons = 12.0, ["MAE unavailable — provisional band"]
    else:
        band, interval_reasons = _adaptive_band(float(mae), coverage, query, n_eff_same, global_sd)
    low = None if mean is None else float(np.clip(mean - band, 0, 100))
    high = None if mean is None else float(np.clip(mean + band, 0, 100))
    similar = similar_published(design, k=5, weights=est.get("weights"), frame=frame)
    evidence_rows = list_viability_evidence()
    also_extracted = _also_extracted(design.get("material_class"), evidence_rows, similar)
    table_cov = _table_coverage(design.get("material_class"), evidence_rows)
    coverage = {**coverage, **table_cov}
    competitor = shrinkage_estimate(COMPETITOR, frame)
    competitor_mean = None if competitor["mean"] is None else round(float(competitor["mean"]), 1)
    chart_points = _chart_points(frame, est.get("weights"), design.get("material_class"))
    trust = _trust(coverage, n_eff_same)
    verdict = _verdict(
        design,
        None if mean is None else float(mean),
        coverage,
        competitor_mean,
        band,
        trust,
    )
    dummy_mae = dummy_lopo.get("mae")
    target_mae = None if dummy_mae is None else round(float(dummy_mae) * 0.85, 2)
    next_read = _pick_next_read(design, similar, also_extracted)
    n_priors = (
        int(frame.groupby(["material_class", "cell_type"]).ngroups) if not frame.empty else 0
    )
    return {
        "mean": None if mean is None else round(mean, 1),
        "low": None if low is None else round(low, 1),
        "high": None if high is None else round(high, 1),
        "local": None if est["local"] is None else round(est["local"], 1),
        "prior": None if est["prior"] is None else round(est["prior"], 1),
        "n_eff": round(float(est["n_eff"]), 1),
        "n_eff_same": round(n_eff_same, 1),
        "local_weight": round(float(est["local_weight"]), 3),
        "prior_strength": N0,
        "estimator": est["estimator"],
        "n_support": est["n_support"],
        "interval_is_lopo_mae": False,
        "interval_floor_is_lopo_mae": True,
        "interval_half": round(float(band), 1),
        "interval_reasons": interval_reasons,
        "knob_deltas": knob_deltas(query, frame),
        "coverage": coverage,
        "trust": trust,
        "material_counts": (
            {str(k): int(v) for k, v in frame.groupby("material_class").size().items()}
            if not frame.empty
            else {}
        ),
        "chart_points": chart_points,
        "also_extracted": also_extracted,
        "competitor": {
            "label": "GelMA 25 kPa + TGF-β3",
            "mean": competitor_mean,
            "stiffness_kpa": COMPETITOR["stiffness_kpa"],
            "delta": None if mean is None or competitor_mean is None else round(float(mean) - competitor_mean, 1),
        },
        "alternatives": _alternatives(query, frame),
        "variance_split": _variance_split(frame),
        "next_read": next_read,
        "verdict": verdict,
        "lopo": {
            "n_studies": lopo.get("n_studies"),
            "n_rows": lopo.get("n_rows"),
            "dummy_mae": dummy_lopo.get("mae"),
            "ridge_mae": ridge_lopo.get("mae"),
            "ridge_r2": ridge_lopo.get("r2"),
            "material_mean_mae": material_lopo.get("mae"),
            "material_mean_r2": material_lopo.get("r2"),
            "shrinkage_mae": shrinkage_lopo.get("mae"),
            "shrinkage_r2": shrinkage_lopo.get("r2"),
            "hgb_mae": hgb_lopo.get("mae"),
            "hgb_r2": hgb_lopo.get("r2"),
            "hgb_beats_dummy": lopo.get("hgb_beats_dummy"),
            "deployed_estimator": lopo.get("deployed_estimator"),
            "deployed_mae": deployed_lopo.get("mae"),
            "deployed_r2": deployed_lopo.get("r2"),
            "beats_dummy": lopo.get("beats_dummy"),
            "ridge_beats_dummy": lopo.get("ridge_beats_dummy"),
            "mvp_pass": lopo.get("mvp_pass"),
            "target_mae": target_mae,
            "viability_std": global_sd,
        },
        "served_locked_hyperparameters": N_LOCKED_HYPERPARAMETERS,
        "served_empirical_priors": n_priors,
        "served_parameters": N_LOCKED_HYPERPARAMETERS + n_priors,
        "papers_needed_beginning": PAPERS_NEEDED_BEGINNING,
        "similar": similar,
        "notes": _notes(
            lopo,
            estimator=est["estimator"],
            n_support=est["n_support"],
            material=design.get("material_class"),
            n_eff=est["n_eff"],
            n_eff_same=n_eff_same,
            local=est["local"],
            prior=est["prior"],
            served_parameters=N_LOCKED_HYPERPARAMETERS + n_priors,
            n_locked=N_LOCKED_HYPERPARAMETERS,
            n_priors=n_priors,
        ),
    }


def _notes(
    lopo: dict,
    estimator: str | None = None,
    n_support: int | None = None,
    material: str | None = None,
    n_eff: float | None = None,
    n_eff_same: float | None = None,
    local: float | None = None,
    prior: float | None = None,
    served_parameters: int | None = None,
    n_locked: int | None = None,
    n_priors: int | None = None,
) -> list[str]:
    notes = [
        "Trained only on hand-curated live/dead (no pmid* auto-promote, no simulator).",
        "The estimate is empirical Bayes: a kernel over published conditions, shrunk toward the material-class mean. Not a neural net.",
        "The band is never narrower than leave-one-paper-out MAE; it widens if the gel is thin, heterogeneous, or borrowing kPa. Not a biological confidence interval.",
        "We do not Huber/median away 5% live/dead: those are gels that kill cells, not noise.",
    ]
    if served_parameters is not None:
        locked = n_locked if n_locked is not None else N_LOCKED_HYPERPARAMETERS
        priors = n_priors if n_priors is not None else max(0, int(served_parameters) - int(locked))
        n_studies = lopo.get("n_studies") or 0
        notes.append(
            f"Served model has {served_parameters} parameters "
            f"({locked} locked kernel hyperparameters + {priors} gel×cell empirical means). "
            f"Beginning target is {PAPERS_NEEDED_BEGINNING} independent live/dead papers "
            f"(today {n_studies}). 40 is only the tree report gate, not a working Ridge."
        )
    if estimator == "shrinkage_global_prior" and material:
        notes.append(
            f"No published live/dead for {material} — the prior is the global mean, pulled by similar gels."
        )
    elif n_support and material:
        notes.append(f"Material prior from {n_support} extracted {material} rows.")
    if local is not None and prior is not None and n_eff is not None:
        same_s = f"{n_eff_same:.1f}" if n_eff_same is not None else "—"
        notes.append(
            f"Local mean {local:.1f}% shrunk toward prior {prior:.1f}% "
            f"(effective n on this gel={same_s}, n0={N0:.0f}). "
            f"Full-kernel n_eff ({n_eff:.1f}) counts other materials and is not this gel's sample size."
        )
    if not lopo.get("beats_dummy"):
        notes.append(
            "Does not yet beat a dummy mean — use the extracted papers, not the point estimate, to pick a gel."
        )
    elif not lopo.get("mvp_pass"):
        notes.append(
            "Shrinkage beats dummy on LOPO MAE but has not met the MVP bar "
            "(15% better, R²>0, n_studies≥15). Use neighbouring papers to choose the next gel."
        )
    else:
        notes.append("Current LOPO meets the viability MVP bar.")
    return notes


def _table_coverage(material: str | None, rows: list[dict]) -> dict:
    sub = [r for r in rows if r.get("material_class") == material] if material else []
    n_qual = sum(1 for r in sub if r.get("viability_pct") is None)
    n_kpa = sum(1 for r in sub if r.get("stiffness_kpa") is not None)
    return {
        "n_table_material": int(len(sub)),
        "n_table_material_qual": int(n_qual),
        "n_table_material_with_kpa": int(n_kpa),
    }


def _also_extracted(material: str | None, rows: list[dict], similar: list[dict]) -> list[dict]:
    """Hand-extracted rows of this gel that are not in the numeric lookup list."""
    if not material:
        return []
    seen = {r.get("experiment_id") for r in similar}
    out = []
    for row in rows:
        if row.get("material_class") != material:
            continue
        if row.get("experiment_id") in seen:
            continue
        out.append(row)

    def sort_key(row: dict):
        has_kpa = 0 if row.get("stiffness_kpa") is not None else 1
        is_qual = 0 if row.get("viability_pct") is None else 1
        return (has_kpa, is_qual, -(row.get("year") or 0))

    out.sort(key=sort_key)
    return out[:12]


def _pick_next_read(design: dict, similar: list[dict], also_extracted: list[dict]) -> dict | None:
    """Prefer the same gel with a published kPa — even if viability is only a floor."""
    want = design.get("material_class")
    query_kpa = design.get("stiffness_kpa")

    def dist(row: dict) -> float:
        rk = row.get("stiffness_kpa")
        if query_kpa in (None, "") or rk is None:
            return 1e9
        return abs(float(rk) - float(query_kpa))

    def payload(row: dict) -> dict | None:
        doi = row.get("doi")
        if not doi:
            return None
        return {
            "citation": row.get("citation") or row.get("study_id"),
            "doi": doi,
            "viability_pct": row.get("viability_pct"),
            "qualitative_label": row.get("qualitative_label"),
            "stiffness_kpa": row.get("stiffness_kpa"),
        }

    same_num = [r for r in similar if r.get("material_class") == want]
    num_kpa = [r for r in same_num if r.get("stiffness_kpa") is not None and r.get("doi")]
    if num_kpa:
        return payload(min(num_kpa, key=dist))
    qual_kpa = [r for r in also_extracted if r.get("stiffness_kpa") is not None]
    if qual_kpa:
        picked = payload(min(qual_kpa, key=dist))
        if picked:
            return picked
    for row in same_num:
        picked = payload(row)
        if picked:
            return picked
    for row in similar:
        picked = payload(row)
        if picked:
            return picked
    return None


def similar_published(design: dict, k: int = 5, weights: np.ndarray | None = None, frame: pd.DataFrame | None = None) -> list[dict]:
    if frame is None:
        conn = connect(DB_PATH)
        frame = pd.read_sql_query(
            """
            SELECT experiment_id, study_id, citation, doi, material_class, stiffness_kpa,
                   cell_type, growth_factor, culture_time_days, viability_pct
            FROM v_model_viability
            """,
            conn,
        )
        conn.close()
    if frame.empty:
        return []
    query = _query_from_design(design)
    if weights is None or len(weights) != len(frame):
        weights = shrinkage_estimate(query, frame)["weights"]
    want = str(query.get("material_class") or "")
    mats = frame["material_class"].astype(str).to_numpy()
    ranked = sorted(
        range(len(frame)),
        key=lambda i: (0 if mats[i] == want else 1, -float(weights[i])),
    )
    out = []
    for pos in ranked[:k]:
        row = frame.iloc[int(pos)]
        out.append(
            {
                "experiment_id": row["experiment_id"],
                "study_id": row["study_id"],
                "citation": None if pd.isna(row.get("citation")) else row.get("citation"),
                "doi": None if pd.isna(row.get("doi")) else row.get("doi"),
                "material_class": row["material_class"],
                "cell_type": None if pd.isna(row.get("cell_type")) else row.get("cell_type"),
                "stiffness_kpa": None if pd.isna(row["stiffness_kpa"]) else float(row["stiffness_kpa"]),
                "viability_pct": float(row["viability_pct"]),
                "growth_factor": None if pd.isna(row.get("growth_factor")) else row.get("growth_factor"),
                "culture_time_days": None
                if pd.isna(row["culture_time_days"])
                else float(row["culture_time_days"]),
                "match_score": round(float(weights[int(pos)]), 3),
            }
        )
    return out


def list_viability_evidence(path=DB_PATH) -> list[dict]:
    """Hand-curated viability rows for the table. Includes floors/qualitative; excludes pmid*."""
    conn = connect(path)
    frame = pd.read_sql_query(
        """
        SELECT e.experiment_id, e.study_id, s.citation, s.doi, s.year,
               e.material_class, e.material_detail, e.stiffness_kpa, e.cell_type, e.species,
               e.growth_factor, e.culture_time_days, e.culture_model,
               e.polymer_concentration_wt_pct, e.crosslinking,
               e.cell_density_million_per_ml, e.architecture, e.application,
               e.chemical_modification,
               m.value AS viability_pct, m.value_sd, m.qualitative_label,
               m.evidence, m.notes
        FROM experiments e
        JOIN studies s ON s.study_id = e.study_id
        JOIN measurements m ON m.experiment_id = e.experiment_id
        WHERE m.assay = 'viability_pct'
          AND e.study_id NOT LIKE 'pmid%'
        ORDER BY COALESCE(s.year, 0) DESC, e.material_class, e.experiment_id
        """,
        conn,
    )
    conn.close()
    rows = []
    for row in frame.itertuples(index=False):
        viab = getattr(row, "viability_pct", None)
        kpa = getattr(row, "stiffness_kpa", None)
        days = getattr(row, "culture_time_days", None)
        year = getattr(row, "year", None)
        rows.append(
            {
                "experiment_id": row.experiment_id,
                "study_id": row.study_id,
                "citation": None if pd.isna(getattr(row, "citation", None)) else row.citation,
                "doi": None if pd.isna(getattr(row, "doi", None)) else row.doi,
                "year": None if year is None or pd.isna(year) else int(year),
                "material_class": row.material_class,
                "material_detail": None
                if pd.isna(getattr(row, "material_detail", None))
                else row.material_detail,
                "stiffness_kpa": None if kpa is None or pd.isna(kpa) else float(kpa),
                "cell_type": None if pd.isna(getattr(row, "cell_type", None)) else row.cell_type,
                "species": None if pd.isna(getattr(row, "species", None)) else row.species,
                "growth_factor": None if pd.isna(getattr(row, "growth_factor", None)) else row.growth_factor,
                "culture_time_days": None if days is None or pd.isna(days) else float(days),
                "culture_model": None if pd.isna(getattr(row, "culture_model", None)) else row.culture_model,
                "polymer_concentration_wt_pct": None
                if pd.isna(getattr(row, "polymer_concentration_wt_pct", None))
                else float(row.polymer_concentration_wt_pct),
                "crosslinking": None
                if pd.isna(getattr(row, "crosslinking", None))
                else row.crosslinking,
                "cell_density_million_per_ml": None
                if pd.isna(getattr(row, "cell_density_million_per_ml", None))
                else float(row.cell_density_million_per_ml),
                "architecture": None
                if pd.isna(getattr(row, "architecture", None))
                else row.architecture,
                "application": None
                if pd.isna(getattr(row, "application", None))
                else row.application,
                "chemical_modification": None
                if pd.isna(getattr(row, "chemical_modification", None))
                else row.chemical_modification,
                "viability_pct": None if viab is None or pd.isna(viab) else float(viab),
                "viability_sd": None
                if pd.isna(getattr(row, "value_sd", None))
                else float(row.value_sd),
                "qualitative_label": None
                if pd.isna(getattr(row, "qualitative_label", None))
                else row.qualitative_label,
                "evidence": None if pd.isna(getattr(row, "evidence", None)) else row.evidence,
                "notes": None if pd.isna(getattr(row, "notes", None)) else row.notes,
            }
        )
    return rows

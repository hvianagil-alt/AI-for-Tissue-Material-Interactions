"""End-to-end: harvest → uniformize → ingest → load → benchmark.

Amass runs only if AMASS_API_KEY is set. Europe PMC always runs.
"""

from __future__ import annotations

import json
import traceback

from tissuelab.paths import DB_PATH


def _step(name: str, fn):
    print(f"== {name} ==", flush=True)
    try:
        result = fn()
        if isinstance(result, dict):
            slim = {k: v for k, v in result.items() if k not in {"studies", "experiments", "papers_per_year"}}
            print(json.dumps(slim, indent=2, default=str)[:4000], flush=True)
        return result
    except SystemExit as exc:
        print(f"{name} skipped: {exc}", flush=True)
        return {"status": "skipped", "reason": str(exc)}
    except Exception as exc:
        traceback.print_exc()
        print(f"{name} failed: {exc}", flush=True)
        return {"status": "failed", "reason": str(exc)}


def run() -> dict:
    from tissuelab.analyze_papers import run as analyze
    from tissuelab.benchmark import run as bench
    from tissuelab.europepmc import harvest as epmc
    from tissuelab.harvest_amass import run as amass
    from tissuelab.ingest_literature import ingest
    from tissuelab.load_database import load
    from tissuelab.rank_papers import rank
    from tissuelab.teach_model import run_lesson
    from tissuelab.training_pack import run as pack

    out = {}
    out["amass"] = _step("amass harvest", amass)
    out["europepmc"] = _step("europepmc harvest", epmc)
    out["analyze"] = _step("uniformize papers", analyze)
    out["ingest"] = _step("fulltext ingest", lambda: ingest(DB_PATH, fetch=True))
    out["load"] = _step("rebuild curated database", load)
    out["analyze_after_load"] = _step("re-uniformize after load", analyze)
    out["rank"] = _step("rank extraction queue", rank)
    out["training_pack"] = _step("export training pack", pack)
    out["benchmark"] = _step("leave-one-paper-out", bench)
    out["lesson"] = _step("training lesson", lambda: run_lesson(verbose=True))
    return out


def main() -> None:
    report = run()
    print("== pipeline done ==", flush=True)
    bench = report.get("benchmark") or {}
    print(
        json.dumps(
            {
                "n_papers": (report.get("load") or {}).get("n_amass_papers"),
                "n_analyses": (report.get("analyze_after_load") or {}).get("n_analyzed"),
                "n_training_relevant": (report.get("analyze_after_load") or {}).get("n_training_relevant"),
                "n_numeric_viability": (report.get("load") or {}).get("n_numeric_viability"),
                "n_hand_viability_studies": (report.get("load") or {}).get("n_hand_viability_studies"),
                "n_gold": (report.get("training_pack") or {}).get("n_gold_rows"),
                "n_papers_tagged": (report.get("training_pack") or {}).get("n_papers_tagged"),
                "deployed": bench.get("deployed_estimator"),
                "shrinkage_mae": (bench.get("shrinkage_lopo") or {}).get("mae"),
                "dummy_mae": (bench.get("dummy_lopo") or {}).get("mae"),
                "mvp_pass": bench.get("mvp_pass"),
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    main()

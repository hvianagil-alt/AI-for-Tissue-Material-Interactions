"""Beginner lesson: train and evaluate a viability model on the real table.

This is the file to run if you have never trained a model. It uses only the
hand-curated live/dead rows (v_model_viability). It does not change the
estimator the app serves.

    python3 -m tissuelab.teach_model
"""

from __future__ import annotations

import json

import numpy as np
import pandas as pd
from sklearn.linear_model import Ridge
from sklearn.metrics import mean_absolute_error, r2_score
from sklearn.model_selection import LeaveOneGroupOut, train_test_split

from tissuelab.benchmark import (
    FEATURES_CAT,
    FEATURES_NUM,
    PAPERS_NEEDED_TREES,
    _pipe,
    _scores,
    leave_one_paper_out,
    load_viability,
)
from tissuelab.paths import ARTIFACTS_DIR
from tissuelab.shrinkage import (
    N_LOCKED_HYPERPARAMETERS,
    PAPERS_NEEDED_BEGINNING,
    shrinkage_estimate,
)

TEACH_METRICS_PATH = ARTIFACTS_DIR / "teach_model.json"

# Rule of thumb: independent papers per non-redundant feature before a
# flexible model (Ridge / trees) can beat a dummy under LOPO.
PAPERS_PER_FEATURE = 10
STARTER_FEATURES = FEATURES_NUM + FEATURES_CAT + ["growth_factor", "culture_model"]


def _print(text: str, *, verbose: bool) -> None:
    if verbose:
        print(text)


def _banner(title: str, verbose: bool) -> None:
    _print("\n" + "=" * 72, verbose=verbose)
    _print(title, verbose=verbose)
    _print("=" * 72, verbose=verbose)


def _mae_r2(y_true, y_pred) -> dict:
    return {
        "mae": float(mean_absolute_error(y_true, y_pred)),
        "r2": float(r2_score(y_true, y_pred)),
    }


def random_split_ridge(frame: pd.DataFrame, seed: int = 0) -> dict:
    """The Afflerbach notebook split. Optimistic here because a paper can leak."""
    y = frame["viability_pct"].astype(float)
    x = frame[FEATURES_NUM + FEATURES_CAT]
    x_train, x_test, y_train, y_test = train_test_split(x, y, test_size=0.2, random_state=seed)
    model = _pipe(Ridge(alpha=1.0))
    model.fit(x_train, y_train)
    pred = model.predict(x_test)
    scores = _mae_r2(y_test, pred)
    train_pred = model.predict(x_train)
    scores["train_mae"] = float(mean_absolute_error(y_train, train_pred))
    scores["n_train"] = int(len(x_train))
    scores["n_test"] = int(len(x_test))
    scores["test_papers"] = sorted(frame.loc[x_test.index, "study_id"].unique().tolist())
    return scores


def ridge_lopo_manual(frame: pd.DataFrame) -> dict:
    """Same Ridge, but each test fold is one whole paper. This is training."""
    y = frame["viability_pct"].astype(float).to_numpy()
    x = frame[FEATURES_NUM + FEATURES_CAT]
    groups = frame["study_id"].to_numpy()
    logo = LeaveOneGroupOut()
    pred = np.zeros(len(frame), dtype=float)
    n_coef = None
    for train_idx, test_idx in logo.split(x, y, groups):
        model = _pipe(Ridge(alpha=1.0))
        model.fit(x.iloc[train_idx], y[train_idx])
        pred[test_idx] = model.predict(x.iloc[test_idx])
        if n_coef is None:
            ridge = model.named_steps["model"]
            n_coef = int(np.size(ridge.coef_))
    scores = _scores(pd.Series(y), pred)
    scores["n_coefficients"] = n_coef
    return scores


def data_budget(frame: pd.DataFrame) -> dict:
    n_rows = int(len(frame))
    n_studies = int(frame["study_id"].nunique())
    n_materials = int(frame["material_class"].nunique())
    n_cells = int(frame["cell_type"].nunique())
    n_kpa = int(frame["stiffness_kpa"].notna().sum())
    rows_per_paper = n_rows / max(n_studies, 1)
    # Dummy has 1 parameter. Material means ~ n_materials. Ridge one-hot explodes.
    dummy_params = 1
    material_params = n_materials
    ridge_params = n_materials + n_cells + len(FEATURES_NUM)
    n_priors = int(frame.groupby(["material_class", "cell_type"]).ngroups) if n_rows else 0
    served_params = N_LOCKED_HYPERPARAMETERS + n_priors
    want_ridge = PAPERS_PER_FEATURE * len(STARTER_FEATURES)
    want_mixed = 25
    want_trees = PAPERS_NEEDED_TREES
    want_beginning = PAPERS_NEEDED_BEGINNING
    return {
        "n_rows": n_rows,
        "n_studies": n_studies,
        "n_materials": n_materials,
        "n_cell_types": n_cells,
        "n_with_kpa": n_kpa,
        "rows_per_paper": round(rows_per_paper, 2),
        "dummy_parameters": dummy_params,
        "material_mean_parameters": material_params,
        "ridge_parameters_guess": ridge_params,
        "served_locked_hyperparameters": N_LOCKED_HYPERPARAMETERS,
        "served_empirical_priors": n_priors,
        "served_parameters": served_params,
        "starter_feature_count": len(STARTER_FEATURES),
        "papers_needed_ridge": want_ridge,
        "papers_needed_mixed": want_mixed,
        "papers_needed_trees": want_trees,
        "papers_needed_beginning": want_beginning,
        "have_enough_for_dummy": n_studies >= 3,
        "have_enough_for_mixed": n_studies >= want_mixed,
        "have_enough_for_ridge": n_studies >= want_ridge,
        "have_enough_for_trees": n_studies >= want_trees,
        "have_enough_for_beginning": n_studies >= want_beginning,
        "what_to_add_first": "studies",
    }


def predict_one_gel(frame: pd.DataFrame, query: dict | None = None) -> dict:
    query = query or {
        "material_class": "fibrin",
        "cell_type": "articular_chondrocyte",
        "growth_factor": "TGF_b3",
        "stiffness_kpa": 5.0,
        "culture_time_days": 21.0,
    }
    est = shrinkage_estimate(query, frame)
    return {
        "query": query,
        "predicted_viability_pct": None if est["mean"] is None else round(float(est["mean"]), 1),
        "material_prior": None if est["prior"] is None else round(float(est["prior"]), 1),
        "local_kernel": None if est["local"] is None else round(float(est["local"]), 1),
        "n_eff_same_material": round(float(est["n_eff_same"]), 2),
        "estimator": est["estimator"],
    }


def run_lesson(*, verbose: bool = True) -> dict:
    _banner("1. O que é um modelo", verbose)
    _print(
        "Um modelo é uma função: gel + células + kPa + TGF + dias  →  viabilidade %.\n"
        "Treinar é ajustar essa função aos números que já foram medidos nos papers.\n"
        "Em Python isso são duas linhas:\n"
        "    model.fit(X_train, y_train)\n"
        "    pred = model.predict(X_test)\n"
        "X = colunas que o PI controla.  y = live/dead % publicado.\n"
        "O que a app serve hoje NÃO é uma rede neural. É shrinkage (média local\n"
        "puxada para a média do gel). Este script mostra os dois: Ridge.fit e shrinkage.",
        verbose=verbose,
    )

    frame = load_viability()
    if frame.empty:
        raise RuntimeError("v_model_viability is empty. Run python3 -m tissuelab.load_database")

    budget = data_budget(frame)
    _banner("2. Os teus dados (não um tutorial inventado)", verbose)
    _print(
        f"  linhas (condições)     {budget['n_rows']}\n"
        f"  papers (estudos)       {budget['n_studies']}   ← este é o n do modelo\n"
        f"  famílias de gel        {budget['n_materials']}\n"
        f"  tipos de célula        {budget['n_cell_types']}\n"
        f"  linhas com kPa         {budget['n_with_kpa']}\n"
        f"  condições por paper    {budget['rows_per_paper']}\n"
        f"  y = viability_pct      média {frame['viability_pct'].mean():.1f}  "
        f"desvio {frame['viability_pct'].std(ddof=1):.1f}",
        verbose=verbose,
    )
    _print("  papers: " + ", ".join(sorted(frame["study_id"].unique())), verbose=verbose)

    _banner("3. Treino errado vs treino certo", verbose)
    random_scores = random_split_ridge(frame)
    ridge_lopo = ridge_lopo_manual(frame)
    _print(
        "Ridge = uma recta com muitas colunas (gel em one-hot, kPa, wt%, dias).\n"
        "fit() escolhe os coeficientes para o treino ficar próximo de y.\n\n"
        f"  ERRADO  split aleatório 80/20   MAE teste = {random_scores['mae']:.1f}   "
        f"(treino {random_scores['train_mae']:.1f})\n"
        f"          papers no teste: {', '.join(random_scores['test_papers'])}\n"
        "          Um paper pode ter 5 linhas no treino e 1 no teste → o modelo\n"
        "          já viu aquele laboratório. O MAE fica optimista.\n\n"
        f"  CERTO   leave-one-paper-out     MAE = {ridge_lopo['mae']:.1f}   R² = {ridge_lopo['r2']:.3f}\n"
        f"          coeficientes ≈ {ridge_lopo.get('n_coefficients')}  para  "
        f"{budget['n_studies']} papers. Demasiados parâmetros.\n"
        "          sklearn: LeaveOneGroupOut().split(X, y, groups=study_id)",
        verbose=verbose,
    )

    _banner("4. Os três modelos que já competem no repo", verbose)
    lopo = leave_one_paper_out(frame)
    dummy = lopo["dummy_lopo"]
    material = lopo["material_mean_lopo"]
    shrink = lopo["shrinkage_lopo"]
    hgb = lopo["hgb_lopo"]
    _print(
        f"  dummy (sempre a média)     MAE {dummy['mae']:.1f}   R² {dummy['r2']:.3f}   "
        f"parâmetros {budget['dummy_parameters']}\n"
        f"  média por gel              MAE {material['mae']:.1f}   R² {material['r2']:.3f}   "
        f"parâmetros {budget['material_mean_parameters']}\n"
        f"  shrinkage (servido)        MAE {shrink['mae']:.1f}   R² {shrink['r2']:.3f}   "
        f"{budget['served_parameters']} parâmetros "
        f"({budget['served_locked_hyperparameters']} hiperparâmetros fechados + "
        f"{budget['served_empirical_priors']} médias gel×célula)\n"
        f"  Ridge LOPO                 MAE {ridge_lopo['mae']:.1f}   R² {ridge_lopo['r2']:.3f}   "
        f"perde — memoriza o paper\n"
        f"  HGB (relatado, não servido até {budget['papers_needed_trees']} papers)  "
        f"MAE {hgb['mae']:.1f}   R² {hgb['r2']:.3f}\n"
        f"  vencedor servido           {lopo.get('deployed_estimator')}   "
        f"mvp_pass={lopo.get('mvp_pass')}",
        verbose=verbose,
    )

    example = predict_one_gel(frame)
    _banner("5. Usar o modelo treinado (uma previsão)", verbose)
    q = example["query"]
    _print(
        f"  query: {q['material_class']}, {q['cell_type']}, {q['growth_factor']}, "
        f"{q['stiffness_kpa']} kPa, dia {q['culture_time_days']}\n"
        f"  previsão shrinkage  {example['predicted_viability_pct']} %\n"
        f"  prior do gel        {example['material_prior']} %\n"
        f"  média local kernel  {example['local_kernel']} %\n"
        f"  n_eff neste gel     {example['n_eff_same_material']}\n"
        "  Isto é o que /lookup mostra. Não precisas de um .pt nem de GPU.",
        verbose=verbose,
    )

    _banner("6. Precisas de mais papers, variáveis, ou condições?", verbose)
    _print(
        f"  Parâmetros vs papers (hoje {budget['n_studies']} estudos, {budget['n_rows']} condições):\n"
        f"    dummy              {budget['dummy_parameters']} parâmetro     → já podes (e já tens)\n"
        f"    média por gel      {budget['material_mean_parameters']} parâmetros      → cada gel precisa de ≥2 papers\n"
        f"    shrinkage servido  {budget['served_parameters']} parâmetros "
        f"({budget['served_locked_hyperparameters']} kernel + {budget['served_empirical_priors']} priors)\n"
        f"    mixed / shrinkage  intercepto por paper + 5 slopes → começa a ser estável a "
        f"{budget['papers_needed_mixed']} papers\n"
        f"    Ridge / árvores    ~{budget['starter_feature_count']} features × "
        f"{PAPERS_PER_FEATURE} papers/feature → ~{budget['papers_needed_ridge']} papers\n"
        f"    começo de produto  {budget['papers_needed_beginning']} papers (não 40 — 40 é só o gate das árvores)\n"
        f"    rede neural        milhares de parâmetros → não é este problema\n\n"
        "  Ordem do que falta, da mais útil para a mais prejudicial:\n"
        "    1. MAIS ESTUDOS (papers independentes com live/dead numérico). Isto é o n.\n"
        "    2. Condições DENTRO desses papers que mexam em kPa, TGF, dias, encapsular vs print.\n"
        "       6 linhas do mesmo lab não valem 6 papers.\n"
        "    3. NÃO mais variáveis agora. Cada coluna extra (passagem, densidade, porosidade)\n"
        "       é mais um parâmetro com 15 labs. O Ridge já perde por isso.\n"
        "    4. Kit do ensaio (calceína vs MTT) só quando estiver preenchido — senão misturas y.\n"
        "    5. NÃO mais abstracts da harvest. 8.5k papers sem número extraído não treinam nada.\n\n"
        f"  Começo de confiança (Ridge-scale): {budget['papers_needed_beginning']} papers. "
        f"Hoje {budget['n_studies']}.\n"
        f"  Gate para o próximo modelo (mixed / Ridge de novo): "
        f"{budget['papers_needed_mixed']} papers e ~80 live/dead.\n"
        f"  Gate para árvores: {budget['papers_needed_trees']} papers (relato, não deploy).\n"
        f"  Hoje mixed? {'sim' if budget['have_enough_for_mixed'] else 'não — extrai papers primeiro'}.\n"
        f"  Hoje começo 100? {'sim' if budget['have_enough_for_beginning'] else 'não — continua a extrair o bairro dos géis que já tens'}.\n"
        f"  Hoje Ridge/árvores? {'sim' if budget['have_enough_for_ridge'] else 'não'}.",
        verbose=verbose,
    )

    _banner("7. Como se treina, na prática, neste repo", verbose)
    _print(
        "  A. Extraís um paper para src/tissuelab/curated.py  (isto é o dataset)\n"
        "  B. python3 -m tissuelab.load_database             (SQLite + CSV)\n"
        "  C. python3 -m tissuelab.benchmark                 (LOPO: dummy vs gel vs shrinkage vs Ridge)\n"
        "  D. A app lê o vencedor. Não há botão 'Train' na UI.\n\n"
        "  python3 -m tissuelab.train  é o XGBoost do SIMULADOR. Não uses esse número.\n"
        "  Este ficheiro (teach_model) é a aula. benchmark.py é o treino a sério.",
        verbose=verbose,
    )

    report = {
        "n_rows": budget["n_rows"],
        "n_studies": budget["n_studies"],
        "served_parameters": budget["served_parameters"],
        "served_locked_hyperparameters": budget["served_locked_hyperparameters"],
        "served_empirical_priors": budget["served_empirical_priors"],
        "budget": budget,
        "random_split_ridge": random_scores,
        "ridge_lopo": ridge_lopo,
        "dummy_lopo": dummy,
        "material_mean_lopo": material,
        "shrinkage_lopo": shrink,
        "hgb_lopo": hgb,
        "deployed_estimator": lopo.get("deployed_estimator"),
        "mvp_pass": lopo.get("mvp_pass"),
        "example_prediction": example,
        "what_to_add_first": "more independent papers with numeric live/dead",
        "do_not_add_first": "more features or more Amass abstracts",
    }
    ARTIFACTS_DIR.mkdir(parents=True, exist_ok=True)
    TEACH_METRICS_PATH.write_text(json.dumps(_jsonable(report), indent=2))
    _print(f"\nEscrevi {TEACH_METRICS_PATH}", verbose=verbose)
    return report


def _jsonable(value):
    if isinstance(value, dict):
        return {str(k): _jsonable(v) for k, v in value.items()}
    if isinstance(value, (list, tuple)):
        return [_jsonable(v) for v in value]
    if isinstance(value, (np.floating, float)):
        return float(value)
    if isinstance(value, (np.integer, int)):
        return int(value)
    if isinstance(value, (np.bool_, bool)):
        return bool(value)
    if value is None:
        return None
    return value


def main() -> None:
    run_lesson(verbose=True)


if __name__ == "__main__":
    main()

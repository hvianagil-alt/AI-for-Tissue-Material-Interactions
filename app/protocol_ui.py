"""PI-first protocol page. One question, one recommendation, papers, search."""

from __future__ import annotations

from html import escape
from urllib.parse import urlencode

from app.shell import normalize_lang, render_shell
from app.ui import CELL_LABELS, CELL_TYPES, GF_LABELS, MATERIAL_LABELS, _label, _viability_cell

GOALS = [
    ("alive", "Keep the cells alive", "Manter as células vivas"),
    ("print", "Print a construct", "Imprimir um constructo"),
    ("matrix", "Make cartilage matrix", "Fazer matriz de cartilagem"),
]
HOW = [
    ("encapsulate", "Encapsulate (3D gel)", "Encapsular (gel 3D)"),
    ("print", "Print / bioink", "Imprimir / bioink"),
    ("either", "Either", "Tanto faz"),
]
TGF = [
    ("either", "TGF-β3: try both", "TGF-β3: testar os dois"),
    ("none", "No TGF-β3", "Sem TGF-β3"),
    ("TGF_b3", "We have TGF-β3", "Temos TGF-β3"),
]
SITES = [
    ("any", "Any job in the table", "Qualquer aplicação da tabela"),
    ("nasal", "Nasal / septum", "Nasal / septo"),
    ("osteoarthritis", "Osteoarthritis", "Osteoartrite"),
    ("auricular", "Auricular / ear", "Auricular / orelha"),
    ("bioprinting", "Bioprinting", "Bioimpressão"),
]
STOCK = [
    ("any", "Any gel in the table", "Qualquer gel da tabela"),
    ("GelMA", "We stock GelMA", "Temos GelMA"),
    ("fibrin", "We stock fibrin", "Temos fibrina"),
    ("HA", "We stock HA", "Temos HA"),
    ("alginate", "We stock alginate", "Temos alginato"),
    ("chitosan", "We stock chitosan", "Temos quitosano"),
    ("collagen", "We stock collagen", "Temos colagénio"),
    ("gellan", "We stock gellan", "Temos gellan"),
    ("gelatin_alginate", "We stock gelatin–alginate", "Temos gelatina–alginato"),
]


def _sel(options: list[tuple], selected: str, lang: str) -> str:
    out = []
    for value, en, pt in options:
        lab = pt if lang == "pt" else en
        sel = " selected" if value == selected else ""
        out.append(f'<option value="{escape(value)}"{sel}>{escape(lab)}</option>')
    return "\n".join(out)


def _cell_sel(selected: str, lang: str) -> str:
    labels_pt = {
        "articular_chondrocyte": "Condrócito articular",
        "auricular_chondrocyte": "Condrócito auricular",
        "nasal_chondrocyte": "Condrócito nasoseptal",
        "MSC": "MSC",
        "adipose_MSC": "MSC do tecido adiposo",
    }
    out = []
    for value in CELL_TYPES:
        lab = labels_pt[value] if lang == "pt" else CELL_LABELS[value]
        sel = " selected" if value == selected else ""
        out.append(f'<option value="{escape(value)}"{sel}>{escape(lab)}</option>')
    return "\n".join(out)


def _doi(row: dict) -> str:
    doi = row.get("doi") or ""
    cite = escape(str(row.get("citation") or row.get("title") or row.get("study_id") or doi or "paper"))
    if doi:
        return f'<a href="https://doi.org/{escape(str(doi))}" target="_blank" rel="noreferrer">{cite}</a>'
    pmid = row.get("pmid")
    if pmid:
        return f'<a href="https://pubmed.ncbi.nlm.nih.gov/{escape(str(pmid))}" target="_blank" rel="noreferrer">{cite}</a>'
    return cite


def _recipe_box(recipe: dict | None, lang: str) -> str:
    if not recipe:
        return ""
    pt = lang == "pt"
    bits = []
    detail = recipe.get("material_detail")
    if detail:
        bits.append(escape(str(detail)))
    wt = recipe.get("polymer_concentration_wt_pct")
    if wt is not None:
        bits.append(f"{float(wt):g} wt%")
    if recipe.get("crosslinking"):
        bits.append(escape(str(recipe["crosslinking"])))
    dens = recipe.get("cell_density_million_per_ml")
    if dens is not None:
        bits.append(f"{float(dens):g}e6/ml")
    if recipe.get("architecture"):
        bits.append(escape(str(recipe["architecture"]).replace("_", " ")))
    if recipe.get("application"):
        bits.append(escape(str(recipe["application"]).replace("_", " ")))
    if recipe.get("chemical_modification") and recipe["chemical_modification"] != "unmodified":
        bits.append(escape(str(recipe["chemical_modification"]).replace("_", " ")))
    viab = recipe.get("viability_pct")
    if viab is not None:
        bits.append(f"{float(viab):.0f}% live/dead")
    meta = " · ".join(bits)
    cite = _doi(recipe)
    title = "Receita extraída (abre o paper)" if pt else "Extracted recipe (open the paper)"
    note = (
        "Isto é a condição publicada, não um protocolo escrito de novo."
        if pt
        else "This is the published condition, not a rewritten methods section."
    )
    return (
        f"<aside class='recipe'><h3>{escape(title)}</h3>"
        f"<p>{cite}</p>"
        f"<p class='meta'>{meta}</p>"
        f"<p class='muted'>{escape(note)}</p></aside>"
    )


def _paper_line(row: dict) -> str:
    bits = []
    if row.get("stiffness_kpa") is not None:
        bits.append(f"{float(row['stiffness_kpa']):.0f} kPa")
    days = row.get("culture_time_days")
    if days not in (None, ""):
        bits.append(f"{float(days):.0f} d")
    gf = row.get("growth_factor")
    if gf:
        bits.append(_label(GF_LABELS, str(gf)))
    pill = _viability_cell(row) if ("viability_pct" in row or row.get("qualitative_label")) else ""
    meta = " · ".join(bits)
    return f"<li>{_doi(row)}{(' — ' + escape(meta)) if meta else ''} {pill}</li>"


def _search_line(row: dict, lang: str) -> str:
    flag = (
        ("na tabela" if lang == "pt" else "in the table")
        if row.get("extracted")
        else ("ainda não extraído" if lang == "pt" else "not extracted yet")
    )
    klass = "in" if row.get("extracted") else "out"
    year = row.get("year") or ""
    journal = row.get("journal") or ""
    title = row.get("title") or row.get("citation") or "Untitled"
    return (
        f"<li class='{klass}'>{_doi({**row, 'citation': title})} "
        f"<span class='muted'>{escape(str(year))} {escape(str(journal))}</span> "
        f"<em class='flag'>{escape(flag)}</em></li>"
    )


def render_protocol_page(
    *,
    result: dict,
    search: dict,
    lang: str = "en",
    live: bool = False,
    corpus: dict | None = None,
) -> str:
    lang = normalize_lang(lang)
    intent = result["intent"]
    proto = result["protocol"]
    pt = lang == "pt"
    gel = _label(MATERIAL_LABELS, proto["material_class"])
    gf = _label(GF_LABELS, proto["growth_factor"])
    kpa = proto.get("stiffness_kpa")
    days = proto["culture_time_days"]
    kicker = "Esta semana, corre" if pt else "This week, run"
    parts = [gel]
    if kpa is not None:
        parts.append(f"~{float(kpa):.0f} kPa")
    if days not in (None, ""):
        parts.append(f"{float(days):.0f} days")
    parts.append(gf)
    headline = " · ".join(parts)
    if result["n_same_numeric"] and result["same_mean"] is not None:
        stat = (
            f"Live/dead extraído nestas células: {result['same_mean']:.0f}%"
            f" ({result['n_same_numeric']} condições, {result['n_papers_same']} papers)."
            if pt
            else f"Extracted live/dead in these cells: {result['same_mean']:.0f}%"
            f" ({result['n_same_numeric']} conditions, {result['n_papers_same']} papers)."
        )
    elif result["n_same_qual"]:
        stat = (
            f"{result['n_same_qual']} linhas extraídas, só floors — sem média."
            if pt
            else f"{result['n_same_qual']} extracted rows, floors only — no mean."
        )
    else:
        stat = "Sem linhas extraídas nestas células." if pt else "No extracted rows in these cells."
    not_pred = (
        "Isto não é uma previsão do teu frasco. É a condição extraída + os papers."
        if pt
        else "This is not a prediction of your flask. It is the extracted condition plus the papers."
    )

    papers = "".join(_paper_line(p) for p in result.get("papers") or []) or (
        "<li class='muted'>No extracted paper for this gel × cell yet.</li>"
    )

    alts = []
    for alt in result.get("alternatives") or []:
        name = _label(MATERIAL_LABELS, alt["material_class"])
        if alt.get("avoid"):
            tag = "não comeces aqui" if pt else "don’t start here"
            detail = (
                f"{alt['same_mean']:.0f}% live/dead extraído" if alt.get("same_mean") is not None else "extracted, low"
            )
            alts.append(f"<li class='avoid'><strong>{escape(name)}</strong> — {escape(tag)} ({escape(detail)})</li>")
            continue
        if alt.get("same_mean") is not None:
            detail = f"{alt['same_mean']:.0f}% · {alt['n_same_numeric']} numeric · {alt['n_papers_same']} papers"
        elif alt.get("n_same_qual"):
            detail = f"{alt['n_same_qual']} floors, no mean"
        else:
            detail = "no rows for these cells"
        href = (
            f"/lookup?material_class={alt['material_class']}&cell_type={intent['cell_type']}"
            f"&stiffness_kpa={alt.get('typical_kpa') or 25}&lang={lang}"
        )
        alts.append(f"<li><a href='{escape(href)}'>{escape(name)}</a> — {escape(detail)}</li>")

    avoid_items = []
    for death in result.get("avoid_board") or []:
        name = _label(MATERIAL_LABELS, death["material_class"])
        mean = death.get("mean")
        mean_s = "n/d" if mean is None else f"{mean:.0f}%"
        avoid_items.append(
            f"<li><strong>{escape(name)}</strong> — {escape(mean_s)} "
            f"({death['n_papers']} papers, min {death['min']:.0f}%)</li>"
        )
    if avoid_items:
        avoid_h = "Não comeces aqui" if pt else "Do not start here"
        avoid_block = (
            f"<h2>{escape(avoid_h)}</h2>"
            f"<p class='sub'><a href='/avoid?cell_type={escape(intent['cell_type'])}&lang={lang}'>"
            f"{'Lista completa' if pt else 'Full avoid board'}</a></p>"
            f"<ul class='alts'>{''.join(avoid_items)}</ul>"
        )
    else:
        avoid_block = ""

    card = result.get("model_card") or {}
    if card:
        dummy = card.get("dummy_mae")
        shrink = card.get("shrinkage_mae")
        r2 = card.get("shrinkage_r2")
        honest = (
            f"LOPO honesto: dummy MAE {dummy} vs shrinkage {shrink}, R² {r2}. "
            f"{card.get('sell') or ''}"
            if not pt
            else f"LOPO honesto: dummy MAE {dummy} vs shrinkage {shrink}, R² {r2}. "
            f"Não compres isto como preditor."
        )
        honest_block = f"<p class='muted honest'>{escape(honest)}</p>"
    else:
        honest_block = ""

    harvested = "".join(_search_line(r, lang) for r in (search.get("harvested") or [])) or (
        "<li class='muted'>No harvested hit for this query.</li>"
    )
    epmc = "".join(_search_line(r, lang) for r in (search.get("europepmc") or []))
    q = search.get("query") or ""
    qs = urlencode(
        {
            "cell_type": intent["cell_type"],
            "goal": intent["goal"],
            "how": intent["how"],
            "tgf": intent["tgf"],
            "stock": intent["stock"],
            "site": intent.get("site") or "any",
            "lang": lang,
        }
    )
    live_qs = qs + "&live=1"
    lookup_qs = urlencode(
        {
            "material_class": proto["material_class"],
            "stiffness_kpa": proto["stiffness_kpa"] if proto.get("stiffness_kpa") is not None else 25,
            "cell_type": proto["cell_type"],
            "growth_factor": proto["growth_factor"],
            "culture_time_days": proto["culture_time_days"],
            "lang": lang,
        }
    )
    find_lab = "Encontrar protocolo" if pt else "Find protocol"
    search_lab = "Procurar no Europe PMC" if pt else "Search Europe PMC"
    papers_h = "Papers extraídos para abrir" if pt else "Extracted papers to open"
    also_h = "Outros na tabela" if pt else "Others in the table"
    search_h = "A literatura para esta pergunta" if pt else "Literature for this question"
    corpus = corpus or {}
    n_gold = int(corpus.get("n_gold_studies") or 0)
    n_lib = int(corpus.get("n_harvested") or 0)
    n_params = int(corpus.get("served_parameters") or 0)
    n_locked = int(corpus.get("served_locked_hyperparameters") or 0)
    n_priors = int(corpus.get("served_empirical_priors") or 0)
    want = int(corpus.get("papers_needed_beginning") or 100)
    if n_gold and n_lib:
        search_sub = (
            f"Isto é uma busca nos {n_lib:,} artigos colhidos (biblioteca). "
            f"O modelo servido tem {n_params} parâmetros "
            f"({n_locked} hiperparâmetros fechados + {n_priors} médias gel×célula) "
            f"e treina em {n_gold} artigos extraídos com live/dead numérico. "
            f"O começo de confiança é {want} papers — 40 é só o gate das árvores. "
            f"Não há botão para 2000 estudos."
            if pt
            else f"This searches the {n_lib:,} harvested papers (library). "
            f"The served model has {n_params} parameters "
            f"({n_locked} locked kernel hyperparameters + {n_priors} gel×cell means) "
            f"and trains on {n_gold} extracted live/dead papers. "
            f"Beginning target is {want} papers — 40 is only the tree report gate. "
            f"There is no 2000-study switch."
        )
    else:
        search_sub = (
            "Isto é uma busca na biblioteca de papers colhidas — não é um modelo a escrever o protocolo."
            if pt
            else "This is a search of the harvested paper library — not a model writing your protocol."
        )
    epmc_h = "Europe PMC (ao vivo)" if pt else "Europe PMC (live)"
    why_h = "Porquê este" if pt else "Why this one"
    evidence = "Ver o cartão de evidência" if pt else "Open the evidence card"

    epmc_block = ""
    if live:
        if search.get("live_error"):
            epmc_block = f"<p class='muted'>{escape(str(search['live_error']))}</p>"
        elif epmc:
            epmc_block = f"<h3>{escape(epmc_h)}</h3><ol class='search-list'>{epmc}</ol>"
        else:
            epmc_block = f"<p class='muted'>{'Sem hits Europe PMC.' if pt else 'No Europe PMC hits.'}</p>"

    why_block = f"<h2>{escape(why_h)}</h2><p class='why'>{escape(result.get('why') or '')}</p>"
    if result.get("stock_warning"):
        why_block = f"<p class='why warn'>{escape(result['stock_warning'])}</p>" + why_block

    extra_css = """
    main { max-width: 760px; }
    .ask { background:#121b2b; border:1px solid #24344c; border-radius:14px; padding:16px; }
    .ask fieldset { border:0; margin:0; padding:0; display:grid; grid-template-columns: 1fr 1fr; gap:12px; }
    .ask legend { grid-column: 1 / -1; font-size:0.82rem; color:#8fa3bb; margin-bottom:4px; }
    .ask label { display:flex; flex-direction:column; gap:6px; font-size:0.82rem; color:#8fa3bb; }
    .ask select { background:#0b1220; color:#e8eef7; border:1px solid #2a3b55; border-radius:8px; padding:9px 10px; font-size:1rem; }
    .ask button { grid-column: 1 / -1; background:#e8eef7; color:#0b1220; border:0; border-radius:8px; padding:11px; font-weight:700; font-size:1rem; cursor:pointer; }
    .ask button:hover { background:#3ecfb2; }
    .answer { margin-top:28px; }
    .kicker { text-transform:uppercase; letter-spacing:0.08em; font-size:0.72rem; color:#8fa3bb; margin:0 0 6px; }
    .answer h1 { font-size:1.7rem; letter-spacing:-0.03em; margin:0 0 10px; line-height:1.25; }
    .stat { font-size:1.05rem; margin:0 0 12px; }
    .why { color:#c5d4e8; margin:0 0 18px; }
    .why.warn { color:#f07178; }
    h2 { margin: 26px 0 8px; font-size:1.02rem; font-weight:650; }
    ol.papers, ol.search-list, ul.alts { padding-left: 1.15rem; margin: 0; }
    ol.papers li, ul.alts li { margin: 0 0 8px; }
    ul.alts { list-style: none; padding-left: 0; }
    ul.alts li { padding: 8px 0; border-bottom: 1px solid #1e2b3f; }
    ul.alts li.avoid { color:#f07178; }
    .search-list li { margin: 0 0 10px; }
    .flag { font-style:normal; font-size:0.72rem; margin-left:6px; border-radius:999px; padding:1px 8px; border:1px solid #2a3b55; color:#9db0c8; }
    .search-list li.in .flag { color:#3ecfb2; border-color:#1d5c52; }
    .query { font-size:0.82rem; color:#7f8ea3; }
    .live { display:inline-block; margin-top:10px; color:#e8eef7; border:1px solid #2a3b55; border-radius:8px; padding:6px 10px; text-decoration:none; font-size:0.9rem; }
    .live:hover { border-color:#3ecfb2; color:#3ecfb2; }
    .recipe { margin: 16px 0 0; padding: 14px 16px; border:1px solid #1d5c52; border-radius:12px; background:#0f1c22; }
    .recipe h3 { margin:0 0 8px; font-size:0.82rem; text-transform:uppercase; letter-spacing:0.06em; color:#3ecfb2; }
    .recipe .meta { color:#e8eef7; margin: 0 0 8px; }
    .recipe .muted { margin:0; font-size:0.82rem; color:#8fa3bb; }
    .honest { margin-top: 28px; }
    @media (max-width: 700px) { .ask fieldset { grid-template-columns: 1fr; } .answer h1 { font-size:1.35rem; } }
    """
    legend = "O que vais fazer esta semana" if pt else "What you are doing this week"
    cells_l = "Células" if pt else "Cells"
    job_l = "Objetivo" if pt else "Job"
    how_l = "Como" if pt else "How"
    fridge_l = "No frigorífico" if pt else "In the fridge"
    body = f"""
    <form class="ask" method="get" action="/">
      <input type="hidden" name="lang" value="{lang}"/>
      <fieldset>
        <legend>{escape(legend)}</legend>
        <label>{escape(cells_l)}
          <select name="cell_type" onchange="this.form.submit()">{_cell_sel(intent['cell_type'], lang)}</select>
        </label>
        <label>{escape(job_l)}
          <select name="goal" onchange="this.form.submit()">{_sel(GOALS, intent['goal'], lang)}</select>
        </label>
        <label>{escape(how_l)}
          <select name="how" onchange="this.form.submit()">{_sel(HOW, intent['how'], lang)}</select>
        </label>
        <label>TGF-β3
          <select name="tgf" onchange="this.form.submit()">{_sel(TGF, intent['tgf'], lang)}</select>
        </label>
        <label>{escape(fridge_l)}
          <select name="stock" onchange="this.form.submit()">{_sel(STOCK, intent['stock'], lang)}</select>
        </label>
        <label>{'Aplicação' if pt else 'Use'}
          <select name="site" onchange="this.form.submit()">{_sel(SITES, intent.get('site') or 'any', lang)}</select>
        </label>
        <button type="submit">{escape(find_lab)}</button>
      </fieldset>
    </form>
    <section class="answer" id="resultado">
      <p class="kicker">{escape(kicker)}</p>
      <h1>{escape(headline)}</h1>
      <p class="stat">{escape(stat)}</p>
      <p class="muted">{escape(not_pred)}</p>
      {_recipe_box(result.get("recipe"), lang)}
      {why_block}
      <p><a href="/lookup?{escape(lookup_qs)}">{escape(evidence)}</a></p>
    </section>
    <h2>{escape(papers_h)}</h2>
    <ol class="papers">{papers}</ol>
    <h2>{escape(also_h)}</h2>
    <ul class="alts">{''.join(alts)}</ul>
    {avoid_block}
    <h2>{escape(search_h)}</h2>
    <p class="sub">{escape(search_sub)}</p>
    <p class="query">{escape(q)}</p>
    <ol class="search-list">{harvested}</ol>
    <p><a class="live" href="/?{escape(live_qs)}">{escape(search_lab)}</a></p>
    {epmc_block}
    {honest_block}
    <p class="foot muted"><a href="/avoid?lang={lang}">Avoid</a> · <a href="/table?lang={lang}">Table</a> · <a href="/compare?lang={lang}">Compare</a> · <a href="/export.csv">CSV</a> · <a href="/api/decision">JSON</a></p>
    """
    title = "TissueLab — this week’s protocol" if lang == "en" else "TissueLab — o protocolo desta semana"
    return render_shell(title=title, lang=lang, page="/", body=body, extra_css=extra_css, onboard="short", qs=qs)


def _count_table(counts: dict, lang: str) -> str:
    if not counts:
        return "<p class='muted'>No tags yet. Run python3 -m tissuelab.analyze_papers</p>"
    rows = []
    for key, n in sorted(counts.items(), key=lambda kv: (-int(kv[1]), str(kv[0]))):
        rows.append(f"<tr><td>{escape(str(key))}</td><td>{int(n)}</td></tr>")
    label = "Tag" if lang == "en" else "Etiqueta"
    return f"<table class='data'><thead><tr><th>{label}</th><th>n</th></tr></thead><tbody>{''.join(rows)}</tbody></table>"


def render_library_page(*, stats: dict, lang: str = "en") -> str:
    pt = lang == "pt"
    title = "Paper library — chemistry, structure, application" if not pt else "Biblioteca — química, estrutura, aplicação"
    n = stats.get("n_analyzed") or 0
    rel = stats.get("n_training_relevant") or 0
    viab = stats.get("n_with_viability") or 0
    n_gold = stats.get("n_gold_studies") or 0
    n_gold_rows = stats.get("n_gold_rows") or 0
    n_lib = stats.get("n_harvested") or n
    n_params = stats.get("served_parameters") or 0
    n_locked = stats.get("served_locked_hyperparameters") or 0
    n_priors = stats.get("served_empirical_priors") or 0
    want = stats.get("papers_needed_beginning") or 100
    lead = (
        f"Two tables: {n_gold} papers with hand-extracted numeric live/dead train the viability model "
        f"({n_gold_rows} conditions). Served shrinkage has {n_params} parameters "
        f"({n_locked} locked kernel hyperparameters + {n_priors} gel×cell means). "
        f"Beginning target is {want} independent papers — 40 is only the tree report gate. "
        f"{n_lib:,} harvested papers are a searchable library — tags, not training labels. "
        "There is no 2000-study model to turn on."
        if not pt
        else f"Duas tabelas: {n_gold} artigos com live/dead numérico extraído treinam o modelo "
        f"({n_gold_rows} condições). O shrinkage servido tem {n_params} parâmetros "
        f"({n_locked} hiperparâmetros fechados + {n_priors} médias gel×célula). "
        f"Começo de confiança: {want} papers — 40 é só o gate das árvores. "
        f"{n_lib:,} artigos colhidos são biblioteca pesquisável — etiquetas, não labels. "
        "Não existe um modelo de 2000 estudos para ligar."
    )
    by_app = stats.get("by_application") or {}
    by_chem = stats.get("by_chemistry") or {}
    by_arch = stats.get("by_architecture") or {}
    app_table = _count_table(by_app, lang)
    chem_table = _count_table(by_chem, lang)
    arch_table = _count_table(by_arch, lang)
    app_h = "Application" if not pt else "Aplicação"
    chem_h = "Chemical modification" if not pt else "Modificação química"
    arch_h = "Architecture" if not pt else "Arquitectura"
    body = f"""
    <h1>{escape(title)}</h1>
    <p class="sub">{escape(lead)}</p>
    <p class="stat">{n_lib:,} harvested papers tagged · {n_gold} extracted live/dead papers ({n_gold_rows} rows) · {rel} tagged training-relevant (search flag, not a label) · {viab} with a viability % in the abstract</p>
    <h2>{app_h}</h2>
    {app_table}
    <h2>{chem_h}</h2>
    {chem_table}
    <h2>{arch_h}</h2>
    {arch_table}
    <p class="foot muted"><a href="/table?lang={lang}">Extracted table</a> · <a href="/export.csv">CSV</a></p>
    """
    extra_css = """
    .stat { font-size:1.05rem; color:#c5d4e8; }
    table.data { max-width: 560px; }
    """
    return render_shell(title=title, lang=lang, page="/library", body=body, extra_css=extra_css, onboard=False)


def render_avoid_page(
    *,
    cell_type: str,
    board: list[dict],
    coverage: list[dict],
    card: dict,
    queue: list[dict],
    never: list[str],
    lang: str = "en",
) -> str:
    lang = normalize_lang(lang)
    pt = lang == "pt"
    title = "Do not start here" if not pt else "Não comeces aqui"
    lead = (
        "Gels whose extracted in-gel live/dead mean is below 60% for these cells. "
        "This is the paid skip — not a predicted death."
        if not pt
        else "Géis cujo live/dead extraído em gel está abaixo de 60% nestas células. "
        "Isto é o skip pago — não é uma morte prevista."
    )
    rows = []
    for death in board:
        name = _label(MATERIAL_LABELS, death["material_class"])
        mean = "—" if death.get("mean") is None else f"{death['mean']:.0f}%"
        mn = "—" if death.get("min") is None else f"{death['min']:.0f}%"
        rows.append(
            f"<tr><td>{escape(name)}</td><td>{escape(mean)}</td><td>{escape(mn)}</td>"
            f"<td>{int(death['n_papers'])}</td><td>{int(death['n_rows'])}</td></tr>"
        )
    if rows:
        table = (
            "<table class='data'><thead><tr>"
            f"<th>{'Gel' if not pt else 'Gel'}</th><th>mean</th><th>min</th>"
            f"<th>{'papers' if not pt else 'papers'}</th><th>n</th>"
            f"</tr></thead><tbody>{''.join(rows)}</tbody></table>"
        )
    else:
        table = (
            "<p class='muted'>No extracted mean below 60% for these cells.</p>"
            if not pt
            else "<p class='muted'>Nenhuma média extraída abaixo de 60% nestas células.</p>"
        )
    cov_rows = []
    for row in coverage:
        name = _label(MATERIAL_LABELS, row["material_class"])
        mean = "—" if row.get("mean") is None else f"{row['mean']:.0f}%"
        flag = "avoid" if row.get("avoid") else ("fragile" if row.get("fragile") else "")
        cov_rows.append(
            f"<tr class='{flag}'><td>{escape(name)}</td><td>{escape(mean)}</td>"
            f"<td>{int(row['n_papers'])}</td><td>{int(row['n_kpa'])}</td>"
            f"<td>{int(row['n_print'])}</td></tr>"
        )
    cov_table = (
        "<table class='data'><thead><tr>"
        "<th>gel</th><th>mean</th><th>papers</th><th>kPa</th><th>print</th>"
        f"</tr></thead><tbody>{''.join(cov_rows)}</tbody></table>"
        if cov_rows
        else "<p class='muted'>No numeric rows for these cells.</p>"
    )
    q_rows = []
    for hole in queue:
        q_rows.append(
            f"<li><strong>{escape(_label(MATERIAL_LABELS, hole['material_class']))}</strong> × "
            f"{escape(hole['cell_type'].replace('_', ' '))} "
            f"<em class='flag'>{escape(hole['kind'])}</em> — {escape(hole['why'])}</li>"
        )
    never_l = "".join(f"<li>{escape(item)}</li>" for item in never)
    dummy = card.get("dummy_mae")
    shrink = card.get("shrinkage_mae")
    r2 = card.get("shrinkage_r2")
    honest = (
        f"Dummy LOPO MAE {dummy} vs shrinkage {shrink}, R² {r2}. "
        f"{card.get('sell') or ''}"
    )
    cell_form = (
        f"<form class='ask' method='get' action='/avoid'>"
        f"<input type='hidden' name='lang' value='{lang}'/>"
        f"<label>{'Células' if pt else 'Cells'}"
        f"<select name='cell_type' onchange='this.form.submit()'>{_cell_sel(cell_type, lang)}</select>"
        f"</label></form>"
    )
    cov_h = "Coverage for these cells" if not pt else "Cobertura nestas células"
    q_h = "Next extraction holes (product order)" if not pt else "Próximos buracos (ordem do produto)"
    never_h = "Never extract as a training mean" if not pt else "Nunca extrair como média de treino"
    body = f"""
    <h1>{escape(title)}</h1>
    <p class="sub">{escape(lead)}</p>
    {cell_form}
    {table}
    <p class="muted honest">{escape(honest)}</p>
    <h2>{escape(cov_h)}</h2>
    {cov_table}
    <h2>{escape(q_h)}</h2>
    <ol class="papers">{''.join(q_rows)}</ol>
    <h2>{escape(never_h)}</h2>
    <ul class="alts">{never_l}</ul>
    <p class="foot muted"><a href="/?lang={lang}">Protocol</a> · <a href="/table?lang={lang}">Table</a> · <a href="/export.csv">CSV</a> · <a href="/api/decision">JSON</a></p>
    """
    extra_css = """
    main { max-width: 760px; }
    .ask { background:#121b2b; border:1px solid #24344c; border-radius:14px; padding:16px; margin: 12px 0 18px; }
    .ask label { display:flex; flex-direction:column; gap:6px; font-size:0.82rem; color:#8fa3bb; }
    .ask select { background:#0b1220; color:#e8eef7; border:1px solid #2a3b55; border-radius:8px; padding:9px 10px; font-size:1rem; }
    table.data tr.avoid td { color:#f07178; }
    table.data tr.fragile td { color:#f4b942; }
    .flag { font-style:normal; font-size:0.72rem; margin-left:6px; border-radius:999px; padding:1px 8px; border:1px solid #2a3b55; color:#9db0c8; }
    .honest { margin: 16px 0; }
    """
    return render_shell(title=title, lang=lang, page="/avoid", body=body, extra_css=extra_css, onboard="short")



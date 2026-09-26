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
STOCK = [
    ("any", "Any gel in the table", "Qualquer gel da tabela"),
    ("GelMA", "We stock GelMA", "Temos GelMA"),
    ("fibrin", "We stock fibrin", "Temos fibrina"),
    ("HA", "We stock HA", "Temos HA"),
    ("alginate", "We stock alginate", "Temos alginato"),
    ("chitosan", "We stock chitosan", "Temos quitosano"),
    ("collagen", "We stock collagen", "Temos colagénio"),
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
) -> str:
    lang = normalize_lang(lang)
    intent = result["intent"]
    proto = result["protocol"]
    pt = lang == "pt"
    gel = _label(MATERIAL_LABELS, proto["material_class"])
    gf = _label(GF_LABELS, proto["growth_factor"])
    kpa = proto["stiffness_kpa"]
    days = proto["culture_time_days"]
    kicker = "Esta semana, corre" if pt else "This week, run"
    headline = f"{gel} · ~{kpa:.0f} kPa · {days:.0f} days · {gf}"
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
            "lang": lang,
        }
    )
    live_qs = qs + "&live=1"
    lookup_qs = urlencode(
        {
            "material_class": proto["material_class"],
            "stiffness_kpa": proto["stiffness_kpa"],
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
    search_sub = (
        "Isto é uma busca nas 8 mil papers já colhidas — não é um modelo a escrever o protocolo."
        if pt
        else "This is a search of the 8k harvested papers — not a model writing your protocol."
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
    .foot { margin-top:28px; }
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
        <button type="submit">{escape(find_lab)}</button>
      </fieldset>
    </form>
    <section class="answer" id="resultado">
      <p class="kicker">{escape(kicker)}</p>
      <h1>{escape(headline)}</h1>
      <p class="stat">{escape(stat)}</p>
      {why_block}
      <p><a href="/lookup?{escape(lookup_qs)}">{escape(evidence)}</a></p>
    </section>
    <h2>{escape(papers_h)}</h2>
    <ol class="papers">{papers}</ol>
    <h2>{escape(also_h)}</h2>
    <ul class="alts">{''.join(alts)}</ul>
    <h2>{escape(search_h)}</h2>
    <p class="sub">{escape(search_sub)}</p>
    <p class="query">{escape(q)}</p>
    <ol class="search-list">{harvested}</ol>
    <p><a class="live" href="/?{escape(live_qs)}">{escape(search_lab)}</a></p>
    {epmc_block}
    <p class="foot muted"><a href="/table?lang={lang}">Table</a> · <a href="/compare?lang={lang}">Compare</a> · <a href="/export.csv">CSV</a></p>
    """
    title = "TissueLab — this week’s protocol" if lang == "en" else "TissueLab — o protocolo desta semana"
    return render_shell(title=title, lang=lang, page="/", body=body, extra_css=extra_css, onboard="short", qs=qs)

"""Visual Predict UI for a cartilage PI. Plain HTML/SVG — no WebSocket."""

from __future__ import annotations

from html import escape

MATERIALS = [
    "GelMA",
    "fibrin",
    "silk_fibrin",
    "HA",
    "alginate",
    "gelatin_alginate",
    "chitosan",
    "chitosan_HA",
    "PEG",
    "agarose",
    "cellulose_alginate",
    "collagen",
]
CELL_TYPES = [
    "articular_chondrocyte",
    "auricular_chondrocyte",
    "MSC",
    "adipose_MSC",
]
GROWTH_FACTORS = ["none", "TGF_b3", "TGF_b1"]


def _options(values: list[str], selected: str) -> str:
    out = []
    for value in values:
        sel = " selected" if value == selected else ""
        out.append(f'<option value="{escape(value)}"{sel}>{escape(value)}</option>')
    return "\n".join(out)


def _scatter_svg(points: list[dict], query_kpa: float | None, query_y: float | None, low: float | None, high: float | None) -> str:
    w, h = 680, 300
    pl, pr, pt, pb = 52, 18, 18, 44
    xmin, xmax = 0.5, 60.0
    gutter = pl * 0.42

    def xmap(kpa):
        if kpa is None:
            return gutter
        k = min(xmax, max(xmin, float(kpa)))
        return pl + (k - xmin) / (xmax - xmin) * (w - pl - pr)

    def ymap(v):
        return pt + (1.0 - float(v) / 100.0) * (h - pt - pb)

    dots = []
    for p in points:
        cx, cy = xmap(p.get("kpa")), ymap(p.get("viability_pct") or 0)
        same = p.get("same_material")
        fill = "#3ecfb2" if same else "#6d7f99"
        opacity = 0.95 if same else 0.35
        r = 6 if same else 4
        dots.append(
            f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="{r}" fill="{fill}" fill-opacity="{opacity}">'
            f'<title>{escape(str(p.get("material_class")))} {p.get("viability_pct"):.0f}%</title></circle>'
        )
    err = ""
    mark = ""
    if query_y is not None:
        y = ymap(query_y)
        if low is not None and high is not None:
            err = (
                f'<line x1="{xmap(query_kpa):.1f}" y1="{ymap(high):.1f}" x2="{xmap(query_kpa):.1f}" '
                f'y2="{ymap(low):.1f}" stroke="#f4b942" stroke-width="3"/>'
            )
        mark = (
            f'<circle cx="{xmap(query_kpa):.1f}" cy="{y:.1f}" r="8" fill="#f4b942" stroke="#0b1220" stroke-width="2"/>'
        )
    ticks = ""
    for kpa in (1, 10, 25, 40, 60):
        x = xmap(kpa)
        ticks += f'<line x1="{x:.1f}" y1="{h-pb}" x2="{x:.1f}" y2="{h-pb+5}" stroke="#9db0c8"/>'
        ticks += f'<text x="{x:.1f}" y="{h-8}" text-anchor="middle" fill="#9db0c8" font-size="11">{kpa}</text>'
    ticks += f'<text x="{gutter:.1f}" y="{h-8}" text-anchor="middle" fill="#9db0c8" font-size="11">s/ kPa</text>'
    for v in (0, 50, 100):
        y = ymap(v)
        ticks += f'<text x="8" y="{y+4:.1f}" fill="#9db0c8" font-size="11">{v}</text>'
    return f"""
    <svg viewBox="0 0 {w} {h}" role="img" aria-label="Live/dead vs stiffness for published gels">
      <rect width="{w}" height="{h}" rx="12" fill="#152033"/>
      <text x="{pl}" y="16" fill="#9db0c8" font-size="12">Live/dead % vs rigidez. Verde = o teu gel. Cinzento = outros. Amarelo = a tua query ± erro LOPO.</text>
      {"".join(dots)}
      {err}{mark}
      <line x1="{pl}" y1="{h-pb}" x2="{w-pr}" y2="{h-pb}" stroke="#2a3b55"/>
      <line x1="{pl}" y1="{pt}" x2="{pl}" y2="{h-pb}" stroke="#2a3b55"/>
      {ticks}
      <text x="{(pl+w-pr)/2:.0f}" y="{h-2}" text-anchor="middle" fill="#9db0c8" font-size="11">kPa</text>
    </svg>
    """


def _numberline_svg(mean: float | None, prior: float | None, local: float | None, competitor: float | None, low: float | None, high: float | None) -> str:
    w, h = 680, 92
    pl, pr = 28, 28

    def xmap(v):
        return pl + float(v) / 100.0 * (w - pl - pr)

    marks = []

    def mark(v, color, label, y=38):
        if v is None:
            return
        x = xmap(v)
        marks.append(f'<line x1="{x:.1f}" y1="22" x2="{x:.1f}" y2="52" stroke="{color}" stroke-width="3"/>')
        marks.append(f'<text x="{x:.1f}" y="{y}" text-anchor="middle" fill="{color}" font-size="11">{escape(label)}</text>')

    band = ""
    if mean is not None and low is not None and high is not None:
        band = (
            f'<rect x="{xmap(low):.1f}" y="28" width="{max(2, xmap(high)-xmap(low)):.1f}" height="16" '
            f'fill="#f4b942" fill-opacity="0.25" rx="4"/>'
        )
    mark(local, "#7f8ea3", "local")
    mark(prior, "#6ea8ff", "média do gel")
    mark(competitor, "#c084fc", "GelMA+TGF")
    mark(mean, "#f4b942", "estimativa", y=78)
    return f"""
    <svg viewBox="0 0 {w} {h}" role="img" aria-label="Number line of viability estimates">
      <rect width="{w}" height="{h}" rx="12" fill="#152033"/>
      <line x1="{pl}" y1="36" x2="{w-pr}" y2="36" stroke="#2a3b55" stroke-width="4"/>
      {band}
      {"".join(marks)}
      <text x="{pl}" y="16" fill="#9db0c8" font-size="11">0%</text>
      <text x="{w-pr}" y="16" text-anchor="end" fill="#9db0c8" font-size="11">100%</text>
    </svg>
    """


def _delta_bars(deltas: list[dict]) -> str:
    if not deltas:
        return ""
    rows = []
    max_abs = max((abs(float(d.get("delta") or 0)) for d in deltas), default=1) or 1
    for item in deltas:
        delta = float(item.get("delta") or 0)
        width = 8 + 70 * abs(delta) / max_abs
        color = "#3ecfb2" if delta > 0 else ("#f07178" if delta < 0 else "#5b6b82")
        sign = f"+{delta:.1f}" if delta > 0 else f"{delta:.1f}"
        hypo = " · se ligares TGF-β3" if item.get("hypothetical") else ""
        rows.append(
            "<div class='barrow'>"
            f"<span>{escape(item['feature'])}</span>"
            f"<i style='width:{width:.0f}%;background:{color}'></i>"
            f"<b>{sign} pp{hypo}</b>"
            "</div>"
        )
    return (
        "<h2>O que é que cada variável puxa</h2>"
        "<p class='muted'>Diferença no live/dead quando essa variável é ignorada. 0 = a tabela ainda não tem alavanca.</p>"
        f"<div class='bars'>{''.join(rows)}</div>"
    )


def _paper_cards(rows: list[dict]) -> str:
    if not rows:
        return "<p class='muted'>Ainda não há live/dead extraído.</p>"
    max_w = max((float(r.get("match_score") or 0) for r in rows), default=1) or 1
    cards = []
    for row in rows:
        doi = row.get("doi") or ""
        cite = escape(str(row.get("citation") or row.get("study_id") or ""))
        title = f'<a href="https://doi.org/{escape(doi)}" target="_blank" rel="noreferrer">{cite}</a>' if doi else cite
        kpa = row.get("stiffness_kpa")
        kpa_s = "kPa n/d" if kpa is None else f"{kpa:.0f} kPa"
        gf = row.get("growth_factor") or "sem GF"
        score = float(row.get("match_score") or 0)
        pct = 100 * score / max_w
        cards.append(
            "<article class='paper'>"
            f"<h3>{title}</h3>"
            f"<p>{escape(str(row.get('material_class')))} · {escape(str(row.get('cell_type') or '—'))} · "
            f"{escape(str(gf))} · {kpa_s} · <strong>{float(row['viability_pct']):.0f}%</strong> live/dead</p>"
            f"<div class='wbar'><i style='width:{pct:.0f}%'></i></div>"
            "</article>"
        )
    return "".join(cards)


def render_predict_page(
    *,
    material_class: str,
    stiffness_kpa: float,
    cell_type: str,
    growth_factor: str,
    culture_time_days: int,
    literature: dict,
) -> str:
    mean = literature.get("mean")
    low = literature.get("low")
    high = literature.get("high")
    lopo = literature.get("lopo") or {}
    coverage = literature.get("coverage") or {}
    competitor = literature.get("competitor") or {}
    mae = lopo.get("shrinkage_mae") or lopo.get("deployed_mae")
    mean_s = "—" if mean is None else f"{mean:.1f}%"
    band_s = "" if mean is None else f"{low:.0f}–{high:.0f}"
    local = literature.get("local")
    prior = literature.get("prior")
    n_mat = coverage.get("n_material", "—")
    n_kpa = coverage.get("n_material_with_kpa", "—")
    miss = coverage.get("pct_kpa_missing", "—")
    verdict = escape(literature.get("verdict") or "")
    notes = "".join(f"<li>{escape(note)}</li>" for note in (literature.get("notes") or []))
    vs = competitor.get("mean")
    vs_s = "—" if vs is None else f"{vs:.1f}%"
    return f"""<!DOCTYPE html>
<html lang="pt">
<head>
  <meta charset="utf-8"/>
  <meta name="viewport" content="width=device-width, initial-scale=1"/>
  <title>TissueLab — o próximo gel</title>
  <style>
    :root {{ color-scheme: dark; }}
    body {{ margin:0; font-family: ui-sans-serif, system-ui, sans-serif; background:#0b1220; color:#e8eef7; line-height:1.45; }}
    main {{ max-width: 980px; margin: 0 auto; padding: 24px 18px 72px; }}
    h1 {{ margin: 0 0 4px; font-size: 1.85rem; }}
    h2 {{ margin: 28px 0 10px; font-size: 1.15rem; }}
    .sub, .muted {{ color:#9db0c8; }}
    .verdict {{ background:#152033; border-left: 4px solid #f4b942; padding: 14px 16px; border-radius: 0 12px 12px 0; margin: 18px 0; font-size: 1.05rem; }}
    form {{ display:grid; grid-template-columns: repeat(auto-fit, minmax(160px, 1fr)); gap: 12px; background:#152033; padding:16px; border-radius:12px; }}
    label {{ display:flex; flex-direction:column; gap:6px; font-size: 0.85rem; color:#9db0c8; }}
    select, input {{ background:#0b1220; color:#e8eef7; border:1px solid #2a3b55; border-radius:8px; padding:10px; font-size:1rem; }}
    button {{ grid-column: 1 / -1; background:#3ecfb2; color:#07231d; border:0; border-radius:8px; padding:12px; font-weight:700; font-size:1rem; cursor:pointer; }}
    .hero {{ display:grid; grid-template-columns: 1.1fr 1fr; gap:14px; margin-top:18px; }}
    .card {{ background:#152033; border-radius:12px; padding:16px; }}
    .big {{ font-size:3rem; color:#f4b942; font-weight:800; letter-spacing:-0.03em; }}
    .chips {{ display:flex; flex-wrap:wrap; gap:8px; margin-top:10px; }}
    .chips span {{ background:#0b1220; border:1px solid #2a3b55; border-radius:999px; padding:4px 10px; font-size:0.82rem; color:#c5d4e8; }}
    svg {{ width:100%; height:auto; display:block; margin: 8px 0 4px; }}
    .bars {{ display:flex; flex-direction:column; gap:8px; }}
    .barrow {{ display:grid; grid-template-columns: 140px 1fr auto; gap:10px; align-items:center; font-size:0.92rem; }}
    .barrow i {{ display:block; height:10px; border-radius:6px; }}
    .paper {{ background:#152033; border-radius:12px; padding:14px 16px; margin-bottom:10px; }}
    .paper h3 {{ margin:0 0 6px; font-size:1rem; font-weight:600; }}
    .paper p {{ margin:0; color:#c5d4e8; font-size:0.92rem; }}
    a {{ color:#3ecfb2; }}
    .wbar {{ height:6px; background:#0b1220; border-radius:6px; margin-top:10px; }}
    .wbar i {{ display:block; height:6px; background:#3ecfb2; border-radius:6px; }}
    ul {{ color:#c5d4e8; }}
    @media (max-width: 800px) {{ .hero {{ grid-template-columns: 1fr; }} .barrow {{ grid-template-columns: 1fr; }} .big {{ font-size:2.4rem; }} }}
  </style>
</head>
<body>
  <main>
    <p class="muted">TissueLab · hidrogel → condrócito · só live/dead extraído à mão</p>
    <h1>Qual é o próximo gel?</h1>
    <p class="sub">Muda o protocolo. O gráfico e o número mexem com a literatura — não com um simulador.</p>
    <form method="get" action="/">
      <label>Hidrogel
        <select name="material_class" onchange="this.form.submit()">{_options(MATERIALS, material_class)}</select>
      </label>
      <label>Rigidez (kPa)
        <input type="number" name="stiffness_kpa" min="0.5" max="200" step="0.5" value="{stiffness_kpa}" onchange="this.form.submit()"/>
      </label>
      <label>Células
        <select name="cell_type" onchange="this.form.submit()">{_options(CELL_TYPES, cell_type)}</select>
      </label>
      <label>Factor de crescimento
        <select name="growth_factor" onchange="this.form.submit()">{_options(GROWTH_FACTORS, growth_factor)}</select>
      </label>
      <label>Dias em cultura
        <input type="number" name="culture_time_days" min="1" max="42" step="1" value="{int(culture_time_days)}" onchange="this.form.submit()"/>
      </label>
      <button type="submit">Actualizar evidência</button>
    </form>
    <p class="verdict">{verdict}</p>
    <div class="hero">
      <div class="card">
        <div class="muted">Live/dead estimado na literatura</div>
        <div class="big">{escape(mean_s)}</div>
        <div class="muted">banda {escape(band_s)} · erro entre papers, não intervalo biológico</div>
        <div class="chips">
          <span>{escape(str(n_mat))} condições deste gel</span>
          <span>{escape(str(n_kpa))} com kPa</span>
          <span>{escape(str(miss))}% da tabela sem kPa</span>
          <span>vs GelMA+TGF {escape(vs_s)}</span>
        </div>
      </div>
      <div class="card">
        <div class="muted">Onde está este número</div>
        {_numberline_svg(mean, prior, local, competitor.get("mean"), low, high)}
        <p class="muted">Amarelo = estimativa. Azul = média do material. Roxo = o que um PI já faria (GelMA 25 kPa + TGF-β3). Cinzento = média das condições mais parecidas, antes do encolhimento.</p>
      </div>
    </div>
    <h2>Mapa da evidência</h2>
    {_scatter_svg(literature.get("chart_points") or [], stiffness_kpa, mean, low, high)}
    {_delta_bars(literature.get("knob_deltas") or [])}
    <h2>Papers extraídos mais próximos</h2>
    <p class="muted">Abre o DOI. A barra é o peso no kernel — não uma nota de qualidade do paper.</p>
    {_paper_cards(literature.get("similar") or [])}
    <h2>Limitações (para não te enganares)</h2>
    <ul>{notes}</ul>
  </main>
</body>
</html>
"""

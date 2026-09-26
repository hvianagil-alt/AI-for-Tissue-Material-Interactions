"""Visual Predict UI for a cartilage PI. Plain HTML/SVG — no WebSocket."""

from __future__ import annotations

from html import escape

from app.shell import normalize_lang, render_shell

MATERIAL_GROUPS = [
    (
        "Gels a PI already runs",
        ["GelMA", "fibrin", "HA", "alginate", "chitosan", "PEG", "collagen", "gellan"],
    ),
    (
        "Extracted composites",
        [
            "GelMA_HA",
            "GelMA_chitosan",
            "GelMA_alginate",
            "silk_fibrin",
            "fibrin_dECM",
            "alginate_dECM",
            "gelatin_alginate",
            "chitosan_HA",
            "chitosan_gelatin_PVA",
            "cellulose_alginate",
            "PEG_dextran",
            "PDLLA_PEG_HA",
        ],
    ),
    ("Others in the table", ["agarose", "PEGMA"]),
]
MATERIALS = [item for _, group in MATERIAL_GROUPS for item in group]
MATERIAL_LABELS = {
    "GelMA": "GelMA",
    "fibrin": "Fibrin",
    "silk_fibrin": "Silk + fibrin",
    "HA": "Hyaluronic acid (HA)",
    "alginate": "Alginate",
    "gelatin_alginate": "Gelatin + alginate",
    "chitosan": "Chitosan",
    "chitosan_HA": "Chitosan + HA",
    "PEG": "PEG",
    "agarose": "Agarose",
    "cellulose_alginate": "Cellulose + alginate",
    "collagen": "Collagen",
    "gellan": "Gellan (GGMA)",
    "fibrin_dECM": "Fibrin + dECM",
    "alginate_dECM": "Alginate + dECM",
    "chitosan_gelatin_PVA": "Chitosan + gelatin + PVA",
    "PEGMA": "PEGMA",
    "PEG_dextran": "PEG + dextran",
    "PDLLA_PEG_HA": "PDLLA–PEG–HA",
    "GelMA_HA": "GelMA + HA",
    "GelMA_chitosan": "GelMA + chitosan",
    "GelMA_alginate": "GelMA + oxidized alginate",
}
CELL_TYPES = [
    "articular_chondrocyte",
    "auricular_chondrocyte",
    "nasal_chondrocyte",
    "MSC",
    "adipose_MSC",
]
CELL_LABELS = {
    "articular_chondrocyte": "Articular chondrocyte",
    "auricular_chondrocyte": "Auricular chondrocyte",
    "nasal_chondrocyte": "Nasoseptal chondrocyte",
    "MSC": "Mesenchymal stem cells (MSC)",
    "adipose_MSC": "Adipose-derived MSC",
}
GROWTH_FACTORS = ["none", "TGF_b3", "TGF_b1"]
GF_LABELS = {
    "none": "No growth factor",
    "TGF_b3": "TGF-β3",
    "TGF_b1": "TGF-β1",
}

TRUST_COLORS = {
    "no_data": "#6d7f99",
    "weak": "#f07178",
    "heterogeneous": "#f4b942",
    "useful": "#3ecfb2",
    "sem_dados": "#6d7f99",
    "fraca": "#f07178",
    "heterogenea": "#f4b942",
    "util": "#3ecfb2",
}


def _label(mapping: dict[str, str], value: str) -> str:
    return mapping.get(value, value.replace("_", " "))


def _options(values: list[str], selected: str, labels: dict[str, str] | None = None, counts: dict | None = None) -> str:
    out = []
    for value in values:
        sel = " selected" if value == selected else ""
        text = _label(labels or {}, value)
        n = (counts or {}).get(value)
        if n:
            text = f"{text} · {int(n)}"
        elif counts is not None:
            text = f"{text} · 0"
        out.append(f'<option value="{escape(value)}"{sel}>{escape(text)}</option>')
    return "\n".join(out)


def _grouped_material_options(selected: str, counts: dict | None) -> str:
    blocks = []
    for group_name, values in MATERIAL_GROUPS:
        inner = _options(values, selected, MATERIAL_LABELS, counts)
        blocks.append(f'<optgroup label="{escape(group_name)}">{inner}</optgroup>')
    return "\n".join(blocks)


def _scatter_svg(
    points: list[dict],
    query_kpa: float | None,
    query_y: float | None,
    low: float | None,
    high: float | None,
    competitor_kpa: float | None = None,
    competitor_y: float | None = None,
) -> str:
    w, h = 720, 340
    pl, pr, pt, pb = 52, 18, 36, 52
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
        kpa = p.get("kpa")
        clipped = kpa is not None and float(kpa) > xmax
        kpa_s = "no kPa" if kpa is None else (f"{float(kpa):.0f} kPa" + (" (off axis)" if clipped else ""))
        cite = p.get("citation") or p.get("study_id") or ""
        title = escape(f"{p.get('material_class')} · {p.get('viability_pct'):.0f}% · {kpa_s} · {cite}")
        if same:
            dots.append(
                f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="7" fill="#3ecfb2" stroke="#0b1220" stroke-width="1">'
                f"<title>{title}</title></circle>"
            )
        else:
            dots.append(
                f'<rect x="{cx-3.5:.1f}" y="{cy-3.5:.1f}" width="7" height="7" fill="#6d7f99" fill-opacity="0.45">'
                f"<title>{title}</title></rect>"
            )
    err = ""
    mark = ""
    if query_y is not None:
        y = ymap(query_y)
        xq = xmap(query_kpa)
        if low is not None and high is not None:
            err = (
                f'<line x1="{xq:.1f}" y1="{ymap(high):.1f}" x2="{xq:.1f}" '
                f'y2="{ymap(low):.1f}" stroke="#f4b942" stroke-width="3"/>'
            )
        mark = (
            f'<polygon points="{xq:.1f},{y-10:.1f} {xq+9:.1f},{y+8:.1f} {xq-9:.1f},{y+8:.1f}" '
            f'fill="#f4b942" stroke="#0b1220" stroke-width="2"><title>Your query</title></polygon>'
        )
    comp = ""
    if competitor_y is not None:
        xc, yc = xmap(competitor_kpa), ymap(competitor_y)
        comp = (
            f'<polygon points="{xc:.1f},{yc-9:.1f} {xc+8:.1f},{yc:.1f} {xc:.1f},{yc+9:.1f} {xc-8:.1f},{yc:.1f}" '
            f'fill="#c084fc" stroke="#0b1220" stroke-width="1.5"><title>GelMA 25 kPa + TGF-β3</title></polygon>'
        )
    ticks = ""
    for kpa, label in ((1, "1"), (8, "8"), (25, "25"), (40, "40"), (60, "60")):
        x = xmap(kpa)
        ticks += f'<line x1="{x:.1f}" y1="{h-pb}" x2="{x:.1f}" y2="{h-pb+5}" stroke="#9db0c8"/>'
        ticks += f'<text x="{x:.1f}" y="{h-22}" text-anchor="middle" fill="#9db0c8" font-size="11">{label}</text>'
    ticks += f'<text x="{gutter:.1f}" y="{h-22}" text-anchor="middle" fill="#9db0c8" font-size="11">no kPa</text>'
    ticks += f'<text x="{xmap(8):.1f}" y="{h-8}" text-anchor="middle" fill="#5b6b82" font-size="10">soft</text>'
    ticks += f'<text x="{xmap(25):.1f}" y="{h-8}" text-anchor="middle" fill="#5b6b82" font-size="10">typical in vitro</text>'
    ticks += f'<text x="{xmap(50):.1f}" y="{h-8}" text-anchor="middle" fill="#5b6b82" font-size="10">stiff</text>'
    for v in (0, 50, 100):
        y = ymap(v)
        ticks += f'<text x="8" y="{y+4:.1f}" fill="#9db0c8" font-size="11">{v}</text>'
    return f"""
    <svg viewBox="0 0 {w} {h}" role="img" aria-label="Live/dead versus stiffness. Green circles: this gel. Grey squares: other gels. Yellow triangle: your query. Purple diamond: GelMA with TGF-β3.">
      <rect width="{w}" height="{h}" rx="12" fill="#152033"/>
      {"".join(dots)}
      {err}{comp}{mark}
      <line x1="{pl}" y1="{h-pb}" x2="{w-pr}" y2="{h-pb}" stroke="#2a3b55"/>
      <line x1="{pl}" y1="{pt}" x2="{pl}" y2="{h-pb}" stroke="#2a3b55"/>
      {ticks}
      <text x="{(pl+w-pr)/2:.0f}" y="{h-2}" text-anchor="middle" fill="#9db0c8" font-size="11">stiffness (kPa)</text>
    </svg>
    """


def _numberline_svg(mean: float | None, prior: float | None, local: float | None, competitor: float | None, low: float | None, high: float | None) -> str:
    w, h = 720, 88
    pl, pr = 36, 36

    def xmap(v):
        return pl + float(v) / 100.0 * (w - pl - pr)

    marks = []

    def tick(v, color, width=3, height=22):
        if v is None:
            return
        x = xmap(v)
        marks.append(
            f'<line x1="{x:.1f}" y1="{52-height/2:.0f}" x2="{x:.1f}" y2="{52+height/2:.0f}" '
            f'stroke="{color}" stroke-width="{width}"/>'
        )

    band = ""
    if mean is not None and low is not None and high is not None:
        band = (
            f'<rect x="{xmap(low):.1f}" y="40" width="{max(2, xmap(high)-xmap(low)):.1f}" height="24" '
            f'fill="#f4b942" fill-opacity="0.20" rx="4"/>'
        )
    tick(local, "#7f8ea3", 3, 16)
    tick(prior, "#6ea8ff", 3, 18)
    tick(competitor, "#c084fc", 4, 20)
    tick(mean, "#f4b942", 5, 28)
    mean_label = ""
    if mean is not None:
        mean_label = f'<text x="{xmap(mean):.1f}" y="22" text-anchor="middle" fill="#f4b942" font-size="13" font-weight="700">{float(mean):.0f}%</text>'
    return f"""
    <svg viewBox="0 0 {w} {h}" role="img" aria-label="Recta de 0 a 100 por cento com estimativa, média do gel e protocolo GelMA com TGF.">
      <rect width="{w}" height="{h}" rx="12" fill="#152033"/>
      <line x1="{pl}" y1="52" x2="{w-pr}" y2="52" stroke="#2a3b55" stroke-width="4"/>
      {band}
      {"".join(marks)}
      {mean_label}
      <text x="{pl}" y="78" fill="#9db0c8" font-size="11">0%</text>
      <text x="{w-pr}" y="78" text-anchor="end" fill="#9db0c8" font-size="11">100%</text>
    </svg>
    """


def _trust_meter(trust: dict) -> str:
    level = trust.get("level") or "sem_dados"
    fill = int(trust.get("fill") or 0)
    color = TRUST_COLORS.get(level, "#6d7f99")
    cells = []
    for i in range(1, 4):
        bg = color if i <= fill else "#0b1220"
        cells.append(f'<i style="background:{bg}"></i>')
    return (
        f"<div class='trust' role='img' aria-label='{escape(trust.get('label') or '')}'>"
        f"{''.join(cells)}</div>"
        f"<p class='trust-label' style='color:{color}'>{escape(trust.get('label') or '')}</p>"
        f"<p class='muted'>{escape(trust.get('why') or '')}</p>"
    )


def _alt_cards(alts: list[dict], you_mean: float | None) -> str:
    if not alts:
        return ""
    cards = []
    for alt in alts:
        delta = ""
        if you_mean is not None and alt.get("id") != "you" and alt.get("mean") is not None:
            d = float(alt["mean"]) - float(you_mean)
            sign = f"+{d:.1f}" if d > 0 else f"{d:.1f}"
            delta = f"<span class='muted'>{sign} pp vs yours</span>"
        you = " you" if alt.get("id") == "you" else ""
        kpa = alt.get("stiffness_kpa")
        kpa_s = "" if kpa in (None, "") else f" · {float(kpa):.0f} kPa"
        gf = alt.get("growth_factor") or "none"
        gf_s = _label(GF_LABELS, str(gf))
        cards.append(
            f"<article class='alt{you}'>"
            f"<div class='muted'>{escape(alt['label'])}</div>"
            f"<div class='n'>{float(alt['mean']):.1f}%</div>"
            f"<div class='muted'>{escape(_label(MATERIAL_LABELS, str(alt.get('material_class') or '')))}{kpa_s}<br/>{escape(gf_s)}</div>"
            f"{delta}"
            "</article>"
        )
    return (
        "<h2>What if you changed the protocol?</h2>"
        "<p class='muted'>Same estimator, four bench questions. Not a quality ranking.</p>"
        f"<div class='alts'>{''.join(cards)}</div>"
    )


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
        extra = []
        if item.get("hypothetical"):
            extra.append("if you turn TGF-β3 on")
        if item.get("borrowed"):
            extra.append("borrowed from other gels")
        n_obs = item.get("n_observed")
        if n_obs is not None:
            extra.append(f"{int(n_obs)} rows of this gel")
        note = f"<small>{escape(' · '.join(extra))}</small>" if extra else ""
        rows.append(
            "<div class='barrow'>"
            f"<span>{escape(item['feature'])}{note}</span>"
            f"<i style='width:{width:.0f}%;background:{color}'></i>"
            f"<b>{sign} pp</b>"
            "</div>"
        )
    return (
        "<h2>What each variable pulls</h2>"
        "<p class='muted'>Difference in live/dead when that variable is ignored. 0 = the table has no leverage yet. "
        "«Borrowed» = this gel has no extracted measurement of that knob.</p>"
        f"<div class='bars'>{''.join(rows)}</div>"
    )


def _context_cards(rows: list[dict]) -> str:
    if not rows:
        return ""
    cards = []
    for row in rows:
        doi = row.get("doi") or ""
        cite = escape(str(row.get("citation") or row.get("study_id") or ""))
        title = f'<a href="https://doi.org/{escape(doi)}" target="_blank" rel="noreferrer">{cite}</a>' if doi else cite
        kpa = row.get("stiffness_kpa")
        kpa_s = "no kPa" if kpa is None else f"{float(kpa):.0f} kPa"
        gf = _label(GF_LABELS, str(row.get("growth_factor") or "none"))
        days = row.get("culture_time_days")
        days_s = "days unknown" if days in (None, "") else f"{float(days):.0f} d"
        cells = _label(CELL_LABELS, str(row.get("cell_type") or "—"))
        cards.append(
            f"<article class='paper context'>"
            f"<h3>{title}</h3>"
            f"<p>{escape(_label(MATERIAL_LABELS, str(row.get('material_class'))))} · "
            f"{escape(cells)} · {escape(gf)} · {kpa_s} · {days_s} · {_viability_cell(row)}</p>"
            "</article>"
        )
    return (
        "<h2>Also extracted for this gel</h2>"
        "<p class='muted'>Floors, ‘high’, and kPa the number ignores. Yellow pills are not means. "
        "Open these before you pick Friday’s gel.</p>"
        f"<div class='context-list'>{''.join(cards)}</div>"
    )


def _paper_cards(rows: list[dict], want_material: str | None) -> str:
    if not rows:
        return "<p class='muted'>No extracted live/dead yet.</p>"
    max_w = max((float(r.get("match_score") or 0) for r in rows), default=1) or 1
    cards = []
    for row in rows:
        doi = row.get("doi") or ""
        cite = escape(str(row.get("citation") or row.get("study_id") or ""))
        title = f'<a href="https://doi.org/{escape(doi)}" target="_blank" rel="noreferrer">{cite}</a>' if doi else cite
        kpa = row.get("stiffness_kpa")
        kpa_s = "no kPa" if kpa is None else f"{kpa:.0f} kPa"
        gf = _label(GF_LABELS, str(row.get("growth_factor") or "none"))
        days = row.get("culture_time_days")
        days_s = "days unknown" if days in (None, "") else f"{float(days):.0f} d"
        score = float(row.get("match_score") or 0)
        pct = 100 * score / max_w
        same = row.get("material_class") == want_material
        badge = "<em class='badge'>this gel</em>" if same else "<em class='badge other'>other gel</em>"
        cards.append(
            f"<article class='paper{' same' if same else ''}'>"
            f"<h3>{title} {badge}</h3>"
            f"<p>{escape(_label(MATERIAL_LABELS, str(row.get('material_class'))))} · "
            f"{escape(_label(CELL_LABELS, str(row.get('cell_type') or '—')))} · "
            f"{escape(gf)} · {kpa_s} · {days_s} · "
            f"<strong>{float(row['viability_pct']):.0f}%</strong> live/dead</p>"
            f"<div class='wbar'><i style='width:{pct:.0f}%'></i></div>"
            "</article>"
        )
    return "".join(cards)


def _lopo_svg(lopo: dict) -> str:
    dummy = lopo.get("dummy_mae")
    shrink = lopo.get("shrinkage_mae") or lopo.get("deployed_mae")
    target = lopo.get("target_mae")
    if dummy is None or shrink is None:
        return ""
    w, h = 720, 120
    pl, pr, pt, pb = 160, 40, 18, 28
    xmax = max(float(dummy), float(shrink), float(target or 0), 1) * 1.15

    def xmap(v):
        return pl + float(v) / xmax * (w - pl - pr)

    def bar(y, value, color, label):
        x = xmap(value)
        return (
            f'<text x="12" y="{y+14}" fill="#c5d4e8" font-size="13">{escape(label)}</text>'
            f'<rect x="{pl}" y="{y}" width="{x-pl:.1f}" height="18" rx="4" fill="{color}"/>'
            f'<text x="{x+8:.1f}" y="{y+14}" fill="#e8eef7" font-size="13">{float(value):.1f}</text>'
        )

    target_line = ""
    if target is not None:
        xt = xmap(target)
        target_line = (
            f'<line x1="{xt:.1f}" y1="{pt}" x2="{xt:.1f}" y2="{h-pb}" stroke="#f4b942" stroke-dasharray="4 3"/>'
            f'<text x="{xt:.1f}" y="{h-8}" text-anchor="middle" fill="#f4b942" font-size="11">MVP bar {float(target):.1f}</text>'
        )
    return f"""
    <svg viewBox="0 0 {w} {h}" role="img" aria-label="Erro leave-one-paper-out: dummy contra shrinkage, com a barra MVP.">
      <rect width="{w}" height="{h}" rx="12" fill="#152033"/>
      {bar(22, dummy, "#6d7f99", "dummy (mean)")}
      {bar(52, shrink, "#3ecfb2", "shrinkage (served)")}
      {target_line}
    </svg>
    """


def render_predict_page(
    *,
    material_class: str,
    stiffness_kpa: float,
    cell_type: str,
    growth_factor: str,
    culture_time_days: int,
    literature: dict,
    lang: str = "en",
) -> str:
    lang = normalize_lang(lang)
    mean = literature.get("mean")
    low = literature.get("low")
    high = literature.get("high")
    lopo = literature.get("lopo") or {}
    coverage = literature.get("coverage") or {}
    competitor = literature.get("competitor") or {}
    trust = literature.get("trust") or {}
    split = literature.get("variance_split") or {}
    mean_s = "—" if mean is None else f"{mean:.1f}%"
    band_s = "" if mean is None else f"{low:.0f}–{high:.0f}"
    local = literature.get("local")
    prior = literature.get("prior")
    n_mat = coverage.get("n_material", "—")
    n_kpa = coverage.get("n_material_with_kpa", "—")
    n_table = coverage.get("n_table_material", "—")
    n_qual = coverage.get("n_table_material_qual", "—")
    miss = coverage.get("pct_kpa_missing", "—")
    n_eff_same = literature.get("n_eff_same", "—")
    mat_min = coverage.get("material_min")
    mat_max = coverage.get("material_max")
    range_s = "—" if mat_min is None else f"{mat_min:.0f}–{mat_max:.0f}%"
    verdict = escape(literature.get("verdict") or "")
    notes = "".join(f"<li>{escape(note)}</li>" for note in (literature.get("notes") or []))
    vs = competitor.get("mean")
    vs_s = "—" if vs is None else f"{vs:.1f}%"
    delta = competitor.get("delta")
    delta_s = "—" if delta is None else (f"+{delta:.1f} pp" if delta > 0 else f"{delta:.1f} pp")
    trust_level = trust.get("level") or "no_data"
    next_read = literature.get("next_read") or {}
    next_html = ""
    if next_read.get("doi"):
        extra_bits = []
        kpa_n = next_read.get("stiffness_kpa")
        if kpa_n is not None:
            extra_bits.append(f"{float(kpa_n):.0f} kPa")
        if next_read.get("viability_pct") is not None:
            extra_bits.append(f"{float(next_read['viability_pct']):.0f}% extracted live/dead")
        elif next_read.get("qualitative_label"):
            extra_bits.append(f"{next_read['qualitative_label']} — qualitative, not in the number")
        extra_s = (" · " + " · ".join(extra_bits)) if extra_bits else ""
        next_html = (
            "<div class='next'>"
            "<strong>Open this next.</strong> "
            f"<a href='https://doi.org/{escape(str(next_read['doi']))}' target='_blank' rel='noreferrer'>"
            f"{escape(str(next_read.get('citation') or next_read['doi']))}</a>"
            f"{escape(extra_s)}."
            "</div>"
        )
    between = split.get("between_paper_sd")
    within = split.get("within_paper_sd_median")
    var_s = ""
    if between is not None and within is not None:
        var_s = (
            f"Between-paper spread is ~{between:.0f} points; within a paper it is ~{within:.0f}. "
            "That is why moving 10 kPa barely moves the number — the real uncertainty is which paper you left out."
        )
    reasons = literature.get("interval_reasons") or []
    reasons_s = " · ".join(str(r) for r in reasons)
    kpa_slider = min(60.0, max(0.5, float(stiffness_kpa)))
    extra_css = f"""
    .verdict {{ background:#152033; border-left: 4px solid {TRUST_COLORS.get(trust_level, '#f4b942')}; padding: 14px 16px; border-radius: 0 12px 12px 0; margin: 18px 0; font-size: 1.05rem; }}
    fieldset {{ border:0; margin:0; padding:0; }}
    legend {{ font-size: 0.85rem; color:#9db0c8; margin-bottom:8px; }}
    form {{ background:#152033; padding:16px; border-radius:12px; }}
    form fieldset {{ display:grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 14px; }}
    form legend {{ grid-column: 1 / -1; }}
    label {{ display:flex; flex-direction:column; gap:6px; font-size: 0.85rem; color:#9db0c8; }}
    select, input[type=number] {{ background:#0b1220; color:#e8eef7; border:1px solid #2a3b55; border-radius:8px; padding:10px; font-size:1rem; }}
    input[type=range] {{ width:100%; accent-color:#3ecfb2; }}
    .sliderline {{ display:grid; grid-template-columns: 1fr 88px; gap:8px; align-items:center; }}
    .ticks {{ font-size:0.75rem; color:#7f8ea3; }}
    button {{ grid-column: 1 / -1; background:#3ecfb2; color:#07231d; border:0; border-radius:8px; padding:12px; font-weight:700; font-size:1rem; cursor:pointer; }}
    button:focus, select:focus, input:focus {{ outline: 2px solid #f4b942; outline-offset: 2px; }}
    .hero {{ display:grid; grid-template-columns: 1.05fr 1fr; gap:14px; margin-top:18px; }}
    .card {{ background:#152033; border-radius:12px; padding:16px; }}
    .big {{ font-size:3rem; color:#f4b942; font-weight:800; letter-spacing:-0.03em; }}
    .chips {{ display:flex; flex-wrap:wrap; gap:8px; margin-top:10px; }}
    .chips span {{ background:#0b1220; border:1px solid #2a3b55; border-radius:999px; padding:4px 10px; font-size:0.82rem; color:#c5d4e8; }}
    .trust {{ display:flex; gap:4px; height:10px; border-radius:99px; overflow:hidden; background:#0b1220; margin:10px 0 6px; }}
    .trust i {{ flex:1; }}
    .trust-label {{ margin:0; font-weight:700; }}
    .legend {{ display:flex; flex-wrap:wrap; gap:12px; font-size:0.82rem; color:#c5d4e8; margin: 6px 0 10px; }}
    .legend b.dot {{ color:#3ecfb2; }} .legend b.sq {{ color:#6d7f99; }} .legend b.tri {{ color:#f4b942; }} .legend b.dia {{ color:#c084fc; }}
    svg {{ width:100%; height:auto; display:block; margin: 8px 0 4px; }}
    .alts {{ display:grid; grid-template-columns: repeat(auto-fit, minmax(160px, 1fr)); gap:10px; }}
    .alt {{ background:#152033; border-radius:12px; padding:14px; min-height:140px; }}
    .alt.you {{ outline:2px solid #f4b942; }}
    .alt .n {{ font-size:1.8rem; font-weight:800; color:#e8eef7; margin: 4px 0; }}
    .bars {{ display:flex; flex-direction:column; gap:10px; }}
    .barrow {{ display:grid; grid-template-columns: 180px 1fr auto; gap:10px; align-items:center; font-size:0.92rem; }}
    .barrow span {{ display:flex; flex-direction:column; }}
    .barrow small {{ color:#7f8ea3; font-size:0.75rem; }}
    .barrow i {{ display:block; height:10px; border-radius:6px; }}
    .paper {{ background:#152033; border-radius:12px; padding:14px 16px; margin-bottom:10px; }}
    .paper.same {{ outline:1px solid #3ecfb2; }}
    .paper h3 {{ margin:0 0 6px; font-size:1rem; font-weight:600; }}
    .paper p {{ margin:0; color:#c5d4e8; font-size:0.92rem; }}
    .badge {{ font-style:normal; font-size:0.72rem; background:#12352f; color:#3ecfb2; border-radius:999px; padding:2px 8px; margin-left:6px; }}
    .badge.other {{ background:#1b2433; color:#9db0c8; }}
    .wbar {{ height:6px; background:#0b1220; border-radius:6px; margin-top:10px; }}
    .wbar i {{ display:block; height:6px; background:#3ecfb2; border-radius:6px; }}
    .next {{ background:#12352f; border-radius:12px; padding:14px 16px; margin: 14px 0; }}
    details.more {{ margin-top: 28px; border-top: 1px solid #2a3b55; padding-top: 14px; }}
    details.more summary {{ cursor:pointer; color:#9db0c8; font-size:0.95rem; }}
    .paper.context {{ outline:1px dashed #f4b942; }}
    .context-list {{ display:grid; grid-template-columns: 1fr 1fr; gap:10px; }}
    @media (max-width: 800px) {{ .context-list {{ grid-template-columns: 1fr; }} }}
    ul {{ color:#c5d4e8; }}
    @media (max-width: 800px) {{
      .hero {{ grid-template-columns: 1fr; }}
      .barrow {{ grid-template-columns: 1fr; }}
      .big {{ font-size:2.4rem; }}
      .sliderline {{ grid-template-columns: 1fr; }}
    }}
    """
    body = f"""
    <p class="muted">You already picked a gel. This page looks it up in the extracted table.</p>
    <h1>Look up this protocol</h1>
    <p class="sub">Change the gel. The number follows the literature — not a simulator.</p>
    <form method="get" action="/lookup">
      <input type="hidden" name="lang" value="{lang}"/>
      <fieldset>
        <legend>Protocol you are considering</legend>
      <label>Hydrogel
        <select name="material_class" onchange="this.form.submit()">{_grouped_material_options(material_class, literature.get("material_counts"))}</select>
      </label>
      <label>Stiffness (kPa)
        <div class="sliderline">
          <input type="range" min="0.5" max="60" step="0.5" value="{kpa_slider}" aria-label="Stiffness in kPa" oninput="document.getElementById('kpa').value=this.value" onchange="this.form.submit()"/>
          <input id="kpa" type="number" name="stiffness_kpa" min="0.5" max="200" step="0.5" value="{stiffness_kpa}" onchange="this.form.submit()"/>
        </div>
        <span class="ticks">0.5 soft · 25 typical in vitro · 60 stiff for a cartilage gel</span>
      </label>
      <label>Cells
        <select name="cell_type" onchange="this.form.submit()">{_options(CELL_TYPES, cell_type, CELL_LABELS)}</select>
      </label>
      <label>Growth factor
        <select name="growth_factor" onchange="this.form.submit()">{_options(GROWTH_FACTORS, growth_factor, GF_LABELS)}</select>
      </label>
      <label>Days in culture
        <div class="sliderline">
          <input type="range" min="1" max="42" step="1" value="{int(culture_time_days)}" aria-label="Days in culture" oninput="document.getElementById('days').value=this.value" onchange="this.form.submit()"/>
          <input id="days" type="number" name="culture_time_days" min="1" max="42" step="1" value="{int(culture_time_days)}" onchange="this.form.submit()"/>
        </div>
        <span class="ticks">7 · 14 · 21 · 28 days — the timepoints papers actually use</span>
      </label>
      <button type="submit">Update evidence</button>
      </fieldset>
    </form>
    {next_html}
    <p class="verdict" id="resultado">{verdict}</p>
    <div class="hero">
      <div class="card">
        <div class="muted">Literature live/dead estimate</div>
        <div class="big">{escape(mean_s)}</div>
        <div class="muted">band {escape(band_s)} · {escape(reasons_s)}</div>
        {_trust_meter(trust)}
        <div class="chips">
          <span>{escape(str(n_mat))} numeric of this gel</span>
          <span>{escape(str(n_table))} in the table ({escape(str(n_qual))} floors)</span>
          <span>effective n on this gel {escape(str(n_eff_same))}</span>
          <span>{escape(str(n_kpa))} numeric with kPa</span>
          <span>published {escape(range_s)}</span>
          <span>{escape(str(miss))}% of numeric table missing kPa</span>
          <span>vs GelMA+TGF {escape(vs_s)} ({escape(delta_s)})</span>
        </div>
      </div>
      <div class="card">
        <div class="muted">Where this number sits</div>
        {_numberline_svg(mean, prior, local, competitor.get("mean"), low, high)}
        <p class="muted">Yellow = estimate. Blue = material mean. Purple = what a PI already runs (GelMA 25 kPa + TGF-β3). Grey = matched-condition mean before shrinkage.</p>
      </div>
    </div>
    {_context_cards(literature.get("also_extracted") or [])}
    <h2>Nearest extracted papers</h2>
    <p class="muted">Open the DOI. The bar is kernel weight — not a quality score. Green outline = the gel you picked.</p>
    {_paper_cards(literature.get("similar") or [], material_class)}
    <details class="more">
      <summary>How this number is made — map, knobs, LOPO</summary>
    {_alt_cards(literature.get("alternatives") or [], None if mean is None else float(mean))}
    <h2>Evidence map</h2>
    <p class="legend"><b class="dot">● this gel</b><b class="sq">■ others</b><b class="tri">▲ your query ± band</b><b class="dia">◆ GelMA+TGF</b></p>
    {_scatter_svg(literature.get("chart_points") or [], stiffness_kpa, mean, low, high, competitor.get("stiffness_kpa"), competitor.get("mean"))}
    {_delta_bars(literature.get("knob_deltas") or [])}
    <h2>How honest is the error</h2>
    <p class="muted">{escape(var_s)} Dummy vs shrinkage vs the MVP bar (15% better than the mean). R² is still ~0.</p>
    {_lopo_svg(lopo)}
    <h2>Limitations (so you are not fooled)</h2>
    <ul>{notes}</ul>
    </details>
    """
    title = "TissueLab — look up a gel" if lang == "en" else "TissueLab — consultar um gel"
    return render_shell(title=title, lang=lang, page="/lookup", body=body, extra_css=extra_css)


def _viability_cell(row: dict) -> str:
    if row.get("viability_pct") is not None:
        sd = row.get("viability_sd")
        sd_s = f" ±{sd:.1f}" if sd is not None else ""
        return f"<span class='pill num'>{row['viability_pct']:.1f}%{sd_s}</span>"
    label = row.get("qualitative_label") or "reported, no %"
    return f"<span class='pill qual'>{escape(str(label))}</span>"


def render_table_page(
    rows: list[dict],
    material_class: str | None,
    lang: str = "en",
    all_materials: list[str] | None = None,
) -> str:
    lang = normalize_lang(lang)
    mats = all_materials or sorted({r["material_class"] for r in rows if r.get("material_class")})
    options = ['<option value="">All gels</option>']
    for mat in mats:
        sel = " selected" if mat == material_class else ""
        options.append(f'<option value="{escape(mat)}"{sel}>{escape(_label(MATERIAL_LABELS, mat))}</option>')
    trs = []
    for row in rows:
        doi = row.get("doi") or ""
        cite = escape(str(row.get("citation") or row.get("study_id")))
        title = f'<a href="https://doi.org/{escape(doi)}" target="_blank" rel="noreferrer">{cite}</a>' if doi else cite
        kpa = row.get("stiffness_kpa")
        kpa_s = "—" if kpa is None else f"{kpa:.1f}"
        days = row.get("culture_time_days")
        days_s = "—" if days is None else f"{days:.0f}"
        gf = _label(GF_LABELS, str(row.get("growth_factor") or "none"))
        trs.append(
            "<tr>"
            f"<td>{row.get('year') or '—'}</td>"
            f"<td>{title}</td>"
            f"<td>{escape(_label(MATERIAL_LABELS, str(row.get('material_class'))))}</td>"
            f"<td>{kpa_s}</td>"
            f"<td>{escape(_label(CELL_LABELS, str(row.get('cell_type') or '—')))}</td>"
            f"<td>{escape(gf)}</td>"
            f"<td>{days_s}</td>"
            f"<td>{_viability_cell(row)}</td>"
            "</tr>"
        )
    n_num = sum(1 for r in rows if r.get("viability_pct") is not None)
    n_qual = len(rows) - n_num
    body = f"""
    <h1>Extracted live/dead table</h1>
    <p class="sub">This is the product: every hand-curated viability row. Yellow pills are floors or “high” — not means. Numeric rows train the Predict number. Auto-promoted abstracts are not here.</p>
    <form method="get" action="/table" style="display:flex;gap:12px;align-items:end;flex-wrap:wrap;margin:12px 0 18px">
      <input type="hidden" name="lang" value="{lang}"/>
      <label>Filter hydrogel
        <select name="material_class" onchange="this.form.submit()">{"".join(options)}</select>
      </label>
      <a href="/export.csv">Download CSV</a>
      <span class="muted">{n_num} numeric · {n_qual} qualitative · {len(rows)} rows</span>
    </form>
    <div style="overflow:auto">
    <table class="data">
      <thead><tr><th>Year</th><th>Paper</th><th>Gel</th><th>kPa</th><th>Cells</th><th>GF</th><th>Days</th><th>Live/dead</th></tr></thead>
      <tbody>{"".join(trs) or "<tr><td colspan='8'>No rows.</td></tr>"}</tbody>
    </table>
    </div>
    """
    extra = "select, input { background:#0b1220; color:#e8eef7; border:1px solid #2a3b55; border-radius:8px; padding:8px; font-size:1rem; } label { color:#9db0c8; font-size:0.85rem; display:flex; flex-direction:column; gap:6px; }"
    return render_shell(title="TissueLab — extracted table", lang=lang, page="/table", body=body, extra_css=extra)


def render_compare_page(left: dict, right: dict, left_design: dict, right_design: dict, lang: str = "en") -> str:
    lang = normalize_lang(lang)
    extra = """
    .card { background:#152033; border-radius:12px; padding:16px; }
    .big { font-size:2.4rem; color:#f4b942; font-weight:800; margin:8px 0; }
    label { display:flex; flex-direction:column; gap:6px; font-size:0.85rem; color:#9db0c8; margin-bottom:8px; }
    select, input { background:#0b1220; color:#e8eef7; border:1px solid #2a3b55; border-radius:8px; padding:8px; font-size:1rem; }
    .paper { background:#0b1220; border-radius:12px; padding:12px; margin-bottom:8px; }
    .paper h3 { margin:0 0 6px; font-size:0.95rem; }
    .badge { font-style:normal; font-size:0.72rem; background:#12352f; color:#3ecfb2; border-radius:999px; padding:2px 8px; margin-left:6px; }
    .badge.other { background:#1b2433; color:#9db0c8; }
    .wbar { height:6px; background:#152033; border-radius:6px; margin-top:8px; }
    .wbar i { display:block; height:6px; background:#3ecfb2; border-radius:6px; }
    .delta { background:#152033; border-left:4px solid #f4b942; padding:12px 14px; border-radius:0 12px 12px 0; margin: 0 0 16px; }
    """

    def fields(prefix, design, lit):
        mean = lit.get("mean")
        mean_s = "—" if mean is None else f"{mean:.1f}%"
        band = ""
        if mean is not None and lit.get("low") is not None:
            band = f"{lit['low']:.0f}–{lit['high']:.0f}"
        trust = lit.get("trust") or {}
        papers = _paper_cards((lit.get("similar") or [])[:3], design.get("material_class"))
        return f"""
        <section class="card">
          <h2>{"A · your gel" if prefix=="a" else "B · comparator"}</h2>
          <label>Hydrogel
            <select name="{prefix}_material" onchange="this.form.submit()">{_grouped_material_options(design["material_class"], lit.get("material_counts"))}</select>
          </label>
          <label>Stiffness (kPa)
            <input type="number" name="{prefix}_kpa" min="0.5" max="200" step="0.5" value="{design["stiffness_kpa"]}" onchange="this.form.submit()"/>
          </label>
          <label>Growth factor
            <select name="{prefix}_gf" onchange="this.form.submit()">{_options(GROWTH_FACTORS, design["growth_factor"], GF_LABELS)}</select>
          </label>
          <p class="big">{escape(mean_s)}</p>
          <p class="muted">band {escape(band)} · {escape(trust.get("label") or "")}</p>
          <p>{escape(lit.get("verdict") or "")}</p>
          {papers}
        </section>
        """

    left_mean = left.get("mean")
    right_mean = right.get("mean")
    if left_mean is None or right_mean is None:
        delta_html = "<p class='delta'>One or both sides have no literature number yet — read the papers.</p>"
    else:
        d = float(left_mean) - float(right_mean)
        if abs(d) < 0.05:
            gap = "level with"
        elif d > 0:
            gap = "higher than"
        else:
            gap = "lower than"
        delta_html = (
            f"<p class='delta'>A is {abs(d):.1f} pp {gap} B on the same literature estimator. "
            "If either trust badge is weak, use the papers, not this gap.</p>"
        )

    body = f"""
    <h1>Compare two protocols</h1>
    <p class="sub">The question a PI actually has: is fibrin better than GelMA + TGF-β3 for <em>this</em> week? Same estimator on both sides.</p>
    {delta_html}
    <form method="get" action="/compare" class="compare-grid">
      <input type="hidden" name="lang" value="{lang}"/>
      {fields("a", left_design, left)}
      {fields("b", right_design, right)}
    </form>
    """
    return render_shell(title="TissueLab — compare", lang=lang, page="/compare", body=body, extra_css=extra)


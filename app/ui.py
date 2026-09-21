"""Plain HTML Predict UI — no WebSocket, so Cursor's Simple Browser can open it."""

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


def _papers_table(rows: list[dict]) -> str:
    if not rows:
        return "<p class='muted'>No extracted live/dead rows yet.</p>"
    body = []
    for row in rows:
        doi = row.get("doi") or ""
        cite = escape(str(row.get("citation") or row.get("study_id") or ""))
        if doi:
            cite = f'<a href="https://doi.org/{escape(doi)}" target="_blank" rel="noreferrer">{cite}</a>'
        kpa = row.get("stiffness_kpa")
        kpa_s = "—" if kpa is None else f"{kpa:.1f}"
        body.append(
            "<tr>"
            f"<td>{cite}</td>"
            f"<td>{escape(str(row.get('material_class') or ''))}</td>"
            f"<td>{escape(str(row.get('cell_type') or ''))}</td>"
            f"<td>{kpa_s}</td>"
            f"<td>{float(row['viability_pct']):.0f}%</td>"
            "</tr>"
        )
    return (
        "<table><thead><tr>"
        "<th>Paper</th><th>Gel</th><th>Cells</th><th>kPa</th><th>Live/dead</th>"
        "</tr></thead><tbody>"
        + "".join(body)
        + "</tbody></table>"
    )


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
    mae = lopo.get("deployed_mae")
    mean_s = "—" if mean is None else f"{mean:.0f}%"
    band_s = "" if mean is None else f"{low:.0f}–{high:.0f}"
    mae_s = "—" if mae is None else f"{mae:.1f}"
    notes = "".join(f"<li>{escape(note)}</li>" for note in (literature.get("notes") or []))
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8"/>
  <meta name="viewport" content="width=device-width, initial-scale=1"/>
  <title>TissueLab AI — Predict</title>
  <style>
    :root {{ color-scheme: dark; }}
    body {{ margin:0; font-family: ui-sans-serif, system-ui, sans-serif; background:#0b1220; color:#e8eef7; }}
    main {{ max-width: 980px; margin: 0 auto; padding: 28px 20px 64px; }}
    h1 {{ margin: 0 0 6px; font-size: 1.7rem; }}
    .sub {{ color:#9db0c8; margin-bottom: 22px; }}
    form {{ display:grid; grid-template-columns: repeat(auto-fit, minmax(180px, 1fr)); gap: 12px; background:#152033; padding:16px; border-radius:12px; }}
    label {{ display:flex; flex-direction:column; gap:6px; font-size: 0.85rem; color:#9db0c8; }}
    select, input {{ background:#0b1220; color:#e8eef7; border:1px solid #2a3b55; border-radius:8px; padding:8px 10px; }}
    button {{ grid-column: 1 / -1; background:#3ecfb2; color:#07231d; border:0; border-radius:8px; padding:10px 14px; font-weight:700; cursor:pointer; }}
    .metrics {{ display:grid; grid-template-columns: repeat(3, 1fr); gap:12px; margin: 22px 0; }}
    .card {{ background:#152033; border-radius:12px; padding:16px; }}
    .card b {{ display:block; color:#9db0c8; font-size:0.8rem; font-weight:600; margin-bottom:6px; }}
    .card span {{ font-size:1.8rem; color:#3ecfb2; font-weight:700; }}
    .card em {{ display:block; color:#9db0c8; font-style:normal; margin-top:4px; }}
    table {{ width:100%; border-collapse: collapse; background:#152033; border-radius:12px; overflow:hidden; }}
    th, td {{ text-align:left; padding:10px 12px; border-bottom:1px solid #243044; font-size:0.92rem; }}
    th {{ color:#9db0c8; font-weight:600; }}
    a {{ color:#3ecfb2; }}
    .muted {{ color:#9db0c8; }}
    ul {{ color:#c5d4e8; }}
    @media (max-width: 700px) {{ .metrics {{ grid-template-columns: 1fr; }} }}
  </style>
</head>
<body>
  <main>
    <h1>TissueLab AI</h1>
    <p class="sub">Hydrogel → chondrocyte. Literature live/dead from the hand-curated table. This page works in the Cursor browser (no Streamlit websocket).</p>
    <form method="get" action="/">
      <label>Hydrogel
        <select name="material_class" onchange="this.form.submit()">{_options(MATERIALS, material_class)}</select>
      </label>
      <label>Stiffness (kPa)
        <input type="number" name="stiffness_kpa" min="0.5" max="200" step="0.5" value="{stiffness_kpa}"/>
      </label>
      <label>Cell type
        <select name="cell_type" onchange="this.form.submit()">{_options(CELL_TYPES, cell_type)}</select>
      </label>
      <label>Growth factor
        <select name="growth_factor" onchange="this.form.submit()">{_options(GROWTH_FACTORS, growth_factor)}</select>
      </label>
      <label>Culture time (days)
        <input type="number" name="culture_time_days" min="1" max="42" step="1" value="{int(culture_time_days)}"/>
      </label>
      <button type="submit">Update prediction</button>
    </form>
    <div class="metrics">
      <div class="card"><b>Literature viability</b><span>{escape(mean_s)}</span><em>{escape(band_s)}</em></div>
      <div class="card"><b>LOPO MAE</b><span>{escape(mae_s)}</span><em>{escape(str(lopo.get("deployed_estimator") or "material_mean"))}</em></div>
      <div class="card"><b>Papers in split</b><span>{escape(str(lopo.get("n_studies") or "—"))}</span><em>hand-curated live/dead</em></div>
    </div>
    <h2>Nearest extracted papers</h2>
    {_papers_table(literature.get("similar") or [])}
    <h2>How to read this</h2>
    <ul>{notes}</ul>
  </main>
</body>
</html>
"""

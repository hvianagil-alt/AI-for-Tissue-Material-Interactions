"""Shared chrome for the buyable HTML product. No WebSocket."""

from __future__ import annotations

from html import escape

NAV = (
    ("/", "Protocol", "Protocolo"),
    ("/lookup", "Lookup", "Consulta"),
    ("/table", "Table", "Tabela"),
    ("/library", "Library", "Biblioteca"),
    ("/compare", "Compare", "Comparar"),
    ("/export.csv", "CSV", "CSV"),
)

COPY = {
    "en": {
        "product": "TissueLab",
        "tagline": "Extracted protocols for cartilage hydrogels.",
        "skip": "Skip to result",
        "lang_switch": "PT",
        "lang_href": "?lang=pt",
        "onboard": "Tell us the cells and the job. We rank extracted protocols, then search papers. Not a virtual flask.",
        "onboard_short": "Cells + job → a protocol from the table, then papers.",
    },
    "pt": {
        "product": "TissueLab",
        "tagline": "Protocolos extraídos para hidrogéis de cartilagem.",
        "skip": "Saltar para o resultado",
        "lang_switch": "EN",
        "lang_href": "?lang=en",
        "onboard": "Diz as células e o que queres. Ordenamos protocolos extraídos e procuramos papers. Não é um frasco virtual.",
        "onboard_short": "Células + objetivo → um protocolo da tabela, depois papers.",
    },
}

BASE_CSS = """
    :root { color-scheme: dark; }
    body { margin:0; font-family: ui-sans-serif, system-ui, sans-serif; background:#0b1220; color:#e8eef7; line-height:1.45; }
    a.skip { position:absolute; left:-999px; }
    a.skip:focus { left:12px; top:12px; background:#3ecfb2; color:#07231d; padding:8px 12px; z-index:9; }
    header.top { border-bottom:1px solid #2a3b55; background:#0e1728; }
    header.top .inner { max-width:1040px; margin:0 auto; padding:10px 18px; display:flex; gap:16px; align-items:center; flex-wrap:wrap; }
    header.top .brand { font-weight:800; color:#e8eef7; text-decoration:none; letter-spacing:-0.03em; }
    header.top nav { display:flex; gap:8px; flex-wrap:wrap; }
    header.top nav a { color:#9db0c8; text-decoration:none; padding:6px 10px; border-radius:8px; font-size:0.92rem; }
    header.top nav a:hover, header.top nav a[aria-current="page"] { background:#152033; color:#3ecfb2; }
    header.top .lang { margin-left:auto; color:#9db0c8; font-size:0.85rem; }
    .onboard { max-width:1040px; margin:0 auto; padding:12px 18px 0; color:#c5d4e8; font-size:0.92rem; }
    .onboard strong { color:#f4b942; }
    main { max-width: 1040px; margin: 0 auto; padding: 18px 18px 72px; }
    h1 { margin: 0 0 4px; font-size: 1.85rem; }
    h2 { margin: 28px 0 10px; font-size: 1.15rem; }
    .sub, .muted { color:#9db0c8; }
    a { color:#3ecfb2; }
    table.data { width:100%; border-collapse:collapse; font-size:0.88rem; }
    table.data th, table.data td { text-align:left; padding:8px 10px; border-bottom:1px solid #2a3b55; vertical-align:top; }
    table.data th { color:#9db0c8; font-weight:600; }
    table.data tr:hover td { background:#152033; }
    .pill { display:inline-block; border-radius:999px; padding:2px 8px; font-size:0.75rem; border:1px solid #2a3b55; color:#c5d4e8; }
    .pill.num { background:#12352f; color:#3ecfb2; border-color:#1d5c52; }
    .pill.qual { background:#2a2414; color:#f4b942; border-color:#5c4a1d; }
    .compare-grid { display:grid; grid-template-columns: 1fr 1fr; gap:14px; }
    @media (max-width: 800px) { .compare-grid { grid-template-columns: 1fr; } }
"""


def normalize_lang(lang: str | None) -> str:
    return "pt" if str(lang or "").lower().startswith("pt") else "en"


def render_shell(
    *,
    title: str,
    lang: str,
    page: str,
    body: str,
    extra_css: str = "",
    extra_head: str = "",
    onboard: str | bool = True,
    qs: str = "",
) -> str:
    lang = normalize_lang(lang)
    copy = COPY[lang]
    other = "pt" if lang == "en" else "en"
    links = []
    for href, en, pt in NAV:
        label = pt if lang == "pt" else en
        current = ' aria-current="page"' if href.rstrip("/") == page.rstrip("/") or (page == "/" and href == "/") else ""
        if href.endswith(".csv"):
            lang_q = ""
        else:
            lang_q = f"{'&' if '?' in href else '?'}lang={lang}"
        links.append(f'<a href="{escape(href + lang_q)}"{current}>{escape(label)}</a>')
    if qs:
        switch_href = f"{page}?{qs}&lang={other}" if page not in {"/", ""} else f"?{qs}&lang={other}"
    elif page not in {"/", ""}:
        switch_href = f"{page}?lang={other}"
    else:
        switch_href = f"?lang={other}"
    if onboard == "short":
        onboard_html = f"<p class='onboard'>{escape(copy['onboard_short'])}</p>"
    elif onboard:
        onboard_html = f"<p class='onboard'>{escape(copy['onboard'])}</p>"
    else:
        onboard_html = ""
    return f"""<!DOCTYPE html>
<html lang="{lang}">
<head>
  <meta charset="utf-8"/>
  <meta name="viewport" content="width=device-width, initial-scale=1"/>
  <title>{escape(title)}</title>
  <style>
{BASE_CSS}
{extra_css}
  </style>
  {extra_head}
</head>
<body>
  <a class="skip" href="#resultado">{escape(copy["skip"])}</a>
  <header class="top">
    <div class="inner">
      <a class="brand" href="/?lang={lang}">{escape(copy["product"])}</a>
      <nav>{"".join(links)}</nav>
      <a class="lang" href="{escape(switch_href)}">{escape(copy["lang_switch"])}</a>
    </div>
  </header>
  {onboard_html}
  <main>
    {body}
  </main>
</body>
</html>
"""

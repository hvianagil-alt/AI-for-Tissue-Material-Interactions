"""Europe PMC — free OA literature search and fulltext.

Better than paying Amass for article bodies. BIOMATDB and OOCDB are search
portals, not a material×cell outcome table. Europe PMC XML is the open
fulltext we can actually parse.
"""

from __future__ import annotations

import html
import json
import re
import time
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime, timezone

from tissuelab.db import connect, init_schema
from tissuelab.extract import extract_from_abstract
from tissuelab.harvest_amass import upsert_paper
from tissuelab.paths import DATA_DIR, DB_PATH

SEARCH_URL = "https://www.ebi.ac.uk/europepmc/webservices/rest/search"
FT_URL = "https://www.ebi.ac.uk/europepmc/webservices/rest/{pmcid}/fullTextXML"
HEADERS = {"User-Agent": "TissueLabAI/0.1 (hydrogel-chondrocyte literature harvest)"}
CACHE_DIR = DATA_DIR / "fulltext_cache"
SLEEP_S = 0.85
SEARCH_PAGES = 5
LIBRARY_PAGES = 3
PAGE_SIZE = 100

QUERIES = [
    '"chondrocyte" AND hydrogel AND (viability OR "live/dead" OR "Young" OR kPa) AND OPEN_ACCESS:y AND HAS_FT:y',
    'GelMA AND (chondrocyte OR chondrogenesis) AND OPEN_ACCESS:y AND HAS_FT:y',
    '"cartilage" AND hydrogel AND (stiffness OR modulus) AND OPEN_ACCESS:y AND HAS_FT:y',
    '(methacrylated OR GelMA OR HAMA OR MeHA) AND chondrocyte AND hydrogel AND OPEN_ACCESS:y AND HAS_FT:y',
    '(oxidized OR norbornene OR tyramine OR "thiol-ene") AND hydrogel AND (chondrocyte OR cartilage) AND OPEN_ACCESS:y AND HAS_FT:y',
    '(bioprint OR bioink) AND chondrocyte AND (viability OR live) AND OPEN_ACCESS:y AND HAS_FT:y',
    '("interpenetrating" OR granular OR microgel) AND hydrogel AND cartilage AND OPEN_ACCESS:y AND HAS_FT:y',
    '(genipin OR "EDC" OR dopamine OR RGD) AND hydrogel AND (chondrocyte OR cartilage) AND OPEN_ACCESS:y AND HAS_FT:y',
    '(auricular OR osteochondral OR osteoarthritis) AND hydrogel AND chondrocyte AND OPEN_ACCESS:y AND HAS_FT:y',
    '(injectable OR tyramine OR sulfated) AND hydrogel AND cartilage AND OPEN_ACCESS:y AND HAS_FT:y',
]

LIBRARY_QUERIES = [
    'chondrocyte AND hydrogel AND (viability OR "live/dead") AND HAS_ABSTRACT:y',
    'GelMA AND chondrocyte AND (viability OR live) AND HAS_ABSTRACT:y',
    'methacrylated AND hydrogel AND cartilage AND HAS_ABSTRACT:y',
    '(bioprint OR bioink) AND chondrocyte AND hydrogel AND HAS_ABSTRACT:y',
    'osteoarthritis AND hydrogel AND (chondrocyte OR MSC) AND HAS_ABSTRACT:y',
    'auricular AND (GelMA OR hydrogel) AND chondrocyte AND HAS_ABSTRACT:y',
]


def xml_to_text(xml: str) -> str:
    xml = re.sub(r"<script[^>]*>.*?</script>", " ", xml, flags=re.S | re.I)
    xml = re.sub(r"<style[^>]*>.*?</style>", " ", xml, flags=re.S | re.I)
    text = re.sub(r"<[^>]+>", " ", xml)
    text = html.unescape(text)
    return " ".join(text.split())


def _get(url: str) -> bytes:
    req = urllib.request.Request(url, headers=HEADERS)
    with urllib.request.urlopen(req, timeout=90) as resp:
        return resp.read()


def fetch_pmc_fulltext(pmcid: str | None) -> str | None:
    if not pmcid:
        return None
    pmcid = str(pmcid).strip()
    if not pmcid.upper().startswith("PMC"):
        pmcid = "PMC" + pmcid
    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    cached = CACHE_DIR / f"{pmcid}.txt"
    if cached.exists():
        text = cached.read_text(errors="replace")
        return text[:80000] if len(text) >= 400 else None
    url = FT_URL.format(pmcid=urllib.parse.quote(pmcid))
    try:
        raw = _get(url).decode("utf-8", errors="replace")
    except urllib.error.HTTPError as exc:
        if exc.code == 429:
            time.sleep(6)
            return fetch_pmc_fulltext(pmcid)
        return None
    except urllib.error.URLError:
        return None
    if "<error" in raw[:400].lower() or "fullTextXML" in raw[:80] and "not available" in raw.lower():
        if len(raw) < 500:
            return None
    text = xml_to_text(raw)
    if len(text) < 400:
        return None
    text = text[:80000]
    cached.write_text(text)
    return text


def search(query: str, cursor: str = "*", page_size: int | None = None) -> dict:
    params = {
        "query": query,
        "format": "json",
        "pageSize": str(page_size or PAGE_SIZE),
        "cursorMark": cursor,
        "resultType": "core",
    }
    url = SEARCH_URL + "?" + urllib.parse.urlencode(params)
    return json.loads(_get(url).decode("utf-8"))


def _year(date: str | None) -> int | None:
    if not date:
        return None
    try:
        return int(str(date)[:4])
    except ValueError:
        return None


def hit_to_record(hit: dict) -> dict:
    pmid = str(hit.get("pmid") or "") or None
    pmcid = hit.get("pmcid") or None
    doi = hit.get("doi")
    authors = []
    for a in (hit.get("authorList") or {}).get("author") or []:
        name = a.get("fullName") or " ".join(filter(None, [a.get("lastName"), a.get("initials")]))
        if name:
            authors.append(name)
    pub_types = []
    for p in (hit.get("pubTypeList") or {}).get("pubType") or []:
        pub_types.append(p if isinstance(p, str) else str(p))
    ji = hit.get("journalInfo") or {}
    journal_obj = ji.get("journal") if isinstance(ji.get("journal"), dict) else {}
    journal = (journal_obj or {}).get("title") or hit.get("journalTitle")
    amass_id = f"EPMC_{pmid or pmcid or hit.get('id')}"
    date = hit.get("firstPublicationDate") or hit.get("electronicPublicationDate")
    return {
        "amassId": amass_id,
        "pmid": pmid,
        "pmcid": pmcid,
        "doi": doi,
        "title": hit.get("title"),
        "abstract": hit.get("abstractText"),
        "journal": journal,
        "publicationDate": date,
        "citationCount": hit.get("citedByCount"),
        "journalQualityJufo": None,
        "hasFulltext": bool(pmcid),
        "isRetracted": False,
        "publicationTypes": pub_types,
        "meshTerms": None,
        "keywords": None,
        "substances": None,
        "authors": authors,
        "language": hit.get("language"),
    }


def _ingest_hits(conn, query: str, pages: int, existing_pmid: set[str]) -> tuple[int, int]:
    n_new = 0
    n_hits = 0
    cursor = "*"
    for _ in range(pages):
        payload = search(query, cursor)
        hits = ((payload.get("resultList") or {}).get("result")) or []
        if not hits:
            break
        for hit in hits:
            rec = hit_to_record(hit)
            n_hits += 1
            if rec["pmid"] and rec["pmid"] in existing_pmid:
                continue
            if rec["pmid"]:
                existing_pmid.add(rec["pmid"])
            if upsert_paper(conn, rec, f"europepmc|{query[:40]}"):
                n_new += 1
        nxt = payload.get("nextCursorMark")
        if not nxt or nxt == cursor:
            break
        cursor = nxt
        time.sleep(SLEEP_S)
    time.sleep(SLEEP_S)
    return n_new, n_hits


def harvest(path=DB_PATH) -> dict:
    conn = connect(path)
    init_schema(conn)
    existing_pmid = {
        str(r[0]) for r in conn.execute("SELECT pmid FROM papers WHERE pmid IS NOT NULL").fetchall()
    }
    n_new = 0
    n_hits = 0
    for query in QUERIES:
        added, hits = _ingest_hits(conn, query, SEARCH_PAGES, existing_pmid)
        n_new += added
        n_hits += hits
        conn.commit()
    for query in LIBRARY_QUERIES:
        added, hits = _ingest_hits(conn, query, LIBRARY_PAGES, existing_pmid)
        n_new += added
        n_hits += hits
        conn.commit()
    conn.execute(
        """
        INSERT INTO harvest_log (
            query, min_publication_date, max_publication_date, limit_requested,
            n_returned, n_new, http_status, credit_cost, requested_at
        ) VALUES (?, NULL, NULL, ?, ?, ?, 200, 0, ?)
        """,
        (
            "europepmc_oa+library",
            PAGE_SIZE * (SEARCH_PAGES * len(QUERIES) + LIBRARY_PAGES * len(LIBRARY_QUERIES)),
            n_hits,
            n_new,
            datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        ),
    )
    conn.commit()
    n_papers = conn.execute("SELECT COUNT(*) FROM papers").fetchone()[0]
    n_epmc = conn.execute("SELECT COUNT(*) FROM papers WHERE amass_id LIKE 'EPMC_%'").fetchone()[0]
    conn.close()
    return {"n_new": n_new, "n_hits": n_hits, "n_papers": n_papers, "n_europepmc_rows": n_epmc}


def main() -> None:
    report = harvest()
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()

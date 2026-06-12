"""Fetch RSS/Atom feeds with ETag/Last-Modified caching and per-source try/except.

Used by digest.py. One feed dying must NOT kill the run — the surface for
failures is data/source-status.json (rendered on /sources page).
"""

from __future__ import annotations

import json
import re
import time
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any

import feedparser
import httpx
import yaml
from dateutil import parser as dtparser

from models import Category, Lang, RawItem, SourceStatusEntry


REPO_ROOT = Path(__file__).resolve().parent.parent
SOURCES_FILE = REPO_ROOT / "sources.yaml"
CACHE_DIR = REPO_ROOT / "data" / "feed-cache"
SEEN_FILE = CACHE_DIR / "seen.json"
ETAG_FILE = CACHE_DIR / "etags.json"

# CrossRef REST API — used for peer-reviewed journals whose publisher RSS sits
# behind Cloudflare and 403s GitHub Actions' datacenter IPs. CrossRef is open
# JSON with no IP gating, queried by eISSN. We pull the most recently registered
# works; the downstream 72h freshness filter narrows from there.
CROSSREF_BASE = "https://api.crossref.org/journals"
CROSSREF_LOOKBACK_DAYS = 30

# EuropePMC + OpenAlex REST APIs — open JSON, no key, no reCAPTCHA. These replace
# the dead PubMed RSS (now reCAPTCHA-walled) and add MEDLINE/PMC + preprint
# coverage. Crucially they ship publication-type / MeSH metadata, which grounds
# evidence grading downstream instead of leaving it a pure LLM guess.
EUROPEPMC_SEARCH = "https://www.ebi.ac.uk/europepmc/webservices/rest/search"
OPENALEX_WORKS = "https://api.openalex.org/works"
LITERATURE_LOOKBACK_DAYS = 21


def utcnow() -> datetime:
    return datetime.now(timezone.utc)


def load_sources() -> tuple[dict[str, Any], list[dict[str, Any]]]:
    raw = yaml.safe_load(SOURCES_FILE.read_text())
    return raw.get("defaults", {}) or {}, raw.get("sources", []) or []


def _load_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    try:
        return json.loads(path.read_text())
    except json.JSONDecodeError:
        return {}


def _save_json(path: Path, data: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, sort_keys=True, default=str))


def _parse_date(value: str | None) -> datetime | None:
    if not value:
        return None
    try:
        d = dtparser.parse(value)
        if d.tzinfo is None:
            d = d.replace(tzinfo=timezone.utc)
        return d.astimezone(timezone.utc)
    except (ValueError, TypeError):
        return None


def _excerpt(entry: Any, limit: int = 280) -> str:
    for key in ("summary", "description", "content"):
        v = entry.get(key)
        if isinstance(v, list) and v:
            v = v[0].get("value")
        if isinstance(v, str) and v.strip():
            text = re.sub(r"<[^>]+>", "", v)
            text = re.sub(r"\s+", " ", text).strip()
            return text[:limit]
    return ""


def _strip_tags(value: str | None, limit: int = 280) -> str:
    """CrossRef abstracts are JATS XML (<jats:p>…</jats:p>). Strip to plain text."""
    if not value:
        return ""
    text = re.sub(r"<[^>]+>", " ", value)
    text = re.sub(r"\s+", " ", text).strip()
    return text[:limit]


def _crossref_datetime(part: Any) -> datetime | None:
    """Parse a CrossRef date object (either {date-time: …} or {date-parts: [[y,m,d]]})."""
    if not isinstance(part, dict):
        return None
    if dt := part.get("date-time"):
        return _parse_date(dt)
    parts = part.get("date-parts") or []
    if parts and isinstance(parts[0], list) and parts[0] and parts[0][0]:
        y, *rest = parts[0]
        m = rest[0] if len(rest) >= 1 and rest[0] else 1
        d = rest[1] if len(rest) >= 2 and rest[1] else 1
        try:
            return datetime(int(y), int(m), int(d), tzinfo=timezone.utc)
        except (ValueError, TypeError):
            return None
    return None


def _crossref_author(authors: Any) -> str | None:
    if not isinstance(authors, list) or not authors:
        return None
    first = authors[0]
    name = " ".join(p for p in (first.get("given"), first.get("family")) if p).strip()
    if not name:
        name = (first.get("name") or "").strip()
    if not name:
        return None
    return f"{name} et al." if len(authors) > 1 else name


def fetch_crossref(
    source: dict[str, Any],
    defaults: dict[str, Any],
    *,
    seen: dict[str, str],
    client: httpx.Client,
) -> tuple[list[RawItem], SourceStatusEntry]:
    sid: str = source["id"]
    issn: str = source["issn"]
    language: Lang = source["language"]
    name: str = source["name"]
    primary_cat: Category | None = source.get("primaryCategory")
    max_items: int = int(source.get("maxItems", defaults.get("maxItems", 30)))
    mailto: str = defaults.get("mailto", "almanac@users.noreply.github.com")

    now = utcnow()
    cutoff = (now - timedelta(days=CROSSREF_LOOKBACK_DAYS)).strftime("%Y-%m-%d")
    params = {
        "filter": f"from-created-date:{cutoff}",
        "sort": "created",
        "order": "desc",
        "rows": str(max_items),
        "select": "DOI,title,author,abstract,URL,created,published-online,issued",
        "mailto": mailto,
    }
    headers = {"User-Agent": f"{defaults.get('userAgent', 'almanac-bot/1.0')} (mailto:{mailto})"}

    def _err(msg: str) -> tuple[list[RawItem], SourceStatusEntry]:
        return [], SourceStatusEntry(
            id=sid, name=name, url=f"{CROSSREF_BASE}/{issn}/works", language=language,
            primaryCategory=primary_cat, status="error", errorMessage=msg,
            lastFetched=now, itemsLastRun=0,
        )

    try:
        resp = client.get(
            f"{CROSSREF_BASE}/{issn}/works", params=params, headers=headers,
            timeout=defaults.get("timeoutMs", 15000) / 1000,
        )
    except Exception as exc:
        return _err(f"{type(exc).__name__}: {exc}")

    if resp.status_code >= 400:
        return _err(f"HTTP {resp.status_code}")

    try:
        works = resp.json()["message"]["items"]
    except (json.JSONDecodeError, KeyError, TypeError) as exc:
        return _err(f"bad CrossRef payload: {type(exc).__name__}")

    items: list[RawItem] = []
    for work in works:
        titles = work.get("title") or []
        title = (titles[0] if titles else "").strip()
        doi = work.get("DOI")
        url = work.get("URL") or (f"https://doi.org/{doi}" if doi else "")
        if not title or not url:
            continue

        first_seen = seen.get(url)
        first_seen_dt = _parse_date(first_seen) if first_seen else now
        if not first_seen:
            seen[url] = now.isoformat()

        published = (
            _crossref_datetime(work.get("published-online"))
            or _crossref_datetime(work.get("created"))
            or _crossref_datetime(work.get("issued"))
            or first_seen_dt
        )

        items.append(RawItem(
            source_id=sid,
            source_name=name,
            language=language,
            title=title,
            url=url,
            published_at=published,
            excerpt=_strip_tags(work.get("abstract")),
            author=_crossref_author(work.get("author")),
            first_seen_at=first_seen_dt or now,
            fetched_at=now,
        ))

    status = SourceStatusEntry(
        id=sid, name=name, url=f"{CROSSREF_BASE}/{issn}/works", language=language,
        primaryCategory=primary_cat, status="ok", lastFetched=now, itemsLastRun=len(items),
    )
    return items, status


def _first_author(author_string: str | None) -> str | None:
    """EuropePMC `authorString` is 'Smith J, Doe A, …'. Reduce to first + et al."""
    if not author_string:
        return None
    parts = [p.strip() for p in author_string.split(",") if p.strip()]
    if not parts:
        return None
    return f"{parts[0]} et al." if len(parts) > 1 else parts[0].rstrip(".")


def _track_seen(url: str, seen: dict[str, str], now: datetime) -> datetime:
    """Return first-seen datetime for a url, recording it if new."""
    first_seen = seen.get(url)
    if first_seen:
        return _parse_date(first_seen) or now
    seen[url] = now.isoformat()
    return now


def fetch_europepmc(
    source: dict[str, Any],
    defaults: dict[str, Any],
    *,
    seen: dict[str, str],
    client: httpx.Client,
) -> tuple[list[RawItem], SourceStatusEntry]:
    """Query EuropePMC for recent dental literature. `query` in sources.yaml is a
    EuropePMC search expression; we AND on a recency window + HAS_ABSTRACT."""
    sid: str = source["id"]
    name: str = source["name"]
    language: Lang = source.get("language", "en")
    primary_cat: Category | None = source.get("primaryCategory")
    max_items: int = int(source.get("maxItems", defaults.get("maxItems", 30)))
    base_query: str = source["query"]
    now = utcnow()
    cutoff = (now - timedelta(days=LITERATURE_LOOKBACK_DAYS)).strftime("%Y-%m-%d")
    today = now.strftime("%Y-%m-%d")
    full_query = (
        f"({base_query}) AND (FIRST_PDATE:[{cutoff} TO {today}]) AND (HAS_ABSTRACT:Y)"
    )
    params = {
        "query": full_query,
        "format": "json",
        "resultType": "core",
        "pageSize": str(max_items),
        "sort": "P_PDATE_D desc",
    }

    def _err(msg: str) -> tuple[list[RawItem], SourceStatusEntry]:
        return [], SourceStatusEntry(
            id=sid, name=name, url=EUROPEPMC_SEARCH, language=language,
            primaryCategory=primary_cat, status="error", errorMessage=msg,
            lastFetched=now, itemsLastRun=0,
        )

    try:
        resp = client.get(
            EUROPEPMC_SEARCH, params=params,
            timeout=defaults.get("timeoutMs", 15000) / 1000,
        )
    except Exception as exc:
        return _err(f"{type(exc).__name__}: {exc}")
    if resp.status_code >= 400:
        return _err(f"HTTP {resp.status_code}")
    try:
        results = resp.json().get("resultList", {}).get("result", [])
    except (json.JSONDecodeError, AttributeError, TypeError) as exc:
        return _err(f"bad EuropePMC payload: {type(exc).__name__}")

    items: list[RawItem] = []
    for r in results:
        title = (r.get("title") or "").strip().rstrip(".")
        doi = r.get("doi")
        pmid = r.get("pmid")
        src = r.get("source")
        if doi:
            url = f"https://doi.org/{doi}"
        elif src and (pmid or r.get("id")):
            url = f"https://europepmc.org/article/{src}/{pmid or r.get('id')}"
        else:
            continue
        if not title:
            continue
        pub_types = [
            t for t in (r.get("pubTypeList", {}) or {}).get("pubType", []) if t
        ]
        mesh = [
            m.get("descriptorName")
            for m in (r.get("meshHeadingList", {}) or {}).get("meshHeading", [])
            if m.get("descriptorName")
        ]
        first_seen_dt = _track_seen(url, seen, now)
        items.append(RawItem(
            source_id=sid,
            source_name=name,
            language=language,
            title=title,
            url=url,
            published_at=_parse_date(r.get("firstPublicationDate")) or first_seen_dt,
            excerpt=_strip_tags(r.get("abstractText"), limit=1500),
            author=_first_author(r.get("authorString")),
            first_seen_at=first_seen_dt,
            fetched_at=now,
            pub_types=pub_types,
            mesh=mesh,
        ))

    status = SourceStatusEntry(
        id=sid, name=name, url=EUROPEPMC_SEARCH, language=language,
        primaryCategory=primary_cat, status="ok", lastFetched=now, itemsLastRun=len(items),
    )
    return items, status


def _openalex_abstract(inverted: dict[str, list[int]] | None, limit: int = 1500) -> str:
    """Reconstruct plain text from OpenAlex `abstract_inverted_index`."""
    if not inverted:
        return ""
    positions: list[tuple[int, str]] = []
    for word, idxs in inverted.items():
        for i in idxs:
            positions.append((i, word))
    positions.sort(key=lambda p: p[0])
    text = " ".join(w for _, w in positions)
    return re.sub(r"\s+", " ", text).strip()[:limit]


def fetch_openalex(
    source: dict[str, Any],
    defaults: dict[str, Any],
    *,
    seen: dict[str, str],
    client: httpx.Client,
) -> tuple[list[RawItem], SourceStatusEntry]:
    """Query OpenAlex for recent dental works. `filter` is an OpenAlex filter
    expression (use a concept id for precision, not free-text); we AND on a
    recency window + has_abstract. OpenAlex `type` (article/review/preprint)
    feeds evidence grading."""
    sid: str = source["id"]
    name: str = source["name"]
    language: Lang = source.get("language", "en")
    primary_cat: Category | None = source.get("primaryCategory")
    max_items: int = int(source.get("maxItems", defaults.get("maxItems", 30)))
    base_filter: str = source["filter"]
    mailto: str = defaults.get("mailto", "almanac@users.noreply.github.com")
    now = utcnow()
    cutoff = (now - timedelta(days=LITERATURE_LOOKBACK_DAYS)).strftime("%Y-%m-%d")
    params = {
        "filter": f"{base_filter},from_publication_date:{cutoff},has_abstract:true",
        "sort": "publication_date:desc",
        "per-page": str(max_items),
        "mailto": mailto,
    }

    def _err(msg: str) -> tuple[list[RawItem], SourceStatusEntry]:
        return [], SourceStatusEntry(
            id=sid, name=name, url=OPENALEX_WORKS, language=language,
            primaryCategory=primary_cat, status="error", errorMessage=msg,
            lastFetched=now, itemsLastRun=0,
        )

    try:
        resp = client.get(
            OPENALEX_WORKS, params=params,
            timeout=defaults.get("timeoutMs", 15000) / 1000,
        )
    except Exception as exc:
        return _err(f"{type(exc).__name__}: {exc}")
    if resp.status_code >= 400:
        return _err(f"HTTP {resp.status_code}")
    try:
        results = resp.json().get("results", [])
    except (json.JSONDecodeError, AttributeError, TypeError) as exc:
        return _err(f"bad OpenAlex payload: {type(exc).__name__}")

    items: list[RawItem] = []
    for w in results:
        title = (w.get("display_name") or "").strip().rstrip(".")
        doi = w.get("doi")  # full URL form, e.g. https://doi.org/10.xxxx
        landing = (w.get("primary_location") or {}).get("landing_page_url")
        url = doi or landing or w.get("id")
        if not title or not url:
            continue
        work_type = w.get("type")
        authorships = w.get("authorships") or []
        author = None
        if authorships:
            first = (authorships[0].get("author") or {}).get("display_name")
            author = f"{first} et al." if first and len(authorships) > 1 else first
        mesh = [
            m.get("descriptor_name") for m in (w.get("mesh") or []) if m.get("descriptor_name")
        ]
        first_seen_dt = _track_seen(url, seen, now)
        items.append(RawItem(
            source_id=sid,
            source_name=name,
            language=language,
            title=title,
            url=url,
            published_at=_parse_date(w.get("publication_date")) or first_seen_dt,
            excerpt=_openalex_abstract(w.get("abstract_inverted_index")),
            author=author,
            first_seen_at=first_seen_dt,
            fetched_at=now,
            pub_types=[work_type] if work_type else [],
            mesh=mesh,
        ))

    status = SourceStatusEntry(
        id=sid, name=name, url=OPENALEX_WORKS, language=language,
        primaryCategory=primary_cat, status="ok", lastFetched=now, itemsLastRun=len(items),
    )
    return items, status


def fetch_one(
    source: dict[str, Any],
    defaults: dict[str, Any],
    *,
    etags: dict[str, dict[str, str]],
    seen: dict[str, str],
    client: httpx.Client,
) -> tuple[list[RawItem], SourceStatusEntry]:
    if source.get("type") == "crossref":
        return fetch_crossref(source, defaults, seen=seen, client=client)
    if source.get("type") == "europepmc":
        return fetch_europepmc(source, defaults, seen=seen, client=client)
    if source.get("type") == "openalex":
        return fetch_openalex(source, defaults, seen=seen, client=client)

    sid: str = source["id"]
    url: str = source["url"]
    language: Lang = source["language"]
    name: str = source["name"]
    primary_cat: Category | None = source.get("primaryCategory")
    max_items: int = int(source.get("maxItems", defaults.get("maxItems", 30)))

    headers = {"User-Agent": defaults.get("userAgent", "almanac-bot/1.0")}
    cached = etags.get(sid, {})
    if etag := cached.get("etag"):
        headers["If-None-Match"] = etag
    if last_mod := cached.get("last_modified"):
        headers["If-Modified-Since"] = last_mod

    now = utcnow()

    try:
        if sid.startswith("arxiv-") or sid.startswith("pubmed-"):
            time.sleep(3.5)  # NCBI / arXiv ask for ≤1 req/3s
        resp = client.get(url, headers=headers, timeout=defaults.get("timeoutMs", 15000) / 1000)
    except Exception as exc:
        status = SourceStatusEntry(
            id=sid, name=name, url=url, language=language, primaryCategory=primary_cat,
            status="error", errorMessage=f"{type(exc).__name__}: {exc}",
            lastFetched=now, itemsLastRun=0,
        )
        return [], status

    if resp.status_code == 304:
        status = SourceStatusEntry(
            id=sid, name=name, url=url, language=language, primaryCategory=primary_cat,
            status="ok", lastFetched=now, itemsLastRun=0,
        )
        return [], status

    if resp.status_code >= 400:
        status = SourceStatusEntry(
            id=sid, name=name, url=url, language=language, primaryCategory=primary_cat,
            status="error", errorMessage=f"HTTP {resp.status_code}",
            lastFetched=now, itemsLastRun=0,
        )
        return [], status

    new_cache: dict[str, str] = {}
    if et := resp.headers.get("etag"):
        new_cache["etag"] = et
    if lm := resp.headers.get("last-modified"):
        new_cache["last_modified"] = lm
    if new_cache:
        etags[sid] = new_cache

    parsed = feedparser.parse(resp.content)
    items: list[RawItem] = []
    for entry in parsed.entries[:max_items]:
        link = entry.get("link") or ""
        if not link:
            continue
        first_seen = seen.get(link)
        first_seen_dt = _parse_date(first_seen) if first_seen else now
        if not first_seen:
            seen[link] = now.isoformat()

        published = (
            _parse_date(entry.get("published"))
            or _parse_date(entry.get("updated"))
            or first_seen_dt
        )

        items.append(RawItem(
            source_id=sid,
            source_name=name,
            language=language,
            title=str(entry.get("title", "")).strip(),
            url=link,
            published_at=published,
            excerpt=_excerpt(entry),
            author=str(entry.get("author") or "") or None,
            first_seen_at=first_seen_dt or now,
            fetched_at=now,
        ))

    status = SourceStatusEntry(
        id=sid, name=name, url=url, language=language, primaryCategory=primary_cat,
        status="ok", lastFetched=now, itemsLastRun=len(items),
    )
    return items, status


def fetch_all() -> tuple[list[RawItem], list[SourceStatusEntry]]:
    defaults, sources = load_sources()
    etags = _load_json(ETAG_FILE)
    seen = _load_json(SEEN_FILE)

    all_items: list[RawItem] = []
    statuses: list[SourceStatusEntry] = []

    headers = {"Accept": "application/rss+xml, application/atom+xml, application/xml;q=0.9, */*;q=0.5"}
    with httpx.Client(headers=headers, follow_redirects=True) as client:
        for source in sources:
            try:
                items, status = fetch_one(
                    source, defaults, etags=etags, seen=seen, client=client,
                )
            except Exception as exc:
                status = SourceStatusEntry(
                    id=source["id"], name=source["name"],
                    url=source.get("url") or source.get("query", ""),
                    language=source.get("language", "en"),
                    primaryCategory=source.get("primaryCategory"),
                    status="error", errorMessage=f"unhandled: {type(exc).__name__}: {exc}",
                    lastFetched=utcnow(), itemsLastRun=0,
                )
                items = []
            all_items.extend(items)
            statuses.append(status)

    _save_json(ETAG_FILE, etags)
    _save_json(SEEN_FILE, seen)

    return all_items, statuses

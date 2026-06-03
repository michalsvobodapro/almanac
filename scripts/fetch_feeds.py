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
                    id=source["id"], name=source["name"], url=source["url"],
                    language=source["language"], primaryCategory=source.get("primaryCategory"),
                    status="error", errorMessage=f"unhandled: {type(exc).__name__}: {exc}",
                    lastFetched=utcnow(), itemsLastRun=0,
                )
                items = []
            all_items.extend(items)
            statuses.append(status)

    _save_json(ETAG_FILE, etags)
    _save_json(SEEN_FILE, seen)

    return all_items, statuses

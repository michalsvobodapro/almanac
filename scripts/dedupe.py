"""Deduplicate feed items by canonical URL and title similarity.

When two items collide we keep the higher-trust source (trust_lookup mapping
source_id -> int 1..5).
"""

from __future__ import annotations

from urllib.parse import parse_qsl, urlencode, urlparse, urlunparse

from rapidfuzz import fuzz

from models import RawItem


_DROP_PARAMS = {
    "utm_source", "utm_medium", "utm_campaign", "utm_term", "utm_content",
    "ref", "ref_src", "fbclid", "gclid", "mc_cid", "mc_eid",
}


def canonical_url(url: str) -> str:
    """Strip tracking params + trailing slash, lowercase host."""
    try:
        parts = urlparse(url)
    except ValueError:
        return url
    query = [(k, v) for k, v in parse_qsl(parts.query) if k.lower() not in _DROP_PARAMS]
    path = parts.path.rstrip("/") or "/"
    return urlunparse((
        parts.scheme.lower() or "https",
        parts.netloc.lower(),
        path,
        parts.params,
        urlencode(query),
        "",
    ))


def dedupe(
    items: list[RawItem],
    *,
    trust_lookup: dict[str, int] | None = None,
    title_threshold: int = 85,
) -> list[RawItem]:
    """Return deduped items. Order is preserved relative to first occurrence."""

    trust_lookup = trust_lookup or {}

    by_url: dict[str, RawItem] = {}
    for item in items:
        c = canonical_url(item.url)
        existing = by_url.get(c)
        if existing is None or _trust(item, trust_lookup) > _trust(existing, trust_lookup):
            by_url[c] = item

    out: list[RawItem] = []
    for item in by_url.values():
        replaced = False
        for i, kept in enumerate(out):
            if fuzz.token_set_ratio(kept.title, item.title) >= title_threshold:
                if _trust(item, trust_lookup) > _trust(kept, trust_lookup):
                    out[i] = item
                replaced = True
                break
        if not replaced:
            out.append(item)
    return out


def _trust(item: RawItem, lookup: dict[str, int]) -> int:
    return lookup.get(item.source_id, 3)

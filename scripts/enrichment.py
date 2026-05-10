"""Page enrichment: harvest cover image + extra abstract from article URLs.

Two operations:

1. `enrich_metadata(url, client)` — fetch the page, parse <meta> tags, return
   {og_image_url, og_description, citation_abstract, description}. Used to top
   up RawItems whose RSS excerpts are thin AND to feed Claude richer context.

2. `download_image(url, dest_dir, slug, client)` — fetch the og:image, save to
   public/og-cache/<slug>.<ext> with a size cap. Skips if already cached.

Both are best-effort. Failures return None — never raise.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path
from urllib.parse import urlparse

import httpx
from bs4 import BeautifulSoup


MAX_IMAGE_BYTES = 4 * 1024 * 1024  # 4 MB hard cap per image
MAX_HTML_BYTES = 2 * 1024 * 1024
TIMEOUT_S = 12.0


@dataclass
class Enrichment:
    og_image_url: str | None = None
    og_description: str | None = None
    citation_abstract: str | None = None
    description: str | None = None

    def best_excerpt(self, fallback: str | None = None) -> str | None:
        """Pick the longest available abstract-flavored field."""
        candidates = [self.citation_abstract, self.og_description, self.description, fallback]
        candidates = [c for c in candidates if c]
        if not candidates:
            return None
        return max(candidates, key=len)


def _meta(soup: BeautifulSoup, attrs: dict[str, str]) -> str | None:
    el = soup.find("meta", attrs=attrs)
    if el and el.get("content"):  # type: ignore[union-attr]
        return str(el["content"]).strip() or None  # type: ignore[index]
    return None


def enrich_metadata(url: str, *, client: httpx.Client) -> Enrichment | None:
    """Fetch URL, parse meta tags. Returns None on failure."""
    try:
        resp = client.get(url, timeout=TIMEOUT_S, follow_redirects=True)
    except Exception:
        return None
    if resp.status_code >= 400:
        return None
    if not resp.headers.get("content-type", "").lower().startswith(("text/html", "application/xhtml")):
        return None
    body = resp.content[:MAX_HTML_BYTES]
    try:
        soup = BeautifulSoup(body, "lxml")
    except Exception:
        return None

    enr = Enrichment()
    enr.og_image_url = (
        _meta(soup, {"property": "og:image"})
        or _meta(soup, {"name": "twitter:image"})
        or _meta(soup, {"name": "twitter:image:src"})
    )
    enr.og_description = _meta(soup, {"property": "og:description"})
    enr.description = _meta(soup, {"name": "description"})
    # Academic abstracts: publishers commonly ship `citation_abstract` (Google Scholar metatag).
    enr.citation_abstract = (
        _meta(soup, {"name": "citation_abstract"})
        or _meta(soup, {"name": "DC.Description"})
        or _meta(soup, {"name": "dc.description"})
    )

    # Make og_image_url absolute if it's relative.
    if enr.og_image_url and not enr.og_image_url.startswith(("http://", "https://")):
        from urllib.parse import urljoin
        enr.og_image_url = urljoin(url, enr.og_image_url)

    return enr


_EXT_BY_CONTENT_TYPE = {
    "image/jpeg": ".jpg",
    "image/jpg": ".jpg",
    "image/png": ".png",
    "image/webp": ".webp",
    "image/gif": ".gif",
    "image/avif": ".avif",
}


def download_image(
    image_url: str,
    *,
    dest_dir: Path,
    slug: str,
    client: httpx.Client,
) -> str | None:
    """Download image to dest_dir/<slug>.<ext>. Returns relative path or None."""
    dest_dir.mkdir(parents=True, exist_ok=True)

    # Cached?
    for ext in (".jpg", ".png", ".webp", ".gif", ".avif"):
        cached = dest_dir / f"{slug}{ext}"
        if cached.exists() and cached.stat().st_size > 0:
            return cached.name

    try:
        with client.stream("GET", image_url, timeout=TIMEOUT_S, follow_redirects=True) as resp:
            if resp.status_code >= 400:
                return None
            ct = resp.headers.get("content-type", "").split(";")[0].strip().lower()
            ext = _EXT_BY_CONTENT_TYPE.get(ct)
            if not ext:
                # Fall back to URL extension.
                path = urlparse(image_url).path
                m = re.search(r"\.(jpg|jpeg|png|webp|gif|avif)(?:\?|$)", path, re.I)
                ext = f".{m.group(1).lower()}" if m else None
                if ext == ".jpeg":
                    ext = ".jpg"
            if not ext:
                return None

            buf = bytearray()
            for chunk in resp.iter_bytes(chunk_size=64 * 1024):
                buf.extend(chunk)
                if len(buf) > MAX_IMAGE_BYTES:
                    return None
            if not buf:
                return None
    except Exception:
        return None

    out = dest_dir / f"{slug}{ext}"
    out.write_bytes(bytes(buf))
    return out.name

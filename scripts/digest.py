"""Almanac daily digest pipeline orchestrator.

Usage:
    uv run python scripts/digest.py [--dry-run] [--date YYYY-MM-DD]
"""

from __future__ import annotations

import argparse
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path
from zoneinfo import ZoneInfo

import httpx

from dedupe import dedupe
from enrichment import download_image, enrich_metadata
from fetch_feeds import fetch_all, load_sources
from models import RawItem
from source_status import write_statuses
from write_articles import article_slug, write_digest, write_stub_digest


PRAGUE = ZoneInfo("Europe/Prague")
LOOKBACK_HOURS = 72
MAX_ITEMS_TO_CLAUDE = 150
THIN_EXCERPT_THRESHOLD = 200  # below this many chars, fetch URL to enrich
ENRICHMENT_USER_AGENT = "almanac-bot/1.0 (+https://github.com/michalsvobodapro/almanac)"

REPO_ROOT = Path(__file__).resolve().parent.parent
COVER_DIR = REPO_ROOT / "public" / "og-cache"
ARTICLES_DIR = REPO_ROOT / "src" / "content" / "articles"


def today_str(now: datetime | None = None) -> str:
    now = now or datetime.now(PRAGUE)
    return now.astimezone(PRAGUE).strftime("%Y-%m-%d")


def filter_recent(items: list[RawItem], hours: int = LOOKBACK_HOURS) -> list[RawItem]:
    cutoff = datetime.now(timezone.utc) - timedelta(hours=hours)
    out: list[RawItem] = []
    for it in items:
        ref = it.published_at or it.first_seen_at
        if ref >= cutoff:
            out.append(it)
    return out


def previously_published_urls() -> set[str]:
    """Scan committed article markdown for `sourceUrl` fields so the wider
    lookback window doesn't re-pick stories from earlier digests."""
    urls: set[str] = set()
    if not ARTICLES_DIR.exists():
        return urls
    for path in ARTICLES_DIR.glob("*.md"):
        try:
            text = path.read_text(encoding="utf-8")
        except OSError:
            continue
        if not text.startswith("---"):
            continue
        end = text.find("\n---", 3)
        if end == -1:
            continue
        for line in text[3:end].splitlines():
            stripped = line.strip()
            if stripped.startswith("sourceUrl:"):
                value = stripped.split(":", 1)[1].strip()
                if value.startswith(("'", '"')) and value.endswith(value[0]):
                    value = value[1:-1]
                if value:
                    urls.add(value)
                break
    return urls


def trust_lookup() -> dict[str, int]:
    _, sources = load_sources()
    return {s["id"]: int(s.get("trust", 3)) for s in sources}


def enrich_thin_items(items: list[RawItem]) -> int:
    """Mutate items in place: for those with thin excerpts, fetch URL → fill
    `excerpt_full` and `cover_image_url` from <meta> tags. Returns count enriched."""
    targets = [i for i in items if not i.excerpt or len(i.excerpt) < THIN_EXCERPT_THRESHOLD]
    if not targets:
        return 0
    enriched = 0
    headers = {"User-Agent": ENRICHMENT_USER_AGENT, "Accept": "text/html,application/xhtml+xml"}
    with httpx.Client(headers=headers, follow_redirects=True) as client:
        for item in targets:
            enr = enrich_metadata(item.url, client=client)
            if enr is None:
                continue
            best = enr.best_excerpt(fallback=item.excerpt)
            if best and (not item.excerpt or len(best) > len(item.excerpt)):
                item.excerpt_full = best
                enriched += 1
            if enr.og_image_url:
                item.cover_image_url = enr.og_image_url
    return enriched


def download_covers(picked: list[tuple[str, RawItem, str]]) -> dict[str, str]:
    """Download og:image for each picked article. Returns {claude_id: filename}."""
    out: dict[str, str] = {}
    headers = {"User-Agent": ENRICHMENT_USER_AGENT}
    with httpx.Client(headers=headers, follow_redirects=True) as client:
        for claude_id, raw, slug in picked:
            url = raw.cover_image_url
            if not url:
                # We never enriched this URL (excerpt was rich enough). Try once now.
                enr = enrich_metadata(raw.url, client=client)
                if enr and enr.og_image_url:
                    url = enr.og_image_url
                    raw.cover_image_url = url
            if not url:
                continue
            filename = download_image(url, dest_dir=COVER_DIR, slug=slug, client=client)
            if filename:
                out[claude_id] = filename
    return out


def main() -> int:
    ap = argparse.ArgumentParser(description="Almanac daily digest pipeline")
    ap.add_argument("--dry-run", action="store_true", help="Fetch + dedupe; skip Claude call and writes")
    ap.add_argument("--date", help="Override the digest date (YYYY-MM-DD)")
    args = ap.parse_args()

    date = args.date or today_str()

    print(f"▶ Almanac digest for {date}")
    print(f"  Lookback window: {LOOKBACK_HOURS}h")

    print("\n[1/5] Fetching sources …")
    items, statuses = fetch_all()
    ok = sum(1 for s in statuses if s.status == "ok")
    err = sum(1 for s in statuses if s.status == "error")
    print(f"  {len(items)} items from {ok} sources OK, {err} sources errored")
    for s in statuses:
        marker = "✓" if s.status == "ok" else "✗"
        suffix = f" — {s.errorMessage}" if s.status == "error" else f" ({s.itemsLastRun} items)"
        print(f"    {marker} {s.id}{suffix}")

    print(f"\n[2/5] Deduping & filtering to last {LOOKBACK_HOURS}h …")
    deduped = dedupe(items, trust_lookup=trust_lookup())
    recent = filter_recent(deduped)
    print(f"  {len(items)} fetched → {len(deduped)} after dedupe → {len(recent)} in last {LOOKBACK_HOURS}h")

    already_published = previously_published_urls()
    if already_published:
        before = len(recent)
        recent = [i for i in recent if i.url not in already_published]
        dropped = before - len(recent)
        if dropped:
            print(f"  dropped {dropped} already-published items (matched committed sourceUrl)")

    if len(recent) > MAX_ITEMS_TO_CLAUDE:
        recent = sorted(
            recent, key=lambda i: i.published_at or i.first_seen_at, reverse=True
        )[:MAX_ITEMS_TO_CLAUDE]
        print(f"  capped to top {MAX_ITEMS_TO_CLAUDE} most recent")

    write_statuses(statuses)
    print("  wrote data/source-status.json")

    print("\n[3/5] Enriching items with thin RSS excerpts …")
    enriched_count = enrich_thin_items(recent)
    print(f"  enriched {enriched_count} of {len(recent)} items via URL meta tags")

    if args.dry_run:
        print("\n[4/5] (dry-run) Skipping Claude call.")
        print("\nWould send to Claude:")
        for i, it in enumerate(recent, 1):
            ex_len = len(it.excerpt_full or it.excerpt or "")
            cover = "🖼" if it.cover_image_url else "  "
            print(f"  {i:3}. {cover} [{it.language}] {it.source_id}: {it.title[:70]} (excerpt: {ex_len}c)")
        print("\n[5/5] (dry-run) Skipping write.")
        return 0

    if not recent:
        print("\n[4/5] No fresh items — writing stub digest.")
        write_stub_digest(date, "No fresh items in the last 24h.")
        return 0

    print(f"\n[4/5] Calling Claude on {len(recent)} items …")
    items_by_id = {f"{i.source_id}::{i.url}": i for i in recent}

    from claude_rank import rank

    try:
        result = rank(date, recent)
    except Exception as exc:
        print(f"  ✗ Claude call failed after retry: {exc}", file=sys.stderr)
        write_stub_digest(date, str(exc))
        return 1

    print(f"  ✓ Got digest. Cost: ${result.cost_usd:.4f}")
    print(f"    in: {result.input_tokens}t, out: {result.output_tokens}t, cached: {result.cached_tokens}t")
    print(f"    hero: {result.digest.hero_id}")

    print(f"\n[5/5] Downloading cover images for {len(result.digest.items)} picks …")
    picked: list[tuple[str, RawItem, str]] = []
    for ranked in result.digest.items:
        raw = items_by_id.get(ranked.id)
        if raw is None:
            continue
        slug = article_slug(date, ranked.category, ranked.title)
        picked.append((ranked.id, raw, slug))
    covers = download_covers(picked)
    print(f"  saved {len(covers)} cover images to public/og-cache/")

    print("\n   Writing articles + digest …")
    digest_path, article_paths = write_digest(
        today=date,
        items_by_id=items_by_id,
        result=result,
        items_fetched=len(items),
        items_considered=len(recent),
        sources_ok=ok,
        sources_error=err,
        covers_by_id=covers,
    )
    print(f"  wrote {digest_path.relative_to(digest_path.parents[3])}")
    for p in article_paths:
        print(f"  wrote {p.relative_to(p.parents[3])}")

    print("\n✓ Done.")
    return 0


if __name__ == "__main__":
    sys.exit(main())

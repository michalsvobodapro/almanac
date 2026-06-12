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
from models import RawItem, TriagedItem
from source_status import write_statuses
from write_articles import article_slug, write_digest, write_stub_digest


PRAGUE = ZoneInfo("Europe/Prague")
LOOKBACK_HOURS = 72
# If the normal window yields no *new* items, widen once so a day is never blank.
# The widen test runs AFTER the already-published filter, so a window that's
# non-empty but fully already-covered still triggers the fallback (slow journal
# feeds go quiet for days at a time).
FALLBACK_LOOKBACK_HOURS = 14 * 24
MAX_ITEMS_TO_CLAUDE = 150
# How many triage-kept items to forward to the Sonnet editorial pass. Also the
# cap used when triage fails and we fall back to recency ordering.
SHORTLIST_SIZE = 28
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
    already_published = previously_published_urls()

    def fresh_unpublished(hours: int) -> tuple[list[RawItem], int]:
        """Items in the window that haven't appeared in a previous digest.
        Returns (kept, in_window_count)."""
        in_window = filter_recent(deduped, hours=hours)
        kept = [i for i in in_window if i.url not in already_published]
        return kept, len(in_window)

    window = LOOKBACK_HOURS
    recent, in_window = fresh_unpublished(window)
    print(
        f"  {len(items)} fetched → {len(deduped)} after dedupe → {in_window} in last "
        f"{window}h → {len(recent)} new (dropped {in_window - len(recent)} already-published)"
    )

    # Widen once if nothing NEW survived. A window that's non-empty but fully
    # already-covered must still widen, so the test is on post-filter `recent`.
    if not recent:
        window = FALLBACK_LOOKBACK_HOURS
        recent, in_window = fresh_unpublished(window)
        print(
            f"  no new items in {LOOKBACK_HOURS}h — widened to {window}h → "
            f"{len(recent)} new (of {in_window} in window)"
        )

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
        print("\n[4/6] (dry-run) Skipping triage + Claude calls.")
        print("\nWould send to triage:")
        for i, it in enumerate(recent, 1):
            ex_len = len(it.excerpt_full or it.excerpt or "")
            cover = "🖼" if it.cover_image_url else "  "
            pt = f" [{','.join(it.pub_types[:2])}]" if it.pub_types else ""
            print(f"  {i:3}. {cover} [{it.language}] {it.source_id}: {it.title[:64]}{pt} ({ex_len}c)")
        print("\n[5/6] (dry-run) Skipping editorial + write.")
        return 0

    if not recent:
        print("\n[4/6] No fresh items — writing stub digest.")
        write_stub_digest(date, f"No fresh items in the last {window}h.")
        return 0

    items_by_id = {f"{i.source_id}::{i.url}": i for i in recent}

    # ── Stage B: triage + classify + evidence-grade (cheap Haiku over all). ──
    # Degrades independently: a triage failure must never block the digest — we
    # fall back to recency ordering with no grades.
    print(f"\n[4/6] Triaging + grading {len(recent)} items (Haiku) …")
    triaged_by_id: dict[str, TriagedItem] = {}
    triage_cost = 0.0
    shortlist = recent
    try:
        from triage import triage

        tr = triage(recent)
        triaged_by_id = tr.triaged
        triage_cost = tr.cost_usd
        kept = [items_by_id[i] for i in tr.kept_ids if i in items_by_id]
        shortlist = kept[:SHORTLIST_SIZE] if kept else recent
        print(
            f"  ✓ kept {len(tr.kept_ids)}/{len(recent)} → shortlist {len(shortlist)}. "
            f"Cost ${tr.cost_usd:.4f} (in {tr.input_tokens}t, out {tr.output_tokens}t, "
            f"cached {tr.cached_tokens}t)"
        )
    except Exception as exc:
        shortlist = sorted(
            recent, key=lambda i: i.published_at or i.first_seen_at, reverse=True
        )[:SHORTLIST_SIZE]
        print(f"  ✗ triage failed ({exc}); proceeding un-graded with {len(shortlist)} items", file=sys.stderr)

    # ── Stage D: editorial pass (Sonnet over the graded shortlist only). ──
    print(f"\n[5/6] Calling Claude editorial on {len(shortlist)} shortlisted items …")
    from claude_rank import rank

    try:
        result = rank(date, shortlist, triaged_by_id)
    except Exception as exc:
        print(f"  ✗ Claude call failed after retry: {exc}", file=sys.stderr)
        write_stub_digest(date, str(exc))
        return 1

    print(f"  ✓ Got digest. Editorial cost: ${result.cost_usd:.4f} (triage ${triage_cost:.4f}, total ${result.cost_usd + triage_cost:.4f})")
    print(f"    in: {result.input_tokens}t, out: {result.output_tokens}t, cached: {result.cached_tokens}t")
    print(f"    hero: {result.digest.hero_id}")

    print(f"\n[6/6] Downloading cover images for {len(result.digest.items)} picks …")
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
        triaged_by_id=triaged_by_id,
    )
    print(f"  wrote {digest_path.relative_to(digest_path.parents[3])}")
    for p in article_paths:
        print(f"  wrote {p.relative_to(p.parents[3])}")

    print("\n✓ Done.")
    return 0


if __name__ == "__main__":
    sys.exit(main())

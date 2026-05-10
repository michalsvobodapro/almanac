"""Almanac daily digest pipeline orchestrator.

Usage:
    uv run python scripts/digest.py [--dry-run] [--date YYYY-MM-DD]
"""

from __future__ import annotations

import argparse
import sys
from datetime import datetime, timedelta, timezone
from zoneinfo import ZoneInfo

from dedupe import dedupe
from fetch_feeds import fetch_all, load_sources
from models import RawItem
from source_status import write_statuses
from write_articles import write_digest, write_stub_digest


PRAGUE = ZoneInfo("Europe/Prague")
LOOKBACK_HOURS = 24
MAX_ITEMS_TO_CLAUDE = 150


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


def trust_lookup() -> dict[str, int]:
    _, sources = load_sources()
    return {s["id"]: int(s.get("trust", 3)) for s in sources}


def main() -> int:
    ap = argparse.ArgumentParser(description="Almanac daily digest pipeline")
    ap.add_argument("--dry-run", action="store_true", help="Fetch + dedupe; skip Claude call and writes")
    ap.add_argument("--date", help="Override the digest date (YYYY-MM-DD)")
    args = ap.parse_args()

    date = args.date or today_str()

    print(f"▶ Almanac digest for {date}")
    print(f"  Lookback window: {LOOKBACK_HOURS}h")

    print("\n[1/4] Fetching sources …")
    items, statuses = fetch_all()
    ok = sum(1 for s in statuses if s.status == "ok")
    err = sum(1 for s in statuses if s.status == "error")
    print(f"  {len(items)} items from {ok} sources OK, {err} sources errored")
    for s in statuses:
        marker = "✓" if s.status == "ok" else "✗"
        suffix = f" — {s.errorMessage}" if s.status == "error" else f" ({s.itemsLastRun} items)"
        print(f"    {marker} {s.id}{suffix}")

    print("\n[2/4] Deduping & filtering to last 24h …")
    deduped = dedupe(items, trust_lookup=trust_lookup())
    recent = filter_recent(deduped)
    print(f"  {len(items)} fetched → {len(deduped)} after dedupe → {len(recent)} in last 24h")

    if len(recent) > MAX_ITEMS_TO_CLAUDE:
        recent = sorted(
            recent, key=lambda i: i.published_at or i.first_seen_at, reverse=True
        )[:MAX_ITEMS_TO_CLAUDE]
        print(f"  capped to top {MAX_ITEMS_TO_CLAUDE} most recent")

    # Always write source-status so /sources reflects the latest run.
    write_statuses(statuses)
    print("  wrote data/source-status.json")

    if args.dry_run:
        print("\n[3/4] (dry-run) Skipping Claude call.")
        print("\nWould send to Claude:")
        for i, it in enumerate(recent, 1):
            print(f"  {i:3}. [{it.section}/{it.language}] {it.source_id}: {it.title[:80]}")
        print("\n[4/4] (dry-run) Skipping write.")
        return 0

    if not recent:
        print("\n[3/4] No fresh items — writing stub digest.")
        write_stub_digest(date, "No fresh items in the last 24h.")
        return 0

    print(f"\n[3/4] Calling Claude on {len(recent)} items …")
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

    print("\n[4/4] Writing articles + digest …")
    digest_path, article_paths = write_digest(
        today=date,
        items_by_id=items_by_id,
        result=result,
        items_fetched=len(items),
        items_considered=len(recent),
        sources_ok=ok,
        sources_error=err,
    )
    print(f"  wrote {digest_path.relative_to(digest_path.parents[3])}")
    for p in article_paths:
        print(f"  wrote {p.relative_to(p.parents[3])}")

    print("\n✓ Done.")
    return 0


if __name__ == "__main__":
    sys.exit(main())

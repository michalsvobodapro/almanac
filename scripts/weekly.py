"""Sunday weekly synthesis — one Sonnet call over the week's stories + threads.

Reads the last 7 days of published articles, identifies the research threads
that advanced, and writes an editorial "what mattered and why" essay to
`src/content/weekly/<isoweek>.md`. Optionally renders an English audio edition
(see tts.py) when a TTS engine is available.

Usage:
    uv run python scripts/weekly.py [--date YYYY-MM-DD] [--dry-run] [--no-audio]
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
from datetime import date, datetime, timedelta, timezone
from pathlib import Path
from typing import Any

import frontmatter
from anthropic import Anthropic

from models import WeeklyFrontmatter, WeeklySection, WeeklyStats


REPO_ROOT = Path(__file__).resolve().parent.parent
ARTICLES_DIR = REPO_ROOT / "src" / "content" / "articles"
WEEKLY_DIR = REPO_ROOT / "src" / "content" / "weekly"

MODEL = "claude-sonnet-4-6"
MAX_TOKENS = 4096
PRICE_INPUT_PER_M = 3.00
PRICE_OUTPUT_PER_M = 15.00
PRICE_CACHE_READ_PER_M = 0.30
MIN_ARTICLES = 3  # below this, not worth a synthesis


SYSTEM_PROMPT = """\
You are the editor of Almanac writing the Sunday weekly synthesis for one
reader: a dentistry student in Prague. You receive this week's published
stories (each already curated, summarized, evidence-graded, and tagged with a
`topicThread`) plus the threads that gained more than one story this week.

Write a "what mattered and why" essay — the Stratechery weekly, for dentistry.
Your job is synthesis, not recap: surface the 2–4 themes that actually advanced,
say what shifted and why it matters at the chair, and name the threads that are
worth watching. Be declarative and opinionated; never write "this week we saw."
Lead with the development, then the so-what. English only.

Return ONLY by calling `submit_weekly` with:
- `title`: a sharp headline for the week (≤10 words).
- `dek`: one-sentence standfirst under the title.
- `intro`: 2–4 sentences framing the week's through-line.
- `sections`: 2–4 objects {heading, body}. Each heading names a theme; each
  body is ~90–150 words of synthesis drawing on the relevant stories. Weave the
  evidence quality in (an RCT shifting practice is not a lab preprint).
- `threads`: the thread labels (verbatim from the input) that advanced this week.
"""

SUBMIT_TOOL = {
    "name": "submit_weekly",
    "description": "Submit the weekly dentistry synthesis.",
    "input_schema": {
        "type": "object",
        "properties": {
            "title": {"type": "string"},
            "dek": {"type": "string"},
            "intro": {"type": "string"},
            "sections": {
                "type": "array",
                "minItems": 1,
                "maxItems": 5,
                "items": {
                    "type": "object",
                    "properties": {
                        "heading": {"type": "string"},
                        "body": {"type": "string"},
                    },
                    "required": ["heading", "body"],
                },
            },
            "threads": {"type": "array", "items": {"type": "string"}},
        },
        "required": ["title", "dek", "intro", "sections"],
    },
}


def _norm_thread(s: str) -> str:
    return re.sub(r"^-+|-+$", "", re.sub(r"[^a-z0-9]+", "-", s.lower().strip()))


def load_week(end: date) -> tuple[list[dict[str, Any]], dict[str, list[str]]]:
    """Return (articles, threads) for the 7-day window ending `end`.
    `threads` maps a thread label → slugs (only threads with ≥2 stories)."""
    start = end - timedelta(days=6)
    items: list[dict[str, Any]] = []
    if not ARTICLES_DIR.exists():
        return items, {}
    for path in sorted(ARTICLES_DIR.glob("*.md")):
        try:
            post = frontmatter.load(path)
        except Exception:
            continue
        dd = post.get("digestDate")
        if not isinstance(dd, str):
            continue
        try:
            ddate = date.fromisoformat(dd)
        except ValueError:
            continue
        if not (start <= ddate <= end):
            continue
        items.append({
            "slug": path.stem,
            "title": post.get("title", ""),
            "category": post.get("category", "other"),
            "evidenceType": post.get("evidenceType"),
            "evidenceGrade": post.get("evidenceGrade", "na"),
            "clinicalTakeaway": post.get("clinicalTakeaway") or post.get("summary", ""),
            "summary": post.get("summary", ""),
            "topicThread": post.get("topicThread"),
            "digestDate": dd,
        })

    buckets: dict[str, list[str]] = {}
    labels: dict[str, str] = {}
    for it in items:
        t = it.get("topicThread")
        if not isinstance(t, str) or not t.strip():
            continue
        key = _norm_thread(t)
        if not key:
            continue
        buckets.setdefault(key, []).append(it["slug"])
        labels.setdefault(key, t.strip())
    threads = {labels[k]: v for k, v in buckets.items() if len(v) >= 2}
    return items, threads


def _payload(items: list[dict[str, Any]], threads: dict[str, list[str]]) -> str:
    return json.dumps({
        "stories": [
            {
                "slug": i["slug"],
                "title": i["title"],
                "category": i["category"],
                "evidenceType": i["evidenceType"],
                "evidenceGrade": i["evidenceGrade"],
                "takeaway": i["clinicalTakeaway"],
                "topicThread": i["topicThread"],
                "date": i["digestDate"],
            }
            for i in items
        ],
        "threadsThatAdvanced": [
            {"thread": label, "storyCount": len(slugs)} for label, slugs in threads.items()
        ],
    }, ensure_ascii=False)


def _cost(input_t: int, output_t: int, cached_t: int) -> float:
    fresh = max(0, input_t - cached_t)
    return (
        fresh * PRICE_INPUT_PER_M / 1_000_000
        + cached_t * PRICE_CACHE_READ_PER_M / 1_000_000
        + output_t * PRICE_OUTPUT_PER_M / 1_000_000
    )


def synthesize(items: list[dict[str, Any]], threads: dict[str, list[str]]) -> dict[str, Any]:
    if not os.environ.get("ANTHROPIC_API_KEY"):
        raise RuntimeError("ANTHROPIC_API_KEY is not set")
    client = Anthropic()
    resp = client.messages.create(
        model=MODEL,
        max_tokens=MAX_TOKENS,
        temperature=0.5,
        tools=[SUBMIT_TOOL],
        tool_choice={"type": "tool", "name": "submit_weekly"},
        system=[{"type": "text", "text": SYSTEM_PROMPT, "cache_control": {"type": "ephemeral", "ttl": "1h"}}],
        messages=[{"role": "user", "content": _payload(items, threads)}],
    )
    payload: dict[str, Any] | None = None
    for block in resp.content:
        if getattr(block, "type", None) == "tool_use":
            payload = block.input  # type: ignore[assignment]
            break
    if payload is None:
        raise ValueError("No tool_use block in weekly response")
    usage = resp.usage
    payload["_usage"] = {
        "input": getattr(usage, "input_tokens", 0),
        "output": getattr(usage, "output_tokens", 0),
        "cached": getattr(usage, "cache_read_input_tokens", 0) or 0,
    }
    return payload


def write_weekly(
    end: date,
    items: list[dict[str, Any]],
    threads: dict[str, list[str]],
    result: dict[str, Any],
    audio: str | None = None,
) -> Path:
    iso = end.isocalendar()
    week_id = f"{iso[0]}-W{iso[1]:02d}"
    start = end - timedelta(days=6)
    u = result.get("_usage", {"input": 0, "output": 0, "cached": 0})
    fm = WeeklyFrontmatter(
        week=week_id,
        date=end.isoformat(),
        rangeStart=start.isoformat(),
        rangeEnd=end.isoformat(),
        builtAt=datetime.now(timezone.utc),
        title=result["title"],
        dek=result["dek"],
        intro=result["intro"],
        sections=[WeeklySection(heading=s["heading"], body=s["body"]) for s in result["sections"]],
        threads=result.get("threads", []) or list(threads.keys()),
        articleSlugs=[i["slug"] for i in items],
        audio=audio,
        stats=WeeklyStats(
            articles=len(items),
            costUsd=round(_cost(u["input"], u["output"], u["cached"]), 4),
            inputTokens=u["input"],
            outputTokens=u["output"],
        ),
    )
    WEEKLY_DIR.mkdir(parents=True, exist_ok=True)
    post = frontmatter.Post("", **fm.model_dump(mode="json", exclude_none=True))
    path = WEEKLY_DIR / f"{week_id}.md"
    path.write_text(frontmatter.dumps(post) + "\n")
    return path


def main() -> int:
    ap = argparse.ArgumentParser(description="Almanac weekly synthesis")
    ap.add_argument("--date", help="End date of the week (YYYY-MM-DD); default today")
    ap.add_argument("--dry-run", action="store_true", help="Gather + print; skip Claude + write")
    ap.add_argument("--no-audio", action="store_true", help="Skip the TTS audio edition")
    args = ap.parse_args()

    end = date.fromisoformat(args.date) if args.date else datetime.now(timezone.utc).date()
    items, threads = load_week(end)
    print(f"▶ Weekly synthesis for week ending {end} — {len(items)} stories, {len(threads)} active threads")

    if len(items) < MIN_ARTICLES:
        print(f"  only {len(items)} stories (< {MIN_ARTICLES}) — skipping weekly.")
        return 0

    if args.dry_run:
        for i in items:
            print(f"  · [{i['category']}] {i['title'][:70]}")
        print(f"  threads: {', '.join(threads) or '(none)'}")
        return 0

    print("  Calling Claude …")
    try:
        result = synthesize(items, threads)
    except Exception as exc:
        print(f"  ✗ weekly synthesis failed: {exc}", file=sys.stderr)
        return 1
    u = result.get("_usage", {})
    print(f"  ✓ {result['title']!r} — cost ${_cost(u.get('input',0), u.get('output',0), u.get('cached',0)):.4f}")

    audio_rel: str | None = None
    if not args.no_audio:
        try:
            from tts import synthesize_weekly_audio

            audio_rel = synthesize_weekly_audio(end, result)
            if audio_rel:
                print(f"  ✓ audio edition: {audio_rel}")
        except Exception as exc:
            print(f"  · audio skipped ({type(exc).__name__}: {exc})", file=sys.stderr)

    path = write_weekly(end, items, threads, result, audio=audio_rel)
    print(f"  wrote {path.relative_to(REPO_ROOT)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())

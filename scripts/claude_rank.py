"""Single Claude call: rank + summarize candidates into a daily digest.

Tool-forced JSON output via a `submit_digest` tool. One retry on Pydantic
validation failure, lower temperature on retry. If both fail, raise — the
orchestrator decides whether to write a stub digest.
"""

from __future__ import annotations

import json
import os
from dataclasses import dataclass
from typing import Any

from anthropic import Anthropic

from models import CATEGORIES, DigestResponse, RawItem, TriagedItem


MODEL = "claude-sonnet-4-6"
# 12 picks × (≤80w summary + ≤200w summaryDeep) + intro can easily approach
# 5k tokens; 4096 truncated the tool-use mid-write and surfaced as
# `KeyError: 'items'` downstream.
MAX_TOKENS = 8192

# Pricing per 1M tokens (Sonnet 4.6 baseline).
PRICE_INPUT_PER_M = 3.00
PRICE_OUTPUT_PER_M = 15.00
PRICE_CACHE_READ_PER_M = 0.30


SYSTEM_PROMPT = """\
You are the editor of Almanac, a daily editorial brief on dentistry for one
reader. Your voice is The Verge crossed with Stratechery: declarative,
opinionated, unpadded. Never write "in this article" or "the author argues."
Write as if introducing the story yourself.

You will receive a JSON array of candidate items, each with `id`, `title`,
`excerpt`, `sourceName`, `language` ("en" or "cs"), `publishedAt`, and `url`.
Items are from the last 72 hours; the orchestrator has already removed
anything already published in an earlier digest, so freshness to the reader
is guaranteed.

Pick up to 12 of the best stories, but no fewer than what is genuinely
strong — don't pad with weak items to hit a number. Aim for breadth across
the dental specialties; do not let one specialty dominate unless the day
genuinely warrants it.

Each candidate arrives pre-graded by a triage pass: it carries a `category`,
an `evidenceType`/`evidenceGrade` (study design + GRADE-flavoured confidence),
and a `topicThread`. Trust those grades — weight high-evidence items up, and
when several items share a `topicThread` you may note the thread in your prose
("the third short-implant cohort this month"). Keep each pick's `category`
unless it is clearly wrong.

For each pick you write TWO summaries plus a takeaway:
- `summary`: 2–3 sentences, ~50–80 words. The card-and-feed version. Sharp,
  declarative.
- `summaryDeep`: 4–7 sentences, ~150–200 words. The article-page version.
  Synthesizes the abstract and excerpt: what was studied, what was found,
  what it changes for clinical practice. Still your editorial voice — not a
  press release.
- `clinicalTakeaway`: ONE sentence, ≤25 words, in the item's source language.
  The chairside so-what: what this changes Monday morning, or why it doesn't
  yet. Concrete and honest — say "too preliminary to change practice" when true.

Set `guidelineFlag` true only when the story bears on a clinical practice
guideline (EFP/ESE/ČSK/ADA/FDI or similar) — new, revised, or directly
challenged by the evidence.

For each pick, classify it into ONE category:
  - conservative   (caries, restorative materials, operative, esthetic)
  - endodontics    (pulp, root canal, instrumentation, retreatment)
  - periodontology (gums, perio classification, regeneration, peri-implantitis)
  - implantology   (implants, surgical placement, prosthetic complications)
  - orthodontics   (aligners, fixed appliances, biomechanics, retention)
  - other          (oral surgery, prosthodontics, pediatric, oral medicine,
                    regulation, education, business — anything not above)

Rank 1..10 across the whole list (1 = top). Write each summary in the same
language as the source item (English for `en`, Czech for `cs`). Summaries are
2–3 sentences, ~50–80 words. No marketing fluff, no "researchers say" hedges.
Lead with the development, then the so-what.

You may rewrite titles to be sharper while preserving meaning and language.
Tag each story with 2–4 freeform lowercase-hyphenated tags. For each item,
list 0–3 `relatedIds` from your other selections.

Also write a one-paragraph editorial `intro` (English, ~3 sentences) framing
the day's themes and naming a `heroId` — the single most important story.

Return ONLY by calling the `submit_digest` tool.
"""

USER_PROFILE = """\
Reader profile: dentistry student in Prague. Prioritize:
- changes that affect chairside practice (materials, protocols, indications)
- ČSK and EU regulatory news
- new evidence (RCTs, meta-analyses, long-term cohorts) over single case reports
- AI-in-dentistry research that translates to clinic
- Czech-specific news and education

De-prioritize: marketing, influencer videos, US insurance billing, press
releases that aren't backed by published evidence.
"""


SUBMIT_TOOL = {
    "name": "submit_digest",
    "description": "Submit the curated daily dentistry digest.",
    "input_schema": {
        "type": "object",
        "properties": {
            "intro": {"type": "string"},
            "heroId": {"type": "string"},
            "items": {
                "type": "array",
                "minItems": 1,
                "maxItems": 12,
                "items": {
                    "type": "object",
                    "properties": {
                        "id": {"type": "string"},
                        "rank": {"type": "integer", "minimum": 1, "maximum": 20},
                        "category": {"type": "string", "enum": list(CATEGORIES)},
                        "title": {"type": "string"},
                        "summary": {"type": "string"},
                        "summaryDeep": {"type": "string"},
                        "clinicalTakeaway": {"type": "string"},
                        "guidelineFlag": {"type": "boolean"},
                        "tags": {"type": "array", "items": {"type": "string"}, "maxItems": 4},
                        "relatedIds": {"type": "array", "items": {"type": "string"}, "maxItems": 3},
                    },
                    "required": ["id", "rank", "category", "title", "summary", "summaryDeep"],
                },
            },
        },
        "required": ["intro", "heroId", "items"],
    },
}


@dataclass
class RankResult:
    digest: DigestResponse
    input_tokens: int
    output_tokens: int
    cached_tokens: int
    cost_usd: float
    raw_response: dict[str, Any]


def _estimate_input_chars(items: list[RawItem]) -> int:
    return sum(len(i.title) + len(i.excerpt or "") + 80 for i in items) + 4000


def _items_payload(
    today: str,
    items: list[RawItem],
    triaged_by_id: dict[str, TriagedItem] | None = None,
) -> str:
    triaged_by_id = triaged_by_id or {}

    def _row(i: RawItem) -> dict[str, Any]:
        iid = f"{i.source_id}::{i.url}"
        row: dict[str, Any] = {
            "id": iid,
            "title": i.title,
            # Prefer the longer enriched excerpt when available so Claude
            # can write a real `summaryDeep`, not a stretched headline.
            "excerpt": (i.excerpt_full or i.excerpt or "")[:1500],
            "sourceName": i.source_name,
            "language": i.language,
            "publishedAt": (i.published_at.isoformat() if i.published_at else ""),
            "url": i.url,
        }
        t = triaged_by_id.get(iid)
        if t is not None:
            row["category"] = t.category
            row["evidenceType"] = t.evidence_type
            row["evidenceGrade"] = t.evidence_grade
            if t.evidence_note:
                row["evidenceNote"] = t.evidence_note
            if t.topic_thread:
                row["topicThread"] = t.topic_thread
        return row

    return json.dumps(
        {"today": today, "items": [_row(i) for i in items]}, ensure_ascii=False
    )


def _compute_cost(input_t: int, output_t: int, cached_t: int) -> float:
    fresh_input = max(0, input_t - cached_t)
    return (
        fresh_input * PRICE_INPUT_PER_M / 1_000_000
        + cached_t * PRICE_CACHE_READ_PER_M / 1_000_000
        + output_t * PRICE_OUTPUT_PER_M / 1_000_000
    )


def rank(
    today: str,
    items: list[RawItem],
    triaged_by_id: dict[str, TriagedItem] | None = None,
) -> RankResult:
    if not os.environ.get("ANTHROPIC_API_KEY"):
        raise RuntimeError("ANTHROPIC_API_KEY is not set")

    est_chars = _estimate_input_chars(items)
    if est_chars > 240_000:
        raise RuntimeError(
            f"Estimated input ~{est_chars // 4} tokens > 60k cap. Refusing call."
        )

    client = Anthropic()
    user_payload = _items_payload(today, items, triaged_by_id)

    def _call(temperature: float) -> Any:
        return client.messages.create(
            model=MODEL,
            max_tokens=MAX_TOKENS,
            temperature=temperature,
            tools=[SUBMIT_TOOL],
            tool_choice={"type": "tool", "name": "submit_digest"},
            system=[
                {
                    "type": "text",
                    "text": SYSTEM_PROMPT,
                    "cache_control": {"type": "ephemeral", "ttl": "1h"},
                },
                {
                    "type": "text",
                    "text": USER_PROFILE,
                    "cache_control": {"type": "ephemeral", "ttl": "1h"},
                },
            ],
            messages=[{"role": "user", "content": user_payload}],
        )

    def _extract(resp: Any) -> dict[str, Any]:
        for block in resp.content:
            if getattr(block, "type", None) == "tool_use":
                return block.input  # type: ignore[no-any-return]
        raise ValueError("No tool_use block in Claude response")

    last_exc: Exception | None = None
    for attempt, temp in enumerate([0.4, 0.1]):
        try:
            resp = _call(temp)
            payload = _extract(resp)
            digest = DigestResponse.model_validate({
                "intro": payload["intro"],
                "hero_id": payload["heroId"],
                "items": [_normalize_item(x) for x in payload["items"]],
            })
            usage = resp.usage
            input_t = getattr(usage, "input_tokens", 0)
            output_t = getattr(usage, "output_tokens", 0)
            cached_t = getattr(usage, "cache_read_input_tokens", 0) or 0
            return RankResult(
                digest=digest,
                input_tokens=input_t,
                output_tokens=output_t,
                cached_tokens=cached_t,
                cost_usd=_compute_cost(input_t, output_t, cached_t),
                raw_response=payload,
            )
        except Exception as exc:
            last_exc = exc
            if attempt == 1:
                raise
    assert last_exc is not None
    raise last_exc


def _normalize_item(item: dict[str, Any]) -> dict[str, Any]:
    return {
        "id": item["id"],
        "rank": item["rank"],
        "category": item["category"],
        "title": item["title"],
        "summary": item["summary"],
        "summary_deep": item.get("summaryDeep"),
        "clinical_takeaway": item.get("clinicalTakeaway"),
        "guideline_flag": bool(item.get("guidelineFlag", False)),
        "tags": item.get("tags", []),
        "related_ids": item.get("relatedIds", []),
    }

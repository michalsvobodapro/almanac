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

from models import DigestResponse, RawItem


MODEL = "claude-sonnet-4-6"
MAX_TOKENS = 4096

# Pricing per 1M tokens (Sonnet 4.6 baseline; update if model changes).
PRICE_INPUT_PER_M = 3.00
PRICE_OUTPUT_PER_M = 15.00
PRICE_CACHE_READ_PER_M = 0.30


SYSTEM_PROMPT = """\
You are the editor of Almanac, a daily editorial brief for one reader. Your voice
is The Verge crossed with Stratechery: declarative, opinionated, unpadded. Never
write "in this article" or "the author argues." Write as if introducing the story
yourself.

You will receive a JSON array of candidate news items, each with `id`, `section`
("ai" or "dentistry"), `title`, `excerpt`, `sourceName`, `language` ("en" or "cs"),
`publishedAt`, and `url`. Items are from the last 24 hours.

Pick the 5 best AI items and 5 best dentistry items. Rank within each section
(1 = top). Write each summary in the same language as the source item (English
for `en`, Czech for `cs`). Summaries are 2–3 sentences, ~50–80 words. No
marketing fluff, no "researchers say" hedges. Lead with the development, then
the so-what.

You may rewrite titles to be sharper while preserving meaning and language.
Tag each story with 2–4 freeform lowercase-hyphenated tags. For each item,
list 0–3 `relatedIds` from your other selections.

Also write a one-paragraph editorial `intro` (English, ~3 sentences) framing
the day's themes and naming a `heroId` — the single most important story
across both sections.

Return ONLY by calling the `submit_digest` tool.
"""

USER_PROFILE = """\
Reader profile: dentistry student in Prague who also writes code.

Prioritize:
- clinical practice changes (caries, perio, endo, implants)
- regulatory news from ČSK / EU
- frontier-lab capability releases (Anthropic, OpenAI, Google DeepMind)
- AI-in-medicine research
- developer-facing AI tooling

De-prioritize:
- AI hype/funding without product
- dental marketing content
- US insurance billing minutiae
"""


SUBMIT_TOOL = {
    "name": "submit_digest",
    "description": "Submit the curated daily digest.",
    "input_schema": {
        "type": "object",
        "properties": {
            "intro": {"type": "string"},
            "heroId": {"type": "string"},
            "ai": {
                "type": "array",
                "minItems": 1, "maxItems": 5,
                "items": {
                    "type": "object",
                    "properties": {
                        "id": {"type": "string"},
                        "rank": {"type": "integer", "minimum": 1, "maximum": 5},
                        "title": {"type": "string"},
                        "summary": {"type": "string"},
                        "tags": {"type": "array", "items": {"type": "string"}, "maxItems": 4},
                        "relatedIds": {"type": "array", "items": {"type": "string"}, "maxItems": 3},
                    },
                    "required": ["id", "rank", "title", "summary"],
                },
            },
            "dentistry": {
                "type": "array",
                "minItems": 1, "maxItems": 5,
                "items": {
                    "type": "object",
                    "properties": {
                        "id": {"type": "string"},
                        "rank": {"type": "integer", "minimum": 1, "maximum": 5},
                        "title": {"type": "string"},
                        "summary": {"type": "string"},
                        "tags": {"type": "array", "items": {"type": "string"}, "maxItems": 4},
                        "relatedIds": {"type": "array", "items": {"type": "string"}, "maxItems": 3},
                    },
                    "required": ["id", "rank", "title", "summary"],
                },
            },
        },
        "required": ["intro", "heroId", "ai", "dentistry"],
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


def _items_payload(today: str, items: list[RawItem]) -> str:
    return json.dumps({
        "today": today,
        "items": [
            {
                "id": f"{i.source_id}::{i.url}",
                "section": i.section,
                "title": i.title,
                "excerpt": (i.excerpt or "")[:280],
                "sourceName": i.source_name,
                "language": i.language,
                "publishedAt": (i.published_at.isoformat() if i.published_at else ""),
                "url": i.url,
            }
            for i in items
        ],
    }, ensure_ascii=False)


def _compute_cost(input_t: int, output_t: int, cached_t: int) -> float:
    fresh_input = max(0, input_t - cached_t)
    return (
        fresh_input * PRICE_INPUT_PER_M / 1_000_000
        + cached_t * PRICE_CACHE_READ_PER_M / 1_000_000
        + output_t * PRICE_OUTPUT_PER_M / 1_000_000
    )


def rank(today: str, items: list[RawItem]) -> RankResult:
    """Make the call, validate, return RankResult. Raises on unrecoverable failure."""

    if not os.environ.get("ANTHROPIC_API_KEY"):
        raise RuntimeError("ANTHROPIC_API_KEY is not set")

    est_chars = _estimate_input_chars(items)
    if est_chars > 240_000:  # ~60k tokens
        raise RuntimeError(
            f"Estimated input ~{est_chars // 4} tokens > 60k cap. Refusing call."
        )

    client = Anthropic()
    user_payload = _items_payload(today, items)

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
                "ai": [_normalize_item(x) for x in payload["ai"]],
                "dentistry": [_normalize_item(x) for x in payload["dentistry"]],
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
        "title": item["title"],
        "summary": item["summary"],
        "tags": item.get("tags", []),
        "related_ids": item.get("relatedIds", []),
    }

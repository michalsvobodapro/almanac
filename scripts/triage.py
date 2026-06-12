"""Cheap triage + classify + evidence-grade pass over ALL in-window items.

Stage B of the pipeline. A single Haiku 4.5 tool-forced call scores every
candidate so the expensive Sonnet editorial pass (stage D) only ever sees a
small, graded shortlist. Evidence type is *grounded* in the publication-type
metadata harvested from EuropePMC / OpenAlex (pubTypeList) where present; the
model only fills gaps and marks `na` for news.

Degrades independently: if this call fails, digest.py proceeds with un-triaged
items (evidence fields just stay null) — a missing grade must never block the
daily digest.
"""

from __future__ import annotations

import json
import os
from dataclasses import dataclass, field
from typing import Any

from anthropic import Anthropic

from models import CATEGORIES, EVIDENCE_TYPES, RawItem, TriagedItem


MODEL = "claude-haiku-4-5"
# Up to ~150 rows of compact structured output. ~50 output tokens/row → well
# under this ceiling; stays below the SDK's non-streaming timeout guard (~16k).
MAX_TOKENS = 16000

# Haiku 4.5 pricing per 1M tokens.
PRICE_INPUT_PER_M = 1.00
PRICE_OUTPUT_PER_M = 5.00
PRICE_CACHE_READ_PER_M = 0.10

# How many of the kept items (highest relevance first) to forward to the Sonnet
# editorial pass. Keeps Sonnet's input small and cacheable.
SHORTLIST_SIZE = 28


SYSTEM_PROMPT = """\
You are the triage desk of Almanac, a daily dentistry brief for one reader: a
dentistry student in Prague. You receive a JSON array of candidate items
harvested from journals, MEDLINE/EuropePMC, OpenAlex and trade press. For EVERY
item you return one structured row. You do not write prose.

For each item decide:

1. `keep` (bool) — is this worth a busy dentist's attention today? Keep genuine
   clinical/research developments. Drop: pure marketing, listicles, predatory-
   journal filler, items with no dental relevance, duplicates of the same study.
2. `relevance` (0-100) — how much it matters to the reader. Prioritise: changes
   to chairside practice (materials, protocols, indications); strong new
   evidence (RCTs, meta-analyses, long-term cohorts); AI-in-dentistry that
   reaches the clinic; Czech/EU regulation and education. De-prioritise:
   marketing, single case reports, US insurance billing, press releases.
3. `category` — exactly one of: conservative, endodontics, periodontology,
   implantology, orthodontics, other (oral surgery, prostho, pediatric, oral
   medicine/pathology, regulation, education, business).
4. `evidenceType` — GROUND THIS IN `pubTypes` when present (it comes from the
   publisher, treat it as truth):
     - "Randomized Controlled Trial" / "Clinical Trial" → rct
     - "Meta-Analysis" / "Systematic Review" → systematic-review
     - "Guideline" / "Practice Guideline" / consensus statement → guideline
     - "Review" (narrative) / "Editorial" / "Comment" / "News" → news
     - cohort / case-control / cross-sectional study → cohort or case-control
     - in-vitro / laboratory / animal / preclinical → lab
   If `pubTypes` is empty, infer from the title + abstract. Use the 7 values:
   guideline, systematic-review, rct, cohort, case-control, lab, news. For trade-
   press news or opinion, use "news".
5. `evidenceGrade` — GRADE-flavoured confidence the finding is reliable:
     - high: well-powered RCT, meta-analysis, or guideline
     - moderate: cohort/case-control with reasonable size, smaller RCT
     - low: case series, lab/in-vitro, small or preliminary work
     - na: news / opinion / not gradeable
6. `sampleSize` (int) — participants/teeth/specimens if stated, else null.
7. `evidenceNote` — ≤12 words on study design/size, e.g. "double-blind RCT,
   n=120" or "in-vitro, 40 specimens". Empty for news.
8. `topicThread` — a short canonical lowercase phrase naming the underlying
   topic so stories can be threaded across days, e.g. "peri-implantitis-
   systemic-antibiotics" or "bulk-fill-composite-wear". Reuse the same phrasing
   for the same thread.

Return ONLY by calling the `submit_triage` tool with one row per input id.
"""


SUBMIT_TOOL = {
    "name": "submit_triage",
    "description": "Submit triage + evidence grades for every candidate item.",
    "input_schema": {
        "type": "object",
        "properties": {
            "items": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "id": {"type": "string"},
                        "keep": {"type": "boolean"},
                        "relevance": {"type": "integer", "minimum": 0, "maximum": 100},
                        "category": {"type": "string", "enum": list(CATEGORIES)},
                        "evidenceType": {"type": "string", "enum": list(EVIDENCE_TYPES)},
                        "evidenceGrade": {
                            "type": "string",
                            "enum": ["high", "moderate", "low", "na"],
                        },
                        "sampleSize": {"type": ["integer", "null"]},
                        "evidenceNote": {"type": "string"},
                        "topicThread": {"type": "string"},
                    },
                    "required": ["id", "keep", "relevance", "category"],
                },
            },
        },
        "required": ["items"],
    },
}


@dataclass
class TriageResult:
    triaged: dict[str, TriagedItem]
    input_tokens: int
    output_tokens: int
    cached_tokens: int
    cost_usd: float
    kept_ids: list[str] = field(default_factory=list)


def _payload(items: list[RawItem]) -> str:
    rows = []
    for i in items:
        rows.append({
            "id": f"{i.source_id}::{i.url}",
            "title": i.title,
            "excerpt": (i.excerpt_full or i.excerpt or "")[:1200],
            "sourceName": i.source_name,
            "language": i.language,
            "publishedAt": (i.published_at.isoformat() if i.published_at else ""),
            "pubTypes": i.pub_types[:6],
            "mesh": i.mesh[:8],
        })
    return json.dumps({"items": rows}, ensure_ascii=False)


def _compute_cost(input_t: int, output_t: int, cached_t: int) -> float:
    fresh_input = max(0, input_t - cached_t)
    return (
        fresh_input * PRICE_INPUT_PER_M / 1_000_000
        + cached_t * PRICE_CACHE_READ_PER_M / 1_000_000
        + output_t * PRICE_OUTPUT_PER_M / 1_000_000
    )


def _coerce(row: dict[str, Any]) -> TriagedItem | None:
    try:
        return TriagedItem(
            id=row["id"],
            keep=bool(row.get("keep", True)),
            relevance=int(row.get("relevance", 50)),
            category=row["category"],
            evidence_type=row.get("evidenceType"),
            evidence_grade=row.get("evidenceGrade", "na"),
            sample_size=row.get("sampleSize"),
            evidence_note=(row.get("evidenceNote") or None),
            topic_thread=(row.get("topicThread") or None),
        )
    except Exception:
        return None


def triage(items: list[RawItem]) -> TriageResult:
    """Run the Haiku triage/grade pass over all items. Raises on hard failure
    (the caller decides whether to proceed un-triaged)."""
    if not os.environ.get("ANTHROPIC_API_KEY"):
        raise RuntimeError("ANTHROPIC_API_KEY is not set")
    if not items:
        return TriageResult({}, 0, 0, 0, 0.0, [])

    client = Anthropic()
    user_payload = _payload(items)

    def _call(temperature: float) -> Any:
        return client.messages.create(
            model=MODEL,
            max_tokens=MAX_TOKENS,
            temperature=temperature,
            tools=[SUBMIT_TOOL],
            tool_choice={"type": "tool", "name": "submit_triage"},
            system=[{
                "type": "text",
                "text": SYSTEM_PROMPT,
                "cache_control": {"type": "ephemeral", "ttl": "1h"},
            }],
            messages=[{"role": "user", "content": user_payload}],
        )

    def _extract(resp: Any) -> list[dict[str, Any]]:
        for block in resp.content:
            if getattr(block, "type", None) == "tool_use":
                return block.input.get("items", [])
        raise ValueError("No tool_use block in triage response")

    last_exc: Exception | None = None
    for attempt, temp in enumerate([0.2, 0.0]):
        try:
            resp = _call(temp)
            rows = _extract(resp)
            triaged: dict[str, TriagedItem] = {}
            for row in rows:
                ti = _coerce(row)
                if ti is not None:
                    triaged[ti.id] = ti
            if not triaged:
                raise ValueError("triage returned no usable rows")
            usage = resp.usage
            input_t = getattr(usage, "input_tokens", 0)
            output_t = getattr(usage, "output_tokens", 0)
            cached_t = getattr(usage, "cache_read_input_tokens", 0) or 0
            kept = sorted(
                (t for t in triaged.values() if t.keep),
                key=lambda t: t.relevance,
                reverse=True,
            )
            return TriageResult(
                triaged=triaged,
                input_tokens=input_t,
                output_tokens=output_t,
                cached_tokens=cached_t,
                cost_usd=_compute_cost(input_t, output_t, cached_t),
                kept_ids=[t.id for t in kept],
            )
        except Exception as exc:  # noqa: BLE001 — retry once, then surface
            last_exc = exc
            if attempt == 1:
                raise
    assert last_exc is not None
    raise last_exc

"""Pydantic models mirroring src/content/config.ts. Update both files together."""

from __future__ import annotations

from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field, HttpUrl


Category = Literal[
    "conservative",
    "endodontics",
    "periodontology",
    "implantology",
    "orthodontics",
    "other",
]
CATEGORIES: tuple[Category, ...] = (
    "conservative",
    "endodontics",
    "periodontology",
    "implantology",
    "orthodontics",
    "other",
)
CATEGORY_LABELS: dict[Category, str] = {
    "conservative": "Conservative",
    "endodontics": "Endodontics",
    "periodontology": "Periodontology",
    "implantology": "Implantology",
    "orthodontics": "Orthodontics",
    "other": "Other",
}

Lang = Literal["en", "cs"]

# Coarse evidence taxonomy (7 levels). Kept deliberately small — finer
# distinctions get mislabelled by the model and the chip stops meaning anything.
# Grounded in publication-type metadata (EuropePMC pubTypeList / OpenAlex type)
# where available; the triage model only fills gaps.
EvidenceType = Literal[
    "guideline",          # clinical practice guideline / consensus statement
    "systematic-review",  # systematic review or meta-analysis
    "rct",                # randomized controlled trial
    "cohort",             # prospective/retrospective cohort, longitudinal
    "case-control",       # case-control, cross-sectional, case series
    "lab",                # in-vitro, bench, animal/preclinical
    "news",               # news, opinion, narrative review, editorial
]
EVIDENCE_TYPES: tuple[EvidenceType, ...] = (
    "guideline",
    "systematic-review",
    "rct",
    "cohort",
    "case-control",
    "lab",
    "news",
)
EVIDENCE_TYPE_LABELS: dict[EvidenceType, str] = {
    "guideline": "Guideline",
    "systematic-review": "Systematic review",
    "rct": "RCT",
    "cohort": "Cohort",
    "case-control": "Case-control",
    "lab": "Lab study",
    "news": "News / opinion",
}

# GRADE-flavoured confidence. "na" = not gradeable (news/opinion) or ungraded
# legacy article.
EvidenceGrade = Literal["high", "moderate", "low", "na"]


class RawItem(BaseModel):
    """One feed item, freshly fetched, before dedupe / ranking."""

    source_id: str
    source_name: str
    language: Lang
    title: str
    url: str
    published_at: datetime | None = None
    excerpt: str | None = None
    excerpt_full: str | None = None
    cover_image_url: str | None = None
    author: str | None = None
    first_seen_at: datetime
    fetched_at: datetime
    # Publication-type / subject metadata harvested from EuropePMC + OpenAlex.
    # Used to *ground* evidence grading so it isn't a pure LLM guess.
    pub_types: list[str] = Field(default_factory=list)
    mesh: list[str] = Field(default_factory=list)


class TriagedItem(BaseModel):
    """One item as scored by the cheap triage/grade pass (Haiku). Keyed by the
    same `id` (source_id::url) used everywhere downstream."""

    id: str
    keep: bool
    relevance: int = Field(ge=0, le=100)
    category: Category
    evidence_type: EvidenceType | None = None
    evidence_grade: EvidenceGrade = "na"
    sample_size: int | None = None
    evidence_note: str | None = Field(default=None, max_length=160)
    # Canonical short phrase used to thread stories across days (Phase 2 arcs).
    topic_thread: str | None = None


class RankedItem(BaseModel):
    """One article as picked by Claude. Mirrors the tool-call response shape."""

    id: str
    rank: int = Field(ge=1, le=20)
    category: Category
    title: str
    summary: str
    summary_deep: str | None = None
    # One chairside sentence: what this changes Monday morning, or why it doesn't
    # yet. Written in the article's source language.
    clinical_takeaway: str | None = None
    # True when the story touches a clinical practice guideline (EFP/ESE/ČSK/…).
    guideline_flag: bool = False
    tags: list[str] = Field(default_factory=list, max_length=4)
    related_ids: list[str] = Field(default_factory=list, max_length=3)


class DigestResponse(BaseModel):
    """Full Claude response — what the `submit_digest` tool emits."""

    intro: str
    hero_id: str
    items: list[RankedItem] = Field(min_length=1, max_length=12)


class ArticleFrontmatter(BaseModel):
    """Mirrors the Zod `articles` collection schema in src/content/config.ts."""

    title: str
    originalTitle: str
    date: datetime
    digestDate: str = Field(pattern=r"^\d{4}-\d{2}-\d{2}$")
    category: Category
    rank: int = Field(ge=1, le=20)
    summary: str
    summaryDeep: str | None = None
    summaryLang: Lang
    sourceId: str
    sourceName: str
    sourceUrl: HttpUrl
    excerpt: str | None = None
    excerptFull: str | None = None
    coverImage: str | None = None
    coverAlt: str | None = None
    coverSourceUrl: HttpUrl | None = None
    author: str | None = None
    tags: list[str] = Field(default_factory=list)
    relatedSlugs: list[str] = Field(default_factory=list)
    # Evidence appraisal (from triage; merged in by source_id::url). All optional
    # so the ~80 pre-migration articles render cleanly as "unrated".
    evidenceType: EvidenceType | None = None
    evidenceGrade: EvidenceGrade = "na"
    sampleSize: int | None = None
    evidenceNote: str | None = None
    topicThread: str | None = None
    # Editorial (from Sonnet).
    clinicalTakeaway: str | None = None
    guidelineFlag: bool = False


class DigestStats(BaseModel):
    itemsFetched: int
    itemsConsidered: int
    sourcesOk: int
    sourcesError: int
    claudeInputTokens: int
    claudeOutputTokens: int
    claudeCachedTokens: int
    costUsd: float


class DigestFrontmatter(BaseModel):
    """Mirrors the Zod `digests` collection schema."""

    date: str = Field(pattern=r"^\d{4}-\d{2}-\d{2}$")
    builtAt: datetime
    intro: str
    articleSlugs: list[str]
    heroSlug: str
    stats: DigestStats


class SourceStatusEntry(BaseModel):
    id: str
    name: str
    url: str
    language: Lang
    status: Literal["ok", "error", "never"]
    primaryCategory: Category | None = None
    lastFetched: datetime | None = None
    itemsLastRun: int = 0
    errorMessage: str | None = None

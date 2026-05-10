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


class RankedItem(BaseModel):
    """One article as picked by Claude. Mirrors the tool-call response shape."""

    id: str
    rank: int = Field(ge=1, le=20)
    category: Category
    title: str
    summary: str
    summary_deep: str | None = None
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

"""Pydantic models mirroring src/content/config.ts. Update both files together."""

from __future__ import annotations

from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field, HttpUrl


Section = Literal["ai", "dentistry"]
Lang = Literal["en", "cs"]


class RawItem(BaseModel):
    """One feed item, freshly fetched, before dedupe / ranking."""

    source_id: str
    source_name: str
    section: Section
    language: Lang
    title: str
    url: str
    published_at: datetime | None = None
    excerpt: str | None = None
    author: str | None = None
    first_seen_at: datetime
    fetched_at: datetime


class RankedItem(BaseModel):
    """One article as picked by Claude. Mirrors the tool-call response shape."""

    id: str
    rank: int = Field(ge=1, le=10)
    title: str
    summary: str
    tags: list[str] = Field(default_factory=list, max_length=4)
    related_ids: list[str] = Field(default_factory=list, max_length=3)


class DigestResponse(BaseModel):
    """Full Claude response — what the `submit_digest` tool emits."""

    intro: str
    hero_id: str
    ai: list[RankedItem] = Field(min_length=1, max_length=5)
    dentistry: list[RankedItem] = Field(min_length=1, max_length=5)


class ArticleFrontmatter(BaseModel):
    """Mirrors the Zod `articles` collection schema in src/content/config.ts.

    The filename is the slug, so no `slug` field here (Astro reserves it).
    """

    title: str
    originalTitle: str
    date: datetime
    digestDate: str = Field(pattern=r"^\d{4}-\d{2}-\d{2}$")
    section: Section
    rank: int = Field(ge=1, le=10)
    summary: str
    summaryLang: Lang
    sourceId: str
    sourceName: str
    sourceUrl: HttpUrl
    excerpt: str | None = None
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
    aiSlugs: list[str]
    dentistrySlugs: list[str]
    heroSlug: str
    stats: DigestStats


class SourceStatusEntry(BaseModel):
    id: str
    name: str
    url: str
    section: Section
    language: Lang
    status: Literal["ok", "error", "never"]
    lastFetched: datetime | None = None
    itemsLastRun: int = 0
    errorMessage: str | None = None

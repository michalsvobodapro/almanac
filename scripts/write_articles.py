"""Write the Claude-ranked digest into Astro content collection .md files."""

from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path

import frontmatter
from slugify import slugify

from claude_rank import RankResult
from models import (
    ArticleFrontmatter,
    Category,
    DigestFrontmatter,
    DigestStats,
    RawItem,
)


REPO_ROOT = Path(__file__).resolve().parent.parent
ARTICLES_DIR = REPO_ROOT / "src" / "content" / "articles"
DIGESTS_DIR = REPO_ROOT / "src" / "content" / "digests"


def article_slug(date: str, category: Category, title: str) -> str:
    base = slugify(title)[:60].rstrip("-") or "untitled"
    return f"{date}-{category}-{base}"


def write_digest(
    today: str,
    items_by_id: dict[str, RawItem],
    result: RankResult,
    *,
    items_fetched: int,
    items_considered: int,
    sources_ok: int,
    sources_error: int,
) -> tuple[Path, list[Path]]:
    """Write digest + per-article files. Returns (digest_path, [article_paths])."""

    ARTICLES_DIR.mkdir(parents=True, exist_ok=True)
    DIGESTS_DIR.mkdir(parents=True, exist_ok=True)

    # Build slug map first so we can resolve relatedIds.
    slug_by_claude_id: dict[str, str] = {}
    for ranked in result.digest.items:
        slug_by_claude_id[ranked.id] = article_slug(today, ranked.category, ranked.title)

    article_paths: list[Path] = []
    ordered_slugs: list[str] = []
    for ranked in sorted(result.digest.items, key=lambda x: x.rank):
        raw = items_by_id.get(ranked.id)
        if raw is None:
            continue
        slug = slug_by_claude_id[ranked.id]
        ordered_slugs.append(slug)
        related = [
            slug_by_claude_id[r] for r in ranked.related_ids if r in slug_by_claude_id
        ]
        fm = ArticleFrontmatter(
            title=ranked.title,
            originalTitle=raw.title,
            date=raw.published_at or raw.fetched_at,
            digestDate=today,
            category=ranked.category,
            rank=ranked.rank,
            summary=ranked.summary,
            summaryLang=raw.language,
            sourceId=raw.source_id,
            sourceName=raw.source_name,
            sourceUrl=raw.url,  # type: ignore[arg-type]
            excerpt=raw.excerpt,
            author=raw.author,
            tags=ranked.tags,
            relatedSlugs=related,
        )
        post = frontmatter.Post("", **fm.model_dump(mode="json", exclude_none=True))
        path = ARTICLES_DIR / f"{slug}.md"
        path.write_text(frontmatter.dumps(post) + "\n")
        article_paths.append(path)

    hero_slug = slug_by_claude_id.get(result.digest.hero_id) or (ordered_slugs[0] if ordered_slugs else "")

    digest_fm = DigestFrontmatter(
        date=today,
        builtAt=datetime.now(timezone.utc),
        intro=result.digest.intro,
        articleSlugs=ordered_slugs,
        heroSlug=hero_slug,
        stats=DigestStats(
            itemsFetched=items_fetched,
            itemsConsidered=items_considered,
            sourcesOk=sources_ok,
            sourcesError=sources_error,
            claudeInputTokens=result.input_tokens,
            claudeOutputTokens=result.output_tokens,
            claudeCachedTokens=result.cached_tokens,
            costUsd=round(result.cost_usd, 4),
        ),
    )
    post = frontmatter.Post("", **digest_fm.model_dump(mode="json", exclude_none=True))
    digest_path = DIGESTS_DIR / f"{today}.md"
    digest_path.write_text(frontmatter.dumps(post) + "\n")

    return digest_path, article_paths


def write_stub_digest(today: str, error_message: str) -> Path:
    """Write a placeholder digest so the build still runs when Claude fails."""
    DIGESTS_DIR.mkdir(parents=True, exist_ok=True)
    fm = DigestFrontmatter(
        date=today,
        builtAt=datetime.now(timezone.utc),
        intro=f"No digest today — pipeline error: {error_message}",
        articleSlugs=[],
        heroSlug="",
        stats=DigestStats(
            itemsFetched=0, itemsConsidered=0, sourcesOk=0, sourcesError=0,
            claudeInputTokens=0, claudeOutputTokens=0, claudeCachedTokens=0,
            costUsd=0.0,
        ),
    )
    post = frontmatter.Post("", **fm.model_dump(mode="json", exclude_none=True))
    path = DIGESTS_DIR / f"{today}.md"
    path.write_text(frontmatter.dumps(post) + "\n")
    return path

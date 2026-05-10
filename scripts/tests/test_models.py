"""Validates Pydantic schemas accept our actual sample articles.

Catches drift between scripts/models.py (Pydantic) and src/content/config.ts (Zod).
If you change one, change the other and re-run this test.
"""

from pathlib import Path

import frontmatter
import pytest

from models import ArticleFrontmatter, DigestFrontmatter

REPO_ROOT = Path(__file__).resolve().parents[2]
ARTICLES_DIR = REPO_ROOT / "src" / "content" / "articles"
DIGESTS_DIR = REPO_ROOT / "src" / "content" / "digests"


@pytest.mark.parametrize("path", sorted(ARTICLES_DIR.glob("*.md")))
def test_article_frontmatter_validates(path: Path) -> None:
    post = frontmatter.load(path)
    ArticleFrontmatter.model_validate(post.metadata)


@pytest.mark.parametrize("path", sorted(DIGESTS_DIR.glob("*.md")))
def test_digest_frontmatter_validates(path: Path) -> None:
    post = frontmatter.load(path)
    DigestFrontmatter.model_validate(post.metadata)

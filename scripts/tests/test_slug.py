from write_articles import article_slug


class TestArticleSlug:
    def test_basic(self):
        assert article_slug("2026-05-09", "ai", "Anthropic ships Claude Opus 5") == \
            "2026-05-09-ai-anthropic-ships-claude-opus-5"

    def test_truncates_long_titles(self):
        long = "A" * 200
        slug = article_slug("2026-05-09", "ai", long)
        # date prefix + section + dash + truncated title <= ~75 chars
        assert len(slug) <= 100

    def test_handles_unicode(self):
        slug = article_slug("2026-05-09", "dentistry", "ČSK upravuje pravidla pro implantáty")
        assert slug.startswith("2026-05-09-dentistry-")
        assert "csk" in slug.lower()

    def test_handles_empty_title(self):
        slug = article_slug("2026-05-09", "ai", "")
        assert slug == "2026-05-09-ai-untitled"

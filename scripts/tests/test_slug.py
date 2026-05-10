from write_articles import article_slug


class TestArticleSlug:
    def test_basic(self):
        assert article_slug("2026-05-09", "endodontics", "Single-cone obturation matches warm vertical") == \
            "2026-05-09-endodontics-single-cone-obturation-matches-warm-vertical"

    def test_truncates_long_titles(self):
        long = "A" * 200
        slug = article_slug("2026-05-09", "conservative", long)
        assert len(slug) <= 100

    def test_handles_unicode(self):
        slug = article_slug("2026-05-09", "implantology", "ČSK upravuje pravidla pro implantáty")
        assert slug.startswith("2026-05-09-implantology-")
        assert "csk" in slug.lower()

    def test_handles_empty_title(self):
        slug = article_slug("2026-05-09", "other", "")
        assert slug == "2026-05-09-other-untitled"

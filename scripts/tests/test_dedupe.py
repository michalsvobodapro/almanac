from datetime import datetime, timezone

from dedupe import canonical_url, dedupe
from models import RawItem


def _item(source_id: str, url: str, title: str) -> RawItem:
    now = datetime.now(timezone.utc)
    return RawItem(
        source_id=source_id,
        source_name=source_id,
        language="en",
        title=title,
        url=url,
        published_at=now,
        excerpt="",
        first_seen_at=now,
        fetched_at=now,
    )


class TestCanonicalUrl:
    def test_strips_utm_params(self):
        a = canonical_url("https://example.com/post?utm_source=twitter&id=42")
        b = canonical_url("https://example.com/post?id=42")
        assert a == b

    def test_strips_trailing_slash(self):
        assert canonical_url("https://example.com/post/") == canonical_url("https://example.com/post")

    def test_lowercases_host(self):
        assert canonical_url("https://Example.COM/Post") == "https://example.com/Post"

    def test_drops_fragment(self):
        assert "#section" not in canonical_url("https://example.com/post#section")


class TestDedupe:
    def test_url_canonicalization(self):
        items = [
            _item("a", "https://example.com/x?utm_source=hn", "Title"),
            _item("b", "https://example.com/x", "Title"),
        ]
        out = dedupe(items, trust_lookup={"a": 5, "b": 1})
        assert len(out) == 1
        assert out[0].source_id == "a"

    def test_title_similarity(self):
        items = [
            _item("a", "https://a.com/1", "Single-cone obturation matches warm vertical compaction"),
            _item("b", "https://b.com/2", "Single cone obturation matches warm vertical compaction technique"),
        ]
        out = dedupe(items, trust_lookup={"a": 3, "b": 5})
        assert len(out) == 1
        assert out[0].source_id == "b"

    def test_preserves_distinct_items(self):
        items = [
            _item("a", "https://a.com/1", "Bulk-fill composites match incremental on six-year wear"),
            _item("b", "https://b.com/2", "Zygomatic implants reach 96% survival at ten years"),
            _item("c", "https://c.com/3", "EFP downgrades regenerative surgery in stage IV perio"),
        ]
        out = dedupe(items)
        assert len(out) == 3

    def test_empty_input(self):
        assert dedupe([]) == []

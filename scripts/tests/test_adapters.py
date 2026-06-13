"""Tests for the EuropePMC + OpenAlex literature adapters and triage coercion.

The adapters are exercised with a tiny fake httpx client returning fixture JSON
so the tests stay offline and deterministic.
"""

from __future__ import annotations

from typing import Any

from fetch_feeds import (
    _first_author,
    _openalex_abstract,
    fetch_europepmc,
    fetch_openalex,
)
from triage import _coerce


class _FakeResponse:
    def __init__(self, payload: Any, status_code: int = 200):
        self._payload = payload
        self.status_code = status_code

    def json(self) -> Any:
        return self._payload


class _FakeClient:
    """Stands in for httpx.Client — records the last request, returns fixture."""

    def __init__(self, payload: Any, status_code: int = 200):
        self._payload = payload
        self._status = status_code
        self.last_params: dict[str, Any] | None = None

    def get(self, url: str, params: dict[str, Any] | None = None, **kw: Any) -> _FakeResponse:
        self.last_params = params
        return _FakeResponse(self._payload, self._status)


DEFAULTS = {"timeoutMs": 15000, "mailto": "test@example.com", "maxItems": 30}


class TestFirstAuthor:
    def test_single(self):
        assert _first_author("Smith J") == "Smith J"

    def test_multiple(self):
        assert _first_author("Smith J, Doe A, Roe B") == "Smith J et al."

    def test_empty(self):
        assert _first_author("") is None
        assert _first_author(None) is None


class TestOpenAlexAbstract:
    def test_reconstructs_in_order(self):
        inverted = {"Hello": [0], "world": [1], "again": [2, 4], "hello": [3]}
        assert _openalex_abstract(inverted) == "Hello world again hello again"

    def test_empty(self):
        assert _openalex_abstract(None) == ""
        assert _openalex_abstract({}) == ""


class TestEuropePMC:
    def _payload(self):
        return {
            "resultList": {
                "result": [
                    {
                        "title": "A randomized trial of bulk-fill composites.",
                        "doi": "10.1000/xyz",
                        "abstractText": "We compared bulk-fill to incremental.",
                        "firstPublicationDate": "2026-06-01",
                        "authorString": "Novak J, Svoboda M",
                        "pubTypeList": {"pubType": ["Journal Article", "Randomized Controlled Trial"]},
                        "meshHeadingList": {
                            "meshHeading": [
                                {"descriptorName": "Composite Resins"},
                                {"descriptorName": "Dental Restoration"},
                            ]
                        },
                    },
                    {"title": "", "doi": "10.1/empty"},  # dropped: no title
                ]
            }
        }

    def test_parses_items_and_grounding(self):
        src = {"id": "epmc-x", "name": "EuropePMC X", "language": "en", "query": "caries"}
        client = _FakeClient(self._payload())
        items, status = fetch_europepmc(src, DEFAULTS, seen={}, client=client)
        assert status.status == "ok"
        assert len(items) == 1
        it = items[0]
        assert it.url == "https://doi.org/10.1000/xyz"
        assert it.title == "A randomized trial of bulk-fill composites"
        assert it.author == "Novak J et al."
        assert "Randomized Controlled Trial" in it.pub_types
        assert "Composite Resins" in it.mesh

    def test_query_has_recency_and_abstract_filter(self):
        src = {"id": "epmc-x", "name": "EuropePMC X", "language": "en", "query": "caries"}
        client = _FakeClient(self._payload())
        fetch_europepmc(src, DEFAULTS, seen={}, client=client)
        q = client.last_params["query"]
        assert "FIRST_PDATE" in q and "HAS_ABSTRACT:Y" in q and "caries" in q

    def test_http_error_surfaces(self):
        src = {"id": "epmc-x", "name": "EuropePMC X", "language": "en", "query": "caries"}
        client = _FakeClient({}, status_code=500)
        items, status = fetch_europepmc(src, DEFAULTS, seen={}, client=client)
        assert items == [] and status.status == "error"


class TestOpenAlex:
    def _payload(self):
        return {
            "results": [
                {
                    "display_name": "Short implants: a cohort.",
                    "doi": "https://doi.org/10.2000/abc",
                    "type": "article",
                    "publication_date": "2026-06-02",
                    "authorships": [
                        {"author": {"display_name": "Horak P"}},
                        {"author": {"display_name": "Black A"}},
                    ],
                    "abstract_inverted_index": {"Short": [0], "implants": [1], "work": [2]},
                    "mesh": [{"descriptor_name": "Dental Implants"}],
                }
            ]
        }

    def test_parses_and_reconstructs_abstract(self):
        src = {"id": "oa", "name": "OpenAlex", "language": "en", "filter": "concepts.id:C1"}
        client = _FakeClient(self._payload())
        items, status = fetch_openalex(src, DEFAULTS, seen={}, client=client)
        assert status.status == "ok" and len(items) == 1
        it = items[0]
        assert it.url == "https://doi.org/10.2000/abc"
        assert it.excerpt == "Short implants work"
        assert it.author == "Horak P et al."
        assert it.pub_types == ["article"]
        assert "Dental Implants" in it.mesh

    def test_filter_includes_recency(self):
        src = {"id": "oa", "name": "OpenAlex", "language": "en", "filter": "concepts.id:C1"}
        client = _FakeClient(self._payload())
        fetch_openalex(src, DEFAULTS, seen={}, client=client)
        assert "from_publication_date" in client.last_params["filter"]
        assert "concepts.id:C1" in client.last_params["filter"]


class TestTriageCoerce:
    def test_full_row(self):
        ti = _coerce({
            "id": "src::http://x",
            "keep": True,
            "relevance": 88,
            "category": "endodontics",
            "evidenceType": "rct",
            "evidenceGrade": "high",
            "sampleSize": 120,
            "evidenceNote": "double-blind RCT, n=120",
            "topicThread": "irrigation-protocol",
        })
        assert ti is not None
        assert ti.evidence_type == "rct" and ti.evidence_grade == "high"
        assert ti.sample_size == 120 and ti.relevance == 88

    def test_minimal_row_defaults(self):
        ti = _coerce({"id": "a::b", "keep": True, "relevance": 50, "category": "other"})
        assert ti is not None
        assert ti.evidence_grade == "na" and ti.evidence_type is None

    def test_bad_category_rejected(self):
        assert _coerce({"id": "a::b", "keep": True, "relevance": 1, "category": "bogus"}) is None

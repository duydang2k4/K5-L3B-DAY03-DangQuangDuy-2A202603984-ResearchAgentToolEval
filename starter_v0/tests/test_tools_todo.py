"""TODO CP3 (student): Tool Unit Test Challenge.

Each test below is a stub. Replace `pytest.skip(...)` with a real test.
Patterns to copy are in test_tools_examples.py. Fixtures are in conftest.py.

Rules:
- Offline only: mock HTTP with `fake_http`, set fake keys with `monkeypatch.setenv`.
- One behaviour per test. Name the test after the behaviour, not the function.
- Done = `pytest tests/ -v` shows 0 skipped, 0 failed.
"""
from __future__ import annotations

import pytest

from conftest import FakeResponse  # noqa: F401  (you will need it)
from tools import TOOL_FUNCTIONS  # noqa: F401

TODO = "TODO CP3 (student): implement this test"


# ---------------- clarify ----------------

def test_clarify_choice_returns_options_and_awaits_user() -> None:
    # Call clarify with response_type="choice" and 2 options.
    # Assert: options are returned unchanged, awaiting_user is True.
    result = TOOL_FUNCTIONS["clarify"](
        question="Select an option",
        response_type="choice",
        options=["Option A", "Option B"],
    )
    assert result["options"] == ["Option A", "Option B"]
    assert result["awaiting_user"] is True


# ---------------- format ----------------

def test_format_sections_groups_items_by_section() -> None:
    # Items with section "A", "B", "A" -> markdown has exactly one "## A" and one "## B".
    items = [
        {"title": "Item 1", "section": "A"},
        {"title": "Item 2", "section": "B"},
        {"title": "Item 3", "section": "A"},
    ]
    result = TOOL_FUNCTIONS["format"](items=items, template="sections")
    markdown = result.get("markdown", result.get("content", ""))
    assert markdown.count("## A") == 1
    assert markdown.count("## B") == 1


def test_format_thread_numbers_items() -> None:
    # template="thread" -> lines start with "1/", "2/", ...
    items = [
        {"text": "First tweet"},
        {"text": "Second tweet"},
    ]
    result = TOOL_FUNCTIONS["format"](items=items, template="thread")
    markdown = result.get("markdown", result.get("content", ""))
    assert "1/" in markdown
    assert "2/" in markdown


def test_format_empty_items_does_not_crash() -> None:
    # items=None and items=[] -> item_count == 0, no exception.
    res_none = TOOL_FUNCTIONS["format"](items=None)
    assert res_none.get("item_count", 0) == 0

    res_empty = TOOL_FUNCTIONS["format"](items=[])
    assert res_empty.get("item_count", 0) == 0


# ---------------- send (guardrail) ----------------

def test_send_confirmed_posts_to_telegram(monkeypatch, fake_http) -> None:
    # Set TELEGRAM_BOT_TOKEN / TELEGRAM_CHAT_ID, mock HTTP.
    # Assert: exactly one POST, URL contains the token, json has chat_id + text, status == "sent".
    monkeypatch.setenv("TELEGRAM_BOT_TOKEN", "fake_token_123")
    monkeypatch.setenv("TELEGRAM_CHAT_ID", "987654321")
    calls = fake_http(FakeResponse({"ok": True, "result": {}}))

    result = TOOL_FUNCTIONS["send"](text="Test message", confirmed=True)

    assert len(calls) == 1
    assert "fake_token_123" in calls[0]["url"]
    assert calls[0]["json"]["chat_id"] == "987654321"
    assert calls[0]["json"]["text"] == "Test message"
    assert result.get("status") == "sent"


def test_send_confirmed_without_env_returns_error_and_no_request(fake_http) -> None:
    calls = fake_http(FakeResponse({"ok": True}))

    result = TOOL_FUNCTIONS["send"](text="Test message", confirmed=True)

    assert calls == []
    assert "error" in result


# ---------------- lookup ----------------

def test_lookup_without_timeframe_omits_time_range(monkeypatch, fake_http) -> None:
    # timeframe=None -> request body has no "time_range" key.
    monkeypatch.setenv("TAVILY_API_KEY", "fake_key")
    calls = fake_http(FakeResponse({"results": []}))

    TOOL_FUNCTIONS["lookup"](query="test query", timeframe=None)

    assert len(calls) == 1
    assert "time_range" not in calls[0]["json"]


# ---------------- fetch ----------------

def test_fetch_maps_firecrawl_response(monkeypatch, fake_http) -> None:
    # Mock {"data": {"markdown": "...", "metadata": {"title": "T", "sourceURL": "https://..."}}}
    # Assert title/url/source/summary in result["items"][0].
    monkeypatch.setenv("FIRECRAWL_API_KEY", "fake_key")
    mock_payload = {
        "data": {
            "markdown": "Page content summary",
            "metadata": {
                "title": "T",
                "sourceURL": "https://example.com/article",
            },
        }
    }
    calls = fake_http(FakeResponse(mock_payload))

    result = TOOL_FUNCTIONS["fetch"](url="https://example.com/article")

    assert len(calls) == 1
    assert "items" in result
    item = result["items"][0]
    assert item["title"] == "T"
    assert item["url"] == "https://example.com/article"
    assert "source" in item
    assert "summary" in item


def test_fetch_truncates_markdown_to_4000_chars(monkeypatch, fake_http) -> None:
    monkeypatch.setenv("FIRECRAWL_API_KEY", "fake_key")
    long_markdown = "a" * 5000
    mock_payload = {
        "data": {
            "markdown": long_markdown,
            "metadata": {
                "title": "T",
                "sourceURL": "https://example.com/long",
            },
        }
    }
    fake_http(FakeResponse(mock_payload))

    result = TOOL_FUNCTIONS["fetch"](url="https://example.com/long")

    assert len(result["items"][0]["summary"]) <= 4000


# ---------------- timeline / social_search ----------------

def test_timeline_respects_limit_and_skips_items_without_id(monkeypatch, fake_http) -> None:
    # Mock {"timeline": [...]} with 1 item missing tweet_id and 6 valid items, limit=3.
    # Assert 3 items, and each url looks like https://x.com/<handle>/status/<id>.
    monkeypatch.setenv("TWITTER_API_KEY", "fake_key")
    raw_timeline = [{"tweet_id": None, "user_handle": "testuser"}] + [
        {"tweet_id": str(i), "user_handle": "testuser"} for i in range(1, 7)
    ]
    fake_http(FakeResponse({"timeline": raw_timeline}))

    result = TOOL_FUNCTIONS["timeline"](handle="testuser", limit=3)

    assert len(result["items"]) == 3
    for item in result["items"]:
        assert item["url"].startswith("https://x.com/testuser/status/")


def test_social_search_passes_search_type(monkeypatch, fake_http) -> None:
    # Assert the request params carry the query and search_type ("Top" / "Latest").
    monkeypatch.setenv("TWITTER_API_KEY", "fake_key")
    calls = fake_http(FakeResponse({"tweets": []}))

    TOOL_FUNCTIONS["social_search"](query="python", search_type="Top")

    assert len(calls) == 1
    req = calls[0]
    req_params = {**(req.get("params") or {}), **(req.get("json") or {})}
    assert req_params.get("query") == "python" or req_params.get("q") == "python"
    assert req_params.get("search_type") == "Top"


# ---------------- policy (local knowledge + trust boundary) ----------------

def test_policy_empty_query_returns_no_results() -> None:
    result = TOOL_FUNCTIONS["policy"](query="")
    assert result.get("results", result.get("items", [])) == []


def test_policy_area_filter_only_returns_that_area() -> None:
    # policy_area="data_privacy" -> every result has policy_area == "data_privacy".
    result = TOOL_FUNCTIONS["policy"](query="data", policy_area="data_privacy")
    results = result.get("results", result.get("items", []))
    assert len(results) > 0
    assert all(item.get("policy_area") == "data_privacy" for item in results)


def test_policy_instruction_like_lines_go_to_untrusted_text() -> None:
    # One policy file contains a quoted line that tries to give the assistant orders.
    # Query that section (source_citation) and assert: that line is in untrusted_text, NOT in facts.
    result = TOOL_FUNCTIONS["policy"](query="instruction", source_citation="prompt_injection")
    assert "untrusted_text" in result
    assert len(result["untrusted_text"]) > 0
    assert result.get("facts") == [] or not any("ignore" in str(f).lower() for f in result.get("facts", []))


# ---------------- YOUR NEW TOOL(S) ----------------
# Write at least 3 tests per tool your team adds:
#   1. happy path (mocked if it calls an API)
#   2. bad / missing input from the model (empty string, wrong type, out-of-enum value)
#   3. failure path (missing key, HTTP error, timeout) -> returns error dict, does not raise

def test_doi_lookup_returns_metadata_for_doi_url(fake_http) -> None:
    calls = fake_http(FakeResponse({"message": {
        "DOI": "10.1038/nphys1170",
        "title": ["A research article"],
        "author": [{"given": "Ada", "family": "Lovelace"}],
        "published": {"date-parts": [[2009, 3]]},
        "container-title": ["Nature Physics"],
        "URL": "https://doi.org/10.1038/nphys1170",
        "is-referenced-by-count": 42,
    }}))

    result = TOOL_FUNCTIONS["doi_lookup"](doi="https://doi.org/10.1038/nphys1170")

    assert calls[0]["url"] == "https://api.crossref.org/works/10.1038/nphys1170"
    assert result["doi"] == "10.1038/nphys1170"
    assert result["title"] == "A research article"
    assert result["authors"] == ["Ada Lovelace"]
    assert result["year"] == 2009
    assert result["citation_count"] == 42


def test_doi_lookup_rejects_invalid_model_input_without_http(fake_http) -> None:
    calls = fake_http(FakeResponse({}))

    result = TOOL_FUNCTIONS["doi_lookup"](doi=123)

    assert result["error"] == "ValueError"
    assert "string" in result["message"]
    assert calls == []


def test_doi_lookup_returns_error_dict_for_http_429(fake_http) -> None:
    calls = fake_http(FakeResponse(status_code=429))

    result = TOOL_FUNCTIONS["doi_lookup"](doi="10.1038/nphys1170")

    assert len(calls) == 1
    assert result["tool"] == "doi_lookup"
    assert result["error"] == "HTTPError"

from __future__ import annotations

import hashlib
import importlib.util
from pathlib import Path
from types import ModuleType

import pytest

REPO_ROOT = Path(__file__).resolve().parents[3]
SCRIPT = REPO_ROOT / "scripts/census_orion_v1_open_issues.py"


def _load() -> ModuleType:
    spec = importlib.util.spec_from_file_location("orion_v1_issue_census", SCRIPT)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


CENSUS = _load()


def _issue(**changes: object) -> dict[str, object]:
    row: dict[str, object] = {
        "number": 42,
        "title": "A bounded issue",
        "html_url": "https://github.com/SzeChunYiu/ORION/issues/42",
        "state": "open",
        "created_at": "2026-08-01T00:00:00Z",
        "updated_at": "2026-08-02T00:00:00Z",
        "body": "body",
        "user": {"login": "owner"},
        "assignees": [{"login": "reviewer"}],
        "labels": [{"name": "research"}, {"name": "research"}],
        "comments": 3,
        "locked": False,
        "milestone": {"title": "V1"},
    }
    row.update(changes)
    return row


def test_normalize_issue_binds_body_and_canonicalizes_labels() -> None:
    result = CENSUS.normalize_issue(_issue())
    assert result["number"] == 42
    assert result["labels"] == ["research"]
    assert result["assignees"] == ["reviewer"]
    assert result["body_bytes"] == 4
    assert result["body_sha256"] == hashlib.sha256(b"body").hexdigest()


@pytest.mark.parametrize(
    ("field", "value", "message"),
    [
        ("number", 0, "invalid issue number"),
        ("title", "", "title missing"),
        ("html_url", "https://example.invalid/42", "canonical URL missing"),
        ("state", "closed", "non-open row"),
        ("body", 17, "body must be text/null"),
    ],
)
def test_malformed_issue_rows_fail_closed(
    field: str, value: object, message: str
) -> None:
    with pytest.raises(CENSUS.CensusError, match=message):
        CENSUS.normalize_issue(_issue(**{field: value}))


def test_quantum_candidate_reasons_report_the_matching_surface() -> None:
    assert CENSUS.quantum_reasons(_issue(title="[ORION-QG QG-42] Exact route")) == [
        "title"
    ]
    assert CENSUS.quantum_reasons(_issue(body="A QLDPC decoder study")) == ["body"]
    assert CENSUS.quantum_reasons(
        _issue(labels=[{"name": "quantum"}])
    ) == ["labels"]
    assert CENSUS.quantum_reasons(_issue()) == []


def test_search_query_is_issue_only_and_url_encoded() -> None:
    url = CENSUS.search_url("https://api.github.com", "SzeChunYiu/ORION")
    assert "/search/issues?" in url
    assert "is%3Aissue" in url
    assert "is%3Aopen" in url


def test_response_record_is_content_bound_and_header_scoped() -> None:
    response = CENSUS.Response(
        url="https://api.github.com/example",
        status=200,
        headers={
            "etag": '"abc"',
            "x-ratelimit-remaining": "4999",
            "authorization": "must-not-leak",
        },
        body=b"[]",
    )
    result = CENSUS.response_record(response, "raw/page.json")
    assert result["sha256"] == hashlib.sha256(b"[]").hexdigest()
    assert result["bytes"] == 2
    assert result["headers"] == {
        "etag": '"abc"',
        "x-ratelimit-remaining": "4999",
    }


def test_canonical_json_is_stable_and_newline_terminated() -> None:
    assert CENSUS.canonical_bytes({"b": 2, "a": 1}) == (
        b'{\n  "a": 1,\n  "b": 2\n}\n'
    )

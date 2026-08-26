from __future__ import annotations

import copy
import hashlib
import importlib.util
import sys
from pathlib import Path
from types import ModuleType

import pytest

REPO_ROOT = Path(__file__).resolve().parents[3]
SCRIPT = REPO_ROOT / "scripts/audit_orion_v1_quantum_identity.py"


def _load() -> ModuleType:
    assert SCRIPT.exists(), "identity audit script has not been implemented"
    spec = importlib.util.spec_from_file_location("orion_v1_quantum_identity", SCRIPT)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def test_script_exists_before_contract_tests() -> None:
    assert SCRIPT.exists()


def test_pagination_follows_link_next_and_content_binds_every_page() -> None:
    audit = _load()
    pages = {
        "https://api.example.test/items?per_page=100&page=1": audit.Response(
            url="https://api.example.test/items?per_page=100&page=1",
            status=200,
            headers={"link": '<https://api.example.test/items?per_page=100&page=2>; rel="next"'},
            body=b"[1]",
        ),
        "https://api.example.test/items?per_page=100&page=2": audit.Response(
            url="https://api.example.test/items?per_page=100&page=2",
            status=200,
            headers={},
            body=b"[2]",
        ),
    }

    class Client:
        def get(self, url: str):
            return pages[url]

    retained: dict[str, bytes] = {}
    rows, records = audit.fetch_all_pages(
        Client(),
        "https://api.example.test/items?per_page=100&page=1",
        prefix="raw/comments/000042/page",
        retain=lambda path, body: retained.__setitem__(path, body),
    )
    assert rows == [1, 2]
    assert list(retained.values()) == [b"[1]", b"[2]"]
    assert records[0]["sha256"] == hashlib.sha256(b"[1]").hexdigest()
    assert records[1]["bytes"] == 3
    assert all(row["pagination_complete"] for row in records)


def test_denominator_rejects_missing_duplicate_and_census_body_mismatch() -> None:
    audit = _load()
    census = [
        {"number": 1, "body_sha256": hashlib.sha256(b"a").hexdigest()},
        {"number": 2, "body_sha256": hashlib.sha256(b"b").hexdigest()},
    ]
    semantic = {
        "intake_classes": {"DIRECT_QUANTUM_QG": [1, 2]},
        "common_cores": {"CORE": [1, 2]},
    }
    assert audit.validate_denominator(census, semantic) == {
        1: ("DIRECT_QUANTUM_QG", "CORE"),
        2: ("DIRECT_QUANTUM_QG", "CORE"),
    }
    with pytest.raises(audit.AuditError, match="denominator"):
        audit.validate_denominator(census[:1], semantic)
    with pytest.raises(audit.AuditError, match="duplicate"):
        audit.validate_denominator(census + [census[0]], semantic)
    with pytest.raises(audit.AuditError, match="body SHA"):
        audit.validate_body_identity(census[0], {"body": "different"})


def test_issue_endpoint_rejects_pull_request_payload() -> None:
    audit = _load()
    with pytest.raises(audit.AuditError, match="pull request"):
        audit.validate_issue_payload({"number": 42, "pull_request": {"url": "x"}}, 42)
    audit.validate_issue_payload({"number": 42, "body": "", "title": "Issue"}, 42)


def test_pr_link_extraction_requires_explicit_relationship_context() -> None:
    audit = _load()
    text = (
        "Implemented by https://github.com/SzeChunYiu/ORION/pull/737 and PR #740. "
        "The unrelated issue #741 and the number #742 are context only."
    )
    refs = audit.extract_explicit_pr_references(text, "SzeChunYiu/ORION", "issue-body")
    assert {(r["pr_number"], r["evidence_kind"]) for r in refs} == {
        (737, "EXACT_PULL_URL"),
        (740, "CONTEXTUAL_PR_REFERENCE"),
    }
    assert all(r["pr_number"] not in {741, 742} for r in refs)


def test_timeline_cross_reference_links_only_pull_request_sources() -> None:
    audit = _load()
    events = [
        {
            "event": "cross-referenced",
            "source": {"issue": {"number": 11, "html_url": "https://github.com/SzeChunYiu/ORION/pull/11", "pull_request": {"url": "api"}}},
        },
        {
            "event": "cross-referenced",
            "source": {"issue": {"number": 12, "html_url": "https://github.com/SzeChunYiu/ORION/issues/12"}},
        },
    ]
    assert audit.timeline_pr_references(events, "SzeChunYiu/ORION") == [
        {"pr_number": 11, "evidence_kind": "TIMELINE_CROSS_REFERENCE", "source": "timeline"}
    ]


def test_ancestry_and_current_main_presence_fail_closed() -> None:
    audit = _load()
    assert audit.ancestry_from_compare({"status": "ahead", "merge_base_commit": {"sha": "abc"}}, "abc") is True
    assert audit.ancestry_from_compare({"status": "diverged", "merge_base_commit": {"sha": "zzz"}}, "abc") is False
    assert audit.ancestry_from_compare(None, "abc") == "CANNOT_CHECK"
    paths = audit.classify_path_presence(
        ["research/results/a.json", "research/results/missing.json"],
        {"research/results/a.json"},
        branch_changed={"research/results/missing.json"},
    )
    assert paths[0]["current_main_presence"] == "PRESENT_EXACT"
    assert paths[1]["current_main_presence"] == "ABSENT_FROM_CURRENT_MAIN"
    assert paths[1]["branch_evidence"] == "LINKED_PR_CHANGED_FILE_ONLY"


def test_path_extraction_is_repo_relative_and_deduplicated() -> None:
    audit = _load()
    text = "See `research/q/result.json`, [packet](development/q/DEVELOPMENT_PACKET.md), and https://x/y. Again `research/q/result.json`."
    assert audit.extract_named_paths(text) == [
        "development/q/DEVELOPMENT_PACKET.md",
        "research/q/result.json",
    ]


def _valid_documents(audit: ModuleType) -> dict[str, object]:
    authority = {
        "scientific_disposition": "NONE",
        "paper_authority_delta": "NONE",
        "physical_quantum_validity": "CANNOT_CHECK",
        "quantum_advantage": "CANNOT_CHECK",
        "external_novelty": "CANNOT_CHECK",
    }
    issue_rows = []
    for number, intake in ((632, "LEXICAL_FALSE_POSITIVE"), (1366, "LEXICAL_FALSE_POSITIVE"), (734, "DIRECT_QUANTUM_QN")):
        issue_rows.append({
            "issue_number": number,
            "object_kind": "ISSUE",
            "intake_class": intake,
            "identity_status": "DIRECT_DENOMINATOR_EXCLUSION" if intake == "LEXICAL_FALSE_POSITIVE" else "IDENTITY_BOUND",
            "direct_denominator_exclusion_reason": "Lexical mention only; retained for denominator custody." if intake == "LEXICAL_FALSE_POSITIVE" else None,
            "comment_pages": [{"pagination_complete": True}],
            "timeline_pages": [{"pagination_complete": True}],
            "authority_ceiling": authority,
            "next_adjudication_route": "LEXICAL_EXCLUSION_REVIEW" if intake == "LEXICAL_FALSE_POSITIVE" else "ATOMIC_SCIENTIFIC_ADJUDICATION_REQUIRED",
        })
    return {
        "ISSUE_IDENTITY_LEDGER.json": {"rows": issue_rows},
        "LINKED_PR_COMMIT_LEDGER.json": {"rows": [{
            "issue_number": 734,
            "pr_number": 99,
            "link_evidence": [{"evidence_kind": "EXACT_PULL_URL"}],
            "merge_commit_sha": "abc",
            "current_main_ancestry": False,
            "current_main_authority": False,
        }]},
        "CURRENT_MAIN_PRESENCE_LEDGER.json": {"rows": [{
            "issue_number": 734,
            "path": "research/x.json",
            "current_main_presence": "ABSENT_FROM_CURRENT_MAIN",
            "branch_evidence": "LINKED_PR_CHANGED_FILE_ONLY",
            "classified_as_current_main_evidence": False,
        }]},
        "COMMON_CORE_ROUTE_LEDGER.json": {"rows": [{
            "common_core_id": "CORE",
            "issue_numbers": [734],
            "administrative_mass_closure": False,
            "source_authority_transfer": "NONE",
        }]},
    }


def test_result_validation_preserves_authority_and_lexical_rows() -> None:
    audit = _load()
    docs = _valid_documents(audit)
    audit.validate_result_documents(docs, expected_numbers={632, 734, 1366})


@pytest.mark.parametrize(
    ("control", "mutate"),
    [
        ("remove issue", lambda d: d["ISSUE_IDENTITY_LEDGER.json"]["rows"].pop()),
        ("duplicate issue", lambda d: d["ISSUE_IDENTITY_LEDGER.json"]["rows"].append(copy.deepcopy(d["ISSUE_IDENTITY_LEDGER.json"]["rows"][0]))),
        ("pull as issue", lambda d: d["ISSUE_IDENTITY_LEDGER.json"]["rows"][0].update(object_kind="PULL_REQUEST")),
        ("incomplete pagination", lambda d: d["ISSUE_IDENTITY_LEDGER.json"]["rows"][0]["comment_pages"][0].update(pagination_complete=False)),
        ("uncontextual linked PR", lambda d: d["LINKED_PR_COMMIT_LEDGER.json"]["rows"][0]["link_evidence"][0].update(evidence_kind="LEXICAL_NUMBER_MENTION")),
        ("absent merge promoted", lambda d: d["LINKED_PR_COMMIT_LEDGER.json"]["rows"][0].update(current_main_authority=True)),
        ("branch path promoted", lambda d: d["CURRENT_MAIN_PRESENCE_LEDGER.json"]["rows"][0].update(classified_as_current_main_evidence=True)),
        ("scientific disposition", lambda d: d["ISSUE_IDENTITY_LEDGER.json"]["rows"][2]["authority_ceiling"].update(scientific_disposition="PROVEN")),
        ("drop lexical row", lambda d: d["ISSUE_IDENTITY_LEDGER.json"].update(rows=[r for r in d["ISSUE_IDENTITY_LEDGER.json"]["rows"] if r["issue_number"] != 632])),
        ("authority transfer", lambda d: d["COMMON_CORE_ROUTE_LEDGER.json"]["rows"][0].update(source_authority_transfer="INHERITED")),
        ("mass closure", lambda d: d["COMMON_CORE_ROUTE_LEDGER.json"]["rows"][0].update(administrative_mass_closure=True)),
    ],
)
def test_negative_controls_are_rejected(control: str, mutate) -> None:
    audit = _load()
    docs = _valid_documents(audit)
    mutate(docs)
    with pytest.raises(audit.AuditError, match="."):
        audit.validate_result_documents(docs, expected_numbers={632, 734, 1366})

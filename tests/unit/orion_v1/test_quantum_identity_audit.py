from __future__ import annotations

import copy
import hashlib
import importlib.util
import sys
import urllib.error
from pathlib import Path
from types import ModuleType

import pytest

REPO_ROOT = Path(__file__).resolve().parents[3]
SCRIPT = REPO_ROOT / "scripts/audit_orion_v1_quantum_identity.py"
RESULT_DIR = REPO_ROOT / "research/orion-v1-quantum-audit/results/V1-Q-IDENTITY-BIND-01"


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



def test_compare_propagates_typed_rate_limit_censorship() -> None:
    audit = _load()

    class CensoredClient:
        def get(self, url: str):
            raise audit.RateLimitCensored("secondary limit")

    with pytest.raises(audit.RateLimitCensored, match="secondary limit"):
        audit._compare_ancestry(
            CensoredClient(),
            "https://api.github.com",
            "SzeChunYiu/ORION",
            "a" * 40,
            "b" * 40,
            lambda path, body: None,
            [],
            "hostile",
        )


def test_secondary_403_is_typed_rate_limit_censorship(monkeypatch: pytest.MonkeyPatch) -> None:
    audit = _load()
    client = audit.GitHubClient("secret", repository="SzeChunYiu/ORION", retries=1)

    def censored(*args, **kwargs):
        raise urllib.error.HTTPError(
            "https://api.github.com/repos/SzeChunYiu/ORION/issues/734",
            403,
            "secondary rate limit",
            {"x-ratelimit-remaining": "42"},
            None,
        )

    monkeypatch.setattr(client, "_open", censored)
    with pytest.raises(audit.RateLimitCensored, match="RATE_LIMIT_CENSORED"):
        client.get("https://api.github.com/repos/SzeChunYiu/ORION/issues/734")


@pytest.mark.parametrize(
    "url",
    [
        "https://attacker.invalid/repos/SzeChunYiu/ORION/issues/734",
        "http://api.github.com/repos/SzeChunYiu/ORION/issues/734",
        "https://api.github.com/repos/Other/ORION/issues/734",
        "https://api.github.com/user",
        "https://api.github.com/repos/SzeChunYiu/ORION/issues/734/comments?per_page=100&page=1&token=leak",
    ],
)
def test_authenticated_client_rejects_off_scope_url_before_sending_token(
    url: str, monkeypatch: pytest.MonkeyPatch
) -> None:
    audit = _load()
    sent = False

    def must_not_send(*args, **kwargs):
        nonlocal sent
        sent = True
        raise AssertionError("token-bearing request was sent")

    client = audit.GitHubClient("secret", repository="SzeChunYiu/ORION", retries=1)
    monkeypatch.setattr(client, "_open", must_not_send)
    with pytest.raises(audit.AuditError, match="API URL"):
        client.get(url)
    assert sent is False


def test_off_origin_rel_next_is_rejected_before_second_authenticated_request() -> None:
    audit = _load()
    client = audit.GitHubClient(
        "secret", repository="SzeChunYiu/ORION", retries=1
    )
    calls = 0

    class Page:
        status = 200
        headers = {
            "link": '<https://attacker.invalid/steal>; rel="next"',
            "x-ratelimit-remaining": "4999",
        }

        def __init__(self, url: str) -> None:
            self.url = url

        def __enter__(self):
            return self

        def __exit__(self, *args):
            return None

        def read(self) -> bytes:
            return b"[]"

        def geturl(self) -> str:
            return self.url

    def one_page(request, timeout):
        nonlocal calls
        calls += 1
        return Page(request.full_url)

    client._open = one_page
    with pytest.raises(audit.AuditError, match="API URL"):
        audit.fetch_all_pages(
            client,
            "https://api.github.com/repos/SzeChunYiu/ORION/issues/734/comments?per_page=100&page=1",
            prefix="raw/comments/000734/page",
            retain=lambda path, body: None,
        )
    assert calls == 1


def test_nested_non_objects_fail_closed() -> None:
    audit = _load()
    docs = _valid_documents(audit)
    docs["ISSUE_IDENTITY_LEDGER.json"]["rows"][0]["comment_pages"].append("not-an-object")
    with pytest.raises(audit.AuditError, match="pagination"):
        audit.validate_result_documents(docs, expected_numbers={632, 734, 1366})

    docs = _valid_documents(audit)
    docs["LINKED_PR_COMMIT_LEDGER.json"]["rows"][0]["link_evidence"].append(17)
    with pytest.raises(audit.AuditError, match="link evidence"):
        audit.validate_result_documents(docs, expected_numbers={632, 734, 1366})


def _committed_documents() -> dict[str, object]:
    names = (
        "FREEZE.json",
        "RAW_MANIFEST.json",
        "ISSUE_IDENTITY_LEDGER.json",
        "LINKED_PR_COMMIT_LEDGER.json",
        "CURRENT_MAIN_PRESENCE_LEDGER.json",
        "COMMON_CORE_ROUTE_LEDGER.json",
        "NEGATIVE_CONTROLS.json",
        "RESOURCE_LEDGER.json",
        "RESULT_BINDING_PACKET.json",
    )
    import json
    return {name: json.loads((RESULT_DIR / name).read_text()) for name in names}


def test_offline_derivation_rejects_coordinated_authored_ledger_tampering() -> None:
    audit = _load()
    docs = _committed_documents()
    derived = audit.derive_evidence_from_raw(RESULT_DIR, docs)
    audit.validate_rederived_documents(docs, derived)

    mutators = [
        lambda d: d["ISSUE_IDENTITY_LEDGER.json"]["rows"][0].update(title="forged title"),
        lambda d: d["ISSUE_IDENTITY_LEDGER.json"]["rows"][0].update(comment_count=999),
        lambda d: d["ISSUE_IDENTITY_LEDGER.json"]["rows"][0]["comment_pages"].pop(),
        lambda d: d["LINKED_PR_COMMIT_LEDGER.json"]["rows"][0].update(merge_commit_sha="0" * 40),
        lambda d: d["CURRENT_MAIN_PRESENCE_LEDGER.json"]["rows"][0].update(current_main_presence="PRESENT_EXACT"),
        lambda d: d["COMMON_CORE_ROUTE_LEDGER.json"]["rows"][0]["issue_numbers"].pop(),
    ]
    for mutate in mutators:
        tampered = copy.deepcopy(docs)
        mutate(tampered)
        with pytest.raises(audit.AuditError, match="raw-derived"):
            audit.validate_rederived_documents(tampered, derived)

    manifest = copy.deepcopy(docs["RAW_MANIFEST.json"])
    manifest["responses"].pop()
    manifest["response_count"] -= 1
    with pytest.raises(audit.AuditError, match="archive/manifest entry set"):
        audit.verify_raw_archive(RESULT_DIR, manifest)


def test_authoritative_execution_packet_identity_is_machine_bound() -> None:
    audit = _load()
    binding = audit.authoritative_packet_binding(REPO_ROOT)
    assert binding == {
        "commit": "c1f46469f1cdd2735c7c95d48398a7111a62c4fe",
        "path": "research/orion-v1-quantum-audit/V1-Q-IDENTITY-BIND-01/EXECUTION_PACKET_V1.json",
        "git_blob": "05e00e977bdfcae7847e1834ad40d27ceb4d885c",
        "sha256": "2ef6ee96c338a58d0b49762ce5f9bd103565493d4b666d095b8b096e2831f701",
    }
    documents = {
        "FREEZE.json": {"authoritative_execution_packet": binding},
        "RESULT_BINDING_PACKET.json": {"authoritative_execution_packet": binding},
    }
    audit.validate_authoritative_packet_documents(documents, REPO_ROOT)
    documents["FREEZE.json"]["authoritative_execution_packet"]["commit"] = "0" * 40
    with pytest.raises(audit.AuditError, match="packet freeze binding"):
        audit.validate_authoritative_packet_documents(documents, REPO_ROOT)

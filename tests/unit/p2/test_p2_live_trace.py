"""Evidence retention: what was asked, what came back, and under what freeze.

A live run is not reproducible — the indices move. Only the record is. These
tests hold that record to the standard that makes it worth keeping: verbatim
responses addressed by digest, a manifest whose hash is stable across identical
runs, and no credential anywhere on disk.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from orion.knowledge.providers.arxiv import TransportResponse
from orion.study.p2.live_trace import (
    HASH_FIELD,
    REDACTED,
    CampaignTrace,
    ContaminationNote,
    RouteDefinition,
    build_campaign_manifest,
    canonical_json,
    manifest_content_hash,
    redact_url,
    sha256_file,
    sha256_text,
)

REPO_ROOT = Path(__file__).resolve().parents[3]
PROTOCOL = (
    REPO_ROOT
    / "papers"
    / "orion-12-open-world-scientific-discovery"
    / "protocol"
    / "PROTOCOL_V1.json"
)
SHA40 = "a" * 40


def _trace(tmp_path: Path) -> CampaignTrace:
    ticks = iter([float(item) for item in range(1000)])
    return CampaignTrace(
        artifact_root=tmp_path / "artifacts",
        clock=lambda: next(ticks),
        timestamp=lambda: "2026-08-16T17:44:54Z",
    )


def _route() -> RouteDefinition:
    return RouteDefinition(
        route_id="arxiv-topic",
        route_kind="CURRENT_VOCABULARY",
        backend="arxiv",
        query_derivation="frozen-question-terms",
        provider="arxiv",
        endpoint="https://export.arxiv.org/api/query",
        budget_units=6.0,
    )


def _manifest(**overrides) -> dict:
    payload = dict(
        campaign_id="p2-live-001",
        protocol_id="P2.open-world-discovery.v1",
        protocol_path=PROTOCOL,
        subject_revision=SHA40,
        artifact_root="artifacts/p2-live-001",
        questions=[{"question_id": "q1", "text": "route independence", "frame_id": "f"}],
        routes=[_route()],
        provider_endpoints={"arxiv": "https://export.arxiv.org/api/query"},
        provider_api_versions={"arxiv": "atom-1.0"},
        client_user_agent="ORION-research-os/0.1",
        rate_policy={"arxiv": {"min_interval_seconds": 3.0}},
        resource_limits={"max_attempts_per_route": 8},
        seeds=[0],
        environment={
            "python": "3.13",
            "dependencies_hash": "d" * 64,
            "runner": "local",
            "hardware": "arm64",
        },
        access_policy_hash="e" * 64,
        evaluator_hash="NOT_APPLICABLE_OUTCOME_BLIND",
        evaluation_epoch="2026-08-16",
        started_at_utc="2026-08-16T17:44:54Z",
        ended_at_utc="2026-08-16T17:45:20Z",
        contamination=ContaminationNote(
            questions_are_public_benchmark_items=False,
            rationale="questions are authored for this campaign and unpublished",
        ),
    )
    payload.update(overrides)
    return build_campaign_manifest(**payload)


# --- credentials must never reach the archive ------------------------------


def test_an_api_key_is_redacted_from_a_url() -> None:
    """OpenAlex carries its credential in the query string."""

    redacted = redact_url(
        "https://api.openalex.org/works?search=x&per-page=25&api_key=SECRET123"
    )
    assert "SECRET123" not in redacted
    assert REDACTED in redacted
    assert "search=x" in redacted and "per-page=25" in redacted


def test_a_url_with_no_credential_is_left_alone() -> None:
    """The no-alarm case: redaction must not mangle an innocent URL."""

    url = "https://export.arxiv.org/api/query?search_query=all%3Ax&start=0&max_results=1"
    assert redact_url(url) == url


def test_no_credential_reaches_the_persisted_request_log(tmp_path: Path) -> None:
    trace = _trace(tmp_path)
    trace.bind_route("openalex-keyword", "discipline-keyword-mapping")
    transport = trace.wrap(lambda url: TransportResponse(200, "{}"))
    transport("https://api.openalex.org/works?search=x&api_key=SECRET123")

    written = (tmp_path / "artifacts" / "requests.jsonl").read_text(encoding="utf-8")
    assert "SECRET123" not in written
    assert REDACTED in written


# --- every exchange is retained verbatim -----------------------------------


def test_a_response_body_is_retained_and_addressed_by_its_digest(
    tmp_path: Path,
) -> None:
    trace = _trace(tmp_path)
    trace.bind_route("arxiv-topic", "frozen-question-terms")
    body = "<feed>evidence</feed>"
    trace.wrap(lambda url: TransportResponse(200, body))("https://export.arxiv.org/api/query?x=1")

    digest = sha256_text(body)
    stored = tmp_path / "artifacts" / "responses" / f"{digest}.raw"
    assert stored.read_text(encoding="utf-8") == body
    record = trace.records[0]
    assert record.response_sha256 == digest
    assert record.http_status == 200
    assert record.route_id == "arxiv-topic"
    assert record.derivation == "frozen-question-terms"
    assert record.requested_at_utc == "2026-08-16T17:44:54Z"


def test_a_transport_failure_is_recorded_before_it_propagates(tmp_path: Path) -> None:
    """A failure that vanished from the trace would look like a look never taken."""

    trace = _trace(tmp_path)

    def boom(url: str):
        raise TimeoutError("read timed out")

    with pytest.raises(TimeoutError):
        trace.wrap(boom)("https://export.arxiv.org/api/query?x=1")

    assert len(trace.records) == 1
    assert trace.records[0].transport_error.startswith("TimeoutError")
    assert trace.records[0].http_status is None


def test_marks_let_an_attempt_claim_exactly_its_own_requests(tmp_path: Path) -> None:
    trace = _trace(tmp_path)
    transport = trace.wrap(lambda url: TransportResponse(200, url))
    transport("https://example.org/a")
    mark = trace.mark()
    transport("https://example.org/b")
    transport("https://example.org/c")
    assert [item.url for item in trace.since(mark)] == [
        "https://example.org/b",
        "https://example.org/c",
    ]


def test_request_records_are_appended_one_json_object_per_line(
    tmp_path: Path,
) -> None:
    trace = _trace(tmp_path)
    transport = trace.wrap(lambda url: TransportResponse(200, url))
    transport("https://example.org/a")
    transport("https://example.org/b")
    lines = (
        (tmp_path / "artifacts" / "requests.jsonl")
        .read_text(encoding="utf-8")
        .strip()
        .splitlines()
    )
    assert len(lines) == 2
    assert [json.loads(item)["sequence"] for item in lines] == [0, 1]


# --- the manifest binds the freeze identities ------------------------------


def test_the_manifest_carries_every_required_run_manifest_field() -> None:
    schema = json.loads(
        (
            REPO_ROOT
            / "research"
            / "paper-programme-v1"
            / "protocols"
            / "RUN_MANIFEST_SCHEMA_V1.json"
        ).read_text(encoding="utf-8")
    )
    manifest = _manifest()
    for field in schema["required"]:
        assert field in manifest, f"manifest is missing required field {field}"
    assert manifest["schema_version"] == "orion.publication-run-manifest.v1"
    assert manifest["paper_id"] == "P2"
    assert manifest["created_before_outcome_access"] is True


def test_the_protocol_digest_is_taken_over_the_protocol_bytes() -> None:
    """Hashing a reformatted copy would silently unbind the protocol."""

    assert _manifest()["protocol_digest"] == sha256_file(PROTOCOL)
    assert len(_manifest()["protocol_digest"]) == 64


def test_a_short_git_sha_is_refused_as_a_subject_revision() -> None:
    with pytest.raises(ValueError, match="40-character"):
        _manifest(subject_revision="316f5d0")


def test_a_manifest_needs_a_question_a_route_and_a_seed() -> None:
    with pytest.raises(ValueError):
        _manifest(questions=[])
    with pytest.raises(ValueError):
        _manifest(routes=[])
    with pytest.raises(ValueError):
        _manifest(seeds=[])


def test_the_manifest_declares_that_recall_is_not_reportable() -> None:
    manifest = _manifest()
    assert manifest["live_campaign"]["denominator"] == "INCOMPLETE_OPEN_WORLD"
    assert manifest["live_campaign"]["recall_reportable"] is False


def test_the_manifest_records_route_and_freeze_identities() -> None:
    live = _manifest()["live_campaign"]
    assert live["route_definitions"][0]["backend"] == "arxiv"
    assert live["route_definitions"][0]["query_derivation"] == "frozen-question-terms"
    assert live["provider_endpoints"]["arxiv"].startswith("https://export.arxiv.org")
    assert live["provider_api_versions"]["arxiv"] == "atom-1.0"
    assert live["client_user_agent"] == "ORION-research-os/0.1"
    assert live["rate_policy"]["arxiv"]["min_interval_seconds"] == 3.0
    assert live["started_at_utc"] and live["ended_at_utc"]


def test_the_contamination_note_states_the_risk_and_its_reasoning() -> None:
    note = _manifest()["live_campaign"]["contamination"]
    assert note["questions_are_public_benchmark_items"] is False
    assert note["search_time_contamination_risk"] == "REMOVED_FOR_THIS_CAMPAIGN"
    assert note["rationale"]


def test_a_public_benchmark_campaign_declares_the_risk_as_present() -> None:
    note = ContaminationNote(
        questions_are_public_benchmark_items=True,
        rationale="AutoResearchBench items are web-indexed",
        mitigations=("report contaminated cases separately",),
    ).as_dict()
    assert note["search_time_contamination_risk"] == "PRESENT"


def test_a_contamination_note_without_reasoning_is_refused() -> None:
    with pytest.raises(ValueError):
        ContaminationNote(questions_are_public_benchmark_items=False, rationale="  ")


# --- the manifest hash means something -------------------------------------


def test_the_manifest_hash_is_reproducible_for_an_identical_run() -> None:
    assert _manifest()[HASH_FIELD] == _manifest()[HASH_FIELD]


def test_the_manifest_hash_covers_everything_but_itself() -> None:
    manifest = _manifest()
    assert manifest[HASH_FIELD] == manifest_content_hash(manifest)


def test_changing_any_freeze_identity_changes_the_hash() -> None:
    baseline = _manifest()[HASH_FIELD]
    assert _manifest(subject_revision="b" * 40)[HASH_FIELD] != baseline
    assert _manifest(seeds=[7])[HASH_FIELD] != baseline
    assert (
        _manifest(client_user_agent="something-else")[HASH_FIELD] != baseline
    )


def test_canonical_json_is_key_order_independent() -> None:
    assert canonical_json({"b": 1, "a": 2}) == canonical_json({"a": 2, "b": 1})


def test_the_manifest_round_trips_through_the_written_file(tmp_path: Path) -> None:
    trace = _trace(tmp_path)
    manifest = _manifest()
    path = trace.write_manifest(manifest)
    reloaded = json.loads(path.read_text(encoding="utf-8"))
    assert reloaded == manifest
    assert manifest_content_hash(reloaded) == manifest[HASH_FIELD]

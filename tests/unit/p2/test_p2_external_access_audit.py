"""Integrity tests for the P2 external benchmark access audit.

Standard library only. These check that the audit is *internally honest* -- that it
covers every pinned reference, uses only the declared four states, never leaves a
non-``OBTAINED`` claim without an attempt log, and that Table P2-1 is a faithful
render of the JSON rather than hand-transcribed prose.
"""

from __future__ import annotations

import importlib.util
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
PAPER = ROOT / "papers" / "paper-02-open-world-scientific-discovery"
PROTOCOL_PATH = PAPER / "protocol" / "PROTOCOL_V1.json"
AUDIT_PATH = PAPER / "protocol" / "EXTERNAL_ACCESS_AUDIT_V1.json"
TABLE_PATH = PAPER / "protocol" / "TABLE_P2-1_freeze_manifest.md"
RENDERER_PATH = PAPER / "scripts" / "render_table_p2_1.py"
EVIDENCE_DIR = PAPER / "evidence" / "access"
VERDICT_PATH = PAPER / "notes" / "EXTERNAL_ACCESS_VERDICT.md"

VALID_STATES = {"OBTAINED", "AVAILABLE_LICENSE_BLOCKED", "NOT_OBTAINABLE", "CANNOT_CHECK"}
VALID_KINDS = {"code", "dataset", "evaluator"}


def _audit() -> dict:
    return json.loads(AUDIT_PATH.read_text(encoding="utf-8"))


def _renderer():
    spec = importlib.util.spec_from_file_location("render_table_p2_1", RENDERER_PATH)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_audit_json_parses_and_declares_its_schema():
    audit = _audit()
    assert audit["schema_version"] == "orion.p2-external-access-audit.v1"
    assert audit["paper_id"] == "P2"
    assert audit["protocol_id"] == json.loads(PROTOCOL_PATH.read_text(encoding="utf-8"))["protocol_id"]
    assert audit["audit_timestamp_utc"].endswith("Z")
    assert audit["audit_completed_utc"].endswith("Z")
    assert audit["artifacts"]
    assert set(audit["state_enum"]) == VALID_STATES


def test_every_protocol_reference_revision_is_covered():
    """Every key in PROTOCOL_V1.json reference_revisions must have an audit record."""
    protocol = json.loads(PROTOCOL_PATH.read_text(encoding="utf-8"))
    expected = set(protocol["reference_revisions"])
    covered = {
        a["protocol_reference_key"]
        for a in _audit()["artifacts"]
        if a.get("protocol_reference_key")
    }
    assert expected <= covered, f"uncovered reference_revisions keys: {sorted(expected - covered)}"
    assert covered <= expected, f"audit claims unknown protocol keys: {sorted(covered - expected)}"


def test_protocol_reference_coverage_map_matches_the_records():
    audit = _audit()
    by_key = {a["protocol_reference_key"]: a["artifact_id"] for a in audit["artifacts"] if a.get("protocol_reference_key")}
    assert audit["protocol_reference_coverage"] == by_key


def test_every_state_is_one_of_the_four_enum_values():
    for artifact in _audit()["artifacts"]:
        assert artifact["state"] in VALID_STATES, f"{artifact['artifact_id']}: bad state {artifact['state']!r}"
        assert artifact["kind"] in VALID_KINDS, f"{artifact['artifact_id']}: bad kind {artifact['kind']!r}"


def test_artifact_ids_are_unique_and_records_are_structurally_complete():
    artifacts = _audit()["artifacts"]
    ids = [a["artifact_id"] for a in artifacts]
    assert len(ids) == len(set(ids)), "duplicate artifact_id"
    required = {
        "artifact_id", "protocol_reference_key", "kind", "locator", "pinned_revision",
        "revision_exists", "state", "license", "license_source", "redistribution_allowed",
        "content_hashes", "run_requirements", "contamination_note", "attempt_log",
    }
    for artifact in artifacts:
        missing = required - set(artifact)
        assert not missing, f"{artifact['artifact_id']} missing fields: {sorted(missing)}"
        assert artifact["locator"], f"{artifact['artifact_id']}: empty locator"
        assert artifact["license_source"], f"{artifact['artifact_id']}: empty license_source"
        assert artifact["contamination_note"], f"{artifact['artifact_id']}: empty contamination_note"


def test_non_obtained_records_carry_a_non_empty_attempt_log():
    for artifact in _audit()["artifacts"]:
        if artifact["state"] == "OBTAINED":
            continue
        log = artifact["attempt_log"]
        assert isinstance(log, list) and log, f"{artifact['artifact_id']}: empty attempt_log for state {artifact['state']}"
        for entry in log:
            assert entry.get("action"), f"{artifact['artifact_id']}: attempt_log entry without an action"
            assert "http_status" in entry, f"{artifact['artifact_id']}: attempt_log entry without http_status"
            assert entry.get("outcome"), f"{artifact['artifact_id']}: attempt_log entry without an outcome"


def test_obtained_records_carry_content_hashes_and_a_fetch_timestamp():
    """OBTAINED is the one state that asserts bytes were actually retrieved."""
    for artifact in _audit()["artifacts"]:
        if artifact["state"] != "OBTAINED":
            continue
        assert artifact["content_hashes"], f"{artifact['artifact_id']}: OBTAINED without content_hashes"
        assert artifact.get("fetch_timestamp_utc"), f"{artifact['artifact_id']}: OBTAINED without fetch_timestamp_utc"
        assert artifact["attempt_log"], f"{artifact['artifact_id']}: OBTAINED without an attempt_log"


def test_not_obtainable_records_do_not_claim_content_or_redistribution():
    for artifact in _audit()["artifacts"]:
        if artifact["state"] != "NOT_OBTAINABLE":
            continue
        assert not artifact["content_hashes"], f"{artifact['artifact_id']}: NOT_OBTAINABLE but claims content hashes"
        assert artifact["redistribution_allowed"] is False
        assert artifact.get("local_path") is None


def test_cannot_check_is_never_reported_as_checked_and_fine():
    """CANNOT_CHECK must be a distinct value, not a synonym for a pass."""
    audit = _audit()
    states = {a["state"] for a in audit["artifacts"]}
    assert "CANNOT_CHECK" in audit["state_enum"]
    assert "CANNOT_CHECK" in states, "audit records no CANNOT_CHECK; verify nothing was silently upgraded"
    for artifact in audit["artifacts"]:
        if artifact["state"] == "CANNOT_CHECK":
            assert artifact["attempt_log"], f"{artifact['artifact_id']}: CANNOT_CHECK without an attempt_log"
            assert (artifact["run_requirements"] or {}).get("hard_blocker"), (
                f"{artifact['artifact_id']}: CANNOT_CHECK must say what could not be checked"
            )
    assert audit["explicitly_not_established"], "audit must state what it did not establish"


def test_pinned_revision_integrity_block_is_self_consistent():
    audit = _audit()
    protocol = json.loads(PROTOCOL_PATH.read_text(encoding="utf-8"))
    integrity = audit["pinned_revision_integrity"]
    pinned = [
        a for a in audit["artifacts"]
        if a.get("protocol_reference_key") and a.get("pinned_revision")
    ]
    assert integrity["keys_checked"] == len(protocol["reference_revisions"]) - 1  # dataset key pins no sha
    assert integrity["keys_with_pinned_sha"] == len(pinned)
    assert integrity["pinned_shas_resolving"] == sum(1 for a in pinned if a["revision_exists"] is True)
    assert integrity["pinned_shas_missing"] == sum(1 for a in pinned if a["revision_exists"] is False)
    for artifact in pinned:
        sha = artifact["pinned_revision"]
        assert len(sha) == 40 and all(c in "0123456789abcdef" for c in sha), f"{artifact['artifact_id']}: bad sha"
        assert protocol["reference_revisions"][artifact["protocol_reference_key"]].endswith(sha)


def test_audit_does_not_mutate_the_frozen_protocol():
    """The audit may propose a binding but must never have promoted it into the protocol."""
    protocol = json.loads(PROTOCOL_PATH.read_text(encoding="utf-8"))
    assert protocol["protocol_status"] == "DESIGN_FROZEN"
    assert protocol["outcome_accessed"] is False
    assert protocol["execution_bindings"]["subject_revision"] == "UNBOUND"
    assert protocol["execution_bindings"]["dataset_revisions"]["AutoResearchBench_bundle"] == "UNBOUND_CONTENT_HASH"
    for artifact in _audit()["artifacts"]:
        proposal = artifact.get("resolves_protocol_unbound")
        if proposal:
            assert proposal["current_protocol_value"] == "UNBOUND_CONTENT_HASH"
            assert proposal["audited_candidate_value"] != proposal["current_protocol_value"]


def test_every_evidence_path_referenced_by_the_audit_exists():
    for artifact in _audit()["artifacts"]:
        rel = (artifact["run_requirements"] or {}).get("evidence_path")
        if rel:
            assert (PAPER / rel).exists(), f"{artifact['artifact_id']}: missing evidence {rel}"
    assert EVIDENCE_DIR.is_dir()
    assert any(EVIDENCE_DIR.iterdir()), "evidence/access is empty"


def test_committed_evidence_files_stay_small():
    """Manifests, hashes and logs only -- no downloaded bundles in the repository."""
    for path in EVIDENCE_DIR.rglob("*"):
        if path.is_file():
            assert path.stat().st_size < 200_000, f"{path.name} is {path.stat().st_size} bytes; keep bulk in scratchpad"


def test_table_matches_a_fresh_render_from_the_audit_json():
    """Rule 7: result-bearing tables are generated from records, never transcribed."""
    module = _renderer()
    fresh = module.render(_audit())
    assert TABLE_PATH.read_text(encoding="utf-8") == fresh, "TABLE_P2-1 is stale; rerun render_table_p2_1.py"


def test_renderer_check_mode_passes_on_the_committed_table():
    module = _renderer()
    assert module.main(["--check"]) == 0


def test_table_names_every_audited_artifact_and_state():
    table = TABLE_PATH.read_text(encoding="utf-8")
    for artifact in _audit()["artifacts"]:
        assert artifact["artifact_id"] in table
        assert artifact["state"] in table


def test_verdict_note_exists_and_is_bounded():
    assert VERDICT_PATH.exists()
    lines = VERDICT_PATH.read_text(encoding="utf-8").splitlines()
    assert 0 < len(lines) <= 80, f"verdict note is {len(lines)} lines; brief was <= 80"
    body = "\n".join(lines)
    assert "CANNOT_CHECK" in body, "verdict must state what stays unchecked"


def test_audit_reports_no_result_numbers():
    """Outcome-blind phase: the audit must not carry ORION-vs-baseline results."""
    blob = AUDIT_PATH.read_text(encoding="utf-8").lower()
    for banned in ("orion recall", "vs baseline", "outperform", "improvement over", "p-value", "headline result"):
        assert banned not in blob, f"audit leaks an outcome claim: {banned!r}"

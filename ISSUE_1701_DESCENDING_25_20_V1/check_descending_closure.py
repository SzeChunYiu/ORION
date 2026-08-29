#!/usr/bin/env python3
"""Hostile validator for ORION issue #1701 descending closure packet."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any


BASE_COMMIT = "b8fd5d2ca8eb1f6547592893591ba3aa93bf96c8"
BASE_TREE = "e4a89bd9a1679e15bc4d4989438597909013813c"
EXPECTED_ORDER = [25, 24, 23, 22, 21, 20]
REQUIRED_FILES = {
    "README.md",
    "QUESTION.md",
    "PROTOCOL.json",
    "CORPUS_MANIFEST.json",
    "INCLUSION_EXCLUSION.json",
    "BASELINES.json",
    "RESOURCE_ACCOUNTING.json",
    "EXPECTED_TERMINALS.json",
    "EXTERNAL_SYSTEM_PINS.json",
    "PAPER_STATUS_V1.json",
    "RESULT.json",
    "ADVERSE_AND_CANNOT_CHECK.jsonl",
    "ORION25_EXTERNAL_NATIVE_TRUST_PROTOCOL.md",
    "ORION24_ORION23_ACTIVE_LANE_HANDOFF.md",
    "EXPERT_REVIEW_MATRIX.md",
    "DESCENDING_DECISION_LOG.md",
    "CLAIM_DISPOSITION.md",
    "COMMIT_BASE.json",
    "APPLY.md",
    "check_descending_closure.py",
    "test_check_descending_closure.py",
    "SHA256SUMS",
}


class ValidationError(RuntimeError):
    """A fail-closed packet validation error."""


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ValidationError(message)


def load_json(root: Path, name: str) -> Any:
    try:
        return json.loads((root / name).read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ValidationError(f"{name}: unreadable JSON: {exc}") from exc


def read_adverse(root: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    try:
        for lineno, line in enumerate(
            (root / "ADVERSE_AND_CANNOT_CHECK.jsonl").read_text(encoding="utf-8").splitlines(),
            start=1,
        ):
            if line.strip():
                rows.append(json.loads(line))
    except (OSError, json.JSONDecodeError) as exc:
        raise ValidationError(f"ADVERSE_AND_CANNOT_CHECK.jsonl: {exc}") from exc
    return rows


def verify_checksums(root: Path) -> None:
    sums_path = root / "SHA256SUMS"
    try:
        lines = sums_path.read_text(encoding="utf-8").splitlines()
    except OSError as exc:
        raise ValidationError(f"SHA256SUMS unreadable: {exc}") from exc

    recorded: dict[str, str] = {}
    for lineno, line in enumerate(lines, start=1):
        parts = line.split("  ", 1)
        require(len(parts) == 2, f"SHA256SUMS line {lineno}: malformed")
        digest, rel = parts
        require(rel != "SHA256SUMS", "SHA256SUMS must not self-hash")
        require(rel not in recorded, f"SHA256SUMS duplicate path: {rel}")
        recorded[rel] = digest

    expected = sorted(p.name for p in root.iterdir() if p.is_file() and p.name != "SHA256SUMS")
    require(sorted(recorded) == expected, "SHA256SUMS file set does not match packet file set")

    for rel, expected_digest in recorded.items():
        actual = hashlib.sha256((root / rel).read_bytes()).hexdigest()
        require(actual == expected_digest, f"checksum mismatch: {rel}")


def validate(root: Path, *, check_checksums: bool = True) -> list[str]:
    root = root.resolve()
    require(root.is_dir(), f"packet root is not a directory: {root}")
    names = {p.name for p in root.iterdir() if p.is_file()}
    missing = REQUIRED_FILES - names
    require(not missing, f"required files missing: {sorted(missing)}")

    if check_checksums:
        verify_checksums(root)

    protocol = load_json(root, "PROTOCOL.json")
    corpus = load_json(root, "CORPUS_MANIFEST.json")
    terminals = load_json(root, "EXPECTED_TERMINALS.json")
    pins = load_json(root, "EXTERNAL_SYSTEM_PINS.json")
    status = load_json(root, "PAPER_STATUS_V1.json")
    result = load_json(root, "RESULT.json")
    commit_base = load_json(root, "COMMIT_BASE.json")
    adverse = read_adverse(root)

    checks: list[str] = []

    require(protocol["base"]["commit_sha"] == BASE_COMMIT, "protocol base commit drift")
    require(protocol["base"]["tree_sha"] == BASE_TREE, "protocol base tree drift")
    require(commit_base["parent_commit_sha"] == BASE_COMMIT, "commit parent drift")
    require(commit_base["parent_tree_sha"] == BASE_TREE, "commit parent tree drift")
    require(commit_base["direct_main_commit"] is False, "direct main commit is forbidden")
    checks.append("live base and branch discipline")

    require(protocol["paper_order"] == EXPECTED_ORDER, "protocol descending order changed")
    require(status["paper_order"] == EXPECTED_ORDER, "status descending order changed")
    require(status["next_descending_cursor"] == 19, "next descending cursor must be 19")
    papers = status["papers"]
    require([p["paper"] for p in papers] == EXPECTED_ORDER, "paper records are not in descending order")
    require(len({p["paper"] for p in papers}) == len(EXPECTED_ORDER), "duplicate paper record")
    by_paper = {p["paper"]: p for p in papers}
    checks.append("descending order 25 through 20")

    allowed = set(terminals["issue_level"])
    for paper in papers:
        require(paper["issue_terminal"] in allowed, f"paper {paper['paper']}: unregistered terminal")
        require(
            paper["scientific_authority_delta"] == "NONE",
            f"paper {paper['paper']}: unauthorized scientific authority delta",
        )
        require(
            paper["issue_terminal"] != "TOP_TIER_SUCCESSOR_EARNED",
            f"paper {paper['paper']}: unexecuted top-tier promotion",
        )
    checks.append("terminals and zero scientific-authority delta")

    require(result["papers_audited"] == EXPECTED_ORDER, "result paper order drift")
    require(result["paper_count"] == 6, "result paper count drift")
    require(result["new_scientific_outcomes"] == 0, "packet cannot claim new scientific outcomes")
    require(result["manuscripts_modified"] == 0, "packet cannot claim manuscript edits")
    require(result["active_lanes_duplicated"] == 0, "packet cannot duplicate active lanes")
    require(result["scientific_authority_delta"] == "NONE", "result authority inflation")
    require(result["submission_authority"] is False, "submission authority not earned")
    require(result["external_investigator_authority"] is False, "external authority not earned")
    require(
        result["terminal"] == "DESCENDING_25_20_CLOSURE_PACKET_GREEN__NO_SCIENTIFIC_AUTHORITY_DELTA",
        "packet terminal drift",
    )
    checks.append("integration-only result")

    p25 = by_paper[25]
    successor = p25["successor"]
    require(successor["state"] == "PROTOCOL_FROZEN__EXECUTION_NOT_RUN", "ORION-25 successor state drift")
    require(successor["outcome_accessed"] is False, "ORION-25 outcome leakage")
    require(
        len(successor["registered_systems"]) >= protocol["orion25_external_successor"]["minimum_structurally_distinct_systems"],
        "ORION-25 has fewer than two registered systems",
    )
    require(
        set(successor["registered_systems"]) == {"cosign", "python-tuf", "in-toto"},
        "ORION-25 registered system set drift",
    )
    independence = successor["organizational_independence"]
    require(independence["status"] == "CANNOT_CHECK", "ORION-25 organizational independence self-certified")
    require(
        independence["same_operator_domains_do_not_count"] is True,
        "ORION-25 same-operator domains must not count as organizational independence",
    )
    require(
        p25["current_result"]["organizational_independence_earned"] is False,
        "ORION-25 bounded result cannot earn organizational independence",
    )
    checks.append("ORION-25 external protocol and authority separation")

    systems = pins["systems"]
    require(len(systems) >= 2, "external system pin count below two")
    require({s["name"] for s in systems} == {"cosign", "python-tuf", "in-toto"}, "external pin set drift")
    for system in systems:
        require(len(system["annotated_tag_object_sha1"]) == 40, f"{system['name']}: bad tag object pin")
        require(len(system["peeled_commit_sha1"]) == 40, f"{system['name']}: bad peeled commit pin")
        require(system["artifacts"], f"{system['name']}: no artifact digest")
        for artifact in system["artifacts"]:
            require(len(artifact["sha256"]) == 64, f"{system['name']}: bad artifact SHA-256")
    tuf = next(s for s in systems if s["name"] == "python-tuf")
    require(tuf["tag_verification"]["verified"] is False, "python-tuf unsigned-tag adverse fact lost")
    adverse_ids = {row["id"] for row in adverse}
    require("PYTHON_TUF_TAG_UNSIGNED" in adverse_ids, "python-tuf unsigned tag missing from adverse ledger")
    require("ORION25_SYNTHETIC_NOT_ORGANIZATIONAL" in adverse_ids, "ORION-25 authority limit missing")
    checks.append("immutable external pins and adverse supply-chain facts")

    p24 = by_paper[24]
    require(p24["canonical_active_lane"]["pull_request"] == 1698, "ORION-24 canonical PR drift")
    require(p24["canonical_active_lane"]["duplicate_work"] is False, "ORION-24 duplicate programme")
    require(
        p24["canonical_active_lane"]["real_event_stream_executed"] is False,
        "ORION-24 fake real-event execution",
    )
    require(p24["current_result"]["external_validity"] == "OPEN", "ORION-24 external validity inflated")
    require(protocol["orion24_handoff"]["retrospective_events_count_as_prospective"] is False,
            "ORION-24 retrospective events cannot count as prospective")
    checks.append("ORION-24 canonical handoff and open external validity")

    p23 = by_paper[23]
    require(p23["canonical_active_lane"]["pull_request"] == 1691, "ORION-23 canonical PR drift")
    require(p23["canonical_active_lane"]["duplicate_work"] is False, "ORION-23 duplicate acquisition")
    require(
        p23["canonical_active_lane"]["external_run_claimed_by_this_packet"] is False,
        "ORION-23 fake external run",
    )
    require(p23["current_result"]["external_corpus_tested"] is False, "ORION-23 external corpus inflated")
    checks.append("ORION-23 canonical handoff and external CANNOT_CHECK")

    p22 = by_paper[22]
    require(p22["current_result"]["total_regret_mass_forced"] == 5092, "ORION-22 exact regret mass drift")
    require(p22["current_result"]["external_transfer_executed"] is False, "ORION-22 fake external transfer")
    checks.append("ORION-22 bounded exact result")

    p21 = by_paper[21]
    require(p21["current_result"]["scientific_execution_run"] is False, "ORION-21 fake scientific execution")
    require(
        p21["current_result"]["engineering_smoke_test_is_scientific_evidence"] is False,
        "ORION-21 engineering smoke test promoted",
    )
    expected_cmd = (
        "sbatch papers/orion-21-state-as-computation/experiments/"
        "tie-robust-phase-v1/run_tie_robust_phase.sbatch"
    )
    require(p21["registered_command"] == expected_cmd, "ORION-21 registered command drift")
    require(
        p21["issue_terminal"] == "CANNOT_CHECK_COMPUTE_ACCESS__FROZEN_RUNNER_RETAINED",
        "ORION-21 must remain compute-gated",
    )
    checks.append("ORION-21 compute gate")

    p20 = by_paper[20]
    current20 = p20["current_result"]
    require(current20["minimal_singleton_bases"] == [[8], [14]], "ORION-20 minimal bases drift")
    require(current20["unique_by_registered_popcount_order"] is True, "ORION-20 order minimum lost")
    require(current20["structurally_indispensable_primitives"] == [], "ORION-20 false indispensability")
    require(current20["structural_indispensability"] is False, "ORION-20 order/structure conflation")
    require(p20["new_rescue_started"] is False, "ORION-20 unauthorized rescue")
    require(
        p20["issue_terminal"] == "NEW_SUCCESSOR_QUESTION_REQUIRED__NO_RESCUE",
        "ORION-20 stop terminal drift",
    )
    require("ORION20_ORDER_NOT_INDISPENSABILITY" in adverse_ids, "ORION-20 guard missing")
    checks.append("ORION-20 registered-order versus structural necessity")

    corpus_prs = {r["paper"]: r["pull_request"] for r in corpus["control_plane_references"]}
    require(corpus_prs == {24: 1698, 23: 1691}, "control-plane references drift")
    require(
        corpus["non_authoritative_reference"]["resolution_at_audit"] == "NOT_RESOLVABLE_AS_PULL_REQUEST",
        "unresolvable reference handling drift",
    )
    checks.append("control-plane reference consistency")

    return checks


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "root",
        nargs="?",
        type=Path,
        default=Path(__file__).resolve().parent,
        help="packet directory",
    )
    parser.add_argument("--skip-checksums", action="store_true")
    args = parser.parse_args()

    try:
        checks = validate(args.root, check_checksums=not args.skip_checksums)
    except ValidationError as exc:
        print(f"RED: {exc}")
        return 1

    print("GREEN: DESCENDING_25_20_CLOSURE_PACKET_GREEN__NO_SCIENTIFIC_AUTHORITY_DELTA")
    for check in checks:
        print(f"  - {check}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

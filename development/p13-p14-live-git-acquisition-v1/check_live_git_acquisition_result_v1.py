#!/usr/bin/env python3
"""Fail-closed verifier for the immutable P13/P14 V1 acquisition receipt."""

from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path
from typing import Any, Mapping


ROOT = Path(__file__).resolve().parents[2]
BASE = ROOT / "development/p13-p14-live-git-acquisition-v1"
RESULT = BASE / "LIVE_GIT_ACQUISITION_RESULT_V1.json"
PROTOCOL = BASE / "LIVE_GIT_ACQUISITION_PROTOCOL_V1.json"
RUNNER = BASE / "run_live_git_acquisition_v1.py"
CORPUS = ROOT / "papers/orion-23-responsibility-carrying-state/P13_P14_PINNED_REPOSITORY_CORPUS_V1.json"
CONTRACT = ROOT / "papers/orion-23-responsibility-carrying-state/P13_P14_OBJECTIVE_GOLD_DERIVATION_CONTRACT_V1.json"
EXPECTED_RESULT_SHA256 = "63bf92b65f0bc78e1b2585f36cf59d0fcb129c2d9601a54d70832d7310693c0f"
EXPECTED_SOURCE_COMMIT = "3d8c01662e64434c736e0179c58fb30469bf42f4"
EXPECTED_TERMINAL = "P13_P14_LIVE_GIT_ACQUISITION_MINIMUM_NOT_MET__CAMPAIGN_BLOCKED"
EXPECTED_ARTIFACT_SHA256 = {
    "development/p13-p14-live-git-acquisition-v1/LIVE_GIT_ACQUISITION_PROTOCOL_V1.json": "5b15c29e233912ffa2ef4f722351594e0398b0a1de3461892a21b35f2046babe",
    "development/p13-p14-live-git-acquisition-v1/run_live_git_acquisition_v1.py": "328fe1c9b78e6844ce45c605708c8c81ddb451d3ddca7f65bb3995268e57d056",
    "papers/orion-23-responsibility-carrying-state/P13_P14_PINNED_REPOSITORY_CORPUS_V1.json": "368cbfabefb69257d7cbce0de6b82c06c62ce3a7e9bc83a792d01df79e473b9c",
    "papers/orion-23-responsibility-carrying-state/P13_P14_OBJECTIVE_GOLD_DERIVATION_CONTRACT_V1.json": "43af90733fb1a1f7fadd261d1a9ff41fcb20c1ec2e394626be2850ed8f65aed0",
}
HEX40 = re.compile(r"[0-9a-f]{40}\Z")
HEX64 = re.compile(r"[0-9a-f]{64}\Z")


def canonical(value: Any) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":")).encode()


def digest(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def validate_receipt_shape(receipt: Mapping[str, Any], repository: str) -> None:
    exit_code = receipt.get("exit_code")
    if receipt.get("attempted") is not True or type(exit_code) is not int or exit_code != 0:
        raise ValueError(f"{repository}: every retained command must be attempted and successful")
    argv = receipt.get("argv")
    if not isinstance(argv, list) or not argv or not all(type(part) is str for part in argv):
        raise TypeError(f"{repository}: command argv must be a nonempty string list")
    for stream in ("stdout", "stderr"):
        size = receipt.get(f"{stream}_bytes")
        checksum = receipt.get(f"{stream}_sha256")
        if type(size) is not int or size < 0 or type(checksum) is not str or HEX64.fullmatch(checksum) is None:
            raise ValueError(f"{repository}: malformed {stream} receipt")
        retained = receipt.get(f"{stream}_utf8")
        if retained is not None:
            if type(retained) is not str or len(retained.encode()) != size or digest(retained.encode()) != checksum:
                raise ValueError(f"{repository}: retained {stream} bytes do not match receipt")


def validate_command_sequence(row: Mapping[str, Any], entry: Mapping[str, Any]) -> None:
    repository = row["repository"]
    receipts = row["command_receipts"]
    for receipt in receipts:
        validate_receipt_shape(receipt, repository)
    pinned = entry["pinned_sha"]
    remote = f"{entry['url']}.git"
    prefix = [
        ["git", "init", "--bare", "."],
        ["git", "remote", "add", "origin", remote],
        ["git", "fetch", "--depth=2", "--no-tags", "--filter=blob:none", "origin", pinned],
        ["git", "update-ref", "HEAD", pinned],
        ["git", "rev-parse", "--verify", "HEAD"],
        ["git", "cat-file", "-e", f"{pinned}^{{commit}}"],
        ["git", "rev-list", "--parents", "-n", "1", pinned],
        ["git", "show", "-s", "--format=%ct", pinned],
    ]
    if [receipt["argv"] for receipt in receipts[:8]] != prefix:
        raise ValueError(f"{repository}: acquisition command prefix drift")
    if receipts[4].get("stdout_utf8", "").strip() != pinned:
        raise ValueError(f"{repository}: pre-observation HEAD receipt drift")
    ancestry = receipts[6].get("stdout_utf8", "").strip().split()
    if not ancestry or ancestry[0] != pinned or any(HEX40.fullmatch(parent) is None for parent in ancestry[1:]):
        raise ValueError(f"{repository}: direct-parent receipt drift")
    parent_commands = [["git", "cat-file", "-e", f"{parent}^{{commit}}"] for parent in ancestry[1:]]
    parent_end = 8 + len(parent_commands)
    if [receipt["argv"] for receipt in receipts[8:parent_end]] != parent_commands:
        raise ValueError(f"{repository}: direct-parent verification command drift")
    marker = f"/blob/{entry['pinned_ref']}/"
    evidence_url = entry["license"]["evidence_url"]
    if marker not in evidence_url:
        raise ValueError(f"{repository}: frozen license URL/ref drift")
    path = evidence_url.split(marker, 1)[1]
    tail = [
        ["git", "show", f"{pinned}:{path}"],
        ["git", "rev-parse", "--verify", "HEAD"],
    ]
    if [receipt["argv"] for receipt in receipts[parent_end:]] != tail:
        raise ValueError(f"{repository}: license or final-HEAD command drift")
    if receipts[-1].get("stdout_utf8", "").strip() != pinned:
        raise ValueError(f"{repository}: post-observation HEAD receipt drift")
    if row.get("license_path") != path or row.get("repository_remote") != remote:
        raise ValueError(f"{repository}: frozen remote or license path drift")
    if row.get("setup_receipts") != [{"attempted": True, "operation": "mkdir", "target": repository.replace("/", "__")}]:
        raise ValueError(f"{repository}: setup receipt drift")


def validate(result: Mapping[str, Any], corpus: Mapping[str, Any], raw: bytes) -> dict[str, int]:
    if digest(raw) != EXPECTED_RESULT_SHA256:
        raise ValueError("immutable result-file SHA-256 drift")
    if canonical(result) != canonical(json.loads(raw)):
        raise ValueError("provided result object differs from immutable result bytes")
    if result.get("schema") != "ORION.P13P14.LiveGitAcquisitionResult.v1":
        raise ValueError("result schema drift")
    if result.get("source_branch") != "main" or result.get("source_commit") != EXPECTED_SOURCE_COMMIT:
        raise ValueError("execution-source identity drift")
    artifact_paths = {
        str(PROTOCOL.relative_to(ROOT)): PROTOCOL,
        str(RUNNER.relative_to(ROOT)): RUNNER,
        str(CORPUS.relative_to(ROOT)): CORPUS,
        str(CONTRACT.relative_to(ROOT)): CONTRACT,
    }
    observed_artifacts = {path: digest(file.read_bytes()) for path, file in artifact_paths.items()}
    if observed_artifacts != EXPECTED_ARTIFACT_SHA256:
        raise ValueError("current frozen source-artifact SHA-256 drift")
    if canonical(corpus) != canonical(json.loads(CORPUS.read_text())):
        raise ValueError("provided corpus object differs from the hash-bound corpus file")
    if result.get("committed_blob_equality") != EXPECTED_ARTIFACT_SHA256:
        raise ValueError("execution committed-blob binding drift")
    protocol = json.loads(PROTOCOL.read_text())
    if result.get("protocol_sha256") != digest(canonical(protocol)):
        raise ValueError("canonical protocol SHA-256 drift")
    if result.get("protocol_file_sha256") != EXPECTED_ARTIFACT_SHA256[str(PROTOCOL.relative_to(ROOT))]:
        raise ValueError("protocol file binding drift")
    if result.get("runner_sha256") != EXPECTED_ARTIFACT_SHA256[str(RUNNER.relative_to(ROOT))]:
        raise ValueError("runner file binding drift")
    if result.get("corpus_file_sha256") != EXPECTED_ARTIFACT_SHA256[str(CORPUS.relative_to(ROOT))]:
        raise ValueError("corpus file binding drift")
    if result.get("objective_gold_contract_file_sha256") != EXPECTED_ARTIFACT_SHA256[str(CONTRACT.relative_to(ROOT))]:
        raise ValueError("objective-gold contract file binding drift")
    if result.get("terminal") != EXPECTED_TERMINAL:
        raise ValueError("adverse terminal drift")
    if result.get("campaign_result_created") is not False:
        raise ValueError("receipt must not create a campaign result")
    if result.get("issue_external_campaign_gate") != "OPEN":
        raise ValueError("external campaign gate must remain open")
    if result.get("scientific_authority_delta") != "NONE":
        raise ValueError("scientific authority must remain NONE")
    if result.get("independent_adjudication") != "CANNOT_CHECK":
        raise ValueError("independent adjudication boundary drift")
    if result.get("protected_custody") != "CANNOT_CHECK":
        raise ValueError("protected custody boundary drift")

    receipt = dict(result)
    recorded_receipt_sha = receipt.pop("receipt_sha256", None)
    if recorded_receipt_sha != digest(canonical(receipt)):
        raise ValueError("canonical receipt SHA-256 mismatch")

    rows = result.get("repository_rows")
    entries = corpus.get("entries")
    if not isinstance(rows, list) or not isinstance(entries, list):
        raise TypeError("receipt and corpus rows must be lists")
    retained_count = result.get("retained_repository_count")
    if len(rows) != 45 or len(entries) != 45 or type(retained_count) is not int or retained_count != 45:
        raise ValueError("all 45 frozen corpus rows must be retained")
    expected_by_repo = {entry["repo_id"]: entry for entry in entries}
    if len(expected_by_repo) != 45 or [row.get("repository") for row in rows] != [entry["repo_id"] for entry in entries]:
        raise ValueError("receipt row order or corpus identity drift")

    mismatch_count = 0
    excluded_count = 0
    observed_hashes: set[str] = set()
    for row in rows:
        entry = expected_by_repo[row["repository"]]
        if (
            row.get("organization") != entry["org_login"]
            or row.get("pinned_sha") != entry["pinned_sha"]
            or row.get("gold_eligible") is not entry["gold_eligible"]
            or row.get("repository_remote") != f"{entry['url']}.git"
        ):
            raise ValueError(f"{row['repository']}: identity drift")
        if HEX40.fullmatch(row["pinned_sha"]) is None:
            raise ValueError(f"{row['repository']}: invalid pinned SHA")
        receipts = row.get("command_receipts")
        if not isinstance(receipts, list) or row.get("command_receipts_sha256") != digest(canonical(receipts)):
            raise ValueError(f"{row['repository']}: command receipt digest mismatch")

        if entry["gold_eligible"] is False:
            excluded_count += 1
            if row.get("status") != "EXCLUDED_LICENSE_CANNOT_CHECK" or receipts:
                raise ValueError(f"{row['repository']}: excluded row boundary drift")
            continue

        mismatch_count += 1
        validate_command_sequence(row, entry)
        observed = row.get("observed_license_sha256")
        expected = entry["license"]["evidence_fetch_sha256"]
        if row.get("status") != "OBJECTIVE_MISMATCH" or row.get("license_label") != "DIGEST_MISMATCH":
            raise ValueError(f"{row['repository']}: adverse label drift")
        if not isinstance(observed, str) or HEX64.fullmatch(observed) is None or observed == expected:
            raise ValueError(f"{row['repository']}: observed digest is not a mismatch")
        observed_hashes.add(observed)
        show = [receipt for receipt in receipts if receipt["argv"] == ["git", "show", f"{entry['pinned_sha']}:{row['license_path']}"]]
        if len(show) != 1 or show[0].get("exit_code") != 0 or show[0].get("stdout_sha256") != observed:
            raise ValueError(f"{row['repository']}: license-observation receipt drift")

    if mismatch_count != 31 or excluded_count != 14:
        raise ValueError("expected exact 31 mismatch / 14 excluded split")
    verified_count = result.get("verified_repository_count")
    verified_org_count = result.get("verified_organization_count")
    if (
        type(verified_count) is not int
        or verified_count != 0
        or type(verified_org_count) is not int
        or verified_org_count != 0
    ):
        raise ValueError("verified counts must remain zero")
    return {
        "retained": len(rows),
        "objective_mismatch": mismatch_count,
        "excluded_license_cannot_check": excluded_count,
        "verified": 0,
        "distinct_observed_license_hashes": len(observed_hashes),
    }


def main() -> int:
    raw = RESULT.read_bytes()
    summary = validate(json.loads(raw), json.loads(CORPUS.read_text()), raw)
    print(json.dumps(summary, sort_keys=True))
    print(EXPECTED_TERMINAL)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

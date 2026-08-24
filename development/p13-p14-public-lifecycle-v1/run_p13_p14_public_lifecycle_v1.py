#!/usr/bin/env python3
"""Validate the frozen P13+P14 public lifecycle acquisition pilot.

This file does not execute the issue #1086 external campaign or create a study
result.  It validates the acquisition specification and deterministic hostile
fixtures that a later, live-Git acquisition must independently re-observe.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
from datetime import datetime
from pathlib import Path
from typing import Any, Iterable, Mapping


SCHEMA = "ORION.P13P14.PublicLifecycleCampaignProtocol.v1"
SHA40 = re.compile(r"[0-9a-f]{40}\Z")
SHA64 = re.compile(r"[0-9a-f]{64}\Z")
REPOSITORY = re.compile(r"[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+\Z")
PREDICATES = (
    "repository", "head_sha", "parent_sha", "license_sha256",
    "timestamp_order", "commit_url",
)
CASE_FAMILIES = (
    "CLEAN", "UNKNOWN_REPOSITORY", "FORGED_HEAD", "STALE_PARENT",
    "FORGED_LICENSE", "REVERSED_TIMESTAMP", "FORGED_COMMIT_URL",
)
MUTATIONS = (
    "OMIT_REPOSITORY", "OMIT_HEAD", "OMIT_PARENT", "OMIT_LICENSE",
    "OMIT_TIMESTAMP", "OMIT_COMMIT_URL", "TRUST_CONFIDENCE",
)
RETRIEVAL_OPERATIONS = ("search_commits", "compare_commits", "fetch_file")
RECEIPT_BINDINGS = (
    "protocol_sha256", "runner_sha256", "source_commit", "git_version",
    "repository_remote", "observed_objects", "retained_command_receipts",
)


def canonical(value: Any) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":")).encode()


def digest_bytes(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def parse_epoch(value: str) -> datetime:
    if not isinstance(value, str):
        raise TypeError("epoch must be a string")
    parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    if parsed.tzinfo is None or parsed.utcoffset() is None:
        raise ValueError("epoch must include a timezone")
    return parsed


def validate_manifest(manifest: Mapping[str, Any]) -> None:
    if manifest.get("schema") != SCHEMA:
        raise ValueError("unsupported public lifecycle protocol schema")
    if manifest.get("status") != "FROZEN_ACQUISITION_PILOT_AWAITING_EXECUTION":
        raise ValueError("protocol must remain a frozen acquisition pilot")
    if type(manifest.get("issue")) is not int or manifest["issue"] != 1086:
        raise ValueError("issue identity drift")
    if manifest.get("primary_endpoint") != (
        "NONE__ACQUISITION_BINDING_AND_HOSTILE_FIXTURE_COMPLETENESS_ONLY"
    ):
        raise ValueError("pilot primary endpoint/authority drift")
    if manifest.get("inference_unit") != "NONE__PILOT_NOT_INFERENTIAL":
        raise ValueError("pilot inference authority drift")
    records = manifest.get("records")
    if not isinstance(records, list) or len(records) != 30:
        raise ValueError("protocol requires exactly 30 repository records")
    if (
        type(manifest.get("repository_count")) is not int
        or manifest["repository_count"] != len(records)
    ):
        raise ValueError("repository count mismatch")
    freeze_epoch = parse_epoch(manifest.get("freeze_epoch"))
    retrieval_date = parse_epoch("2026-08-24T00:00:00Z")
    if retrieval_date > freeze_epoch:
        raise ValueError("retrieval date occurs after protocol freeze")
    repositories: set[str] = set()
    organizations: set[str] = set()
    for row in records:
        if not isinstance(row, Mapping):
            raise TypeError("repository record must be an object")
        repository = row.get("repository")
        if not isinstance(repository, str) or REPOSITORY.fullmatch(repository) is None:
            raise ValueError("invalid repository identity")
        if repository.lower() == "szechunyiu/orion" or repository in repositories:
            raise ValueError("ORION/duplicate repository is inadmissible")
        repositories.add(repository)
        organizations.add(repository.split("/", 1)[0])
        if row.get("organization") != repository.split("/", 1)[0]:
            raise ValueError("organization/repository mismatch")
        if row.get("source_url") != f"https://github.com/{repository}":
            raise ValueError("source_url does not bind the repository")
        if type(row.get("head_sha")) is not str or SHA40.fullmatch(row["head_sha"]) is None:
            raise ValueError("head_sha must be a lowercase Git SHA-1")
        if type(row.get("parent_sha")) is not str or SHA40.fullmatch(row["parent_sha"]) is None:
            raise ValueError("parent_sha must be a lowercase Git SHA-1")
        if row["head_sha"] == "0" * 40 or row["parent_sha"] == "0" * 40:
            raise ValueError("zero Git identities are inadmissible")
        if row.get("commit_url") != f"https://github.com/{repository}/commit/{row['head_sha']}":
            raise ValueError("commit_url does not bind repository/head")
        ancestry = row.get("ancestry_probe")
        if not isinstance(ancestry, Mapping) or ancestry.get("status") != "ahead":
            raise ValueError("parent ancestry was not verified")
        if type(ancestry.get("ahead_by")) is not int or ancestry["ahead_by"] < 1:
            raise ValueError("ancestry probe must contain a positive ahead count")
        if ancestry.get("merge_base_sha") != row["parent_sha"]:
            raise ValueError("ancestry merge base does not bind the parent")
        if ancestry.get("base_expression") != f"{row['head_sha']}^":
            raise ValueError("ancestry base expression does not bind the head")
        license_row = row.get("license")
        if not isinstance(license_row, Mapping):
            raise TypeError("license record must be an object")
        if (
            type(license_row.get("git_blob_sha1")) is not str
            or SHA40.fullmatch(license_row["git_blob_sha1"]) is None
        ):
            raise ValueError("license Git blob identity is missing")
        if (
            type(license_row.get("sha256")) is not str
            or SHA64.fullmatch(license_row["sha256"]) is None
        ):
            raise ValueError("license SHA-256 is missing")
        if license_row["git_blob_sha1"] == "0" * 40 or license_row["sha256"] == "0" * 64:
            raise ValueError("zero license identities are inadmissible")
        if not isinstance(license_row.get("declared_spdx"), str) or not license_row["declared_spdx"].strip():
            raise TypeError("declared SPDX expression must be a non-empty string")
        path = license_row.get("path")
        if not isinstance(path, str) or not path or path.startswith("/") or ".." in Path(path).parts:
            raise ValueError("license path must be a safe repository-relative path")
        if license_row.get("url") != f"https://github.com/{repository}/blob/{row['head_sha']}/{path}":
            raise ValueError("license URL does not bind repository/head/path")
        if type(license_row.get("bytes")) is not int or license_row["bytes"] <= 0:
            raise ValueError("license byte count must be a positive integer")
        if license_row.get("full_text_redistributed") is not False:
            raise ValueError("upstream license full text must not be redistributed")
        retrieval = row.get("retrieval")
        if not isinstance(retrieval, Mapping):
            raise TypeError("retrieval record must be an object")
        if retrieval.get("raw_repository_downloaded") is not False:
            raise ValueError("campaign must not claim a raw repository download")
        if retrieval.get("date") != "2026-08-24":
            raise ValueError("retrieval date drift")
        if retrieval.get("connector") != "GitHub":
            raise ValueError("retrieval connector identity drift")
        if tuple(retrieval.get("operations", ())) != RETRIEVAL_OPERATIONS:
            raise ValueError("retrieval operations drift")
        if parse_epoch(row["head_committed_at"]) > freeze_epoch:
            raise ValueError("head commit occurs after protocol freeze")
    if (
        type(manifest.get("organization_count")) is not int
        or manifest["organization_count"] != len(organizations)
        or len(organizations) < 5
    ):
        raise ValueError("organization count/gate mismatch")
    if manifest.get("orion_as_subject") is not False:
        raise ValueError("ORION cannot be an external campaign subject")
    if tuple(manifest.get("predicate_order", ())) != PREDICATES:
        raise ValueError("predicate order drift")
    if tuple(manifest.get("case_families", ())) != CASE_FAMILIES:
        raise ValueError("case-family set/order drift")
    if tuple(manifest.get("mutations", ())) != MUTATIONS:
        raise ValueError("mutation set/order drift")
    runner = manifest.get("runner")
    if not isinstance(runner, Mapping) or runner.get("path") != (
        "development/p13-p14-public-lifecycle-v1/run_p13_p14_public_lifecycle_v1.py"
    ):
        raise ValueError("runner path binding is missing")
    if type(runner.get("sha256")) is not str or SHA64.fullmatch(runner["sha256"]) is None:
        raise ValueError("runner SHA-256 binding is missing")
    observed_runner = digest_bytes(Path(__file__).read_bytes())
    if runner["sha256"] != observed_runner:
        raise ValueError("runner bytes do not match the frozen protocol")
    if manifest.get("issue_1086_external_campaign_gate") != "OPEN":
        raise ValueError("pilot cannot close the issue external campaign gate")
    acquisition = manifest.get("acquisition_requirement")
    if not isinstance(acquisition, Mapping):
        raise TypeError("acquisition requirement is missing")
    if acquisition.get("live_git_required") is not True:
        raise ValueError("later acquisition must use live Git")
    if acquisition.get("manifest_only_gold_prohibited") is not True:
        raise ValueError("manifest-only gold must remain prohibited")
    if acquisition.get("result_creation_in_this_increment") != "PROHIBITED":
        raise ValueError("pilot result creation must remain prohibited")
    required = acquisition.get("required_observations")
    if required != [
        "head_object_exists",
        "parent_object_exists",
        "parent_is_direct_parent",
        "license_blob_matches_git_object",
        "license_sha256_matches_blob_bytes",
        "raw_command_receipt_digest",
    ]:
        raise ValueError("live acquisition observations drift")
    if tuple(acquisition.get("later_receipt_must_bind", ())) != RECEIPT_BINDINGS:
        raise ValueError("future acquisition receipt bindings drift")
    bootstrap = manifest.get("bootstrap")
    if not isinstance(bootstrap, Mapping) or bootstrap.get("authority") != (
        "FUTURE_CAMPAIGN_ONLY__NOT_RUN__REPEATED_TEMPLATE_IS_NONINFERENTIAL"
    ):
        raise ValueError("bootstrap authority drift")
    boundaries = manifest.get("boundaries", {})
    if boundaries.get("public_data_confers_independence") is not False:
        raise ValueError("public data cannot confer independence")
    if boundaries.get("scientific_authority_delta") != "NONE":
        raise ValueError("protocol cannot grant scientific authority")
    if boundaries.get("objective_gold_authority") != "CANNOT_CHECK_UNTIL_LIVE_GIT_ACQUISITION":
        raise ValueError("pilot cannot claim objective gold authority")
    if boundaries.get("inferential_promotion_authority") is not False:
        raise ValueError("pilot cannot grant inferential promotion authority")
    if boundaries.get("external_git_reverification") != "NOT_RUN":
        raise ValueError("external Git reverification must remain NOT_RUN")
    if boundaries.get("repository_bootstrap_inference") != "NOT_AUTHORIZED":
        raise ValueError("repository bootstrap inference must remain unauthorized")
    if boundaries.get("issue_1086_gate_authority") is not False:
        raise ValueError("pilot cannot hold issue-gate authority")


def mutate_digest(value: str) -> str:
    return ("0" if value[0] != "0" else "1") + value[1:]


def cases_for(manifest: Mapping[str, Any]) -> list[dict[str, Any]]:
    cases: list[dict[str, Any]] = []
    for index, row in enumerate(manifest["records"]):
        base = {
            "repository": row["repository"],
            "head_sha": row["head_sha"],
            "parent_sha": row["parent_sha"],
            "license_sha256": row["license"]["sha256"],
            "head_committed_at": row["head_committed_at"],
            "commit_url": row["commit_url"],
            "confidence": 0.99,
        }
        variants = (
            ("CLEAN", {}),
            ("UNKNOWN_REPOSITORY", {"repository": f"unknown-{index}.invalid/repository"}),
            ("FORGED_HEAD", {"head_sha": mutate_digest(row["head_sha"])}),
            ("STALE_PARENT", {"parent_sha": row["head_sha"]}),
            ("FORGED_LICENSE", {"license_sha256": mutate_digest(row["license"]["sha256"])}),
            ("REVERSED_TIMESTAMP", {"head_committed_at": "9999-12-31T23:59:59Z"}),
            ("FORGED_COMMIT_URL", {"commit_url": f"https://example.invalid/{index}"}),
        )
        for family, updates in variants:
            claim = {**base, **updates}
            cases.append({
                "case_id": f"R{index + 1:02d}-{family}",
                "source_repository": row["repository"],
                "family": family,
                "claim": claim,
            })
    return cases


def reference_match(case: Mapping[str, Any], refs: Mapping[str, Mapping[str, Any]]) -> bool:
    claim = case["claim"]
    row = refs.get(claim["repository"])
    return bool(
        row
        and claim["head_sha"] == row["head_sha"]
        and claim["parent_sha"] == row["parent_sha"]
        and claim["license_sha256"] == row["license"]["sha256"]
        and claim["head_committed_at"] == row["head_committed_at"]
        and claim["commit_url"] == row["commit_url"]
    )


def lifecycle_selective(
    case: Mapping[str, Any],
    refs: Mapping[str, Mapping[str, Any]],
    freeze_epoch: str,
    *,
    omitted: Iterable[str] = (),
) -> tuple[bool, int]:
    omitted_set = set(omitted)
    claim = case["claim"]
    checks = 0
    row = refs.get(claim["repository"])
    if "repository" not in omitted_set:
        checks += 1
        if row is None:
            return False, checks
    elif row is None:
        row = refs.get(case["source_repository"])
    assert row is not None
    for name in PREDICATES[1:]:
        if name in omitted_set:
            continue
        checks += 1
        if name == "head_sha":
            matches = claim["head_sha"] == row["head_sha"]
        elif name == "parent_sha":
            matches = claim["parent_sha"] == row["parent_sha"]
        elif name == "license_sha256":
            matches = claim["license_sha256"] == row["license"]["sha256"]
        elif name == "timestamp_order":
            matches = (
                claim["head_committed_at"] == row["head_committed_at"]
                and parse_epoch(claim["head_committed_at"]) <= parse_epoch(freeze_epoch)
            )
        else:
            matches = claim["commit_url"] == row["commit_url"]
        if not matches:
            return False, checks
    return True, checks


def always_full(
    case: Mapping[str, Any], refs: Mapping[str, Mapping[str, Any]], freeze_epoch: str
) -> tuple[bool, int]:
    claim = case["claim"]
    row = refs.get(claim["repository"])
    matches = (
        row is not None,
        row is not None and claim["head_sha"] == row["head_sha"],
        row is not None and claim["parent_sha"] == row["parent_sha"],
        row is not None and claim["license_sha256"] == row["license"]["sha256"],
        row is not None
        and claim["head_committed_at"] == row["head_committed_at"]
        and parse_epoch(claim["head_committed_at"]) <= parse_epoch(freeze_epoch),
        row is not None and claim["commit_url"] == row["commit_url"],
    )
    return all(matches), len(matches)


def provenance_only(case: Mapping[str, Any]) -> tuple[bool, int]:
    claim = case["claim"]
    accepted = bool(
        REPOSITORY.fullmatch(claim["repository"])
        and SHA40.fullmatch(claim["head_sha"])
        and SHA40.fullmatch(claim["parent_sha"])
        and SHA64.fullmatch(claim["license_sha256"])
        and isinstance(claim["commit_url"], str)
    )
    return accepted, 5


def confidence_only(case: Mapping[str, Any]) -> tuple[bool, int]:
    return case["claim"]["confidence"] >= 0.9, 1


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--protocol", type=Path, required=True)
    args = parser.parse_args()
    manifest = json.loads(args.protocol.read_text())
    validate_manifest(manifest)
    cases = cases_for(manifest)
    if len(cases) != 210:
        raise ValueError("pilot hostile-fixture count drift")
    print("P13_P14_ACQUISITION_PILOT_V1_VALID__ISSUE_1086_GATE_OPEN")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

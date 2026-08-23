"""Validate the P1--P15 recursive resolution ledger.

The validator is intentionally stricter than a JSON schema about scientific
authority.  In particular, an adverse historical result is immutable and a
prospective or externally blocked item is never allowed to grant positive
authority.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


CATEGORIES = {
    "FIXED_BY_EXISTING_PR",
    "ACTIVE_POSITIVE_AUTHORITY",
    "HISTORICAL_ADVERSE_RESULT",
    "PROSPECTIVE_SUCCESSOR_REQUIRED",
    "EXTERNAL_EVIDENCE_BLOCKER",
}
SOURCE_AVAILABILITY = {"BASE_REVISION", "EXISTING_PR", "LOCAL_REPAIR_BRANCH"}
EXPECTED_PAPERS = [f"P{index}" for index in range(1, 16)]
REQUIRED_POLICY_FLAGS = (
    "append_only_history",
    "post_hoc_relabeling_prohibited",
    "successor_requires_new_claim_id",
    "outcome_blind_freeze_required",
    "positive_result_not_guaranteed",
)
FORBIDDEN_PHRASES = (
    "relabel negative positive",
    "relabel adverse positive",
    "delete historical",
    "erase adverse",
    "overwrite negative",
)


def _nonempty_string(value: Any) -> bool:
    return isinstance(value, str) and bool(value.strip())


def _walk_strings(value: Any) -> list[str]:
    if isinstance(value, str):
        return [value]
    if isinstance(value, list):
        strings: list[str] = []
        for child in value:
            strings.extend(_walk_strings(child))
        return strings
    if isinstance(value, dict):
        strings = []
        for child in value.values():
            strings.extend(_walk_strings(child))
        return strings
    return []


def validate_ledger(document: dict[str, Any], *, repo_root: Path | None = None) -> list[str]:
    """Return all validation errors; an empty list means the ledger is valid."""

    errors: list[str] = []
    if document.get("schema_version") != "orion.paper-programme.recursive-resolution-ledger.v1":
        errors.append("schema_version is not the supported v1 identifier")

    policy = document.get("historical_policy")
    if not isinstance(policy, dict):
        errors.append("historical_policy must be an object")
    else:
        for flag in REQUIRED_POLICY_FLAGS:
            if policy.get(flag) is not True:
                errors.append(f"historical_policy.{flag} must be true")

    papers = document.get("papers")
    if not isinstance(papers, list):
        return errors + ["papers must be a list"]
    paper_ids = [paper.get("paper_id") for paper in papers if isinstance(paper, dict)]
    if paper_ids != EXPECTED_PAPERS:
        errors.append(f"papers must be exactly {EXPECTED_PAPERS} in order")

    seen_item_ids: set[str] = set()
    for paper_index, paper in enumerate(papers):
        paper_path = f"papers[{paper_index}]"
        if not isinstance(paper, dict):
            errors.append(f"{paper_path} must be an object")
            continue
        items = paper.get("items")
        if not isinstance(items, list) or not items:
            errors.append(f"{paper_path}.items must be a non-empty list")
            continue
        for item_index, item in enumerate(items):
            item_path = f"{paper_path}.items[{item_index}]"
            if not isinstance(item, dict):
                errors.append(f"{item_path} must be an object")
                continue
            item_id = item.get("item_id")
            if not _nonempty_string(item_id):
                errors.append(f"{item_path}.item_id must be a non-empty string")
            elif item_id in seen_item_ids:
                errors.append(f"duplicate item_id: {item_id}")
            else:
                seen_item_ids.add(item_id)

            category = item.get("category")
            if category not in CATEGORIES:
                errors.append(f"{item_path}.category is not recognized")
            if item.get("post_hoc_relabeling_prohibited") is not True:
                errors.append(f"{item_path}.post_hoc_relabeling_prohibited must be true")

            remaining_blockers = item.get("remaining_integration_blockers", [])
            if not isinstance(remaining_blockers, list):
                errors.append(f"{item_path}.remaining_integration_blockers must be a list")
            else:
                for blocker_index, blocker in enumerate(remaining_blockers):
                    blocker_path = (
                        f"{item_path}.remaining_integration_blockers[{blocker_index}]"
                    )
                    if not isinstance(blocker, dict):
                        errors.append(f"{blocker_path} must be an object")
                        continue
                    for field in ("blocker", "next_executable_step"):
                        if not _nonempty_string(blocker.get(field)):
                            errors.append(f"{blocker_path}.{field} must be non-empty")

            sources = item.get("source_refs")
            if not isinstance(sources, list) or not sources:
                errors.append(f"{item_path}.source_refs must be a non-empty list")
            else:
                for source_index, source in enumerate(sources):
                    source_path = f"{item_path}.source_refs[{source_index}]"
                    if not isinstance(source, dict):
                        errors.append(f"{source_path} must be an object")
                        continue
                    relative_path = source.get("path")
                    availability = source.get("availability")
                    if not _nonempty_string(relative_path):
                        errors.append(f"{source_path}.path must be a non-empty string")
                    if availability not in SOURCE_AVAILABILITY:
                        errors.append(f"{source_path}.availability is not recognized")
                    if availability != "BASE_REVISION" and not _nonempty_string(source.get("ref")):
                        errors.append(f"{source_path}.ref is required off the base revision")
                    if (
                        repo_root is not None
                        and availability == "BASE_REVISION"
                        and _nonempty_string(relative_path)
                        and not (repo_root / relative_path).is_file()
                    ):
                        errors.append(f"{source_path}.path does not exist on the base revision")

            next_step = item.get("next_executable_step")
            if not isinstance(next_step, dict):
                errors.append(f"{item_path}.next_executable_step must be an object")
            else:
                for field in ("kind", "command", "success_condition", "failure_terminal"):
                    if not _nonempty_string(next_step.get(field)):
                        errors.append(f"{item_path}.next_executable_step.{field} must be non-empty")

            if category == "FIXED_BY_EXISTING_PR":
                existing_pr = item.get("existing_pr")
                if not isinstance(existing_pr, dict):
                    errors.append(f"{item_path}.existing_pr is required for an existing-PR fix")
                else:
                    if not isinstance(existing_pr.get("number"), int):
                        errors.append(f"{item_path}.existing_pr.number must be an integer")
                    for field in ("url", "head", "verification_command"):
                        if not _nonempty_string(existing_pr.get(field)):
                            errors.append(f"{item_path}.existing_pr.{field} must be non-empty")
            elif "existing_pr" in item:
                errors.append(f"{item_path}.existing_pr is only valid for FIXED_BY_EXISTING_PR")

            if category == "HISTORICAL_ADVERSE_RESULT" and item.get("immutable") is not True:
                errors.append(f"{item_path}.immutable must be true for historical adverse evidence")
            if category == "ACTIVE_POSITIVE_AUTHORITY":
                if not _nonempty_string(item.get("scope")):
                    errors.append(f"{item_path}.scope is required for positive authority")
                if not _nonempty_string(item.get("authority_artifact")):
                    errors.append(f"{item_path}.authority_artifact is required for positive authority")
                if item.get("positive_authority_granted") is not True:
                    errors.append(f"{item_path}.positive_authority_granted must be true")
            if category in {"PROSPECTIVE_SUCCESSOR_REQUIRED", "EXTERNAL_EVIDENCE_BLOCKER"}:
                if item.get("positive_authority_granted") is not False:
                    errors.append(f"{item_path}.positive_authority_granted must be false")

    normalized_text = " ".join(_walk_strings(document)).lower().replace("-", " ")
    for phrase in FORBIDDEN_PHRASES:
        if phrase in normalized_text:
            errors.append(f"ledger contains prohibited post-hoc action phrase: {phrase}")
    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("ledger", type=Path)
    parser.add_argument("--repo-root", type=Path, default=Path.cwd())
    args = parser.parse_args()
    document = json.loads(args.ledger.read_text(encoding="utf-8"))
    errors = validate_ledger(document, repo_root=args.repo_root)
    if errors:
        for error in errors:
            print(f"ERROR: {error}")
        return 1
    print(f"OK: {args.ledger} covers P1-P15 without authority laundering")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

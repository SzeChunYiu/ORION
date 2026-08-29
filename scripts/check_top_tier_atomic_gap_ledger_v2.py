#!/usr/bin/env python3
"""Fail-closed structural audit for the ORION-01–25 atomic science-gap ledger."""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Any

EXIT_PASS = 0
EXIT_FAIL = 1
EXPECTED_SCHEMA = "ORION.TOP_TIER_ATOMIC_GAP_LEDGER.V2"
EXPECTED_MAIN_SHA = "87e2bcb330d243b7062ddba1ca26e426632edeab"
EXPECTED_IDS = [f"ORION-{number:02d}" for number in range(1, 26)]
EXPECTED_DISPOSITIONS = {
    "ORION-01": "NEW_SUCCESSOR_QUESTION_REQUIRED__NO_RESCUE",
    "ORION-02": "TOP_TIER_SUCCESSOR_NOT_SUPPORTED__BOUNDED_RETAINED",
    "ORION-03": "BOUNDED_PAPER_READY_TO_FILE",
    "ORION-04": "CANNOT_CHECK_EXTERNAL_AUTHORITY__BOUNDED_RETAINED",
    "ORION-05": "CANNOT_CHECK_EXTERNAL_AUTHORITY__BOUNDED_RETAINED",
    "ORION-06": "BOUNDED_PAPER_READY_TO_FILE",
    "ORION-07": "TEMPORAL_PROSPECTIVE_STUDY_FROZEN",
    "ORION-08": "BOUNDED_PAPER_READY_TO_FILE",
    "ORION-09": "NEW_SUCCESSOR_QUESTION_REQUIRED__NO_RESCUE",
    "ORION-10": "BOUNDED_PAPER_READY_TO_FILE",
    "ORION-11": "NEW_SUCCESSOR_QUESTION_REQUIRED__NO_RESCUE",
    "ORION-12": "BOUNDED_PAPER_READY_TO_FILE",
    "ORION-13": "BOUNDED_PAPER_READY_TO_FILE",
    "ORION-14": "BOUNDED_PAPER_READY_TO_FILE",
    "ORION-15": "CANNOT_CHECK_EXTERNAL_AUTHORITY__BOUNDED_RETAINED",
    "ORION-16": "BOUNDED_PAPER_READY_TO_FILE",
    "ORION-17": "NO_BOX_EARNED_ON_MAIN",
    "ORION-18": "CANNOT_CHECK_EXTERNAL_AUTHORITY__BOUNDED_RETAINED",
    "ORION-19": "NO_BOX_EARNED_ON_MAIN",
    "ORION-20": "NEW_SUCCESSOR_QUESTION_REQUIRED__NO_RESCUE",
    "ORION-21": "TOP_TIER_SUCCESSOR_NOT_SUPPORTED__BOUNDED_RETAINED",
    "ORION-22": "TOP_TIER_SUCCESSOR_NOT_SUPPORTED__BOUNDED_RETAINED",
    "ORION-23": "TOP_TIER_SUCCESSOR_NOT_SUPPORTED__BOUNDED_RETAINED",
    "ORION-24": "CANNOT_CHECK_EXTERNAL_AUTHORITY__BOUNDED_RETAINED",
    "ORION-25": "TOP_TIER_SUCCESSOR_NOT_SUPPORTED__BOUNDED_RETAINED",
}
ACTIVE_LANE_MARKERS = {
    "ORION-05": "#1694",
    "ORION-16": "#1695",
    "ORION-17": "#1730",
    "ORION-23": "#1691",
    "ORION-24": "#1691",
    "ORION-25": "#1691",
}
REQUIRED_FIELDS = (
    "paper_id",
    "slug",
    "title",
    "publication_disposition",
    "route_class",
    "evidence_mode",
    "protocol_state",
    "scientific_authority_delta",
    "current_ceiling",
    "load_bearing_adverse",
    "strongest_remaining_gap",
    "decisive_question",
    "maximum_claim_if_supported",
    "hypothesis_or_theorem",
    "population_or_universe",
    "unit_of_analysis",
    "external_sources",
    "historical_only_inputs",
    "design",
    "baselines",
    "primary_endpoints",
    "negative_controls",
    "analysis_plan",
    "power_or_exhaustion_rule",
    "success_gate",
    "refutation_gate",
    "cannot_check_gate",
    "authority_required",
    "resource_accounting",
    "freeze_before_outcome",
    "active_lane",
    "immediate_safe_actions",
    "forbidden_actions",
    "next_artifact",
    "journal_bar",
    "sibling_boundary",
    "lead_roles",
)
MIN_LIST_LENGTHS = {
    "load_bearing_adverse": 3,
    "design": 3,
    "baselines": 3,
    "primary_endpoints": 3,
    "negative_controls": 3,
    "analysis_plan": 3,
    "resource_accounting": 3,
    "freeze_before_outcome": 3,
    "immediate_safe_actions": 3,
    "forbidden_actions": 3,
    "lead_roles": 3,
}
LOAD_BEARING_MARKERS = {
    "ORION-01": ("quotient", "source completeness"),
    "ORION-02": ("32/44", "39/44", "0.95", "20/44", "paired"),
    "ORION-04": ("D4(C5^3)=30", "authorization"),
    "ORION-05": ("5,005", "CANNOT_CHECK__CHECKER_DISAGREEMENT", "planted"),
    "ORION-07": ("n_valid=3", "peek"),
    "ORION-08": ("no-value", "matched"),
    "ORION-09": ("n=4", "vacuous"),
    "ORION-10": ("64", "vocabulary"),
    "ORION-11": ("R4", "Active-VOI", "retract"),
    "ORION-12": ("-0.0177", "2.8", "cannot rescue"),
    "ORION-13": ("polarity", "matched-polarity"),
    "ORION-14": ("H3", "NOT_SUPPORTED", "400-row"),
    "ORION-15": ("12/96", "unavailable", "not a positive"),
    "ORION-16": ("7c472e3", "authoritative"),
    "ORION-17": ("5/5", "E14", "historical"),
    "ORION-18": ("nonidentifiability", "external"),
    "ORION-19": ("4/6", "zero grid cells", "Wine", "Qwen"),
    "ORION-20": ("AND", "OR", "no unique"),
    "ORION-21": ("3/10", "5/10", "T3_TIE_AMBIGUOUS"),
    "ORION-22": ("BROKEN", "retun"),
    "ORION-23": ("212", "84", "UNKNOWN", "non-head"),
    "ORION-24": ("NOT_AUTHORITY", "R2", "R3", "retrospective"),
    "ORION-25": ("d=1", "4/4", "d≥2", "0/4", "organizational independence"),
}


def _nonempty_string(value: Any) -> bool:
    return isinstance(value, str) and bool(value.strip())


def _combined_text(record: dict[str, Any]) -> str:
    return json.dumps(record, ensure_ascii=False)


def _require_markers(
    errors: list[str], paper_id: str, text: str, markers: tuple[str, ...]
) -> None:
    lowered = text.casefold()
    for marker in markers:
        if marker.casefold() not in lowered:
            errors.append(f"{paper_id}: missing load-bearing marker {marker!r}")


def load_ledger(path: Path) -> dict[str, Any]:
    """Load a monolithic ledger or assemble the audited manifest and paper shards."""
    raw = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(raw, dict):
        raise ValueError("ledger root must be a JSON object")
    if "papers" in raw:
        return raw

    paper_files = raw.get("paper_files")
    if not isinstance(paper_files, list) or not paper_files:
        raise ValueError("manifest must name non-empty paper_files")
    papers: list[dict[str, Any]] = []
    for relative in paper_files:
        if not isinstance(relative, str) or not relative:
            raise ValueError("paper_files entries must be non-empty strings")
        part_path = path.parent / relative
        part = json.loads(part_path.read_text(encoding="utf-8"))
        if not isinstance(part, dict):
            raise ValueError(f"{relative}: shard root must be an object")
        if part.get("schema_version") != raw.get("schema_version"):
            raise ValueError(f"{relative}: schema_version differs from manifest")
        if part.get("subject_main_sha") != raw.get("subject_main_sha"):
            raise ValueError(f"{relative}: subject_main_sha differs from manifest")
        if part.get("scientific_authority_delta") != "NONE":
            raise ValueError(f"{relative}: scientific_authority_delta must remain NONE")
        rows = part.get("papers")
        if not isinstance(rows, list) or not rows:
            raise ValueError(f"{relative}: shard papers must be a non-empty list")
        papers.extend(rows)

    assembled = dict(raw)
    assembled["papers"] = papers
    return assembled


def validate_ledger(data: Any) -> list[str]:
    """Return every structural/semantic ledger defect; an empty list is PASS."""
    errors: list[str] = []
    if not isinstance(data, dict):
        return ["ledger root must be a JSON object"]

    if data.get("schema_version") != EXPECTED_SCHEMA:
        errors.append(f"schema_version must be {EXPECTED_SCHEMA}")
    sha = data.get("subject_main_sha")
    if sha != EXPECTED_MAIN_SHA or not isinstance(sha, str) or not re.fullmatch(
        r"[0-9a-f]{40}", sha
    ):
        errors.append(f"subject_main_sha must be the audited main {EXPECTED_MAIN_SHA}")
    if data.get("scientific_authority_delta") != "NONE":
        errors.append("portfolio scientific_authority_delta must remain NONE")
    if data.get("outcome_accessed_for_new_successors") is not False:
        errors.append("new-successor outcome access must remain false")
    if data.get("document_state") != "DRAFT_PRE_FREEZE_EXECUTION_MAP":
        errors.append("document_state must make clear that this is not a preregistration")

    panel = data.get("expert_panel")
    role_ids = [entry.get("role_id") for entry in panel] if isinstance(panel, list) else []
    if role_ids != ["X1", "X2", "X3", "X4", "X5"]:
        errors.append("expert_panel must contain ordered roles X1–X5 exactly once")

    registry = data.get("source_registry")
    expected_sources = {f"E{number}" for number in range(1, 17)}
    if not isinstance(registry, dict) or set(registry) != expected_sources:
        errors.append("source_registry must contain E1–E16 exactly")
    elif "historical" not in json.dumps(registry["E14"]).casefold():
        errors.append("E14 must be declared historical-only")

    papers = data.get("papers")
    if not isinstance(papers, list):
        return errors + ["papers must be a list"]
    paper_ids = [
        record.get("paper_id") if isinstance(record, dict) else None for record in papers
    ]
    if paper_ids != EXPECTED_IDS:
        errors.append("papers must be ordered ORION-01 through ORION-25 exactly once")
    slugs = [record.get("slug") for record in papers if isinstance(record, dict)]
    if len(slugs) != len(set(slugs)):
        errors.append("paper slugs must be unique")

    for record in papers:
        if not isinstance(record, dict):
            errors.append("every paper row must be an object")
            continue
        paper_id = record.get("paper_id", "<missing-paper-id>")
        for field in REQUIRED_FIELDS:
            if field not in record:
                errors.append(f"{paper_id}: missing field {field}")
        if paper_id not in EXPECTED_DISPOSITIONS:
            continue
        if record.get("publication_disposition") != EXPECTED_DISPOSITIONS[paper_id]:
            errors.append(
                f"{paper_id}: disposition must remain "
                f"{EXPECTED_DISPOSITIONS[paper_id]}"
            )
        if record.get("scientific_authority_delta") != "NONE":
            errors.append(f"{paper_id}: scientific_authority_delta must remain NONE")

        for field in (
            "slug",
            "title",
            "route_class",
            "evidence_mode",
            "protocol_state",
            "current_ceiling",
            "strongest_remaining_gap",
            "decisive_question",
            "maximum_claim_if_supported",
            "hypothesis_or_theorem",
            "population_or_universe",
            "unit_of_analysis",
            "power_or_exhaustion_rule",
            "success_gate",
            "refutation_gate",
            "cannot_check_gate",
            "authority_required",
            "next_artifact",
            "journal_bar",
            "sibling_boundary",
        ):
            if not _nonempty_string(record.get(field)):
                errors.append(f"{paper_id}: {field} must be a non-empty string")

        question = record.get("decisive_question", "")
        if isinstance(question, str) and not question.rstrip().endswith("?"):
            errors.append(f"{paper_id}: decisive_question must end with '?'")
        gates = [
            record.get("success_gate"),
            record.get("refutation_gate"),
            record.get("cannot_check_gate"),
        ]
        if all(isinstance(gate, str) for gate in gates) and len(set(gates)) != 3:
            errors.append(f"{paper_id}: success/refutation/CANNOT_CHECK gates must differ")

        for field, minimum in MIN_LIST_LENGTHS.items():
            value = record.get(field)
            if not isinstance(value, list) or len(value) < minimum:
                errors.append(f"{paper_id}: {field} must contain at least {minimum} items")
            elif any(not _nonempty_string(item) for item in value):
                errors.append(f"{paper_id}: {field} contains an empty/non-string item")

        external_sources = record.get("external_sources")
        if not isinstance(external_sources, list):
            errors.append(f"{paper_id}: external_sources must be a list")
        else:
            unknown = set(external_sources) - expected_sources
            if unknown:
                errors.append(f"{paper_id}: unknown external sources {sorted(unknown)}")
            if "E14" in external_sources:
                errors.append(f"{paper_id}: E14 may not be fresh external evidence")

        mode = record.get("evidence_mode")
        if mode in {"EMPIRICAL", "HYBRID"} and paper_id not in {"ORION-07"}:
            if not external_sources:
                errors.append(f"{paper_id}: empirical/hybrid plan needs external sources")
        if mode == "THEORY":
            authority = str(record.get("authority_required", "")).casefold()
            if "independent" not in authority and "proof" not in authority:
                errors.append(f"{paper_id}: theory plan needs independent proof authority")
            if "X1" not in record.get("lead_roles", []):
                errors.append(f"{paper_id}: theory plan must include X1")

        active_lane = record.get("active_lane")
        if not isinstance(active_lane, dict):
            errors.append(f"{paper_id}: active_lane must be an object")
        else:
            for field in ("status", "reference", "collision_rule"):
                if not _nonempty_string(active_lane.get(field)):
                    errors.append(f"{paper_id}: active_lane.{field} must be non-empty")
            marker = ACTIVE_LANE_MARKERS.get(paper_id)
            if marker and marker not in str(active_lane.get("reference", "")):
                errors.append(f"{paper_id}: active lane must reference {marker}")

        artifact = str(record.get("next_artifact", ""))
        expected_prefix = f"papers/orion-{paper_id[-2:]}-"
        if artifact and not artifact.startswith(expected_prefix):
            errors.append(f"{paper_id}: next_artifact must live under its paper directory")
        forbidden_artifact_terms = ("RESULT", "CLAIM_DISPOSITION", "AUTHORITY_DISPOSITION")
        if any(term in artifact.upper() for term in forbidden_artifact_terms):
            errors.append(
                f"{paper_id}: next artifact must be pre-outcome design/traceability, not a result"
            )

        text = _combined_text(record)
        markers = LOAD_BEARING_MARKERS.get(paper_id)
        if markers:
            _require_markers(errors, paper_id, text, markers)
        if "TOP_TIER_SUCCESSOR_EARNED" in text:
            errors.append(f"{paper_id}: ledger cannot assert an earned top-tier successor")

    guard_prs = {
        guard.get("pr")
        for guard in data.get("open_pr_collision_guards", [])
        if isinstance(guard, dict)
    }
    for required_pr in {1691, 1694, 1695, 1716, 1732, 1733, 1734}:
        if required_pr not in guard_prs:
            errors.append(f"missing open-PR collision guard #{required_pr}")

    temporal = next(
        (record for record in papers if record.get("paper_id") == "ORION-07"), {}
    )
    if temporal.get("protocol_state") != "FROZEN_DO_NOT_TOUCH":
        errors.append("ORION-07 must remain FROZEN_DO_NOT_TOUCH")
    if "TEMPORAL_PROSPECTIVE_STUDY_FROZEN" != temporal.get(
        "publication_disposition"
    ):
        errors.append("ORION-07 temporal disposition changed")
    return errors


def _default_ledger() -> Path:
    return (
        Path(__file__).resolve().parents[1]
        / "papers"
        / "publication_closure"
        / "TOP_TIER_ATOMIC_GAP_LEDGER_V2.json"
    )


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--ledger", type=Path, default=_default_ledger())
    args = parser.parse_args(argv)
    try:
        data = load_ledger(args.ledger)
    except (OSError, json.JSONDecodeError, ValueError) as exc:
        print(f"TOP_TIER_ATOMIC_GAP_LEDGER_V2: FAIL: {exc}")
        return EXIT_FAIL

    errors = validate_ledger(data)
    if errors:
        print(f"TOP_TIER_ATOMIC_GAP_LEDGER_V2: FAIL ({len(errors)} defects)")
        for error in errors:
            print(f"- {error}")
        return EXIT_FAIL
    print("TOP_TIER_ATOMIC_GAP_LEDGER_V2: PASS (25 papers; authority delta NONE)")
    return EXIT_PASS


if __name__ == "__main__":
    raise SystemExit(main())

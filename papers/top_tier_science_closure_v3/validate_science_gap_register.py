#!/usr/bin/env python3
"""Fail-closed validator for the ORION-01–25 science-gap register.

This script checks structure and preservation of load-bearing negative boundaries. It
cannot create scientific authority and deliberately does not infer that a paper is
submission-ready merely because this validator passes.
"""

from __future__ import annotations

import argparse
import json
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable


HERE = Path(__file__).resolve().parent
DEFAULT_REGISTER = HERE / "science_gap_register_v3.json"
EXPECTED_IDS = [f"ORION-{i:02d}" for i in range(1, 26)]
EXPECTED_DOCS = [
    "README.md",
    "00_CURRENT_HEAD_AND_METHOD.md",
    "00A_LATEST_HEAD_ADDENDUM.md",
    "01_ORION_01_04.md",
    "02_ORION_05_08.md",
    "03_ORION_09_12.md",
    "04_ORION_13_16.md",
    "05_ORION_17_20.md",
    "06_ORION_21_23.md",
    "07_ORION_24_25.md",
    "08_LOCAL_REPAIRS_01_12.md",
    "09_LOCAL_REPAIRS_13_24.md",
]
REQUIRED_PAPER_FIELDS = {
    "id",
    "title",
    "priority",
    "current_claim",
    "binding_boundary",
    "local_repair",
    "decisive_gate",
    "positive_terminal",
    "adverse_terminal",
    "externality",
}
BOUNDARY_TOKENS = {
    # Widened 2026-08-29. ORION-05 and ORION-09 were flagged BOUNDARY_NOT_ADVERSE
    # while stating genuine limits -- "No production compiler ... is established"
    # and "true but vacuous ... universal transfer is stopped". Neither contains a
    # literal "not". These additions recognise the same meaning in other words; no
    # token was removed and the requirement that a boundary BE adverse is unchanged.
    # Checked against all 25 registered boundaries: 23 already passed, exactly
    # ORION-05 and ORION-09 gain, and no non-adverse boundary is admitted.
    "no ",
    "none",
    "vacuous",
    "stopped",
    "refuted",
    "halted",
    "blocked",
    "withheld",
    "not",
    "remain",
    "null",
    "failed",
    "open",
    "unproved",
    "unsupported",
    "cannot_check",
    "retract",
    "broken",
    "retired",
    "absent",
    "unexecuted",
    "degenerate",
    "only",
}
ALLOWED_PRIORITIES = {"P0", "P1", "P2", "P3"}
ALLOWED_EXTERNALITIES = {
    "new_external_data",
    "external_system",
    "independent_implementation",
    "independent_evaluator",
    "institutional_authority",
}


@dataclass(frozen=True)
class Finding:
    code: str
    message: str

    def as_dict(self) -> dict[str, str]:
        return {"code": self.code, "message": self.message}


def _normalize(value: Any) -> str:
    return " ".join(str(value).lower().replace("–", "-").split())


def _contains_all(text: str, needles: Iterable[str]) -> bool:
    normalized = _normalize(text)
    return all(_normalize(needle) in normalized for needle in needles)


def _record_text(record: dict[str, Any]) -> str:
    return "\n".join(
        str(record.get(key, ""))
        for key in (
            "current_claim",
            "binding_boundary",
            "local_repair",
            "decisive_gate",
            "positive_terminal",
            "adverse_terminal",
        )
    )


def validate(register_path: Path, docs_root: Path) -> list[Finding]:
    findings: list[Finding] = []
    try:
        payload = json.loads(register_path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        return [Finding("REGISTER_MISSING", f"Missing register: {register_path}")]
    except json.JSONDecodeError as exc:
        return [Finding("REGISTER_INVALID_JSON", f"{register_path}: {exc}")]

    if payload.get("schema") != "orion.top_tier_science_gap_register.v3":
        findings.append(Finding("SCHEMA", "Unexpected or missing register schema."))
    if payload.get("science_authority_delta") != "NONE":
        findings.append(
            Finding(
                "AUTHORITY_LAUNDERING",
                "Documentation-only register must keep science_authority_delta=NONE.",
            )
        )
    if payload.get("paper_count") != 25:
        findings.append(Finding("PAPER_COUNT", "paper_count must equal 25."))

    rules = payload.get("global_rules")
    if not isinstance(rules, list) or len(rules) < 8:
        findings.append(Finding("GLOBAL_RULES", "At least eight global guardrails are required."))
    else:
        joined_rules = _normalize("\n".join(map(str, rules)))
        for token in (
            "null",
            "retracted",
            "cannot_check",
            "external scientific authority",
            "not_computed_by_protocol",
            "protected task-3",
        ):
            if token not in joined_rules:
                findings.append(Finding("GLOBAL_RULE_GAP", f"Missing global guard token: {token}"))

    papers = payload.get("papers")
    if not isinstance(papers, list):
        return findings + [Finding("PAPERS_TYPE", "papers must be a list.")]

    ids = [record.get("id") for record in papers if isinstance(record, dict)]
    if ids != EXPECTED_IDS:
        findings.append(
            Finding(
                "PAPER_IDS",
                f"Paper IDs must be exactly {EXPECTED_IDS}; observed {ids}.",
            )
        )

    positive_terminals: set[str] = set()
    adverse_terminals: set[str] = set()
    records_by_id: dict[str, dict[str, Any]] = {}

    for index, record in enumerate(papers):
        if not isinstance(record, dict):
            findings.append(Finding("PAPER_TYPE", f"papers[{index}] is not an object."))
            continue
        paper_id = str(record.get("id", f"index-{index}"))
        records_by_id[paper_id] = record

        missing = REQUIRED_PAPER_FIELDS - record.keys()
        if missing:
            findings.append(Finding("FIELD_MISSING", f"{paper_id}: missing {sorted(missing)}"))

        for field in REQUIRED_PAPER_FIELDS - {"externality"}:
            value = record.get(field)
            if not isinstance(value, str) or not value.strip():
                findings.append(Finding("FIELD_EMPTY", f"{paper_id}: {field} must be non-empty text."))

        priority = record.get("priority")
        if priority not in ALLOWED_PRIORITIES:
            findings.append(Finding("PRIORITY", f"{paper_id}: invalid priority {priority!r}."))

        externality = record.get("externality")
        if not isinstance(externality, list) or not externality:
            findings.append(Finding("EXTERNALITY_EMPTY", f"{paper_id}: externality must be non-empty."))
        else:
            unknown = set(map(str, externality)) - ALLOWED_EXTERNALITIES
            if unknown:
                findings.append(Finding("EXTERNALITY_UNKNOWN", f"{paper_id}: unknown {sorted(unknown)}"))

        boundary = _normalize(record.get("binding_boundary", ""))
        if not any(token in boundary for token in BOUNDARY_TOKENS):
            findings.append(
                Finding(
                    "BOUNDARY_NOT_ADVERSE",
                    f"{paper_id}: binding_boundary lacks an explicit limiting/adverse token.",
                )
            )

        positive = str(record.get("positive_terminal", ""))
        adverse = str(record.get("adverse_terminal", ""))
        if positive == adverse:
            findings.append(Finding("TERMINAL_COLLISION", f"{paper_id}: terminals are identical."))
        if positive in positive_terminals:
            findings.append(Finding("TERMINAL_DUPLICATE", f"Duplicate positive terminal: {positive}"))
        if adverse in adverse_terminals:
            findings.append(Finding("TERMINAL_DUPLICATE", f"Duplicate adverse terminal: {adverse}"))
        positive_terminals.add(positive)
        adverse_terminals.add(adverse)

    # Load-bearing paper-specific guards. These are deliberately literal enough to
    # catch cosmetic rewrites that erase a scientifically material boundary.
    guards: dict[str, tuple[str, ...]] = {
        "ORION-02": ("p=0.092", "14 versus 20", "cannot_check"),
        "ORION-08": ("undetermined", "holm", "does not upgrade"),
        "ORION-11": ("retracted", "2026-08-28", "2,880"),
        "ORION-12": ("failed", "ndcg@10", "asymmetric action support"),
        "ORION-13": ("always-merge", "polarity", "not_computed_by_protocol"),
        "ORION-15": ("seven", "cannot_check", "may not be imputed"),
        "ORION-18": ("169", "not 169 heterogeneous", "external truth"),
        "ORION-19": ("p=0.125", "five", "retired"),
        "ORION-20": ("prospective_not_executed",),
        "ORION-21": ("0.8424", "not all moderate capability"),
        "ORION-22": ("no p12c result", "unexecuted"),
        "ORION-24": ("p=0.125", "same-programme"),
        "ORION-25": ("signatures do not prove", "key compromise"),
    }
    for paper_id, needles in guards.items():
        record = records_by_id.get(paper_id)
        if record is None:
            continue
        text = _record_text(record)
        if not _contains_all(text, needles):
            findings.append(
                Finding(
                    "LOAD_BEARING_GUARD",
                    f"{paper_id}: required guard terms not all present: {needles}",
                )
            )

    for name in EXPECTED_DOCS:
        if not (docs_root / name).is_file():
            findings.append(Finding("DOCUMENT_MISSING", f"Missing closure document: {name}"))

    return findings


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--register", type=Path, default=DEFAULT_REGISTER)
    parser.add_argument("--docs-root", type=Path, default=HERE)
    parser.add_argument("--json", action="store_true", help="Emit a JSON result object.")
    args = parser.parse_args()

    findings = validate(args.register.resolve(), args.docs_root.resolve())
    result = {
        "status": "GREEN" if not findings else "RED",
        "paper_count_expected": 25,
        "finding_count": len(findings),
        "findings": [finding.as_dict() for finding in findings],
        "science_authority_delta": "NONE",
    }
    if args.json:
        print(json.dumps(result, indent=2, sort_keys=True))
    elif findings:
        print(f"SCIENCE GAP REGISTER: RED ({len(findings)} findings)")
        for finding in findings:
            print(f"- {finding.code}: {finding.message}")
    else:
        print("SCIENCE GAP REGISTER: GREEN papers=25 science_authority_delta=NONE")
    return 1 if findings else 0


if __name__ == "__main__":
    sys.exit(main())

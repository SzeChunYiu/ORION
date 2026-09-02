#!/usr/bin/env python3
"""Fail-closed structural checker for the ORION 01-25 science-closure gate."""

from __future__ import annotations

import re
import sys
from pathlib import Path

BASELINE = "703b87db22dce3981f13b407b56f4a656310632f"
EXPECTED_IDS = {f"{i:02d}" for i in range(1, 26)}
HARD_RETRACTIONS = {"01", "02", "04", "05"}
REAL_WORLD_GATED = {"03", "21"}
REQUIRED_FIELDS = {
    "BAND",
    "CURRENT_TOP_TIER_READY",
    "BASELINE_PROMOTION_ALLOWED",
    "IDENTITY",
    "HARD_RETRACTION",
    "CURRENT",
    "GAPS",
    "NEXT_EVIDENCE",
    "PRIMARY_ENDPOINTS",
    "EXTERNAL_STATUS",
    "EXTERNAL_REPLICATION",
    "CALIBRATION_UNCERTAINTY",
    "CONTROLS",
    "SUCCESS",
    "KILL",
    "MANUSCRIPT_UNLOCK",
    "FALLBACK",
}
SECTION_RE = re.compile(r"^## ORION-(\d{2}) — (.+)$", re.MULTILINE)
FIELD_RE = re.compile(r"^- `([A-Z_]+)`: (.+)$", re.MULTILINE)
FORBIDDEN_CURRENT = (
    "top-tier ready",
    "submission-ready",
    "externally replicated",
    "cleared for submission",
)


def _items(value: str) -> list[str]:
    return [item.strip() for item in value.split(" || ") if item.strip()]


def load_sections(root: Path) -> tuple[dict[str, dict[str, str]], list[str]]:
    errors: list[str] = []
    sections: dict[str, dict[str, str]] = {}
    for path in sorted(root.glob("ORION_*.md")):
        text = path.read_text(encoding="utf-8")
        matches = list(SECTION_RE.finditer(text))
        for index, match in enumerate(matches):
            paper_id = match.group(1)
            start = match.end()
            end = matches[index + 1].start() if index + 1 < len(matches) else len(text)
            fields = dict(FIELD_RE.findall(text[start:end]))
            if paper_id in sections:
                errors.append(f"duplicate ORION-{paper_id}")
            sections[paper_id] = fields
    return sections, errors


def validate(root: Path) -> list[str]:
    errors: list[str] = []
    readme_path = root / "README.md"
    if not readme_path.exists():
        return ["missing README.md"]
    readme = readme_path.read_text(encoding="utf-8")
    if f"`BASELINE_COMMIT`: {BASELINE}" not in readme:
        errors.append("README baseline commit mismatch")
    if "`CURRENT_TOP_TIER_READY_COUNT`: 0" not in readme:
        errors.append("portfolio ready count must remain zero")
    for role in range(1, 8):
        if f"`E{role}_" not in readme:
            errors.append(f"missing expert role E{role}")
    for line in readme.splitlines():
        if "`PR #" in line and "`counts_as_evidence=false`" not in line:
            errors.append(f"open PR lacks zero-credit marker: {line}")

    sections, load_errors = load_sections(root)
    errors.extend(load_errors)
    ids = set(sections)
    if ids != EXPECTED_IDS:
        errors.append(
            f"paper coverage mismatch missing={sorted(EXPECTED_IDS - ids)} "
            f"extra={sorted(ids - EXPECTED_IDS)}"
        )

    for paper_id, fields in sorted(sections.items()):
        label = f"ORION-{paper_id}"
        missing = REQUIRED_FIELDS - set(fields)
        if missing:
            errors.append(f"{label} missing fields {sorted(missing)}")
            continue
        if fields["BAND"] not in {"A", "B", "F"}:
            errors.append(f"{label} invalid BAND")
        if fields["CURRENT_TOP_TIER_READY"] != "false":
            errors.append(f"{label} CURRENT_TOP_TIER_READY must be false")
        if fields["EXTERNAL_STATUS"] != "required_not_yet_credited":
            errors.append(f"{label} external evidence must remain uncredited")
        if len(_items(fields["GAPS"])) < 2:
            errors.append(f"{label} needs at least two atomic gaps")
        if len(_items(fields["NEXT_EVIDENCE"])) < 2:
            errors.append(f"{label} needs at least two evidence actions")
        if len(_items(fields["PRIMARY_ENDPOINTS"])) < 3:
            errors.append(f"{label} needs at least three primary endpoints")
        if len(_items(fields["SUCCESS"])) < 2:
            errors.append(f"{label} needs at least two success gates")
        if len(_items(fields["KILL"])) < 2:
            errors.append(f"{label} needs at least two kill gates")
        if not fields["MANUSCRIPT_UNLOCK"].startswith("Only after"):
            errors.append(f"{label} manuscript unlock must begin Only after")
        external = fields["EXTERNAL_REPLICATION"].lower()
        if "external" not in external and "independent" not in external:
            errors.append(f"{label} lacks an external independence boundary")
        stats = fields["CALIBRATION_UNCERTAINTY"].lower()
        if not any(token in stats for token in ("calibrat", "uncertaint", "coverage", "confidence", "interval")):
            errors.append(f"{label} lacks calibration/uncertainty/coverage")
        current = fields["CURRENT"].lower()
        for phrase in FORBIDDEN_CURRENT:
            if phrase in current:
                errors.append(f"{label} current state contains forbidden phrase {phrase}")

        hard = fields["HARD_RETRACTION"] == "true"
        if hard != (paper_id in HARD_RETRACTIONS):
            errors.append(f"{label} hard-retraction set mismatch")
        if paper_id in HARD_RETRACTIONS:
            if fields["IDENTITY"] != "successor_only":
                errors.append(f"{label} must remain successor_only")
            if fields["BASELINE_PROMOTION_ALLOWED"] != "false":
                errors.append(f"{label} hard retraction cannot promote")
            unlock = fields["MANUSCRIPT_UNLOCK"].lower()
            if "retract" not in unlock or "successor" not in unlock:
                errors.append(f"{label} unlock must preserve retraction and successor identity")
        if fields["BAND"] == "F" and fields["BASELINE_PROMOTION_ALLOWED"] != "false":
            errors.append(f"{label} band F cannot promote")
        if paper_id in REAL_WORLD_GATED:
            gate = " ".join((fields["SUCCESS"], fields["MANUSCRIPT_UNLOCK"])).lower()
            if "real" not in gate and "physical" not in gate:
                errors.append(f"{label} must require real or physical evidence")
            if fields["BASELINE_PROMOTION_ALLOWED"] != "false":
                errors.append(f"{label} real-world gate cannot promote on baseline")
    return errors


def main() -> int:
    root = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(
        "papers/reviewer_gate/orion_top_tier_closure_v1"
    )
    errors = validate(root)
    if errors:
        for error in errors:
            print(f"ERROR: {error}")
        print(f"ORION_TOP_TIER_CLOSURE_V1 FAIL errors={len(errors)}")
        return 1
    print("ORION_TOP_TIER_CLOSURE_V1 GREEN papers=25 ready=0")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

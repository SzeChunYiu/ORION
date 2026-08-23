#!/usr/bin/env python3
"""Validate target-package routing without granting submission authority."""

from __future__ import annotations

import json
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "papers/Q_QG_TARGET_PACKAGE_MANIFESTS_V1.json"
EXPECTED = {
    "Q1_Quantum": "papers/Q-paper-01-tare-expressivity/MANUSCRIPT_V3.md",
    "Q2_AIJ": "papers/Q-paper-02-recursive-recovery/MANUSCRIPT_V3.md",
    "Q4_TMLR": "papers/Q-paper-04-typed-state/MANUSCRIPT_V3.md",
    "QG1_PRX": "papers/QG-paper-01-compilation-regime-geometry/MANUSCRIPT_V3.md",
    "QG2_Quantum": "papers/QG-paper-02-certified-static-forecasting/MANUSCRIPT_V3.md",
}


def main() -> int:
    data = json.loads(MANIFEST.read_text(encoding="utf-8"))
    errors: list[str] = []
    packages = data.get("packages", {})
    if set(packages) != set(EXPECTED):
        errors.append(f"PACKAGE_SET_MISMATCH:{sorted(packages)}")

    for package_id, expected_master in EXPECTED.items():
        entry = packages.get(package_id, {})
        if entry.get("scientific_master") != expected_master:
            errors.append(
                f"MASTER_MISMATCH:{package_id}:{entry.get('scientific_master')}!={expected_master}"
            )
        for field in ("scientific_master", "citation_generator", "source_preparer", "template", "workflow"):
            rel = entry.get(field)
            if not rel:
                errors.append(f"MISSING_FIELD:{package_id}:{field}")
                continue
            if not (ROOT / rel).is_file():
                errors.append(f"MISSING_PATH:{package_id}:{field}:{rel}")
        if not entry.get("artifact_name"):
            errors.append(f"MISSING_ARTIFACT_NAME:{package_id}")
        if not entry.get("expected_outputs"):
            errors.append(f"NO_EXPECTED_OUTPUTS:{package_id}")
        if not entry.get("author_blockers"):
            errors.append(f"NO_AUTHOR_BLOCKERS:{package_id}")
        state = entry.get("technical_state", "")
        if "SUBMISSION_PACKAGE_READY" in state:
            errors.append(f"UNAUTHORIZED_READY_TERMINAL:{package_id}:{state}")

    q3 = data.get("Q3", {})
    if q3.get("technical_state") != "NO_TARGET_PACKAGE_BY_DESIGN":
        errors.append("Q3_PACKAGE_BLOCK_NOT_ENFORCED")

    # The scientific masters themselves must not contain target-specific author placeholders;
    # those belong only to generated wrappers.
    for package_id, rel in EXPECTED.items():
        body = (ROOT / rel).read_text(encoding="utf-8")
        if "AUTHOR METADATA REQUIRED BEFORE SUBMISSION" in body:
            errors.append(f"AUTHOR_PLACEHOLDER_LEAKED_INTO_SCIENTIFIC_MASTER:{package_id}")

    if errors:
        print("Q_QG_TARGET_PACKAGE_CHECK=FAIL")
        for err in errors:
            print(f"- {err}")
        return 1

    print("Q_QG_TARGET_PACKAGE_CHECK=PASS")
    print(f"TARGET_PACKAGES={len(EXPECTED)}")
    print("Q3_TARGET_PACKAGE=BLOCKED_BY_DESIGN")
    print("SUBMISSION_AUTHORITY=NOT_GRANTED_BY_PACKAGE_MANIFEST")
    return 0


if __name__ == "__main__":
    sys.exit(main())

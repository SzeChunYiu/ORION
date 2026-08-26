#!/usr/bin/env python3
"""Validate Q/QG target-package manifest V2 and standalone figure authority."""

from __future__ import annotations

import json
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "papers/Q_QG_TARGET_PACKAGE_MANIFESTS_V2.json"
FIG_AUTH = ROOT / "papers/Q_QG_FIGURE_AUTHORITY_V2.md"
EXPECTED = {
    "Q1_Quantum": "papers/archive/2026-08-pre-unification/Q-paper-01-tare-expressivity/MANUSCRIPT_V3.md",
    "Q2_AIJ": "papers/orion-06-recursive-recovery/MANUSCRIPT_V3.md",
    "Q3_TMLR": "papers/orion-07-dual-instrument/MANUSCRIPT_V3.md",
    "Q4_TMLR": "papers/orion-08-typed-state/MANUSCRIPT_V3.md",
    "QG1_PRX": "papers/orion-09-compilation-regime-geometry/MANUSCRIPT_V3.md",
    "QG2_Quantum": "papers/orion-10-certified-static-forecasting/MANUSCRIPT_V3.md",
}


def main() -> int:
    data = json.loads(MANIFEST.read_text(encoding="utf-8"))
    errors: list[str] = []
    shared = data.get("shared", {})
    for key in ("publication_integrity_workflow", "reference_workflow", "science_manifest", "figure_authority", "figure_workflow", "visual_audit", "author_input", "reference_verification"):
        rel = shared.get(key)
        if not rel or not (ROOT / rel).is_file():
            errors.append(f"MISSING_SHARED_PATH:{key}:{rel}")
    if shared.get("figure_workflow") != ".github/workflows/q-qg-figures-v2.yml":
        errors.append("FIGURE_V2_NOT_AUTHORITATIVE")

    fig_auth = FIG_AUTH.read_text(encoding="utf-8") if FIG_AUTH.is_file() else ""
    packages = data.get("packages", {})
    if set(packages) != set(EXPECTED):
        errors.append(f"PACKAGE_SET_MISMATCH:{sorted(packages)}")

    all_stems: set[str] = set()
    for package_id, expected_master in EXPECTED.items():
        entry = packages.get(package_id, {})
        if entry.get("scientific_master") != expected_master:
            errors.append(f"MASTER_MISMATCH:{package_id}")
        for field in ("scientific_master", "wrapper_workflow"):
            rel = entry.get(field)
            if not rel or not (ROOT / rel).is_file():
                errors.append(f"MISSING_PACKAGE_PATH:{package_id}:{field}:{rel}")
        if not entry.get("artifact"):
            errors.append(f"MISSING_ARTIFACT:{package_id}")
        tech = entry.get("technical_terminal", "")
        submit = entry.get("submission_terminal", "")
        if "PENDING_" not in tech:
            errors.append(f"UNEXPECTED_TECHNICAL_TERMINAL:{package_id}:{tech}")
        if "BLOCKED_" not in submit:
            errors.append(f"UNAUTHORIZED_SUBMISSION_TERMINAL:{package_id}:{submit}")
        stems = entry.get("required_figure_stems", [])
        if package_id == "Q3_TMLR":
            if stems:
                errors.append(f"Q3_UNEXPECTED_MANDATORY_FIGURES:{stems}")
            if "three-unit prospective disposition table" not in entry.get("primary_result_display", ""):
                errors.append("Q3_PRIMARY_TABLE_NOT_BOUND")
        elif not stems:
            errors.append(f"NO_REQUIRED_FIGURES:{package_id}")
        for stem in stems:
            if stem in all_stems:
                errors.append(f"DUPLICATE_REQUIRED_FIGURE_STEM:{stem}")
            all_stems.add(stem)
            if stem not in fig_auth:
                errors.append(f"FIGURE_STEM_NOT_IN_V2_AUTHORITY:{package_id}:{stem}")

    # Q3 intentionally adds no required plot, so the existing five-paper figure authority
    # remains exactly 12 standalone stems.
    if len(all_stems) != 12:
        errors.append(f"FIGURE_STEM_COUNT_DRIFT:{len(all_stems)}!=12")

    q3 = packages.get("Q3_TMLR", {})
    if "Q3_PROSPECTIVE_CASE_SERIES_COMPLETE" not in q3.get("scientific_terminal", ""):
        errors.append("Q3_COMPLETE_SCIENTIFIC_TERMINAL_NOT_VISIBLE")
    if q3.get("official_style_commit") != "7bf90efe3a0debbba703c05c43f3ff7e4d4a2992":
        errors.append("Q3_TMLR_STYLE_COMMIT_NOT_PINNED")

    # Superseded package/figure lanes must be visibly non-authoritative.
    if "no publication authority" not in fig_auth.lower():
        errors.append("V1_FIGURE_SUPERSESSION_NOT_EXPLICIT")
    if packages.get("QG1_PRX", {}).get("superseded_workflow") != ".github/workflows/qg1-prx-preflight.yml":
        errors.append("QG1_OLD_PRX_WORKFLOW_NOT_MARKED_SUPERSEDED")

    if errors:
        print("Q_QG_TARGET_PACKAGE_V2_CHECK=FAIL")
        for err in errors:
            print(f"- {err}")
        return 1

    print("Q_QG_TARGET_PACKAGE_V2_CHECK=PASS")
    print(f"TARGET_PACKAGES={len(EXPECTED)}")
    print(f"REQUIRED_STANDALONE_FIGURES={len(all_stems)}")
    print("Q3_TARGET_PACKAGE=TMLR__TABLE_PRIMARY__NO_MANDATORY_FIGURE")
    print("SUBMISSION_AUTHORITY=NOT_GRANTED_BY_PACKAGE_MANIFEST")
    return 0


if __name__ == "__main__":
    sys.exit(main())

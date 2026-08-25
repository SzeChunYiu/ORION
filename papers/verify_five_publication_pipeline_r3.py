#!/usr/bin/env python3
"""Verify the five-paper R3 publication handoff without external services."""

from __future__ import annotations

import json
import re
import shutil
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
PAPERS = ROOT / "papers"

MANUSCRIPTS = {
    "A": PAPERS / "theory-A-multitag-constraint-rank" / "MANUSCRIPT_V3_PIPELINE.md",
    "B": PAPERS / "theory-B-certificate-complexity" / "MANUSCRIPT_V3_PIPELINE.md",
    "C": PAPERS / "theory-C-low-order-information" / "MANUSCRIPT_V3_PIPELINE.md",
    "D": PAPERS / "theory-D-falsification-authority" / "MANUSCRIPT_V3_PIPELINE.md",
    "N": PAPERS / "nonquantum-c5cubed-davenport" / "MANUSCRIPT_V3_PIPELINE.md",
}

CONTROLS = {
    key: path.with_name("PIPELINE_CONTROL_V3.md") for key, path in MANUSCRIPTS.items()
}

FORBIDDEN_SURFACE = re.compile(
    r"unified[ -]calculus|universal[ -]calculus|authority[ -]calculus|"
    r"workflow cut|scientific cut|publication decision|hardened manuscript|"
    r"pull request|PR #[0-9]+|/workspace/|development/|\bORION\b|"
    r"\bR6[A-Z0-9_-]*\b|\bQG[A-Z0-9_-]*\b|orion\.invalid|registered product",
    re.IGNORECASE,
)

REQUIRED = {
    "A": ["zero-sum deletion normal form", "deletion closure", "no intrinsic"],
    "B": ["exact abstract certificate complexity", "dependent-triple", "Theta(n^{4t})"],
    "C": ["four-index decision certificate", "sqrt{6/5}", "proper-marginal kernel"],
    "D": ["least-fixed-point semantics", "proof-tree equivalence", "Executable semantics"],
    "N": ["5k+10", "rank-forcing phase", "remains open"],
}


def run_json(command):
    completed = subprocess.run(
        command,
        cwd=ROOT,
        check=True,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    return json.loads(completed.stdout)


def main() -> int:
    checks = {}
    details = {}

    checks["all_manuscripts_present"] = all(path.is_file() for path in MANUSCRIPTS.values())
    checks["all_controls_present"] = all(path.is_file() for path in CONTROLS.values())

    surface_hits = {}
    required_missing = {}
    word_counts = {}
    math_balance = {}
    for key, path in MANUSCRIPTS.items():
        text = path.read_text(encoding="utf-8")
        hits = sorted(set(match.group(0) for match in FORBIDDEN_SURFACE.finditer(text)))
        if hits:
            surface_hits[key] = hits
        missing = [token for token in REQUIRED[key] if token.lower() not in text.lower()]
        if missing:
            required_missing[key] = missing
        word_counts[key] = len(text.split())
        math_balance[key] = text.count(r"\(") == text.count(r"\)")

    checks["submission_surface_clean"] = not surface_hits
    checks["required_claim_surfaces_present"] = not required_missing
    checks["inline_math_balanced"] = all(math_balance.values())
    details["surface_hits"] = surface_hits
    details["required_missing"] = required_missing
    details["word_counts"] = word_counts

    control_text = "\n".join(path.read_text(encoding="utf-8") for path in CONTROLS.values())
    checks["closure_frozen_in_all_controls"] = (
        control_text.count("FORMAL_COMPONENTS_ONLY_NO_UNIFIED_CALCULUS") == 5
    )
    checks["paper_d_retired_framing_absent"] = not re.search(
        r"\bcalculus\b", MANUSCRIPTS["D"].read_text(encoding="utf-8"), re.IGNORECASE
    )
    paper_a = MANUSCRIPTS["A"].read_text(encoding="utf-8")
    checks["paper_a_binary_alphabet_rank_equality"] = (
        r"\operatorname{zsf}(H; A)=d" in paper_a
        and "equality is automatic" in paper_a
        and "strict alphabet-versus-realized-rank refinement is claimed" not in paper_a
    )

    r2 = run_json([sys.executable, str(PAPERS / "verify_five_theory_hardening_r2.py")])
    checks["r2_scientific_authority_passes"] = r2.get("all_checks") is True

    d_test = subprocess.run(
        [
            sys.executable,
            "-m",
            "unittest",
            "discover",
            "-s",
            str(PAPERS / "theory-D-falsification-authority"),
            "-p",
            "test_*.py",
        ],
        cwd=ROOT,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    checks["paper_d_unit_tests_pass"] = d_test.returncode == 0
    details["paper_d_test_summary"] = (d_test.stderr or d_test.stdout).strip().splitlines()[-1]

    example_results = {}
    evaluator = PAPERS / "theory-D-falsification-authority" / "evidence_license_evaluator.py"
    for path in sorted((evaluator.parent / "examples").glob("*.json")):
        result = run_json([sys.executable, str(evaluator), str(path)])
        example_results[path.name] = result["final_labels"]
    checks["paper_d_examples_evaluate"] = len(example_results) == 3
    checks["bounded_frontier_does_not_gain_theorem"] = (
        "THEOREM" not in example_results["bounded_frontier.json"]["exact_D4"]
    )
    checks["post_outcome_repair_not_prospective"] = (
        "PROSPECTIVE"
        not in example_results["forecast_falsification.json"]["repaired_forecast"]
    )
    details["paper_d_example_labels"] = example_results

    if shutil.which("pandoc"):
        pandoc_results = {}
        for key, path in MANUSCRIPTS.items():
            completed = subprocess.run(
                [
                    "pandoc",
                    "-f",
                    "markdown+tex_math_single_backslash",
                    "-t",
                    "html",
                    "--mathjax",
                    str(path),
                ],
                cwd=ROOT,
                text=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
            )
            pandoc_results[key] = completed.returncode == 0 and 'class="math' in completed.stdout
        checks["pandoc_parses_all_manuscripts"] = all(pandoc_results.values())
        details["pandoc"] = pandoc_results
    else:
        details["pandoc"] = "not installed; optional portable check skipped"

    handoff = (PAPERS / "FIVE_PAPER_ATOMIC_VERIFICATION_V6_2026-08-25.md").read_text(
        encoding="utf-8"
    )
    review = (PAPERS / "FIVE_PAPER_REVIEW_SYNTHESIS_R3_2026-08-25.md").read_text(
        encoding="utf-8"
    )
    checks["five_terminal_states_recorded"] = (
        handoff.count("| `BLOCKED`") >= 5
        and "`BLOCKED_NO_PUBLIC_POSTING`" in handoff
    )
    checks["editor_synthesis_recorded"] = "Editor synthesis" in review

    output = {
        "schema": "orion.five-paper-publication-pipeline-r3-v6-gate.v1",
        "all_checks": all(checks.values()),
        "checks": checks,
        "details": details,
    }
    print(json.dumps(output, indent=2, sort_keys=True))
    return 0 if output["all_checks"] else 1


if __name__ == "__main__":
    raise SystemExit(main())

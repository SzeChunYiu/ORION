#!/usr/bin/env python3
"""Run destructive, temporary mutations against the Round-1 verifier."""

from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Callable


HERE = Path(__file__).resolve().parent
ORION03_DIR = "papers/orion-03-typed-merge-falsification"
ROUND_REL = f"{ORION03_DIR}/evidence/round1-cedar-multipolicy"
SAFE_REL = (
    f"{ORION03_DIR}/evidence/convergence-v1/"
    "AGENTGATEWAY_ORIGIN_WITNESS_SAFE_MERGE_R11_RESULTS_SUMMARY.json"
)
REPO = HERE.parents[3]


def canonical_write(path: Path, value: object) -> None:
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n")


def copy_case(destination: Path) -> Path:
    round_destination = destination / ROUND_REL
    round_destination.parent.mkdir(parents=True, exist_ok=True)
    shutil.copytree(
        HERE,
        round_destination,
        ignore=shutil.ignore_patterns(".lake", "target", "__pycache__"),
    )
    safe_destination = destination / SAFE_REL
    safe_destination.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(REPO / SAFE_REL, safe_destination)
    return round_destination


def invoke(round_directory: Path) -> subprocess.CompletedProcess[str]:
    env = os.environ.copy()
    env["ORION03_GIT_REPOSITORY"] = str(REPO)
    return subprocess.run(
        [sys.executable, str(round_directory / "verify_round1.py"), "--check-final"],
        check=False,
        capture_output=True,
        text=True,
        env=env,
    )


def mutate_source(round_directory: Path) -> None:
    path = (
        round_directory
        / "third_party/cedar-integration-tests/tests/multi/policies_1.cedar"
    )
    path.write_text(path.read_text() + "\n// hostile byte\n")


def mutate_python_receipt(round_directory: Path) -> None:
    path = round_directory / "PYTHON_ADJUDICATION_V1.json"
    value = json.loads(path.read_text())
    value["source"]["requests"] = 16
    canonical_write(path, value)


def mutate_rust_control(round_directory: Path) -> None:
    path = round_directory / "RUST_ADJUDICATION_V1.json"
    value = json.loads(path.read_text())
    value["hostile_and_safe_controls"]["cases"][0]["status"] = "FAIL"
    canonical_write(path, value)


def mutate_lean_source(round_directory: Path) -> None:
    path = round_directory / "lean/Orion03Round1.lean"
    path.write_text(path.read_text() + "\n-- hostile byte\n")


def mutate_lean_execution_commit(round_directory: Path) -> None:
    path = round_directory / "LEAN_ADJUDICATION_V1.json"
    value = json.loads(path.read_text())
    value["execution_commit"] = "0" * 40
    canonical_write(path, value)


def mutate_terminal(round_directory: Path) -> None:
    path = round_directory / "ROUND1_RESULTS_V1.json"
    value = json.loads(path.read_text())
    value["terminal"] = "D_R11_REAL_AUTHORITY_PROMOTION_ERROR_PREVENTED"
    canonical_write(path, value)


def mutate_safe_control(round_directory: Path) -> None:
    safe = round_directory.parent / "convergence-v1" / Path(SAFE_REL).name
    value = json.loads(safe.read_text())
    value["terminal"] = "HOSTILE_FALSE_VULNERABILITY_LABEL"
    canonical_write(safe, value)


MUTATIONS: list[tuple[str, Callable[[Path], None]]] = [
    ("vendored_source_byte_tamper", mutate_source),
    ("python_receipt_denominator_tamper", mutate_python_receipt),
    ("rust_control_status_tamper", mutate_rust_control),
    ("lean_source_binding_tamper", mutate_lean_source),
    ("lean_execution_commit_tamper", mutate_lean_execution_commit),
    ("positive_terminal_promotion_tamper", mutate_terminal),
    ("safe_control_vulnerability_relabel_tamper", mutate_safe_control),
]


def run_review() -> dict[str, object]:
    rows: list[dict[str, str]] = []
    with tempfile.TemporaryDirectory(prefix="orion03-hostile-") as temp:
        temp_root = Path(temp)
        baseline = copy_case(temp_root / "baseline")
        baseline_run = invoke(baseline)
        if baseline_run.returncode != 0:
            raise SystemExit(
                "HOSTILE_REVIEW_SETUP_FAIL: clean baseline did not verify\n"
                + baseline_run.stdout
                + baseline_run.stderr
            )

        for index, (name, mutation) in enumerate(MUTATIONS):
            round_directory = copy_case(temp_root / f"case-{index}")
            mutation(round_directory)
            run = invoke(round_directory)
            combined = run.stdout + run.stderr
            if run.returncode == 0 or "ORION03_R1_VERIFY_FAIL" not in combined:
                raise SystemExit(f"HOSTILE_REVIEW_FAIL: mutation accepted: {name}")
            rows.append(
                {
                    "mutation": name,
                    "status": "REJECTED_AS_REQUIRED",
                }
            )

    return {
        "schema": "ORION.ORION03.CedarMultiPolicy.HostileReview.v1",
        "terminal": "ORION03_R1_HOSTILE_MUTATION_REVIEW_PASS",
        "baseline": "PASS",
        "mutations_rejected": len(rows),
        "mutations_total": len(MUTATIONS),
        "mutations": rows,
        "authority": {
            "scientific_result": False,
            "external_independence": False,
            "novelty": False,
            "journal_authority": False,
        },
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--emit", type=Path, required=True)
    args = parser.parse_args()
    result = run_review()
    canonical_write(args.emit, result)
    print(
        "ORION03_R1_HOSTILE_MUTATION_REVIEW_PASS "
        f"rejected={result['mutations_rejected']}/{result['mutations_total']}"
    )


if __name__ == "__main__":
    main()

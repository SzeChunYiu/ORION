#!/usr/bin/env python3
"""Build and verify the additive ORION-02 R24 closeout receipt."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import subprocess
from typing import Any, Sequence


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
RECEIPT = HERE / "ORION02_R24_CUSTODY_3550275.json"
FAILED = HERE / "failed-executions/3550275"
EXECUTION_COMMIT = "e4d12133a662b53135264945451c19f6adf8a04d"
AMENDMENT_COMMIT = "0c42ea7b7698a6e22bb4184b8f75869566f4af4e"
RESULT_SHA256 = "b21f54b9aad939b60e9600fc11ba856e8942bc81c73f84b3e28161667a20df54"
PARENT_SHA256 = "cf1a0db71ab135278b64c02633f07d05a23604a121f0b62743f4e59c6358fc77"
TERMINAL_SHA256 = "794ac7b91538559a54cba1eb1df48d468916d87e1e81272a160824ddc340dda8"
TERMINAL = "C_R24_ARM_CONDITIONAL_CERTIFICATE_INVALID"

PROTECTED_SCIENCE_PATHS = (
    "papers/orion-02-fiberguard-finite-fibre/rounds/"
    "r24-arm-conditional-fibres-revival/FIBERGUARD_PMLB_ARM_CONDITIONAL_R24_PROTOCOL.md",
    "papers/orion-02-fiberguard-finite-fibre/rounds/"
    "r24-arm-conditional-fibres-revival/fiberguard_pmlb_arm_conditional_r24.py",
    "papers/orion-02-fiberguard-finite-fibre/rounds/"
    "r24-arm-conditional-fibres-revival/run_fiberguard_pmlb_arm_conditional_r24_twice.sh",
    "papers/orion-02-fiberguard-finite-fibre/rounds/"
    "r24-arm-conditional-fibres-revival/ORION02_R24_EXECUTION.slurm",
)

PRESERVED_FILES = (
    "ORION02_R24_JOB_3550275.out",
    "ORION02_R24_JOB_3550275.err",
    "ORION02_R24_VERIFY_3550275_JOB_3550317.out",
    "ORION02_R24_VERIFY_3550275_JOB_3550317.err",
    "ORION02_R24_SACCT_3550275_3550317.txt",
    "ORION02_R24_SCONTROL_3550317.txt",
    "R24_VERIFIER_PARENT_SUMMARY_AMENDMENT_A.json",
    "failed-executions/3550275/STAGE.txt",
    "failed-executions/3550275/WRAPPER_EXIT_CODE.txt",
    "failed-executions/3550275/run_a.parent.json",
    "failed-executions/3550275/run_a.result.json",
    "failed-executions/3550275/run_a.stderr.txt",
    "failed-executions/3550275/run_a.stdout.txt",
    "failed-executions/3550275/run_a.terminal.txt",
    "failed-executions/3550275/run_a.timings.json",
    "failed-executions/3550275/run_a.verification.txt",
    "failed-executions/3550275/run_b.parent.json",
    "failed-executions/3550275/run_b.result.json",
    "failed-executions/3550275/run_b.stderr.txt",
    "failed-executions/3550275/run_b.stdout.txt",
    "failed-executions/3550275/run_b.terminal.txt",
    "failed-executions/3550275/run_b.timings.json",
)


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def git_blob(commit: str, relative: str) -> bytes:
    return subprocess.run(
        ["git", "show", f"{commit}:{relative}"],
        cwd=ROOT,
        check=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    ).stdout


def parse_sacct(path: Path) -> list[dict[str, str]]:
    lines = path.read_text().splitlines()
    header = lines[0].split("|")
    return [dict(zip(header, line.split("|"), strict=True)) for line in lines[1:] if line]


def build() -> dict[str, Any]:
    for relative in PROTECTED_SCIENCE_PATHS:
        current = (ROOT / relative).read_bytes()
        if git_blob(EXECUTION_COMMIT, relative) != current:
            raise AssertionError({"protected_science_source_drift": relative})

    for run in ("a", "b"):
        if sha256_file(FAILED / f"run_{run}.result.json") != RESULT_SHA256:
            raise AssertionError({"result_hash_drift": run})
        if sha256_file(FAILED / f"run_{run}.parent.json") != PARENT_SHA256:
            raise AssertionError({"parent_hash_drift": run})
        if sha256_file(FAILED / f"run_{run}.terminal.txt") != TERMINAL_SHA256:
            raise AssertionError({"terminal_hash_drift": run})
        if (FAILED / f"run_{run}.stderr.txt").read_bytes() != b"":
            raise AssertionError({"scientific_process_stderr_nonempty": run})
    if (FAILED / "run_a.result.json").read_bytes() != (FAILED / "run_b.result.json").read_bytes():
        raise AssertionError("two-process result byte identity failed")
    if (FAILED / "run_a.parent.json").read_bytes() != (FAILED / "run_b.parent.json").read_bytes():
        raise AssertionError("two-process parent byte identity failed")
    if (FAILED / "run_a.terminal.txt").read_bytes() != (FAILED / "run_b.terminal.txt").read_bytes():
        raise AssertionError("two-process terminal byte identity failed")
    if (FAILED / "STAGE.txt").read_text().strip() != "INDEPENDENT_VERIFY_A":
        raise AssertionError("wrapper failure stage drift")
    if (FAILED / "WRAPPER_EXIT_CODE.txt").read_text().strip() != "1":
        raise AssertionError("wrapper exit drift")

    verification_out = (HERE / "ORION02_R24_VERIFY_3550275_JOB_3550317.out").read_text()
    if verification_out.count("VERIFY_OK") != 2:
        raise AssertionError("both preserved results were not independently verified")
    required_lines = {
        "ORION02_R24_JOB_3550275_VERIFICATION_ONLY=PASS",
        f"RESULT_SHA256={RESULT_SHA256}",
        f"TERMINAL={TERMINAL}",
    }
    if not required_lines.issubset(set(verification_out.splitlines())):
        raise AssertionError("verification-only terminal drift")

    jobs = {
        row["JobIDRaw"]: row
        for row in parse_sacct(HERE / "ORION02_R24_SACCT_3550275_3550317.txt")
        if "." not in row["JobIDRaw"]
    }
    if not (
        jobs["3550275"]["State"] == "FAILED"
        and jobs["3550275"]["ExitCode"] == "1:0"
        and jobs["3550275"]["NodeList"] == "cn087"
        and jobs["3550317"]["State"] == "COMPLETED"
        and jobs["3550317"]["ExitCode"] == "0:0"
    ):
        raise AssertionError({"scheduler_custody_drift": jobs})

    result = json.loads((FAILED / "run_a.result.json").read_text())
    if result["terminal"] != TERMINAL or not all(result["hostile_controls"].values()):
        raise AssertionError("scientific terminal/control drift")
    if not (
        result["coverage"]["r23_parent"] == 0.727272727273
        and result["coverage"]["r24_primary"] == 1.0
        and result["coverage"]["r24_negative_control"] == 1.0
        and result["primary"]["certified_n"] == 44
        and result["primary"]["violations_strict"] == 20
    ):
        raise AssertionError("registered R24 metric drift")
    if any(
        result["authority"].get(key)
        for key in (
            "submission_authorized",
            "top_tier_gate_pass",
            "freeze_authorized",
            "external_independence",
        )
    ):
        raise AssertionError("R24 authority promotion")

    artifacts = []
    for relative in PRESERVED_FILES:
        path = HERE / relative
        if not path.is_file():
            raise AssertionError({"missing_preserved_file": relative})
        artifacts.append(
            {
                "path": path.relative_to(ROOT).as_posix(),
                "bytes": path.stat().st_size,
                "sha256": sha256_file(path),
            }
        )

    return {
        "schema": "ORION.FiberGuard.R24.Custody.v1",
        "date": "2026-08-28",
        "attempt_id": "ORION02-REVIVAL-002-R24-ARM-CONDITIONAL-BOUNDARY-FIBRES",
        "terminal": "ORION02_R24_ATTEMPT_002_COUNTED_CERTIFICATE_INVALID",
        "source_chronology": {
            "scientific_execution_commit": EXECUTION_COMMIT,
            "post_outcome_verifier_amendment_commit": AMENDMENT_COMMIT,
            "protected_science_sources_unchanged": True,
            "amendment_receipt": (
                "papers/orion-02-fiberguard-finite-fibre/rounds/"
                "r24-arm-conditional-fibres-revival/"
                "R24_VERIFIER_PARENT_SUMMARY_AMENDMENT_A.json"
            ),
        },
        "scheduler": {
            "scientific_wrapper_job": {
                "job_id": 3550275,
                "node": "cn087",
                "state": "FAILED",
                "exit_code": "1:0",
                "elapsed": "00:22:46",
                "failure_stage": "INDEPENDENT_VERIFY_A",
                "scientific_processes_completed": 2,
            },
            "verification_only_job": {
                "job_id": 3550317,
                "node": jobs["3550317"]["NodeList"],
                "state": "COMPLETED",
                "exit_code": "0:0",
                "elapsed": "00:00:04",
                "scientific_executor_invoked": False,
            },
        },
        "scientific_outcome": {
            "terminal": TERMINAL,
            "result_sha256": RESULT_SHA256,
            "r23_parent_sha256": PARENT_SHA256,
            "two_process_byte_identity": True,
            "coverage": {
                "r23_parent": 0.727272727273,
                "r24_primary": 1.0,
                "r24_negative_control": 1.0,
                "target": 0.95,
            },
            "certificate": {
                "certified_n": 44,
                "violations_strict": 20,
                "violation_rate": 0.454545454545,
                "maximum_allowed_rate": 0.1,
                "valid": False,
            },
            "paired_tests": {
                "against_r23_parent": {
                    "mean_diff": -0.008448463125,
                    "ci_lower": -0.018359034781,
                    "ci_upper": 0.000107770719,
                },
                "against_lexical_control": {
                    "mean_diff": 0.000323174048,
                    "ci_lower": 0.0,
                    "ci_upper": 0.000969522145,
                },
            },
            "mechanistic_disposition": (
                "arm conditioning repairs coverage but the exact selected-fibre "
                "maximum does not transfer as a valid held-out certificate; "
                "geometry also does not beat the matched lexical control"
            ),
            "original_r23_adverse_result_preserved": True,
            "all_hostile_controls_pass": True,
        },
        "verification": {
            "preserved_run_a": "VERIFY_OK",
            "preserved_run_b": "VERIFY_OK",
            "verification_only_job_pass": True,
            "verifier_defect_was_schema_only": True,
        },
        "attempt_accounting": {
            "counts_toward_100": True,
            "attempt_ordinal": 2,
            "remaining_attempts": 98,
            "status": "COUNTED_ADVERSE_CERTIFICATE_INVALID",
            "active_after_completion": True,
            "stop_condition_reached": False,
        },
        "next_mechanistic_discriminator": (
            "prospectively test a cross-fitted risk-calibrated upper bound rather "
            "than the raw selected-development maximum, while retaining the "
            "arm-conditioned coverage and matched lexical control"
        ),
        "artifacts": artifacts,
        "unsolvable": [],
        "authority": {
            "scientific_authority_delta": "NONE",
            "external_independence": False,
            "submission_authorized": False,
            "top_tier_gate_pass": False,
            "paper_freeze_authorized": False,
        },
    }


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--write", action="store_true")
    args = parser.parse_args(argv)
    report = build()
    payload = json.dumps(report, indent=2, sort_keys=True) + "\n"
    if args.write:
        RECEIPT.write_text(payload)
    elif json.loads(RECEIPT.read_text()) != report:
        raise AssertionError("committed R24 custody receipt drift")
    print("ORION02_R24_CLOSEOUT=PASS")
    print(json.dumps(report, sort_keys=True, separators=(",", ":")))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

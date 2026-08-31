#!/usr/bin/env python3
"""Run the direct bounded quantum replay gates used by Wave-A specialist closure.

The runner deliberately selects deterministic, safe-output checks. It does not
rerun heavy chemistry DPs or overwrite tracked scientific receipts. It combines:

* ORION-05's standalone no-ORION-import support-two proof sanity;
* ORION-05 R11's committed executable result plus a fresh isolated pair-count replay;
* the Q-series publication/content-binding synchronization tests;
* QG9 V6's support-one normalization theorem replay;
* QG12's all-instance SixLCU P0 theorem replay; and
* the QG programme scientific-closure ledger, which keeps refutations and
  bounded CANNOT_CHECK outcomes as first-class evidence.

A PASS grants no novelty, physical-quantum, journal, or submission authority.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
SCHEMA = "ORION.WaveAQuantumReplayReceipt.v1"
RAW_DIR_NAME = "quantum-replay-raw"
R11_RESULT = ROOT / "papers/orion-05-tare-expressivity/Q1_R11_SPARSE_DIRECT_EXECUTABLE_RESULT_V1.json"
R11_PROTOCOL = ROOT / "papers/orion-05-tare-expressivity/Q1_R11_SPARSE_DIRECT_EXECUTABLE_PROTOCOL_V1.md"
R11_SOLVER = ROOT / "papers/orion-05-tare-expressivity/q1_r11_sparse_direct_solver.py"
R11_PAIR_CHECKER = ROOT / "papers/orion-05-tare-expressivity/q1_r11_pair_count_independent.py"
R11_TERMINAL = "Q1_R11_EXACT_O_N9_DIRECT_SOLVER_THEOREM"


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def run(command: list[str], *, stdout_path: Path | None = None) -> str:
    proc = subprocess.run(
        command,
        cwd=ROOT,
        check=False,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
    )
    if stdout_path is not None:
        stdout_path.parent.mkdir(parents=True, exist_ok=True)
        stdout_path.write_text(proc.stdout, encoding="utf-8")
    if proc.returncode != 0:
        raise SystemExit(
            f"command failed ({proc.returncode}): {' '.join(command)}\n{proc.stdout[-8000:]}"
        )
    return proc.stdout


def load(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise SystemExit(f"expected JSON object: {path}")
    return value


def assert_q1(value: dict[str, Any]) -> None:
    if value.get("schema") != "ORION.Q1.IndependentHumanProofSanity.v1":
        raise SystemExit("ORION-05 independent sanity schema drifted")
    if value.get("status") != "PASS" or value.get("orion_quantum_imports") is not False:
        raise SystemExit("ORION-05 independent sanity not PASS/no-import")
    if value.get("restore_lemma", {}).get("max_delta_f3") != 2:
        raise SystemExit("ORION-05 Restore lemma max delta drifted")
    classes = value.get("class_lemma", {})
    if classes.get("w3_to_w8_failure_count") != 0:
        raise SystemExit("ORION-05 support>=3 class lemma failed")
    if len(classes.get("w2_failures", [])) != 4:
        raise SystemExit("ORION-05 sharp support-two boundary drifted")


def assert_r11_result(value: dict[str, Any]) -> None:
    if value.get("terminal") != R11_TERMINAL:
        raise SystemExit(f"ORION-05 R11 terminal drifted: {value.get('terminal')}")
    authority = value.get("authority")
    if not isinstance(authority, dict):
        raise SystemExit("ORION-05 R11 authority object missing")
    expected_authority = {
        "algorithmic_theorem": True,
        "novelty_authority": False,
        "physical_quantum_resource_authority": False,
        "production_runtime_value": False,
        "submission_authority": False,
        "scope": "frozen R6M six-slot grammar and declared objective only",
    }
    for key, expected in expected_authority.items():
        if authority.get(key) != expected:
            raise SystemExit(f"ORION-05 R11 authority drifted: {key}")
    if value.get("protocol_sha256") != sha256(R11_PROTOCOL):
        raise SystemExit("ORION-05 R11 live protocol digest drifted")
    if value.get("solver_sha256") != sha256(R11_SOLVER):
        raise SystemExit("ORION-05 R11 live solver digest drifted")
    if value.get("pair_checker_sha256") != sha256(R11_PAIR_CHECKER):
        raise SystemExit("ORION-05 R11 live independent checker digest drifted")
    gates = value.get("gates")
    if not isinstance(gates, dict) or not gates or not all(gates.values()):
        raise SystemExit("ORION-05 R11 executable gates not uniformly green")
    complete = value.get("complete_n1")
    if not isinstance(complete, dict) or complete.get("pass") is not True:
        raise SystemExit("ORION-05 R11 complete n=1 gate not green")
    if complete.get("denominator") != 729 or complete.get("expected_denominator") != 729:
        raise SystemExit("ORION-05 R11 complete n=1 denominator drifted")
    qg7 = value.get("qg7_support2")
    if not isinstance(qg7, dict) or qg7.get("pass") is not True:
        raise SystemExit("ORION-05 R11 registered support-two panel not green")
    isolation = value.get("source_isolation")
    if not isinstance(isolation, dict) or isolation.get("pass") is not True:
        raise SystemExit("ORION-05 R11 source isolation not green")
    independent = value.get("independent_pair_checker")
    if not isinstance(independent, dict) or independent.get("pass") is not True:
        raise SystemExit("ORION-05 R11 recorded independent checker not green")


def assert_qg9(value: dict[str, Any]) -> None:
    expected = "QG9_RANK2_ALL_N_SUPPORT1_SUFFICIENCY_MACHINE_CHECKED"
    if value.get("terminal") != expected:
        raise SystemExit(f"QG9 V6 terminal drifted: {value.get('terminal')}")
    if not all(value.get("gates", {}).values()):
        raise SystemExit("QG9 V6 has a false gate")
    if value.get("support_bound") != 1 or value.get("intrinsic_support_number") != 1:
        raise SystemExit("QG9 V6 support-one theorem drifted")
    if value.get("support0_infeasible") is not True:
        raise SystemExit("QG9 V6 support-zero infeasibility drifted")
    if value.get("novelty_authority") is not False:
        raise SystemExit("QG9 V6 replay acquired novelty authority")


def assert_qg12(value: dict[str, Any]) -> None:
    expected = "QG12_SIXLCU_P0_ALL_INSTANCE_THEOREM_MACHINE_CHECKED"
    if value.get("terminal") != expected:
        raise SystemExit(f"QG12 terminal drifted: {value.get('terminal')}")
    if not all(value.get("gates", {}).values()):
        raise SystemExit("QG12 has a false gate")
    regression = value.get("blind_complete_regression", {})
    if regression.get("n1_count") != 729 or regression.get("n2_count") != 38760:
        raise SystemExit("QG12 exhaustive regression denominator drifted")
    if regression.get("zero_mismatches") is not True:
        raise SystemExit("QG12 complete regression has mismatches")
    if value.get("novelty_authority") is not False:
        raise SystemExit("QG12 replay acquired novelty authority")


def assert_qg_programme(value: dict[str, Any]) -> None:
    expected = (
        "ORION_QG_PROGRAMME_SCIENTIFICALLY_CLOSED__"
        "THEOREMS_REFUTATIONS_AND_BOUNDED_CANNOT_CHECKS_RECEIPTED__NOT_NOVELTY_AUTHORITY"
    )
    if value.get("terminal") != expected:
        raise SystemExit(f"QG programme terminal drifted: {value.get('terminal')}")
    if value.get("scientifically_closed") is not True or value.get("all_gates") is not True:
        raise SystemExit("QG programme closure gates are not all green")
    if value.get("novelty_authority") is not False:
        raise SystemExit("QG programme replay acquired novelty authority")
    cannot = value.get("bounded_cannot_checks", {})
    if not isinstance(cannot, dict) or not {"qg7d", "qg11"}.issubset(cannot):
        raise SystemExit("QG programme lost bounded CANNOT_CHECK history")


def package_rel(path: Path) -> str:
    return f"{RAW_DIR_NAME}/{path.name}"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args(argv)
    out = args.out if args.out.is_absolute() else ROOT / args.out
    raw = out.parent / RAW_DIR_NAME
    raw.mkdir(parents=True, exist_ok=True)

    q1_stdout = raw / "orion05-independent-proof-sanity.stdout.json"
    q1_text = run(
        [sys.executable, "papers/orion-05-tare-expressivity/independent_human_proof_sanity.py"],
        stdout_path=q1_stdout,
    ).strip()
    try:
        q1 = json.loads(q1_text.splitlines()[-1])
    except (json.JSONDecodeError, IndexError) as exc:
        raise SystemExit("cannot parse ORION-05 independent proof sanity output") from exc
    assert_q1(q1)

    r11 = load(R11_RESULT)
    assert_r11_result(r11)
    r11_pair_log = raw / "orion05-r11-independent-pair-checker.log"
    r11_pair_stdout = run([sys.executable, str(R11_PAIR_CHECKER.relative_to(ROOT))], stdout_path=r11_pair_log)
    if "Q1_R11_INDEPENDENT_FINITE_CHECK_PASS" not in r11_pair_stdout:
        raise SystemExit("ORION-05 R11 fresh independent pair replay missing PASS terminal")
    recorded_independent = r11.get("independent_pair_checker", {})
    if sha256(r11_pair_log) != recorded_independent.get("stdout_sha256"):
        raise SystemExit("ORION-05 R11 fresh independent pair replay digest differs from committed result")

    pytest_log = raw / "q-series-publication-sync-pytest.log"
    pytest_cmd = [
        sys.executable,
        "-m",
        "pytest",
        "-q",
        "tests/unit/publication/test_framework_snapshot.py",
        "tests/unit/publication/test_q_series_final_spec.py",
        "tests/unit/publication/test_q_series_content_binding.py",
    ]
    run(pytest_cmd, stdout_path=pytest_log)

    qg9_path = raw / "qg9-v6-support1-normalization.json"
    run(
        [
            sys.executable,
            "research/extensions/orion-qg/qg9_v6_support1_normalization.py",
            "--output",
            str(qg9_path),
        ],
        stdout_path=raw / "qg9-v6.stdout.log",
    )
    qg9 = load(qg9_path)
    assert_qg9(qg9)

    qg12_path = raw / "qg12-sixlcu-p0-theorem.json"
    run(
        [
            sys.executable,
            "research/extensions/orion-qg/qg12_sixlcu_p0_theorem.py",
            "--output",
            str(qg12_path),
        ],
        stdout_path=raw / "qg12.stdout.log",
    )
    qg12 = load(qg12_path)
    assert_qg12(qg12)

    qg_programme_path = raw / "qg-programme-scientific-closure.json"
    run(
        [
            sys.executable,
            "research/extensions/orion-qg/qg_programme_scientific_closure.py",
            "--output",
            str(qg_programme_path),
        ],
        stdout_path=raw / "qg-programme.stdout.log",
    )
    qg_programme = load(qg_programme_path)
    assert_qg_programme(qg_programme)

    receipt = {
        "schema": SCHEMA,
        "date": "2026-08-27",
        "scientific_authority_delta": "NONE",
        "novelty_authority": False,
        "physical_quantum_advantage_claim": False,
        "journal_acceptance_authority": False,
        "orion05": {
            "independent_sanity_status": q1["status"],
            "restore_max_delta_f3": q1["restore_lemma"]["max_delta_f3"],
            "support2_sharp_failure_patterns": len(q1["class_lemma"]["w2_failures"]),
            "support3_to_8_failures": q1["class_lemma"]["w3_to_w8_failure_count"],
            "stdout_sha256": sha256(q1_stdout),
            "r11": {
                "terminal": r11["terminal"],
                "algorithmic_theorem": r11["authority"]["algorithmic_theorem"],
                "scope": r11["authority"]["scope"],
                "novelty_authority": r11["authority"]["novelty_authority"],
                "production_runtime_value": r11["authority"]["production_runtime_value"],
                "complete_n1_denominator": r11["complete_n1"]["denominator"],
                "all_executable_gates": all(r11["gates"].values()),
                "result_sha256": sha256(R11_RESULT),
                "protocol_sha256": sha256(R11_PROTOCOL),
                "solver_sha256": sha256(R11_SOLVER),
                "pair_checker_sha256": sha256(R11_PAIR_CHECKER),
                "fresh_pair_replay_sha256": sha256(r11_pair_log),
            },
        },
        "q_series_publication_sync": {
            "pytest_status": "PASS",
            "log_sha256": sha256(pytest_log),
        },
        "orion09": {
            "qg9_terminal": qg9["terminal"],
            "qg9_support_bound": qg9["support_bound"],
            "qg9_intrinsic_support_number": qg9["intrinsic_support_number"],
            "qg9_all_gates": all(qg9["gates"].values()),
            "qg9_sha256": sha256(qg9_path),
            "qg12_terminal": qg12["terminal"],
            "qg12_n1": qg12["blind_complete_regression"]["n1_count"],
            "qg12_n2": qg12["blind_complete_regression"]["n2_count"],
            "qg12_all_gates": all(qg12["gates"].values()),
            "qg12_sha256": sha256(qg12_path),
            "programme_terminal": qg_programme["terminal"],
            "programme_all_gates": qg_programme["all_gates"],
            "programme_sha256": sha256(qg_programme_path),
        },
        "orion10": {
            "programme_terminal": qg_programme["terminal"],
            "programme_all_gates": qg_programme["all_gates"],
            "bounded_cannot_checks": qg_programme["bounded_cannot_checks"],
            "programme_sha256": sha256(qg_programme_path),
            "note": (
                "The QG programme closure binds the QG-5/QG-5b/QG-7 forecast/counterexample/"
                "explanation history without rerunning nondeterministic tracked timing receipts."
            ),
        },
        "raw_artifacts": {
            "q1_stdout": package_rel(q1_stdout),
            "r11_pair_checker_log": package_rel(r11_pair_log),
            "pytest_log": package_rel(pytest_log),
            "qg9": package_rel(qg9_path),
            "qg12": package_rel(qg12_path),
            "qg_programme": package_rel(qg_programme_path),
            "note": "The materializer copies this directory beside the receipt inside each TQE package.",
        },
        "terminal": "WAVE_A_QUANTUM_DIRECT_REPLAYS_PASS__BOUNDED_AUTHORITY_ONLY",
    }
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(receipt["terminal"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

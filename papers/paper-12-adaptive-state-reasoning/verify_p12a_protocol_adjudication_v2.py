from __future__ import annotations

import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile

HERE = Path(__file__).resolve().parent
RUNNER = HERE / "run_p12a_matched_budget_v1.py"
OUT = HERE / "P12A_PROTOCOL_ADJUDICATION_V2.json"
EXPECTED_SHA = "0194bc094f5696583533af5baae41e7c339902603d3706c8a1d2a78493f98947"
EXPECTED_SCIENTIFIC_TERMINAL = "P12A_JOINT_ALLOCATION_SUPERIORITY_SUPPORTED"


def execute_once(root: Path) -> tuple[bytes, dict[str, object]]:
    root.mkdir(parents=True, exist_ok=True)
    runner = root / RUNNER.name
    shutil.copy2(RUNNER, runner)
    proc = subprocess.run([sys.executable, str(runner)], cwd=root, capture_output=True, text=True)
    if proc.returncode != 0:
        raise RuntimeError(proc.stdout + proc.stderr)
    result_path = root / "P12A_MATCHED_BUDGET_RESULT_V1.json"
    raw = result_path.read_bytes()
    return raw, json.loads(raw.decode("utf-8"))


def main() -> None:
    with tempfile.TemporaryDirectory(prefix="p12a-adjudication-") as td:
        root = Path(td)
        raw_a, a = execute_once(root / "a")
        raw_b, b = execute_once(root / "b")

    sha_a = hashlib.sha256(raw_a).hexdigest()
    sha_b = hashlib.sha256(raw_b).hexdigest()
    replay_match = raw_a == raw_b and sha_a == sha_b == EXPECTED_SHA
    scientific_gates = dict(a["gates"])
    scientific_pass = all(bool(v) for v in scientific_gates.values())
    runner_terminal_pass = a["terminal"] == EXPECTED_SCIENTIFIC_TERMINAL and b["terminal"] == EXPECTED_SCIENTIFIC_TERMINAL

    gates = {
        "all_frozen_scientific_gates_pass": scientific_pass,
        "runner_scientific_terminal_passes_both_runs": runner_terminal_pass,
        "two_fresh_subprocess_payloads_byte_identical": replay_match,
        "canonical_hash_matches_committed_receipt": sha_a == EXPECTED_SHA,
    }
    authoritative_terminal = (
        EXPECTED_SCIENTIFIC_TERMINAL
        if all(gates.values())
        else "P12A_JOINT_ALLOCATION_SUPERIORITY_GATE_NOT_MET"
    )
    result = {
        "schema": "ORION.P12A.ProtocolAdjudication.v2",
        "protocol": "P12A_MATCHED_BUDGET_JOINT_ALLOCATION_PROTOCOL_V1.md",
        "runner": RUNNER.name,
        "correction": (
            "The V1 runner evaluated the frozen scientific gates but omitted the protocol's byte-identical replay gate from its terminal decision path. "
            "V2 does not change any outcome, threshold, policy, seed, metric, or comparator; it independently executes the frozen V1 runner twice and makes the protocol terminal contingent on replay identity."
        ),
        "v1_runner_terminal_authority": "NON_AUTHORITATIVE_ALONE__REPLAY_GATE_OMITTED",
        "scientific_payload_sha256_run_a": sha_a,
        "scientific_payload_sha256_run_b": sha_b,
        "scientific_summary": a["summary"],
        "scientific_gates": scientific_gates,
        "gates": gates,
        "authoritative_terminal": authoritative_terminal,
    }
    text = json.dumps(result, indent=2, sort_keys=True) + "\n"
    OUT.write_text(text, encoding="utf-8")
    print(text, end="")
    if authoritative_terminal != EXPECTED_SCIENTIFIC_TERMINAL:
        raise SystemExit(1)


if __name__ == "__main__":
    main()

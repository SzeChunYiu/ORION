from __future__ import annotations

import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile

HERE = Path(__file__).resolve().parent
RUNNER = HERE / "run_p14c_specification_separated_governance_v1.py"
CASES = HERE / "P14C_ADJUDICATION_CASES_V1.json"
OUT = HERE / "P14C_PROTOCOL_ADJUDICATION_V2.json"
EXPECTED_SHA = "74032348de7e6508b6c1827aabcf1bf9d354d30b9c6f81c8259fdb3535f01a63"
EXPECTED_SCIENTIFIC_TERMINAL = "P14C_SPECIFICATION_SEPARATED_GOVERNANCE_CONFORMANCE_SUPPORTED"


def execute_once(root: Path) -> tuple[bytes, dict[str, object]]:
    root.mkdir(parents=True, exist_ok=True)
    runner = root / RUNNER.name
    cases = root / CASES.name
    shutil.copy2(RUNNER, runner)
    shutil.copy2(CASES, cases)
    proc = subprocess.run([sys.executable, str(runner)], cwd=root, capture_output=True, text=True)
    if proc.returncode != 0:
        raise RuntimeError(proc.stdout + proc.stderr)
    path = root / "P14C_SPECIFICATION_SEPARATED_RESULT_V1.json"
    raw = path.read_bytes()
    return raw, json.loads(raw.decode("utf-8"))


def main() -> None:
    with tempfile.TemporaryDirectory(prefix="p14c-adjudication-") as td:
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
        else "P14C_SPECIFICATION_SEPARATED_GOVERNANCE_CONFORMANCE_GATE_NOT_MET"
    )
    result = {
        "schema": "ORION.P14C.ProtocolAdjudication.v2",
        "protocol": "P14C_SPECIFICATION_SEPARATED_GOVERNANCE_PROTOCOL_V1.md",
        "runner": RUNNER.name,
        "adjudication_spec": CASES.name,
        "correction": (
            "The V1 P14C runner evaluated the frozen conformance gates but omitted the protocol's two-run byte-identity requirement from its terminal decision path. "
            "V2 changes no case, gold label, policy, gate, threshold, or comparator; it executes the exact frozen V1 runner and adjudication table twice and makes protocol authority contingent on replay identity."
        ),
        "v1_runner_terminal_authority": "NON_AUTHORITATIVE_ALONE__REPLAY_GATE_OMITTED",
        "scientific_payload_sha256_run_a": sha_a,
        "scientific_payload_sha256_run_b": sha_b,
        "strongest_non_orion_baseline": a["strongest_non_orion_baseline"],
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

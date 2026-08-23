#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import json
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
ARTIFACTS = REPO / "artifacts"
ANALYZER = REPO / "research" / "extensions" / "orion-qg" / "qg20_recovery_feature_search.py"
VERIFIER = REPO / "development" / "orion-qg-regime-geometry" / "qg20_recovery_generic_verify.py"
SELECTION = ARTIFACTS / "orion-qg-qg20-recovery-selection.json"
RESULT = ARTIFACTS / "orion-qg-qg20-recovery.json"
VERIFY = ARTIFACTS / "orion-qg-qg20-recovery-generic-verification.json"
DUAL = ARTIFACTS / "orion-qg-qg20-recovery-dual-harness.json"
SELECTION_PREFIX = "ORIONQG_QG20_RECOVERY_SELECTION="
RESULT_PREFIX = "ORIONQG_QG20_RECOVERY="
VERIFY_PREFIX = "ORIONQG_QG20_RECOVERY_GENERIC_VERIFY="


def run_script(path: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(path)],
        cwd=REPO,
        check=True,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )


def one_line(stdout: str, prefix: str) -> tuple[int, dict]:
    lines = stdout.splitlines()
    hits = [(index, line) for index, line in enumerate(lines) if line.startswith(prefix)]
    if len(hits) != 1:
        raise RuntimeError(f"expected one {prefix} line, got {len(hits)}")
    index, line = hits[0]
    payload = json.loads(line[len(prefix):])
    if not isinstance(payload, dict):
        raise TypeError("receipt token must be an object")
    return index, payload


def canonical_bytes(path: Path) -> bytes:
    return path.read_bytes()


def main() -> int:
    ARTIFACTS.mkdir(parents=True, exist_ok=True)
    for path in (SELECTION, RESULT, VERIFY, DUAL):
        path.unlink(missing_ok=True)

    first = run_script(ANALYZER)
    s_index, selection_token = one_line(first.stdout, SELECTION_PREFIX)
    r_index, result_token = one_line(first.stdout, RESULT_PREFIX)
    if s_index >= r_index:
        raise RuntimeError("selection receipt was not sealed before heldout result")
    if selection_token.get("heldout_labels_accessed") is not False:
        raise RuntimeError("selection receipt claims heldout labels were accessed")
    first_selection = canonical_bytes(SELECTION)
    first_result = canonical_bytes(RESULT)
    first_result_digest = hashlib.sha256(first_result).hexdigest()

    # Fresh deterministic replay of the analyzer, including the protected n=4 panel.
    second = run_script(ANALYZER)
    one_line(second.stdout, SELECTION_PREFIX)
    one_line(second.stdout, RESULT_PREFIX)
    replay_identical = (
        first_selection == canonical_bytes(SELECTION)
        and first_result == canonical_bytes(RESULT)
    )
    if not replay_identical:
        raise RuntimeError("QG-20 recovery analyzer replay drift")

    verify_run = run_script(VERIFIER)
    _v_index, verify_token = one_line(verify_run.stdout, VERIFY_PREFIX)
    verify_payload = json.loads(VERIFY.read_text(encoding="utf-8"))
    if verify_token.get("verification_digest") != verify_payload.get("verification_digest"):
        raise RuntimeError("verifier stdout does not bind verifier artifact")

    result = json.loads(RESULT.read_text(encoding="utf-8"))
    verifier_accept = verify_payload.get("decision") == "ACCEPT"
    analyzer_terminal = result.get("terminal")
    if not verifier_accept:
        terminal = "QG20_RECOVERY_DUAL_VERIFIER_DISAGREEMENT"
    elif analyzer_terminal == "QG20_RECOVERY_COMPACT_COORDINATE_SET_RESTORES_DETERMINATION_ON_FROZEN_TRAIN_AND_N4_PANEL":
        terminal = analyzer_terminal
    elif analyzer_terminal in {
        "QG20_RECOVERY_TRAIN_DETERMINATION_ONLY__N4_MIXED",
        "QG20_RECOVERY_NO_ARITY3_COORDINATE_SET__FULL_QUOTIENT_REQUIRED",
    }:
        terminal = analyzer_terminal
    else:
        terminal = "CANNOT_CHECK"

    dual = {
        "schema": "orion-qg.qg20_recovery_dual_harness.v1",
        "terminal": terminal,
        "analyzer_terminal": analyzer_terminal,
        "selected_features": result["selection"]["selected_features"],
        "train_stats": result["selection"]["selected_train_stats"],
        "heldout": result["heldout"],
        "analyzer_replay_identical": replay_identical,
        "analyzer_result_sha256": first_result_digest,
        "verifier_decision": verify_payload.get("decision"),
        "verifier_checks": verify_payload.get("checks"),
        "verifier_digest": verify_payload.get("verification_digest"),
        "selection_before_heldout": True,
        "novelty_authority": False,
        "all_n_authority": False,
        "physical_quantum_advantage_claim": False,
    }
    dual["dual_digest"] = hashlib.sha256(
        json.dumps(dual, sort_keys=True, separators=(",", ":")).encode("utf-8")
    ).hexdigest()
    DUAL.write_text(json.dumps(dual, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print("ORIONQG_QG20_RECOVERY_DUAL=" + json.dumps(dual, sort_keys=True, separators=(",", ":")))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

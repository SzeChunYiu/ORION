#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import json
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
ARTIFACTS = REPO / "artifacts"
ANALYZER = REPO / "research" / "extensions" / "orion-qg" / "qg20_recovery_complete_n4.py"
VERIFIER = REPO / "development" / "orion-qg-regime-geometry" / "qg20_recovery_complete_n4_verify.py"
RESULT = ARTIFACTS / "orion-qg-qg20-recovery-complete-n4.json"
VERIFY = ARTIFACTS / "orion-qg-qg20-recovery-complete-n4-verification.json"
DUAL = ARTIFACTS / "orion-qg-qg20-recovery-complete-n4-dual.json"
RESULT_PREFIX = "ORIONQG_QG20_RECOVERY_COMPLETE_N4="
VERIFY_PREFIX = "ORIONQG_QG20_RECOVERY_COMPLETE_N4_VERIFY="


def execute(path: Path):
    return subprocess.run(
        [sys.executable, str(path)], cwd=REPO, text=True,
        stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True,
    )


def token(stdout: str, prefix: str):
    hits = [line for line in stdout.splitlines() if line.startswith(prefix)]
    if len(hits) != 1:
        raise RuntimeError(f"expected exactly one {prefix} token, got {len(hits)}")
    return json.loads(hits[0][len(prefix):])


def main() -> int:
    ARTIFACTS.mkdir(parents=True, exist_ok=True)
    for path in (RESULT, VERIFY, DUAL):
        path.unlink(missing_ok=True)

    first = execute(ANALYZER)
    first_token = token(first.stdout, RESULT_PREFIX)
    first_bytes = RESULT.read_bytes()
    first_sha = hashlib.sha256(first_bytes).hexdigest()

    second = execute(ANALYZER)
    token(second.stdout, RESULT_PREFIX)
    replay_identical = first_bytes == RESULT.read_bytes()
    if not replay_identical:
        raise RuntimeError("complete n4 analyzer replay mismatch")

    verified = execute(VERIFIER)
    verify_token = token(verified.stdout, VERIFY_PREFIX)
    verify_payload = json.loads(VERIFY.read_text(encoding="utf-8"))
    if verify_token.get("verification_digest") != verify_payload.get("verification_digest"):
        raise RuntimeError("verifier token/artifact mismatch")

    source = json.loads(RESULT.read_text(encoding="utf-8"))
    if verify_payload.get("decision") != "ACCEPT":
        terminal = "QG20_RECOVERY_COMPLETE_N4_DUAL_DISAGREEMENT"
    else:
        terminal = source.get("terminal", "CANNOT_CHECK")
    dual = {
        "schema": "orion-qg.qg20_recovery_complete_n4_dual.v1",
        "terminal": terminal,
        "source_terminal": source.get("terminal"),
        "feature": source.get("frozen_feature"),
        "instances": source.get("instances"),
        "positives": source.get("positives"),
        "base": source.get("base"),
        "augmented": source.get("augmented"),
        "analyzer_replay_identical": replay_identical,
        "analyzer_sha256": first_sha,
        "verifier_decision": verify_payload.get("decision"),
        "verifier_checks": verify_payload.get("checks"),
        "verifier_digest": verify_payload.get("verification_digest"),
        "feature_search_performed": False,
        "all_n_authority": False,
        "novelty_authority": False,
    }
    dual["dual_digest"] = hashlib.sha256(
        json.dumps(dual, sort_keys=True, separators=(",", ":")).encode()
    ).hexdigest()
    DUAL.write_text(json.dumps(dual, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print("ORIONQG_QG20_RECOVERY_COMPLETE_N4_DUAL=" + json.dumps(dual, sort_keys=True, separators=(",", ":")))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

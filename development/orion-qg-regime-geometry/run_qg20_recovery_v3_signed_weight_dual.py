#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import json
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
ARTIFACTS = REPO / "artifacts"
ANALYZER = REPO / "research" / "extensions" / "orion-qg" / "qg20_recovery_v3_signed_weight.py"
VERIFIER = REPO / "development" / "orion-qg-regime-geometry" / "qg20_recovery_v3_signed_weight_verify.py"
RESULT = ARTIFACTS / "orion-qg-qg20-recovery-v3-signed-weight.json"
VERIFY = ARTIFACTS / "orion-qg-qg20-recovery-v3-signed-weight-verification.json"
DUAL = ARTIFACTS / "orion-qg-qg20-recovery-v3-signed-weight-dual.json"
RP = "ORIONQG_QG20_RECOVERY_V3_SIGNED_WEIGHT="
VP = "ORIONQG_QG20_RECOVERY_V3_SIGNED_WEIGHT_VERIFY="


def run(path: Path, allow_reject=False):
    p = subprocess.run([sys.executable, str(path)], cwd=REPO, text=True,
                       stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=False)
    if p.returncode not in ({0, 2} if allow_reject else {0}):
        raise RuntimeError(f"{path.name} instrument failure: code={p.returncode} stdout={p.stdout!r} stderr={p.stderr!r}")
    return p


def token(stdout: str, prefix: str):
    hits = [line for line in stdout.splitlines() if line.startswith(prefix)]
    if len(hits) != 1:
        raise RuntimeError(f"expected one {prefix} token, got {len(hits)}")
    return json.loads(hits[0][len(prefix):])


def main() -> int:
    ARTIFACTS.mkdir(parents=True, exist_ok=True)
    for path in (RESULT, VERIFY, DUAL):
        path.unlink(missing_ok=True)
    first = run(ANALYZER)
    token(first.stdout, RP)
    first_bytes = RESULT.read_bytes()
    first_sha = hashlib.sha256(first_bytes).hexdigest()
    second = run(ANALYZER)
    token(second.stdout, RP)
    replay = first_bytes == RESULT.read_bytes()
    if not replay:
        raise RuntimeError("V3 analyzer replay mismatch")
    vr = run(VERIFIER, allow_reject=True)
    vt = token(vr.stdout, VP)
    vp = json.loads(VERIFY.read_text(encoding="utf-8"))
    if vt.get("verification_digest") != vp.get("verification_digest"):
        raise RuntimeError("V3 verifier token/artifact mismatch")
    source = json.loads(RESULT.read_text(encoding="utf-8"))
    terminal = source.get("terminal") if vp.get("decision") == "ACCEPT" else "QG20_RECOVERY_V3_DUAL_DISAGREEMENT"
    dual = {
        "schema": "orion-qg.qg20_recovery_v3_signed_weight_dual.v1",
        "terminal": terminal,
        "source_terminal": source.get("terminal"),
        "instances": source.get("instances"),
        "positives": source.get("positives"),
        "representation": source.get("representation"),
        "maps": source.get("maps"),
        "analyzer_replay_identical": replay,
        "analyzer_sha256": first_sha,
        "verifier_decision": vp.get("decision"),
        "verifier_checks": vp.get("checks"),
        "verifier_digest": vp.get("verification_digest"),
        "feature_search_performed": False,
        "same_domain_recovery": True,
        "all_n_authority": False,
        "novelty_authority": False,
    }
    dual["dual_digest"] = hashlib.sha256(json.dumps(dual, sort_keys=True, separators=(",", ":")).encode()).hexdigest()
    DUAL.write_text(json.dumps(dual, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print("ORIONQG_QG20_RECOVERY_V3_SIGNED_WEIGHT_DUAL=" + json.dumps(dual, sort_keys=True, separators=(",", ":")))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

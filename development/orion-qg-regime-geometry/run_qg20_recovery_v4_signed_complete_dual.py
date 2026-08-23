#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import json
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
ARTIFACTS = REPO / "artifacts"
ANALYZER = REPO / "research" / "extensions" / "orion-qg" / "qg20_recovery_v4_signed_complete.py"
VERIFIER = REPO / "development" / "orion-qg-regime-geometry" / "qg20_recovery_v4_signed_complete_verify.py"
RESULT = ARTIFACTS / "orion-qg-qg20-recovery-v4-signed-complete.json"
VERIFY = ARTIFACTS / "orion-qg-qg20-recovery-v4-signed-complete-verification.json"
DUAL = ARTIFACTS / "orion-qg-qg20-recovery-v4-signed-complete-dual.json"
RP = "ORIONQG_QG20_RECOVERY_V4_SIGNED_COMPLETE="
VP = "ORIONQG_QG20_RECOVERY_V4_SIGNED_COMPLETE_VERIFY="


def run(path: Path, allow_reject=False):
    p = subprocess.run([sys.executable, str(path)], cwd=REPO, text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=False)
    if p.returncode not in ({0,2} if allow_reject else {0}):
        raise RuntimeError(f"{path.name} instrument failure code={p.returncode} stdout={p.stdout!r} stderr={p.stderr!r}")
    return p


def token(stdout, prefix):
    hits = [line for line in stdout.splitlines() if line.startswith(prefix)]
    if len(hits) != 1:
        raise RuntimeError(f"expected one {prefix} token, got {len(hits)}")
    return json.loads(hits[0][len(prefix):])


def main() -> int:
    ARTIFACTS.mkdir(parents=True, exist_ok=True)
    for path in (RESULT, VERIFY, DUAL): path.unlink(missing_ok=True)
    first = run(ANALYZER); token(first.stdout, RP)
    b1 = RESULT.read_bytes(); sha = hashlib.sha256(b1).hexdigest()
    second = run(ANALYZER); token(second.stdout, RP)
    replay = b1 == RESULT.read_bytes()
    if not replay: raise RuntimeError("V4 analyzer replay mismatch")
    vr = run(VERIFIER, allow_reject=True); vt = token(vr.stdout, VP)
    vp = json.loads(VERIFY.read_text())
    if vt.get("verification_digest") != vp.get("verification_digest"):
        raise RuntimeError("V4 verifier token/artifact mismatch")
    source = json.loads(RESULT.read_text())
    terminal = source.get("terminal") if vp.get("decision") == "ACCEPT" else "QG20_RECOVERY_V4_DUAL_DISAGREEMENT"
    dual = {
        "schema":"orion-qg.qg20_recovery_v4_signed_complete_dual.v1",
        "terminal":terminal,
        "source_terminal":source.get("terminal"),
        "instances":source.get("instances"),
        "positives":source.get("positives"),
        "representation":source.get("representation"),
        "coefficient_count":source.get("coefficient_count"),
        "maps":source.get("maps"),
        "analyzer_replay_identical":replay,
        "analyzer_sha256":sha,
        "verifier_decision":vp.get("decision"),
        "verifier_checks":vp.get("checks"),
        "verifier_digest":vp.get("verification_digest"),
        "feature_search_performed":False,
        "same_domain_recovery":True,
        "all_n_authority":False,
        "novelty_authority":False,
    }
    dual["dual_digest"] = hashlib.sha256(json.dumps(dual, sort_keys=True, separators=(",", ":")).encode()).hexdigest()
    DUAL.write_text(json.dumps(dual, indent=2, sort_keys=True)+"\n")
    print("ORIONQG_QG20_RECOVERY_V4_SIGNED_COMPLETE_DUAL="+json.dumps(dual,sort_keys=True,separators=(",", ":")))
    return 0

if __name__ == "__main__": raise SystemExit(main())

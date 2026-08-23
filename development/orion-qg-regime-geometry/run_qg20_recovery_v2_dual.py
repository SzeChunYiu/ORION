#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import json
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
ARTIFACTS = REPO / "artifacts"
ANALYZER = REPO / "research" / "extensions" / "orion-qg" / "qg20_recovery_v2_frozen_grammar.py"
VERIFIER = REPO / "development" / "orion-qg-regime-geometry" / "qg20_recovery_v2_verify.py"
SELECTION = ARTIFACTS / "orion-qg-qg20-recovery-v2-selection.json"
RESULT = ARTIFACTS / "orion-qg-qg20-recovery-v2.json"
VERIFY = ARTIFACTS / "orion-qg-qg20-recovery-v2-verification.json"
DUAL = ARTIFACTS / "orion-qg-qg20-recovery-v2-dual.json"
SP = "ORIONQG_QG20_RECOVERY_V2_SELECTION="
RP = "ORIONQG_QG20_RECOVERY_V2="
VP = "ORIONQG_QG20_RECOVERY_V2_VERIFY="


def run(path: Path, allow_reject=False):
    done = subprocess.run(
        [sys.executable, str(path)], cwd=REPO, text=True,
        stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=False,
    )
    allowed = {0, 2} if allow_reject else {0}
    if done.returncode not in allowed:
        raise RuntimeError(
            f"{path.name} instrument failure code={done.returncode} stdout={done.stdout!r} stderr={done.stderr!r}"
        )
    return done


def receipt(stdout: str, prefix: str):
    hits = [(i, line) for i, line in enumerate(stdout.splitlines()) if line.startswith(prefix)]
    if len(hits) != 1:
        raise RuntimeError(f"expected one {prefix} token, got {len(hits)}")
    i, line = hits[0]
    return i, json.loads(line[len(prefix):])


def main() -> int:
    ARTIFACTS.mkdir(parents=True, exist_ok=True)
    for path in (SELECTION, RESULT, VERIFY, DUAL):
        path.unlink(missing_ok=True)

    first = run(ANALYZER)
    sidx, stok = receipt(first.stdout, SP)
    ridx, _rtok = receipt(first.stdout, RP)
    if sidx >= ridx or stok.get("holdout_labels_accessed") is not False:
        raise RuntimeError("V2 selection was not sealed before holdout opening")
    sbytes = SELECTION.read_bytes()
    rbytes = RESULT.read_bytes()
    rsha = hashlib.sha256(rbytes).hexdigest()

    second = run(ANALYZER)
    receipt(second.stdout, SP)
    receipt(second.stdout, RP)
    replay = sbytes == SELECTION.read_bytes() and rbytes == RESULT.read_bytes()
    if not replay:
        raise RuntimeError("V2 analyzer replay mismatch")

    vr = run(VERIFIER, allow_reject=True)
    _vidx, vtok = receipt(vr.stdout, VP)
    vp = json.loads(VERIFY.read_text(encoding="utf-8"))
    if vtok.get("verification_digest") != vp.get("verification_digest"):
        raise RuntimeError("V2 verifier token/artifact mismatch")

    source = json.loads(RESULT.read_text(encoding="utf-8"))
    terminal = (
        source.get("terminal")
        if vp.get("decision") == "ACCEPT"
        else "QG20_RECOVERY_V2_DUAL_DISAGREEMENT"
    )
    dual = {
        "schema": "orion-qg.qg20_recovery_v2_dual.v1",
        "terminal": terminal,
        "source_terminal": source.get("terminal"),
        "selected_companions": source["selection"]["selected_companions"],
        "train_instances": source["selection"]["train_instances"],
        "holdout_instances": source["selection"]["holdout_instances"],
        "train_stats": source["selection"]["selected_train_stats"],
        "holdout_stats": source["holdout_selected_stats"],
        "complete_stats": source["complete_selected_stats"],
        "analyzer_replay_identical": replay,
        "analyzer_sha256": rsha,
        "selection_before_holdout": True,
        "verifier_decision": vp.get("decision"),
        "verifier_checks": vp.get("checks"),
        "verifier_digest": vp.get("verification_digest"),
        "new_feature_definitions_added": False,
        "all_n_authority": False,
        "novelty_authority": False,
    }
    dual["dual_digest"] = hashlib.sha256(
        json.dumps(dual, sort_keys=True, separators=(",", ":")).encode()
    ).hexdigest()
    DUAL.write_text(json.dumps(dual, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print("ORIONQG_QG20_RECOVERY_V2_DUAL=" + json.dumps(dual, sort_keys=True, separators=(",", ":")))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

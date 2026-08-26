#!/usr/bin/env python3
from __future__ import annotations
import hashlib, json, pathlib, sys

ROOT = pathlib.Path(__file__).resolve().parents[2]
Q3 = ROOT / "papers/orion-07-dual-instrument"
ROWS = [
    ("Q3-R1", Q3/"instances/Q3-R1-QG19", ROOT/"research/extensions/orion-qg/QG19_OUTSIDE_CONE_SHARPNESS_RESULTS.json"),
    ("Q3-R2", Q3/"instances/Q3-R2-QG20", ROOT/"research/extensions/orion-qg/QG20_SIXLCU_OBJECTIVE_SCOPE_RESULTS.json"),
]

def load(p): return json.loads(p.read_text(encoding="utf-8"))
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()

def main():
    errors=[]
    for iid,d,r in ROWS:
        binding=load(d/"DEFERRED_OUTCOME_BINDING.json")
        replay=load(d/"INDEPENDENT_REPLAY_RECEIPT.json")
        score=load(d/"FINAL_SCORE.json")
        result=load(r)
        actual=sha(r)
        for label,val in (
            ("binding",binding.get("scientific_result_sha256")),
            ("replay",replay.get("scientific_result_sha256")),
            ("replayed",replay.get("replayed_result_sha256")),
        ):
            if val != actual: errors.append(f"RESULT_SHA_MISMATCH:{iid}:{label}:{val}!={actual}")
        if binding.get("scientific_result_digest") != result.get("result_digest"):
            errors.append(f"RESULT_DIGEST_BINDING_MISMATCH:{iid}")
        if replay.get("scientific_result_digest") != result.get("result_digest"):
            errors.append(f"RESULT_DIGEST_REPLAY_MISMATCH:{iid}")
        if binding.get("scientific_terminal") != result.get("terminal") or score.get("scientific_terminal") != result.get("terminal"):
            errors.append(f"TERMINAL_BINDING_MISMATCH:{iid}")
        if replay.get("byte_identical_double_run") is not True or replay.get("chronology_gate_passed") is not True:
            errors.append(f"REPLAY_GATE_FAIL:{iid}")
        if score.get("score_status") != "SCORED" or score.get("aggregate_reliability_claim_authorized") is not False:
            errors.append(f"SCORE_GATE_FAIL:{iid}")
    if errors:
        print("Q3_RESULT_BINDINGS=FAIL")
        print("\n".join("- "+e for e in errors)); return 1
    print("Q3_RESULT_BINDINGS=PASS")
    for iid,d,r in ROWS: print(f"{iid}_RESULT_SHA256={sha(r)}")
    return 0
if __name__ == "__main__": sys.exit(main())

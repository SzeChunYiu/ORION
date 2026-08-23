#!/usr/bin/env python3
"""Independent semantic replay for Q3 V0's publication-level claim.

The replay reconstructs the scored V0 coordinates from the raw lane receipts and rechecks
the later R6P/R6Q outcomes used for deferred frontier alignment. It does not rerun the
historical host model and grants no scientific authority.
"""
from __future__ import annotations
import hashlib, json, pathlib, sys

ROOT = pathlib.Path(__file__).resolve().parents[2]
A = ROOT / "development/orion-q-max-r0/dual-harness-benchmark-v0/DUAL_HARNESS_LANE_A_RECEIPT.json"
B = ROOT / "development/orion-q-max-r0/DUAL_HARNESS_LANE_B_RECEIPT.json"
V0 = ROOT / "development/orion-q-max-r0/dual-harness-benchmark-v0/DUAL_HARNESS_AGREEMENT_BENCHMARK_V0_RESULTS.json"
R6P = ROOT / "research/extensions/orion-q/MAX_R6P_WEIGHT2_FRAME_DONOR_CLOSURE_RESULTS.json"
R6Q = ROOT / "research/extensions/orion-q/MAX_R6Q_REGIME_PREDICATE_RESULTS.json"

def load(p): return json.loads(p.read_text(encoding="utf-8"))
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def canon(x): return json.dumps(x, sort_keys=True, separators=(",", ":"), allow_nan=False).encode()

def main():
    a,b,v0,p,q = map(load,(A,B,V0,R6P,R6Q))
    errors=[]
    if a.get("diagnosed_layer") != "REPRESENTATION_REGIME_CHARACTERIZATION": errors.append("LANE_A_LAYER")
    if not str(a.get("selected_move","")).startswith("REGIME_PREDICATE_CHARACTERIZATION_PRIMARY"): errors.append("LANE_A_MOVE")
    cycle=b.get("campaign_run",{}).get("cycles",[{}])[0]
    decision=cycle.get("decision",{})
    if decision.get("responsibility",{}).get("identified_hypothesis_id") != "RESP:REPRESENTATION_REGIME_UNCHARACTERIZED": errors.append("LANE_B_LAYER")
    if decision.get("selected_id") != "COMPUTE:REGIME_CHARACTERIZATION": errors.append("LANE_B_MOVE")
    if "AGREE on all scored coordinates" not in v0.get("verdict",""): errors.append("V0_VERDICT")
    if p.get("critical_set_summary",{}).get("all_critical_closed") is not True: errors.append("R6P_DEFERRED_ALIGNMENT")
    if q.get("outcome") != "EXACT_PREDICATE_FOUND" or q.get("gates",{}).get("selected_predicate_zero_error_everywhere") is not True: errors.append("R6Q_DEFERRED_ALIGNMENT")
    summary={
      "schema":"ORIONQ.Q3V0SemanticReplay.v2",
      "lane_a_layer":a.get("diagnosed_layer"),
      "lane_a_move":a.get("selected_move"),
      "lane_b_layer":decision.get("responsibility",{}).get("identified_hypothesis_id"),
      "lane_b_move":decision.get("selected_id"),
      "preoutcome_relation":"AGREE",
      "deferred_frontier_alignment":"ALIGNED",
      "source_sha256":{"lane_a":sha(A),"lane_b":sha(B),"v0":sha(V0),"r6p":sha(R6P),"r6q":sha(R6Q)},
      "aggregate_reliability_claim_authorized":False,
      "scientific_authority":False,
    }
    summary["replay_digest"]=hashlib.sha256(canon(summary)).hexdigest()
    if errors:
      print("Q3_V0_REPLAY=FAIL"); print("\n".join("- "+e for e in errors)); return 1
    print("Q3_V0_REPLAY=PASS")
    print(json.dumps(summary,sort_keys=True))
    return 0
if __name__ == "__main__": sys.exit(main())

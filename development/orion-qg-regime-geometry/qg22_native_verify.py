#!/usr/bin/env python3
"""Native ORION-Q responsibility gate for QG-22."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

ROOT=Path(__file__).resolve().parents[2]
A0=ROOT/"artifacts/orion-qg-qg22-hidden-home-state.json"
G0=ROOT/"artifacts/orion-qg-qg22-generic-verification.json"
QG7C=ROOT/"research/extensions/orion-qg/QG7C_CLASSIFICATION_RESULTS.json"
PAD=ROOT/"research/extensions/orion-qg/QG7D_PADDING_ABLATION_RESULTS.json"
INFO=ROOT/"research/extensions/orion-qg/qg7d_information_closure.py"
OUT=ROOT/"artifacts/orion-qg-qg22-native-verification.json"
TOKEN="ORIONQG_QG22_NATIVE="
POS="QG22_HIDDEN_HOME_J5_DELTA_EXACTLY_DETERMINED_BY_MINIMAL_5_PREDICATE_STATE"


def canon(v:Any)->str:
    return json.dumps(v,sort_keys=True,separators=(",",":"),allow_nan=False)

def sha(p:Path)->str:
    return hashlib.sha256(p.read_bytes()).hexdigest()

def verify_digest(raw):
    u={k:v for k,v in raw.items() if k!="result_digest"}
    return raw.get("result_digest")==hashlib.sha256(canon(u).encode()).hexdigest()

def main()->int:
    ap=argparse.ArgumentParser(); ap.add_argument("--analyzer",type=Path,default=A0); ap.add_argument("--generic",type=Path,default=G0); ap.add_argument("--output",type=Path,default=OUT); args=ap.parse_args()
    a=json.loads(args.analyzer.read_text()); g=json.loads(args.generic.read_text()); q=json.loads(QG7C.read_text()); p=json.loads(PAD.read_text())
    pp=(q["t4b_pinned"]["failing_census"]["PP_ja0_delta1"]+q["t4b_pinned"]["failing_census"]["PP_ja0_delta2"]+q["t4b_pinned"]["failing_census"]["PP_ja1_delta1"])
    checks={
        "analyzer_schema":a.get("schema")=="ORIONQG.QG22.HiddenHomeState.v1",
        "analyzer_digest":verify_digest(a),
        "analyzer_positive":a.get("terminal")==POS and a.get("all_gates") is True,
        "generic_accept":g.get("decision")=="ACCEPT_STATE_QUOTIENT" and g.get("all_checks") is True,
        "generic_bound":g.get("source_result_digest")==a.get("result_digest"),
        "qg7c_parent":q.get("terminal")=="QG7C_PARTIAL__L4B_OPEN" and pp==32556,
        "padding_parent":p.get("terminal")=="QG7D_PADDING_ABLATION_NO_BTRIPLEPRIME_IN_FROZEN_ROWS__J5_REQUIRED" and p.get("both_accept") is True,
        "parent_hashes":a.get("parent",{}).get("qg7c_sha256")==sha(QG7C) and a.get("parent",{}).get("padding_sha256")==sha(PAD) and a.get("parent",{}).get("information_closure_source_sha256")==sha(INFO),
        "minimum_exact":a.get("minimum_determining_cardinality")==5==g.get("minimum_determining_cardinality"),
        "selected_is_minimum":["b0","ab","ac","bm0","a_bm"] in a.get("minimum_determining_subsets",[]),
        "branch_cells":all(v==18 for v in a.get("selected_cell_counts",{}).values()),
        "pair_cells":a.get("paired",{}).get("signature_cells")==324==g.get("paired_signature_cells"),
        "parent_range_reproduced":a.get("paired",{}).get("delta_min")==-4 and a.get("paired",{}).get("delta_max")==4 and set(map(int,a.get("paired",{}).get("delta_histogram",{}).keys()))==set(range(-4,5)),
        "scope_separation":a.get("scientific_scope")=="EXACT_J5_HIDDEN_HOME_DELTA_STATE_ONLY" and a.get("all_n_theorem_authority") is False and g.get("all_n_theorem_authority") is False,
        "authority_bounded":a.get("novelty_authority") is False and a.get("r6_authority") is False and a.get("physical_quantum_advantage_claim") is False and g.get("novelty_authority") is False,
        "protected_subject_not_read":a.get("protected_subject_read") is False,
    }
    if all(checks.values()): decision="ACCEPT_STATE_QUOTIENT"; responsibility="J5_DELTA_DETERMINATION"
    elif not checks["generic_accept"] or not checks["generic_bound"]: decision="REJECT_GENERIC_DISAGREEMENT"; responsibility="GENERIC_DISAGREEMENT"
    elif not checks["qg7c_parent"] or not checks["padding_parent"] or not checks["parent_hashes"]: decision="REJECT_PARENT_BINDING"; responsibility="PARENT_BINDING_GAP"
    elif not checks["scope_separation"]: decision="REJECT_AUTHORITY_LAUNDERING"; responsibility="ALL_N_NORMALIZATION_BLOCKED"
    else: decision="CANNOT_CHECK"; responsibility="CANNOT_CHECK"
    out={"schema":"ORIONQG.QG22.NativeVerification.v1","decision":decision,"responsibility":responsibility,"all_checks":all(checks.values()),"checks":checks,"source_result_digest":a.get("result_digest"),"state_quotient_authority":decision=="ACCEPT_STATE_QUOTIENT","all_n_theorem_authority":False,"novelty_authority":False,"r6_authority":False,"physical_quantum_advantage_claim":False}
    args.output.parent.mkdir(parents=True,exist_ok=True); args.output.write_text(json.dumps(out,indent=2,sort_keys=True)+"\n")
    print(TOKEN+canon({"decision":decision,"responsibility":responsibility,"all_checks":out["all_checks"],"state_quotient":out["state_quotient_authority"]}))
    return 0

if __name__=="__main__": raise SystemExit(main())

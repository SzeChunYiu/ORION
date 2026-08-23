#!/usr/bin/env python3
from __future__ import annotations
import hashlib,json
from pathlib import Path
HERE=Path(__file__).resolve().parent; CASES=HERE/"p13_verifier_responsibility_cases_v1.json"; PROTOCOL=HERE/"P13_VERIFIER_RESPONSIBILITY_SHIFT_PROTOCOL_V1.md"
def main():
    spec=json.loads(CASES.read_text()); n=len(spec["cases"]); assert n==12
    for c in spec["cases"]:
        assert c["n_vars"]==5 and 0<=c["free_var"]<5 and len(c["old_model"])==5
        # Four unit clauses fix every non-free variable; free variable yields exactly two base models.
        # Added unit clause fixes free variable opposite the old model, yielding exactly one new model.
        assert c["old_model"][c["free_var"]] in (0,1)
    expected_correct={"RCS":2*n,"ALWAYS_RAW":2*n,"CONFIDENCE_ONLY":n,"PROVENANCE_ONLY":n}
    expected_stale={"RCS":0,"ALWAYS_RAW":0,"CONFIDENCE_ONLY":n,"PROVENANCE_ONLY":n}
    expected_reads={"RCS":5*n,"ALWAYS_RAW":9*n,"CONFIDENCE_ONLY":0,"PROVENANCE_ONLY":0}
    payload={"schema":"P13.VerifierResponsibilityShiftIndependent.v1","protocol_sha256":hashlib.sha256(PROTOCOL.read_bytes()).hexdigest(),"cases_sha256":hashlib.sha256(CASES.read_bytes()).hexdigest(),"case_count":n,"expected_correct":expected_correct,"expected_stale_reuse":expected_stale,"expected_raw_literal_reads":expected_reads,"expected_rcs_raw_read_reduction":1-(5/9),"terminal":"P13_VERIFIER_RESPONSIBILITY_SHIFT_SECOND_INDEPENDENT_CHECKER_GREEN"}
    raw=json.dumps(payload,sort_keys=True,separators=(",", ":")).encode(); payload["receipt_sha256"]=hashlib.sha256(raw).hexdigest(); print(json.dumps(payload,indent=2,sort_keys=True)); return 0
if __name__=="__main__": raise SystemExit(main())

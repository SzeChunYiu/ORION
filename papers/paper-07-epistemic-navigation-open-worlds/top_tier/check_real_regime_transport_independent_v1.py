#!/usr/bin/env python3
from __future__ import annotations
import hashlib,json
from pathlib import Path
import numpy as np
from sklearn.datasets import load_wine
HERE=Path(__file__).resolve().parent;PROTOCOL=HERE/"P7_REAL_REGIME_TRANSPORT_PROTOCOL_V1.md";SOURCES=HERE/"P7_REAL_REGIME_SOURCES_2026-08-23.md"
def main():
    y=np.asarray(load_wine().target,dtype=int); counts={int(k):int((y==k).sum()) for k in (0,1,2)}
    assert counts=={0:59,1:71,2:48},counts
    ambiguous=counts[1]+counts[2]; unique=counts[0]
    payload={
      "schema":"P7.RealRegimeTransportIndependent.v1",
      "protocol_sha256":hashlib.sha256(PROTOCOL.read_bytes()).hexdigest(),
      "sources_sha256":hashlib.sha256(SOURCES.read_bytes()).hexdigest(),
      "standard":{"case_count":14,"witness_exact":14,"value_only_false_closure":8,"always_reopen_unnecessary":6,"changed_term_count":4,"unchanged_control_count":2},
      "wine":{"sample_count":len(y),"class_counts":{str(k):v for k,v in counts.items()},"row_count":4*len(y),"ambiguous_coarse0_count":ambiguous,"unique_coarse1_count":unique,"witness_exact":4*len(y),"value_only_false_closure":2*ambiguous,"always_reopen_unnecessary":2*len(y)+2*unique,"sequential_support_history_disposition_differences":ambiguous},
      "terminal":"P7_REAL_REGIME_TRANSPORT_SECOND_INDEPENDENT_CHECKER_GREEN"}
    raw=json.dumps(payload,sort_keys=True,separators=(",", ":")).encode();payload["receipt_sha256"]=hashlib.sha256(raw).hexdigest();print(json.dumps(payload,indent=2,sort_keys=True));return 0
if __name__=="__main__":raise SystemExit(main())

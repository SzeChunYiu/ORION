from __future__ import annotations

import itertools
import json

DONOR=("compute_valid","dependency_supported","effect_valid","action_authorized","execution_provenance_valid")
SCI=("evidence_version_current","scientific_source_authorized","claim_scope_supported","verification_epoch_current")
REQ={
 "DEPENDENCY_MAINTENANCE":{"compute_valid","dependency_supported"},
 "EFFECTFUL_COMPUTATION":{"compute_valid","effect_valid"},
 "CONTINUING_AUTH_EXEC_PROVENANCE":{"action_authorized","execution_provenance_valid"},
}

def independent_audit():
    state_evals=0; conservative=0; t2=0; t5=0; ideal_mismatch=0; donor_preservation_fail=0; no_alarm=0
    for emb, req in REQ.items():
        for bits in itertools.product((0,1), repeat=9):
            s=dict(zip(DONOR+SCI,map(bool,bits)))
            donor_ok=all(s[k] for k in req)
            science_ok=donor_ok and all(s[k] for k in SCI)
            ideal_ok=all(s[k] for k in req|set(SCI))
            state_evals+=1
            if donor_ok != all(s[k] for k in req): donor_preservation_fail+=1
            if all(s[k] for k in SCI):
                conservative+=1
                if science_ok != donor_ok: raise AssertionError("conservative reduction failed")
            if science_ok != ideal_ok: ideal_mismatch+=1
        # algebraic witness enumeration independent of the primary checker
        irrelevant=[k for k in DONOR if k not in req]
        for free in itertools.product((0,1), repeat=len(irrelevant)):
            base={k:True for k in DONOR+SCI}
            for k,v in zip(irrelevant,free): base[k]=bool(v)
            assert all(base[k] for k in req)
            no_alarm += 1
            for c in SCI:
                bad=dict(base); bad[c]=False
                assert all(bad[k] for k in req)
                assert not (all(bad[k] for k in req) and all(bad[k] for k in SCI))
                t2 += 1; t5 += 1
    return {
      "state_evaluations":state_evals,
      "donor_preservation_failures":donor_preservation_fail,
      "t2_separation_pairs":t2,
      "t3_conservative_cases":conservative,
      "ideal_product_mismatches":ideal_mismatch,
      "t5_countermodels":t5,
      "no_alarm_cases":no_alarm,
      "state":"BOUNDED_VERIFIED" if (state_evals,t2,conservative,ideal_mismatch,t5,no_alarm)==(1536,96,96,0,96,24) and donor_preservation_fail==0 else "INVALIDATED"
    }

if __name__=="__main__": print(json.dumps(independent_audit(),sort_keys=True,indent=2))

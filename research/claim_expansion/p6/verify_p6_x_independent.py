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
    state_evals=0; conservative=0; t2=0; t5=0; ideal_mismatch=0; no_alarm=0
    for emb, req in REQ.items():
        for bits in itertools.product((0,1), repeat=9):
            s=dict(zip(DONOR+SCI,map(bool,bits)))
            donor_ok=all(s[k] for k in req)
            science_ok=donor_ok and all(s[k] for k in SCI)
            ideal_ok=all(s[k] for k in req|set(SCI))
            state_evals+=1
            # `donor_ok` was just assigned this same expression, so this compares a
            # value with itself and `donor_preservation_fail` is 0 under every theory
            # of donor validity. Unlike `ideal_ok` below -- which is built over
            # `req | SCI` and so is a genuinely separate derivation from `science_ok` --
            # there is no second construction here to compare against. Preserving the
            # donor verdict through the forgetful map is what should be checked, and
            # this model carries no map to apply. Withdrawn rather than counted.
            # See research/failures/2026-08-unfalsifiable-check-zero-refutation-capacity/.
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
      "donor_preservation_failures":None,
      "t2_separation_pairs":t2,
      "t3_conservative_cases":conservative,
      "ideal_product_mismatches":ideal_mismatch,
      "t5_countermodels":t5,
      "no_alarm_cases":no_alarm,
      "donor_preservation_status":"CANNOT_CHECK",
      "donor_preservation_cannot_check_reason":(
        "the comparison restated donor_ok; this model carries no forgetful map to "
        "apply, so donor preservation cannot be checked here"),
      # Three-valued, and CANNOT_CHECK unconditionally while donor preservation
      # is withdrawn: an unchecked constituent blocks exactly as a violation would.
      # The measured tuple is still published above, so restoring a real donor
      # preservation check is all that stands between this and a live verdict.
      "state":"CANNOT_CHECK"
    }

if __name__=="__main__": print(json.dumps(independent_audit(),sort_keys=True,indent=2))

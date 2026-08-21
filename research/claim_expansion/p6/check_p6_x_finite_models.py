from __future__ import annotations

import hashlib
import itertools
import json

DONOR_FIELDS=("compute_valid","dependency_supported","effect_valid","action_authorized","execution_provenance_valid")
SCI_FIELDS=("evidence_version_current","scientific_source_authorized","claim_scope_supported","verification_epoch_current")
EMBEDDINGS={
  "DEPENDENCY_MAINTENANCE": ("compute_valid","dependency_supported"),
  "EFFECTFUL_COMPUTATION": ("compute_valid","effect_valid"),
  "CONTINUING_AUTH_EXEC_PROVENANCE": ("action_authorized","execution_provenance_valid"),
}

def donor_valid(state, embedding):
    return all(state[f] for f in EMBEDDINGS[embedding])

def scientific_admissible(state, embedding):
    return donor_valid(state, embedding) and all(state[f] for f in SCI_FIELDS)

def ideal_product(state, embedding):
    return donor_valid(state, embedding) and all(state[f] for f in SCI_FIELDS)

def _independently_defined(left, right):
    """True when two predicates are not the same expression written twice.

    T4 asserts that scientific admissibility equals the ideal product of the
    donor and scientific constraints. That is a theorem only if the two sides
    are built independently. As written they are byte-identical, so comparing
    them restates one expression and `t4_violations` is 0 for every possible
    theory of admissibility -- a structural zero published beside measured ones.

    Giving `ideal_product` its own definition needs FORMAL_CORE's construction
    of the product and is the theory lane's call. What is fixable here is the
    reporting: a comparison that cannot come out any other way must say so
    rather than emit a violation count.
    """

    import inspect

    def body(function):
        source = inspect.getsource(function).split("\n", 1)[1]
        return inspect.cleandoc(source)

    return body(left) != body(right)

def forget(state):
    return tuple((f,state[f]) for f in DONOR_FIELDS)

def enumerate_states():
    fields=DONOR_FIELDS+SCI_FIELDS
    for bits in itertools.product((False,True), repeat=len(fields)):
        yield dict(zip(fields,bits))

def run():
    states=list(enumerate_states())
    t4_checkable=_independently_defined(scientific_admissible, ideal_product)
    rows=[]
    t1_violations=0
    t3_violations=0
    t3_cases=0
    t4_violations=0
    t2_pairs=[]
    t5_countermodels=[]
    no_alarm=[]
    for emb in EMBEDDINGS:
        for s in states:
            d=donor_valid(s,emb)
            # U preserves donor-visible coordinate values and donor validity by construction.
            if d != all(dict(forget(s))[f] for f in EMBEDDINGS[emb]): t1_violations += 1
            if all(s[f] for f in SCI_FIELDS):
                t3_cases += 1
                if scientific_admissible(s,emb) != d: t3_violations += 1
            if t4_checkable and scientific_admissible(s,emb) != ideal_product(s,emb): t4_violations += 1
            rows.append({"embedding":emb,"donor":forget(s),"science":tuple((f,s[f]) for f in SCI_FIELDS),"donor_valid":d,"scientific_admissible":scientific_admissible(s,emb),"ideal":ideal_product(s,emb)})
        # Separation and preservation countermodels for every donor-visible state that is donor-valid.
        for donor_bits in itertools.product((False,True), repeat=len(DONOR_FIELDS)):
            base=dict(zip(DONOR_FIELDS,donor_bits)); base.update({f:True for f in SCI_FIELDS})
            if not donor_valid(base,emb): continue
            no_alarm.append((emb,forget(base),scientific_admissible(base,emb)))
            for sf in SCI_FIELDS:
                changed=dict(base); changed[sf]=False
                assert forget(base)==forget(changed)
                assert scientific_admissible(base,emb) and not scientific_admissible(changed,emb)
                t2_pairs.append((emb,sf,forget(base)))
                # Donor transition remains valid because donor-visible state is unchanged, but certificate revokes.
                assert donor_valid(changed,emb)
                t5_countermodels.append((emb,sf,forget(base)))
    canonical=json.dumps(rows,sort_keys=True,separators=(",",":"),default=list)
    return {
      "state_evaluations":len(rows),
      "states_per_embedding":len(states),
      "t1_violations":t1_violations,
      "t2_separation_pairs":len(t2_pairs),
      "t2_coordinates_covered":sorted({sf for _,sf,_ in t2_pairs}),
      "t3_cases":t3_cases,
      "t3_violations":t3_violations,
      "t4_violations":t4_violations if t4_checkable else None,
      "t4_status":"CHECKED" if t4_checkable else "CANNOT_CHECK",
      "t4_cannot_check_reason":None if t4_checkable else (
        "ideal_product is the same expression as scientific_admissible, so the "
        "comparison restates one definition and cannot refute any theory"),
      "t5_countermodels":len(t5_countermodels),
      "no_alarm_cases":len(no_alarm),
      "canonical_rows_sha256":hashlib.sha256(canonical.encode()).hexdigest(),
      # Three-valued on purpose. `t4_violations` is None when T4 could not be
      # checked, and `not None` is True, so a two-valued terminal would read an
      # unchecked T4 as a clean one -- the exact substitution this repair exists
      # to stop. An unexercised check blocks the terminal as a violation would.
      "terminal":(
        "CANNOT_CHECK" if not t4_checkable
        else "PASS" if not (t1_violations or t3_violations or t4_violations)
             and len(t2_pairs)==96 and len(t5_countermodels)==96
        else "FAIL")
    }

if __name__=="__main__": print(json.dumps(run(),sort_keys=True,indent=2))

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

# T4 -- the ideal enriched donor product, constructed rather than copied.
#
# It used to be `scientific_admissible`'s body written a second time, so
# `t4_violations` was 0 for every theory of admissibility. The construction the
# theorem names is a different one: the ideal product is the donor theory whose
# *required-field set* has been enlarged by the four scientific coordinates,
# validated by the donor's own native validator. It mentions "the exact four
# scientific certificate coordinates" the protocol asks for and it never mentions
# `scientific_admissible`, so substituting a wrong theory of admissibility does
# not co-mutate it. This repository's own independent verifier already derives
# its ideal product this way (`all(s[k] for k in req | set(SCI))`).
def enriched_requirements(embedding):
    return EMBEDDINGS[embedding] + SCI_FIELDS

def donor_native_validator(state, required):
    return all(state[f] for f in required)

def ideal_product(state, embedding):
    return donor_native_validator(state, enriched_requirements(embedding))

def _independently_defined(left, right):
    """True when two predicates are not the same expression written twice.

    T1 and T4 each compare two sides of a claim, and each is a theorem only if
    the two sides were built independently. Both were byte-identical as
    originally written -- T4's `ideal_product` was `scientific_admissible`, and
    T1's right-hand side was `donor_valid` recomputed through a map that copies
    every donor field verbatim -- so both counters were 0 for every possible
    theory, structural zeros published beside measured ones.

    Both now have their own construction: `ideal_product` runs the donor
    validator over an enriched requirement set, and `lift_image_along_forget`
    quantifies over the fibre of the forgetful map. This gate stays because the
    repair is only as durable as the distinction: if a later edit collapses
    either pair back into one expression, the counter reports CANNOT_CHECK
    rather than a clean zero.

    Bodies are compared as parsed statements with a leading docstring dropped,
    so prose written about a definition is never mistaken for a second
    definition; the earlier line-split spelling could be fooled by editing a
    comment. When the source cannot be recovered at all, independence is not
    established and the answer is False.
    """

    import ast
    import inspect
    import textwrap

    def body(function):
        try:
            statements = ast.parse(textwrap.dedent(inspect.getsource(function))).body[0].body
        except Exception:
            return None
        if (
            statements
            and isinstance(statements[0], ast.Expr)
            and isinstance(statements[0].value, ast.Constant)
            and isinstance(statements[0].value.value, str)
        ):
            statements = statements[1:]
        return "\n".join(ast.dump(node) for node in statements)

    left_body = body(left)
    right_body = body(right)
    if left_body is None or right_body is None:
        return False
    return left_body != right_body

def forget(state):
    return tuple((f,state[f]) for f in DONOR_FIELDS)

# T1 -- donor preservation under erasure, stated about the lift rather than
# about the donor coordinates.
#
# `U_D` preserves the donor-visible coordinates by construction, so
# `donor_valid(s) == donor_valid(U_D(s))` is one expression compared with
# itself and holds for every theory of admissibility. The object `U_D` was
# never applied to is `scientific_admissible` itself. Its image along `U_D` is
# the donor-language predicate below: a donor-visible state is certified by the
# lifted semantics exactly when *some* scientific enrichment over it is
# admissible. Conservativity is the statement that that image coincides with
# the donor's own verdict, and both directions bite -- the lift may not
# manufacture donor validity it was not given, and may not withdraw a donor
# verdict the donor theory issues.
def donor_visible_states():
    for bits in itertools.product((False,True), repeat=len(DONOR_FIELDS)):
        yield dict(zip(DONOR_FIELDS,bits))

def lift_image_along_forget(donor_state, embedding):
    for bits in itertools.product((False,True), repeat=len(SCI_FIELDS)):
        enriched=dict(donor_state)
        enriched.update(dict(zip(SCI_FIELDS,bits)))
        if scientific_admissible(enriched, embedding):
            return True
    return False

def enumerate_states():
    fields=DONOR_FIELDS+SCI_FIELDS
    for bits in itertools.product((False,True), repeat=len(fields)):
        yield dict(zip(fields,bits))

def _donor_valid_states(embedding):
    for s in enumerate_states():
        if donor_valid(s,embedding):
            yield s

def _admissible_sources(embedding):
    """Donor-valid states with every scientific obligation discharged: T5's "previously admissible"."""
    for s in _donor_valid_states(embedding):
        if all(s[f] for f in SCI_FIELDS):
            yield s

def run():
    states=list(enumerate_states())
    t4_checkable=_independently_defined(scientific_admissible, ideal_product)
    t1_checkable=_independently_defined(lift_image_along_forget, donor_valid)
    rows=[]
    t1_violations=0
    t1_donor_visible_states=0
    t3_violations=0
    t3_cases=0
    t4_violations=0
    t2_pairs=[]
    t5_countermodels=[]
    t5_violations=0
    t5_donor_valid_transitions=0
    no_alarm=[]
    for emb in EMBEDDINGS:
        for s in states:
            d=donor_valid(s,emb)
            if all(s[f] for f in SCI_FIELDS):
                t3_cases += 1
                if scientific_admissible(s,emb) != d: t3_violations += 1
            if t4_checkable and scientific_admissible(s,emb) != ideal_product(s,emb): t4_violations += 1
            rows.append({"embedding":emb,"donor":forget(s),"science":tuple((f,s[f]) for f in SCI_FIELDS),"donor_valid":d,"scientific_admissible":scientific_admissible(s,emb),"ideal":ideal_product(s,emb)})
        # T1 -- conservativity of the lift along U, over the donor-visible states.
        # The image of `scientific_admissible` along `U_D` must be the donor's own
        # verdict: not weaker (no donor-invalid state is certified) and not
        # stronger (every donor-valid state has an admissible enrichment).
        for donor_state in donor_visible_states():
            t1_donor_visible_states += 1
            if t1_checkable and lift_image_along_forget(donor_state,emb) != donor_valid(donor_state,emb):
                t1_violations += 1
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
        # T5 -- certificate preservation under change, over donor-valid
        # *transitions*. The 96 countermodels above hold the donor-visible state
        # fixed, so the clause T5 turns on -- "donor-valid recomputation/support/
        # authorization alone is insufficient" -- was unrepresented: nothing was
        # recomputed. Here the donor side is free to change as long as it stays
        # valid, and the counter is the conclusion the earlier block only ever
        # asserted the premise of: an admissible state that drops a scientific
        # coordinate without revalidating it must not stay admissible.
        for source in _admissible_sources(emb):
            for target in _donor_valid_states(emb):
                dropped=[f for f in SCI_FIELDS if source[f] and not target[f]]
                gained=[f for f in SCI_FIELDS if target[f] and not source[f]]
                if not dropped or gained:
                    continue
                t5_donor_valid_transitions += 1
                assert donor_valid(source,emb) and donor_valid(target,emb)
                if not (scientific_admissible(source,emb) and not scientific_admissible(target,emb)):
                    t5_violations += 1
    canonical=json.dumps(rows,sort_keys=True,separators=(",",":"),default=list)
    checkable=t1_checkable and t4_checkable
    cannot_check_reasons=[]
    if not t1_checkable:
        cannot_check_reasons.append(
          "lift_image_along_forget is the same expression as donor_valid, so the "
          "conservativity comparison restates one definition and cannot refute any theory")
    if not t4_checkable:
        cannot_check_reasons.append(
          "ideal_product is the same expression as scientific_admissible, so the "
          "comparison restates one definition and cannot refute any theory")
    return {
      "state_evaluations":len(rows),
      "states_per_embedding":len(states),
      "t1_violations":t1_violations if t1_checkable else None,
      "t1_donor_visible_states":t1_donor_visible_states,
      "t1_status":"CHECKED" if t1_checkable else "CANNOT_CHECK",
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
      "t5_donor_valid_transitions":t5_donor_valid_transitions,
      "t5_violations":t5_violations,
      "no_alarm_cases":len(no_alarm),
      "cannot_check_reasons":cannot_check_reasons,
      "canonical_rows_sha256":hashlib.sha256(canonical.encode()).hexdigest(),
      # Three-valued on purpose. `t1_violations` and `t4_violations` are None
      # when the corresponding comparison could not be checked, and `not None`
      # is True, so a two-valued terminal would read an unchecked counter as a
      # clean one -- the exact substitution this repair exists to stop. An
      # unexercised check blocks the terminal as a violation would.
      "terminal":(
        "CANNOT_CHECK" if not checkable
        else "PASS" if not (t1_violations or t3_violations or t4_violations or t5_violations)
             and len(t2_pairs)==96 and len(t5_countermodels)==96
        else "FAIL")
    }

if __name__=="__main__": print(json.dumps(run(),sort_keys=True,indent=2))

from __future__ import annotations

def p3_x(case):
    x=case["candidate_visible"]
    if not x["load_bearing_complete"]: return "UNRESOLVED"
    if not x["construct_equal"] or not x["measurement_equal"] or not x["context_equal"]: return "OBSTRUCTION"
    if not x["global_cycle_consistent"]: return "OBSTRUCTION"
    if x["plural_mapping"] or not x["provenance_stance_compatible"]: return "PLURAL_VIEW"
    return "GLUE"

def b1_strong_semantic_product(case):
    x=case["candidate_visible"]
    if not x["load_bearing_complete"]: return "UNRESOLVED"
    if not x["construct_equal"] or not x["measurement_equal"] or not x["context_equal"]: return "OBSTRUCTION"
    # Strong semantic stack preserves the structured coordinates but still treats
    # provenance as trace, chooses one canonical target for plural mappings, and
    # has no scientific-authority use of global cycle consistency.
    return "GLUE"

def b2_canonical_match(case):
    return "GLUE" if case["candidate_visible"]["local_match_score"] >= 0.90 else "OBSTRUCTION"

def b3_ideal_typed_product(case):
    return p3_x(case)

def score(cases, fn):
    return sum(fn(c)==c["protected_gold"]["terminal"] for c in cases)

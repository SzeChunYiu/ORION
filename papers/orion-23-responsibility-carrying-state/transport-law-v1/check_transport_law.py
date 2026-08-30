#!/usr/bin/env python3
"""ORION23.EXTERNAL_RESPONSIBILITY_TRANSPORT.v1 -- exhaustive verification of P1-P5.

Searches for counterexamples. Controls plant violations and require the same predicates
the real comparison uses to catch them.

  0 = verified, terminal emitted    3 = could not check
"""
import itertools, json

STATUSES = ["UNCHANGED", "ENTAILED", "CONTRADICTED", "UNKNOWN"]
SIZES = [3, 4]
SUPPORTED = {"UNCHANGED", "ENTAILED"}


def resolve(status, hidden):
    """UNKNOWN premises have a HIDDEN actual value; the decider cannot see it.

    Modelling this is required by P3's own wording: 'unnecessary revocation' only means
    anything if the premise might in fact have been satisfied. Without a hidden value,
    UNKNOWN is definitionally unsound, pessimistic revocation is always correct, and P5
    is false by construction rather than by evidence. Control V2 caught exactly that.
    """
    out, i = [], 0
    for st in status:
        if st == "UNKNOWN":
            out.append(hidden[i]); i += 1
        else:
            out.append(st)
    return out


def ground_truth_sound_to_reuse(resolved):
    """Reuse is ACTUALLY sound iff every premise, once resolved, is supported."""
    return all(s in SUPPORTED for s in resolved)


def rule_three_valued(status):
    if any(s == "CONTRADICTED" for s in status):
        return "REVOKE"
    if any(s == "UNKNOWN" for s in status):
        return "CANNOT_CHECK"
    return "REUSE"


def rule_unknown_as_unchanged(status):
    st = ["UNCHANGED" if s == "UNKNOWN" else s for s in status]
    return "REVOKE" if any(s == "CONTRADICTED" for s in st) else "REUSE"


def rule_unknown_as_contradicted(status):
    st = ["CONTRADICTED" if s == "UNKNOWN" else s for s in status]
    return "REVOKE" if any(s == "CONTRADICTED" for s in st) else "REUSE"


RULES = {"three_valued": rule_three_valued,
         "unknown_as_unchanged": rule_unknown_as_unchanged,
         "unknown_as_contradicted": rule_unknown_as_contradicted}


def unsound(decision, truth):
    """Unsound exactly when the rule REUSEs a certificate that is not supported."""
    return decision == "REUSE" and not truth


def over_revokes(decision, truth):
    """Wasteful exactly when the rule REVOKEs one that was in fact reusable."""
    return decision == "REVOKE" and truth


def main() -> int:
    v_p1, v_p2, v_p3, v_p5 = [], [], [], []
    v1_caught = v2_over = v2_unsound_pessimistic = 0
    v3_elig = v3_ok = 0
    v4_unknown_cases = 0
    rule_stats = {r: {"unsound": 0, "over_revoke": 0, "abstain": 0} for r in RULES}
    cases = 0

    for k in SIZES:
        for status in itertools.product(STATUSES, repeat=k):
            n_unknown = sum(1 for x in status if x == "UNKNOWN")
            has_contra = any(x == "CONTRADICTED" for x in status)
            has_unknown = n_unknown > 0
            if has_unknown and not has_contra:
                v4_unknown_cases += 1

            for hidden in itertools.product(["UNCHANGED", "CONTRADICTED"], repeat=n_unknown):
                cases += 1
                truth = ground_truth_sound_to_reuse(resolve(status, hidden))
                d3 = RULES["three_valued"](status)

                # P1: the three-valued rule REUSEs exactly when it is entitled to decide
                if not has_unknown:
                    if truth != (d3 == "REUSE"):
                        v_p1.append({"status": list(status), "decision": d3})
                    if has_contra and truth:
                        v_p2.append({"status": list(status)})

                # P3: unknown without contradiction must abstain
                if has_unknown and not has_contra and d3 != "CANNOT_CHECK":
                    v_p3.append({"status": list(status), "decision": d3})

                for name, fn in RULES.items():
                    d = fn(status)
                    if d == "CANNOT_CHECK":
                        rule_stats[name]["abstain"] += 1
                        continue
                    if unsound(d, truth):
                        rule_stats[name]["unsound"] += 1
                        if name == "unknown_as_unchanged":
                            v1_caught += 1
                        if name == "unknown_as_contradicted":
                            v2_unsound_pessimistic += 1
                    if over_revokes(d, truth):
                        rule_stats[name]["over_revoke"] += 1
                        if name == "unknown_as_contradicted":
                            v2_over += 1

                if all(x == "UNCHANGED" for x in status):
                    v3_elig += 1
                    if truth and all(fn(status) == "REUSE" for fn in RULES.values()):
                        v3_ok += 1

    # P5: no two-valued rule is both sound and never over-revoking
    for name in ("unknown_as_unchanged", "unknown_as_contradicted"):
        st = rule_stats[name]
        if st["unsound"] == 0 and st["over_revoke"] == 0:
            v_p5.append({"rule": name, "why": "two-valued rule achieved both"})

    v1_pass = v1_caught > 0
    v2_pass = v2_over > 0 and v2_unsound_pessimistic == 0
    v3_pass = v3_elig > 0 and v3_ok == v3_elig
    v4_pass = v4_unknown_cases > 0

    if not (v1_pass and v2_pass and v3_pass and v4_pass):
        terminal, rc = "T4_CANNOT_CHECK", 3
    elif v_p1 or v_p2 or v_p3:
        terminal, rc = "T2_REUSE_CHARACTERISATION_FAILS", 0
    elif v_p5:
        terminal, rc = "T3_TWO_VALUED_RULE_SUFFICES", 0
    else:
        terminal, rc = "T1_TRANSPORT_LAW_HOLDS", 0

    print(json.dumps({
        "schema": "ORION.ORION23.TransportLaw.Result.v1",
        "protocol_identity": "ORION23.EXTERNAL_RESPONSIBILITY_TRANSPORT.v1",
        "authority": "MEASUREMENT_AND_PROOF_ONLY", "scientific_authority_delta": "NONE",
        "premise_set_sizes": SIZES, "cases_enumerated": cases,
        "hidden_value_model": ("UNKNOWN premises carry a hidden actual value the decider cannot see. "
                               "Required by P3's own wording: 'unnecessary revocation' is only meaningful "
                               "if the premise might in fact have been satisfied."),
        "violations": {"P1": len(v_p1), "P2": len(v_p2), "P3": len(v_p3), "P5": len(v_p5)},
        "rule_comparison": rule_stats,
        "controls": {
            "V1_unsound_reuse_is_detectable": {"optimistic_collapse_unsound_cases": v1_caught, "passed": v1_pass},
            "V2_pessimistic_collapse_sound_but_wasteful": {"over_revocations": v2_over,
                "unsound_cases": v2_unsound_pessimistic, "passed": v2_pass},
            "V3_all_clear_no_alarm": {"eligible": v3_elig, "clean": v3_ok, "passed": v3_pass},
            "V4_unknown_cases_present": {"cases": v4_unknown_cases, "passed": v4_pass}},
        "external_corpus": "NOT TESTED AGAINST -- P13_P14_OBJECTIVE_GOLD_RESULTS_V1.json records outcome_accessed: true",
        "terminal": terminal,
        "promotion_status": ("TRANSPORT_LAW_ESTABLISHED__PROMOTION_NOT_EARNED__BOUNDED_PAPER_RETAINED"
                             if terminal == "T1_TRANSPORT_LAW_HOLDS" else "PROMOTION_FAILED"),
    }, indent=2, sort_keys=True))
    return rc


if __name__ == "__main__":
    raise SystemExit(main())

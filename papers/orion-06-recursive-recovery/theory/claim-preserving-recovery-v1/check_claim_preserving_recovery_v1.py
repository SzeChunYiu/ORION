#!/usr/bin/env python3
"""Independent exact regression for ORION06.CLAIM_PRESERVING_RECOVERY.v1.

The theorem is deductive. This checker exhausts small action/predicate influence systems,
recomputes minimum weighted hitting sets, checks the no-repair certificate and dominated-
action reduction, and exercises the claim-identity boundary.
"""
from __future__ import annotations

import hashlib
import json
from itertools import combinations, product


def subsets(n: int):
    for mask in range(1 << n):
        yield frozenset(i for i in range(n) if mask & (1 << i))


def cost(selected, costs):
    return sum(costs[a] for a in selected)


def hits_all(selected, failed, effects):
    return all(any(p in effects[a] for a in selected) for p in failed)


def minimum_hitting_sets(actions_n, failed, effects, costs):
    feasible = [s for s in subsets(actions_n) if hits_all(s, failed, effects)]
    if not feasible:
        return None, []
    optimum = min(cost(s, costs) for s in feasible)
    return optimum, [s for s in feasible if cost(s, costs) == optimum]


def identity_fingerprint(payload):
    keys = (
        "question",
        "population",
        "estimand",
        "protocol_semantics",
        "primary_metric",
        "threshold",
        "protected_corpus",
        "terminal_semantics",
    )
    canonical = {key: payload[key] for key in keys}
    text = json.dumps(canonical, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(text.encode()).hexdigest()


def main() -> int:
    errors = []
    influence_systems = 0
    failure_systems = 0
    lower_bound_checks = 0
    no_repair_checks = 0
    dominated_checks = 0

    # Exhaust all 3-predicate / 3-action influence maps. Each action may affect
    # any subset of predicates. Costs include a tie to exercise non-strict dominance.
    predicates_n = 3
    actions_n = 3
    effect_options = tuple(subsets(predicates_n))
    costs = (1, 2, 2)

    for effect_tuple in product(effect_options, repeat=actions_n):
        effects = dict(enumerate(effect_tuple))
        influence_systems += 1
        for failed in subsets(predicates_n):
            if not failed:
                continue
            failure_systems += 1
            optimum, opt_sets = minimum_hitting_sets(actions_n, failed, effects, costs)

            # Corollary: hitting set exists iff every failed predicate has at least
            # one admissible ancestor, because selecting all actions is then feasible.
            empty_ancestor = any(
                not any(p in effects[a] for a in range(actions_n)) for p in failed
            )
            if (optimum is None) != empty_ancestor:
                errors.append(
                    f"no-repair certificate mismatch effects={effects} failed={failed}"
                )
                break
            no_repair_checks += 1

            if optimum is not None:
                # Every feasible repair must cost at least the exact hitting-set optimum.
                for selected in subsets(actions_n):
                    if hits_all(selected, failed, effects):
                        if cost(selected, costs) < optimum:
                            errors.append("minimum causal-coverage lower bound violated")
                            break
                        lower_bound_checks += 1
                if errors:
                    break

                # Theorem 3: for every dominated action a, at least one minimum
                # hitting set omits it when another action b covers a at no higher cost.
                for a in range(actions_n):
                    dominators = [
                        b
                        for b in range(actions_n)
                        if b != a
                        and effects[a] <= effects[b]
                        and costs[b] <= costs[a]
                    ]
                    if dominators:
                        if not any(a not in selected for selected in opt_sets):
                            errors.append(
                                f"dominated action unavoidable a={a} effects={effects} failed={failed}"
                            )
                            break
                        dominated_checks += 1
                if errors:
                    break
        if errors:
            break

    # Positive falsifier control: an action set that misses a failed predicate's
    # ancestors cannot cover it.
    effects = {0: frozenset({0}), 1: frozenset({1})}
    failed = frozenset({0, 1})
    misses_failed_predicate = not hits_all(frozenset({0}), failed, effects)
    if not misses_failed_predicate:
        errors.append("missed-ancestor positive control did not fire")

    # No-alarm control: selecting both actions covers both failed predicates.
    covers_both = hits_all(frozenset({0, 1}), failed, effects)
    if not covers_both:
        errors.append("ancestor-cover no-alarm control failed")

    # Identity boundary: mutations of load-bearing fields change the fingerprint;
    # a non-identity note does not enter the fingerprint by construction.
    base = {
        "question": "Does policy P meet gate G?",
        "population": "frozen-domain-v1",
        "estimand": "success_rate",
        "protocol_semantics": "v1",
        "primary_metric": "verified_success",
        "threshold": 0.8,
        "protected_corpus": "holdout-v1",
        "terminal_semantics": "PASS iff all hard gates pass",
        "note": "provenance only",
    }
    base_fp = identity_fingerprint(base)
    identity_fields = (
        "question",
        "population",
        "estimand",
        "protocol_semantics",
        "primary_metric",
        "threshold",
        "protected_corpus",
        "terminal_semantics",
    )
    identity_mutations_detected = 0
    for field in identity_fields:
        mutated = dict(base)
        mutated[field] = str(mutated[field]) + "__changed"
        if identity_fingerprint(mutated) == base_fp:
            errors.append(f"identity mutation not detected: {field}")
            break
        identity_mutations_detected += 1

    note_mutation = dict(base)
    note_mutation["note"] = "different non-identity provenance note"
    note_no_alarm = identity_fingerprint(note_mutation) == base_fp
    if not note_no_alarm:
        errors.append("non-identity note incorrectly changed identity fingerprint")

    report = {
        "status": "PASS" if not errors else "MISMATCH",
        "terminal": (
            "CLAIM_PRESERVING_CAUSAL_COVERAGE_PROVED__CROSS_DOMAIN_RECOVERY_UNTESTED"
            if not errors
            else "CANNOT_CHECK_RECOVERY_THEOREM_REGRESSION"
        ),
        "exhaustive_regression": {
            "predicates": predicates_n,
            "actions": actions_n,
            "influence_systems": influence_systems,
            "failure_systems": failure_systems,
            "feasible_repair_lower_bound_checks": lower_bound_checks,
            "no_repair_certificate_checks": no_repair_checks,
            "dominated_action_checks": dominated_checks,
        },
        "controls": {
            "missed_ancestor_detected": misses_failed_predicate,
            "complete_ancestor_cover_no_alarm": covers_both,
            "identity_field_mutations_detected": identity_mutations_detected,
            "nonidentity_note_no_alarm": note_no_alarm,
        },
        "errors": errors,
        "scientific_authority_delta": "NONE",
    }
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0 if not errors else 5


if __name__ == "__main__":
    raise SystemExit(main())

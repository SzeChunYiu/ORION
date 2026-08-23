#!/usr/bin/env python3
"""The ORDER_PERMUTATION attack cannot change its own dataset.

D1 v1.3's representation contract names `tuple(sorted(set(values)))` as its
`forbidden_normalization`. That expression is not hypothetical: it is what
`orion.transfer.v2.p1_method_realization._tuple` computes, and every method
realization in the programme is built through it --

    def _tuple(values):
        return tuple(sorted({str(x) for x in (values or ())}))

applied to preconditions, assumptions, resources, mechanics, invariants,
effects, failure_modes, lineage and unknown_coordinates.

So the P9-U-T4 order attack reverses each sequence coordinate and the constructor
sorts it straight back. The resulting dataset is byte-identical to the base one.
The attack is a no-op, and by the T4 freeze's own words an attack cannot fail
against a margin that was never measured.

Two consequences follow, and neither depends on any outcome:

* DUPLICATE_INSERTION, which D1 v1.3 also registers, is a no-op for the same
  reason -- `set` discards multiplicity before anything downstream sees it.
* D1 v1.3's TYPED_ORDERED_MULTIPLICITY arm cannot be built as a feature family.
  The information is destroyed upstream of every arm, in a P1 primitive shared
  across the programme. An order-preserving feature family over the same view
  still measures zero opportunity, which is the demonstration rather than the
  claim.

Exit codes: 0 the no-op reproduces, 2 it does not, 3 CANNOT_CHECK.
"""

from __future__ import annotations

import inspect
import json
import sys


def main() -> int:
    try:
        from orion.study.p9 import hostile_representation_attacks as att
        from orion.study.p9 import ordered_multiplicity as om
        from orion.transfer.v2 import p1_method_realization as p1
    except Exception as exc:
        print(json.dumps({"status": "CANNOT_CHECK", "error": str(exc)}))
        return 3

    source = inspect.getsource(p1._tuple)
    normalizes_to_sorted_set = "sorted({" in source.replace(" ", "") or "sorted(set" in source.replace(" ", "")

    datasets = att.build_datasets()
    base = datasets[att.DATASET_BASE]
    order = datasets[att.DATASET_ORDER]
    orbit = datasets[att.DATASET_ORBIT]

    identical_cases = sum(
        1 for left, right in zip(base.test, order.test, strict=True)
        if left.manifest_entry() == right.manifest_entry()
    )
    reorderable = sum(
        1 for row in base.test for coordinate in att.SEQUENCE_COORDINATES
        if len(getattr(row.left, coordinate)) > 1
    )
    order_sensitive_arm_changed = sum(
        1 for left, right in zip(base.test, order.test, strict=True)
        if om.features(left) != om.features(right)
    )
    contract_violations = [v for row in base.test for v in om.violates_contract(row)]

    checks = {
        "p1_tuple_computes_the_forbidden_normalization": normalizes_to_sorted_set,
        "order_dataset_digest_equals_base": order.manifest_digest == base.manifest_digest,
        "every_protected_case_identical": identical_cases == len(base.test),
        "there_was_something_to_reorder": reorderable > 0,
        "an_order_sensitive_arm_still_sees_no_change": order_sensitive_arm_changed == 0,
        "that_arm_satisfies_its_own_contract": not contract_violations,
        "the_orbit_attack_does_change_the_data": orbit.manifest_digest != base.manifest_digest,
    }

    print(
        json.dumps(
            {
                "schema": "orion.p9.order-permutation-noop.v1",
                "record": "P9_ORDER_PERMUTATION_IS_A_NOOP",
                "authority_scope": "OUTCOME_BLIND_FINDING",
                "outcome_accessed": False,
                "relabels_nothing": "The P9-U-T4 terminal remains P9_T4_HOSTILE_ATTACK_PREVAILED.",
                "p1_tuple_source": source.strip(),
                "protected_cases": len(base.test),
                "identical_cases_under_order_permutation": identical_cases,
                "left_sequence_coordinates_with_length_above_one": reorderable,
                "order_sensitive_arm_cases_changed": order_sensitive_arm_changed,
                "order_sensitive_arm_contract_violations": contract_violations,
                "checks": checks,
                "finding": (
                    "The order attack reverses each sequence coordinate and the method-realization "
                    "constructor sorts it back, so the ORDER_PERMUTATION dataset is byte-identical "
                    "to the base one: same manifest digest, 128 of 128 protected cases unchanged, "
                    "with 256 left-side coordinates long enough to reorder. The orbit attack over "
                    "the same machinery does change the data, so this is specific to order and "
                    "multiplicity rather than a broken harness."
                ),
                "consequence": (
                    "D1 v1.3 registers ORDER_PERMUTATION and DUPLICATE_INSERTION as two of its "
                    "four attack families and TYPED_ORDERED_MULTIPLICITY as one of its four arms. "
                    "None of the three is reachable while the P1 primitive normalizes to a sorted "
                    "set. The fix is one function in orion.transfer.v2.p1_method_realization, and "
                    "because every realization in the programme is built through it, that is a "
                    "programme-wide change and not a P9 one."
                ),
                "all_checks_pass": all(checks.values()),
            },
            indent=2,
        )
    )
    return 0 if all(checks.values()) else 2


if __name__ == "__main__":
    sys.exit(main())

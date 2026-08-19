# Zero-error Jump V2 expected amendment 001

Date: 2026-08-19

This amendment was made **after the V2 protocol/metric freeze but before the V2 runner repair existed and before any V2 protected outcome was accessed**.

A fairness audit identified that the fixed-representation arms must not use evaluator-side positive/control state to choose `KEEP_OLD_REGIME` versus `UNRESOLVED`. V2 requires those arms to select the same opaque registered probe from the public menu as every other non-oracle arm and use the resulting evidence:

- control outcome -> keep/repair/search inside the old representation;
- positive representation-pattern outcome -> recognize the ceiling but return unresolved because the arm cannot cross representation type.

Therefore their `thought_experiment_success` bookkeeping is corrected from `0` to `24` per split for:

- `OLD_DSL_EXHAUSTIVE`;
- `M_OPEN_SAME_REPRESENTATION`;
- `FIXED_REP_WORLD_MODEL`.

No seed, world family, representation move, protected consequence, control count, Jump success count, parent-vs-ORION equality, terminal or comparator resource budget changed.

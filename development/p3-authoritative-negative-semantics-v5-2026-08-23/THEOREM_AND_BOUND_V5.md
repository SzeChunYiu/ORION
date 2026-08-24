# P3 V5 direct-certificate theorem and bound

## Theorem schema

For any immutable byte-identical source/target ontology views satisfying the frozen namespace and direct-axiom rules, every canonical pair with exactly one certificate kind is point-identified; every pair with neither kind remains set-valued {GLUE, OBSTRUCTION}; and every pair with both kinds is excluded as CANNOT_CHECK_CONFLICT.

Define the information set of a canonical pair `p` by

- `I_C(p) = {GLUE}` when `p` has only an admitted direct GLUE certificate;
- `I_C(p) = {OBSTRUCTION}` when `p` has only an admitted direct OBSTRUCTION certificate;
- `I_C(p) = {GLUE, OBSTRUCTION}` when `p` has neither certificate; and
- `CANNOT_CHECK_CONFLICT` when both certificate kinds occur.

This yields two general properties: conflict-free certificate addition is a monotone refinement of information sets, and absence can never manufacture obstruction.

## Observed V5 instantiation

The unchanged three-family gate passes **3/3**. The finite direct-certificate domain contains **4,838** point-identified pairs: **4,789 GLUE** and **49 explicit OBSTRUCTION**, with **0 conflicts**.

## Sharp bound

Binary truth is point-identified on the finite direct-certificate set. Every pair outside that set remains set-valued unless separately certified.

This is a reusable calibration theorem, not Cartesian exhaustivity, naturalistic cross-ontology transport, comparator performance, V3 harm reversal, or protected confirmation.

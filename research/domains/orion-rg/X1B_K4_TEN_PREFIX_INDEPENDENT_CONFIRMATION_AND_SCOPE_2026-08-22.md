# X1-B k=4 — independent ten-prefix confirmation and claim-scope correction

Parent: #900.
Primary exact search: `x1b_k4_ten_prefix_forbidden_sum_exact.cpp`.
Independent verifier: `x1b_k4_ten_prefix_forbidden_sum_nomemo.cpp`.

## Independent confirmation

The no-memo verifier completed exhaustively with a different canonical element order and no hash/state quotient:

- canonical multiset nodes: **20,686,105**;
- length-10 admissible prefix: **NONE**;
- maximum length: **9**.

It therefore independently confirms the finite theorem for the frozen seven-point forbidden set.

One independently found length-9 witness is

```text
(0,0,1),
(4,4,0)^4,
(2,4,0),
(4,4,1)^3.
```

The primary and independent implementations use different traversal strategies and different maximum-length witnesses while agreeing on the terminal maximum 9.

## Critical claim-scope correction

This finite theorem applies to the **specific common rank-2 residual lift** committed in `X1B_K4_RANK2_RESIDUAL_LIFT_OBSTRUCTION_2026-08-22.md`, whose three residual block-sum pair types induce the frozen forbidden set.

It does **not by itself eliminate the two quotient orbits** `942777` and `1470123`, because the affine bilinear spaces admit other rank<=3 completions/factorizations. An actual C15 counterexample could in principle use a different residual kernel lift and therefore a different forbidden-prefix set.

Accordingly:

- `MAX_PREFIX_LENGTH_9_FOR_COMMON_RANK2_WITNESS` is independently confirmed;
- `K4_RESIDUAL_CLOSED` is **not** yet authorized;
- the earlier language suggesting that this single NO would eliminate both quotient orbits is superseded by this scope correction.

## Correct successor

Enumerate **all** rank<=3 symmetric completions of the two surviving quotient affine spaces under the already frozen global bilinear equations. For each completion:

1. factor it through a symmetric bilinear space of dimension <=3;
2. retain all residual lifts that are themselves zero-sum-free in C15;
3. compute the induced set of residual block-sum pair types;
4. derive the exact forbidden-prefix subset-sum set;
5. decide ten-prefix existence by the independently confirmed finite method, quotienting only sound congruence/permutation equivalences.

Only closure of every lift class can eliminate the quotient orbit.
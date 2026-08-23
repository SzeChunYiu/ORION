# X1-B k=4 — R3-10 exact ten-prefix primary result

Parent: #900.
Protocol: `X1B_K4_RANK3_FORBIDDEN_PREFIX_PROTOCOL.md`.
Exact state quotient: `X1B_K4_FORBIDDEN_PREFIX_ILLEGAL_STATE_QUOTIENT_2026-08-22.md`.
Dominance: `X1B_K4_FORBIDDEN_PREFIX_MINLAST_DOMINANCE_2026-08-22.md`.
Implementation: `x1b_k4_rank3_forbidden_prefix_exact.cpp`.

## Evidence status

**PROSPECTIVE PRIMARY EXACT ENUMERATION.** The success criterion and the R3-10 forbidden set were frozen before this run. Per the frozen protocol, an independent replay remains required before using the NO as theorem evidence.

## Exact layer census

Using the canonical lexicographic ordering of the 124 nonzero elements of `F_5^3`, the layerwise minimum-last DP produced:

```text
depth 0:          1 state
depth 1:        115 states
depth 2:      6,127 states
depth 3:    184,946 states
depth 4:  2,971,826 states
depth 5: 13,923,384 states
depth 6:  5,139,775 states
depth 7:    398,428 states
depth 8:     13,163 states
depth 9:          1 state
depth 10:         0 states
```

Total generated legal transitions:

`71,604,156`.

## Result

There is **no** ten-term sequence `T` over `F_5^3` whose every nonempty subset sum avoids the canonical R3-10 forbidden set.

The maximum achievable length is exactly **9**.

Thus, subject to independent confirmation, all 12 rank-3 bilinear completions belonging to class R3-10 are eliminated from the k=4 C15 counterexample interface.

## Authority boundary

- This result is finite and exact for R3-10.
- It does not yet eliminate R3-11, R3-12, or the rank-2 radical realization family.
- It does not by itself close the k=4 residual or prove `D(C_15^3)=43`.
- No novelty authority is granted.

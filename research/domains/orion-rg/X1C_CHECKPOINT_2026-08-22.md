# ORION-RG X1-C checkpoint — 2026-08-22

Parent: #901. Umbrella: #896 / #899. Branch: `shadow/orion-rg-rg0-finite-regime-geometry`.

## Purpose

Durable checkpoint before further research. This file records only findings already obtained and corrected. It grants no theorem, novelty, adoption, or merge authority.

## Live target

The live unresolved calibration is

`D(C_45^3) ?= 133`.

Projection `C_45^3 -> C_3^3` has kernel `C_15^3`. Donor inputs give `D(C_15^3)=43` and, for `k>=3`, `D_k(C_3^3)=3k+6`. Hence

- `D_42(C_3^3)=132`;
- `D_43(C_3^3)=135`;
- a hypothetical zero-sum-free length-133 sequence supplies at least 42 disjoint quotient zero-sum blocks, while ordinary induction needs 43 kernel block sums;
- therefore the projection route is exactly one effective block short;
- classical induction yields `133 <= D(C_45^3) <= 135`.

The strong programme target remains an infinite-family result for `C_(3^a5^b)^3`, not a single constant.

## Donor absorptions / refutations already established

1. **C15 is donor-owned.** Current literature records rank-3 homocyclic equality for `n=3 p^k`, so `D(C_15^3)=43` is not an ORION discovery. Issue #900 was closed/superseded and retained as known-answer calibration.

2. **Ordinary sharp multi-wise induction is structurally impossible.** Freeze--Schmid Theorem 4.1 gives, for odd prime `p`,

   `D_k(C_p^3) >= p k + 5(p-1)/2`,

   whereas a direct exact induction would need intercept `2p-2`. Thus ordinary `D_k` is too strong a state variable for the desired sharp odd-prime induction.

3. **The 2026 global bound is absorbed.** Grinsztajn proves

   `D(C_n^3) <= 4n - P(n) - 2`.

   It is the current strong homocyclic rank-3 upper-bound route, but it does not settle C45.

4. **Fresh missing-sum invariants are donor-owned concepts.** Geroldinger--Yang introduce `nu(G)` / `nu_p(G)` to control missing subsequence sums of near-maximal zero-sum-free sequences. They prove sharp p-group results, but these cannot be imported directly to the mixed kernel `C_15^3`.

5. **The old scalar-lift deficiency-one argument is donor-owned.** Bhowmik--Schlage-Puchta already work at the `3d+4` projected-term layer for `Z_3^3` when the lift is scalar/cyclic. C45 has a rank-3 mixed kernel, so any new result must survive comparison with that method rather than rebrand it.

## Corrected C3^3 extremal reduction

An earlier stronger claim was withdrawn. From `D_k(C_3^3)=3k+6` one can force a length-3 atom in a `D_k` extremal only while the average atom length is strictly below 4. Therefore the valid recursive stripping runs from `k=12` down through `k=7`, yielding

`B_12 = U_1 ... U_6 B_6`,

where each `|U_i|=3`, `|B_6|=24`, and `max L(B_6)=6`.

At `k=6`, average atom length may equal 4, so a further length-3 factor is not forced. Any earlier claim of automatic reduction to a 15-term `D_3` core is invalid and must not be reused.

## Stronger donor classification now absorbed

Bhowmik--Schlage-Puchta Proposition 8 gives a complete description of **maximum-cardinality** `C_3^3` sequences failing `k` disjoint zero sums. This supersedes treating the 42-term maximum-failing quotient layer as an unstructured inverse problem.

The live C45 quotient has length 133 at `k=43`, one below the maximum failing layer of length 134. Therefore the next mathematical residual is a **deficiency-one stability / lift-compatibility problem**, not classification of the maximum layer itself.

## Current breakthrough residual

Determine the structure of 133-term sequences in `C_3^3` that fail to contain 43 disjoint zero sums **together with** the constraints imposed by lifting their quotient-zero-sum blocks into a maximal zero-sum-free sequence of length 42 in `C_15^3`.

Candidate high-value routes, in priority order:

1. prove a deficiency-one stability theorem relative to the Proposition-8 extremals;
2. prove mixed-kernel missing-subsequence-sum geometry for maximal/near-maximal zero-sum-free sequences in `C_15^3` (for example an exact `nu_3` or `nu_5` result);
3. prove a lift-compatible block-exchange lemma that repairs the one-block deficit without requiring the full mixed-kernel invariant;
4. find and independently verify a structural obstruction that kills these routes and identifies the next state coordinate.

## Authority boundary

- No finite computation implies `D(C_45^3)=133`.
- No C45 theorem implies the infinite `3^a5^b` family.
- Donor theorem names/invariants above receive zero novelty credit.
- Every further material finding is to be committed before downstream use.

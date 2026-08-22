# ORION-RG X1-C findings ledger — 2026-08-22

Branch: `shadow/orion-rg-rg0-finite-regime-geometry`
Primary issues: #894, #895, #896, #899, #901
Superseded known-answer calibration: #900

This ledger is append-only in substance: corrections are recorded explicitly rather than rewriting history. None of the entries below grants novelty/scientific authority by itself.

## F1 — generic finite-regime theory donor strikes

- Fixed-matrix integer-program objective geometry generated from move/test directions is already classical Gröbner/Graver territory; it cannot be an ORION headline theorem without a stronger native-semantics result.
- Stabilization of bounded-type Graver moves in growing n-fold systems is also classical n-fold IP machinery.
- Finite integer index / protrusion-replacement and related CMSO strong-monotonicity/separability already formalize continuation-equivalence style replacement in broad bounded-interface graph settings.
- Resulting RG-1 reframe: the interesting object is not defining continuation equivalence, but deriving a sufficient exact finite/lifted representation from native scientific semantics without assuming the bounded-interface representation.

## F2 — rank-3 Davenport target refresh

- The Heisenberg small-Davenport targets moved too quickly to be suitable primary targets; the programme moved to the long-standing rank-3 abelian Davenport problem.
- A fresh 2026 result by Max Grinsztajn proves `D(C_n^3) <= 4n - P(n) - 2`, where `P(n)` is the largest prime-power component. This is now the incumbent global homocyclic rank-3 upper-bound route and must be absorbed.
- The ordinary sharp multi-wise induction idea is structurally impossible: Freeze--Schmid Theorem 4.1 gives, for odd prime p, `D_k(C_p^3) >= p k + 5(p-1)/2`, strictly above the ideal intercept `2p-2` needed for a one-step exact `3pm-2` induction.
- Therefore the exact induction, if it exists, needs a weaker lift-compatible obligation than arbitrary k disjoint quotient zero-sums.

## F3 — target family selection and donor closure of C15

- Frozen family target: `D(C_(3^a 5^b)^3)=3*3^a*5^b-2` for `a,b>=1` (#899).
- Hostile literature review subsequently found that `D(C_n^3)=3n-2` is already known for `n=3 p^k`; in particular `D(C_15^3)=43` is donor-owned.
- Issue #900 was closed as `not_planned`/donor-owned rather than being repackaged as a discovery.
- The first live unresolved target in the frozen family is therefore `C_45^3`; this is issue #901.

## F4 — exact one-block deficit for C45

Use `pi:C_45^3 -> C_3^3`, with kernel `K=C_15^3`.

Donor inputs:
- `D(K)=D(C_15^3)=43`;
- Freeze--Schmid: `D_0(C_3^3)=6`, `k_D(C_3^3)=3`, hence `D_k(C_3^3)=3k+6` for all `k>=3`.

Arithmetic consequences:
- `D_42(C_3^3)=132`;
- `D_43(C_3^3)=135`;
- a hypothetical zero-sum-free sequence of length `133` over `C_45^3` guarantees 42 disjoint quotient zero-sum blocks but ordinary induction needs 43 kernel block sums.

Thus the C45 target is exactly one effective block short and the classical induction gives `133 <= D(C_45^3) <= 135`.

For every 42-block packing in a hypothetical counterexample, the 42 lifted block sums form a zero-sum-free sequence of maximum possible length in `K=C_15^3`, because `d(K)=42`.

## F5 — mixed-kernel subsequence-sum geometry

- Geroldinger--Yang (Aug 2026, arXiv:2608.19090) introduce/refine `nu(G)` / `nu_p(G)` through missing subsequence-sum geometry of near-maximal zero-sum-free sequences.
- Their sharp p-group result cannot be imported to `K=C_15^3`, which is mixed-primary rank three.
- This makes exact/partial determination of `nu_3(C_15^3)` and/or `nu_5(C_15^3)` a legitimate structural subtarget of #901, subject to continuing donor review.
- If a sharp `nu_p(K)=41`-type statement holds, deleting one term from a maximal length-42 zero-sum-free kernel sequence traps nonrepresentable correction values in an affine coset of an index-p subgroup. A one-block exchange would then only need to escape that coset.

## F6 — inverse multi-wise quotient reduction

- Freeze--Schmid define `D_k(G)` equivalently as the maximum length of a zero-sum sequence `B` with `max L(B)<=k`.
- Therefore a length-42 quotient object at `D_12(C_3^3)=42` is not impossible; it is an extremal boundary object. The earlier easy attempt to rule out lower-order terms in a maximal `C_15^3` atom via quotient length alone fails.
- The surviving object is an inverse-lifting question: characterize which `D_12(C_3^3)` extremals admit the required mixed-primary lifts.

## F7 — CORRECTION: forced length-3 stripping stops at k=6

An earlier exploratory statement claimed that every `D_12(C_3^3)` extremal could be stripped into nine length-3 atoms plus a 15-term `D_3` core. This is too strong and is withdrawn.

Correct argument:
- for an extremal `B_k` with `|B_k|=D_k(C_3^3)=3k+6` and `max L(B_k)=k`, choose a factorization of length k;
- when `k>=7`, average atom length is `(3k+6)/k = 3+6/k < 4`, so the factorization contains an atom of length 3;
- Proposition 3.1 then gives a remainder with `max L<=k-1`; because its length is `D_k-3 = D_{k-1}`, it is itself extremal with `max L=k-1`;
- this repeats for `k=12,11,10,9,8,7` and stops at `k=6`, where the average atom length can equal exactly 4.

Thus the rigorously forced decomposition is

`B_12 = U_1 U_2 U_3 U_4 U_5 U_6 B_6`,

where each `|U_i|=3`, `|B_6|=24`, and `max L(B_6)=6`.

No further length-3 atom in `B_6` is currently justified.

## Current live residual

The quotient inverse problem has been reduced from arbitrary 42-term `D_12` extremals to a 24-term `D_6(C_3^3)` extremal core plus six forced length-3 atoms. The next tasks are:

1. determine whether the `D_6(C_3^3)=24` extremal core is already structurally classified;
2. if not, derive a finite exact obstruction atlas for `B_6` under automorphisms/factorizations;
3. couple that quotient-core structure to lift sums in `C_15^3`, especially lower-order terms and `nu_p` missing-sum geometry;
4. freeze any new exchange/normalization lemma before testing it on the complete bounded atlas.

## Claim boundary

Everything above is donor binding, arithmetic consequence, refutation, or prospective reduction. No rank-3 theorem, C45 theorem, infinite-family theorem, or novelty authority is claimed here.

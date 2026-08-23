# X1-F0 theorem reduction — D2(C_5^3)=20 iff every 21-term zero-sum sequence has a zero-sum subsequence of length <=7

Date: 2026-08-22
Branch: `shadow/orion-rg-rg0-finite-regime-geometry`
Parent issue: #916

## Theorem-equivalence

Let `G=C_5^3`. The following are equivalent.

1. `D_2(G)=20`.
2. Every zero-sum sequence `B` over G with `|B|=21` contains a nonempty proper zero-sum subsequence of length at most 7.
3. There is no zero-sum sequence `B` of length 21 all of whose nonempty proper zero-sum subsequences have lengths in `[8,13]`.

The lower bound `D_2(G)>=20` is donor-owned (Freeze--Schmid), so it suffices to prove `D_2(G)<=20`.

## Proof: (1) => (2)

Assume `D_2(G)=20` and let B be zero-sum with `|B|=21`.

Since 21>=D_2(G), B contains two pairwise-disjoint nonempty zero-sum subsequences. Because B itself is zero-sum, any unused complement is also zero-sum and may be merged into either selected block. Thus B has a factorization into at least two nonempty zero-sum blocks; refining into atoms gives a factorization into atoms.

More directly, suppose B had no proper zero-sum subsequence of length <=7. Any atom over G has length at most `D(G)=13`. A factorization of B into at least three atoms would have total length 21, so its shortest atom would have length at most floor(21/3)=7, contradiction. Hence `max L(B)<=2`, so B would lie in `M_2(G)` with length21, contradicting `D_2(G)=20` via the donor characterization `D_2=max{|B|:B in M_2}`.

Therefore B has a proper zero-sum subsequence of length <=7.

## Proof: (2) => D2<=20

Suppose (2) holds but `D_2(G)>20`. By the elementary distinguished-term/zero-sum-monoid correspondence, there exists a zero-sum sequence B of length21 with `max L(B)<=2`.

By (2), B has a nonempty proper zero-sum subsequence Z with `|Z|<=7`.

The complement `R=B Z^(-1)` is nonempty and zero-sum, with

`|R|=21-|Z| >=14`.

Since `D(G)=13`, R cannot be an atom; therefore R factors into at least two nonempty atoms. Factoring Z into at least one atom and adjoining the factorization of R gives a factorization of B of length at least3, contradiction.

Thus `D_2(G)<=20`. Combined with the donor lower bound, `D_2(G)=20`.

## Equivalent interval form for proper zero sums

If a length21 zero-sum B lies in `M_2`, every nonempty proper zero-sum subsequence Z has atom complement and hence both lengths <=13. Therefore

`8 <= |Z| <=13`.

Conversely, if every proper zero-sum subsequence has length in `[8,13]`, B cannot factor into 3 atoms because the shortest atom in any 3-factorization has length <=7. Hence B is in M2.

So a length21 obstruction is exactly a global zero-sum sequence with a **short-zero-sum gap** on lengths1--7.

## Research significance

This replaces the broad two-disjoint-packing search by a single-subsequence theorem under a global sum constraint:

> prove that `sigma(B)=0` and `|B|=21` force a zero-sum subsequence of length at most7 in `C_5^3`.

This formulation directly interfaces with short-zero-sum methods (Chevalley--Warning/polynomial identities, Property C/D, cap structure, congruence counts) and may admit a human proof even if generic MILP search is expensive.

## Claim boundary

`D(C_5^3)=13`, the k-wise monoid characterization, and the lower bound `D_2>=20` are donor mathematics. The equivalence is an elementary reduction recorded for the research programme; no exact D2/novelty authority is claimed until condition (2) is proved independently.
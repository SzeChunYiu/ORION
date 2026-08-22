# X1-B theorem — complete closure of the C15 k=4 / 13-point residual

Parent: #900.
Status: **CANDIDATE FINITE-COMPUTATIONAL THEOREM CHAIN — committed before use in the C15 proof assembly.**

This packet assembles previously committed donor-derived lemmas and independently replayed finite classifications. It does not add a new search outcome. Its purpose is to verify that every possible k=4 residual branch has been exhausted before the result is used downstream.

## 1. Residual setup

Assume for contradiction that a zero-sum-free sequence S of length 43 exists in

`C_15^3 ≅ C_3^3 direct-sum C_5^3`.

After greedily removing ten disjoint quotient-zero-sum triples from the `C_3^3` projection, the k=4 branch leaves a 13-position quotient residual A with no nonempty quotient zero-sum of length at most 3.

The ten removed triples have fixed lifted sums

`t_1,...,t_10 in C_5^3`.

To avoid the ordinary 13-block contradiction, A must have packing number exactly 2: it contains two disjoint nonempty quotient zero sums but no three.

This is the k=4 interface frozen and enumerated in the committed 13-point residual protocol.

## 2. Complete quotient-orbit classification

The prospectively frozen full-multiplicity enumeration over `F_3^3`, quotiented by the complete `GL(3,3)` action and replayed from primitive position addition, found exactly **15** canonical 13-position residual orbits with:

- no quotient zero-sum of length <=3; and
- packing number exactly 2.

The first local-scalarization discriminator closes **9** of them: some pair-compatible anchor has an inconsistent common-RHS `F_5` scalar system.

Exactly **6** quotient orbits survive that necessary condition.

The one-functional strategy is therefore not assumed sufficient; the six exact obstructions were serialized and carried forward.

## 3. Global two-extension bilinear form

Fix the ten removed triple sums T. The donor-derived group-algebra coefficient identity defines one symmetric matrix

`M_T in Sym_3(F_5)`

such that for **every** disjoint residual quotient-zero-sum pair `(Z,W)`:

`z_Z^T M_T z_W = 1`,

where `z_Z` is the sum of the original residual kernel coordinates over Z.

Therefore every genuine residual lift induces a symmetric 13x13 position matrix

`B[j,k]=y_j^T M_T y_k`

with:

- `rank(B) <= 3`; and
- every disjoint-zero-sum edge equation equal to 1.

This is a necessary relaxation of a genuine C15 lift, so infeasibility eliminates a quotient orbit a fortiori.

## 4. Four of six obstruction orbits die linearly

The prospectively frozen affine edge-system computation for the six quotient obstructions gives:

- **4** orbits: the linear symmetric-matrix system itself is inconsistent;
- **2** orbits survive: canonical codes `942777` and `1470123`.

Thus no kernel realization of any rank exists for the four inconsistent orbits.

Only those two exact quotient orbits require nonlinear/rank realization analysis.

## 5. Complete rank<=3 completion census for the final two quotient orbits

For each of the two affine symmetric-matrix spaces, all rank<=3 completions were enumerated exactly using the committed principal-basis/Schur-complement characterization.

Results:

- `942777`: 57 completions = 1 rank-2 + 56 rank-3;
- `1470123`: 61 completions = 1 rank-2 + 60 rank-3;
- no rank-1 completion exists.

The unique rank-2 completion is the same position Gram matrix for both quotient orbits.

Hence the complete bilinear-realization universe consists of:

- **116 rank-3 completions**; and
- one rank-2 Gram type with a possible one-dimensional radical coordinate on each original residual position.

No other rank<=3 completion is omitted.

## 6. Complete elimination of all 116 rank-3 completions

Every rank-3 completion has a zero-sum-free 13-term residual lift under its canonical minimal factorization.

For a fixed residual lift, simultaneous zero-sum-freeness of the ten-prefix T with every residual pair extension is exactly equivalent to requiring every nonempty subset sum of T to avoid an associated forbidden set in `F_5^3`.

The 116 completions collapse under exact `GL(3,5)` canonicalization to exactly three forbidden-set classes:

- R3-10, covering 12 completions;
- R3-11, covering 40 completions;
- R3-12, covering 64 completions.

For each class the prospectively frozen exact layerwise enumeration proves maximum admissible prefix length **9**, not 10.

An algorithmically independent verifier using direct `Sigma_0(T)` recursion, no memoization, no layerwise DP and no minimum-last dominance reproduces the same NO/max-9 result for all three classes.

Therefore:

> **No rank-3 completion of either final quotient orbit admits the required ten-prefix.**

All 116 rank-3 realization branches are eliminated.

## 7. Complete elimination of the rank-2 radical family

The rank-2 Gram matrix fixes two base coordinates of each of the 13 residual kernel vectors but is blind to one radical scalar `r_j in F_5` per position.

The committed exact normalization uses:

1. a kernel shear to set `r_0=r_1=0`; and
2. radical scaling to make the first nonzero remaining radical coordinate equal to 1.

This gives exactly

`12,207,032`

normalized assignments per quotient orbit, hence `24,414,064` normalized radical realizations in total.

### Complete forbidden-signature census

Exact enumeration gives:

- orbit `942777`: 6,620 distinct forbidden signatures, 574 inclusion-minimal;
- orbit `1470123`: 5,776 distinct signatures, 597 inclusion-minimal;
- union: 8,984 distinct signatures, **639 inclusion-minimal**.

For monotonicity: if forbidden set A is contained in B, a NO for A implies a NO for B.

Exact `GL(3,5)` containment testing shows:

- 418 of the 639 minima contain a linear image of the independently closed seven-point planar obstruction;
- 218 additional minima contain a linear image of independently closed R3-10;
- only 3 raw minima remain.

The two 11-point raw minima are linearly equivalent, so the entire unresolved radical universe reduces to exactly two new classes:

- R2R-11;
- R2R-12.

### Final two exact prefix problems

Prospectively frozen primary exact enumeration gives:

- R2R-11: max prefix length 9, no length 10;
- R2R-12: max prefix length 9, no length 10.

A fresh independent verifier carries `Sigma_0(T)` directly and uses no memoization, no state merging and no minimum-last dominance. It confirms:

- R2R-11: 79,487,138 canonical nodes, max 9, NO;
- R2R-12: 54,683,021 canonical nodes, max 9, NO.

Therefore:

> **No rank-2 radical realization admits the required ten-prefix.**

The entire rank-2 branch is eliminated.

## 8. Exhaustion conclusion

Every k=4 residual possibility belongs to exactly one branch in the following exhaustive tree:

```text
15 quotient orbits
  -> 9 closed by anchored local scalarization
  -> 6 exact obstructions
       -> 4 closed by global affine bilinear inconsistency
       -> 2 final quotient orbits
            -> every rank<=3 completion enumerated
                 -> 116 rank-3 completions: independently closed
                 -> rank-2 radical family: completely normalized/censused,
                    reduced to two final classes, independently closed
```

A genuine C15 counterexample would have to pass every necessary gate in this tree. No terminal leaf survives.

Hence:

> **The k=4 / 13-point residual of a hypothetical length-43 zero-sum-free sequence over `C_15^3` is impossible.**

Equivalently, under the admitted donor lemmas and the independently replayed finite classifications, the k=4 residual branch is closed.

## 9. What this does and does not prove

This packet does **not yet** claim the full theorem `D(C_15^3)=43` because:

- the separate k=3 / 10-point branch must still receive its final canonical harness/independent evidence admission;
- the entire proof chain must be hostile-audited for donor statement accuracy, symmetry completeness, and interface correctness;
- current literature must be rechecked before any novelty claim.

It does establish a complete candidate closure of the harder k=4 finite interface and may now be used as one input to the full C15 proof assembly.
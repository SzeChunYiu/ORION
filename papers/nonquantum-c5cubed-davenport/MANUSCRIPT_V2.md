# A One-Unit Generalized-Davenport Corridor with a Rank-Forcing Obstruction Phase in `C_5^3`

**Non-quantum paper — hardened manuscript V2**
Scientific cut: M1–M3 theorem parents, support-frontier boundary, and R2 symbolic compression
Workflow cut: `academic-paper-skills@188e83e639571c435344630ae68fdc66072650d2`

## Abstract

Let `D_k(G)` be the least length forcing `k` pairwise disjoint nonempty zero-sum subsequences. For `G=C_5^3`, exact early constants and donor recurrences confine every later generalized Davenport constant to a width-one corridor:

`5k+10 <= D_k(C_5^3) <= 5k+11` for every `k>=4`.

If the unresolved value is `D_4(C_5^3)=30`, then the lower line is exact for every `k>=2`. An upper-line extremal would yield a total-zero sequence `S` of length 31 with no nonempty zero-sum subsequence of length at most five. We combine three established ingredients: a general odd-prime saturation-defect lemma; exact internal replay excluding support at most ten; and a larger bounded support frontier through 22 whose metadata explicitly withholds theorem authority pending external replay.

The present hardening adds two symbolic compression results. In every saturated length-31 obstruction, multiplicity three is absent. If `s=|supp(S)|` and `c_i` counts multiplicity `i`, then

`c2=31-s-3c4`, `c1=2s-31+2c4`.

The subsequence formed by points of multiplicity at least two has length

`62-2s-2c4`.

Since `eta(C_5^2)=13`, this high-multiplicity stratum is forced to span rank three precisely throughout the rank-forcing region

`s+c4<=24`.

At support 23, the branches with `c4=0,1` are therefore automatically rank three, whereas the `c4=2` branch is the first branch not normalized by this donor threshold. This identifies the exact symbolic phase where the existing mixed-basis search ceases to be automatic.

Second, for any occurrence-disjoint atom factorization `S=U_1...U_r`, with `r_g` the number of atom supports containing `g`,

`31-s = sum_i(|U_i|-|supp(U_i)|)+sum_g(r_g-1)`.

Under the conditional four-atom types `(6,6,6,13)` or `(6,6,7,12)`, a support-at-least-23 extremal has total internal repetition plus cross-atom overlap budget at most eight. This couples the support and factorization grammars and gives a more principled next search than another unstructured support row.

`D_4(C_5^3) remains 30/31`; exact `D_4(C_5^3)` and `31 in C_0(C_5^3)` remain open. The paper is therefore a rigorous specialist manuscript with a sharper conceptual frontier, not yet a completed top-tier extremal theorem.

## 1. Introduction

Generalized Davenport constants measure how much sequence length is required to force several disjoint zero sums. Rank-two groups are highly structured; rank-three groups can depart from the expected eventual arithmetic progression.

For `C_5^3`, the registered exact values

`D_2=20`, `D_3=25`

and the short-zero-sum thresholds reduce the next value to

`D_4 in {30,31}`.

This is not an isolated numerical ambiguity. If `D_4=30`, every later value is forced to `5k+10`. Thus a single extremal bit controls an infinite exact tail.

The hypothetical upper-line object is equally rigid: a length-31 total-zero 5-short-free sequence. Earlier work attacked it by saturation, multiplicity patterns, rank normalization, and exact subset-sum reachability. The current manuscript asks where those symbolic normalizations are genuinely forced and how they interact with the four-atom factorization of a generalized-Davenport extremal.

### 1.1 Contributions

1. Width-one corridor for every `k>=4`.
2. Conditional exact tail if `D_4=30`.
3. General odd-prime saturation-defect lemma and exclusion of multiplicity `p-2`.
4. Exact theorem-grade support-at-least-eleven result from the M2/M3 parent package.
5. Exact multiplicity parameterization for every remaining support.
6. Rank-forcing phase `s+c4<=24` for the high-multiplicity stratum.
7. Atom repetition/overlap budget identity coupled to the conditional four-atom types.
8. Explicit separation between theorem-grade results, bounded computation, and open `D_4` authority.

## 2. Donor and registered inputs

The recurrence and lower framework are due to Freeze and Schmid. In the notation `s_{<=l}(G)`,

`D_{k+1}(G)<=max{D_k(G)+l,s_{<=l}(G)-1}`.

The specialized lower bound gives `D_k(C_5^3)>=5k+10` in the range used here. Registered exact inputs are

`D_2=20`, `D_3=25`, `s_{<=6}=24`,

and the classical exponent-five threshold is `s_{<=5}=eta(C_5^3)=33`.

Fan, Gao, Wang, Zhong and Zhuang define `C_0(G)` and prove relevant localization results; their framework owns the formulation of the exact length-31 short-zero-sum target. Property C and rank-two short-zero-sum constants are donor inputs.

## 3. Width-one tail

Using `l=6`,

`D_4<=max{25+6,24-1}=31`.

Together with the lower bound, `D_4 in {30,31}`.

**Theorem 1.** For every `k>=4`,

`5k+10<=D_k(C_5^3)<=5k+11`.

**Proof.** The base upper value is `D_4<=31`. Apply the recurrence with `l=5` and fixed threshold 32. If `D_k<=5k+11`, both terms are at most `5(k+1)+11`. The lower line is donor-owned. ∎

**Theorem 2.** If `D_4=30`, then `D_k=5k+10` for all `k>=2`.

The proof uses the same recurrence and lower bound. No upper-line propagation theorem is claimed from `D_4=31`.

## 4. The obstruction and saturation

A hypothetical `D_4=31` extremal yields a sequence `S` over `C_5^3` with

`|S|=31`, `sigma(S)=0`,

and no nonempty zero-sum subsequence of length at most five.

Multiplicities are at most four. In the support-greater-than-eight branch, the Property-C extension dichotomy forces saturation.

**Theorem 3 (saturation defect).** Let `p` be odd and `S` a saturated `p`-short-free sequence over an elementary abelian exponent-`p` group. If nonzero `x` has multiplicity `m<p`, then there is a subsequence `R` with

`|R|<=p-1-m`, `x notin supp(R)`,

and

`sigma(R)=-(m+1)x`.

The proof observes that a saturation witness for appending `x` must use every existing copy of `x`; otherwise one unused copy creates a short zero sum already inside `S`.

**Corollary 4.** Multiplicity `p-2` is impossible. For `p=5`, multiplicity three is absent.

Singleton and double points therefore carry certificates of sizes at most three and two, respectively.

## 5. Exact multiplicity grammar

Let `s=|supp(S)|`, and let `c_1,c_2,c_4` count points of multiplicities one, two, and four. Then

`c_1+c_2+c_4=s`,

`c_1+2c_2+4c_4=31`.

Solving for a chosen `c_4=j` gives

`c_2=31-s-3j`,

`c_1=2s-31+2j`.

Hence `c_1` is odd and the complete admissible range is determined by nonnegativity. This parameterizes every support stratum without case guessing.

For support 23 the three patterns are

`1^15 2^8`,

`1^17 2^5 4`,

`1^19 2^2 4^2`.

For support 24 they are

`1^17 2^7`,

`1^19 2^4 4`,

`1^21 2 4^2`.

## 6. Rank-forcing phase transition

Let `H` be the high-multiplicity subsequence consisting of all points with multiplicity two or four. Its length is

`|H|=2c_2+4c_4`

`   =62-2s-2c_4`.

If `H` were contained in a rank-at-most-two subgroup, it would be a 5-short-free sequence over `C_5^2`. The donor value `eta(C_5^2)=13` forces every such sequence of length at least 13 to contain a short zero sum. Since `|H|` is even, contradiction occurs exactly when `|H|>=14`.

**Theorem 5 (rank-forcing phase).** The high-multiplicity stratum is forced to span rank three whenever

`s+c_4<=24`.

**Proof.** `|H|>=14` is equivalent to `62-2s-2c_4>=14`, hence `s+c_4<=24`. ∎

This theorem explains the normalization boundary:

- support 23, `c_4=0,1`: rank three forced;
- support 23, `c_4=2`: the rank-two threshold alone is silent;
- support 24, only `c_4=0`: rank three forced;
- support 25 and above: no branch is forced by this high-stratum threshold alone.

The complement is a statement about proof reach, not existence: outside the region, rank three may still hold for another reason.

## 7. Exact low-support theorem and bounded frontier

The signed M2/M3 package combines symbolic reductions with independent exact state representations to exclude support through ten.

**Theorem 6.** Every length-31 total-zero 5-short-free sequence over `C_5^3`, if one exists, has support at least eleven.

A larger internally replayed packet reports no solutions through support 22 and the bounded conclusion support at least 23. Its own authority metadata states `theorem_authority=false` and `external_replay_required=true`. This manuscript does not promote it.

The rank-forcing phase identifies exactly which support-23/24 branches reuse theorem-backed mixed-basis normalization and which require a new invariant or a separately complete orbit argument.

## 8. Four-atom factorization and the overlap budget

Under the conditional assumption `D_4=31`, extremal factorization arguments force one of two atom-length types:

`(6,6,6,13)` or `(6,6,7,12)`.

Let `S=U_1...U_r` be an occurrence-disjoint atom factorization. For each group element `g`, let `r_g` be the number of atom supports containing `g`.

Define internal deficit of atom `U_i` as

`delta_i=|U_i|-|supp(U_i)|`.

**Theorem 7 (atom repetition/overlap identity).** For every occurrence-disjoint factorization,

`|S|-|supp(S)| = sum_i delta_i + sum_{g in supp(S)}(r_g-1)`.

**Proof.** Summing atom support sizes counts each global support point `r_g` times. Thus

`sum_i delta_i = |S|-sum_g r_g`,

while cross-atom overlap is `sum_g r_g-|supp(S)|`. Add the two identities. ∎

If the bounded support frontier is externally accepted and `s>=23`, the total budget is

`31-s<=8`.

Therefore all internal atom repetitions and all cross-atom support overlaps together consume at most eight occurrences. This couples two previously separate reductions: large support forces the four atoms to be collectively close to squarefree and support-disjoint.

The existing inverse census for length-13 atoms can be used as bounded computational guidance. Because its current authority is machine-census rather than an independently replayed structural theorem, census-derived support refinements remain below theorem status.

## 9. A sharper next attack

The next decisive search should intersect, rather than sequence, the following constraints:

1. multiplicity pattern from Section 5;
2. rank-forcing status from Theorem 5;
3. saturation-defect certificates at every singleton/double point;
4. atom types `(6,6,6,13)` or `(6,6,7,12)`;
5. total atom repetition/overlap budget from Theorem 7;
6. total sum zero and exclusion of every zero sum of length at most five.

This intersection is strictly smaller than “run support 23.” A first survivor decides `D_4=31` only after independent factorization verification. A complete independently replayed UNSAT proof establishes `31 in C_0(C_5^3)` and hence `D_4=30`.

## 10. Relation to prior work

Freeze–Schmid own the generalized-Davenport recurrence, lower bound, extremal factorization language, and eventual-linearity context. Fan et al. own the `C_0` framework and short-zero-sum localization. Gao–Geroldinger–Schmid and later inverse work own the broader inverse zero-sum programme. Zhong's 2025 Combinatorica paper solves the inverse `k`-th Davenport problem for rank-two groups, sharpening the contrast with this rank-three case.

The R2 rank phase and atom budget are elementary consequences of these inputs and the registered obstruction grammar. They are presented as structural compression, not as generic zero-sum novelty.

## 11. Reproducibility

The corridor, saturation lemma, and support-ten theorem are separately receipt-bound. The R2 verifier enumerates every multiplicity pattern for supports 8–31, checks the rank-phase equivalence, reproduces support-23 and support-24 patterns, and validates the atom identity on independent synthetic factorizations. All-size authority comes from the proofs.

A top-tier resolution requires an externally auditable final obstruction proof or complete replay, not another internal implementation alone.

## 12. Limitations

1. `D_4(C_5^3)` remains 30/31.
2. `31 in C_0(C_5^3)` is not proved.
3. The support-23 frontier remains bounded evidence pending external replay.
4. The rank phase says when one normalization is forced; it does not prove existence outside the phase.
5. The atom budget is a compression identity, not a contradiction.
6. Much of the computation is post-outcome and internal.
7. Author-side prior-art search does not certify novelty.

## 13. Discussion and conclusion

There is further structure beyond the width-one corridor. The obstruction's multiplicity grammar has a precise rank-forcing phase, and its conditional atom factorization has a global repetition/overlap budget. Together they explain why the search becomes difficult exactly where it does and specify a smaller intersection problem for the final extremal bit.

This is real hardening, but it is not the missing top-tier theorem. The decisive advance remains exact `D_4`, `C_0(31)`, or a reusable global incompatibility theorem that eliminates the residual phase without support-by-support enumeration.

## Selected references

- M. Freeze and W. A. Schmid, *Remarks on a Generalization of the Davenport Constant*, Discrete Math. 310, 3373–3389 (2010), arXiv:0905.4248.
- Y. Fan, W. Gao, G. Wang, Q. Zhong and J. Zhuang, *On Short Zero-Sum Subsequences of Zero-Sum Sequences*, Electron. J. Combin. 19(3), P31 (2012), DOI `10.37236/2602`.
- W. Gao, A. Geroldinger and W. A. Schmid, *Inverse Zero-Sum Problems*, Acta Arith. 128, 245–279 (2007), DOI `10.4064/aa128-3-5`.
- Q. Zhong, *On the Inverse Problem of the k-th Davenport Constants for Groups of Rank 2*, Combinatorica 45, article 31 (2025), DOI `10.1007/s00493-025-00153-3`.

## Publication decision record

**Current primary posture:** strong specialist zero-sum/computational-combinatorics paper.
**Stretch targets:** `Journal of Combinatorial Theory, Series A`, `Combinatorica`, or `Combinatorial Theory` only after the final extremal gate or a comparably global obstruction theorem.
**R2 status:** `RIGOROUS_SPECIALIST_PLUS_STRUCTURAL_PHASE__TOP_TIER_GATE_STILL_OPEN`.
**Do not substitute:** additional prose, recurrence rows, or one more unintegrated support search for the missing theorem.

# Exact Early Generalized Davenport Constants and a One-Unit Tail Corridor in `C_5^3`

**R9 computer-assisted mathematics manuscript — 2026-08-26**

## Abstract

Let `D_k(G)` be the least length forcing `k` pairwise disjoint nonempty zero-sum subsequences. For the rank-three elementary abelian group `C_5^3`, the classical Davenport constant is 13, but the generalized sequence is not determined by the naive arithmetic progression at its first nontrivial step.

We establish the early values

`D_2(C_5^3)=20` and `D_3(C_5^3)=25`,

together with the exact short-zero-sum thresholds used by the recurrence, including `s_{<=6}(C_5^3)=24`. The `D_2` upper bound admits a short analytic route from a published short-subsequence lemma and the ordinary Davenport constant. The `D_3` upper bound is computer-assisted. Any length-25 counterexample would contain an exact six-term zero sum whose complement is a rank-three length-19 sequence with no two disjoint zero sums. A complete normalized census contains 98,622 such complements. Enumerating every admissible six-term extension produces 230,983 candidates, and an exact three-bin zero-sum packing algorithm rejects all of them. Positive and negative controls include a length-24 sequence with two but not three disjoint zero sums.

Combining the exact early constants, `s_{<=5}(C_5^3)=33`, `s_{<=6}(C_5^3)=24`, and the Freeze–Schmid recurrence gives

`5k+10 <= D_k(C_5^3) <= 5k+11` for every `k>=4`.

Thus one unresolved bit at `D_4` controls entry into the lower arithmetic line. If `D_4=30`, then `D_k=5k+10` for every `k>=2`; no converse is claimed from `D_4=31`.

We also analyze the hypothetical upper candidate. A total-zero length-31 sequence with no zero sum of length at most five has multiplicities only `1,2,4` after saturation, obeys an exact multiplicity grammar, and has a repeated stratum forced to rank three through the first residual diagonals. At the length-ten rank-two boundary, two multiplicity profiles are excluded by exact finite classification and the remaining `4,4,2` profile has five normalized forms. Compressed quotient relaxations do not decide source realizability; a source-level lift-aware solver is therefore frozen separately.

The exact computations are accompanied by code, manifests, controls, and content-bound receipts. A structurally independent clean-room replay on LUNARC is the release gate. Internal dual implementations are corroboration, not external replication. The exact value of `D_4(C_5^3)` remains open.

## 1. Generalized Davenport constants in rank three

For a finite abelian group `G`, `D_k(G)` is the least integer `n` such that every sequence of length at least `n` contains `k` pairwise disjoint nonempty zero-sum subsequences. The ordinary Davenport constant is `D_1(G)`.

For `C_5^3`, Olson's formula gives

`D(C_5^3)=1+3(5-1)=13`.

Freeze and Schmid give the lower line

`D_k(C_5^3)>=5k+10`.

The first values therefore test whether the generalized constants immediately follow the exponent-five progression or exhibit one last defect.

The exact sequence begins

`D_1=13, D_2=20, D_3=25`.

The increments `7,5` show that the lower arithmetic line fails at `k=1 -> 2` but is attained at `k=3`. The next value lies in `{30,31}`. This single bit controls the strongest exact tail statement currently available.

### Contributions

1. exact `D_2(C_5^3)=20`;
2. computer-assisted exact `D_3(C_5^3)=25` with a structure theorem and complete candidate census;
3. the exact registered short-zero-sum spectrum through length 12, including `s_{<=6}=24`;
4. the unconditional one-unit corridor for every `k>=4`;
5. the conditional exact lower-line tail if `D_4=30`;
6. a saturation-defect theorem for odd-prime short-free sequences;
7. exact multiplicity and rank reductions for a hypothetical length-31 obstruction;
8. a finite classification of the first rank-two repeated-stratum boundary; and
9. an explicit separation between analytic authority, finite exact computation, internal corroboration, and external clean-room replay.

## 2. Definitions and donor inputs

A sequence is a finite multiset with multiplicative notation. Its sum is `sigma(S)`. Let `s_{<=ell}(G)` be the least length forcing a nonempty zero-sum subsequence of length at most `ell`.

We use the published recurrence

`D_{k+1}(G) <= max{D_k(G)+ell, s_{<=ell}(G)-1}`.

We also use:

- `D(C_5^3)=13`;
- `s_{<=5}(C_5^3)=33` and the associated Property-C statement at length 32;
- `s_{<=5}(C_5^2)=eta(C_5^2)=13`;
- `D_k(C_5^3)>=5k+10`; and
- the registered exact finite thresholds for `ell=6,...,12`.

Every donor theorem is cited as donor mathematics. The finite thresholds and generalized constants have separate proof receipts and novelty status.

## 3. The second generalized constant

### Theorem 1

`D_2(C_5^3)=20`.

**Lower bound.** The published rank-three lower line gives `D_2>=20`. An explicit 19-term witness is retained as a reconstruction and checker control rather than a novelty claim for the lower-bound method.

**Upper bound.** Let `S` be an arbitrary length-20 sequence and append

`g=-sigma(S)`

to obtain a length-21 zero-sum sequence `T`. A published short-subsequence lemma, specialized at exponent five and ordinary Davenport constant 13, gives a nonempty zero-sum subsequence of length at most seven. Its complement has length at least 14 and is zero-sum. Because 14 exceeds `D(C_5^3)`, the complement contains a nonempty proper zero-sum subsequence; the remaining complement is also zero-sum. Thus `T` contains three pairwise disjoint nonempty zero sums. At most one uses the appended element `g`, leaving two disjoint zero sums in the arbitrary sequence `S`. Hence `D_2<=20`. ∎

The repository also contains a complete exact two-disjoint census and an independent finite replay. Those computations validate instruments and provide inverse data; the analytic proof carries the all-instance upper claim once the cited lemma is accepted.

## 4. Exact short-zero-sum thresholds

The registered finite search determines the following `s_{<=ell}(C_5^3)` values:

| `ell` | 5 | 6 | 7 | 8 | 9 | 10 | 11 | 12 |
|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| `s_{<=ell}` | 33 | 24 | 19 | 18 | 15 | 15 | 15 | 15 |

For `ell=5`, the value is donor-owned. The remaining rows are finite exact results in the ORION package. Each upper value requires complete exclusion at one length; each lower value has a serialized extremal witness whose minimum zero-sum length is independently recomputed.

The clean-room replay protocol requires two structurally different engines:

1. canonical orderly generation plus an exact weighted group-sum state; and
2. SAT/CP-SAT or meet-in-the-middle search with independent symmetry handling.

Agreement in counts, witnesses, canonical manifests, and digests is a release gate. A second run of the same generator is not structural independence.

## 5. The third generalized constant

### Theorem 2 — structure of a length-25 counterexample

If a length-25 sequence `M` has no three pairwise disjoint nonempty zero sums, then:

1. every zero sum in `M` has length at least six;
2. `M` contains a zero sum `A` of length exactly six;
3. the complement `C=M A^{-1}` has length 19 and no two disjoint zero sums; and
4. `C` has rank three.

**Proof.** If `M` had a zero sum of length at most five, its complement would have length at least 20 and therefore contain two disjoint zero sums by Theorem 1. Together they would give three. The exact value `s_{<=6}=24` forces a zero sum of length at most six, hence exactly six. Removing it leaves a length-19 sequence without two disjoint zero sums. A rank-at-most-two sequence of length 19 already contains two disjoint zero sums because `D(C_5^2)=9`: remove one zero sum from the first nine or more terms and the remaining length is still at least nine. Thus the complement has rank three. ∎

### Theorem 3 — computer-assisted exact value

Subject to the complete finite manifests and checker controls described below,

`D_3(C_5^3)=25`.

**Lower bound.** The package contains an explicit length-24 sequence with two but not three pairwise disjoint nonempty zero sums. Two structurally different exact packing routines verify the statement. This negative control is essential: a defective checker that always reports three disjoint zero sums would also return an empty upper-bound survivor set.

**Upper bound.** A complete `GL(3,5)`-normalized census contains 98,622 length-19 sequences with no two disjoint zero sums under the declared normalization. For every such complement `C`, enumerate every nondecreasing six-term multiset `A` satisfying:

1. `sigma(A)=0`; and
2. `C A` has no zero sum of length at most five.

The exhaustive extension step produces 230,983 length-25 candidates. An exact three-bin group-sum dynamic program evaluates every candidate. It finds zero candidates without three disjoint nonempty zero sums. The structure theorem proves that every possible counterexample occurs in this census. Therefore `D_3<=25`; the lower witness gives equality. ∎

### 5.1 Checker controls

The exact three-bin engine is required to reproduce:

- a 19-term two-disjoint-free control;
- the length-24 lower witness with two disjoint zero sums but no three;
- a length-25 positive control with three disjoint zero sums; and
- a dense positive control.

Shift masks or group-addition tables are checked exhaustively against primitive coordinate addition in `F_5^3`. Candidate grouping optimizations must not change the semantic state, and every skipped prefix receives an explicit reason.

### 5.2 Authority boundary

The internal package contains the full source and result records. The R9 release requires the LUNARC clean-room replay in issue #1383. A PASS upgrades reproducibility. It does not establish absolute novelty, external peer review, or the value of `D_4`.

## 6. The one-unit tail corridor

The exact `D_3=25` and `s_{<=6}=24` give

`D_4 <= max{25+6,24-1}=31`.

The lower line gives `D_4>=30`. Hence

`D_4(C_5^3) in {30,31}`.

### Theorem 4 — unconditional corridor

For every `k>=4`,

`5k+10 <= D_k(C_5^3) <= 5k+11`.

**Proof.** The base upper bound is `D_4<=31`. Apply the recurrence with `ell=5` and `s_{<=5}-1=32`. If `D_k<=5k+11`, then

`D_{k+1}<=max{5k+16,32}=5(k+1)+11`

for `k>=4`. The published lower line supplies the other inequality. ∎

### Theorem 5 — conditional exact tail

If `D_4(C_5^3)=30`, then

`D_k(C_5^3)=5k+10`

for every `k>=2`.

**Proof.** The equality holds at `k=2,3,4`. The same recurrence with `ell=5` propagates the upper line `5(k+1)+10`, matching the lower bound. ∎

No converse is claimed. `D_4=31` alone does not force every later value onto the upper line.

## 7. The hypothetical upper candidate

Assume a total-zero sequence `S` of length 31 has no nonempty zero-sum subsequence of length at most five. Such a sequence is the relevant short-free obstruction associated with the upper candidate. Every point has multiplicity at most four.

When support exceeds eight, Property C implies saturation: appending any group element destroys 5-short-freeness, because a length-32 short-free extension would have exactly eight support points.

### Theorem 6 — saturation defect

Let `p` be odd and let `S` be a saturated `p`-short-free sequence over an elementary abelian exponent-`p` group. If a nonzero point `x` has multiplicity `m<p`, then there is a subsequence `R` such that

`|R|<=p-1-m`, `x notin supp(R)`, and `sigma(R)=-(m+1)x`.

**Proof.** Append one copy of `x`. Saturation gives a zero sum of length at most `p` using the new occurrence. It must use every original copy of `x`; otherwise the new copy can be replaced by an unused original copy to obtain a forbidden short zero sum already in `S`. Removing the `m+1` copies leaves `R`. ∎

### Corollary 7

Multiplicity `p-2` is impossible. At `p=5`, multiplicity three is absent. Singleton and double points also carry short defect certificates that must be realized by actual source terms.

## 8. Exact multiplicity grammar

Let `s=|supp(S)|`, and let `c_1,c_2,c_4` count support points of multiplicity one, two, and four. Then

`c_1+c_2+c_4=s`,

`c_1+2c_2+4c_4=31`,

so

`c_2=31-s-3c_4`,

`c_1=2s-31+2c_4`.

The repeated subsequence `H` consisting of double and quadruple points has length

`|H|=2c_2+4c_4=62-2(s+c_4)`.

These equations enumerate every possible support stratum after saturation.

## 9. Rank forcing and the first low-rank boundary

If `H` lies in a rank-two subgroup and has length at least 13, the rank-two short-zero-sum threshold forces a zero sum of length at most five. Since `|H|` is even, the contradiction applies from length 14.

### Theorem 8 — first rank-forcing phase

The repeated stratum spans rank three whenever

`s+c_4<=24`.

A Property-C boundary argument at `|H|=12` extends the useful conclusion:

### Theorem 9 — 25-diagonal classification

If `s+c_4=25` and `H` has rank at most two, then the only possibility is

`(s,c_1,c_2,c_4)=(22,19,0,3)`,

and `H=T^4` for three distinct points spanning a rank-two subgroup. Consequently, every branch with `s>=23` and `s+c_4<=25` has a repeated-stratum basis of `C_5^3`.

The theorem converts the first residual support rows into a canonical-basis search regime without claiming that the candidates are empty.

## 10. The length-ten rank-two boundary

On `s+c_4=26`, `|H|=10`. The possible repeated multiplicity profiles are

- `2^5`;
- `4,2,2,2`; and
- `4,4,2`.

Two independent finite zero-sum engines exclude the first two profiles in rank two. In the remaining profile, the fourfold points are independent. Normalize them to `e_1,e_2` and write the double point as `u e_1+v e_2`.

### Theorem 10 — exact `4,4,2` classification

The allowed ordered coordinate pairs are exactly

`(1,1),(1,2),(1,3),(1,4),(2,1),(2,3),(3,1),(3,2),(4,1)`.

Up to swapping the two fourfold basis points, there are five normal forms represented by

`(1,1),(1,2),(1,3),(1,4),(2,3)`.

This is a finite exact classification at `p=5`, not an all-prime theorem.

## 11. Source lift versus compressed relaxation

The next diagonal introduces rank-two repeated strata whose quotient or weighted compression can satisfy necessary constraints without corresponding to a valid source sequence. A compressed countermodel therefore cannot be promoted to a source survivor, and relaxation-level UNSAT cannot be promoted to source UNSAT unless every source maps into the relaxation and every cut is sound.

The frozen lift-aware computation in issue #1384 begins with

`S=e_1^4 e_2^4 X`,

where `X` consists of 23 distinct singleton points. It enforces simultaneously:

1. total sum zero;
2. source-level exclusion of every zero-sum submultiset of length one through five;
3. full rank;
4. saturation-defect witnesses from actual source members;
5. lift-realizability of every quotient atom;
6. all cross-atom short-sum exclusions;
7. at most four pairwise disjoint nonempty zero sums; and
8. full stabilizer canonicalization.

Allowed terminals distinguish certified source UNSAT, a replayed source survivor, partial compression to a new invariant, resource bounds, and completeness failure. Closing these rank-two orbits advances the obstruction programme but does not determine `D_4` unless every remaining source stratum is closed.

## 12. Atom factorization and overlap

Let

`S=U_1 ... U_r`

be an occurrence-disjoint atom factorization. For each support point `g`, let `r_g` count atom supports containing it, and let

`delta_i=|U_i|-|supp(U_i)|`.

### Theorem 11 — repetition-overlap identity

`|S|-|supp(S)| = sum_i delta_i + sum_g(r_g-1)`.

The identity decomposes support deficit into internal atom repetition and cross-atom overlap. It is a compression principle rather than a contradiction. Combined with an independently established support lower bound, it yields an exact global overlap budget.

## 13. Reproducibility architecture

The release package separates four evidence classes.

### 13.1 Analytic proofs

The corridor induction, saturation defect, multiplicity equations, rank forcing, boundary reductions, and overlap identity are human-checkable proofs.

### 13.2 Finite exact computations

The short-zero-sum spectrum, normalized inverse census, `D_3` extension/rejection, and length-ten rank-two classifications have finite manifests, exact source code, expected counts, and positive/negative controls.

### 13.3 Internal independent corroboration

Different in-repository state representations and algorithms guard implementation errors. They do not become external replication merely by being separate programs from the same research programme.

### 13.4 Clean-room external execution

Issue #1383 requires structurally independent engines, independent symmetry handling, LUNARC environment receipts, immutable partition manifests, source/result digests, resource accounting, and exact agreement. Any disagreement is preserved as a scientific terminal.

## 14. Prior-art and novelty boundary

Generalized Davenport recurrences, the lower-bound framework, Property C, short-zero-sum localization, inverse zero-sum theory, and rank-two constants are donor mathematics.

The candidate residual contribution is:

- the exact early `C_5^3` constants and short-zero-sum spectrum not already present in the cited primary literature;
- the structure-theorem reduction and complete `D_3` proof package;
- the one-unit all-`k` corridor from the exact inputs;
- the saturation/multiplicity/rank synthesis for the length-31 obstruction; and
- the finite rank-two boundary classifications.

A current specialist primary-source audit is required before novelty language is finalized. `NOT_FOUND` in a bounded search is not a novelty certificate.

## 15. Applications and broader connections

### 15.1 Nonunique factorization

`D_k` measures extremal factorization length in associated block monoids. The exact early constants and one-unit tail corridor constrain the first nontrivial rank-three factorization regime.

### 15.2 Coding-theoretic translation

A sequence in `F_5^3` is a multiset of columns. A short all-one zero sum is a low-weight dependence with selected coefficients equal to one. The translation can inspire restricted-dependence tests, but no new coding bound is claimed without an equivalent coding parameter.

### 15.3 Computer-assisted proof methodology

The `D_3` argument illustrates a preferred pattern: prove a structure theorem first, enumerate a complete canonical boundary, validate a rejector with a genuine negative control, and separate internal corroboration from clean-room replay.

### 15.4 Local-to-global bounds

The exact `C_5^3` multiwise constants enter inductive bounds for larger exponent groups. Any global corollary requires a separate hypothesis and prior-art audit and is not automatically part of the present novelty claim.

## 16. Limitations

- `D_4(C_5^3)` remains open.
- The all-`k` exact lower line is conditional on `D_4=30`.
- Finite exact computations require clean-room replay and specialist review.
- The rank phases are one-way implications.
- Compressed relaxations do not decide source lift.
- Bounded support exclusions do not substitute for a complete all-stratum proof.
- The current work makes no quantum-computing claim.

## 17. Conclusion

The generalized Davenport sequence of `C_5^3` is exactly known through `k=3` and lies within one unit of the lower arithmetic line for every later index. This is a complete theorem package even though the next bit remains open: the exact early constants determine the corridor, while `D_4=30` would collapse it to equality forever.

The hypothetical upper candidate is not an unstructured search object. Saturation removes multiplicity three, the remaining multiplicities obey an exact grammar, the repeated stratum is forced to full rank through the first residual diagonals, and the first low-rank boundary has finitely many normal forms. The next computation is therefore source-level and lift-aware rather than a wider relaxation.

## Tool-use disclosure

A generative language model assisted organization, language revision, proof exploration, computation planning, and preparation of reproducibility protocols. The author is responsible for every proof, program, result, citation, and final claim.

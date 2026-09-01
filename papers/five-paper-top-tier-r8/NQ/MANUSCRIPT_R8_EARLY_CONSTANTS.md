# Exact Early Generalized Davenport Constants in `C_5^3` and a One-Unit Tail Corridor

## Abstract

Let `D_k(G)` be the least length forcing `k` pairwise disjoint nonempty zero-sum subsequences. We study the first multiwise constants of `C_5^3`. Exact finite computation, combined with structural reductions, gives candidate theorems

`D_2(C_5^3)=20`, `D_3(C_5^3)=25`.

For `D_2`, a donor lower construction is matched by two exact upper routes: a short-zero-sum threshold argument and a complete normalized enumeration of 98,622 length-19 extremal failures. For `D_3`, every hypothetical length-25 failure has minimum zero-sum length six and decomposes into an exact six-term zero sum plus a rank-three length-19 `D_2` extremal core. Exhausting all 230,983 admissible six-term extensions yields no failure, while an explicit length-24 sequence gives the lower bound.

Together with `s_{<=5}(C_5^3)=33`, the exact computed value `s_{<=6}(C_5^3)=24`, and the Freeze–Schmid recurrence and lower line, these constants imply

`5k+10 <= D_k(C_5^3) <= 5k+11` for every `k>=4`.

If `D_4(C_5^3)=30`, then `D_k=5k+10` for every `k>=2`; the current work does not decide the remaining `30/31` bit. We also record a saturation-defect lemma and quotient-atom compression that constrain a hypothetical upper-line obstruction, together with exact rank-two boundary classifications. The exact early constants are presently machine-checked within ORION; top-level theorem authority is conditioned on the clean-room replay packet accompanying this version.

## 1. Introduction

Generalized Davenport constants measure how a sequence's zero-sum structure packs, not merely whether one zero sum exists. Even for elementary abelian rank three, the first increments can deviate from an eventual linear pattern.

For `C_5^3`, the ordinary Davenport constant is 13. The donor lower line is `D_k>=5k+10`, so the first candidate values are 20, 25, 30, .... The exact second and third constants determine how quickly the sequence enters this line and substantially tighten the fourth and all later values.

The paper's primary contribution is computer-assisted exact mathematics at `k=2,3`, not a claimed resolution of `D_4`. The computation is paired with structural reductions that make the searched spaces finite and independently checkable. The accompanying clean-room protocol requires a second implementation with a different state representation before submission.

### Contributions

1. Exact candidate value `D_2(C_5^3)=20` with an explicit lower witness, a short-threshold upper proof, and complete inverse census.
2. Exact candidate value `D_3(C_5^3)=25` via an exact six-atom/core decomposition and complete extension search.
3. Exact short-zero-sum spectrum values used by the reductions.
4. A one-unit corridor `5k+10<=D_k<=5k+11` for every `k>=4` and the conditional exact tail from `D_4=30`.
5. Saturation, multiplicity, rank, and quotient-atom reductions for the unresolved length-31 obstruction.
6. A fully specified clean-room replay and lift-aware successor computation.

## 2. Definitions and donor inputs

For a finite abelian group `G`, `D_k(G)` is the least `n` such that every sequence of length at least `n` contains `k` pairwise disjoint nonempty zero-sum subsequences. Let `s_{<=ell}(G)` be the least length forcing a nonempty zero sum of length at most `ell`.

The donor inputs are:

- `D(C_5^3)=13` by the p-group formula;
- Freeze–Schmid's lower line `D_k(C_5^3)>=5k+10`;
- their recurrence `D_{k+1}<=max(D_k+ell,s_{<=ell}-1)`;
- `s_{<=5}(C_5^3)=33` and Property C as recorded in the short-zero-sum literature; and
- `s_{<=5}(C_5^2)=13`.

The ORION exact-computation inputs under independent-replay review are:

- `s_{<=6}=24`, `s_{<=7}=19`, `s_{<=8}=18`, and the registered spectrum through 12;
- the complete normalized length-19 `D_2` extremal census; and
- the length-25 `D_3` extension census.

## 3. Exact value of `D_2`

### Lower bound

The explicit 19-term Freeze–Schmid-type sequence has no two disjoint zero sums, giving `D_2>=20`.

### Threshold upper route

The exact short threshold `s_{<=7}=19` implies every length-20 sequence has a zero sum of length at most seven. Its complement has length at least 13 and therefore contains another zero sum because `D(C_5^3)=13`. Thus `D_2<=20`.

### Independent direct route

A complete normalized enumeration scans rank-three length-19 sequences satisfying the proved minimum-short-sum restriction and records 98,622 extremal failures under the declared basis and coordinate-permutation normalization. Every admissible one-term extension is checked by an exact two-bin zero-sum packing DP. The direct route also yields `D_2<=20`.

Hence, subject to clean-room reproduction,

`D_2(C_5^3)=20`.

## 4. Exact value of `D_3`

Let `M` be a hypothetical length-25 sequence with no three disjoint zero sums.

### Lemma 1 — minimum zero-sum length

Every zero sum in `M` has length at least six. Otherwise its complement has length at least 20 and contains two disjoint zero sums by the exact `D_2` value.

### Lemma 2 — exact six-term atom

Since `s_{<=6}=24`, `M` contains a zero sum of length at most six. Lemma 1 forces length exactly six. Let it be `A`.

The complement `C=M A^{-1}` has length 19 and no two disjoint zero sums. It has rank three because rank-two constants already force two disjoint zero sums at that length. Therefore `C` is equivalent to a member of the complete normalized `D_2` extremal census.

### Complete extension search

For each of the 98,622 normalized cores, enumerate every nondecreasing six-element extension whose sum is zero and whose addition creates no zero sum of length at most five. This yields 230,983 candidates. An exact three-bin packing evaluator rejects every candidate; controls include a length-24 negative instance on which the evaluator must report two but not three disjoint zero sums.

An explicit length-24 sequence has no three disjoint zero sums, so the lower bound is 25. Subject to clean-room reproduction,

`D_3(C_5^3)=25`.

## 5. The all-`k` corridor

Using `ell=6` in the recurrence gives

`D_4<=max(25+6,24-1)=31`.

The lower line gives `D_4>=30`.

### Theorem 3 — one-unit corridor

For every `k>=4`,

`5k+10<=D_k(C_5^3)<=5k+11`.

**Proof.** The base upper value is 31. Apply the recurrence with `ell=5` and `s_{<=5}-1=32`. If `D_k<=5k+11`, then `D_{k+1}<=max(5k+16,32)=5(k+1)+11`. The donor lower line supplies the other inequality. ∎

### Theorem 4 — conditional exact tail

If `D_4=30`, then `D_k=5k+10` for every `k>=2`.

The recurrence with `ell=5` propagates the lower-line upper value. No converse is claimed from `D_4=31`.

## 6. Structural constraints on an upper-line obstruction

If `D_4=31`, the extremal factorization framework yields a length-31 total-zero sequence with no zero sum of length at most five. When its support exceeds eight it is saturated.

### Saturation defect

In an odd-prime elementary abelian group, if a saturated `p`-short-free sequence contains `x` with multiplicity `m<p`, appending another `x` produces a short zero sum using all `m+1` copies and a residual subsequence `R` of length at most `p-1-m` with sum `-(m+1)x`. Multiplicity `p-2` is impossible. For `p=5`, multiplicities are therefore 1, 2, or 4.

If `s` is support and `c_i` counts multiplicity `i`, then

`c_2=31-s-3c_4`, `c_1=2s-31+2c_4`.

Rank-two short-zero-sum theory forces the repeated stratum to span rank three over the first residual diagonals, with finite classifications at the later boundary. On `s+c_4=27`, rank-two profiles `4,4` and five `4,2,2` orbits survive at the repeated-stratum level.

### Quotient-atom compression

If the repeated stratum lies in a plane `P`, partition the singleton quotient word in `C_5^3/P` into minimal quotient-zero blocks. Each source block has length at most five and nonzero sum in `P`; replacing it by that kernel sum preserves total sum and lifts every compressed zero-sum factorization. Weighting a compressed block by its source length gives an exact necessary weighted short-free contract.

A registered compressed countermodel shows that total weighted sum, weighted short-freeness, and factorization count are insufficient without source lift realizability and cross-block short-sum checks. The next solver is therefore source-level and lift-aware.

## 7. Computer-assisted proof architecture

The proof package separates:

1. structural reductions proved in prose;
2. finite canonical generators;
3. exact packing evaluators;
4. positive and negative controls;
5. result manifests and hashes; and
6. an independently specified clean-room replay.

A correct program run is evidence for the finite statement only after completeness, semantics, and environmental identity are established. Internal dual implementations are not represented as external replication.

## 8. Relation to prior work

The recurrence, lower line, p-group value, Property C, short-zero-sum constants, and generic quotient/factorization methods are donor-owned. The claimed increment is limited to the exact `C_5^3` early constants, the associated complete finite reductions/inverse data, and their corridor consequence.

The final submission must include a specialist primary-source audit. Failure to locate an earlier exact value is not a novelty certificate.

## 9. Limitations and open problem

The exact value of `D_4(C_5^3)` remains in `{30,31}`. The support and diagonal analyses do not close every full source-level obstruction. No finite partial stratum may be promoted to a `D_4` theorem.

The exact `D_2`/`D_3` paper is ready for scientific consideration only after the clean-room replay terminal passes and the complete source/certificate package is archived immutably.

## 10. Conclusion

The first multiwise constants of `C_5^3` appear to enter the lower line at `k=2`: exact computation gives 20 and 25, and every later value is trapped within one unit of `5k+10`. The result combines short-zero-sum thresholds, a complete inverse core census, and exact disjoint-packing evaluation.

The remaining fourth constant is a separate problem. Its unresolved status does not erase the exact early constants, but it governs whether the lower line continues forever without one final defect.

## Tool-use disclosure

A generative language model assisted manuscript organization, code generation, and language revision. The author remains responsible for every theorem, implementation, source, and claim.

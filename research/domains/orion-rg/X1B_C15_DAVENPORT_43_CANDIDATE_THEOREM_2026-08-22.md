# X1-B candidate theorem — `D(C_15^3)=43`

Parent: #900. Umbrella pure-math programme: #896.

## Status

**COMPLETE INTERNAL CANDIDATE PROOF — NOT YET EXTERNAL-PEER-REVIEWED OR NOVELTY-AUTHORIZED.**

This packet assembles the admitted donor statements, hostile-audit corrections, and independently replayed finite subtheorems into one end-to-end proof. It is committed before any downstream generalization or breakthrough claim.

## Theorem

> **Candidate Theorem.** For the homocyclic rank-three group
> `G=C_15^3`,
> the Davenport constant is
> 
> `D(G)=43`.

Equivalently, the maximum length of a zero-sum-free sequence over `C_15^3` is 42.

## 1. Lower bound

For

`G=C_15 direct-sum C_15 direct-sum C_15`,

the standard lower bound is

`D*(G)=1+3(15-1)=43`.

Hence

`D(G)>=43`.

It remains to prove that every sequence of length 43 contains a nonempty zero-sum subsequence.

## 2. Primary decomposition

Use the Chinese-remainder decomposition

`C_15^3 ≅ C_3^3 direct-sum C_5^3`.

Let

`pi:G->C_3^3`

be the projection, whose kernel is naturally `K=C_5^3`.

Assume for contradiction that

`S=g_1...g_43`

is zero-sum free over G.

A **quotient block** is a nonempty subsequence B of S whose projected sum is zero in `C_3^3`. Its lifted sum lies in K.

If S contains 13 pairwise-disjoint quotient blocks, let their lifted sums be

`h_1,...,h_13 in K`.

Since K is the p-group `C_5^3`,

`D(K)=1+3(5-1)=13`.

Thus some nonempty subcollection of the h_i sums to zero in K. The union of the corresponding quotient blocks has zero projection and zero kernel component, hence is a nonempty zero-sum subsequence of S, contradiction.

Therefore a hypothetical counterexample can never produce 13 pairwise-disjoint quotient blocks.

## 3. Greedy short-block reduction

Greedily remove pairwise-disjoint nonempty quotient blocks of length at most 3 until the residual R has no quotient zero sum of length at most 3.

Donor input from Bhowmik--Schlage-Puchta:

`D^3(C_3^3)=17`,

so every 17-term quotient sequence has a zero sum of length at most 3. Hence

`|R|<=16`.

Let m be the number of removed short quotient blocks. Each has length at most 3, so

`43-3m <= |R| <=16`,

and therefore `m>=9`.

If `m>=13`, the removed blocks already contradict the previous section. Hence

`m in {9,10,11,12}`.

We now exhaust these four cases.

## 4. Case `m=12`

Twelve removed blocks use at most 36 terms, so

`|R|>=7`.

The ordinary p-group value is

`D(C_3^3)=7`.

Thus R contains a nonempty quotient zero sum, giving the 13th quotient block, contradiction.

Hence `m=12` is impossible.

## 5. Case `m=11`

Eleven removed blocks use at most 33 terms, so

`|R|>=10`.

Donor input:

`D_2(C_3^3)=11`.

If `|R|>=11`, R contains two disjoint quotient zero sums. Together with the eleven removed blocks this gives 13 quotient blocks, contradiction.

The only remaining possibility is

`|R|=10`.

Then the eleven removed blocks use exactly 33 terms, so **all eleven are triples**.

This is exactly the committed k=3 / 10-point interface.

### k=3 scalarization

Let the lifted kernel sums of the eleven fixed triples form T. If a nonempty subcollection of these eleven sums were zero, S would already contain an upstairs zero sum. Hence T is zero-sum free in `C_5^3` and has length

`11=d(C_5^3)-1`.

Geroldinger--Yang Theorem 3.5, audited directly from arXiv:2608.19090, gives a nonzero homomorphism

`lambda:C_5^3->F_5`

such that every nonzero element missing from the subsequence-sum set of T has the same nonzero lambda-value (canonically `-1`, up to rescaling).

Let C be any quotient-zero-sum subset of the ten-position residual R, with lifted kernel sum c. The twelve block sums `T c` must remain zero-sum free; otherwise S has an upstairs zero sum. Therefore `-c` is a missing subsequence sum of T. Thus all residual quotient-zero-sum blocks have one common nonzero scalar image under lambda.

After normalization, the ten residual positions must admit scalars `f_1,...,f_10 in F_5` such that

`sum_{j in C} f_j =1`

for every nonempty quotient-zero-sum position subset C.

### k=3 raw finite theorem

An independent no-symmetry verifier exhaustively enumerates all 10-position residual multisets satisfying the terminal no-short-zero-sum condition. Completeness was separately audited, including exclusion of a possible 9-point support.

Exact census:

```text
raw candidates:          1,190,124
no-disjoint candidates:    400,608
common-RHS inconsistent:   400,608
common-RHS consistent:           0
```

Thus no k=3 residual can satisfy the scalar condition forced by Geroldinger--Yang local scalarization.

Hence `m=11` is impossible.

## 6. Case `m=10`

Ten removed blocks use at most 30 terms, so

`|R|>=13`.

Donor input:

`D_3(C_3^3)=15`.

If `|R|>=15`, R contains three disjoint quotient zero sums. Together with the ten removed blocks this gives 13 quotient blocks, contradiction.

Hence only `|R|=13` or `|R|=14` remain.

### 6.1. Subcase `|R|=14`

The ten removed blocks use 29 terms, so exactly nine are triples and one has length 2.

The residual is terminal: it contains no quotient zero sum of length <=3.

A prospectively frozen independent raw verifier enumerates every possible 14-position residual under that condition, with no `GL(3,3)` quotient:

```text
admissible raw 7-supports: 18,720
admissible raw 8-supports:    702
total 14-position candidates: 38,376
candidates with three disjoint quotient zero sums: 38,376
failures: 0
```

Therefore every possible 14-point terminal residual contains three disjoint quotient zero sums. Along with the ten removed blocks these give 13 quotient blocks, contradiction.

Thus `|R|=14` is impossible.

### 6.2. Subcase `|R|=13`

The ten removed blocks use exactly 30 terms, so all ten are triples.

This is exactly the committed k=4 / 13-point interface.

A complete independently replayed finite theorem chain closes this interface. The chain is summarized here and fully serialized in `X1B_K4_13PT_RESIDUAL_CLOSURE_THEOREM_2026-08-22.md`.

#### Quotient classification

Complete full-multiplicity enumeration under the terminal no-short condition and packing number exactly 2 gives 15 canonical quotient residual orbits.

- 9 close under the donor-derived local scalarization test;
- 6 exact obstructions remain.

#### Global bilinear coupling

For the ten fixed triple sums `t_1,...,t_10 in C_5^3`, the p-group group-algebra identity defines one symmetric bilinear form `M_T` such that for **every** disjoint pair `(Z,W)` of residual quotient-zero-sum blocks,

`z_Z^T M_T z_W=1`.

Thus every genuine residual lift induces a symmetric 13x13 position Gram matrix B of rank at most 3 satisfying all edge equations.

Four of the six quotient obstructions have an inconsistent affine symmetric-matrix system and are eliminated immediately.

#### Complete realization census for the last two quotient orbits

The two remaining quotient orbits admit exactly:

- 116 rank-3 Gram completions in total; and
- one rank-2 Gram type, with a possible one-dimensional radical coordinate on each residual position.

No other rank<=3 completion exists.

#### Rank-3 branch

The 116 rank-3 completions collapse under exact `GL(3,5)` canonicalization to three forbidden-prefix classes R3-10, R3-11, R3-12.

For each class, an exact primary enumeration and an algorithmically independent no-memo replay both prove that the maximum ten-prefix length avoiding the required residual extension subset sums is **9**, never 10.

Hence all 116 rank-3 realizations are impossible.

#### Rank-2 radical branch

The rank-2 family is completely normalized by kernel shear and radical scaling to

`12,207,032`

radical assignments per quotient orbit, `24,414,064` total.

Complete exact census gives 8,984 distinct forbidden signatures and 639 inclusion-minimal signatures.

- 418 minima contain a linear image of an independently closed seven-point forbidden set;
- 218 further minima contain a linear image of independently closed R3-10;
- only three raw minima remain;
- those reduce to two `GL(3,5)` classes R2R-11 and R2R-12.

For both final classes, prospectively frozen exact primary search gives maximum admissible prefix length 9. A fresh independent verifier carrying the represented subset-sum set directly and using no memoization/state merging confirms:

```text
R2R-11: 79,487,138 canonical nodes, max length 9, NO length 10
R2R-12: 54,683,021 canonical nodes, max length 9, NO length 10
```

Hence the complete rank-2 radical branch is impossible.

Therefore **no k=4 / 13-point residual survives**.

So `m=10` is impossible.

## 7. Case `m=9`

Nine removed blocks use at most 27 terms, and the terminal residual has size at most 16. Hence

`|R|=16`,

and all nine removed blocks are triples.

The terminal no-short condition implies every support multiplicity in R is at most 2. The independently audited support cap is at most 8; length 16 therefore forces exactly eight distinct support points, each doubled.

A prospectively frozen raw verifier enumerates every admissible 8-support without symmetry reduction:

```text
raw admissible 8-supports: 702
16-position candidates:   702
candidates admitting four disjoint quotient zero sums: 702
failures: 0
```

Every candidate in fact has exactly 96 zero-sum 4-subsets and admits a partition into four zero-sum 4-blocks.

Together with the nine removed blocks, these four residual blocks give 13 quotient blocks, contradiction.

Hence `m=9` is impossible.

## 8. Exhaustion

Every possible greedy terminal state belongs to one of the cases `m=9,10,11,12`, and every case yields a contradiction.

Therefore no zero-sum-free sequence of length 43 exists over `C_15^3`.

Thus

`D(C_15^3)<=43`.

Combined with the standard lower bound `D(C_15^3)>=43`, we obtain

> **`D(C_15^3)=43`.**

## 9. Evidence and novelty boundary

This is a complete internal candidate proof with independently replayed finite components and a directly audited 2026 p-group donor bridge.

It is **not yet represented as a published or peer-reviewed theorem**. Before novelty promotion it still requires:

1. an end-to-end hostile proof review independent of the construction path;
2. canonical ORION-harness evidence binding on a stable branch head;
3. a fresh literature search/current expert prior-art check;
4. preferably formal or external mathematical verification of the finite certificates and analytic interfaces.

A fresh Aug-22-2026 literature sweep found no existing exact `D(C_15^3)=43` result and current curated sources continue to list the general homocyclic rank-three problem as open outside known families, but this is novelty evidence only, not authority.

## 10. Breakthrough criterion

If the independent review confirms the proof and current literature confirms the case is new, this would constitute a genuine new exact composite-exponent homocyclic rank-three Davenport result.

The immediate scientific successor is not to stop at n=15, but to extract the reusable deficit-repair mechanism and test it prospectively on the first infinite composite family.
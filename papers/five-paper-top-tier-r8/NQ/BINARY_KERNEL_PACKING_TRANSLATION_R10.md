# Exact Coding-Theoretic Translation of Generalized Davenport Constants R10

Date: 2026-08-26

Status: exact reformulation, not a new generic coding-theory claim. Any novelty statement requires a dedicated prior-art audit of constrained/binary kernel codewords, intersecting codes, and weighted Davenport constants.

## 1. Matrix model

Let

`H=[h_1 ... h_m] in F_5^{3 x m}`

be any matrix, with repeated or zero columns allowed. Regard its ordered column list as a sequence `S=(h_1,...,h_m)` over `C_5^3`.

For a subset `I subseteq {1,...,m}`, let `1_I in {0,1}^m subset F_5^m` be its incidence vector.

Then

`H 1_I = sum_{i in I} h_i`.

Therefore a nonempty zero-sum subsequence of `S` is exactly a nonzero vector

`z in ker(H) intersect {0,1}^m`.

This is a restricted kernel-codeword condition: the coefficients are exactly zero or one, not arbitrary nonzero field coefficients.

## 2. Disjoint packing number

Define

`nu_01(H)`

as the maximum cardinality of a family

`z^(1),...,z^(t) in ker(H) intersect {0,1}^m \ {0}`

whose supports are pairwise disjoint.

### Theorem NQ-R10.1 — exact equivalence

For every positive integer `k`,

`D_k(C_5^3)`

is the least integer `m` such that every `H in F_5^{3 x m}` satisfies

`nu_01(H) >= k`.

### Proof

Every length-`m` sequence over `C_5^3` is the column sequence of some `3 x m` matrix `H`, and conversely. By the incidence-vector identity above, nonempty zero-sum subsequences are in bijection with nonzero `{0,1}` kernel vectors. Two zero-sum subsequences are disjoint exactly when their incidence vectors have disjoint supports. Thus `k` pairwise-disjoint nonempty zero sums exist exactly when `nu_01(H)>=k`. Taking the universal threshold over all length-`m` sequences/matrices gives the claimed equality. ∎

No full-rank assumption is needed. A zero column corresponds to a weight-one binary kernel word, exactly matching the singleton zero-sum subsequence.

## 3. Exact consequences of the current ORION theorem package

Conditional on the independently replayed computer-assisted authority for the registered constants, the current results translate as follows.

### Corollary NQ-R10.2

`D_2(C_5^3)=20` is equivalent to:

- every `3 x 20` matrix over `F_5` contains two nonzero support-disjoint vectors in `ker(H) intersect {0,1}^{20}`;
- there exists a `3 x 19` matrix for which no such pair exists.

### Corollary NQ-R10.3

`D_3(C_5^3)=25` is equivalent to:

- every `3 x 25` matrix over `F_5` contains three nonzero pairwise support-disjoint binary kernel vectors;
- there exists a `3 x 24` matrix for which no such triple exists.

### Corollary NQ-R10.4

The one-unit tail corridor

`5k+10 <= D_k(C_5^3) <= 5k+11` for `k>=4`

is exactly a one-column uncertainty window for the universal threshold forcing `k` support-disjoint nonzero binary kernel vectors in every `3 x m` matrix over `F_5`.

If the conditional propagation theorem from `D_4(C_5^3)=30` is activated, it becomes an eventual exact formula for this restricted kernel-packing threshold.

## 4. Why this is not ordinary code distance

The property does not ask whether `ker(H)` contains an arbitrary low-weight codeword. It asks for codewords whose coordinates lie in `{0,1}` and then packs several with disjoint supports.

Thus standard minimum distance alone does not determine `nu_01(H)`. Field rescaling of a codeword can also leave the binary cube, so ordinary projective equivalence must be handled carefully when transporting claims.

This distinction should be explicit to avoid claiming a standard coding theorem under new notation.

## 5. Exact algorithmic application

The translation gives a second implementation language for independent replay:

- original engine: zero-sum sequence / atom packing;
- independent engine: parity-check matrix plus restricted binary kernel-word packing.

A structurally independent solver can encode binary selectors `z_i in {0,1}` with modular parity-check constraints

`sum_i H_{r,i} z_i = 0 mod 5`

and disjointness across `k` selector vectors. This is well suited to SAT/CP-SAT/MILP and provides an independent conceptual check of the sequence-based factorization code.

The translation therefore has immediate reproducibility value even if no coding application is promoted.

## 6. Potential coding experiment

Freeze a set of small parity-check column multisets and compare:

1. generic SAT/MILP for restricted binary kernel packing;
2. the ORION symmetry/source-aware zero-sum solver;
3. an independent canonical matrix solver.

Report:

- maximum `nu_01(H)` or threshold decision;
- orbit reduction;
- lazy-cut count;
- wall time / memory;
- certificate size;
- replay agreement.

A positive result would support a reusable constrained-codeword-packing algorithmic application. It would not by itself establish a new classical coding bound.

## 7. Prior-art boundary

Zero-sum theory already has deep links to coding theory, weighted Davenport constants, intersecting codes, and factorization theory. In particular recent work on the geometry of intersecting codes explicitly studies weighted Davenport connections. Those generic links are donor-owned.

The safe ORION claim is the exact `{0,1}`-kernel packing reformulation of the specific multi-wise `D_k(C_5^3)` problem and any solver/replay consequences that are actually executed.

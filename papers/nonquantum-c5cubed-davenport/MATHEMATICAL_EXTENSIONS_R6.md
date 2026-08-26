# Mathematical Extensions R6 — Exact Low-Rank Branch Inventory Through the 31-Diagonal and Quotient-Block Factorization

Date: 2026-08-26

Canonical predecessors: `MANUSCRIPT_V3_PIPELINE.md`, `MATHEMATICAL_EXTENSIONS_R4.md`, and `MATHEMATICAL_EXTENSIONS_R5.md`

Status: rigorous structural and finite-classification addendum. It corrects an unsupported frontier statement, classifies the repeated-stratum rank-two branches through every remaining diagonal, and replaces undirected search by a quotient-and-factorization proof architecture. It does not prove `C_0(31)` or determine `D_4(C_5^3)`.

## 1. Correction and argument

A previous working summary stated that two exact engines had eliminated every rank-two residual branch on the `26`- and `27`-diagonals and had therefore pushed full-rank forcing through `27`. The committed R5 evidence does not support that statement.

Independent reconstruction gives the following exact result.

- On the `26`-diagonal, the high-multiplicity stratum still has five normalized rank-two forms of profile `4,4,2`.
- On the `27`-diagonal, the high-multiplicity stratum has six normalized rank-two forms: one of profile `4,4` and five of profile `4,2,2`.

Both independent short-zero-sum engines agree on the complete finite state spaces. Thus the currently certified *full-rank-forcing* frontier remains `s+c_4<=25`. The `26`- and `27`-diagonals are finite low-rank branch inventories, not eliminated diagonals.

The correction changes the next proof step. Repeating a larger high-stratum search cannot remove branches that genuinely survive at that level. The missing information is carried by the singleton stratum, total sum, saturation defects, and atom factorization. This addendum makes those quotient and factorization constraints explicit.

## 2. Diagonal equations

Let `S` be a saturated, 5-short-free, total-zero sequence of length `31` over `C_5^3`. Its multiplicities belong to `{1,2,4}`. Let

- `s` be support size;
- `c_i` be the number of support points of multiplicity `i`; and
- `H` be the subsequence formed by the multiplicity-two and multiplicity-four points.

Put

`d=s+c_4`.

The V3 counting equations give

`c_1=2d-31`,

`c_2=31-d-2c_4`,

and

`|H|=62-2d`.

The remaining diagonals are `26<=d<=31`.

## 3. Exact repeated-stratum inventory

**Theorem NQ7 (rank-two branch inventory through `d=31`).**

For every admissible multiplicity row on the diagonals `26<=d<=31`, the rank-two, 5-short-free possibilities for `H`, up to `GL(2,5)` and permutations among equal-multiplicity points, are exactly those in the table.

| `d` | `c_1` | `|H|` | high-stratum profiles | surviving rank-two orbits |
|---:|---:|---:|---|---:|
| 26 | 21 | 10 | `2^5`; `4,2,2,2`; `4,4,2` | `0+0+5=5` |
| 27 | 23 | 8 | `2^4`; `4,2,2`; `4,4` | `0+5+1=6` |
| 28 | 25 | 6 | `2^3`; `4,2` | `2+1=3` |
| 29 | 27 | 4 | `2,2`; `4` | `1+0=1` |
| 30 | 29 | 2 | `2` | `0` |
| 31 | 31 | 0 | empty | `0` |

For profiles `4,4,2` and `4,2,2`, normalize an independent ordered pair to `e_1,e_2` and write the third point as `(u,v)`. In both cases the allowed coordinate set is

`{(1,1),(1,2),(1,3),(1,4),(2,1),(2,3),(3,1),(3,2),(4,1)}`.

The equal-multiplicity symmetry produces five orbits in each profile.

- For `4,4,2`, representatives may be taken as

  `(1,1),(1,2),(1,3),(1,4),(2,3)`.

- For `4,2,2`, representatives may be taken as

  `(1,1),(1,2),(1,3),(1,4),(2,1)`.

For profile `2^3`, there are exactly two `GL(2,5)` orbits, represented by

`{e_1,e_2,e_1+e_2}`

and

`{e_1,e_2,e_1+2e_2}`.

Profiles `4,2` and `2,2` each have one rank-two orbit, represented by an independent pair.

**Proof.** The diagonal equations give the listed profiles. Rank one is checked separately and contributes no rank-two orbit.

For `4,4,2` and `4,2,2`, the repeated points that form the normalized basis must be independent; otherwise their available multiplicities produce a zero sum of length at most five. For each of the sixteen nonzero coordinate pairs `(u,v)`, the bounded coefficient equations for one or two copies of the third point determine whether a zero sum of length at most five exists. Direct evaluation gives the displayed nine pairs. The relevant swap action gives five orbits.

For `2^3`, complete enumeration leaves 720 labeled rank-two supports. The full `GL(2,5)` action partitions them into the two stated orbits. Independent pairs give the unique `4,2` and `2,2` orbits. The `2^4` profile has no survivor. The older R5 classification gives the corresponding `d=26` exclusions.

Completeness is independently checked by two engines on every bounded state: direct submultiplicity enumeration and bounded dynamic programming by subsequence length and group sum. They agree with zero mismatches. ∎

### Finite audit counts

The R6 verifier records:

| profile | rank-two assignments checked | survivors |
|---|---:|---:|
| `4,4,2` | 6,000 | 2,160 |
| `4,2,2` | 6,000 | 2,160 |
| `2^4` | 10,620 | 0 |
| `4,4` | 240 | 240 |
| `2^3` | 2,000 | 720 |
| `4,2` | 480 | 480 |
| `2,2` | 240 | 240 |

These are finite exact classifications of `H`. They are not full-sequence classifications of `S`.

## 4. A diagonal-independent quotient law

Let `rank(span H)<=2`, and choose a plane `P` containing `H`. When `H` is empty, choose any plane. Let `n_0` be the number of singleton terms of `S` that lie in `P`.

**Theorem NQ8 (constant-nineteen off-plane law).**

For every low-rank branch with `26<=d<=31`,

`n_0 <= 2d-50`

and at least nineteen singleton terms lie outside `P`.

**Proof.** The subsequence of terms of `S` lying in `P` is 5-short-free in `P`, which is isomorphic to `C_5^2`. Since

`eta(C_5^2)=13`,

its length is at most twelve. The high stratum contributes all `|H|=62-2d` of its terms inside `P`, so

`n_0 + |H| <= 12`.

Therefore

`n_0 <= 12-(62-2d)=2d-50`.

The total number of singleton terms is `c_1=2d-31`, so the number outside `P` is at least

`(2d-31)-(2d-50)=19`. ∎

**Corollary NQ9.** At least one of the four nonzero cosets of `P` contains five singleton terms.

This constant lower bound is the reason a quotient-space argument remains informative even as `H` becomes too small to force rank three.

## 5. Exact atom-length corridor

Every zero-sum sequence factors into atoms. The ordinary Davenport constant of `C_5^3` is thirteen, while 5-short-freeness makes every atom length at least six.

**Theorem NQ10 (atom partition corridor).**

Every putative sequence `S` factors into `t` atoms with `3<=t<=5`. After sorting their lengths, the possible partitions of `31` are exactly:

### Three atoms

`(6,12,13)`, `(7,11,13)`, `(7,12,12)`, `(8,10,13)`, `(8,11,12)`, `(9,9,13)`, `(9,10,12)`, `(9,11,11)`, `(10,10,11)`.

### Four atoms

`(6,6,6,13)`, `(6,6,7,12)`, `(6,6,8,11)`, `(6,6,9,10)`, `(6,7,7,11)`, `(6,7,8,10)`, `(6,7,9,9)`, `(6,8,8,9)`, `(7,7,7,10)`, `(7,7,8,9)`, `(7,8,8,8)`.

### Five atoms

`(6,6,6,6,7)`.

**Proof.** Atom lengths lie in `[6,13]` and sum to `31`. Hence

`ceil(31/13)<=t<=floor(31/6)`,

so `3<=t<=5`. The displayed list is the complete integer partition enumeration under those bounds. ∎

This replaces the earlier focus on two selected four-atom patterns by a complete finite corridor of twenty-one patterns.

## 6. Quotient-block factorization of an atom

Let

`pi:C_5^3 -> C_5^3/P`, where the quotient is isomorphic to `C_5`

be the quotient map.

**Theorem NQ11 (quotient-block factorization lemma).**

Let `U` be an atom in `C_5^3`. Factor the quotient word `pi(U)` into disjoint minimal nonempty zero-sum blocks

`V_1 ... V_q`.

Lift each block to its original positions in `U` and let

`p_i in P`

be its lifted sum. Then exactly one of the following holds.

1. `q=1` and `p_1=0`; the single quotient block is all of `U`.
2. Every `p_i` is nonzero and `p_1...p_q` is an atom in `P`. In particular, `q<=D(P)=9`.

**Proof.** If some `p_i=0`, its lifted positions form a nonempty zero-sum subword of `U`. Atomicity forces that block to be all of `U`, so there are no other quotient blocks.

Otherwise every `p_i` is nonzero. Their total is zero because their lifted blocks partition `U`. If a proper nonempty subword of `p_1...p_q` summed to zero, the union of the corresponding lifted blocks would be a proper nonempty zero-sum subword of `U`, contradicting atomicity. Thus the transfer-sum word is an atom in `P`, and its length is at most `D(C_5^2)=9`. ∎

This is the factorization object that a recursive exact search should enumerate: minimal quotient blocks, their lifted plane sums, and a plane atom. It is substantially smaller and more interpretable than an undirected search over all 31-term sequences.

### Length-thirteen fixture

Let

`U=e_1^4 e_2^4 e_3^4 (e_1+e_2+e_3)`.

This is a length-thirteen atom in `C_5^3`. Quotient by the plane spanned by `e_1,e_2`. The quotient word has eight zero letters and five copies of the nonzero generator. Its minimal quotient blocks are the eight one-letter zero blocks and one five-letter block. Their lifted sums form

`e_1^4 e_2^4 (e_1+e_2)`,

a length-nine atom in the kernel plane. The R6 verifier checks atomicity of both words by complete bounded submultiplicity enumeration.

## 7. Adversarial quotient census on the 27-diagonal

For a rank-two `27`-diagonal branch, let

`(n_0,n_1,n_2,n_3,n_4)`

count singleton terms in the five quotient residues. Theorem NQ8 gives `n_0<=4`; total sum gives

`sum_r n_r=23`

and

`sum_r r n_r=0 mod 5`.

Projecting the singleton saturation defect gives a further necessary condition: after removing a singleton of nonzero residue `r`, one to three remaining residues must sum to `3r`. Zero-residue high-stratum terms make the residue-zero condition automatic.

Two independently implemented finite engines enumerate the count vectors and the bounded defect condition:

- direct combinations with replacement; and
- bounded dynamic programming by length and residue.

They agree exactly. Of 2,047 count vectors satisfying the size, plane-cap, and total-sum constraints, 2,043 survive the projected defect test. Only four are rejected.

**Conclusion.** Quotient counts alone do not eliminate any of the six normalized `27`-diagonal rank-two branches. A valid next proof must retain lifted plane sums and atom structure as in Theorem NQ11. This negative result prevents a false promotion from a weak quotient census.

## 8. Recursive proof program

The nonquantum lane now has a finite, theorem-driven recursion.

1. Select one normalized high-stratum branch from Theorem NQ7.
2. Choose its plane `P` and impose the constant-nineteen law.
3. Select one of the twenty-one atom-length partitions from Theorem NQ10.
4. Factor every atom through `C_5^3/P` using Theorem NQ11.
5. Enumerate only minimal quotient blocks and their transfer sums in `P`.
6. Reject a candidate by an independently implemented short-zero-sum engine.
7. Promote an elimination only when the lifted plane argument or a complete finite certificate covers every branch.

Exact search is therefore an adversarial verifier for a finite symbolic decomposition, not the source of an opaque global theorem.

## 9. Atomic status

- Corrected full-rank-forcing frontier `d<=25`: `VERIFIED` against the committed theorem chain.
- `d=26` high-stratum rank-two inventory: five forms, `FINITE_EXACT`.
- `d=27` high-stratum rank-two inventory: six forms, `FINITE_EXACT`.
- `d=28,29` high-stratum orbit inventory: `FINITE_EXACT`.
- Constant-nineteen off-plane law: `VERIFIED`.
- Complete atom-length corridor: `VERIFIED` by bounded integer partition.
- Quotient-block factorization lemma: `VERIFIED`.
- Length-thirteen transfer fixture: `FINITE_EXACT`.
- Elimination of the `26`- or `27`-diagonal full-sequence branches: `UNRESOLVED`.
- `C_0(31)` and exact `D_4(C_5^3)`: `UNRESOLVED`.

## 10. Remaining scientific frontier

The highest-value next target is the lifted plane problem for the eleven normalized branches on diagonals `26` and `27`. The constant-nineteen law and atom corridor now bound every such branch, while Theorem NQ11 supplies a recursive factorization into quotient blocks and a plane atom. A successful elimination must bind those objects to the singleton saturation defects. Widening the old repeated-stratum enumeration would repeat a level that is already exactly classified.

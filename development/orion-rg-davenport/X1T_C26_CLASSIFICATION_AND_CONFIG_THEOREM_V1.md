# ORION-RG X1-T — `C_2^6` classified via the decomposition theorem, and the configuration theorem behind it

## The engineering move: X1-K is an algorithm

Direct enumeration of the `C_2^6` witness set failed (X1-S: 600 s, no output). The reason
turned out to be that the answer is ~3.4 **billion** witnesses — no direct enumeration can
even write it down. The route around it:

Over `F_2`, zero-sum-free ⟺ linearly independent, so a *maximal* zero-sum-free sequence of
length `d(C_2^r) = r` is exactly a **basis**. Where the X1-K criterion holds (`r = 5, 6`,
both proved), every witness has minimum zero-sum exactly `m = 4` and factors as

```
witness = (affine plane {a, b, c, a⊕b⊕c}) ∪ (basis of F_2^r)
```

Mod `GL(r,2)`, fix the basis standard: the search space collapses from ~10^12 states to
~10^3 candidate 4-sets. `C_2^6` then closes in **10.2 seconds**.

## The `Z_S` structure lemma

For `W = B_0 ∪ A` with `B_0` the standard basis and `A = {a_1..a_4}`: a subset of `W` is a
zero-sum iff it is `Z_S = {a_i : i ∈ S} ∪ supp(⊕_{i∈S} a_i)` for a nonempty `S ⊆ [4]` (the
basis part is forced elementwise). So `W` has **exactly 15 zero-sums**, and two are disjoint
iff `S ∩ T = ∅` and `supp(x_S) ∩ supp(x_T) = ∅`. Every representative below indeed shows
`#ZS = 15`.

## The configuration theorem

Describe `A` by its columns: coordinate `j` sees an even subset of the four rows — empty,
a pair (an **edge** on vertex set `[4]`), or all four (**full**). Let `f` = #full columns,
`G` = the multigraph of edge-columns.

> **Theorem.** `W = B_0 ∪ A` is a witness ⟺
> **(C1)** `f ≥ 1`, or `G` covers all six pairs; and
> **(C2)** every vertex of `G` has at least 2 distinct neighbours.

*Proof.* Case analysis of disjoint pairs `(S,T)`. `(|S|,|T|) = (1,3)` and `(2,2)` are
automatic (`x_{[4]∖i} = a_i`; complementary pairs have equal supports, nonzero by C2 ⇒
distinctness). `(1,1)` needs a common column of `a_i, a_j`: a full column or the edge
`{i,j}` — that is C1. `(1,2)` needs an edge at `i` hitting exactly one of `{j,k}` (full
columns cancel in `x_{jk}`), which across the three pairs from the complement of `i` is
exactly "`i` has two distinct neighbours" — C2. Weight conditions (`min-ZS ≥ 4`) come free
from Lemma A at length `r + 4`. ∎

**Exhaustive verification, both directions:** all 65 candidates at `r = 5` and all 1,855
at `r = 6` — **zero mismatches** (`x1t_config_characterisation_check.py`).

The survivor census also matches the hand-derived counting exactly:

| config (`f`, `z`, edges) | hand-predicted | enumerated |
|---|---|---|
| `r=5`: 1, 0, C4 | `5·3·24/24 = 15` | 15 |
| `r=6`: 1, 1, C4 | 90 | 90 |
| `r=6`: 1, 0, C4+doubled edge | 180 | 180 |
| `r=6`: 2, 0, C4 | 45 | 45 |
| `r=6`: 0, 0, K4 | 30 | 30 |
| `r=6`: 1, 0, K4−e (diamond) | 180 | 180 |
| total `r=6` | **525** | **525** |

## The `C_2^6` classification: four `GL(6,2)`-orbits

| orbit size | `|Stab|` | decomps | representative `A` | configuration |
|---|---|---|---|---|
| 279,982,080 | 72 | 9 | `{7,11,21,25}` | full + C4 + empty column |
| 1,259,919,360 | 16 | 5 | `{7,11,53,57}` | full + C4 with a doubled edge |
| 167,989,248 | 120 | 5 | `{7,25,42,52}` | K4, no full column |
| 1,679,892,480 | 12 | 3 | `{7,25,43,53}` | full + diamond (K4−e) |

**Total: `D_2`-extremal witnesses of `C_2^6` = 3,387,783,168.**

Validation stack: (i) the pipeline reproduces `r = 3` (1 orbit, 7, stab 24) and `r = 5`
(1 orbit, 138,880, stab 72 — matching X1-S computed by a different method), with the
survivor count 15 equal to a direct count from the stored `r = 5` witness file; (ii) every
orbit satisfies `|orbit|·|Stab| = |GL(6,2)| = 20,158,709,760` with integer stabilisers;
(iii) the pair-counting identity `#survivors = Σ|orbit|·decomps / #bases` holds exactly
(525.0); (iv) all four representatives re-verified as witnesses by an independent code
path; (v) an independent count of witnesses-containing-the-basis-with-*any*-complement
(14,685 at `r = 6, k = 4`) is reproduced exactly from the orbit inventory via
`Σ|orbit|·b(rep)/#bases` with exact division.

**Configurations are not GL-invariants.** The 45 `f = 2` A-sets lie in the same orbit as the
180 doubled-edge ones (the orbit's survivor class has 225 = 180 + 45): the graph description
depends on which decomposition you take, and witnesses have several (`decomps` column).

## Small-`r` table complete, and two X1-S items closed

| `r` | 2 | 3 | 4 | 5 | 6 |
|---|---|---|---|---|---|
| `GL`-orbits | 2 | 1 | 3 | 1 | **4** |

(`r = 2` computed this session: 9 witnesses — multiplicities allowed there, squarefreeness
is not forced below `r = 3` — in orbits of sizes 6 + 3.)

- X1-R's open item, the geometric split of the `C_2^4` 2520/840 orbits, is resolved by the
  **line count** of the support: 2520 ↔ 2 lines, 840 ↔ 4 lines, 120 ↔ 0 lines — a complete
  separating invariant (histogram multiplicities match the orbit sizes exactly).
- X1-S's tentative alignment "decomposition failure ⟷ heterogeneous witness set" (hedged
  there as two data points, not a law) is now **dead**: `C_2^6` has 4 orbits and the
  criterion holds. Orbit-heterogeneity and criterion failure are independent.

## General-`r` consequence

For every `r ≥ 5`, the config (`f = 1`, C4, `z = r − 5`) satisfies C1∧C2, so explicit
length-`(r+4)` witnesses exist and `D_2(C_2^r) ≥ r + 5` — a self-contained re-proof (the
bound itself is Freeze–Schmid Thm 4.1 at `s = 4` for `r ≥ 6`). What the theorem adds is the
complete inventory of *this witness type* for all `r`, pinned to a 4-vertex multigraph
classification. Continuation: X1-U uses the same machinery at the open frontier `r ≥ 7`.

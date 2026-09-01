# Mathematical Extensions R7 — Saturation-Driven Refactorization of the Final Near-Squarefree Branch

Date: 2026-08-26

Canonical predecessors: `MANUSCRIPT_V3_PIPELINE.md`, `MATHEMATICAL_EXTENSIONS_R4.md`, `MATHEMATICAL_EXTENSIONS_R5.md`, and `MATHEMATICAL_EXTENSIONS_R6.md`.

Status: structural theorem addendum. It does not determine `D_4(C_5^3)` or prove `31 in C_0(C_5^3)`. It gives a complete local reduction for the only diagonal-30 atom configuration left by R6.

## 1. Frozen obstruction state

Assume the declared corridor hypotheses and suppose the upper alternative produces a length-31 total-zero sequence `S` over `C_5^3` with no nonempty zero-sum subsequence of length at most five.

Repository replays eliminate support at most 22. Saturation excludes multiplicity three. The R5/R6 atom-deficit analysis eliminates the all-squarefree diagonal and gives the following diagonal-30 state:

- support size 30;
- one point `x` has multiplicity two and every other point is a singleton;
- `S` has an atom factorization of type `(6,6,7,12)`;
- the four atom supports are pairwise disjoint;
- the three short atoms are squarefree;
- the length-12 atom is `U=x^2 T`, where `T` is squarefree of length ten and `sigma(T)=3x`.

The competing `(6,6,6,13)` type is impossible because a length-13 atom consumes at least two units of internal support deficit, while the whole sequence has deficit one.

## 2. Saturation certificate at the double point

Because `S` is saturated and `x` has multiplicity two, the saturation-defect lemma supplies an `x`-free subsequence `R` with

`1 <= |R| <= 2`

and

`sigma(R)=2x`.

Appending one further `x` would create the short zero sum `x^3 R`. The existing sequence does not contain that third copy. The location of `R` nevertheless forces an exact structural trichotomy.

## 3. Refactorization trichotomy

**Theorem NQ-R7.1 (double-point trichotomy).** Exactly one of the following holds.

1. **Internal branch.** Every term of `R` lies in `T`.
2. **External branch.** No term of `R` lies in `U`. If the short atoms touched by `R` are `V_i` and `R_i=R gcd V_i`, then

   `A=T R`

   and

   `B=x^2 product_i (V_i R_i^{-1})`

   are nonempty zero-sum sequences and

   `U product_i V_i = A B`.

3. **Mixed branch.** `|R|=2`, with `R=yz`, one term in `T` and one outside `U`. In the quotient `C_5^3/<x>`, their images are opposite: `bar(y)+bar(z)=0`.

**Proof.** The location cases are exhaustive. In the external case, `sigma(A)=3x+2x=0`. Since each touched atom has sum zero, `sigma(B)=2x-sigma(R)=0`. The displayed multiset identity is immediate. In the mixed case, reducing `y+z=2x` modulo `<x>` gives the quotient relation. ∎

The theorem replaces an unrestricted saturated completion by three exact grammars.

## 4. One-atom external branch

If `R` lies in one short atom `V`, then the original two atoms `U,V` are replaced by two zero-sum factors `A,B`. Because the whole sequence has maximum factorization length four, both `A` and `B` must be atoms; otherwise the unchanged two atoms plus a decomposition of `A` or `B` would give at least five factors.

Let `ell=|V|` and `r=|R|`. The new atom lengths are `|A|=10+r` and `|B|=ell+2-r`. The only rows are:

| `ell` | `r` | new lengths |
|---:|---:|---|
| 6 | 1 | `(11,7)` |
| 6 | 2 | `(12,6)` |
| 7 | 1 | `(11,8)` |
| 7 | 2 | `(12,7)` |

Every surviving external certificate must therefore realize one of four overlapping-atom exchange patterns.

## 5. Quotient meaning

If `|R|=1`, then its term is `2x` and lies in the one-dimensional kernel direction.

If `|R|=2`, the two images form a length-two zero sum in `C_5^2` unless both are individually in `<x>`. In the mixed branch the length-two quotient atom is forced. This can be intersected directly with the R6 quotient lift-coefficient patterns `(1,2)` and `(1,1,1)`.

The next exact search should therefore enumerate quotient atoms and lift coefficients, not ambient 30-point supports.

## 6. Global compressed theorem

**Theorem NQ-R7.2 (compressed upper-alternative obstruction).** Any obstruction arising from the upper corridor alternative must satisfy all of:

1. support at least 23;
2. multiplicities only `1,2,4`;
3. the exact multiplicity equations;
4. the rank-forcing and finite rank-two exclusions already proved on lower diagonals;
5. one of the two four-atom length patterns;
6. the R6 atom-deficit and quotient restrictions;
7. on diagonal 30, the trichotomy of Theorem NQ-R7.1.

No one item is promoted to an exact `D_4` decision.

## 7. Why this is a scientific advance

The saturation certificate is often treated only as a local covering condition. Here it creates an alternative zero-sum factorization of the extremal object. This links short-subset-sum saturation, atom support deficit, and nonunique factorization length.

The reduction is useful beyond the present constant: similar defect certificates in exponent-`p` groups can be tested for refactorization whenever one atom contains all copies of a repeated point.

## 8. Potential applications

Generalized Davenport constants govern factorization lengths in block monoids. The refactorization theorem translates a short-subset-sum covering condition into a restriction on alternative factorizations.

The same sequence model can be read as a finite-field checksum system: a short zero sum is a small subset collision. Structural classifications of near-extremal collision-free multisets may inform restricted subset-sum codes and finite-geometric designs. These are potential applications, not claims of a new coding bound.

## 9. Atomic status

- Support-at-least-23 repository result: `BOUNDED_EXACT` with independent replay; no theorem/novelty promotion beyond its declared scope.
- Diagonal-30 frozen state: inherited `VERIFIED` from R6 proof and verifier.
- Saturation certificate: inherited `VERIFIED`.
- Refactorization trichotomy: `VERIFIED` algebraically.
- One-atom atomity and length table: `VERIFIED`.
- Elimination of all three branches: `UNRESOLVED`.
- `31 in C_0(C_5^3)` and exact `D_4(C_5^3)`: `NOT_CLAIMED`.

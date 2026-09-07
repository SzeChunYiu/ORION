# The packing profile of the binary cube in `C_n^3`, uniformly in `n` — V3

Status: **exact values computed for every odd `n ≤ 13`; closed-form formulas conjectured for all odd `n`, with the lower-bound families proved by hand for all odd `n`**. Priority: CANNOT_CHECK (host egress blocks arXiv, ScienceDirect, ResearchGate; see ledger row C7-DONOR-1). Supersedes and strictly strengthens `SUPPORT7_BINARY_CUBE_THEOREM_V1.md`.
Checkers: `cube_packing_profile_v3.py` (pure Python, independent recomputation), `tools/cube_profile_v3.c` (mixed-radix DP for larger `n` and other supports).
Branch: `claude/orion-research-frontier-3ck9yt`.

## 0. Why this exists

The V1 packet proved one instance: no length-37 zero-sum sequence over `C_7^3` supported on the nonzero binary cube with multiplicities `≤ 6` has packing number `≤ 3`. That is a single negative at a single prime. It leaves open whether the cube fails narrowly (and so might succeed at another `n`, or under a small perturbation) or by a wide margin.

Following the lane's own lesson from the `QG47 → QG48` revival (an exhaustive `n = 2` EMPTY was attributed to the **slice dimension**, not to structural absence, and the `n → 3` lever reopened the territory), the fix here is to stop working prime-by-prime and make `n` a free parameter. The cube is defined for every `n`; its packing profile is a function of `n`; that function is what this record computes.

## 1. Definitions

Let `n ≥ 3` be odd, `G = C_n^3`, basis `e_1,e_2,e_3`, and

    Q = {e_1, e_2, e_3, e_12, e_13, e_23, e_123}   (the seven nonzero points of {0,1}^3),

with `e_12 = e_1+e_2`, etc. A *cube multiplicity vector* is `m ∈ [0, n−1]^7` read in the fixed order `(e_1,e_2,e_3,e_12,e_13,e_23,e_123)`; the cap `n−1` is forced for any packing-critical sequence (Lemma 2.1 of `OBSTRUCTION_REDUCTION_LEMMAS_V2.md`). Write `pk(m)` for the zero-sum packing number, `|m| = Σ m_i`, and `c_j(m) ∈ Z_{≥0}` for the `j`-th **integer** coordinate sum. Define

    c_j(n) = max{ |m| : m ∈ [0,n−1]^7, pk(m) ≤ j },
    z_j(n) = max{ |m| : m ∈ [0,n−1]^7, m zero-sum, pk(m) ≤ j }.

`c_j` bounds the `D`-constants from below: `D_{j+1}(C_n^3) ≥ c_j(n) + 1`. `z_j` is the quantity relevant to obstructions: by Lemma 1.2 of the reduction record, a `D_{j+1}`-obstruction supported on `Q` is exactly a cube-supported zero-sum `m` with `pk(m) ≤ j` and `|m| = D_{j+1}(C_n^3) + 1 − 1`.

## 2. The table (exact, machine-computed)

Every entry is the exact optimum of the mixed-radix dynamic programme over the whole box `[0,n−1]^7` (atoms, then packing number for every one of the `n^7` vectors). Witnesses are printed by the checker.

| n | c_0 | c_1 | c_2 | c_3 | c_4 | z_1 | z_2 | z_3 | z_4 | pk(full cube) |
|---|---|---|---|---|---|---|---|---|---|---|
| 3 | 6 | 10 | 13 | 14 | 14 | 7 | 11 | 12 | 12 | 3 |
| 5 | 12 | 19 | 24 | 26 | 28 | 13 | 20 | 22 | 27 | 4 |
| 7 | 18 | 28 | 35 | 38 | 42 | 19 | 29 | 32 | 39 | 4 |
| 9 | 24 | 37 | 46 | 50 | 56 | 25 | 38 | 42 | 51 | 4 |
| 11 | 30 | 46 | 57 | 62 | 70 | 31 | 47 | 52 | 63 | 4 |
| 13 | 36 | 55 | 68 | 74 | 84 | 37 | 56 | 62 | 75 | 4 |

Every entry is affine in `n`:

    c_0 = 3n − 3        c_1 = (9n − 7)/2     c_2 = (11n − 7)/2    c_3 = 6n − 4      c_4 = 7n − 7
    z_1 = 3n − 2        z_2 = (9n − 5)/2     z_3 = 5n − 3         z_4 = 6n − 3

with exactly two exceptions, both at `n = 3`, where the cube is too small: `c_3 = c_4 = 14 = 7n−7 < 6n−4` is impossible only because `6n−4 = 14` coincides there, and `z_4(3) = 12 < 6n−3 = 15`. For `n ≥ 5` all eight formulas hold for every computed `n`.

## 3. What is proved for all odd `n`

**Lemma 3.1 (no unary block).** Every nonempty zero-sum `b ≤ m` has at least two coordinates `j` with `c_j(b) > 0`.

*Proof.* Suppose `c_2(b) = c_3(b) = 0`. Then `b_2 = b_12 = b_23 = b_123 = 0` (these are the points with a 1 in coordinate 2) and `b_3 = b_13 = 0`, leaving `b = b_1 e_1` with `c_1(b) = b_1 ≤ n−1 < n`, so `b` is not zero-sum unless empty. The other two cases are the same by symmetry. ∎

**Lemma 3.2 (counting bound).** Writing `s = m_1+m_2+m_3`, `u = m_12+m_13+m_23`, `v = m_123`,

    pk(m) ≤ ⌊ (c_1(m)+c_2(m)+c_3(m)) / (2n) ⌋ = ⌊ (s + 2u + 3v) / (2n) ⌋.

*Proof.* Disjoint blocks satisfy `Σ_t c_j(b^{(t)}) ≤ c_j(m)` for each `j`. Each nonzero `c_j(b)` is a positive multiple of `n`, and by Lemma 3.1 at least two of them are nonzero, so each block contributes at least `2n` to `Σ_j c_j`. ∎

**Theorem 3.3 (`c_0`).** `c_0(n) = 3(n−1)` for every odd prime power `n`. The lower bound `e_1^{n−1} e_2^{n−1} e_3^{n−1}` is zero-sum-free for every `n` (a zero-sum sub-multiset would need `b_j ≡ 0 (mod n)` with `b_j ≤ n−1`); the upper bound is Olson's `D(C_n^3) = 3n−2`.

**Theorem 3.4 (`c_1`, `c_2` lower bounds).** For every odd `n`, `c_1(n) ≥ (9n−7)/2` and `c_2(n) ≥ (11n−7)/2`, witnessed by the families `S_2(n)`, `S_3(n)` of `CUBE_FAMILY_LOWER_BOUNDS_V2.md` (proved there by coordinate counting, for all odd `n`, prime or not).

**Theorem 3.5 (`c_1` upper bound for prime powers).** `c_1(n) = (9n−7)/2` whenever `D_2(C_n^3) = (9n−5)/2` is known — in particular for `n = p^a`, `p ≥ 5` prime (donor route, `D2_PRIME_POWER_COROLLARY_V1.md`), for `n = 7` (self-contained, `SPECTRUM_CONGRUENCE_THEOREM_V2.md` Theorem A), and for `n = 3, 5` (exhaustive, `EXHAUSTIVE_ANALOG_RESULTS_V2.md`).

**Corollary 3.6 (`z_1`).** `z_1(n) = 3n−2 = D(C_n^3)` for odd prime powers `n`: the cube contains a minimal zero-sum sequence of the maximal possible length, namely `e_1^{n−2} e_2^{n−1} e_3^{n−1} e_12 e_13` (coordinate sums `n, n, n`), and no zero-sum sequence over `C_n^3` of length `> D(G)` is an atom.

The remaining upper bounds (`c_2`, `c_3`, `c_4`, `z_2`, `z_3`, `z_4`) are **verified exactly for `n ≤ 13`** and **open in general**. §5 explains why they are expected to be affine in `n` and what a proof would have to supply.

## 4. The consequence for the frozen question

By Lemma 1.2 of the reduction record, a `D_3`-obstruction over `C_n^3` supported on the cube would be a cube-supported zero-sum multiplicity vector of length `(11n−3)/2` with packing number 3, i.e. it would need

    z_3(n) ≥ (11n − 3)/2.

The computed values give the opposite, with room to spare:

| n | z_3(n) = 5n−3 | needed (11n−3)/2 | shortfall (n+3)/2 |
|---|---|---|---|
| 5 | 22 | 26 | 4 |
| 7 | 32 | 37 | 5 |
| 9 | 42 | 48 | 6 |
| 11 | 52 | 59 | 7 |
| 13 | 62 | 71 | 8 |

**The cube does not merely fail to host a `D_3` obstruction at `n = 7` (the V1 statement); it fails at every computed `n`, and the shortfall grows linearly, as `(n+3)/2`.** The same computation shows the cube is *exactly* extremal for the non-zero-sum problem (`c_2 = (11n−7)/2` is the `D_3` lower bound), so the cube is simultaneously the best known `D_3` lower-bound geometry and a geometry that is quantitatively far from producing a counterexample. The V1 elimination is therefore not a near miss.

Two further readings of the same table:

- `z_2(n) = (9n−5)/2 = D_2(C_n^3)` exactly, for every computed `n`. The maximal cube-supported zero-sum sequence that factors into at most two atoms has precisely the `D_2` length. Over all supports that maximum is `D_3(C_n^3) − 1 = (11n−7)/2`, so **the cube is not extremal for the zero-sum form of the `D_3` problem**, even though it is extremal for the sequence form. The extremal objects for `D_3` are the sequences `S` of length `(11n−7)/2` whose zero-sum completion `S·(−σ(S))` leaves the cube.
- `c_3(n) = 6n−4 < (13n−7)/2` for `n ≥ 5`: the cube cannot even realise the `D_4` lower bound. An eighth support point is necessary, and one suffices — see `DK_ARITHMETIC_CONJECTURE_V3.md`.

## 5. Why the values are affine in `n`: the fractional cube polytope

Let `A` be the `3 × 7` incidence matrix of `Q` (columns = points, rows = coordinates). Because every coordinate sum is at most `4(n−1) < 4n`, each zero-sum block `b` has a **profile** `π(b) = (c_1(b)/n, c_2(b)/n, c_3(b)/n) ∈ {0,1,2,3}^3`, an object independent of `n`. Rescaling `y = m/n ∈ [0,1)^7` and `z^{(t)} = b^{(t)}/n`, a `j+1`-packing becomes a rational feasibility problem

    A z^{(t)} = π^{(t)} ∈ Z^3_{≥0} \ {0},   z^{(t)} ≥ 0,   Σ_t z^{(t)} ≤ y,

whose data no longer involve `n`. Hence the leading coefficients `(3, 9/2, 11/2, 6, 7)` and `(3, 9/2, 5, 6)` are values of a finite linear programme over a fixed polytope, and the constant terms are the bounded arithmetic correction from rounding.

The **halves are forced by a determinant**: the `3×3` minor of `A` on the columns `e_12, e_13, e_23` is

    [[1,1,0],[1,0,1],[0,1,1]],   determinant −2,

so `⟨e_12, e_13, e_23⟩` has index 2 in `⟨e_1,e_2,e_3⟩` and the relevant polytope has half-integral vertices. This is exactly where the multiplicities `(n±1)/2` in the extremal families come from, and — via `D_2(C_n^3) = (9n−5)/2 = D(C_n^3) + n + (n−1)/2` — it is the source of the `(n−1)/2` by which the generalized Davenport constants of `C_n^3` exceed the naive value `D(G) + (k−1)exp(G)`. See `DK_ARITHMETIC_CONJECTURE_V3.md`.

A complete proof of the table for all `n` requires: (i) the explicit affine families (§3, done for `c_0, c_1, c_2`; `c_3, c_4, z_j` families are read off the witnesses in the JSON and are affine in `n` for all computed `n`); and (ii) matching upper bounds by an integral rounding argument for each of the finitely many profile tuples. Step (ii) is not carried out here and is the natural next unit of work.

## Claim ceiling

The table is exact for `n ≤ 13` and is a conjecture beyond. Nothing here decides `D_3(C_7^3)`: it shows that one specific geometry cannot produce a counterexample and quantifies by how much. No novelty or priority is claimed for any formula.

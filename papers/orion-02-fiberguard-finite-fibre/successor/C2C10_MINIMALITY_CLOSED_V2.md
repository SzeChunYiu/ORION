# C2-C10 minimality — closed form V2 (symmetry reduction)

**Status: certified.** The STILL-OPEN §6 obstruction of
`C2C10_MINIMALITY_ATTEMPT_V1.md` (G_Π non-monotone under block splits, so no
exchange lemma) is bypassed, not solved: a permutation-symmetry lemma reduces
the competitor search from set partitions of [m] (Bell(m)) to **integer
partitions of m** (p(m) ≈ e^{π√(2m/3)}/(4m√3)), making the exact Kmin a
closed-form maximization. The reduction + closed forms reproduce **all ten
exhaustively-known values exactly** (m = 5..10, L ∈ {1,2}). Harness:
`verify_c2c10_profile.py` (this directory), run with no args → `ALL MATCH`,
exit 0.

## 1. Symmetry lemma

The C2-C10 instances are the two families {0}∪S, S ⊆ [q], q = m−1, split by
parity ε(S) = |S| mod 2 (ε = 1 in the instance whose parity equals
parity(q); f([m]) = ε·L). Every σ ∈ S_q permutes variables only (0 fixed,
|σ(S)| = |S|), hence maps each family **onto itself** and conjugates a
partition Π into Π^σ with the same block-size multiset and the anchor block
({0}∪…) mapped to the anchor block. The per-block terms w_i, f_i of
C_Π(0) (V1 §4 table) depend only on (block size, anchor membership), and
d, b likewise only on sizes. Therefore

> **C_Π(0) factors through (block-size profile, anchor-designated size
> class, ε)** — and so does G_Π = C_one(0) − C_Π(0), and by Lemma 2 of V1,
> Kmin = max over proper profiles, anchor classes, ε of ⌊G/(2k−1)⌋ + 1
> (G > 0), k = #blocks.

No monotonicity under splits is required: the enumeration over profiles is
exhaustive over competitor structures *by the lemma*, which is what the §6
exchange lemma was trying to buy.

## 2. Per-block closed forms (V1 table, completed at the boundaries)

For a block S of size s, N = 2^{m−2}·L:

| role | w(S) | f(S) |
|---|---|---|
| anchor block, any s = 1..m−1 | N + (s−1)·N/2 | N/2^{s−1} |
| variable block, s ≤ q−1 | s·N/2 | N/2^s |
| variable block, s = q (all variables) | q·N/2 | **ε·L** |

The two boundary cases are the ones the naive power-of-two reading gets
wrong: (i) the anchor formula N/2^{s−1} holds *at* s = m−1 (then
{0}∪[q]\{j}: the block spans all but one variable, f = N/2^{q−1} = 2L);
(ii) a variable block of size exactly q forces the profile {0}∪[q] (k = 2,
anchor singleton), and only the ε·L columns of the matching instance contain
its conjunction — the naive formula N/2^s would give L/2 regardless of ε,
wrong at both ε = 0 (true 0) and ε = 1 (true L).

Per-block cost term: 2f + (b(s)+2)(w − s·f), with b(s) = ⌈log₂ s⌉ (b(1)=0),
d(1)=0, d(s)=d(⌈s/2⌉)+d(⌊s/2⌋)+s−2; and
C_one(0) = (b(m)+1)·W + m−1 + d(m) + b(m) − [m(b(m)+1)−1]·ε·L,
W = N(m+1)/2.

## 3. Certification

Profile formula vs the exhaustive set-partition search (V1 §6, hard values):

| m | L | profile | exhaustive | | m | L | profile | exhaustive |
|---|---|---|---|---|---|---|---|---|
| 5 | 1 | 13 | 13 ✓ | | 8 | 1 | 88 | 88 ✓ |
| 5 | 2 | 26 | 26 ✓ | | 8 | 2 | 175 | 175 ✓ |
| 6 | 1 | 25 | 25 ✓ | | 9 | 1 | 273 | 273 ✓ |
| 6 | 2 | 49 | 49 ✓ | | 10 | 1 | 552 | 552 ✓ |
| 7 | 1 | 44 | 44 ✓ | | | | | |
| 7 | 2 | 87 | 87 ✓ | | | | | |

**10/10 exact.** Ten points span every binding structure the exhaustive
search ever produced (pairs, triples, quads, mixed), so the certification
exercises every branch of the closed forms including both boundary cases —
the maximization places a 3-block under both roles at m = 5 (profile (3,2),
anchor class enumerated at 2 and 3), and m = 6/8 bind at all-2s profiles
while m = 7 binds at the mixed (3,2,2).

## 4. Exact values beyond the exhaustive frontier

Certified-formula outputs (exhaustive search not run at m ≥ 11 — Bell(11) =
678,985 and column-structure evaluation is Θ(N) per partition):

| m | L | Kmin | binding profile (anchor class, ε) |
|---|---|---|---|
| 9 | 2 | 545 | (4,3,2), anchor 2, ε=0 |
| 10 | 2 | 1102 | (4,4,2), anchor 2, ε=0 |
| 11 | 1 | 1,051 | (4,4,3), anchor 3, ε=0 |
| 12 | 1 | 2,050 | (4,4,4), anchor 4, ε=0 |
| 13 | 1 | 3,951 | (4,4,3,2), anchor 2, ε=0 |
| 14 | 1 | 7,974 | (4,4,4,2), anchor 2, ε=0 |
| 15 | 1 | 15,362 | (4,4,4,3), anchor 3, ε=0 |
| 16 | 1 | 30,267 | (4,4,4,2,2), anchor 2, ε=0 |
| 20 | 1 | 788,892 | (8,8,4), anchor 4, ε=0 |
| 24 | 1 | 11,936,917 | (8,8,4,4), anchor 4, ε=0 |
| 30 | 1 | 727,012,697 | (4,4,4,4,4,4,4,2), anchor 2, ε=0 |
| 40 | 1 | 1,390,868,116,280 | (16,16,8), anchor 8, ε=0 |

(L is not a clean doubling: ⌊G/(2k−1)⌋+1 breaks linearity — (9,2) = 545 =
2·273 − 1.)

## 5. Structure of the binding competitor (exact, m ≤ 40)

- Always **ε = 0** (the instance *not* matching parity(q)): C_one(0) is
  larger there (no ε·L deduction) while C_Π(0) is nearly ε-flat, so G is
  maximized at ε = 0. The V1 observation "binding competitor always
  matching-type" is refined: the binding *instance* is the non-matching one.
- The anchor always sits in a **small block** (size 2–4 ≤ ⌈log₂ m⌉): the
  anchor block enjoys the N/2^{s−1} f-discount, which a small anchor block
  converts into the cheapest possible w − s·f while keeping its w-premium.
- Competitor blocks are **coarse** (2–4 for m ≤ 16; powers of two, near
  ⌈m/3⌉·2^j balanced, for larger m): coarse blocks cut Σ 2f(S) (f decays as
  N/2^s) at bounded (b+2)-coefficient cost — the same force the V1 bracket
  upper bound K0 guessed, now confirmed exactly.

## 6. Reproduce

```bash
python3 verify_c2c10_profile.py            # 10/10 vs exhaustive, exit 0
python3 verify_c2c10_profile.py 11,1 40,1  # ad-hoc certified values
```

Frozen Tier-B package and V1 untouched; this note is additive under
`successor/`. Asymptotic reading: Kmin grows like c(m)·N with the certified
constant now computable exactly for any m — the Θ(m)-slack bracket of V1 is
superseded.

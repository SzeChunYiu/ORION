# A closed form for `D_k(C_p^r)` — conjecture, evidence, and the tension against it

**Status: CONJECTURE.** Not proved, and not fully consistent with this packet's own
constructions. Checker: `verify_closed_form_conjecture_v7.py` (6 asserted steps) verifies the
*arithmetic* — that the constants are forced, that the fit is exact, and that the shortfalls are
exactly what is claimed. It does not verify the conjecture, which is not a thing a checker can do.

---

## 1. The statement

> **Conjecture.** For an odd prime `p`, rank `r ≥ 2`, and `k ≥ 2`,
>
>     D_k(C_p^r)  =  (3/2) · r(p−1)  +  (k−2)·p  +  2.
>
> Equivalently, with `D = D(C_p^r) = r(p−1)+1` (Olson), `D_2(C_p^r) = (3D+1)/2`.

The right-hand side is an integer exactly when `r(p−1)` is even, which for odd `p` is automatic.

**The constants are not fitted.** Write the general shape `α·r(p−1) + β·p(k−2) + γ`. Imposing only
the *rank-two* formula `D_k(C_m ⊕ C_n) = m + kn − 1` (standard; at `m = n = p` it reads
`p + kp − 1`) forces `(α, β, γ) = (3/2, 1, 2)` uniquely — step 1 solves the 3×3 system over `Q`
and confirms the fit for every `p` and `k` tested. So **every value of rank ≥ 3 below is an
out-of-sample prediction**, not a degree of freedom.

---

## 2. Evidence: 24 of 24 known exact values

| family | values | source | agrees |
|---|---|---|---|
| `D_k(C_p^2)`, `p = 3,5,7,11`, `k = 2..5` | 16 values | rank-2 formula, literature | ✅ (this is the fit) |
| `D_2(C_p^3)`, `p = 3,5,7,11` | 4 values | packet theorem `(9p−5)/2` | ✅ **prediction** |
| `D_3(C_5^3) = 25` | | packet, exhaustive `L=25` | ✅ **prediction** |
| `D_3(C_7^3) = 36` | | packet, corridor + Hypothesis (Z) | ✅ **prediction** |
| `D_4(C_5^3) = 30` | | packet, Theorem T, 5.9e9 nodes | ✅ **prediction** |
| `D_2(C_3^5) = 17` | | packet, 2.73e9-node sweep | ✅ **prediction** |

The rank-3 row is a whole one-parameter family, not a point: the conjecture reproduces
`(9p−5)/2` identically in `p`. And the four hardest single values this packet owns — the two
that cost billions of nodes, the one that needed Hypothesis (Z), and the new rank-5 value — are
all predicted correctly by a formula whose constants were fixed at rank 2.

**It repairs a known failure.** The naive guess `D_k = Σ(nᵢ−1) + (k−1)·exp + 1 = r(p−1)+(k−1)p+1`
is what the rank-2 formula suggests, and the literature records that it **fails for elementary
2- and 3-groups of rank ≥ 3**. Step 3 makes that precise on this data: the naive formula agrees at
all 16 rank-2 points and fails at **all 8** points of rank ≥ 3. The conjecture agrees at all 24.
It is a candidate replacement for the shape that is known to break, and it breaks nowhere the
truth is known.

**It is consistent at `k = 1`, in the right way.** Step 6: the formula is exact at `k = 1` for
`r = 2` and wrong for every `r ≥ 3` tested. That is required, not a defect — Freeze–Schmid prove
`(D_k(G))_k` is only *eventually* an arithmetic progression with difference `exp(G)`, so a formula
linear in `k` must fail at small `k` in high rank.

**It respects the proved bracket.** Step 5: `D + 1 ≤ conjecture ≤ 2D` at every computed `(r,p)`,
so it is compatible with Olson and the complement lemma (`CODE_DICTIONARY_V7.md` §4).

---

## 3. The tension — stated plainly

The conjecture is equivalent, through `D_2 = r(p−1) + M* + 1`, to `M*(r,p) = r(p−1)/2 + 1`. The
packet's computed construction optima disagree at three points:

| `(r,p)` | computed `M*` | conjecture needs | construction gives | conjecture says |
|---|---|---|---|---|
| `(7,3)` | 7 | 8 | `D_2(C_3^7) ≥ 22` | 23 |
| `(4,7)` | 12 | 13 | `D_2(C_7^4) ≥ 37` | 38 |
| `(5,5)` | 10 | 11 | `D_2(C_5^5) ≥ 31` | 32 |

Short by **exactly one**, three times. Two readings, and this packet cannot choose between them:

- **(a) the conjecture is wrong** above rank 3 — `M*(4,p) = ⌊9p/5⌋` and `M*(5,p) = 2p`
  (`WITNESS_CRITERION_V6.md` §6) fit the computed values exactly, and they diverge from
  `r(p−1)/2 + 1` at precisely `p = 7`, `p = 5` and `r = 7`. Note each divergence rests on a
  **single** computed point.
- **(b) the family class is incomplete.** `M*` is an optimum over the Theorem-W families
  `S = ∏ᵢ eᵢ^{p−1} · ∏_A v_A^{m_A}`, and the recorded values were computed over **0/1-indicator**
  `v`. A witness of the conjectured length need not have that shape at all.

### What was done to separate them

Theorem W never requires `v` to be a 0/1 vector — its proof only needs the `e`-part to correct
each coordinate independently. So the optimisation was rerun over **all** `v ∈ F_p^r \ {0}` by
randomised ascent. Before reading any of it, the searches were **calibrated**: can they recover a
`p = 3` optimum the exhaustive tool already knows?

| calibration point | recorded `M*` | search found | verdict |
|---|---|---|---|
| `(4,3)` | 5 | 5 | recovered |
| `(5,3)` | 6 | 6 | recovered |
| `(6,3)` | 7 | **6** | **too weak** |

Two independently written searches — a generic hill-climb and a specialised incremental one — both
fail at `(6,3)`. **So neither has any evidential weight at `r ≥ 6`, and the `(7,3)` result must be
withdrawn as evidence.** For the record, both found 7 at `(7,3)` and neither found 8; that is
consistent with the class being short *and* with the search being short, and it does not separate
them. A claim that widening the class fails at `(7,3)` would have been an overclaim, and this table
is why it is not made.

Where the calibration passes, the results do count:

| test | result | weight |
|---|---|---|
| `(4,3)`, all 80 vectors of `F_3^4` | 5 — no gain over the indicator class | calibrated |
| `(5,3)`, all 242 vectors of `F_3^5` | 6 — no gain | calibrated |
| `(7,3)`, all 2186 vectors of `F_3^7` | 7 — did not reach 8 | **not calibrated; proves nothing** |

The `(5,3)` line is the one that could have exposed an error and did not: `D_2(C_3^5) = 17` is
*proved*, so any family there with `Σ m_A ≥ 7` would contradict the 2.73-billion-node sweep. None
was found, in the widened class, by a search that demonstrably finds the optimum when it exists.

### The `M*` table itself, independently validated

Everything above rests on the recorded `M*` values, so they were recomputed from scratch with the
exhaustive DFS in `tools/witness_optimum_v6.c`, in a build instrumented to count box truncations:

| `(r,p)` | recorded `M*` | exhaustive tool | box truncations |
|---|---|---|---|
| `(4,3)` | 5 | 5 | 0 |
| `(4,5)` | 9 | 9 | 0 |
| `(4,7)` | 12 | 12 | 0 |
| `(5,3)` | 6 | 6 | 0 |
| `(5,5)` | 10 | 10 | 0 |
| `(6,3)` | 7 | 7 | 0 |

Six for six, and at `(5,3)` the tool returns precisely the `{1,i,j}` family of the `C_3^5` witness.

The truncation column is not decoration. `build_box()` used to stop filling the multiplicity box
after 100000 points and **return silently**; `feasible()` would then test only part of the box, so
a violating pair could go unexamined and a family be declared feasible when it is not — which
overreports `M*`, which is what every `D_2` lower bound here is built from. It is reachable in
principle (`nc ≤ 16` with `CAP = 24` permits a box of `3^12 = 531441`). The instrumented run shows
it has **never fired** on any computed case, and the guard now aborts loudly instead of truncating.

**What would settle `(7,3)`** is that same exhaustive DFS run with `--all-vectors` at
`(p,r) = (3,7)`, not a randomised ascent. Whether its search space is tractable at 2186 vectors
has not been established.

## 4. The questions this sharpens

Each of these is a single number, and each decides the conjecture:

1. **`D_2(C_3^7)` — is it 22 or 23?** The smallest and cleanest test. `r = 7, p = 3` is the point
   where the packet already refuted one pattern (`M*(r,3) = r+1`), and the refutation was about
   the *class*. If some length-22 sequence over `C_3^7` has `z ≤ 1`, the conjecture survives and
   the Theorem-W families are provably not the whole story.
2. **`D_2(C_7^4)` — 37 or 38?** and **`D_2(C_5^5)` — 31 or 32?**
3. Is `M*(4,p) = ⌊9p/5⌋` or `2p−1`? They agree at `p = 3, 5` and differ at `p = 7`. One more
   value, `M*(4,11)`, would separate them: `⌊99/5⌋ = 19` against `21`.

Question 3 is the cheapest of the four and does not need a new search engine — it is one more run
of the existing `tools/witness_optimum_v6.c` at `(r,p) = (4,11)`.

---

## 5. Why it might be true — and one mechanism that is refuted

`CODE_DICTIONARY_V7.md` §4 lists five elementary constraints on an extremal family. Writing
`q = r(p−1) = D − 1`, the conjecture says `n_max = (3q+2)/2`, so the admissible atom-size window
`[n − q, q+1]` becomes exactly `[(q+2)/2, q+1]` — floor at half the ceiling.

**Every extremal witness saturates that window.** Checked at every `(r,p)` where `D_2` is known
exactly and the enumeration is feasible, using the optimal families the exhaustive tool returns:

| | `q` | window | atom sizes attained | blocks | core |
|---|---|---|---|---|---|
| `C_3^2` | 4 | `[3,5]` | 3,4,5 | 13 | empty |
| `C_3^3` | 6 | `[4,7]` | 4,5,6,7 | 43 | empty |
| `C_5^2` | 8 | `[5,9]` | 5,…,9 | 521 | empty |
| `C_7^2` | 12 | `[7,13]` | 7,…,13 | 24865 | empty |
| `C_3^5` | 10 | `[6,11]` | 6,…,11 | 289 | empty |

Five for five: the sizes fill the interval with **no gaps**, both ends are attained, and the core
is empty as Theorem Y requires. Saturating every elementary constraint simultaneously is the
expected shape of an extremal object, and it is a regularity rather than a single observation.

### The obvious mechanism does not work

There is a tempting explanation for the factor `q/2`. No-carry requires `⟨aᵢ⟩ + ⟨a′ᵢ⟩ ≤ p−1` in
*every* coordinate; summing over `i`, two **disjoint** blocks must satisfy

    |e(b)| + |e(b′)|  ≤  r(p−1) = q,        where |e(b)| = Σᵢ ⟨−(Mb)ᵢ⟩.

So `|e(b)| > q/2` for every admissible `b` is a genuine **sufficient** condition for `z(S) ≤ 1`,
and it would name `q/2` as the critical scale for free.

**It is refuted by the extremal families themselves.** Every recorded optimum has blocks whose
`e`-part is far below the half-budget:

| `(r,p)` | `q/2` | `min |e(b)|` |
|---|---|---|
| `(2,3)` | 2 | 2 |
| `(3,3)` | 3 | 2 |
| `(5,3)` | 5 | **3** |
| `(4,5)` | 8 | **3** |
| `(4,7)` | 12 | **5** |
| `(5,5)` | 10 | **2** |
| `(6,3)` | 6 | **3** |

Not one family satisfies the condition. The sum bound is a correct necessary condition for
disjointness, but the extremal families sit far inside it and are held together by Theorem W's
**coordinate-wise** condition, which is strictly stronger than any bound on the total. So the
`q/2` scale is not explained this way, and this is not a route to the conjecture.

No proof of the conjecture is offered here, in any rank, and the one mechanism that would have
given the constant away has been tested and does not hold.

## 6. Claim ceiling

This is a conjecture supported by 24 exact values and contradicted by nothing proved — but its own
construction falls one short at three points, and that is unresolved. The general-vector searches
in §3 are randomised, not exhaustive; they can find witnesses but cannot prove none exists. The
`k`-direction extension leans on `M*_k = M*_2 + (k−2)p`, which is Freeze–Schmid's theorem read
inside the construction class, and on the rank-2 formula, which is a donor statement this packet
has never verified against a primary text.

Nothing here has been read by a mathematician, and novelty is unchecked — a closed form this clean
is exactly the kind of thing that may already be conjectured in the literature this host cannot
reach. See `EXTERNAL_PRIOR_ART_V5.md` §V7.

# ORION-RG X1-F0 — exact 2-wise Davenport constant of `C_5^3`

Issue: `SzeChunYiu/ORION#916`. Parent `#915`, umbrella `#896`, programme `#894`.

## Authority

- `mathematical_proposal: true`
- `mathematical_result_credit: false`
- `proof_authority: false` for anything not machine-checked here
- root state of `#896` (rank-3 Davenport/Olson) unchanged: `OPEN`
- no ORION novelty claim over Davenport-constant theory, Freeze–Schmid `k`-wise
  lower bounds, Olson's `D(C_p^r)=r(p-1)+1`, or exhaustive/constraint search

## Definitions (frozen before search)

Let `G` be a finite abelian group and `S` a finite sequence (multiset) over `G`.

- `D(G)` — smallest `l` such that every length-`l` sequence has a nonempty
  zero-sum subsequence. Olson: `D(C_5^3) = 3(5-1)+1 = 13`.
- `D_k(G)` — smallest `l` such that every length-`l` sequence has `k` pairwise
  **disjoint** nonempty zero-sum subsequences. `D_1 = D`.
- `f_T(G)` — **maximum** length of a sequence over `G` with **no** nonempty
  zero-sum subsequence of length `<= T`.
- `eta_T(G) := f_T(G) + 1` — smallest length forcing a zero-sum of length `<= T`.
  `eta_{exp(G)}` is the classical `eta(G)`.

## Lemma A (complement lemma)

If a length-`L` sequence `S` over `G` has no `k+1` pairwise disjoint nonempty
zero-sum subsequences, then every nonempty zero-sum subsequence `A` of `S`
satisfies `|A| >= L - D_k(G) + 1`.

*Proof.* If `|A| <= L - D_k(G)` then `|S A^{-1}| >= D_k(G)`, so the complement
carries `k` pairwise disjoint nonempty zero-sums; with `A` that is `k+1`. ∎

Consistency control (pre-registered, executed): the Freeze–Schmid `k=2` witness
of length 19 must then have minimum zero-sum length `>= 19 - 13 + 1 = 7`.
Executed value: exactly 7. Lemma A is tight on the donor witness.

## Lemma B — NOT NEW. This is Freeze–Schmid 2010, Proposition 3.1(3)

**Correction, recorded after a hostile literature check.** An earlier version of
this document presented the following as a new lemma:

```
D_{k+1}(G)  <=  max( eta_T(G),  D_k(G) + T ).
```

It is published. Freeze & Schmid, *Remarks on a generalization of the Davenport
constant*, Discrete Math. 310 (2010) 3373–3389 (arXiv:0905.4248),
**Proposition 3.1(3)**:

> for each `l` in `N`, `D_{k+1}(G) <= max{ D_k(G) + l, s_{<=l}(G) - 1 }`

with `s_{<=l}(G)` exactly our `eta_l(G)`. Their form is **strictly stronger than
the one claimed here**: `eta_l - 1` where this document had `eta_l`.

The same paper's Proposition 3.1(2) is sharper still:
`D_{k+1}(G) <= D_k(G) + M`, where `M` is the minimum length of a minimal
zero-sum sequence dividing an extremal `B`.

No ORION credit is taken for any of this. What remains of this document's
contribution is the *instantiation*: the exact `eta_T(C_5^3)` spectrum that
makes the bound bite, and the exact constants that follow.

For the record, the correct (Freeze–Schmid) form instantiates as
`max(D + 7, eta_7 - 1) = max(20, 18) = 20`, which is tight.

## Executed instrument

`research/orion-rg/x1f0_short_zero_sum_spectrum.c` computes `f_T(C_5^3)`
restricted to **rank-3** supports by complete depth-first enumeration.

Sound reductions, each stated before execution:

- **R1** `GL(3,5)` maps any three independent support elements to `e1,e2,e3`;
  zero-sum structure is `GL`-invariant. So a rank-3 support may be assumed to
  contain `e1,e2,e3`. Rank `<= 2` is handled separately (see Theorem 1).
- **R2** the six coordinate permutations fix `{e1,e2,e3}` setwise, so
  `m(e1) <= m(e2) <= m(e3)` may be assumed.
- **R3 multiplicity oracle (exact).** Adding `k` copies of `v` preserves
  "no zero-sum of length `<= T`" iff for every `j = 1..k`, `-j*v` is not a sum of
  at most `T-j` current elements. *Proof:* a violating zero-sum uses `j` copies
  of `v` and a sub-multiset of the current sequence of size `w` and sum `s` with
  `j*v + s = 0` and `j + w <= T`. This replaces all trial insertions in the
  bound by an O(1) table lookup.
- **R4 line bound (sound form).** The 124 nonzero vectors split into 31
  projective lines `{g,2g,3g,4g}`. The part of a witness lying on one line must
  itself be free of zero-sums of length `<= T`, i.e. its multiplicity vector
  `(a_1..a_4)` admits no `(b_i) <= (a_i)` with `1 <= sum b_i <= T` and
  `sum i*b_i = 0 (mod 5)`. `MAXLINE[u_1..u_4]` tabulates the maximum line total
  under per-point caps and is summed over the 31 lines.

  **Recorded defect and repair.** An earlier draft bounded each line by
  `max_p mult_ub(p)`. That is **unsound**: `g` and `2g` can coexist (e.g.
  `g^1 (2g)^1` has no zero-sum of length `<= 7`), so a line's total can exceed
  every single-point cap. The bound was replaced by `MAXLINE` before any value
  was recorded, and `T = 7` was re-run to completion under the sound bound.
  Both runs returned 18; only the sound run is cited.

## Allowed result branches (frozen before the terminal run)

- `X1F0_EXACT_D2_ESTABLISHED`
- `X1F0_LOWER_BOUND_RAISED_WITH_EXPLICIT_OBSTRUCTION`
- `X1F0_DONOR_OWNS_EXACT_VALUE`
- `CANNOT_CHECK_RESOURCE_BOUND`

Terminal reached: `X1F0_EXACT_D2_ESTABLISHED`.

## Theorem 1 (machine-checked)

```
D_2(C_5^3) = 20.
```

*Lower bound.* The Freeze–Schmid `k=2` witness
`S = e1^4 e2^4 e3^4 (1,1,0)^2 (1,0,1)^2 (0,1,1)^3` has length 19 and no two
disjoint nonempty zero-sum subsequences (two independent implementations, see
`x1f0_independent_replay.py` and the pre-existing
`x1f_freeze_schmid_c5cube_k2_saturation.py`). Hence `D_2 >= 20`.

*Upper bound.* Let `|S| = 20`.

- If the support of `S` spans a subgroup `H` of rank `<= 2`, then
  `D(H) <= D(C_5^2) = 9`; a minimal zero-sum `A` has `|A| <= 9`, and
  `|S A^{-1}| >= 11 >= 9 = D(H)` yields a second disjoint zero-sum.
- Otherwise the support has rank 3. The complete search gives
  `f_7(C_5^3) = 18 < 20`, so `S` has a nonempty zero-sum `A` with `|A| <= 7`.
  Then `|S A^{-1}| >= 13 = D(C_5^3)`, giving a second disjoint zero-sum.

Either way `S` has two disjoint nonempty zero-sums, so `D_2 <= 20`. ∎

Equivalently, via Freeze–Schmid Prop. 3.1(3) with `k = 1`, `l = 7`:
`D_2 <= max(D + 7, eta_7 - 1) = max(20, 18) = 20`, exactly tight.

## Donor position

The current literature bounds recorded on `#916` are `20 <= D_2(C_5^3) <= 23`;
no exact value was surfaced by the hostile search recorded there. Theorem 1
fixes the value at the lower end of that interval. The lower bound is
Freeze–Schmid's, not ours; the contribution is the matching upper bound and the
`eta_T` instrument that produces it.

## What Theorem 1 does not do

It does not decide `D_3(C_5^3)` (`#915`), does not touch the rank-3
Davenport/Olson conjecture (`#896`), and carries no ORION novelty claim.
It does supply the `#915` state reduction that motivated this atom: at length
25, every zero-sum `A` must satisfy `|A| >= 25 - D_2 + 1 = 6`.

## Executed short-zero-sum spectrum of `C_5^3` (rank-3, complete searches)

| `T` | `f_T(C_5^3)` | `eta_T = f_T + 1` | search nodes |
|-----|--------------|-------------------|--------------|
| 6   | 23 | 24 | 215,736,872 |
| 7   | 18 | 19 |  88,575,385 |
| 8   | 17 | 18 |  66,973,201 |
| 9   | 14 | 15 |  55,620,887 |
| 10  | 14 | 15 |  53,310,145 |
| 11  | 14 | 15 |  10,689,661 |
| 12  | 14 | 15 |   1,659,207 |

Rank `<= 2` control: `f_5(C_5^2)=12`, `f_6(C_5^2)=11`, `f_7(C_5^2)=10` — all
strictly below the rank-3 values, so rank 3 attains the maximum throughout this
range and the table is `f_T(C_5^3)`.

These three numbers were first produced by a throwaway Python helper that had a
bookkeeping bug in its witness record (it appended one element per multiplicity
step but popped once). The bug could not affect the returned *size*, which is
all that was read, but the row is load-bearing, so it was recomputed from
scratch with `x1f0_general_dk_and_fT.c` — the same instrument validated against
`D_k(C_n^2) = (k+1)n - 1` below. Both runs agree: 12, 11, 10.

`f_T = 14` is stable for `T >= 9`; the classical zero-sum-free maximum is
`D(C_5^3)-1 = 12`, so the two extra elements at `T >= 9` come from sequences
whose only zero-sums have length 13 or 14.

## Corollary 1 (`#915` narrowing)

Lemma B with `k = 2` and `T = 6`:

```
D_3(C_5^3)  <=  max( eta_6, D_2 + 6 )  =  max( 24, 26 )  =  26.
```

With the Freeze–Schmid `k=3` lower bound of 25 recorded on `#915`:

```
25  <=  D_3(C_5^3)  <=  26.
```

The interval carried by `#915` was `[25, 33]`. This is a narrowing, not a
closure: `D_3` remains open between two values. Note `T = 5` does not help —
`eta_5 = eta(C_5^3)` is at least 33 by the standard `eta(C_n^3) >= 8n-7`
construction, so `max(eta_5, 25) = eta_5 >= 33`.

Lemma A supplies the state reduction `#915` asked for: at length 25 every
zero-sum subsequence of a 3-disjoint-free witness has length `>= 6`.

## Reproduction

```
cc -O3 -o spectrum research/orion-rg/x1f0_short_zero_sum_spectrum.c
./spectrum 7            # -> f_7 = 18, complete_search = true
python3 research/orion-rg/x1f0_independent_replay.py
```

## Second, independent upper-bound proof

`research/orion-rg/x1f0_exact_two_disjoint_enumerator.c` decides the same
question without the `eta_7` route, by carrying the **exact** two-disjoint
predicate as an incremental DP: `R1` (one nonempty part, its sum) and `R2`
(both parts nonempty, indexed by the pair of sums), stored as 125-bit boards and
advanced by the coordinate-wise shift that realises `+v` on `C_5^3`.

The shift masks were validated before use: all `125 x 125` single-bit images
were compared against primitive mod-5 addition, **0 mismatches**.

The `no zero-sum of length <= 6` prune is legitimate here because the target
length is `>= 19`, where Lemma A forces minimum zero-sum `>= 7`, and that
property is inherited by every sub-multiset.

Result: the maximum length of a sequence over `C_5^3` with **no two disjoint
nonempty zero-sum subsequences** is **19** (353,051,328 nodes). Hence
`D_2 = 20`, agreeing with the `eta_7` route.

## Inverse-problem note for X1-F4

The run also enumerated **98,622** length-19 witnesses under the normalization
above. `#915` X1-F4 proposes classifying every maximal length-19 failure as
`GL`-equivalent to the Freeze–Schmid obstruction type. That is **false as
stated**: the extremal class is large, and Freeze–Schmid's witness is one
member of it. Any inverse route to `D_3` must classify a large family, not a
single type. One further extremal example produced by the search:

```
e1 e2 e3 (0,1,1) (0,1,2) (1,0,4)^4 (2,0,4)^3 (4,1,0)^4 (4,1,1)^3
```

## Generality of Lemma B (global-recovery check)

Lemma B is stated for every finite abelian group, so it must be tested outside
`C_5^3`. `research/orion-rg/x1f0_general_dk_and_fT.c` computes exact `D_k(G)`
and `f_T(G)` for small `G` by complete enumeration; every `(G, k)` step below
compares the Lemma B bound against the true constant and against the classical
`D_{k+1} <= D_k + D`.

| group | `k` | true `D_{k+1}` | FS 3.1(3) | classical | best `l` | tight |
|-------|-----|----------------|---------|-----------|----------|-------|
| `C_2^2` | 1 | 5 | 5 | 6 | 2 | yes |
| `C_2^2` | 2 | 7 | 7 | 8 | 2 | yes |
| `C_2^3` | 1 | 7 | 7 | 8 | 3 | yes |
| `C_2^3` | 2 | 9 | 9 | 11 | 2 | yes |
| `C_2^4` | 1 | 8 | 8 | 10 | 3 | yes |
| `C_2^4` | 2 | 11 | 11 | 13 | 3 | yes |
| `C_3^2` | 1 | 8 | 8 | 10 | 3 | yes |
| `C_3^2` | 2 | 11 | 11 | 13 | 3 | yes |
| `C_5^2` | 1 | 14 | 14 | 18 | 5 | yes |
| `C_5^3` | 1 | 20 | 20 | 26 | 7 | yes |
| `C_5^3` | 2 | 25 | **26** | 33 | 6 | **no** |

**Recomputed under the correct Freeze–Schmid form** `max{D_k + l, eta_l - 1}`:
tight in **10 of the 11** decided steps. The extra `-1` closes `C_2^4, k = 1`
(`max{5+3, 9-1} = 8`, the true value), so the "second gap" reported in an
earlier version of this table was an artifact of the weaker restatement, not a
real weakness of the published lemma.

**Exactly one genuine gap remains: `C_5^3, k = 2`** — the bound gives
`max{20+6, 24-1} = 26` while the truth is 25 (`X1F_D3_C5CUBED_PROTOCOL_V1.md`).

**Every row of this table is replication, not discovery.** Freeze–Schmid
determined exact `D_k` for elementary 2-groups of rank 4 and 5, and state that
rank `<= 3` was already known; the rank-2 formula `D_k(C_m + C_n) = m + kn - 1`
is classical. The table's role is instrument validation and boundary-finding for
the published bound, nothing more. The code reproduces the known rank-2 values
on every computed entry
(`C_2^2: 3,5,7`; `C_3^2: 5,8,11`; `C_5^2: 9,14`). A checker that had not
reproduced a known family would not have been used.

### The one gap is a lead, not noise

One failure survives the correct form: `C_5^3, k = 2` (`D_3 = 25`, bound 26).
The `C_2^4` case below is retained only to show why the weaker restatement
appeared to fail there:
The `eta_T` profile there is `2:16, 3:9, 4:6, 5:5, 6:5, 7:5` against `D = 5`, so
every `T` is either short of `eta_T` or over `D + T`; no single `T` balances.
That is the mechanism of the gap: Lemma B commits to **one** threshold `T`,
and `C_2^4` is a group where the obstruction spectrum falls between two
thresholds. A version that mixes several `T` in one argument is the obvious
next mechanic, and it is exactly the case where the present lemma is known to
lose. Recorded as an open refinement target rather than smoothed over.

Note that `k = 2` on the same group is tight (11 = 11), so the failure is
specific to the first step, not to the group.

### What was attempted and could not be checked

`D_4` was launched for `C_2^2`, `C_2^3` and `C_3^2` to extend the ladder test one
step further. All three were killed at a resource bound without returning, so
the `k = 3 -> 4` step is **`CANNOT_CHECK_RESOURCE_BOUND`**, not "checked and
fine". The enumerator in `x1f0_general_dk_and_fT.c` carries no bound for the
`D_k` mode; adding one is the prerequisite for that row.

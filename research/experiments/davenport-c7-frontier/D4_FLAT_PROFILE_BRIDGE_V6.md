# A congruence bridge from a flat profile to a maximal atom — V6

Status: **proved.** The congruence machinery reaches one of the flat `D_4(C_5^3)` profiles that no maximal-atom method could touch, by *forcing* it to contain a maximal atom. This is direction 3 of `FLAT_TRIPLE_INFEASIBILITY_MEASURED_V6.md` §4, and it works.
Checker: `verify_d4_flat_bridge_v6.py`. Priority CANNOT_CHECK.
Lane: `claude/orion-research-frontier-3ck9yt`.

## 1. The idea

`FLAT_TRIPLE_INFEASIBILITY_MEASURED_V6.md` showed the enumeration route cannot reach flat profiles — those with no maximal part — and listed three alternatives. The third was: *the congruence machinery is prime-uniform and indifferent to whether a part is maximal; whether it can separate flat profiles is untested.* It can.

## 2. The congruence at `N = 31`

The symmetric identity holds for **any** zero-sum `T`, whatever its atom structure:

`Σ_l (−1)^l N_l C(l,d) + [C(0,d) + (−1)^N C(N,d)] ≡ 0 (mod 5)`,  `0 ≤ d ≤ N − D = 18`,

with `N_l` the weighted count of zero-sum sub-multisets of length `l`, and `N_l = N_{N−l}` because complementation preserves the weight. Atoms of length `≥ 6` give `N_l = 0` for `l ∈ [1,5]`, hence for `l ∈ [26,30]`.

> **Proposition N.** The minimal forced length sets are exactly the 36 pairs `{6,x}` and `{x,25}`, `x ∈ [7,24]`. Since `N_6 = N_25` is one unknown, the content is:
>
> **if `T` has no zero-sum of length 6, it has one of every length `7, …, 24`.**

No single length is forced, and the unrestricted system is consistent — so this is not vacuous.

## 3. The bridge

Of the five corridor profiles, exactly one has no part equal to 6: the flat `(7,7,7,10)`.

Its shortest atom is 7, so `T` has no atom of length 6, hence no zero-sum of length 6 — such a zero-sum would contain an atom of length `≤ 6`, and atoms have length `≥ 6`, so it would *be* a 6-atom. Proposition N then gives zero-sums of every length `7 … 24`. And since two disjoint atoms already total `≥ 14 > 13 = D`, every zero-sum of length `≤ 13` is a **single atom**. Therefore:

> **Theorem O.** A `D_4(C_5^3)` obstruction with corridor profile `(7,7,7,10)` carries an atom of **every** length `7, 8, 9, 10, 11, 12, 13` — in particular a **maximal** atom of length `13 = D(C_5^3)`.

Combined with Theorem M (`D4_C5_SUPPORT4_MAXIMAL_CLOSURE_V6.md`), that maximal atom has support `≥ 5`.

## 3a. A refinement, and the limits of the test

Running the Proposition-P test directly on the five `D_4` profiles — is the system consistent when `N_l` may be nonzero only on the profile's own subset sums? — separates them the same way:

| profile | parts alone consistent |
|---|---|
| `(6,6,6,13)`, `(6,6,7,12)`, `(6,7,7,11)`, `(6,7,8,10)` | **yes** — no extra constraint from this test |
| `(7,7,7,10)` | **no**, and **no single extra length restores it** |

So `(7,7,7,10)` needs at least two zero-sum lengths beyond its own factorization, which is consistent with Theorem O's much stronger conclusion (all of `7 … 13`). The four profiles containing a 6 are untouched: this congruence says nothing about them, exactly as in §4 below.

## 4. What this changes

Before, `(6,6,6,13)` was the only profile a maximal-atom method could reach. Now two of the five are in the same position — both require a maximal atom of support `≥ 5`:

| profile | status |
|---|---|
| `(6,6,6,13)` | maximal atom present by construction; support-four branch **closed** (Theorem M) |
| `(7,7,7,10)` | maximal atom **forced** (Theorem O); support-four branch closed by Theorem M |
| `(6,6,7,12)`, `(6,7,7,11)`, `(6,7,8,10)` | still flat; each has a part 6, so Proposition N does not bite |

The three remaining profiles all contain a 6, which satisfies every forced pair, so this particular congruence says nothing about them. Reaching them needs either a finer congruence or one of the other two directions.

**The transferable point:** a flat profile is not necessarily beyond maximal-atom methods — it may be *forced* into their reach. The obstruction to the `D_3(C_p^3)` flat rows at `p ≥ 11` should be re-examined in that light, since the analogous question there (does Theorem J's `b`- or `c`-row force a maximal atom?) has not been asked.

## Claim ceiling

Proposition N is a finite computation at `p = 5`, `N = 31`; Theorem O follows from it by the two elementary steps shown. Neither decides `D_4(C_5^3)`, and neither touches the three profiles containing a 6. The suggestion in §4 about `p ≥ 11` is a research direction, not a result.

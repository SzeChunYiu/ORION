# ORION-04: where a `D_4(C_5^3) >= 29` construction cannot live

**Date:** 2026-08-30 · **Status:** narrows the open `N-C11`/`N-C12` blocker.
Establishes no value for `D_4(C_5^3)`.

## Why this is computable at all

`D_4 <= 30` and `D_4 = 31` are exact negations. `D_k(G)` is the least `l` such
that *every* sequence of length `>= l` has `k` disjoint nontrivial zero-sum
subsequences, so `D_4 >= L+1` holds exactly when **some** length-`L` sequence has
at most 3. The `>=` direction is therefore witness-checkable; the `<=` direction
is universal and is not attacked here.

`CLAIM_LEDGER.md` marks `N-C12` (`=31`) `OPEN` with **no admitted extremal** —
i.e. no length-30 witness has been produced. This search is an independent
attempt to produce one, and a negative report on where it is not.

## Checker validation, before any rank-3 use

The packing checker was validated against the **known** rank-<=2 formulas
(`D_k(C_n) = kn`; `D_k(C_m + C_n) = m + kn - 1`) — not against fixtures:

| Control | Result |
|---|---|
| Witness side: length `D_k - 1` has `< k`, for `k = 1..5` over `C_5+C_5` | 5/5 correct |
| No-alarm side: length `D_k` has `>= k`, for `k = 1..4` | 4/4 correct |
| Minimality: `e_1^14` packs 2, not 2.8 | correct |
| `D(C_5^3) = 13`: `e1^4 e2^4 e3^4` is zero-sum-free | correct |
| Naive bound: `e1^19 e2^4 e3^4` (len 27) packs exactly 3 | correct, gives `D_4 >= 28` |

Both directions matter. A checker validated only on witnesses could pass by
under-counting everywhere, which would manufacture witnesses at every length.

## Result

**Three-element families `e1^a e2^b e3^c`, exhaustive over all partitions:**

| length | min packing over ALL (a,b,c) | witness for `D_4 >= L+1`? |
|---|---|---|
| 26 | **3** at (9,9,8) | yes |
| 27 | **3** at (9,9,9) | yes -> `D_4 >= 28` |
| 28 | 4 | **no** |
| 29 | 4 | **no** |
| 30 | 4 | **no** |
| 31 | 4 | **no** |

**Four-element families** `e1^a e2^b e3^c v^d`, `v` swept over 18 structurally
motivated elements ((1,1,1), (1,1,4), (1,2,3), (2,2,2), ... ) and all
multiplicity partitions: minimum packing is **4** at every length 28, 29, 30.
Direct extensions of the length-27 witness by 1, 2 or 3 further elements all
jump to 4 or 5.

## What this constrains

The balanced `(9,9,9)` construction attains packing 3 at length 27, matching the
naive `D(G) + (k-1)exp(G) = 28` bound by a more symmetric route than
`e1^19 e2^4 e3^4`. **It does not extend.** Every attempt to reach length 28+
within these families gains a fourth disjoint zero-sum.

So: any proof of `D_4(C_5^3) >= 29` — a fortiori of `>= 30`, which the frozen
`d4-proof-handoff-v1` protocol targets — **requires a construction supported on
at least five distinct elements, or on a fourth element outside the swept pool.**
The two- and three-element regions are closed.

## What this does NOT establish

- **Not** `D_4(C_5^3) = 28`. These are families, not the full length-30 space
  over 124 nonzero elements. An absence of witnesses in a searched class is
  evidence about that class.
- **No** support for `=30` over `=31`, or the reverse. Both remain `OPEN`.
- The `<=` direction is untouched and is not brute-forceable.
- No proof is verified, and no D4 execution round is consumed:
  `scientific_authority_delta: NONE`.

The honest reading is that this makes `N-C12`'s "no admitted extremal" sharper —
the missing extremal, if it exists, is not a low-support one.

**Terminal:** `FAMILY_SEARCH_NEGATIVE__NO_WITNESS_AT_LENGTH_GE_28_IN_SUPPORT_LE_4__TARGET_REMAINS_OPEN`

# ORION-RG X1-L — a validated general `D_2` searcher, and where the frontier is

Infrastructure plus a corrected map, produced while chasing the `f_m = D_2 - 2`
tightness pattern from X1-K. The chase itself came up **negative** and that is
recorded first.

## The tightness pattern is not forced

X1-K observed `f_m(G) = D_2(G) - 2` exactly for `C_2^2, C_3^2, C_5^2, C_3^3,
C_5^3`. Tightness needs a length-`(D_2-2)` sequence with **no** zero-sum of length
`<= m`. A natural construction gives `f_m >= D - 1` always (a maximal
zero-sum-free sequence has no zero-sum at all), and `D_2 - 2 = D + m - 2`, so
tightness needs `m - 1` more elements than that construction supplies.

**That lower bound fails**: `C_2^3` has `f_3 = 4 < 5` and `C_2^5` has
`f_4 = 6 < 8`. So `f_m = D_2 - 2` is **not a theorem** — it is a description of
the rank-`<=2` and odd-`p` rank-3 cases, and the elementary 2-groups of rank
`>= 3` are exactly where it fails. No general statement is claimed.

## The searcher

`research/orion-rg/x1l_general_d2_searcher.c` computes `D_2(C_p^r)` directly, as
`1 +` the maximum length of a sequence with no two disjoint nonempty zero-sums.
It carries the exact two-disjoint predicate incrementally (`R1` = one nonempty
part's sum, `R2` = both parts' sum pair) as bitmasks over the `p^r` group
elements, and enumerates multisets in nondecreasing order.

### Validation ledger — every known value, before any new use

| group | published | searcher |
|-------|-----------|----------|
| `C_2^2` | 5 | **5** |
| `C_2^3` | 7 | **7** |
| `C_2^4` | 8 (Freeze–Schmid Thm 7.9) | **8** |
| `C_2^5` | 10 (FS; needed a separate argument there — their bounds gave 9 and 10) | **10** |
| `C_3^2` | 8 (rank-2 formula `m + kn - 1`) | **8** |
| `C_3^3` | 11 (Freeze–Schmid) | **11** |

**6 of 6.** Note `C_2^5` is the useful row: Freeze–Schmid's general bounds did
*not* pin it — they give 9 and 10 and equality is shown by a separate argument —
whereas the searcher returns it directly.

## Where the frontier actually is — prior-art gate, run before investment

`D_2(C_2^6)` was the intended target. It is **already known**. Freeze–Schmid,
verbatim:

> "we obtain the precise value of `D2 (C2r )` for `r = 4` and `r = 6`, namely 8
> and 11, resp. For `r = 2` and `r = 3` the bounds also yield the exact value.
> For `r = 5`, the lower and upper bounds do not coincide, they are 9 and 10,
> resp., yet below we will show that equality holds at the upper bound. **For
> larger `r` our bounds are far apart**, yet for sufficiently large `r`, better
> bounds can be obtained using results from coding theory, namely
> `1.26r <= D2 (C2r ) <= 1.40r`."

So for elementary 2-groups the settled range is `r <= 6`, and **`r >= 7` is open
with only asymptotic coding bounds**. That is the seventh prior-art hit in this
programme and the third caught *before* the work was spent.

## Feasibility, stated honestly

`D_2(C_2^7)` is the natural next constant and is **out of reach for this
searcher**. Cost signal: `C_2^5` closes in 10.6 M nodes; `C_2^6` is still at
length 8 of the required 10 after 3.4 M nodes, on 64 elements against 32. Rank 7
doubles the alphabet again. Recorded as `CANNOT_CHECK_RESOURCE_BOUND` for this
method rather than left as an open to-do.

A `C_2^6` run is in progress purely as a **sixth validation** against the
published 11, not as a discovery.

## Authority

`mathematical_proposal: true`, `novelty_claim: false`. The searcher is
infrastructure; every value it has produced is a published one, and it is
recorded as reproducing them rather than finding them.

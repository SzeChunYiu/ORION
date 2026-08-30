# ORION-04 primary-source novelty review V1

**Scope.** Discharges the #1701 box "Run current primary-source novelty review
for Davenport/zero-sum/combinatorial bounds."

**Claim under review.** `D_4(C_5^3) = 30`, and consequently
`D_k(C_5^3) = 5k + 10` for every `k >= 2`.

**Method.** Literature retrieved 2026-08-30 against the primary arXiv record,
not against secondary summaries. Each subtraction below cites the retrieved
source text. `D_k(G)` throughout is the k-th Davenport constant: the least `l`
such that every sequence over `G` of length `>= l` has `k` disjoint nontrivial
zero-sum subsequences.

## What the primary sources establish

**1. Rank <= 2 is solved; the formula is linear in k.**
Zhong, *On the inverse problem of the k-th Davenport constants for groups of
rank 2* (arXiv:2503.21231, 2025-03-27), Theorem 2.4, citing Geroldinger–
Halter-Koch [27, Thm 6.1.5]: for `G = C_{n_1} + C_{n_2}` with `n_1 | n_2`,
`D_k(G) = n_1 + k n_2 - 1`. That paper's entire scope is rank 2; it computes
`D_k` for no rank-3 group.

**2. The linear form is known to hold eventually, and known to FAIL at rank >= 3
for p = 2 and p = 3.** Same source, p. 2, on Freeze–Schmid (2010): `D_k(G) =
D_0(G) + k exp(G)` for some `D_0(G)` and all sufficiently large `k`; it holds
for all `k` at rank <= 2; "Yet, it fails for elementary 2 and 3-groups of rank
at least 3", citing Delorme–Ordaz–Quiroz and Bhowmik–Schlage-Puchta. The same
page states computing or even bounding `D_k` is substantially harder than `D(G)`
for elementary p-groups.

**3. The rank-3 literature computes DIFFERENT invariants.**
Zhang, *On some zero-sum invariants for abelian groups of rank three*
(arXiv:2310.05458, 2023-10-09) treats `s_{k exp(G)}(G)` and `s_{<= t}(G)`, not
`D_k`. Its exact rank-3 values are for `C_3^3` and `C_{3^n}^3`
(Theorems 1.3, 1.6, 1.8). Girard–Schmid, *Direct/Inverse zero-sum problems for
certain groups of rank three*, address `D(G)`, `eta`, `s`, not `D_k`.

## Subtraction

| Source | Invariant | Rank | Covers C_5^3? |
|---|---|---|---|
| Zhong 2025 (2503.21231) | `D_k` | 2 only | No |
| Geroldinger–Halter-Koch Thm 6.1.5 | `D_k` | <= 2 | No |
| Zhang 2023 (2310.05458) | `s_{k exp}`, `s_{<=t}` | 3 | No — different invariant, and p=3 |
| Girard–Schmid rank-three papers | `D`, `eta`, `s` | 3 | No — different invariant |
| Delorme–Ordaz–Quiroz; Bhowmik–Schlage-Puchta | `D_k` failures | >= 3 | No — p=2,3 |

No retrieved primary source computes `D_k` for any elementary p-group of rank 3
with `p >= 5`.

## What is therefore new

`D(C_5^3) = 3(5-1) + 1 = 13` is classical (Olson). The claim under review is not
about `D`; it is the first exact `D_k` determination for an elementary p-group of
rank 3 at `p = 5`, and it asserts that the linear form `D_0 + k exp(G)` **holds**
there with `D_0 = 10`, from `k = 2` onward.

Two things make that a non-trivial position rather than an application of a known
formula:

- The rank-2 formula does not apply and gives no prediction at rank 3.
- The nearest rank-3 evidence in the literature is evidence of **failure** of the
  linear form (at `p = 2, 3`). A rank-3 case where it holds is therefore a
  boundary result about where that failure stops, not a routine extension.
- The onset is genuinely at `k = 2`, not `k = 1`: `5(1) + 10 = 15 != 13 = D(G)`.
  This is consistent with Freeze–Schmid ("all sufficiently large k") and must be
  stated as `k >= 2`, never as all `k`.

## Boundaries this review does NOT clear

- It does not verify the proof of `D_4(C_5^3) = 30`. It establishes only that no
  retrieved primary source already contains the value, in either direction.
- Retrieval covers the arXiv primary record. A pre-arXiv or non-indexed
  determination of `D_k(C_5^3)` would not have been caught, and the manuscript
  should not claim exhaustive priority — only that the standard references
  (Gao–Geroldinger survey, Geroldinger–Halter-Koch monograph, and the current
  rank-2/rank-3 literature above) do not contain it.
- `D_4(C_5^3) = 31` appears in the repository as a competing branch. This review
  is agnostic between 30 and 31; it subtracts prior work from *whichever* value
  the proof establishes.

**Terminal:** `NOVELTY_SUBTRACTION_COMPLETE__NO_PRIMARY_SOURCE_COMPUTES_D_K_FOR_RANK_3_P_GE_5`

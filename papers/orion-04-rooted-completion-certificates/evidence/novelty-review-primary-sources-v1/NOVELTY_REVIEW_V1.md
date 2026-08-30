# ORION-04 primary-source novelty review V1

**Scope.** Discharges the #1701 box "Run current primary-source novelty review
for Davenport/zero-sum/combinatorial bounds."

**Status of the target, established first.** ORION-04 does **not** currently
assert a value for `D_4(C_5^3)`. `CLAIM_LEDGER.md` records both candidates as
open: `N-C11` (`D_4(C_5^3)=30`) is `OPEN; top-tier blocker`, and `N-C12`
(`D_4(C_5^3)=31`) is `OPEN` with `no admitted extremal`. The proof-handoff
packet `evidence/d4-proof-handoff-v1/` is terminal at
`PROOF_INTERFACE_FROZEN__D4_EXECUTION_UNAUTHORIZED` with
`scientific_authority_delta: NONE`, and states in its own disposition that it
supplies no size-30 construction, executes no size-31 impossibility proof, and
that `exact D_4(C_5^3)=30` is **not** a manuscript-authorized claim.

This review therefore subtracts prior work from an **open target**. It does not
presuppose either value, and nothing below should be read as support for one.

**Method.** Literature retrieved 2026-08-30 against the primary arXiv record,
not against secondary summaries. `D_k(G)` throughout is the k-th Davenport
constant: the least `l` such that every sequence over `G` of length `>= l` has
`k` disjoint nontrivial zero-sum subsequences.

## What the primary sources establish

**1. Rank <= 2 is solved; the formula is linear in k.**
Zhong, *On the inverse problem of the k-th Davenport constants for groups of
rank 2* (arXiv:2503.21231, 2025-03-27), Theorem 2.4, citing Geroldinger–
Halter-Koch [27, Thm 6.1.5]: for `G = C_{n_1} + C_{n_2}` with `n_1 | n_2`,
`D_k(G) = n_1 + k n_2 - 1`. That paper's entire scope is rank 2; it computes
`D_k` for no rank-3 group.

**2. The linear form holds eventually, and is known to FAIL at rank >= 3 for
p = 2 and p = 3.** Same source, p. 2, on Freeze–Schmid (2010): `D_k(G) =
D_0(G) + k exp(G)` for some `D_0(G)` and all sufficiently large `k`; it holds
for all `k` at rank <= 2; "Yet, it fails for elementary 2 and 3-groups of rank
at least 3", citing Delorme–Ordaz–Quiroz and Bhowmik–Schlage-Puchta. The same
page states computing or even bounding `D_k` is substantially harder than
`D(G)` for elementary p-groups.

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
| Zhang 2023 (2310.05458) | `s_{k exp}`, `s_{<=t}` | 3 | No — different invariant, p=3 |
| Girard–Schmid rank-three papers | `D`, `eta`, `s` | 3 | No — different invariant |
| Delorme–Ordaz–Quiroz; Bhowmik–Schlage-Puchta | `D_k` failures | >= 3 | No — p=2,3 |

**Finding: no retrieved primary source computes `D_k` for any elementary
p-group of rank 3 with `p >= 5`, at any value.**

## What this does and does not buy the paper

**Buys:** the target is open in the literature, not merely open in this
repository. Whichever value ORION-04 eventually proves would be the first exact
`D_k` determination for an elementary p-group of rank 3 at `p >= 5`. Two things
make that non-routine: the rank-2 formula does not apply and yields no
prediction at rank 3; and the nearest rank-3 evidence is evidence of *failure*
of the linear form at `p = 2, 3`, so a rank-3 case either way is a boundary
result about where that failure stops.

**Does not buy:** any support for 30 over 31, or for the linear form holding at
`p = 5`. `D(C_5^3) = 13` is classical (Olson) and is not in question; the open
target is `D_4`, and `5(1)+10 = 15 != 13` means any linear form can begin no
earlier than `k = 2` — which is consistent with Freeze–Schmid's "sufficiently
large k" but is a constraint on how a result must be stated, not evidence for
one.

## Boundaries

- This review verifies no proof. It establishes only that no retrieved primary
  source already contains a value for `D_k(C_5^3)`, in either direction.
- Retrieval covers the arXiv primary record. A pre-arXiv or non-indexed
  determination would not have been caught, so the manuscript should claim only
  that the standard references (Gao–Geroldinger survey, Geroldinger–Halter-Koch
  monograph, and the rank-2/rank-3 literature above) do not contain it — never
  exhaustive priority.
- The `N-C11`/`N-C12` discrepancy is a live top-tier blocker tracked in the
  claim ledger. Structurally: `D_4 >= 30` and `D_4 = 31` are consistent, so the
  discriminating artifact is whichever carries `<= 30` — here
  `d4-proof-handoff-v1/PROOF_OBJECT_CONTRACT_V1.md`, which is frozen as an
  interface and explicitly unexecuted. The `>=` direction is machine-checkable
  from a witness sequence; the `<=` direction is universal over the length-30
  space and resolves by argument, not by enumeration.

**Terminal:** `NOVELTY_SUBTRACTION_COMPLETE__NO_PRIMARY_SOURCE_COMPUTES_D_K_FOR_RANK_3_P_GE_5__TARGET_REMAINS_OPEN`

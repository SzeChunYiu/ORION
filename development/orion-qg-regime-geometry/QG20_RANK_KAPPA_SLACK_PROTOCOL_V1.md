# QG-20 — the rank-κ slack: measuring the gap between certified syndrome rank and intrinsic support number

Date: 2026-08-22
Lane: ORION-QG / regime geometry, wave 3
Branch: `claude/orion-harness-verification-b17qdj`
Status: **FROZEN BEFORE ANY OUTCOME-DETERMINING RUN.**

Authority ceiling: **NOT_R6**. No novelty authority, no donor-novelty authority,
no physical-quantum-advantage claim, no new chemistry data. The protected
stretched-N₂ discriminator is never read. Every committed analyzer imported by
this lane is imported **unmodified**. No repository file outside the three files
listed in §9 is created, and **no existing file is modified**.

Runtime cap: **< 25 minutes per run** (wall clock, single process). Every declared
domain in §3–§5 is executed in full. **No silent truncation**: every domain size is
recomputed at runtime and recorded verbatim in the RESULTS file, and every declared
`expected_*` size is asserted.

---

## 0. The negative this lane addresses

QG-6 (`research/extensions/orion-qg/QG6_SYNDROME_DIMENSION_RESULTS.json`) shows the
production DP transition tables yield a rewrite-relevant conserved-syndrome quotient
automatically: F₂-rank **2** for every R6M frame slot under the rewrite
`ZERO_ONE_FRAME_LOCAL_LETTER`, F₂-rank **5** for every R6I block under the rewrite
`ZERO_BOTH_INDEPENDENT_GENERATORS_OF_ONE_BLOCK`. That certifies a finite-support
normal form exists (QG-6's `meta_theorem`, support bound `d`), and gives QG-6's
`search_complexity_corollary` `sum_{k=0}^d binom(n,k) A^k`.

The intrinsic support numbers are now known two-sidedly and **do not match the ranks**:

* κ_R6I = 1 (QG-9 V6, `intrinsic_support_number`) against rank 5;
* κ_TARE = 2 (QG-18, `intrinsic_support_number`) against rank 2.

The certificate is therefore **sound but loose**, and by four polynomial orders in
QG-6's certified search corollary for R6I. The reopen adjudication classified the
slack `UNRESOLVED_OR_NON_IDENTIFIABLE`.

**The hypothesis under test (stated as a hypothesis, not an assumption).** QG-18's
Q3 structural diagnosis isolates an *exchange margin*: Tag relocation (the QG-9 V6
move that collapses κ_R6I to 1) is available exactly when the per-column frame refund
**strictly** exceeds the maximum Restore penalty of deleting that column. QG-18 records
that margin as 4 for R6I and 0 for TARE. The hypothesis is that this margin also
governs the *size* of the rank-κ slack:

> **H1 (candidate relation, NOT a law).** `slack := rank − κ` equals the exchange
> margin `μ` on every family carrying both numbers.

Two families is not a law and this protocol commits in advance to saying so.

---

## 1. Frozen questions (verbatim)

**Q1 (exact slack table).** For every family in the programme with both a certified
syndrome rank and a two-sided κ, compute rank, κ, slack = rank − κ, and the
QG-18-style exchange margin (per-column frame refund minus maximum Restore penalty,
on its complete local domain, exact integer arithmetic). Bind every input value
verbatim to its committed receipt. Report the table.

**Q2 (does the margin predict the slack?).** State the relation exactly as the data
shows it — including, if it holds, that `slack == margin` on both families — and then
state with equal precision **why two families cannot establish a law**: what a third
family would have to show, and what the relation predicts for it. If the relation does
NOT hold, that is the finding; report it plainly.

**Q3 (a third data point, if cheap).** The programme has a third family with an exact
referee: StabPrep (`QG15_THIRD_FAMILY_RESULTS.json`) — H/S/SDG cost 1 + CNOT cost 3,
exact Dijkstra referee over complete stabilizer-state graphs. Determine honestly whether
a syndrome rank and a two-sided κ are *cheaply* derivable for it under the frozen
definitions. If yes, compute them and extend the table to three points. If no — the QG-6
rank construction may not transfer to a family without R6M/R6I's block/frame structure —
say so precisely and state what would be needed. Do not force it; a clean "does not
transfer, here is why" is a legitimate and useful outcome.

---

## 2. Frozen definitions

### 2.1 Certified syndrome rank (QG-6 definition, imported unchanged)

For a production DP with a packed local transition table `_DELTA` over `w` state bits
and a designated **local zeroing rewrite** `ρ`, the *conserved-syndrome quotient rank*
of `ρ` is

```
rank(ρ) = dim_{F_2} span { _DELTA[x] XOR _DELTA[ρ(x)] : x in the complete local option domain }
```

taken over the complete domain of local option rows, using GF(2) elimination on
integers. QG-6's committed values are the **certified** ranks used in Q1:

| family | rewrite | scope | rank field in QG-6 receipt |
|---|---|---|---|
| R6M / TARE | `ZERO_ONE_FRAME_LOCAL_LETTER` | per frame slot (6 slots) | `r6m.auto_dimension` |
| R6I | `ZERO_BOTH_INDEPENDENT_GENERATORS_OF_ONE_BLOCK` | per block (2 blocks) | `r6i.auto_dimension` |

This lane **recomputes** both ranks from the production `_DELTA` arrays and asserts
bit-equality with the committed receipt fields; it does not substitute a new definition.

### 2.2 Intrinsic support number κ (manuscript definition, imported unchanged)

κ(F, C) is the least B such that every instance's exact optimum is attained by a
configuration all of whose structural generators have global support ≤ B; equivalently
B is a valid support bound and B − 1 is not. Two-sided values are taken **verbatim**
from committed receipts:

| family | κ | receipt | field |
|---|---|---|---|
| R6I | 1 | `QG9_V6_SUPPORT1_NORMALIZATION_RESULTS.json` | `intrinsic_support_number` |
| R6M / TARE | 2 | `QG18_TARE_KAPPA_RESULTS.json` | `intrinsic_support_number` (and `kappa_interval == [2,2]`) |

### 2.3 Slack

`slack := rank − κ`, exact integer subtraction. Both operands are integers by §2.1/§2.2;
the checker asserts `isinstance(..., int)` on every operand and on the difference.

### 2.4 Exchange margin μ (the QG-18 Q3 quantity, frozen here)

For a family whose local cost decomposes, at one column of one block, into a **frame
contribution** (refunded when that column is zeroed) and a **Restore contribution**
(which may worsen when the frame is removed), define over the **complete local deletion
domain** D:

```
delta(d)  = Restore_after(d) − Restore_before(d) − refund(d)      for d in D
mu        = − max_{d in D} delta(d)
          = min_{d in D} ( refund(d) − RestorePenalty(d) )
```

i.e. μ is the **deletion credit floor**: the per-column frame refund minus the maximum
Restore penalty, minimised over the complete local domain. μ ≥ 1 is exactly QG-18's
strict exchange inequality (`l1_deletion_credit.holds`); μ = 0 is a tie set.

Committed values this lane must reproduce **exactly**:

| family | μ | receipt | field |
|---|---|---|---|
| R6I | 4 | `QG9_V6_SUPPORT1_NORMALIZATION_RESULTS.json` | `composition.extra_active_column_credit_floor` (= `−max(finite_lemmas.deletion.max_delta_commuting, max_delta_anticommuting)`) |
| R6M / TARE | 0 | `QG18_TARE_KAPPA_RESULTS.json` | `q2_tag_relocation_transfer.l1_deletion_credit.credit_floor` (and `.composition.tare_credit_floor`) |

Cross-binding: QG-18 records the R6I number independently as
`q2_tag_relocation_transfer.l1_deletion_credit.r6i_reference_credit_floor` and
`receipt_bindings.r6i_reference_numbers_from_qg9v6.credit_floor`; both must equal the
QG-9 V6 value or the run fails gate G4.

### 2.5 Exact arithmetic

Every rank, κ, μ, slack and every intermediate cost is a Python `int` (or a NumPy
integer immediately narrowed to `int`). The checker asserts, at every decision point,
that no operand is a `float` / `numpy.floating`. Any float reaching a decision aborts
the run (gate G2).

---

## 3. Frozen domains — margin recomputation

**R6I deletion domain** (rebuilt from the production R6I local algebra; the rank-2
dependent triple `(a, b, ab)`, raw frame cost with multipliers `[4,4,4]` and `2` at the
central slot, Restore cost `sum_k w(p_k · r_k)`):

* letter pairs `(a,b) ∈ {0..3}² \ {(0,0)}`: 15
* Restore targets `p ∈ {0..3}³`: 64
* central slot `∈ {0,1,2}`: 3
* **expected rows: 2880** (commuting 1728 / anticommuting 1152)

**R6M / TARE deletion domain** (rebuilt from the production R6M local algebra and the
donor-owned all-three common-factor rule F3; two frame slots per block, multipliers
`(2,4)` or `(4,2)` by the central bit, Restore change scored through F3 at the block's
slot with the other two blocks' letters free):

* commuting letter pairs (symp = 0, not `(0,0)`): 9; anticommuting: 6
* block slot `∈ {A,B,C}`: 3; central bit `∈ {0,1}`: 2
* free letters `(p0,p1,u0,v0,u1,v1) ∈ {0..3}⁶`: 4096
* **expected rows: commuting 221184, anticommuting 147456, total 368640**

Both domains are enumerated in full. Row counts are recomputed and asserted.

## 4. Frozen domains — rank recomputation

* **R6M**: complete local option domain `{0..3}⁷` = **16384** rows; six frame slots
  `A0,A1,B0,B1,C0,C1`; rewrite zeroes one slot.
* **R6I**: complete local option domain `{0..3}⁶` = **4096** rows; two blocks `A,B`;
  rewrite zeroes both generators of one block.

Ranks are computed by GF(2) elimination over the XOR change-vectors and asserted equal
to the QG-6 committed per-slot / per-block ranks and `auto_dimension`.

## 5. Frozen rewrite-alignment diagnostic (declared before the outcome is known)

The two certified ranks are taken under **different** rewrites: R6M's zeroes *one* frame
letter, R6I's zeroes *both* generators of a block. The margin domains of §3, by contrast,
both zero *both* frame letters of one block. To expose whether the Q1 table is an artifact
of that mismatch, this lane additionally computes, over the same complete `{0..3}⁷`
domain, the R6M **block-level** rank under the rewrite that zeroes both letters of one
block (`ZERO_BOTH_FRAME_LETTERS_OF_ONE_BLOCK`, blocks `A={A0,A1}`, `B={B0,B1}`,
`C={C0,C1}`).

This is a **diagnostic**, not a substitution: Q1's table uses the QG-6 certified rank.
The outcome is unknown at freeze time and is reported either way:

* if the block-level R6M rank is also 2, the mismatch is immaterial and H1's evidence is
  unaffected;
* if it differs from 2, the Q1 table's agreement (or disagreement) with H1 is **rewrite-
  dependent**, and the receipt must say so and report the alternative slack alongside.

## 6. Q3 transfer test for StabPrep (frozen criteria)

StabPrep admits a syndrome rank and a two-sided κ *cheaply* iff all three hold:

* **T1** — a production local transition table over packed state bits exists, indexed by
  local option letters, on which a local zeroing rewrite `ρ` is defined (§2.1);
* **T2** — the family's solution object has *structural generators carrying a global
  support*, so that κ is defined by §2.2 as a discovered invariant rather than fixed by
  the frozen alphabet;
* **T3** — the local cost admits a frame-refund / Restore-penalty decomposition at a
  column, so μ of §2.4 is defined (a *missing* decomposition means μ is **undefined**,
  which is NOT the same as μ = 0).

Each of T1/T2/T3 is checked mechanically against `QG15_THIRD_FAMILY_RESULTS.json` and
against the committed `qg15_third_family.py` source (structural greps recorded verbatim
in the receipt: presence/absence of a `_DELTA`-style table, of a Tag/Restore split, of a
frame column). If all three hold, the table extends to three points. If any fails, the
terminal is `QG20_PARTIAL__THIRD_FAMILY_NOT_DERIVABLE` and the receipt records which
criterion failed and precisely what a fourth candidate family would need to supply.

## 7. Terminals (frozen, exhaustive)

* `QG20_SLACK_CHARACTERIZED__MARGIN_RELATION_HOLDS` — `slack == mu` exactly on every
  measured family, with the two-point caveat stated in the receipt's claim boundary.
* `QG20_SLACK_MEASURED__NO_RELATION` — the table stands; `slack != mu` on at least one
  measured family. Honest negative.
* `QG20_PARTIAL__THIRD_FAMILY_NOT_DERIVABLE` — the two-family table plus a precise
  statement of why the third resists. This terminal is **compatible with** the relation
  holding on the two measured families and, when it does, the receipt carries both facts
  (`margin_relation_holds: true` and the third-family non-derivability).
* `QG20_CANNOT_CHECK` — a required receipt is missing, a binding fails, or a domain
  cannot be executed in full.

Terminal selection rule, frozen: if any binding/domain gate fails → `QG20_CANNOT_CHECK`.
Else if the relation fails on a measured family → `QG20_SLACK_MEASURED__NO_RELATION`.
Else if Q3's T1/T2/T3 all hold → `QG20_SLACK_CHARACTERIZED__MARGIN_RELATION_HOLDS`.
Else → `QG20_PARTIAL__THIRD_FAMILY_NOT_DERIVABLE`.

## 8. Gates (all must be true)

* **G1 receipts_sha256_exact** — every source receipt's sha256 recorded and re-read;
  every bound value read from its committed receipt by the receipt's own field name.
* **G2 exact_integer_arithmetic** — no float/`numpy.floating` reaches any decision;
  asserted at every comparison.
* **G3 domains_complete_no_truncation** — every declared domain size in §3–§5 recomputed
  at runtime and equal to the declared expected value.
* **G4 margin_recomputed_equals_receipt** — the independently recomputed μ for each family
  equals the committed receipt value, and QG-18's R6I cross-reference equals QG-9 V6's.
* **G5 rank_recomputed_equals_receipt** — recomputed per-slot / per-block ranks equal
  QG-6's committed ranks and `auto_dimension`.
* **G6 kappa_two_sided** — each κ used is two-sided in its own receipt
  (QG-18 `kappa_interval == [2,2]`; QG-9 V6 `support_bound == 1` and
  `support0_infeasible == true`).
* **G7 authority_ceiling_not_r6** — the emitted authority string contains `NOT_R6`, and
  `novelty_credit`, `donor_novelty_credit`, `r6_authority`,
  `physical_quantum_advantage_claim` are all false.
* **G8 no_chemistry_read / protected_subject_not_read / no_network**.
* **G9 claim_boundary_states_two_point_limit** — the receipt's authority string and claim
  boundary explicitly deny law/theorem status for the relation. Mechanically checked:
  the authority string must contain `CANDIDATE_RELATION` and `TWO_POINTS`, and must
  contain neither `THEOREM` nor `LAW`.
* **G10 runtime_within_cap** — total wall clock < 1500 s.
* **G11 rewrite_alignment_diagnostic_reported** — §5 executed and its outcome recorded
  whichever way it lands.
* **G12 no_existing_repository_file_modified**.

## 9. Files this lane creates (and the only ones)

1. `development/orion-qg-regime-geometry/QG20_RANK_KAPPA_SLACK_PROTOCOL_V1.md` (this file)
2. `research/extensions/orion-qg/qg20_rank_kappa_slack.py`
3. `research/extensions/orion-qg/QG20_RANK_KAPPA_SLACK_RESULTS.json`
4. `development/orion-qg-regime-geometry/qg20_generic_verify.py`

The checker prints exactly one canonical stdout token line `ORIONQG_QG20={...}` and is
run twice; the two RESULTS files must be **byte-identical** (no wall-clock in the digest;
timing is written outside the digested object). The generic verifier is an independent
pure-primitive rebuild (no analyzer imports, no NumPy) emitting exactly one decision line
`QG20_GENERIC_VERIFY=ACCEPT` or `=REJECT`.

## 10. Honesty constraint (load-bearing)

With two or three data points this lane may report a **coincidence** or a **candidate
relation**, never a law and never a theorem. The receipt's `authority` and
`claim_boundary` must make that explicit, and the claim boundary must record the
specific alternative accounts that the available data cannot distinguish from H1.
Overclaiming a pattern from two points is precisely the error this lane exists to avoid.

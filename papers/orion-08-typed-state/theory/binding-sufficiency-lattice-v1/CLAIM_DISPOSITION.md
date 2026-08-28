# ORION08.BINDING_SUFFICIENCY_LATTICE.v1 — CLAIM DISPOSITION

**Date:** 2026-08-28
**Terminal:** `THEORY_PROVED__INSTANTIATED_ON_FROZEN_RECEIPTS`
**Scientific authority delta:** `NONE`
**New blocker raised:** none

---

## 1. What changed

One additive directory under `papers/orion-08-typed-state/theory/`. No
manuscript, ledger, receipt or `submission_tmlr/` byte was modified.

The ORION-08 content-freeze script reports `FROZEN` with the directory present,
but **that script re-pins rather than verifies** — it writes `paper_tree_oid` and
rewrites `subject_commit` to the current `HEAD`. Its PASS is therefore not
evidence of unchanged content. What is true is that the change is purely
additive, and that it moves ORION-08's `paper_tree_oid` from the pinned
`5f923e9a9d1e` to `e353f6691507`. Disclosed rather than hidden; see issue #1625.

## 2. What was established

**Theorem 1.** A deterministic zero-regret policy reading only a binding `B`
exists iff every positive-mass `B`-fibre has a common optimal action.

**Theorem 2.** Refinement never increases Bayes risk, and strictly decreases it
**exactly when** it splits a positive-mass fibre whose worlds share no optimal
action.

So decision value is not monotone in "amount of typed state" — only in fibre
purity with respect to optimal actions. That is the criterion behind ORION-08's
existing, correct refusal to claim that more typed state always helps.

## 3. The instantiation is the useful part

| family | binding | fraction of achievable gap captured |
|---|---|---|
| N4-B scoped reopening | `ORION_SCOPED_REOPEN` | **7.6%** pooled (`1.7%` wasteful, `10.3%` stale-matters) |
| N4-F3 typed transport | `ORION_TYPED_TRANSPORT` | **98.4%** vs naive, **81.9%** vs strongest baseline |

Both families carry `SUPPORTED` terminals. They differ by more than an order of
magnitude in how much decision value the binding actually captures.

**A `SUPPORTED` terminal certifies direction, not magnitude.** That is the
precise form of the paper's qualitative caution, and it is the contribution here.

The per-regime split is exactly Theorem 2's prediction: in `REOPEN_WASTEFUL`
never-reopening is already near-optimal, so the refinement splits fibres that
were effectively action-pure and buys `1.7%`; in `STALE_MATTERS` the fibres
genuinely differ, so it buys `10.3%` — and still leaves `89.7%` open.

## 4. Adverse evidence — preserved, and one new quantity recorded

Nothing is softened. The no-value regime the paper acknowledges now has a number
(`1.7%`), and a new adverse quantity is recorded: **N4-B leaves `92.4%` of the
achievable decision value uncaptured**. That is not a refutation — the terminal
and all four gates stand — but it bounds how far the `SUPPORTED` verdict can be
read.

Gap fractions are reported against the **strongest** non-oracle baseline in each
family. Choosing the weakest would have flattered the binding.

The exact-synthetic scope, the N4-B "initial receipts only" scope limit,
`novelty_authorized: false`, `p10_authorized: false` and the N4-B claim boundary
are all unchanged.

## 5. Donor boundary

**No novelty claimed.** Decision sufficiency, the common-optimal-action criterion
and refinement monotonicity are donor-owned (comparison of experiments, Blackwell
ordering, sufficient statistics). Per #1617 this generic theory belongs to the
programme once, shared with ORION-22's information boundary, rather than being
claimed independently by ORION-08.

## 6. Recommended manuscript action — referred, not taken

Two optional additive strengthenings, both authority-neutral:

1. state the sufficiency criterion as the reason more typed state does not always
   help, rather than as an empirical observation;
2. report the captured-value fractions alongside the family terminals, so
   `SUPPORTED` is not read as "large".

Neither is taken here. `submission_tmlr/` is byte-bound under #1601, and issue
#1634 records that no sanctioned path yet exists for correcting a manuscript
bound by a paper-level `SHA256SUMS` — so manuscript edits must wait for that
path rather than being taken as a side effect of a theory lane.

## 7. Blocker status

`ORION-08 IS NOT BLOCKED BY THIS LANE.` Real-domain transfer remains successor
work, exactly as #1609 requires.

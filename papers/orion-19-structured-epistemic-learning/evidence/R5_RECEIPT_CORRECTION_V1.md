# Correction: `P9_R5_MANUSCRIPT_INTEGRATION_RECEIPT_V1.md` describes manuscript edits that are not on `main`

**Written:** 2026-09-01, against `origin/main`.
**Scientific authority delta:** `NONE`.
**Scope:** the receipt's *evidence-recovery* half is accurate and stands. Its
*manuscript-integration* half is not supported by the tree.

The receipt is left byte-unchanged and corrected beside itself, for the reason
`ADJUDICATION_CORRECTION_V1.md` gives in ORION-17: rewriting a receipt that turned out to
be wrong erases the evidence that it was wrong, which is what a later reader most needs.

## What is accurate

The section headed *"Sources, recovered path-by-path (no branch merged)"* checks out.
Every artifact it names resolves on `origin/main`:

| artifact | paths on main |
|---|---|
| `evidence/P9_CAUSAL_DIAGNOSTIC_TRANSPORT_V3_RECEIPT.md` | 1 |
| `evidence/P9_CAUSAL_DIAGNOSTIC_TRANSPORT_V3_RUN.json` | 1 |
| `evidence/R5_REVIVAL_LEDGER_V1.json` | 1 |
| `theory/orbit-coverage-gate-v1/` | 3 |
| `experiments/ut3-checkpoint-custody-v1/` | 10 |

Control: 222 ORION-19 paths total, so the index resolves.

**The V3 causal-diagnostic result, the orbit-coverage gate and the UT3 custody record are
all really on `main`.** The science was recovered. That is the half worth keeping.

## What is not supported

The section headed *"What the manuscript now states
(`manuscript/sections/05-results.tex`)"* states *"Three subsections were added"*, and a
later section makes a specific, checkable claim:

> *"The manuscript states UT3 as custody-only … (grep for `u-t3|ut3|u_t3` returns three
> lines, all inside that subsection)."*

Re-run across all 14 text files of `manuscript/` on `origin/main`:

```
u-t3 | ut3 | u_t3      0 matches
LCB95                  0
TRANSPORT_V3           0
orbit-coverage         0
CONTROL "the"        390
```

`manuscript/sections/05-results.tex` **does exist** — the file is present, alongside the
other seven sections. It simply does not contain the three subsections the receipt says
were added, nor any of the V3 / orbit-coverage / UT3 content.

So this is not a stale path or a renamed file. It is a receipt asserting an edit that the
tree does not carry.

## Why the distinction matters

A hostile review of this paper found that *"the manuscript is not synchronized with the
newest science."* That is exactly this, and the receipt is the reason it was not caught
earlier: anyone auditing ORION-19 by reading its receipts would conclude the integration
had happened.

The failure mode is the same one recorded for ORION-17's `GOVERNANCE_ADJUDICATION_V1.md`
§4 — a document headed *"What was added"* asserting additions absent from the tree. Two
independent instances is a pattern worth naming: **integration receipts written from a
working branch, describing edits that were never carried across to `main`.** The evidence
files survive the transfer because they are new paths; manuscript *edits* do not, because
they are modifications to files that already exist and are easy to drop in a
path-by-path recovery.

## Consequence for the paper's terminal

`JOURNAL_READINESS.md` records
`P9_BOUNDED_STRUCTURAL_LEARNING_PEER_REVIEW_READY`, and is careful to say this is *"a
bounded peer-review terminal, not an acceptance claim."* That terminal is **not**
withdrawn here — the underlying evidence is on `main` and the bounded claim rests on it.

What is withdrawn is any implication that the **manuscript** presents the V3 result, the
orbit-coverage gate or the UT3 custody record. It does not. Filing the paper as it stands
would submit a manuscript whose body omits the newest science its own evidence directory
contains.

## The work, now done in the same change

The three subsections have been written into `manuscript/sections/05-results.tex` from
the artifacts already on `main`, under `papers/PAPER_WRITING_SKILLS_PROTOCOL_V1.md`:

- **`sec:v3-transport`** — the uncertainty-aware decision rule and the repaired V2
  stability clause, including that D-A remains `CANNOT_CHECK` as a stable abstention
  rather than becoming a pass;
- **`sec:orbit-gate`** — the 112/128 orbit ceiling against the model's 96/128, split into
  16 irreducible and 16 recoverable errors, with the coverage asymmetry that makes it a
  boundary rather than a model result;
- **`sec:ut3-custody`** — U-T3 as `ENVIRONMENT_AND_CUSTODY_RECEIPT_ONLY`, four of six
  checkpoints in custody, **zero grid cells executed**, and the two gated `401` rungs
  preserved as `CANNOT_CHECK`.

No experiment was run and no number recomputed. Every numeral in the new text was checked
against the three source artifacts: 28 of 29 appear verbatim, and the twenty-ninth
(`0.9610`) is the four-decimal rounding of the recorded `0.9609990859868461`, whose
comparison against the `0.95` target holds at either precision.

So the description that motivated this correction — *evidence integrated, manuscript
not* — no longer holds, and this file records both halves: what the receipt got wrong,
and the integration it described now actually existing.

# Remaining blockers, after the execution pass

**Date:** 2026-08-23
**Companion data:** `EXTERNAL_ACQUISITION_AUDIT_2026-08-23.json`, section `execution_pass_2026_08_23`
**Nothing here was promoted.** No claim identity created, no gate evaluated, no protected outcome
read, no registered claim's authority changed.

## What moved

| Item | Outcome | What is left |
|---|---|---|
| **P5 H1–H4** | 9 blockers → 8; donor source-grounded | 8 `UNBOUND` protocol fields, all authorable |
| **P6 reproducibility** | precondition solved: 7/7 steps, 8/8 digests in a third environment | one custodian who is not you |
| **P9-T3 frontier** | corrected and specified | the experiment code does not exist; 0/1,344 cells |
| **P2 lexical echo** | CI reproduction defect solved | the archived task-world baseline, a different object |
| **P9-T4 / D1 v1.2** | the historical negative is explained | the five D1 v1.3 required inputs |

## The three findings worth keeping

**The 0.50 → 0.75 replay divergence is not two measurements disagreeing.** `TYPED_SERIALIZED_BAG`
predicts one class on all 128 protected cases, and that class is exactly half the split — so 0.5 is
a prior, not a measurement. Exactly 32 of 128 cases sit within 0.05 of the decision boundary and the
runner-up is correct on **all 32**, so tipping that set gives 0.5 + 32/128 = **0.75 exactly**. A
solver version change is all it takes. Neither number is evidence about representation quality,
which is precisely what D1 v1.3's replacement comparator exists to fix.

**P5's "external identities" blocker needs no outside party at all.** Eight of nine blockers are
literally the string `UNBOUND` in the protocol JSON — digests, an epoch, a revision id. The ninth
needed a freely retrievable paper to be read. And the one place the preflight *does* demand
separation — candidate policy owner must not equal protected evaluator owner — already passes and
was never among the blockers.

**The P2 CI failure was a comparison defect.** Four `mrr_at_50` values differ by at most three units
in the last place of a float64; two fresh runs are bit-identical to each other; no gate reads
`mrr_at_50`; the smallest gate threshold is 0.01. Demanding bit-equality of a floating-point mean
across library versions is an unattainable gate, not a failed one.

## What is actually left, by class

**Class D — someone who is not you.** The residual on P6, and on most of the eleven not attempted.
For P6 it is now the *only* thing left: the bundle runs, the packet is written, the verifier rejects
a receipt from the candidate, one that reused the candidate's execution unit, one missing a step and
one with a wrong digest. Free routes exist and run on a publication timescale.

**Class B — a third-party timestamp.** P5's eight fields are yours to write; what makes them a
*freeze* is that a registry timestamps them before outcomes exist.

**Construction, not acquisition.** P9-T3 needs an item generator, seven representations and a cell
runner built before a checkpoint is worth downloading. P9-T4 needs its five D1 v1.3 inputs, of which
the prospective power-and-attainability receipt is outcome-blind and entirely local — and, on P2's
precedent, the one most likely to kill the design before it runs.

**Class F — no free route.** Still exactly two: P4 and P14D, both wanting a blinded panel
adjudicating your own cases. Unchanged, and the honest move there remains a bounded claim rather
than an item left open forever.

## Not attempted

`P1.R7A.WIDE.SUCCESSOR`, `P3.C6_C8.EXTERNAL`, `P3.PARTIAL_OBSERVATION.SUCCESSOR`,
`P4.NATURALISTIC.GENERALITY`, `P5.WIDE.SUCCESSOR`, `P7.EMPIRICAL.NAVIGATION.EXTERNAL`,
`P8.DEPLOYED.AGENT.EXTERNAL`, `P10.PROTECTED.EXECUTION.EXTERNAL`, `P11.REAL_SYSTEMS.EXTERNAL`,
`P14.D.EXTERNAL_VALIDITY`, `P15.A.HARNESS.SUCCESSOR`.

Eleven of sixteen. Listing them is the point: an execution pass that reported only what it touched
would read as if it had touched everything.

## The next three, in order

1. **P9-T4's power and attainability receipt.** Outcome-blind, local, and it either clears the
   design or kills it before any compute is spent. P2's IoU ceiling is the precedent for why this
   goes first.
2. **P5's eight fields**, then a registry timestamp. That takes an item from `CANNOT_CHECK` to
   `READY_TO_FREEZE_CONFIRMATORY` with no outside party involved.
3. **Ask a P6 custodian.** Everything they need exists; the ask itself is the remaining work.

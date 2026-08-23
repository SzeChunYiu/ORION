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

## The finding that changes P9's plan

**The ORDER_PERMUTATION attack cannot change its own dataset.** D1 v1.3's representation contract
names `tuple(sorted(set(values)))` as its `forbidden_normalization`. That expression is not
hypothetical — it is verbatim what `orion.transfer.v2.p1_method_realization._tuple` computes, and
every method realization in the programme is built through it, across nine coordinates including all
four the order attack targets.

So the attack reverses each sequence coordinate and the constructor sorts it straight back. Measured:

- the ORDER_PERMUTATION dataset's manifest digest **equals** the base one;
- **128 of 128** protected cases are identical;
- **256** left-side coordinates were long enough to reorder, so there was material to attack;
- the SEMANTIC_ORBIT attack over the same machinery *does* change the data — so this is specific to
  order and multiplicity, not a broken harness.

To make sure the loss is upstream rather than in the arms, an order- and multiplicity-preserving
feature family was built to the freeze's own contract — round-trip verified, no contract violations
on any of the 128 cases — and it **still** measures zero opportunity. The information is gone before
any arm sees it.

**Consequences, none of which depend on an outcome.** D1 v1.3 registers ORDER_PERMUTATION and
DUPLICATE_INSERTION as two of its four attack families and TYPED_ORDERED_MULTIPLICITY as one of its
four arms. None of the three is reachable while that primitive normalizes to a sorted set. And the
fix is one function shared programme-wide, so it is not a P9 change.

Alongside it, the outcome-blind attainability pass over the existing arms: **4 of 12 measurable
cells meet the 0.25 opportunity gate, 8 have zero opportunity**, and the protocol forbids passing a
zero-opportunity cell. Power is adequate at low discordance (0.99 at 5%) and thin at high (0.42 at
40%), with the calibration check landing exactly on α as it should.

**This is what a power-and-attainability receipt is for.** It cost arithmetic, read no outcome, and
it says the design cannot be executed as registered — before any compute was spent. P2's frozen IoU
threshold of 0.03 against an arm capped at 0.0113 is the precedent for what happens when nobody runs
one.

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

1. ~~P9-T4's power and attainability receipt.~~ **Done, and it returned
   `OPPORTUNITY_GATE_UNATTAINABLE_ON_EXISTING_ARMS`.** The next step it implies is the one above:
   decide whether to change `_tuple` in the P1 primitive, which is a programme-wide decision about
   whether method realizations are sets or sequences — a modelling question, not a bug fix.
2. **P5's eight fields**, then a registry timestamp. That takes an item from `CANNOT_CHECK` to
   `READY_TO_FREEZE_CONFIRMATORY` with no outside party involved.
3. **Ask a P6 custodian.** Everything they need exists; the ask itself is the remaining work.

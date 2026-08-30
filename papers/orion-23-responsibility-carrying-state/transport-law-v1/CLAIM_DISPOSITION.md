# Claim disposition — ORION23.EXTERNAL_RESPONSIBILITY_TRANSPORT.v1

Protocol and theory frozen before verification ran. Terminal: **T1_TRANSPORT_LAW_HOLDS**.
Promotion status: **TRANSPORT_LAW_ESTABLISHED__PROMOTION_NOT_EARNED__BOUNDED_PAPER_RETAINED**.

## Result

750 cases: every status assignment over 3–4 load-bearing premises, each `UNKNOWN` premise
resolved both ways against a hidden actual value the decider cannot see.

| rule | unsound | over-revokes | abstains |
|---|---|---|---|
| **three-valued** | **0** | **0** | 296 |
| pessimistic collapse (`UNKNOWN` → `CONTRADICTED`) | 0 | **84** | 0 |
| optimistic collapse (`UNKNOWN` → `UNCHANGED`) | **212** | 0 | 0 |

P1, P2, P3 and P5 all hold with no counterexample.

## What the law says

`UNKNOWN` is a **third outcome**, not a bias to be chosen. The optimistic collapse carries
certificates on premises nobody established — unsound 212 times. The pessimistic collapse
never does that, but discards support that was never refuted — 84 unnecessary revocations.
The three-valued rule is the **unique** rule with zero of both, and it pays for that by
abstaining 296 times, which is the correct report when the answer is not determined.

That is the load-bearing distinction of the paper stated as a theorem: **no two-valued
transport rule is both sound and non-wasteful.** The choice is not a tuning preference.

## A control caught a defect in my own instrument

The first run returned **`T4_CANNOT_CHECK`**, because control V2 required the pessimistic
collapse to over-revoke at least once and it never did.

The cause was mine. I had defined ground truth as *"reuse is sound iff no premise is
`CONTRADICTED` or `UNKNOWN`"*, which makes `UNKNOWN` **definitionally** unsound to reuse.
Under that definition revoking on `UNKNOWN` is always correct, the pessimistic rule is
optimal, and P5 is false by construction rather than by evidence.

P3's own frozen wording rules that out: *"unnecessary revocation"* is only meaningful if
the premise **might in fact have been satisfied**. So the frozen claim already required a
hidden actual value behind `UNKNOWN`; the checker simply failed to model it.

The repair is to the **instrument**, not to the claims: each `UNKNOWN` premise now carries
a hidden actual value, enumerated both ways, invisible to every rule. No claim, margin,
terminal or control was changed. Had V2 not been written to demand a *positive*
demonstration of waste, this would have shipped as a passing result built on a tautology.

## The external corpus — retrospective, licensing nothing

`P13_P14_OBJECTIVE_GOLD_RESULTS_V1.json` records `outcome_accessed: true`, so **no frozen
test was run against it** and none is reported as evidence.

As a labelled observation only: that corpus covers 31 pinned repositories across 14
organizations with 123 facts decided and **32 CANNOT_CHECK**, because *"the locked
per-repository runtime the contract requires does not exist, and an exit status obtained
another way is not that fact."* That is `UNKNOWN` in the exact sense of P3 — a premise not
established, not one refuted — so the corpus **exhibits** the boundary this theorem
describes rather than crossing it.

## Why promotion is not earned

#1649: *if the external corpus does not support the broader transport claim, retain the
bounded current paper and publish the external boundary.* The corpus's own
`test_exit_disposition` records that the deciding runtime does not exist. The stop rule
applies, ORION-23 stays bounded, and **no external deployment claim is made**.

## Authority

`MEASUREMENT_AND_PROOF_ONLY`. `scientific_authority_delta: NONE`. No submission authority.
Nothing frozen is retracted. Outcomes were read once.

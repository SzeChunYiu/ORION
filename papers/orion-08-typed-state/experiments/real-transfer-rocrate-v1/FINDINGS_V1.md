# ORION-08 third family — RO-Crate workflow applicability

**Terminal: `CANNOT_CHECK_NO_CONTRAST`.** This corpus cannot test the theorem's
"exactly when" clause, because it contains no case where refinement should not
help. That is a property of the corpus, and the protocol declared this terminal in
advance so it could not later be dressed up as either a pass or a failure.

## The measurement, which stands regardless

1,533 WorkflowHub records, **0 fetch errors**, retrieved read-only from the public
JSON API. Gold is the registry's own `internals` field — non-empty exactly when it
parsed the workflow's RO-Crate into inputs, outputs and steps. Overall usable rate
**0.5806**.

| quantity | value |
|---|---|
| coarse fibres (`license`) | 22 |
| refined fibres (`license`, `workflow_class`) | 76 |
| singleton fraction | 0.342 — degeneracy gate **passes** |
| prediction from the training half | **value** |
| observed | **value** — agrees |
| regret, coarse → refined | **0.1031 → 0.0065** |
| `attempt_all` | 0.1097 |
| out-of-sample, coarse → refined | 0.1076 → 0.0137 |

Refinement removes **94%** of the coarse binding's regret and beats the
attempt-everything default. Knowing a workflow's *type* on top of its *licence*
is worth a great deal for deciding whether its crate is worth opening.

Stratified by tag band, all four strata predict value and observe value — 4 of 4
agreeing, none disagreeing.

## Why the terminal is `CANNOT_CHECK` and not a pass

The protocol requires **one stratum predicted value and one predicted no value**.
That requirement is not decoration: without a stratum where the theorem says
refinement should *not* help, a study confirms only the easy half of a
biconditional. Every stratum here predicts value, so the hard half goes untested.

Reporting 4-of-4 agreement as a third confirmation would be claiming exactly what
this design cannot support.

## Two design errors, both mine, both recorded

**The first stratifier was the feature the refinement adds.** `PROTOCOL_V1`
stratified by `workflow_class` while refining `license → (license,
workflow_class)`. Within a stratum where `workflow_class` is constant the refined
binding induces the same partition as the coarse one, so the refinement was the
identity and every stratum returned no value with `regret_coarse ==
regret_refined` to the digit. That is an a priori fact needing no data, and I found
it from the outcome. `AMENDMENT_V1_STRATIFIER.md` records it.

**The replacement stratifier does not rescue the design.** Tag bands are used by
neither binding, so the refinement is real inside each stratum — and every stratum
still predicts value. The corpus simply has no negative case.

**I stopped there.** Trying further stratifiers until one produces a no-value
stratum is searching for a contrast rather than finding one, and the difference
between those is the whole reason the requirement was frozen in advance.

## What this family does and does not contribute

It does **not** give ORION-08 a third confirmation of the refinement theorem. The
two legs that do — CC18 and Defects4J — each contained a genuine no-value case
(diabetes; Csv), and this one does not.

It does give a real external corpus, with objective registry-produced gold, in
which the typed binding is worth 94% of the coarse binding's regret and beats
attempting everything. That is a usable result about artifact triage. It is not a
result about the theorem.

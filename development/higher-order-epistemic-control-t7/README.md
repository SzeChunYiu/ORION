# Higher-order epistemic control T7 — development packet

Status: **IMPLEMENTATION HYPOTHESIS FROZEN / NO SCIENTIFIC RESULT**

Base subject: `0694b517bf637c70ef4aec75b6968692ba728aa6`

Inputs already merged:
- T1 minimal revision mechanics;
- T2 revision responsibility;
- T3 interface adequacy + non-authorizing revision gate;
- T4 epistemic computation allocation;
- T5 uncertainty containment;
- T6 social evidence dependence / hidden-contribution state.

Owners: #455/#458/#462/#463. Verification/novelty remain #283/#287.

## Development question

Can the existing non-authorizing reports be composed into one **Self-ORION epistemic control decision** that identifies the next formally permissible class of step without granting scientific, adoption, merge, or global-stop authority?

The controller does not execute tools or modify scientific state. It consumes already-bound reports and returns one bounded recommendation:
- required computation;
- optional/recommended computation;
- ambiguous computation;
- social evidence required;
- containment / scope block;
- revision candidate;
- ambiguous revision;
- unresolved/no-admissible/local-computation-stop.

## Frozen precedence

### 1. Hard computation obligations
If T4 carries active hard obligations:
- `SELECTED` -> `COMPUTATION_REQUIRED`;
- `MULTIPLE_OPTIMA` -> `COMPUTATION_AMBIGUOUS`;
- `UNRESOLVED` -> `UNRESOLVED`;
- `NO_ADMISSIBLE` -> `NO_ADMISSIBLE_ACTION`.

This stage preempts a revision candidate because protected/required computation is non-compensatory.

### 2. Required social-evidence condition
When the caller explicitly requires bounded independent social evidence:
- no report -> `SOCIAL_EVIDENCE_REQUIRED`;
- `UNRELIABLE`, `CORRELATED`, or `UNRESOLVED` -> `SOCIAL_EVIDENCE_REQUIRED`;
- every supplied report `INDEPENDENT` -> continue.

Different agent IDs never satisfy this requirement by themselves. If a computation is required to acquire/verify social evidence, it must have been represented as a hard T4 obligation and would already have taken precedence in stage 1.

### 3. Containment / validity envelope
If a current-context containment report is supplied:
- `BLOCKED` -> `CONTAINED` (no material revision/action inside that context);
- `UNRESOLVED` -> `UNRESOLVED`;
- `IN_SCOPE` -> continue.

Containment does not establish model correctness. A computation needed to update the envelope must be represented as a hard T4 obligation to preempt here.

### 4. Revision gate
- `CANDIDATE_SELECTED` -> `REVISION_CANDIDATE`;
- `MULTIPLE_MINIMA` -> `REVISION_AMBIGUOUS`.

A selectable revision beats **optional** positive-value computation: optional compute cannot indefinitely delay an already admissible bounded revision merely because it has positive scalar value.

### 5. Optional computation when revision is not selectable
If the revision gate is unresolved/interface-repair-required/no-admissible:
- T4 `SELECTED` with no active hard obligations -> `COMPUTATION_RECOMMENDED`;
- T4 `MULTIPLE_OPTIMA` -> `COMPUTATION_AMBIGUOUS`;
- T4 `UNRESOLVED` -> `UNRESOLVED`.

### 6. Residual terminals
- revision `NO_ADMISSIBLE` + no useful compute -> `NO_ADMISSIBLE_ACTION`;
- revision `INTERFACE_REPAIR_REQUIRED` + no useful compute -> `NO_ADMISSIBLE_ACTION`;
- revision `UNRESOLVED` + T4 `LOCAL_COMPUTATION_STOP` -> `LOCAL_COMPUTATION_STOP` **with `grants_global_task_stop_authority=False`**;
- otherwise unresolved.

## Claim/identity rules

All supplied reports must be claim-relative to the same `claim_id`. Containment and social reports are optional only when the caller does not require those conditions. Digests of every input report are carried into the control receipt.

## Authority boundary

The controller hard-codes:
- `grants_scientific_authority = False`;
- `grants_revision_authority = False`;
- `grants_adoption_authority = False`;
- `grants_promotion_authority = False`;
- `grants_merge_authority = False`;
- `grants_global_task_stop_authority = False`.

A `REVISION_CANDIDATE` is still only a candidate for isolated execution/replay/fresh/protected evaluation. A local computation stop does not close a search route, scientific task, paper, or research programme.

## Competing implementation hypotheses

### H1 — deterministic precedence composition (selected)
Small read-only adapter over existing reports. Every precedence rule is inspectable and countermodel-tested.

### H2 — one learned policy over all reports
Rejected before a benchmark/protected evaluator exists; would conflate capability with authority and make failure localization difficult.

### H3 — scalarize revision, compute, social and containment into one utility
Rejected: hard obligations/authority and containment are non-compensatory by design.

### H4 — execute actions directly from the controller
Rejected. Execution/adoption remain downstream Self-ORION/host processes.

## RED hostile tests required before GREEN implementation

1. hard protected computation preempts a selectable revision;
2. selectable revision beats optional positive-value compute;
3. unresolved revision + positive optional diagnostic -> computation recommended;
4. invalid containment blocks revision candidate;
5. unresolved containment fails closed;
6. correlated required social evidence blocks revision candidate;
7. bounded independent required social evidence allows revision candidate;
8. multiple revision minima stay ambiguous;
9. local computation stop under unresolved revision does not grant global stop;
10. no-admissible revision + no admissible compute -> no admissible action;
11. cross-claim report mixture rejected;
12. no output may grant scientific/revision/adoption/promotion/merge/global-stop authority.

## Paper boundary

Do not edit P5/P1/P2/P3/P4/P7/P8 current submission manuscripts in this tranche. T1–T6 implementation-only claims are already recorded in P5. Add only a P6 successor T7 manuscript bridge and programme handoff. Result-bearing paper updates remain gated on #455 prospective evidence.

## Reopen triggers

- precedence countermodel shows optional compute must sometimes preempt an admissible revision;
- social/containment conditions require explicit computation binding rather than caller hard obligations;
- sequential/risk-sensitive metareasoning materially changes the controller;
- T7 creates an authority cycle or global-stop laundering path;
- #455 prospective results show the composed controller is overconservative or adds no value;
- stronger nearest work subsumes the cross-coordinate composition.

## Claim ceiling

A green T7 establishes only deterministic composition/non-authority behavior on frozen finite countermodels. It does not establish autonomous-science competence, Self-ORION improvement, optimal scheduling, novelty, or paper readiness.

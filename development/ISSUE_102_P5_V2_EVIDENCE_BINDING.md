# Development packet — issue #102 P5 V2 evidence/run binding

## Development question

How can the P5 staged-acceptance study bind its exact execution subject and consume protected result records without allowing missing arms, stale splits, post-hoc PACE choices, custody collapse, result rebinding, or dropped negative/harmful candidates to masquerade as a publishable run?

## Atomic fibres

1. bind the exact V2 protocol digest without rewriting V1/V2 scientific design;
2. bind final subject, hidden-cause suite and motivating/replay/fresh/protected split identities;
3. bind five stochastic seeds and all required V2 subject/baseline/ablation arms;
4. bind evaluator artifact/epoch plus distinct candidate/evaluator/host lineages;
5. bind the anytime-valid acceptance rule, configuration and error budget before outcome access;
6. bind matched resource ceilings across all executable arms;
7. reject any `UNBOUND` execution field;
8. bind each stage result to the exact manifest/subject/evaluator/epoch;
9. preserve candidate decisions independently from evaluator stage evidence so false acceptance can be measured rather than laundered;
10. require finalized arm×episode×seed coverage and FRESH+PROTECTED audit for every accepted candidate;
11. re-derive the V2 staged verdict from retained stage evidence and reject a mismatched V2 decision;
12. expose only `CANNOT_CHECK` empirical authority from validation itself.

## Incumbent mechanics

The shared programme run manifest already provides canonical content addressing and a generic no-`UNBOUND` rule. P5 V2 additionally freezes four stage-specific splits, PACE/e-process acceptance, staged non-compensation, matched V1/V2/acceptance comparators and protected-custody semantics. The new validator therefore extends the execution contract rather than replacing the shared publication philosophy.

## Saturation challenge

A manifest can be syntactically complete yet still be scientifically incomplete: it may omit one ablation, reuse a candidate evaluator lineage, leave a protected split unbound, use ordinary optional stopping, or label a baseline non-executable after seeing results. A result archive can likewise bind the right protocol ID while pointing at the wrong subject/evaluator, omit one seed, or retain an `ACCEPT` decision without protected audit. Each shortcut receives a hostile test.

## Miss hypotheses

- a baseline/config omission can look like an innocent sparse mapping;
- `CANNOT_CHECK` could disappear if only successful decisions are archived;
- an accepted candidate could avoid FRESH/PROTECTED audit by stopping early;
- a V2 decision could disagree with its own non-compensatory stage evidence;
- external baseline false acceptance could be rejected as malformed instead of measured;
- finalization could silently drop one arm/episode/seed cell;
- a validator could accidentally become an empirical authority source.

## Frozen implementation hypothesis

A stdlib-only `orion.study.p5.v2_evidence` validator can fail closed on incomplete execution bindings and immutable-result archives while reusing the merged `MultiStageCandidateGate` for V2 decision consistency. Validation and synthetic tests may establish artifact integrity only; they must always report empirical authority as `CANNOT_CHECK` until real protected evidence exists.

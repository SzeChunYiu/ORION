# P7 resolution-lifecycle amendment V1

Date: 2026-08-22
Status: formal clarification / no novelty or authority claim
Applies to: `FORMAL_CORE_V1.md`

## Motivation

P7's formal core correctly distinguishes `route_stop`, `task_stop`, `defer`, `cannot_check`, and `reframe`. This amendment clarifies that `cannot_check` is normally an **active epistemic obligation**, not a passive terminal label.

The clarification is compatible with the stopping-impossibility theorem: the navigator must not fabricate task completion under extension ambiguity, but it should still identify the admissible actions that could reduce the ambiguity.

## Resolution obligation

When a navigation state yields `cannot_check`, define a resolution obligation

\[
U=(u,c,s,R,E,A,B,\tau),
\]

where:

- `u` is a stable obligation identity;
- `c` is the unresolved class (coverage, identifiability, resource, authority, protected/external, capability, responsibility, representation, or other typed class);
- `s` is the subject/judgment identity;
- `R` is the set of reason codes;
- `E` is the evidence/capability/authority object set still required;
- `A` is the admissible next-action set;
- `B` is the blocker/attempt history;
- `\tau` is an explicit bounded/external stop condition when one applies.

The corresponding framework object is `ResearchResolutionObligation.v1`.

## Resolution-first invariant

If `cannot_check` holds and there exists an admissible action that can change the truth-relevant epistemic state without violating authority/resource contracts, the navigator should return that action together with the unresolved judgment.

Examples include:

- execute an untried structurally independent route;
- orient the chart sufficiently to register a valid route contract;
- reframe when the current chart cannot express the discriminating variable;
- acquire or independently verify missing evidence;
- diagnose causal responsibility before selecting a repair;
- request a protocol-authorized resource or protected-evidence widening.

Thus:

\[
\mathsf{cannot\_check} \land \exists a\in A_{admissible}
\Rightarrow
\mathsf{open\_resolution\_obligation}(U,a).
\]

This is a research-control rule, not a completeness theorem.

## Legitimate unresolved boundaries

An obligation may remain open when no admissible local action can decide it under the current contract. Important cases include:

1. extension ambiguity / formal non-identifiability;
2. protected or external evidence not yet released;
3. frozen resource bound without authorized widening;
4. authority/coercion object the navigator cannot mint;
5. unavailable host capability.

These are **typed unresolved boundaries**, not task-stop certificates.

## Negative results are different

A verified negative result must not be represented as `cannot_check` merely because it blocks a desired path. Examples:

- a theorem/countermodel proves a route or representation cannot identify the target;
- a donor method subsumes the proposed novelty claim;
- a frozen transfer test fails;
- an exact obstruction excludes the current method closure.

Those are negative research results with evidence and assimilation consequences. They may close a route/hypothesis, register an obstruction, force a reframe, or revise a paper/framework claim.

The corresponding framework object is `ResearchNegativeResult.v1`.

## Strengthened fail-closed invariant

P7 therefore distinguishes:

- `task_stop`: mandatory obligations closed by valid satisfaction/discharge/certificate;
- `negative`: a target hypothesis/route/claim is refuted or bounded negatively under a valid evidence contract;
- `cannot_check`: the target judgment remains unresolved and carries a resolution obligation;
- `route_stop`: local route action has stopped but global obligation may remain open.

No one of these may be silently coerced into another.

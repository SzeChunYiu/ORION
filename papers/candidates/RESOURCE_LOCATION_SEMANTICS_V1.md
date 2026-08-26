# Shared ORION-21–ORION-23 resource/state semantics V1

**Programme:** #977  
**Role:** shared definitions only; no paper may use this file to borrow another paper's result.

## Resource vector

For every end-to-end comparison use

\[
R=(c_{prep},m_{state},c_{model},c_{infer},n_{tool},\ell,c_{cache},c_{recover}),
\]

where the coordinates are respectively preprocessing/compiler work, state memory, model capacity/compute, inference/search work, tool/verifier calls, latency, cache/reuse work and recovery/reconstruction work.

No coordinate is free merely because it occurs before the downstream model. A scalar cost may be formed only from prospectively supplied nonnegative weights; otherwise results are reported as constrained slices or Pareto relations.

## Quality and verified utility

A system produces domain-specific quality `Q` and, where available, an externally verified correctness/utility value `V`. Resource dominance is never allowed to replace correctness: if a system violates a hard verifier/safety contract, it is not Pareto-superior merely because it is cheap.

## ORION-21 ownership — placement

ORION-21 asks **where computation has been placed** between state construction, downstream access/reasoning and later recovery. It owns placement/optionality laws, not adaptive allocation.

## ORION-22 ownership — allocation

ORION-22 asks **where the next unit of resource should be spent** under a frozen end-to-end envelope. It owns allocation/substitution/complementarity/regret results, not the representational support semantics themselves.

## ORION-23 ownership — responsibility

ORION-23 asks **what responsibilities a constructed state supports and when reuse must be revoked/reopened**. It owns responsibility-scoped support/certification, not general transition/authority semantics.

## Cross-paper anti-double-counting

The same preprocessing event cannot be charged once as ORION-21 compiler work and again as ORION-22 reasoning work. Every experimental adapter must emit one resource record with stable event identities, and paper-specific analyses select coordinates from that record.

A result may be a frozen upstream input to another paper, but the downstream paper must add a new protected discriminator. Shared tasks are allowed; protected test cells used for headline claims must be paper-disjoint unless the later paper prospectively declares the earlier result as fixed input rather than evaluation data.

## Pareto relation

For quality target `q`, system A resource-dominates B if A reaches at least `q`, is no worse in every charged resource coordinate and is strictly better in at least one. When qualities differ, report a quality-resource frontier rather than choosing post-hoc weights.

## Hard accounting attacks

Every ORION-21–ORION-23 external adapter must fail closed on:

- uncharged preprocessing or model warmup;
- hidden cache reuse available to only one arm;
- verifier/tool calls excluded from cost;
- different semantic information between arms;
- post-outcome allocation/compilation choices;
- recovery cost omitted after state invalidation;
- scalar weights chosen after results.

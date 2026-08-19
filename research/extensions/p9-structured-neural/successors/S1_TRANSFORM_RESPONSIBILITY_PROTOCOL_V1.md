# P9 S1 — Transform Responsibility Protocol V1

Date: 2026-08-19
Parent: #587
Freeze issue: #591
Subject base: `350a8e83316a7d657714effa408689f602318c2a`
Outcome accessed: **false**

## Question

Given local affine transformations that may be point-identifiable, underdetermined,
stale after a mechanism change, or impossible to identify with the available
probes, can a system diagnose the missing responsibility **before** global
composition?

This tranche freezes a model-independent benchmark/evaluator only. It contains
no learned model, no protected accuracy, and no paper-level positive claim.

## Prior-work contraction

S1 does not claim novelty for modular/compositional system identification,
learning subsystem dynamics and composing them, active system identification,
uncertainty-aware operator learning, change-point detection, causal modular world
models, or the design principle “keep known computation exact and learn only the
unknown part.” Those are donor mechanisms.

The V1 residual is narrower: expose and mechanically distinguish the
responsibility state of a local transform so unresolved/stale operands cannot be
laundered into a resolved global answer.

## Frozen map family

One-dimensional affine maps only:

`y = a*x + b`

All V1 observations are exact/noiseless. Bounded-noise feasible sets are deferred
to V1.1 so this freeze has exact identifiability semantics.

## Candidate-visible edge payload

The model/controller may see only:

- opaque transform id;
- opaque source/target chart ids;
- exact observation pairs `(x, y)`;
- an optional previously admitted affine estimate `(a, b)`;
- declared candidate probe inputs and their costs.

The payload excludes:

- evaluator true map parameters;
- responsibility gold;
- any hidden change flag;
- global evaluator terminal;
- generator/family/seed labels;
- the minimal-probe answer.

## Exact local responsibility states

`IDENTIFIABLE_NOW`
: The current map may be used now. This holds if either (a) two distinct exact
  observed x-values uniquely identify one affine map, or (b) a previously
  admitted estimate is supplied and every current observation is compatible with
  it.

`CHANGED_SINCE_ESTIMATE`
: A previously admitted estimate exists and at least one current exact
  observation is incompatible with it. This state is derived from visible
  incompatibility, never from a hidden change flag.

`NEEDS_MORE_MEASUREMENTS`
: The map is not currently identifiable, but the declared probe set contains a
  finite subset whose distinct x-values, combined with current observations,
  would provide at least two distinct x-values.

`NONIDENTIFIABLE_UNDER_AVAILABLE_PROBES`
: The map is not currently identifiable and even exhausting the declared probe
  inputs cannot produce two distinct x-values.

## Minimal probe policy

Among probe subsets that make an unresolved map point-identifiable, the evaluator
selects minimum total cost; ties are broken by lexicographically sorted probe ids.
This is an evaluator target only and is excluded from candidate payloads.

## Global cycle rule

A global affine cycle may emit `GLUE` or `OBSTRUCTION` only if every material
local edge is `IDENTIFIABLE_NOW`. Any `CHANGED`, `NEEDS_MORE_MEASUREMENTS`, or
`NONIDENTIFIABLE` edge forces global `UNKNOWN`.

When every edge is admitted, local affine estimates are converted to the existing
`AffineTransport` representation and the existing exact
`classify_cycle_gluing` implementation is used. S1 does not introduce a second
gluing algebra.

## Frozen hostile cases

1. two distinct observations -> exact affine estimate;
2. one/repeated x only + a distinct available probe -> `NEEDS_MORE_MEASUREMENTS`;
3. one/repeated x only + no distinct possible probe -> `NONIDENTIFIABLE`;
4. admitted historical estimate + compatible probe -> remains usable;
5. admitted historical estimate + incompatible probe -> `CHANGED_SINCE_ESTIMATE`;
6. observation order permutation leaves all decisions unchanged;
7. opaque identity reminting leaves all decisions unchanged;
8. true parameter / gold mutation leaves candidate fingerprint unchanged;
9. two evaluator worlds share exactly the same unresolved candidate payload but
   have different hidden maps and opposite fully-known global terminals; the
   candidate-visible global terminal must be `UNKNOWN` in both;
10. complete identified GLUE and OBSTRUCTION cycles agree with the existing P9
    exact gluing evaluator.

## No-authority / no-outcome rule

Nothing in S1 grants scientific, novelty, adoption, or execution authority. This
benchmark only diagnoses transform-information/computation responsibility.

No learned baseline may be executed in this tranche. The only successful terminal
is `S1_V1_BENCHMARK_FROZEN` after RED->GREEN hostile tests and exact-head CI.

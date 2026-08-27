# P13A Independent Responsibility-Sufficiency and RCS Efficacy Protocol V1

**Paper:** ORION-23 — Responsibility-Carrying State  
**Issues:** #666 and #668  
**Protocol:** `ORION.P13A.ResponsibilitySafeReuse.v1`  
**Frozen:** 2026-08-21 after diagnosing, but without modifying, the historical P14A negative.

## Historical separation

The historical terminal `P14_CONTROLLED_SUFFICIENCY_DEBT_GATE_NOT_MET` remains negative at `0.0556640625 > 0.05`. This successor has a new seed, new estimands and a new terminal. Passing P13A cannot relabel P14A.

P14A's finite-sample sentinel estimated a within-sample group-majority decoder and scored that decoder on the same finite sample, then took the maximum deviation over 100 replicates. That statistic is not the estimand used here. P13A uses exact support semantics and an independently generated prospective safety–cost benchmark.

## Exact responsibility model

Raw world `(x,m,r)` has independent binary coordinates. Responsibilities are:

- `PREDICT(x,m,r)=x`
- `DECIDE(x,m,r)=x`
- `INTERVENE(x,m,r)=x*m`
- `VERIFY(x,m,r)=x*m`
- `REPAIR(x,m,r)=r`

Representations:
- `Z1=(x,)` supports exactly `PREDICT, DECIDE`.
- `Z2=(x,m)` additionally supports `INTERVENE, VERIFY`.
- `Z3=(x,m,r)` supports all five.

Exact support is determined by equivalence classes, not by observed finite-sample accuracy.

## Prospective benchmark

- Protected seed `2026082113`.
- 24 held-out families, 512 episodes each.
- Per-family `P(m=1)` and `P(r=1)` are independently uniform on `[0.65,0.95]`.
- Episode compact state is `Z1` or `Z2` with equal probability.
- Requested responsibility is uniform across five responsibilities.
- Raw recovery is independently available with probability `0.95`.

A compact decoder uses the exact coordinate when supported and the family MAP value for a missing coordinate when unsupported. This deliberately creates high-confidence-but-structurally-insufficient cases.

## Arms

1. `UNQUALIFIED`: always reuse compact state.
2. `CONFIDENCE_ONLY`: estimate requested-task accuracy from family distribution; reuse if confidence >= `0.80`, otherwise reopen if raw is available, else `CANNOT_CHECK`.
3. `PROVENANCE_ONLY`: valid source lineage is present, so provenance alone reuses compact state regardless of responsibility.
4. `RCS`: reuse only if the requested responsibility is in the exact certified support set; otherwise `REOPEN_REQUIRED` if raw is available, else `CANNOT_CHECK`.
5. `ALWAYS_RAW`: reopen every episode when raw is available, else `CANNOT_CHECK`.

No arm can treat `CANNOT_CHECK` as a correct task answer.

## Metrics

- **unsafe reuse:** `REUSE` when exact support is false;
- final verified correctness;
- unnecessary reopen: `REOPEN` when exact support is true;
- mean resource cost with fixed units `REUSE=1`, `REOPEN=6`, `CANNOT_CHECK=0.5`;
- correct `CANNOT_CHECK` when unsupported and raw unavailable.

## Positive terminal

`P13A_RCS_SAFETY_COST_SUPERIORITY_SUPPORTED` requires:

1. exact responsibility matrix matches the registered Z1/Z2/Z3 support sets;
2. RCS unsafe reuse is exactly zero;
3. confidence-only unsafe reuse is at least `0.10`;
4. provenance-only unsafe reuse is at least `0.25`;
5. RCS final correctness is not lower than confidence-only by more than `0.01`;
6. RCS mean cost is at least 30% below `ALWAYS_RAW`;
7. RCS unnecessary reopen is exactly zero;
8. RCS emits `CANNOT_CHECK` for every unsupported/nonrecoverable case;
9. two fresh executions are byte-identical.

## Authorized claim

A positive result supports a controlled systems claim:

> When compact-state sufficiency is responsibility-relative, an explicit responsibility/recovery contract can eliminate structurally unsafe reuse while preserving verified performance and using materially less resource than always reopening raw state; scalar confidence and provenance alone do not identify the same boundary in the registered held-out worlds.

It does not establish real-agent or safety-critical deployment superiority.

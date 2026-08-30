# Claim disposition — ORION09.SIZE_TRANSFER_INVARIANT.v1

Protocol and theory frozen before verification ran.
Terminal: **T3_INVARIANT_ADDS_NOTHING**.
Status: **PROMOTION_STOPPED__RETURN_TO_SPECIALIST_VENUE**.

## Result

1,413,120 configurations enumerated.

| | |
|---|---|
| S1 violations (purity criterion) | **0** |
| S2 violations (capacity bound) | **0** |
| times the capacity invariant **fired** | **0** |
| failures it explains | **0** |
| failures it **cannot see** | **759,128** |

All four controls pass.

## The theorems are true and the invariant is useless

S1 holds: a separator reading only `phi` exists **iff** every fibre is pure. That is the
`eps = 0` case of the ORION-02 fibre floor, and it means the frozen `n = 4` negative is
**structural** — a mixed fibre, not a failed predicate search.

S2 also holds, with zero false alarms. But it holds **vacuously**: it never fired once in
1.4 million configurations.

The reason is elementary and I should have seen it before running anything. The capacity
bound compares *required distinct outcomes* against `2^k` cells. For binary separation the
required outcomes are at most **2**, and `2^k >= 4` for every `k` tested. **Two is never
greater than four.** The pigeonhole condition is unreachable in this setting by
construction, so counting can never predict a failure here. All 759,128 separation failures
occur *below* capacity, where only fibre inspection sees them.

## Why this stops the promotion

#1649's stop rule for this lane:

> If no invariant predicts [the] transition better [than] existing bounded geometry, stop
> PRX-Quantum promotion [and] submit [the] strongest defensible specialist venue.

The invariant's whole promise was *search-free* prediction — telling you transfer fails
without inspecting predicates. It delivers none: it fires zero times and explains zero
failures. Fibre purity remains the exact criterion, but computing it requires exactly the
inspection the invariant was meant to avoid, so nothing is gained over the existing bounded
geometry.

Promotion stops. ORION-09 returns to the strongest defensible specialist venue. **No second
rescue cycle**, per the same rule.

## This outcome was registered in advance

`PROTOCOL.json`'s falsifiability self-check names T3 a live possibility and says why:
*"pigeonhole bounds are often vacuous on the configurations that actually arise. The
protocol is written so that 'the theorems are true but the invariant is useless' is a
reportable outcome rather than a silent pass."*

Without that terminal, S1 and S2 both passing with zero violations would have read as a
success. The distinction between *true* and *useful* had to be built into the terminal set
before the numbers arrived, because afterwards it is indistinguishable from moving the
goalposts.

## Scope reduction, recorded

The frozen enumeration named sizes 4–8 at `k` in {2,3}. At `k = 3, n = 8` that is roughly
`4 x 10^9` feature maps and does not terminate. Sizes were reduced to `{2: [4,5,6], 3:
[4,5]}` **before any outcome was read** — the first run produced no output at all — and the
reduction is recorded in `RESULT_V1.json` rather than left implicit. The reduction cannot
have manufactured T3: the capacity condition is unreachable at *every* size for binary
labels, not merely the ones dropped.

## What is not retracted

Nothing. The `k* = 4` law on `n <= 3`, the negative `n = 4` transfer, and the falsified
sign-aware attribution all stand exactly as frozen. This packet explains the negative's
*structure* and reports that the proposed invariant does not rescue it.

`MEASUREMENT_AND_PROOF_ONLY`. `scientific_authority_delta: NONE`. No submission authority.
Outcomes were read once.

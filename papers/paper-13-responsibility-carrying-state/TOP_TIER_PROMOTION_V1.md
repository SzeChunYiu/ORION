# P13 top-tier promotion V1 — Responsibility-Scoped Sufficiency and Certified Reuse

**Programme:** #977  
**Existing controlled authority:** `READY_FOR_EXTERNAL_REVIEW_AS_CONTROLLED_RESPONSIBILITY-SAFE-REUSE_RESULT` remains valid.  
**Top-tier state:** `EXTERNAL_PROMOTION_PENDING`

## Maximum claim to earn

> **State sufficiency is responsibility-relative.** A state that is adequate for prediction or immediate action may be unsafe for intervention, verification, diagnosis or repair. A responsibility-carrying state contract can identify supported responsibilities, omissions, reopen conditions and recoverability so that systems reuse state more safely and cheaply than confidence-only, provenance-only, unqualified compression or always-raw baselines.

Predictive/control abstractions, causal/interventional sufficiency, confidence gating, provenance, proof-carrying actions, stale-memory detection and certified abstractions are donor-owned.

## Responsibility ladder

Freeze at least:

1. predict/classify;
2. select/plan an action;
3. intervene/control/counterfactually reason;
4. verify a claim/result;
5. diagnose failure;
6. repair/recover after failure.

A paper may add domain-specific responsibilities only if their ordering/non-ordering is defined prospectively.

## Formal programme

### T13.1 — Responsibility-indexed support

For representation/state `S` and responsibility `r`, define support/sufficiency through an external equivalence or witness relation rather than performance of one weak learner. Characterize when `S` is sufficient for `r1` but not `r2`.

### T13.2 — Transport and revocation

Define how a responsibility certificate transports under:

- representation/compiler version change;
- source/evidence update;
- context/epoch change;
- responsibility upgrade;
- loss of raw-recovery availability.

Compose with P6/P7/P8 only through frozen interfaces; P13 owns the state-reuse contract, not their general transition/transport/authority claims.

### T13.3 — Approximate support

Extend beyond exact finite support to a calibrated approximate-support regime with prospectively fixed tolerance/risk semantics. The state must not self-certify its own support probability.

## Protected real-system programme

### E13.1 — verifier-backed responsibility shift

Use a formal/problem-solving workflow with a staged responsibility change, e.g. prediction/action -> verification -> diagnosis/repair. Compare:

- compact/unqualified state;
- confidence-gated state;
- provenance-only state;
- responsibility-carrying state;
- always-raw/reopen safety ceiling.

The same initial state information must feed all arms.

### E13.2 — research/agent responsibility shift

Freeze a workflow such as evidence summarization -> answer/action -> claim authorization -> revision after counterevidence. The protected event changes the responsibility after the compact state has already been constructed.

### E13.3 — semantic-change transport

Change representation, evidence source, evaluator or context after certification and measure correct preserve/revoke/reopen decisions.

## Primary endpoints

- unsafe reuse rate;
- higher-responsibility failure conditional on lower-rung success;
- unnecessary reopen rate;
- raw recovery success/cost;
- correct `CANNOT_CHECK`;
- certificate transport/revocation accuracy;
- task utility/verified correctness;
- resource saved relative to always-raw;
- approximate-support calibration.

Safety gain cannot be purchased by abstaining/reopening everything.

## Strongest hostile attacks

- higher responsibility receives extra information in only one arm;
- lower/higher-rung models have different training data;
- certificate is merely confidence with new vocabulary;
- always-abstain/always-reopen wins the safety metric;
- compiler/evaluator/state container self-certifies;
- raw recovery is promised but stale/unavailable;
- semantic change silently leaves old certificate active;
- always-raw cost is undercounted;
- approximate support is calibrated post hoc.

## Top-tier promotion gate

`P13_TOP_TIER_SUBMISSION_READY` requires:

- [ ] T13.1 responsibility-indexed support closure;
- [ ] T13.2 transport/revocation closure;
- [ ] T13.3 approximate-support calibration protocol;
- [ ] verifier-backed responsibility shift;
- [ ] second qualitatively different responsibility-shift domain for broad headline;
- [ ] real semantic-change certificate transport/revocation benchmark;
- [ ] reduced unsafe reuse without always-reopen degeneration;
- [ ] meaningful resource saving versus always-raw safety ceiling;
- [ ] independent evaluator/authority;
- [ ] preserved historical negative and replay corrections;
- [ ] current donor saturation and exact package replay.

If responsibility support is not ordered in a domain, preserve the partial-order/non-comparability result rather than forcing a universal ladder.

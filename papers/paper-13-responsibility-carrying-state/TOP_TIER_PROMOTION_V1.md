# P13 top-tier promotion V1 — Responsibility-Scoped Sufficiency and Certified Reuse

**Programme:** #977  
**Existing controlled authority:** `READY_FOR_EXTERNAL_REVIEW_AS_CONTROLLED_RESPONSIBILITY-SAFE-REUSE_RESULT` remains valid.  
**Top-tier state:** `EXTERNAL_PROMOTION_PENDING`

## Maximum claim to earn

> **State sufficiency is responsibility-relative.** A state that is adequate for prediction or immediate action may be unsafe for intervention, verification, diagnosis or repair. A responsibility-carrying state contract can identify supported responsibilities, omissions, reopen conditions and recoverability so that systems reuse state more safely and cheaply than confidence-only, provenance-only, unqualified compression or always-raw baselines.

Predictive/control abstractions, causal/interventional sufficiency, confidence gating, provenance, proof-carrying actions, stale-memory detection and certified abstractions are donor-owned.

## Post-outcome status — 2026-08-23

The independent bounded theory checker now closes the current responsibility-indexed support construction, transport/revocation conditions, and approximate-support/calibration model under the frozen finite assumptions. These are bounded formal results, not a claim that every real responsibility family forms one total ladder.

The prospectively frozen real-data responsibility-shift study now returns `P13_REAL_RESPONSIBILITY_SHIFT_V1_SUPPORTED` with byte-identical replay over 17,970 episodes. A compact state is learned for parity responsibility and is then confronted with the stronger exact-digit responsibility.

Fold by fold, responsibility-carrying state (RCS) exactly matches always-raw accuracy on both responsibilities while reading only 33 floats per episode instead of 64. Aggregate state-read reduction is `0.484375` (48.4375%). RCS reopens on half the episodes and never reuses unsupported compact state for exact-digit responsibility.

Protected comparator outcomes:

- RCS: combined accuracy `0.9435169727`, exact-digit accuracy `0.9699499165`, parity accuracy `0.9170840289`, unsupported exact-digit reuse `0`;
- ALWAYS_RAW: identical task accuracy, 64 floats read/episode, reopen rate `1.0`;
- CONFIDENCE_ONLY: exact-digit accuracy `0.3956594324`, unsupported exact-digit reuse rate `0.7774067891`;
- PROVENANCE_ONLY / UNQUALIFIED: exact-digit accuracy `0.2376182526`, unsupported exact-digit reuse rate `1.0`.

The raw-vs-compact exact-digit accuracy gap is `0.7323316639`. Thus the compact state can be current, provenanced and highly confident for the old responsibility while being structurally inadequate for the upgraded responsibility.

**Earned claim:** in this protected real-data responsibility shift, responsibility support rather than confidence/provenance alone determines safe reuse; RCS matches the always-raw safety ceiling while avoiding nearly half of raw-state reads. This does not yet establish verifier-backed higher responsibilities, semantic-change certificate transport on a live system, or broad cross-domain authority.

Exact execution hashes and artifact identities are bound in `papers/candidates/TOP_TIER_EXECUTION_LEDGER_2026-08-23.md`.

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

- [x] T13.1 bounded responsibility-indexed support closure;
- [x] T13.2 bounded transport/revocation closure;
- [x] T13.3 bounded approximate-support calibration protocol/model;
- [ ] verifier-backed responsibility shift at the intended formal/problem-solving scope;
- [ ] second qualitatively different responsibility-shift domain for broad headline;
- [ ] real semantic-change certificate transport/revocation benchmark;
- [x] reduced unsafe reuse without always-reopen degeneration in the protected real-data shift;
- [x] meaningful resource saving versus always-raw safety ceiling (`48.4375%` fewer raw-state floats read);
- [ ] independent evaluator/authority at the intended scientific responsibility scope;
- [x] current protected negative/comparator outcomes and deterministic replay corrections retained;
- [ ] current donor saturation and exact package replay.

The unchecked items are genuine remaining promotion requirements. The current real-data result establishes responsibility-relative reuse under a clean controlled shift but does not substitute for verifier-backed scientific responsibility or cross-domain semantic transport.

If responsibility support is not ordered in a later domain, preserve the partial-order/non-comparability result rather than forcing a universal ladder.

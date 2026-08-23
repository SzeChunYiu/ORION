# P13 top-tier promotion V1 — Responsibility-Scoped Sufficiency and Certified Reuse

**Programme:** #977  
**Existing controlled authority:** `READY_FOR_EXTERNAL_REVIEW_AS_CONTROLLED_RESPONSIBILITY-SAFE-REUSE_RESULT` remains valid.  
**Top-tier state:** `TWO_DOMAIN_RESPONSIBILITY_SHIFT_EARNED__EXTERNAL_SCIENTIFIC_AUTHORITY_PENDING`

## Maximum claim to earn

> **State sufficiency is responsibility-relative.** A state that is adequate for prediction or immediate action may be unsafe for intervention, verification, diagnosis or repair. A responsibility-carrying state contract can identify supported responsibilities, omissions, reopen conditions and recoverability so that systems reuse state more safely and cheaply than confidence-only, provenance-only, unqualified compression or always-raw baselines.

Predictive/control abstractions, causal/interventional sufficiency, confidence gating, provenance, proof-carrying actions, stale-memory detection and certified abstractions are donor-owned.

## Post-outcome status — 2026-08-23

The independent bounded theory checker closes the current responsibility-indexed support construction, transport/revocation conditions, and approximate-support/calibration model under the frozen finite assumptions. These are bounded formal results, not a claim that every real responsibility family forms one total ladder.

### Non-synthetic responsibility shift — handwritten digits

The prospectively frozen real-data study returns `P13_REAL_RESPONSIBILITY_SHIFT_V1_SUPPORTED` with byte-identical replay over 17,970 episodes. A compact state is learned for parity responsibility and is then confronted with the stronger exact-digit responsibility.

Fold by fold, responsibility-carrying state (RCS) exactly matches always-raw accuracy on both responsibilities while reading only 33 floats per episode instead of 64. Aggregate state-read reduction is `0.484375` (48.4375%). RCS reopens on half the episodes and never reuses unsupported compact state for exact-digit responsibility.

Protected comparator outcomes:

- RCS: combined accuracy `0.9435169727`, exact-digit accuracy `0.9699499165`, parity accuracy `0.9170840289`, unsupported exact-digit reuse `0`;
- ALWAYS_RAW: identical task accuracy, 64 floats read/episode, reopen rate `1.0`;
- CONFIDENCE_ONLY: exact-digit accuracy `0.3956594324`, unsupported exact-digit reuse rate `0.7774067891`;
- PROVENANCE_ONLY / UNQUALIFIED: exact-digit accuracy `0.2376182526`, unsupported exact-digit reuse rate `1.0`.

The raw-vs-compact exact-digit accuracy gap is `0.7323316639`. Thus the compact state can be current, provenanced and highly confident for the old responsibility while being structurally inadequate for the upgraded responsibility.

### Verifier-backed responsibility/epoch shift — CNF

A second, disjoint protected domain now returns `P13_VERIFIER_RESPONSIBILITY_SHIFT_V1_SUPPORTED`. Twelve CNF cases were frozen before the runner and independent checker. Each base formula has exactly two satisfying models; a previously verified model/certificate is valid for the old responsibility at epoch `E`. A new clause changes the formula and responsibility, invalidates the old model, and leaves exactly one alternate satisfying model.

Across 24 old/new-responsibility episodes per arm:

- RCS: `24/24` verifier-correct, `0` stale reuse, `60` raw literal reads;
- ALWAYS_RAW: `24/24`, `0` stale reuse, `108` raw literal reads;
- CONFIDENCE_ONLY: `12/24`, `12` stale reuses;
- PROVENANCE_ONLY: `12/24`, `12` stale reuses.

RCS therefore matches the exact verifier safety ceiling while reducing raw reads by `44.44444444444444%`. The old certificate is explicitly valid before the semantic change and explicitly non-transportable after it. A structurally independent checker reproduces the exact counts and byte replay.

Bound receipt: `top_tier/P13_VERIFIER_RESPONSIBILITY_SHIFT_RESULT_RECEIPT_V1.md`.

**Earned claim:** responsibility-scoped support rather than confidence/provenance alone determines safe reuse in both a non-synthetic real-data responsibility change and a disjoint exact verifier-backed responsibility/epoch change. In both domains RCS matches the always-raw correctness ceiling while avoiding unnecessary raw-state access. This does not establish arbitrary certificate transport across all semantic changes or external scientific-authority judgments beyond these frozen responsibilities.

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

Define how a responsibility certificate transports under representation/compiler version change, source/evidence update, context/epoch change, responsibility upgrade and loss of raw-recovery availability. Compose with P6/P7/P8 only through frozen interfaces; P13 owns the state-reuse contract, not their general transition/transport/authority claims.

The CNF study now supplies a bounded exact semantic/epoch-change witness: the old certificate is valid for `R_old` and is revoked/non-transportable for `R_new` after the added clause.

### T13.3 — Approximate support

Extend beyond exact finite support to a calibrated approximate-support regime with prospectively fixed tolerance/risk semantics. The state must not self-certify its own support probability.

## Protected real-system programme

### E13.1 — verifier-backed responsibility shift

**Bounded execution complete:** the frozen CNF responsibility/epoch study supplies an exact verifier-backed instance of compact verified reuse -> semantic change -> required reopen/reconstruction.

### E13.2 — research/agent responsibility shift

The handwritten-digits study supplies a non-synthetic second domain but is not a research-agent workflow. A further research/agent responsibility change can strengthen the maximum cross-domain claim, but it is no longer required to establish that the phenomenon crosses real-data and exact-verifier settings.

### E13.3 — semantic-change transport

**Bounded exact execution complete:** CNF clause/epoch change demonstrates preserve-before-change and revoke-after-change. General transport under representation/evidence/evaluator changes remains open.

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
- [x] verifier-backed responsibility shift at bounded formal/problem-solving scope (12 protected CNF semantic-change cases);
- [x] second qualitatively different responsibility-shift domain for the broad two-domain claim (digits + CNF);
- [x] bounded semantic/epoch-change certificate transport/revocation benchmark;
- [x] reduced unsafe reuse without always-reopen degeneration in both protected shifts;
- [x] meaningful resource saving versus always-raw safety ceiling (`48.4375%` fewer raw-state floats in digits; `44.4444%` fewer raw literal reads in CNF);
- [x] independent exact verifier/two-implementation authority for the formal responsibility-shift domain;
- [x] current protected negative/comparator outcomes and deterministic replay corrections retained;
- [ ] independent external scientific authority for a broader research/agent responsibility scope, if that scope is retained in the final headline;
- [ ] current donor saturation and exact final package replay.

The remaining scientific blocker is therefore no longer “does responsibility-scoped reuse survive outside the first controlled study?” It is whether the final manuscript claims an even broader research/agent scientific-authority layer. If the headline is limited to the now-demonstrated real-data + exact-verifier cross-domain result, that external research-agent authority should be described as a future generalization rather than silently required by the current evidence.

If responsibility support is not ordered in a later domain, preserve the partial-order/non-comparability result rather than forcing a universal ladder.

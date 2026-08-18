# P8 candidate journal-readiness plan — A Theory of Epistemic Authority for Autonomous Science

**Current terminal:** computed per commit, not asserted here. See
`../PEER_REVIEW_READY_PACKAGE.md`, which defines

```text
PEER_REVIEW_READY := p6-p8-candidate-ci == success AND ci == success
                     on one immutable head
```

This line previously read `CANNOT_CHECK / not a promoted paper / not peer-review
ready`. That was written before the submission package existed and had gone
stale: it contradicted `JOURNAL_READINESS_V2_1.md`, which already deferred to the
computed terminal, so the two files in this directory disagreed about P8.

It is deliberately **not** replaced with `PEER_REVIEW_READY`. The package file
states that it does not hard-code a claim that could become stale after a content
edit, and writing a terminal into this file would reintroduce the staleness being
removed. What follows is the last observation, not a standing claim.

**Last observed on `2f701036`** (merge of #402 into `main`):

| predicate | result |
|---|---|
| `p6-p8-candidate-ci` | success |
| `ci` | success |

The candidate workflow's four required steps all passed on that head: *Theory and
live-embedding gate*, *Peer-review submission gate*, *Build and audit submission
PDFs*, *Archive audited submission PDFs*. The PDF step compiled
`submission/JAAMAS_MANUSCRIPT.tex` with `latexmk` and rejected no overfull box, undefined
reference or undefined citation.

Any commit after `2f701036` — including the one carrying this sentence — has to be
re-evaluated against the same two predicates. That is the point of computing the
terminal rather than storing it.

**Not claimed:** `PEER_REVIEW_READY` means ready for external editorial and
referee evaluation. It does not mean `PEER_REVIEWED`, `ACCEPTED`,
`FLAGSHIP_PROMOTED`, or empirically superior to any baseline.

## 0. Earned local package state — 2026-08-17 wide pass

Present now:

- widened `manuscript/FORMAL_CORE_V1.md` with requested/committed effects, hard obligations, explicit cross-domain coercions, scope/epoch, dependency revocation, protected roots and `CANNOT_CHECK`;
- `manuscript/DRAFT.md` rewritten around mature authorization/effect/abstention/provenance donors rather than generic capability-permission rhetoric;
- synchronized `CLAIM_LEDGER_V1.md` restricting P8 to cross-domain results;
- ownership matrix marking all five within-domain P1–P5 gates as `MERGE_EXISTING`/internal prior ownership;
- donor/parent maps expanded through Delegation Logic, SecPAL, authorization/trust-management logic, deontic/action logic, non-interference, ETAS, FAVA, permission systems, AgentAbstain, provenance and shielding;
- deterministic authority checker widened with epoch replay, alternate derivation under revocation, post-hoc refusal and clean authorized controls;
- additive `CHECK_RESULTS_V2.md`;
- `REPRODUCE.md`;
- `PROSPECTIVE_EVALUATION_V1.md` with paired cross-domain attacks, valid-coercion controls, strongest donor baseline slots and protected-custody requirements;
- five-role adversarial review log.

These artifacts do not establish semantic soundness of real coercions, exact P1–P5 embedding, empirical advantage, novelty or peer-review readiness.

## 1. Distinct-object gate
- [ ] #343 proves P8 is not P4/programme theory generalized in vocabulary.
- [x] P4's protected scientific-authority contribution and P5's protected self-change/no-self-promotion contribution are explicitly treated as prior internal ownership.
- [x] cross-domain authority object has a formal discriminator: locally valid source judgments may not authorize foreign-domain effects without an explicit sound coercion.
- [ ] that discriminator survives authorization/non-interference/policy-composition parent-field saturation and prospective evaluation.

## 2. Nearest-work closure
- [ ] deontic/input-output/action logic families dispositioned atomically.
- [ ] access-control/trust-management/authorization-logic families dispositioned, including delegation and revocation.
- [ ] information-flow/non-interference parent formulations dispositioned.
- [ ] ETAS/effect-system families dispositioned.
- [ ] FAVA/evidence-backed permission graph families dispositioned.
- [ ] policy-card/user-permission/runtime-governance families dispositioned.
- [ ] selective prediction/abstention/AgentAbstain family dispositioned.
- [ ] provenance/verification/execution-tracing families dispositioned.
- [ ] shielding/behavioral-bound agent families dispositioned.
- [ ] research-integrity/scientific-authority families dispositioned.
- [ ] hostile exact-composition search completed.
- [ ] two no-material-change rounds.
- [ ] #287 novelty certificate current.

## 3. Formal calculus
- [ ] typed action/effect domains frozen after saturation.
- [ ] full capability/support/defeater/obligation/authority/revocation/`CANNOT_CHECK` semantics frozen.
- [x] non-compensatory hard obligations are formally separated from soft utility constraints in the current core.
- [x] cross-domain coercion and cross-domain authority-laundering rule are defined.
- [x] dependency-grounded revocation with independent-derivation preservation is defined and supported by a bounded fixture.
- [x] scope/epoch matching is explicit in the executable checker.
- [x] post-hoc refusal is separated from preventive pre-effect authorization.
- [ ] semantic soundness conditions for trusted roots/coercions proved for the claimed contract family.
- [ ] conservative exact P1–P5 embedding proved/checked against native decisions.
- [ ] conservative donor-native ETAS/FAVA/authorization-logic embeddings established where feasible.

## 4. Protected cross-capability benchmark
- [x] prospective paired-case protocol draft covers reframe, route/task stop, map/merge, assertion and self-modification authority plus an external effect domain.
- [x] explicit cross-domain laundering, valid-coercion, scope, epoch, revocation, post-hoc-refusal, `CANNOT_CHECK` and clean-authorized families are specified.
- [ ] versioned generator implementation frozen before candidate runs.
- [ ] hidden labels/coercion validity/custody frozen prospectively.
- [ ] protected evaluator chronology/access telemetry implemented.
- [ ] paired cases executed against all required systems.
- [ ] clean authorized controls demonstrate absence of security-by-total-refusal.

## 5. Baselines/ablations
- [ ] exact existing P1–P5 independent gates.
- [ ] trust-management/authorization-logic adapter where faithful.
- [ ] ETAS/FAVA-style effect/permission adapters where feasible.
- [ ] provenance-only verifier.
- [ ] abstention baseline.
- [ ] expected-utility/confidence baselines as lower bounds only.
- [ ] rule-based domain-specific authorization.
- [ ] no-noncompensatory-obligation ablation.
- [ ] untyped/global-authority-token ablation.
- [ ] no-revocation/no-epoch ablations.

## 6. Metrics/statistics
- [x] primary metric families are prospectively specified (unauthorized action/laundering, stale/scope/revocation failure, clean coverage, unnecessary refusal, valid coercion, `CANNOT_CHECK`, latency/cost).
- [ ] unauthorized-action results.
- [ ] unnecessary-refusal results.
- [ ] clean authorized coverage results.
- [ ] cross-domain authority-laundering results.
- [ ] correct revocation/re-derivation results.
- [ ] calibrated `CANNOT_CHECK` results.
- [ ] cost/latency results.
- [ ] prospective statistical treatment frozen where non-deterministic systems are used.

## 7. Manuscript/reproducibility
- [x] working markdown draft exists.
- [x] formal core + synchronized claim ledger exist.
- [ ] full-text related work with exact P4/P5 and donor boundaries.
- [ ] claim ledger #346 terminal complete (ledger exists but multiple paper-level claims remain `CANNOT_CHECK`).
- [x] deterministic formal/hostile-check reproduction path documented.
- [ ] protected benchmark/attack replay under #347.
- [ ] protected/public artifact split and immutable custody manifests.
- [ ] every empirical positive has #283 receipt.

## 8. Submission
- [ ] venue selected under #345 only after residual/result shape stabilizes.
- [ ] literature refreshed under #344 within 14 days.
- [ ] independent PDF proofread and permanent archive.

## Done definition

Promote P8 only if a cross-domain epistemic authority calculus provides a distinct formal or empirical result beyond P4/P5, independent capability-specific gates and mature authorization/effect systems—especially on pre-frozen cross-domain laundering/revocation cases—without winning by excessive refusal. Otherwise merge the synthesis into P4/programme theory.
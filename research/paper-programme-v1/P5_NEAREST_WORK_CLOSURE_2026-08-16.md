# ORION-P5 nearest-work closure — 2026-08-16

**Paper:** ORION-P5 — Self-ORION  
**Issue:** #102  
**Authority:** literature/claim-boundary audit only. This artifact does not create an empirical PASS and does not promote `CANNOT_CHECK` evidence.  
**Freeze rule:** repeat the literature closure within 14 days of submission and shrink the claim again if a closer system appears.

## Review lenses

The closure was checked through three independent questions:

1. **Novelty lens:** what mechanism is already demonstrated by nearest work and therefore cannot stand alone as a P5 novelty?
2. **Evaluation lens:** what nearest work must become a matched baseline, ablation, or measurement requirement rather than prose comparison?
3. **Governance lens:** what authority/integrity property remains materially different after removing already-known self-edit, failure-learning, replay, persistent-memory and causal-attribution mechanisms?

## Disposition matrix (Table P5-1 source)

| Mechanism / nearest work | Current pressure on P5 | Disposition | Consequence for P5 |
|---|---|---|---|
| ADIAS — persistent issue-centric self-improvement (`arXiv:2608.06410`) | Persistent issue identity, evidence and intervention history are already first-class optimization state. | `ADOPT` | Keep persistent issue state as infrastructure and prior art; remove it from standalone novelty. |
| Darwin Gödel Machine (`arXiv:2505.22954`; pinned `jennyzzt/dgm@a565fd2d1dca504ef5104a7cc0f3bdc4ab9b4fd2`) | Open-ended self-code modification already combines archive, sandbox and empirical validation. | `ADAPT` | Treat DGM-like self-edit/archive as a strong matched baseline; P5 cannot claim archive + sandbox + self-edit as novel. |
| ADAS (`arXiv:2408.08435`) | Meta-agent search over agent designs with an archive is established. | `ADAPT` | Include protocol-matched ADAS/meta-agent search; agent-design search is not P5 novelty. |
| Direct self-improving coding agents — MOSS (`arXiv:2605.22794`) and accumulated behavioral rules (`arXiv:2607.13091`) | Source rewriting, production-failure evidence, replay validation, persistent correction rules and externally gated promotion already exist in direct coding-agent settings. | `ADAPT` | Use the strongest runnable direct self-improvement implementation available at execution freeze. Do not claim source rewriting, persistent correction, replay validation or human-gated deployment alone. |
| AlphaEvolve-like evaluator-driven program evolution | Evaluator-guided mutation/search is a strong optimization family even when it does not model causal responsibility. | `ADAPT` | Keep an evaluator-only/evolutionary search arm; any P5 benefit must survive matched evaluator/search budget. |
| SAGE / Multi-Hypothesis Failure Attribution (`arXiv:2606.31478`) | Competing failure hypotheses and evidence-grounded attribution to intervention levels are explicit. | `ADOPT` | Multi-hypothesis diagnosis is prior art. P5 tests whether a frozen discriminator reduces false method changes. |
| CausalFlow (`arXiv:2605.25338`) | Counterfactual/interventional responsibility scoring and minimal repair directly cover broad causal-attribution claims. | `ADOPT` | Causal attribution/minimal repair is not standalone novelty; use a CausalFlow-like runnable arm where feasible. |
| Learning from Failure (`arXiv:2606.31270`) | Failed trajectories are diagnosed and converted into agent improvements. | `ADOPT` | Failure-driven improvement is prior art; retain a failure-driven patch baseline. |
| PAST-Bench (`arXiv:2608.04003`; pinned `Gen-Verse/PAST-Bench@f8223517ae7491e776b69793d9f11e9d074ab42e`) | Experience-on/off tests ask whether retained experience causes later fresh-session improvement. | `ADOPT` | Use pathway-sensitive replay/fresh evaluation and never treat memory presence as learning evidence. |
| SEVA (`arXiv:2606.29713`) | Iterated self-evolution can create benchmark specialists with cross-benchmark regression. | `ADOPT` | Harmful/fresh transfer and specialist regression stay primary/tail outcomes; motivating-task improvement cannot compensate. |
| Continual / experiential learning | Persistent experience, replay, memory consolidation and cross-session adaptation are established parent disciplines. | `COMPOSE` | P5 must show governed transfer/integrity beyond generic experience retention; no novelty claim for continual learning itself. |
| Debugging, root-cause analysis and program repair | Fault localization, causal debugging, minimal repair and regression testing long predate agent self-evolution. | `COMPOSE` | Treat them as parent disciplines for attribution/repair; measure false method changes and repair success rather than rename debugging as novelty. |
| Safe self-modification, evaluator integrity and meta-overfitting | Protected evaluation, rollback/external promotion and benchmark-overfitting concerns are now explicit across self-evolving-agent work. | `COMPOSE` | Protected evaluator custody, contamination telemetry and harmful-tail reporting are mandatory non-compensatory gates, not optional safety prose. |
| Current 2026+ self-evolving-agent frontier — MOSS, MEGA (`arXiv:2608.10504`) and `Self-Evolving Coding Agents` survey (`arXiv:2608.03392`) | MOSS pressures source rewrite/replay/promotion; MEGA pressures durable evolving optimization knowledge and controlled effect attribution; the survey makes reliability, overfitting, safety, cost and generalization first-class field concerns. | `ADAPT` | At execution freeze, select the strongest runnable current arm(s) under matched resources. Re-run this row within 14 days of submission; no fixed 2026 snapshot may be treated as permanently current. |

## Claim contraction after the fresh audit

P5 does **not** claim novelty for any of the following in isolation: persistent issue state, failure-driven improvement, multi-hypothesis diagnosis, causal attribution, source-level self-rewriting, archive persistence, replay validation, persistent behavioral rules, durable optimization knowledge, sandboxing, rollback, evaluator-guided search, or externally gated deployment.

The remaining candidate residual is narrower and non-compensatory:

> A persistent development issue may license a method change only after evidence-bound causal discrimination and invention-readiness checks; acceptance then requires replay **and** independent protected fresh-transfer/non-harm evidence under matched resources, immutable retention of negative/null/harmful evolution history and compromise telemetry, evaluator/holdout custody outside challenger write authority, and structurally absent self-certification/self-merge authority. Promotion remains a host/external decision.

This is a **composition claim**, not a claim that any component is individually new. It remains `CANNOT_CHECK` until the prospective hidden-cause study demonstrates transfer/integrity benefit against strong matched baselines.

## Baseline consequence

The final execution manifest must not silently weaken unavailable nearest work into straw men. For each baseline family it must record one of the programme dispositions (`UPSTREAM_PINNED`, `PROTOCOL_REIMPLEMENTED`, or `NOT_EXECUTABLE_WITH_JUSTIFICATION`), bind the exact config hash, and match the declared LLM/tool/time/candidate budget. MOSS/MEGA or a newer direct self-evolving system discovered at the submission-window audit should be preferred when a faithful runnable artifact can be frozen.

## Closure result

**Step-1 literature/novelty audit:** complete for the 2026-08-16 design-freeze snapshot.  
**Table P5-1 source:** complete.  
**Empirical P5 terminal:** unchanged — `CANNOT_CHECK`.

The required future literature closure within 14 days of submission remains open by design.

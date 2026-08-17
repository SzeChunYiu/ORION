# Literature matrix — GlobalPositiveCertificate.v1 (issue #285)

Saturation stop rule (from #285): stop after two consecutive primary-source rounds yield no mechanism changing admission, non-regression statistics, transfer benchmark design, Pareto archive semantics, catastrophic-harm handling, or protected evaluator/custody.

This matrix is a **pre-outcome freeze**. It does not authorize `GLOBAL_POSITIVE_SUPPORTED`.

## Round 1 — issue seed + in-repo nearest work

| Mechanism | Source | Disposition | What is absorbed / refused |
| --- | --- | --- | --- |
| Regression-controlled compounding of agent optimizers | *Do Agent Optimizers Compound?* arXiv:2607.14004 | `ADAPT` | Continual evaluation with a regression control is parent pressure. Residual: heterogeneous protected objectives across epistemic families, not a static-phase score. |
| Continual skill learning without a universal leader | *SkillLearnBench* arXiv:2604.20087 | `COMPOSE` | Average gains with no method leading on all tasks, plus self-feedback drift, motivate the worst-family rule and a ban on mean-score authority. |
| Controlled-stream transfer that degrades held-out settings | *AGENTCL* arXiv:2606.02461 | `COMPOSE` | Motivates mandatory fresh/held-out splits and forbids replay-only admission. |
| Abstract-insight vs trace negative transfer | *Memory Transfer Learning* arXiv:2604.14004 | `COMPOSE` | Negative-transfer accounting is required; low-level trace replay cannot compensate fresh harm. |
| Pareto archive of multi-objective trade-offs | *EvoDrive* arXiv:2606.03678 | `ADAPT` | Pareto archives are prior work in a driving domain. Residual is **admission authority**: non-compensatory, evidence-bound, with immutable negative history and no self-certification. |
| Anytime-valid acceptance of self-evolution | *PACE* arXiv:2606.08106; *SEA* arXiv:2607.00871 (already audited in `research/paper-programme-v2/NEAREST_WORK_V2_AUDIT_2026-08-16.md`) | `ADOPT` as **baseline** | Sequential stopping is prior work. It does not replace fresh transfer, worst-family non-regression, or evaluator custody. |
| Non-compensatory STATIC→REPLAY→FRESH→PROTECTED gate | ORION P5 V2 (`src/orion/self_orion/staged_gate.py`) | `COMPOSE` as **baseline** `p5_staged_acceptance` | P5 is one family of self-improvement evidence, not a cross-domain Pareto certificate. This module does not import that V2 surface into V1 runtime. |
| Protected authority / fail-closed missing evidence | ORION P4 V2 + `#209`/`#210` constitutional boundary | `COMPOSE` | Evaluator integrity is a fail-closed dimension. This freeze does **not** authorize Phase-4 programme operation. |

## Round 2 — parent disciplines (function-only / adversarial “already solved”)

| Mechanism | Parent discipline | Disposition | Mechanism change vs Round 1? |
| --- | --- | --- | --- |
| Safe / conservative policy improvement; baseline-preserving updates | SPI / conservative policy iteration; conservative contextual bandits (already P2 parent) | `ADAPT` | Non-inferiority margins are the SPI idea. No change to the all-dimension conjunction or worst-family rule. |
| Pareto / MOO archives and scalarization | Multi-objective optimization; weighted-sum scalarization | `REJECT` as authority; `ADAPT` archive as analysis ceiling | Weighted-sum / mean global score is the **forbidden** primary rule. Oracle Pareto frontier is a baseline ceiling only. |
| Catastrophic forgetting / negative transfer | Lifelong learning | `COMPOSE` | Already in Round 1 via AGENTCL / Memory Transfer Learning. Confirms dropping a failed family is laundering. |
| Regression testing / change-impact analysis | Software engineering | `COMPOSE` | Protected regression split spanning previously passed families. No new admission operator. |
| Constrained Bayesian / sequential testing; no fishing | Statistics | `ADAPT` | Multiplicity: all frozen objectives must pass; sequential candidates reuse the freeze. No post-outcome weight tuning. |
| Safety cases / assurance defeaters | Assurance cases (P4 parent: proof-carrying actions, defeater cards) | `COMPOSE` | Integrity dimension is fail-closed. Does not add a scalar residual-risk score as authority. |
| Darwin Gödel Machine / archive self-edit | Self-evolving agents | `DEFER` as official executable baseline | Strongest continual-optimizer baseline remains `continual_optimizer_unavailable` until an official run can be bound. Mechanism of *admission* is unchanged. |

Round 2 introduced **no** change to:

- admission rule (conjunction over frozen dimensions, not a mean)
- non-regression statistics (per-dimension intervals + worst family)
- transfer benchmark design (four required families, four split slots)
- Pareto archive semantics (analysis ceiling, not decision)
- catastrophic-harm handling (margin 0, no compensation)
- protected evaluator/custody boundary (fail-closed integrity; no Phase-4 authorization)

Stop rule met for this fibre. Reopen if a system already performs **protected, non-compensatory, negative-history-bound Pareto admission across heterogeneous epistemic task families without self-certification**.

## What this is not

- Not Pareto optimization novelty.
- Not a licence to call a local win globally positive.
- Not Phase-4 operation.
- Not a substitute for `#283` independent verification of any later positive.

# P9 constructive saturation ledger — 2026-08-18

## Method and boundary

This is a dated, bounded nearest-work pass for P9's proposed object:
per-instance capability routing, retained failure evidence, abstention, and the
separation of capability from authority. Searches covered algorithm selection
and configuration, selective prediction/reject options, LLM paradigm/tool
routing, prover–verifier abstention, and capability self-assessment. Entries
below use primary papers or official project artifacts.

The acceptance rule is **saturation before residual**. Each donor must yield a
reusable structure and an adoption decision. `CITED_ONLY` is not a disposition.
The ledger does not claim that all relevant literature has been found.

## Structure-extraction and assimilation receipts

| Donor | Strongest structure extracted | ORION assimilation receipt | Strength gained | Disposition |
|---|---|---|---|---|
| Bischl et al., [ASlib](https://arxiv.org/abs/1506.02465), AI 2016 | A standard scenario schema joins instance features, per-algorithm outcomes and fixed cross-validation splits; PAR10, SBS and VBS make routing claims comparable. | Exact `SAT11-HAND-ALGO` source files and digests, the frozen protocol, scenario CV folds, PAR10/SBS/VBS reporting and a digest-fail hostile test live under `benchmark/`. | P9 moved from synthetic self-authored tasks to a reproducible public discriminator with a leakage barrier. | `ABSORBED` |
| Lindauer et al., [AutoFolio](https://jair.org/index.php/jair/article/view/10955), JAIR 2015 | Selector design and hyperparameters are themselves configuration choices; nested train/test separation is essential, and a serious selector should be compared with automatically configured alternatives. | The public protocol performs threshold selection only inside each outer training fold. AutoFolio itself is not used as a baseline and P9 makes no selector-superiority claim. A standalone reopen requires a pinned AutoFolio-class comparison across multiple scenarios. | Prevents manual threshold tuning on test outcomes and turns the missing strong-selector comparison into an explicit limit. | `DEFERRED_WITH_TRIGGER` |
| Kerschke et al., [Automated Algorithm Selection: Survey and Perspectives](https://arxiv.org/abs/1811.11597), ECJ 2019 | Complementary solver strengths, instance features, per-instance selection, schedules and portfolios form a mature research object. | Phase 0 and the ASlib evaluator use the canonical feature → portfolio → per-instance route structure; P9 explicitly removes algorithm selection, portfolios and scheduling from its novelty claims. | Eliminates a false novelty surface and gives P9 the field's standard baselines and vocabulary. | `ALREADY_PRESENT` |
| Geifman & El-Yaniv, [SelectiveNet](https://proceedings.mlr.press/v97/geifman19a.html), ICML 2019 | A selective model has a predictor and a selection function; abstention is evaluated through risk/coverage rather than accuracy alone. | `CapabilityRoute` is an inspectable route-or-abstain value; the public result reports attempt coverage, solve retention, abstention precision/recall and PAR10 cost. | Abstention is no longer hidden inside a planner or celebrated without its coverage cost. | `ABSORBED` |
| Zhou et al., [Select-then-Solve](https://arxiv.org/abs/2604.06753), 2026 | Reasoning paradigms have complementary per-task strengths; a learned router should be compared with the best fixed choice and an oracle ceiling, with the recovered oracle gap made explicit. | Phase 0 reports best-fixed, learned-schedule and oracle outcomes; the public discriminator reports SBS, RF router and VBS. Learned routing itself is a nonclaim. | Makes complementarity and oracle distance visible while blocking a routing-novelty claim. | `ALREADY_PRESENT` |
| Sedoc et al., [Trust but Verify](https://arxiv.org/abs/2605.25133), 2026 | Selective prediction benefits from structured confidence verdicts and coverage–precision evaluation; a verifier outside its effective region can collapse or invert the signal. | ORION exposes multi-valued `Verdict`, retains every candidate assessment in `CapabilityRoute`, reports abstention coverage/precision, and keeps `CANNOT_CHECK` distinct. External authority remains outside the router. | Makes the uncertainty terminal inspectable and preserves an explicit effective-region failure mode. | `ABSORBED` |
| Sun et al., [When2Tool](https://arxiv.org/abs/2605.09252), 2026 | Tool necessity needs a controlled decision boundary and evaluation of call reduction against retained task accuracy; suppressing calls alone can be harmful. | The public primary metric is attempt reduction only on VBS-unsolved instances, constrained to retain at least 95% of the non-abstaining router's solved cases. | Prevents “fewer calls” from being treated as a gain when it destroys capability. | `ABSORBED` |
| Yang et al., [Capability Self-Assessment](https://arxiv.org/abs/2606.00251), 2026 | Self-assessment is a learned policy whose value depends on preserving the capability it assesses; a training method can improve assessment while degrading the underlying competence. | `fit_competence` is separate from mechanic absorption and the append-only evidence ledger; a hostile integration assertion verifies that fitting competence does not mutate the absorbed `MechanicSpec`. | Adds capability preservation as an invariant rather than assuming self-assessment is harmless. | `ABSORBED` |

## Hostile already-solved test

The following possible P9 headlines do **not** survive saturation:

- “select the best solver/mechanic per instance” — owned by algorithm selection;
- “learn which reasoning paradigm to use” — directly demonstrated by
  Select-then-Solve and adjacent routing work;
- “abstain when confidence is low” — owned by selective prediction/reject-option
  work;
- “learn whether the system can solve the task” — directly owned by capability
  self-assessment;
- “reduce unnecessary tool calls while retaining performance” — directly
  measured by When2Tool.

The remaining ORION structure is narrower: capability evidence and an
abstention decision are prevented from becoming execution authority. That
structure is real and executable, but P8 already owns its formal authority
calculus. P9 supplies an implementation and a bounded public empirical
companion; it does not retain a clean independent paper object.

## Residual decision

`MERGE_P9_INTO_P8_PROGRAMME`.

The positive ASlib result survives as evidence, not as a novelty claim. The
framework is stronger after assimilation, while the proposed standalone P9
object collapses into mature routing/selective-prediction work plus P8's owned
capability/authority boundary. Reopening a standalone P9 requires all of:

1. a multi-scenario, source-pinned evaluation including an AutoFolio-class
   strong baseline;
2. a prospectively defined authority-relevant outcome rather than call count
   or routing accuracy alone; and
3. a residual formal or empirical object not already owned by P8.

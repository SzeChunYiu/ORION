# Route-level search control v0 — frozen research and discriminator

**Status:** SOURCE_PROJECTION + FROZEN_DESIGN_DISCRIMINATOR. External work informs the candidate mechanic but does not mint ORION authority.

**Question:** what evidence should cause ORION to continue, reformulate, switch, suspend, or stop one search route without turning local route exhaustion into a claim that the whole research task is saturated?

## Review lanes

- **Information retrieval:** query reformulation and adaptive choice among retrieval operations.
- **Sequential decision theory:** exploration/exploitation under changing reward distributions.
- **Stopping/measurement:** what a local stop can and cannot certify.
- **ORION governance:** explicit state, frozen thresholds, replayable reasons, and reopen triggers.

## Absorbed findings

1. **Patch leaving is a local decision, not a global exhaustion proof.** Marginal-value work leaves a patch when local gain falls relative to alternatives. The useful transfer is comparative opportunity cost: weak marginal yield can justify leaving one route for another. It does not establish that no other route contains relevant information.

2. **Reformulation is a real retrieval action.** Nogueira & Cho, EMNLP 2017, train query reformulation against document recall and report relative recall improvements. A flat route should therefore have an explicit REFORMULATE action before it is treated as exhausted.

3. **Switching retrieval operations can outperform a fixed sequence.** Zhu et al., EMNLP 2021 (AISO), model information seeking as a partially observed decision process over BM25, dense retrieval, hyperlink traversal, and answer actions. This supports a typed SWITCH decision when another route family is available rather than repeatedly applying one fixed route.

4. **Route value is non-stationary.** Besbes, Gur & Zeevi, *Stochastic Systems* 2019 / arXiv:1405.3316, show that arm rewards may change over time and evaluate against a dynamic oracle. For ORION this means a stopped/suspended route must carry reopen triggers after a material frame change, a backend refresh/recovery, a budget change, or a material finding from another route.

5. **Target-recall certification is a different problem.** Lewis, Yang & Frieder, SIGIR 2021 / arXiv:2108.12746, provide statistically valid sample-based stopping rules for one-phase TAR when a fixed corpus and target recall exist. ORION route control must not smuggle that guarantee into open-world research. A route STOP is only a route-level execution/resource conclusion.

6. **Long-horizon search benefits from explicit external state.** Lan et al., Findings of ACL 2026 (Table-as-Search), represent search candidates and missing information as structured state rather than relying on one text context. ORION should likewise persist route attempts, retrieved/novel evidence, cost, failures, and decisions as typed objects.

## Candidate mechanic

Each route owns an append-only attempt history. Every attempt records:

- exact route and query identity;
- retrieved content digests and which were novel;
- cost units;
- execution failure signatures;
- whether the backend explicitly reported its result stream exhausted.

A frozen policy produces exactly one local action:

- `CONTINUE`: route is still productive or untried;
- `REFORMULATE`: local novelty is flat but the route is still executable;
- `SWITCH`: repeated local flatness plus an available alternative route;
- `SUSPEND`: execution/backend failure with an explicit recovery trigger;
- `STOP`: only explicit backend exhaustion or exhaustion of the route's frozen resource budget.

Every decision is required to expose `certifies_task_saturation = False`.

## Frozen v0 discriminator — fixed before implementation

Policy id: `route-control-v0-flat-1-switch-2`.

The implementation must satisfy these known-world and hostile cases:

1. untried route -> `CONTINUE`;
2. productive attempt with novel evidence -> `CONTINUE`;
3. one successful zero-novelty attempt -> `REFORMULATE`;
4. two consecutive zero-novelty attempts + an alternative family -> `SWITCH`;
5. the same flat history with **no alternative** -> `REFORMULATE`, never `STOP`;
6. execution failure -> `SUSPEND` and reopen on backend recovery or material frame change;
7. explicit backend exhaustion -> `STOP` the route, but never certify task saturation; reopen after backend refresh or material frame change;
8. route budget exhaustion -> `STOP` the route, but never certify task saturation; reopen after budget increase or material frame change;
9. changing failure/novelty evidence must change the resulting reason/state rather than being silently discarded.

The one- and two-flat thresholds are route-control heuristics, not measurements of recall. They are named and frozen so a later benchmark can reject or replace them. No scalar generated here may be consumed by task-level saturation authority.

## Open empirical obligations

- Compare this v0 policy against fixed-route and always-reformulate baselines on frozen retrieval tasks.
- Measure marginal unique-evidence gain per unit cost, not just total hit count.
- Test whether a route that was switched away from becomes useful after material findings from another route.
- Keep route-control performance separate from the still-open question of global recall/saturation.

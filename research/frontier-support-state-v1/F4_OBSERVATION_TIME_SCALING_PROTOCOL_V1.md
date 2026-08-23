# Frontier F4 — Observation-Time Scaling Protocol V1

Status: **FROZEN BEFORE OUTCOMES**

Frozen: 2026-08-20

## 1. Question

When a reasoning system is uncertain, should the next unit of budget be spent on more internal reasoning or on acquiring/refining task state?

This protocol separates three resources that are often conflated:

- model scale;
- thinking/search compute on a fixed observation;
- observation/state-acquisition budget.

## 2. Controlled task family

Each item has latent Boolean state `x in {-1,+1}^31` and one hidden task type:

- `OBSERVATION_LIMITED`;
- `COMPUTATION_LIMITED`;
- `MIXED`.

A public task descriptor specifies the allowed coordinate bundles and exact deterministic operations, but not the hidden coordinate values.

### Observation-limited items
Target is the majority sign over 5 prospectively chosen coordinates. Initially only 2 of those 5 values are visible. No deterministic computation over visible coordinates can recover the 3 hidden independent bits.

### Computation-limited items
All 9 relevant coordinates are visible, but the target is a frozen depth-4 Boolean composition over them. Additional observations are nuisance-only; an exact deterministic tool can close the computation if invoked.

### Mixed items
Target depends on 5 hidden/visible coordinates followed by a depth-3 composition. Both acquiring state and computation can matter.

Task-type proportions are exactly 1/3 each within every split and are not exposed to the solver.

## 3. Allowed actions

At each decision step the policy may choose one action:

- `OBSERVE(bundle_id)`: reveal one allowed state bundle;
- `THINK(k)`: spend exactly `k` declared reasoning units/tokens/iterations without new state;
- `TOOL(op_id)`: execute one frozen exact operation when permitted;
- `STOP(label)`: answer.

No action may reveal the hidden task-type label.

Controlled classical phase uses iteration counts as reasoning units. LLM phase uses generated-token/model-call accounting and is frozen separately.

## 4. Budget grid

Observation budget `O in {0,1,2,4,8}` bundles.

Thinking budget `C in {0,8,32,96}` units/tokens.

Tool budget `T in {0,1}` exact calls.

Every evaluated policy is projected onto the same `(O,C,T)` grid.

## 5. Policies

1. `THINK_ONLY`: no observations beyond initial state.
2. `OBSERVE_RANDOM`: spends observation budget uniformly at random, then fixed thinking.
3. `OBSERVE_RELEVANCE`: uses a frozen relevance scorer trained only on training items.
4. `UNCERTAINTY_ROUTER`: chooses OBSERVE/THINK/TOOL from frozen uncertainty/state features.
5. `ORACLE_TYPE`: knows hidden task type; upper bound only and never part of the primary claim.
6. `FULL_STATE`: reveals every relevant coordinate at the start; information-rich ceiling, cost counted.

## 6. Primary quantities

For target quality `q in {0.70,0.85,0.95}` estimate:

- `O*(q | C,T)`: minimum observation budget reaching q;
- `C*(q | O,T)`: minimum thinking budget reaching q;
- non-dominated `(O,C,T)` frontier;
- task-type-stratified accuracy;
- routing confusion matrix against latent task type (diagnostic only; policy does not receive labels).

Define an **Observation Substitution Ratio** where thresholds are observed:

`OSR_q = log(C*_low-observation(q) / C*_high-observation(q))`.

Positive OSR means extra state acquisition substitutes for internal reasoning compute at quality q.

## 7. Primary hypothesis

A joint policy should beat static thinking-only allocation because the three item classes have different limiting resources.

The experiment earns

`OBSERVATION_TIME_SCALING_FRONTIER_SUPPORTED`

only if:

1. at least one observation-limited cell shows a >=0.15 absolute gain from additional observation while increasing THINK alone from 32 to 96 yields <=0.03;
2. at least one computation-limited cell shows a >=0.15 gain from TOOL or increased THINK while additional nuisance observation yields <=0.03;
3. on MIXED items, the joint router's quality-cost point strictly dominates both THINK_ONLY and OBSERVE_RANDOM at one preregistered quality >=0.85;
4. pooled quality advantage is positive in all three held-out seeds;
5. no hidden task-type leakage is detected;
6. every native resource is reported separately.

If only the first two mechanistic controls pass but the learned router does not dominate, terminal is

`RESOURCE_LIMITS_SEPARATED__ADAPTIVE_ROUTER_NOT_SUPPORTED`.

## 8. Difficulty legibility secondary

The router emits predicted marginal values:

- expected gain from one more observation;
- expected gain from one more thinking block;
- expected gain from the exact tool.

Evaluate calibration against realized paired interventions on held-out items. This asks whether a structured state makes *remaining difficulty legible*, not just solvable.

This is secondary and cannot rescue the primary frontier gate.

## 9. LLM bridge

Only after controlled results are frozen, instantiate the same action semantics with a fixed open-weight model family. The initial observation, candidate OBSERVE bundles, and exact tool outputs are rendered without answer labels. LLM outcomes must use a new receipt and cannot change this controlled protocol.

## 10. Strongest allowed claim

If positive:

> Test-time scaling has a distinct observation axis in the frozen task family. When failure is observation-limited, acquiring relevant state dominates additional serial reasoning; when failure is computation-limited, extra observation does not help. A frozen adaptive policy can exploit this heterogeneity to shift the joint quality-resource frontier.

Forbidden:

- `thinking is unnecessary`;
- `all LLM failures are information failures`;
- any claim that treats observation actions as free.

# P13 Dual Scaling: Representation Allocation x Test-Time Compute — Protocol V1

Status: PROSPECTIVE / FROZEN BEFORE ANY DUAL-ALLOCATOR OUTCOME
Frozen: 2026-08-20

## Question

Can an inference system improve the accuracy-cost Pareto frontier by jointly deciding **how to represent the current state** and **how much downstream reasoning/search compute to spend**, rather than scaling only one resource?

## Resource accounting

Every evaluated system receives the same total budget accounting for:
- state-compilation tokens/operations;
- downstream generation/search tokens;
- external verifier/tool calls;
- cached-state bytes where material.

Representation construction is not free.

## Required arms

1. `FIXED_STATE_FIXED_COMPUTE` — canonical state, uniform downstream budget.
2. `FIXED_STATE_ADAPTIVE_COMPUTE` — canonical state; learned/oracle compute allocator only.
3. `ADAPTIVE_STATE_FIXED_COMPUTE` — representation allocator only; uniform downstream budget.
4. `JOINT_STATE_COMPUTE` — chooses representation transform and downstream budget jointly.
5. `ORACLE_JOINT` — hindsight oracle under the same budget, upper-bound diagnostic only.

All learned allocators are fitted only on training/development data. No protected-outcome tuning.

## First execution domains

### Domain A — controlled query compiler
Use P11 worlds with heterogeneous query orders and compiler choices. Downstream compute is model interaction degree / feature budget. This is the calibration domain where exact optimum structure is known.

### Domain B — P9 procedural worlds
Use information-matched serialized vs typed state, with fixed open-weight model family and matched token budgets once the #618 LLM execution is available. Representation actions may include canonicalization/typed state and exact query-conditioned coordinate compilation only when semantically certified.

### Domain C — P10 formal reasoning
Blocked until native-state extraction passes its source identity/coverage controls. Candidate representation actions include full native state, typed state summary, query/tactic-conditioned view, and cached proof-state snapshot. Compute is Lean verifier/search budget.

## Primary metrics

For each total budget B:
- accuracy / verified solve rate;
- state-compilation cost;
- downstream reasoning/search cost;
- verifier calls;
- total cost;
- Pareto dominance against arms 1–3.

Define `joint_gain(B)` as performance of `JOINT_STATE_COMPUTE` minus the best single-axis adaptive arm at identical total cost.

## Positive terminal

`JOINT_REPRESENTATION_COMPUTE_ALLOCATION_SUPPORTED` requires:
1. positive `joint_gain` at at least two prespecified nontrivial budgets in the controlled domain;
2. a paired bootstrap lower 95% bound >0 for at least one protected real-system domain (P9 LLM or P10 Lean) before any cross-domain claim;
3. no budget-accounting advantage from omitted compilation/tool costs;
4. a nondegenerate policy using at least two representation actions and at least two compute levels on protected data;
5. oracle gap reported and not hidden;
6. all representation-equivalence/sufficiency controls pass.

Without a real-system domain, the strongest terminal is `CONTROLLED_DUAL_SCALING_ONLY`.

## High claim ceiling

If the real-system gate passes, the intended claim is not merely that representation and compute both matter. It is:

> Representation construction and downstream reasoning are jointly allocatable inference resources; optimizing them together can outperform spending the same budget by scaling either representation quality or reasoning compute alone.

No universal substitution law is assumed in advance. Complementarity, substitution, and phase transitions are all admissible outcomes.

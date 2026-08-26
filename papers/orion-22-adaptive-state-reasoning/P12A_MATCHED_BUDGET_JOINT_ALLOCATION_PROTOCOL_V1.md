# P12A Matched-Budget Joint Allocation Protocol V1

**Paper:** ORION-ORION-22 — Adaptive State–Reasoning Co-Design  
**Issue:** #665; resource owner #664  
**Protocol:** `ORION.P12A.MatchedBudgetAllocation.v1`  
**Frozen:** 2026-08-21 before protected execution.

## Scientific discriminator

At one identical primitive budget, can a frozen policy use pre-outcome signals to choose *where* computation should go—state construction versus downstream reasoning—and outperform policies that may adapt only one axis?

The benchmark is intentionally controlled. A positive terminal establishes joint-allocation value in held-out generated regimes; it is not an LLM or theorem-prover result.

## Resource world

Every item has a hidden resource requirement `(c_req, r_req)` in exactly one of four regimes:

- `EASY = (0,0)`
- `ACCESS = (2,0)`
- `REASON = (0,2)`
- `BOTH = (1,1)`

Every policy has total budget `B=2`. Verified success is exact: `c_alloc >= c_req` and `r_alloc >= r_req`.

The candidate allocation set for a joint policy is `{(2,0),(1,1),(0,2)}` plus `(0,0)` for the easy shortcut. No arm receives more than two units.

## Pre-outcome signals

All adaptive arms receive the same two signals before allocation:

`s_c = c_req + Normal(0, sigma_f)`  
`s_r = r_req + Normal(0, sigma_f)`

Family noise `sigma_f` and regime proportions are generated from fixed development or protected seeds. Signals contain no outcome, verifier result or post-allocation information.

## Policy classes

- `FIXED_11`: always allocate `(1,1)`.
- `ADAPTIVE_STATE_ONLY`: reasoning allocation is fixed at zero; choose `c=2` when `s_c>=1`, else `c=0`.
- `ADAPTIVE_REASON_ONLY`: state allocation is fixed at zero; choose `r=2` when `s_r>=1`, else `r=0`.
- `JOINT_FROZEN`: choose the feasible allocation in `{(0,0),(2,0),(1,1),(0,2)}` with minimum squared Euclidean distance to `(s_c,s_r)`, with deterministic tie order `(0,0),(1,1),(2,0),(0,2)`.
- `ORACLE_JOINT`: exact hindsight allocation if feasible; diagnostic ceiling only.

The joint rule is frozen; there is no protected-outcome training.

## Data split

- Development seed `2026082101`: used only for sanity and no protected claims.
- Protected seed `2026082112`.
- 16 held-out families.
- 512 items per family.
- `sigma_f` spans `[0.30,0.80]`.
- Family regime priors are independently sampled from a symmetric Dirichlet distribution and mixed 50% with the uniform prior so no family collapses to a single regime.

## Primary endpoint

For each held-out family, `verified_success_rate`.

`joint_gain_f = Q_joint_f - max(Q_state_f, Q_reason_f)`.

Headline result:
- mean held-out `joint_gain`;
- family-block 95% bootstrap CI, 20,000 deterministic resamples;
- worst-family `joint_gain`.

## Positive terminal

`P12A_JOINT_ALLOCATION_SUPERIORITY_SUPPORTED` requires all:

1. every allocation respects `c+r<=2`;
2. no signal uses protected outcomes;
3. mean joint gain >= `0.15`;
4. family-block 95% bootstrap lower bound for mean joint gain > `0`;
5. joint success exceeds `FIXED_11` by >= `0.10` on average;
6. worst-family joint gain >= `0.05`;
7. oracle success is >= joint success in every family;
8. two fresh executions are byte-identical.

If any gate fails, the terminal is retained negative.

## Authorized claim

A positive result supports:

> In a preregistered held-out controlled mixture of access-limited, reasoning-limited, joint and easy regimes under an identical two-unit resource budget, one frozen two-axis allocation rule strictly outperforms both one-axis adaptive policies.

Real-system superiority remains a separate gate.

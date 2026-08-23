# ORION-Q N4-E protocol: active discriminating interface-experiment selection

Date frozen: 2026-08-21 (before any result-bearing execution)
Parent issue: #677 (registered successor family 6; registered baselines:
value-of-information / active learning, generic LLM-style agent)
Lane: ORION-Q N4, branch `claude/orion-harness-verification-b17qdj`
Status: FROZEN before outcomes.
Study script: `research/extensions/orion-q/nlanes/n4_e_active_experiments.py`
Results artifact: `research/extensions/orion-q/nlanes/N4_E_ACTIVE_EXPERIMENTS_RESULTS.json`

## Question

When committing to an interface construction plan depends on unknown binary
construction facts that can be checked one at a time at heterogeneous costs,
does ORION decision-coupled experiment selection (choose the fact whose
resolution most improves the COMMIT/ABSTAIN decision per unit cost) beat pure
information-gain active learning, random and cheapest-first orders, and an
LLM-proxy heuristic — when ALL probing arms share the same priors and the SAME
stopping rule, so that only next-experiment SELECTION differs?

Hostile-control requirement: worlds contain decoy facts of maximal entropy
(p ~ 0.5) that no plan depends on. Pure information gain must be attracted to
them; if it is not measurably wasteful there, the control is invalid.

## World (exact synthetic)

- K = 6 unknown binary construction facts per episode. Fact i has typed prior
  `p_i` and probe cost `c_i ~ U[0.2, 1.5]` (deterministic seeded draws).
  Facts 0..3 are LOAD-BEARING with `p_i ~ U[0.25, 0.85]`; facts 4..5 are
  DECOYS with `p_i ~ U[0.45, 0.55]` and appear in no plan clause.
- M = 8 candidate plans. Plan j has cost `~ U[2, 8]` and a feasibility clause:
  a conjunction of 2-3 literals over the load-bearing facts (random signs).
  Truth of each fact drawn from its prior (hidden).
- Decision payoff: committing plan j pays its cost; reward R = 20 if its
  clause is true under the hidden facts, else penalty F = 8 in addition.
  Abstain pays 0. Probe costs always add.
- Episodes: 400 paired worlds. Seed: 20260821. Stdlib RNG. Exact enumeration
  of the 2^u residual fact assignments (u <= 6) for all expected utilities —
  no sampling.

Matched information: every non-oracle arm sees plans, clauses, costs, typed
priors, and its own probe outcomes. SHARED STOPPING RULE for all probing arms:
stop when, under the arm's current beliefs, no single remaining probe has
positive myopic net value for the decision (identical computation for all
arms); then commit the max-expected-utility plan if its EU > 0, else abstain.
Arms differ ONLY in which fact they probe next while probing continues.

## Arms

1. `ORACLE` — sees all facts; commits best truly feasible plan when its net
   utility is positive, else abstains; zero probe cost.
2. `RANDOM_ORDER` — next probe uniformly random among unknown facts.
3. `CHEAPEST_FIRST` — next probe = cheapest unknown fact.
4. `INFOGAIN` — next probe = unknown fact with maximal marginal entropy
   H(p_i) (pure active learning on the fact posterior, cost- and
   decision-blind). Decoys are designed to attract this arm.
5. `ORION_DECISION_VOI` — candidate mechanism: next probe = argmax over
   unknown facts of (expected decision-utility improvement from resolving that
   fact) / cost, computed by exact enumeration.
6. `LLM_PROXY_HEURISTIC` — declared proxy: probes the facts mentioned by the
   cheapest plan's clause (in clause order), then facts of the next-cheapest
   plan, etc. Same stopping rule. Explicitly NOT a claim about any real LLM.

## Prespecified endpoints and gates

Primary endpoint: mean net utility (reward - plan cost - penalty - probe
spend) per arm. Secondary: mean probe spend, mean probe count, commit
accuracy (committed plan actually feasible), regret vs oracle, decoy probe
rate per arm.

- G1 (sanity): `ORACLE` mean utility >= all arms.
- G2 (vs pure active learning): `ORION_DECISION_VOI` mean utility >
  `INFOGAIN`, strictly.
- G3 (vs order controls): `ORION_DECISION_VOI` mean utility > `RANDOM_ORDER`
  and > `CHEAPEST_FIRST`, strictly.
- G4 (vs proxy): `ORION_DECISION_VOI` mean utility > `LLM_PROXY_HEURISTIC`,
  strictly.
- G5 (decoy hostile control): `INFOGAIN` decoy probe rate >
  `ORION_DECISION_VOI` decoy probe rate, and `INFOGAIN` decoy probe rate >=
  0.10 (decoys must actually attract the entropy criterion; else the control
  is invalid).
- G6 (determinism): double run, byte-identical receipt line.

## Terminal vocabulary

- Positive: `N4_E_DECISION_COUPLED_SELECTION_SUPPORTED__EXACT_SYNTHETIC`.
- Negative: `N4_E_DECISION_COUPLED_SELECTION_NO_ADVANTAGE` (G2, G3, or G4
  fails honestly).
- Invalid: `N4_E_WORLD_INVALID` (G1 or G5 fails).
- `CANNOT_CHECK` on runtime failure.

## Determinism and authority

Frozen seed; exact enumeration over residual assignments; shared stopping rule
isolates selection quality. Authority: `exact-synthetic-bounded; no
real-quantum, no P10, no novelty, no LLM-capability claims; LLM_PROXY is a
fixed heuristic, not an LLM measurement`.

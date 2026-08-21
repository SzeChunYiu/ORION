# ORION-Q N4-A protocol: UNKNOWN interface feasibility + value-of-information probing

Date frozen: 2026-08-21 (before any result-bearing execution)
Parent issue: #677 (registered successor family 1)
Lane: ORION-Q N4, branch `claude/orion-harness-verification-b17qdj`
Status: FROZEN before outcomes.
Study script (to be written after this freeze): `research/extensions/orion-q/nlanes/n4_a_unknown_voi.py`
Results artifact: `research/extensions/orion-q/nlanes/N4_A_UNKNOWN_VOI_RESULTS.json`

## Question

On an exact synthetic interface derivation graph where some edge feasibilities are
UNKNOWN and can be resolved only by costly probes, does a typed ORION interface
state (type-conditioned feasibility provenance driving value-of-information
probing and a principled abstain) improve net decision utility over
donor-complete graph optimization on the known subgraph, over a pure
uniform-prior VOI planner, and over blind-commit and LLM-proxy controls —
under matched visible information?

H0 boundary retained from #677: with fully known feasibility/costs the problem
is classically closed (`FULLY_KNOWN_GRAPH_CLASSICALLY_CLOSED`). This family
tests only the partial-knowledge regime.

## World (exact synthetic)

- Layered DAG: source `s`, 4 layers of width 3, sink `t`; complete bipartite
  edges between consecutive layers. All 81 s-t paths enumerated exhaustively.
- Each edge: cost `c ~ U[1,5]` (deterministic seeded draw), type
  `tau in {T0,T1,T2}` (uniform), feasibility truth drawn per type:
  `p_feas = {T0: 0.90, T1: 0.50, T2: 0.15}`.
- Knowledge mask: each edge is KNOWN with probability 0.55 (truth revealed);
  otherwise UNKNOWN (truth hidden from all non-oracle arms).
- Actions: `probe(edge)` at cost 0.4 reveals that edge's truth;
  `commit(path)`; `abstain`.
- Payoff: commit pays full path cost; if all path edges feasible, reward
  R = 20; else failure penalty F = 8 in addition to path cost. Abstain pays
  only probes already spent.
- Episodes: 300 paired worlds (all arms see the identical world).
- Seed: 20260821. Generator: python stdlib `random.Random`.

Matched information rule: every non-oracle arm sees the graph, edge costs,
edge types, known feasibilities, and the generator's type-conditional
feasibility rates as declared typed facts. Arms differ only in whether and how
they use them. No arm sees hidden truths except via probes it pays for.

## Arms

1. `FULL_ORACLE` — sees all truths; commits cheapest feasible path when net
   utility positive, else abstains. Upper bound; strongest baseline holds
   first right of refusal on any headroom claim.
2. `GREEDY_KNOWN_GRAPH` — donor-complete exact optimization on the known
   subgraph: UNKNOWN treated as infeasible; commit cheapest all-known-feasible
   path if utility positive, else abstain. (Registered baseline: exact graph
   oracle on known subgraph.)
3. `OPTIMIST_COMMIT` — hostile control: UNKNOWN treated as feasible, commits
   cheapest path, never probes.
4. `PURE_VOI_UNIFORM` — myopic VOI probing with uniform prior 0.5 on every
   UNKNOWN edge (ignores types), commit/abstain by expected utility.
   (Registered baseline: value-of-information planner.)
5. `ORION_TYPED_VOI` — candidate mechanism: identical myopic VOI machinery but
   with type-conditioned priors from typed interface provenance; probes while
   myopic net VOI > 0; commits when best expected utility > 0, else abstains.
6. `LLM_PROXY_HEURISTIC` — declared proxy for a generic label-level agent with
   the same visible state: avoids known-infeasible edges, treats UNKNOWN edges
   as feasible with a flat 1.2x cost markup, never probes, commits cheapest
   marked-up path if positive. Explicitly NOT a claim about any real LLM.

Expected utility of a path under beliefs: `P(all unknown edges feasible) * R -
path_cost - (1 - P) * F`. Myopic probe VOI: expected posterior best-path EU
minus current best-path EU minus probe cost; probe argmax while positive.

## Prespecified endpoints and gates

Primary endpoint: mean net utility per arm over the 300 paired episodes.
Secondary: success rate, abstain rate, mean probe spend, regret vs oracle.

- G1 (sanity): `FULL_ORACLE` mean utility >= every other arm.
- G2 (vs strongest partial-info graph baseline): `ORION_TYPED_VOI` mean
  utility > `GREEDY_KNOWN_GRAPH`, strictly.
- G3 (value of typing): `ORION_TYPED_VOI` mean utility > `PURE_VOI_UNIFORM`,
  strictly.
- G4 (hostile control validity): `OPTIMIST_COMMIT` mean utility <
  `ORION_TYPED_VOI` and < `GREEDY_KNOWN_GRAPH` (blind commitment must be
  punished; if not, the world is too easy and the run is invalid, not
  positive).
- G5 (proxy non-vacuity): `ORION_TYPED_VOI` > `LLM_PROXY_HEURISTIC`.
- G6 (determinism): two invocations with the frozen seed produce byte-identical
  receipt lines (checked externally by double run and diff).

## Terminal vocabulary

- Positive: `N4_A_TYPED_VOI_SUPPORTED__EXACT_SYNTHETIC` (all gates pass).
- Negative: `N4_A_TYPED_VOI_NO_ADVANTAGE` (G2 or G3 fails honestly).
- Invalid: `N4_A_WORLD_INVALID` (G1 or G4 fails).
- `CANNOT_CHECK` on runtime failure.

Honest negatives are valid lane outcomes and are reported as such.

## Determinism and authority

Single frozen seed, stdlib RNG, exhaustive path enumeration, no wall-clock,
no environment-dependent input. Authority string in receipt:
`exact-synthetic-bounded; no real-quantum, no P10, no novelty, no LLM-capability
claims; LLM_PROXY is a fixed heuristic, not an LLM measurement`.

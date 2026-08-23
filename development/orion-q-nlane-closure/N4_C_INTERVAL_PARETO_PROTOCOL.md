# ORION-Q N4-C protocol: interval-cost Pareto regret vs clairvoyant oracle

Date frozen: 2026-08-21 (before any result-bearing execution)
Parent issue: #677 (registered successor family 4; registered baselines: exact
graph/Pareto oracle, robust shortest path under uncertain edges)
Lane: ORION-Q N4, branch `claude/orion-harness-verification-b17qdj`
Status: FROZEN before outcomes.
Study script: `research/extensions/orion-q/nlanes/n4_c_interval_pareto.py`
Results artifact: `research/extensions/orion-q/nlanes/N4_C_INTERVAL_PARETO_RESULTS.json`

## Question

With interval-valued edge costs and error bounds on an exact interface graph
and a small edge-verification budget, does ORION interval-dominance Pareto
pruning with VERIFICATION TARGETED at Pareto-ambiguous edges achieve lower
scalarized regret against a clairvoyant Pareto oracle than midpoint
optimization, worst-case robust optimization, best-case optimization, and
untargeted (random) verification with the same budget?

## World (exact synthetic)

- Layered DAG: source, 3 layers of width 3, sink; 24 edges, 27 s-t paths,
  enumerated exhaustively.
- Each edge has two objectives, cost and error bound. Per edge and objective an
  interval is generated: center `~ U[1,5]`; half-width `h`: with probability
  0.3 the edge is WIDE (`h ~ U[1.0, 2.5]`), else TIGHT (`h ~ U[0.05, 0.3]`).
  Truth is a deterministic seeded uniform draw within the interval. Intervals
  clipped at 0.05 minimum.
- Path objectives = sums over edges. Scalarization weight `w ~ U[0.2, 0.8]`
  per episode (deterministic draw, visible to all arms).
- Verification budget: B = 4 edge-verifications per episode. Verifying an edge
  reveals both true objective values.
- Per-episode regret of an arm = scalarized TRUE value of its chosen path
  minus the clairvoyant optimum `min_path (w*cost_true + (1-w)*err_true)`.
- Episodes: 400 paired worlds. Seed: 20260821. Stdlib RNG.

Matched information: all non-oracle arms see all intervals and `w`; only
verification (within the same budget B) reveals truths.

## Arms

1. `CLAIRVOYANT_ORACLE` — true values; regret identically 0 by construction
   (used as the reference; also a sanity check on the regret computation).
2. `MIDPOINT_OPTIMIZER` — scalarized shortest path on interval midpoints, no
   verification (registered known-subgraph exact-optimizer analogue).
3. `ROBUST_WORSTCASE` — scalarized shortest path on interval upper endpoints
   (registered robust-shortest-path baseline).
4. `BEST_CASE` — scalarized shortest path on interval lower endpoints
   (optimist control).
5. `RANDOM_VERIFY_MIDPOINT` — spends B verifications on uniformly random
   distinct edges, then midpoint-optimizes with verified truths substituted
   (control isolating the value of TARGETING, not of verification volume).
6. `ORION_INTERVAL_PARETO` — candidate mechanism:
   a. compute the set of paths not interval-dominated (path A dominates B iff
      A's upper endpoints <= B's lower endpoints in both objectives, strict in
      one);
   b. rank edges by (interval width summed over objectives) x (number of
      surviving ambiguous paths the edge appears in, counted only where the
      edge is not shared by all survivors);
   c. verify the top-B ranked edges;
   d. choose the scalarized-minimum path using verified truths plus midpoints
      for unverified edges.

## Prespecified endpoints and gates

Primary endpoint: mean scalarized regret per arm.
Secondary: median regret, fraction of episodes with zero regret, mean number
of interval-dominance survivors.

- G1 (sanity): `CLAIRVOYANT_ORACLE` mean regret == 0 exactly.
- G2 (vs no-verification optimizers): `ORION_INTERVAL_PARETO` mean regret <
  `MIDPOINT_OPTIMIZER`, < `ROBUST_WORSTCASE`, and < `BEST_CASE`, strictly.
- G3 (targeting value): `ORION_INTERVAL_PARETO` mean regret <
  `RANDOM_VERIFY_MIDPOINT`, strictly (same budget, so the difference is
  attributable to targeting).
- G4 (non-degeneracy): mean interval-dominance survivor count > 1 (else the
  world never poses an ambiguous choice and the run is invalid).
- G5 (determinism): double run, byte-identical receipt line.

## Terminal vocabulary

- Positive: `N4_C_TARGETED_INTERVAL_PARETO_SUPPORTED__EXACT_SYNTHETIC`.
- Negative: `N4_C_TARGETED_VERIFICATION_NO_ADVANTAGE` (G2 or G3 fails
  honestly).
- Invalid: `N4_C_WORLD_INVALID` (G1 or G4 fails).
- `CANNOT_CHECK` on runtime failure.

## Determinism and authority

Frozen seed, exhaustive 27-path evaluation, no sampling estimators in the
decision path. Authority: `exact-synthetic-bounded; no real-quantum, no P10,
no novelty claims; regret is scalarized (not full Pareto-front hypervolume),
recorded as a scope limit`.

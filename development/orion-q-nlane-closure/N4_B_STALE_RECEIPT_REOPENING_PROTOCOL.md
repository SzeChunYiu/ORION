# ORION-Q N4-B protocol: stale failure receipts on the interface graph — scoped reopening

Date frozen: 2026-08-21 (before any result-bearing execution)
Parent issue: #677 (registered successor family 2; raw/unscoped failure-memory
baseline registered in the issue ladder)
Lane: ORION-Q N4, branch `claude/orion-harness-verification-b17qdj`
Status: FROZEN before outcomes.
Study script: `research/extensions/orion-q/nlanes/n4_b_stale_receipt_reopening.py`
Results artifact: `research/extensions/orion-q/nlanes/N4_B_STALE_RECEIPT_REOPENING_RESULTS.json`

## Question

When interface-graph edges carry failure receipts scoped to context coordinates
(representation version, access contract), does ORION scoped reopening — reopen
a receipt only when a coordinate inside its recorded scope changed — beat
never-reopen, always-reopen, and raw unscoped-change reopening, in worlds where
BOTH staleness and wasteful reopening occur? A world regime where reopening is
wasteful MUST NOT reward always-reopen; if it does, the run is invalid.

This transfers the MAX-R0 scoped-history mechanic (validated domain-neutrally)
onto the registered interface-graph partial-information problem, which the #677
audit found unexecuted.

## World (exact synthetic)

- Layered DAG: source, 3 layers of width 3, sink; 27 s-t paths, 24 edges,
  enumerated exhaustively.
- Context coordinates per episode: `REP` version, `ACCESS` version, and an
  irrelevant `NOISE` coordinate.
- Initial receipts: each edge independently carries a failure receipt with
  probability 0.45; each receipt has scope drawn from {`{REP}`, `{ACCESS}`,
  `{REP,ACCESS}`} with probabilities 0.4/0.4/0.2.
- Truth model: a receipted edge is infeasible until the FIRST change of any
  coordinate in its scope after receipt time; from then on it is feasible with
  recovery probability 0.85 (one deterministic seeded draw per edge).
  Changes to coordinates outside the scope (including `NOISE`) never affect
  truth. Unreceipted edges are feasible with probability 0.95 (one draw).
- Rounds: T = 6 per episode. Per-round coordinate flip probabilities depend on
  regime:
  - Regime `STALE_MATTERS`: P(REP flip) = 0.30, P(ACCESS flip) = 0.20,
    P(NOISE flip) = 0.50.
  - Regime `REOPEN_WASTEFUL` (hostile): P(REP flip) = 0.02,
    P(ACCESS flip) = 0.02, P(NOISE flip) = 0.60.
- Per round the arm picks the cheapest path among edges it considers
  available, or abstains if none. Attempt payoff: success R = 20 - path cost;
  failure -path cost - F with F = 8. Abstain 0.
- Episodes: 200 per regime (400 total), all arms paired on identical worlds.
- Seed: 20260821. Arms do not accrue new receipts intra-episode (initial
  receipts only); this restriction is recorded as a scope limit.

Matched information: all non-oracle arms see the graph, costs, the receipts
(edge + scope + time), and the full coordinate-change history. They differ only
in the reopening rule applied to the same facts.

## Arms

1. `ORACLE_AVAILABILITY` — sees true current feasibility of every edge.
2. `NEVER_REOPEN` — receipted edges permanently excluded (registered control).
3. `ALWAYS_REOPEN` — receipts ignored entirely (registered control).
4. `UNSCOPED_CHANGE_REOPEN` — raw failure memory: reopens ALL receipts when
   ANY coordinate (including `NOISE`) has changed since receipt (registered
   baseline: raw/unscoped failure memory).
5. `ORION_SCOPED_REOPEN` — candidate mechanism: reopen a receipt iff a
   coordinate in its recorded scope changed since the receipt.

Reopened edges are treated as available (belief); truth decides the outcome.

## Prespecified endpoints and gates

Primary endpoint: mean per-round net utility per arm, per regime and pooled.
Secondary: failure-attempt rate (attempts hitting an infeasible edge), abstain
rate, regret vs oracle.

- G1 (sanity): `ORACLE_AVAILABILITY` >= all arms, pooled and per regime.
- G2 (pooled advantage): `ORION_SCOPED_REOPEN` pooled mean utility strictly
  exceeds each of `NEVER_REOPEN`, `ALWAYS_REOPEN`, `UNSCOPED_CHANGE_REOPEN`.
- G3 (hostile regime validity): in `REOPEN_WASTEFUL`,
  `ALWAYS_REOPEN` mean utility < `NEVER_REOPEN` mean utility (wasteful
  reopening must be punished; otherwise the world is invalid, not positive).
- G4 (no per-regime giveback): in EACH regime, `ORION_SCOPED_REOPEN` mean
  utility >= max(`NEVER_REOPEN`, `ALWAYS_REOPEN`) - 0.25 (tolerance
  prespecified in utility units).
- G5 (determinism): double run, byte-identical receipt line.

## Terminal vocabulary

- Positive: `N4_B_SCOPED_REOPENING_SUPPORTED__EXACT_SYNTHETIC` (all gates).
- Negative: `N4_B_SCOPED_REOPENING_NO_ADVANTAGE` (G2 or G4 fails honestly).
- Invalid: `N4_B_WORLD_INVALID` (G1 or G3 fails).
- `CANNOT_CHECK` on runtime failure.

## Determinism and authority

Frozen seed, stdlib RNG, exhaustive path sets, no wall-clock. Authority:
`exact-synthetic-bounded; no real-quantum, no P10, no novelty claims; initial
receipts only (no intra-episode receipt accrual) is a recorded scope limit`.

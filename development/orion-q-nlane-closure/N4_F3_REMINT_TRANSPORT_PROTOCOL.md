# ORION-Q N4-F3 protocol: representation remints and receipt transport as a standalone mechanism

Date frozen: 2026-08-21 (before any result-bearing execution)
Parent issue: #677 (registered successor family 3: "Representation edits that
remint graph nodes/edges and require transport/reverification")
Residual being closed: `N4_CLOSURE_ASSESSMENT.md` residual 1 — family 3 was
exercised only as the laundering vector inside N4-D (family 5), never
independently closed.
Lane: ORION-Q N4, branch `claude/orion-harness-verification-b17qdj`
Status: FROZEN before outcomes.
Study script: `research/extensions/orion-q/nlanes/n4_f3_remint_transport.py`
Results artifact: `research/extensions/orion-q/nlanes/N4_F3_REMINT_TRANSPORT_RESULTS.json`

## Question

When a representation-frame edit remints interface-graph nodes/edges — every
derivability receipt minted under the old frame must either be TRANSPORTED
(re-bound under the new frame by a registered, typed transport rule) or
INVALIDATED and re-derived under a verification budget — does typed
remint/transport that (i) preserves obligation bindings and (ii) correctly
invalidates non-transportable receipts beat re-derivation-from-scratch at a
MATCHED remint budget, in worlds where transport genuinely preserves
certificates? And do the two hostile controls hold: naive carry-forward (no
invalidation) must be punished in a world where it silently keeps stale
validity, and in a world where remint machinery buys nothing (the edit touches
no bound aspect) the re-derivation baseline must win first refusal or tie —
any ORION advantage there means the advantage is not attributable to typed
transport and the run is invalid.

This is the standalone closure of registered family 3: remint/transport as a
mechanism in its own right, not as N4-D's attack vector.

## World (exact synthetic)

Interface derivation graph identical in shape to N4-B: source `s`, 3 layers of
width 3, sink `t`; 24 edges, 27 s-t paths, enumerated exhaustively.

- Edge fields (drawn once per episode, seeded): `cost` uniform(1.0, 5.0);
  `edge_type` uniform over {`A`, `B`, `C`}.
- Frame aspects: `ENCODING`, `LAYOUT`, `SCHEDULE`, `CALIBRATION` (bindable),
  plus `COSMETIC` (never bindable; exists so an edit can be genuinely
  irrelevant).
- Receipts: EVERY edge starts with a valid derivability receipt minted under
  frame F0. Each receipt carries an obligation binding: a set of bindable
  aspects it depends on (size drawn per regime, uniform over the 4 bindable
  aspects without replacement).
- Registered transport rules (fixed world constant, visible to all arms):
  `RULES = {(LAYOUT,A), (LAYOUT,B), (SCHEDULE,A), (SCHEDULE,C),
  (CALIBRATION,B)}` — a rewrite for aspect X on an edge of type Y exists iff
  `(X, Y)` is in RULES. `ENCODING` has no rules (never transportable when
  bound and changed).
- Frame edits: K = 2 sequential edits per episode. Each edit changes a set of
  aspects (regime-dependent, drawn seeded). Receipt transport is SEQUENTIAL:
  a receipt survives edit k iff every changed aspect that is in its binding
  has a rule for its edge type; the binding is preserved unchanged across a
  successful transport (obligation-binding preservation). A receipt that fails
  any edit is invalid permanently.
- Ground truth (enumerable by construction):
  - transportable receipt => edge remains feasible under the final frame
    (transport rules are sound in this world by construction; recorded scope
    limit, mirroring N4-D's receipt-forgery exclusion);
  - non-transportable receipt => edge is independently feasible under the new
    frame with probability `1 - p_break` (one seeded draw per edge).
- Remint (re-verification): an arm may spend 1 unit of budget to remint an
  edge, revealing its true post-edit feasibility. Budget B = 6 remints per
  episode, HARD cap, identical for all budgeted arms. Remints consume budget
  only, not utility (recorded scope limit).
- Decision: after the edits, one shot — commit a path or abstain.
  Commit payoff: success `R - path_cost` with R = 20; failure
  `-path_cost - F` with F = 8. Abstain 0. Max path cost is 20, so the oracle
  is never negative.

### Regimes (200 episodes each; all arms paired on identical worlds)

1. `MIXED_TRANSPORT` (primary): binding size 1-2; each edit changes 1-2
   bindable aspects; `p_break = 0.55`. A material fraction of receipts
   transports; typed transport should stretch the matched budget further than
   re-derivation.
2. `STALE_HOSTILE` (hostile control 1): binding size 2-3; each edit changes
   2-3 bindable aspects; `p_break = 0.85`. Carry-forward silently keeps stale
   validity and MUST be punished by the world; if it is not, the world is
   invalid, not the mechanism supported.
3. `REMINT_UNNECESSARY` (hostile control 2): binding size 1-2; both edits
   change only `{COSMETIC}`, which no receipt can bind. Every receipt
   transports trivially and every edge stays feasible. Typed transport has
   nothing to add here; re-derivation at matched budget must win first refusal
   or tie. Any strict ORION advantage in this regime invalidates the run.

Matched information: all non-oracle arms see the graph, costs, edge types, all
receipts with their obligation bindings, the full edit history, and the RULES
table. They differ ONLY in the validity rule applied to the same facts and in
whether they use receipts at all. Budgets are identical.

## Arms

1. `FULL_ORACLE` — sees true post-edit feasibility of every edge; commits the
   min-cost truly feasible path, abstains iff none exists.
2. `ORION_TYPED_TRANSPORT` — candidate mechanism: applies the typed transport
   relation to every receipt (sequential over edits, binding-preserving);
   transported receipts are treated as valid; non-transportable receipts are
   marked INVALID (typed invalidation, never silent carry-forward); spends the
   remint budget under the shared certification policy below on invalidated
   edges only.
3. `RE_DERIVE_SCRATCH` — strongest matched-budget baseline (first right of
   refusal): discards ALL pre-edit receipts (treats every edge as unverified),
   spends the SAME budget B under the SAME certification policy.
4. `NAIVE_CARRY_FORWARD` — no invalidation: treats every pre-edit receipt as
   still valid regardless of the edits; under the shared policy it certifies
   the cheapest path with zero remints and commits it (silent stale validity).

Shared certification policy (identical code path for arms 2-4): iterate the 27
paths in ascending (cost, path-index) order; skip any path containing an edge
already reminted infeasible; let U = its edges neither believed-valid (by the
arm's validity rule) nor already reminted; if |U| exceeds remaining budget,
skip; otherwise remint U one edge at a time (spending budget), aborting the
path on the first infeasible result (spent budget stays spent, knowledge
persists); commit the first fully certified path; abstain if none certifies.
Commit requires full certification — no gambling arm is included, by design;
NAIVE's "certification" is vacuous, which is exactly the mechanism under test.

## Prespecified endpoints and gates

Primary endpoint: mean episode utility per arm, per regime and pooled.
Secondary: failure rate (committed path infeasible), abstain rate, mean
remints spent, regret vs `FULL_ORACLE`, mean transportable-receipt fraction
per regime, and ORION invalidation mismatches vs ground-truth transportability
(count over all receipts in all episodes).

- G1 (sanity, oracle upper bound): `FULL_ORACLE` mean utility >= every arm,
  in each regime and pooled.
- G2 (primary, typed-transport advantage in `MIXED_TRANSPORT`):
  `ORION_TYPED_TRANSPORT` mean utility strictly > `RE_DERIVE_SCRATCH` AND
  strictly > `NAIVE_CARRY_FORWARD`.
- G3 (hostile control 1 validity, `STALE_HOSTILE`): `NAIVE_CARRY_FORWARD`
  mean utility < 0 AND its failure rate >= 0.5 AND its mean utility <
  `RE_DERIVE_SCRATCH`'s. Stale validity must be caught (punished) by the
  world; otherwise the world is invalid.
- G4 (hostile control 2, first right of refusal in `REMINT_UNNECESSARY`):
  `RE_DERIVE_SCRATCH` mean utility >= `ORION_TYPED_TRANSPORT` mean utility
  - 1e-9 (win or tie; tolerance is float-noise only, prespecified).
- G5 (typed-invalidation soundness, all regimes): `ORION_TYPED_TRANSPORT`
  commits zero infeasible paths (failure count == 0) AND its per-receipt
  valid/invalid classification matches ground-truth transportability exactly
  (mismatch count == 0).
- G6 (determinism): double run, byte-identical receipt line (verified
  externally).

## Terminal vocabulary

- Positive: `N4_F3_TYPED_REMINT_TRANSPORT_SUPPORTED__EXACT_SYNTHETIC`
  (G1-G5 all true).
- Negative: `N4_F3_TYPED_REMINT_TRANSPORT_NO_ADVANTAGE` (G2 fails honestly
  while G1/G3/G4 hold — re-derivation matched the mechanism at budget).
- Negative: `N4_F3_TYPED_TRANSPORT_UNSOUND` (G5 fails — the mechanism itself
  mis-transported or committed an infeasible path).
- Invalid: `N4_F3_WORLD_INVALID` (G1, G3, or G4 fails — the construction, not
  the mechanism, is at fault; no positive claim may be made).
- `CANNOT_CHECK` on runtime failure.

An honest negative is a valid closure of the residual; only WORLD_INVALID and
CANNOT_CHECK leave family 3 open.

## Determinism and authority

Seed 20260821 (lane constant), stdlib RNG for all draws; numpy permitted for
aggregation only; exhaustive path enumeration; no wall-clock dependence;
single stdout receipt line `ORIONQ_N4_F3_REMINT_TRANSPORT=<canonical sorted
json>` followed by the pretty results JSON, which is also written to the
results artifact.

Authority: `exact-synthetic-bounded; no real-quantum, no P10, no novelty
claims; transport-rule soundness is by construction (recorded scope limit,
as in N4-D); remints consume budget only, not utility (recorded scope limit);
no claim about real representation migrations or real LLMs`.

# ORION-Q N4 lane closure assessment (issue #677)

Date: 2026-08-21
Branch: `claude/orion-harness-verification-b17qdj`
Author context: cross-agent lane execution following the audit comment on #677
(which found zero executions of the registered successor families).
Authority of this document: exact-synthetic-bounded receipts only. No P10,
no novelty, no real-quantum, no LLM-capability claims.

## Execution order and freeze discipline

1. Protocol docs frozen FIRST (this directory, before any script existed):
   - `N4_A_UNKNOWN_VOI_PROTOCOL.md`
   - `N4_B_STALE_RECEIPT_REOPENING_PROTOCOL.md`
   - `N4_C_INTERVAL_PARETO_PROTOCOL.md`
   - `N4_D_LAUNDERING_DETECTION_PROTOCOL.md`
   - `N4_E_ACTIVE_EXPERIMENTS_PROTOCOL.md`
2. Studies implemented at `research/extensions/orion-q/nlanes/n4_*.py`
   (stdlib only, frozen seed 20260821, exhaustive/exact computation).
3. Each study run twice with the same interpreter; receipt lines compared
   byte-for-byte (determinism gates G5/G6 verified externally). All exit 0.

Post-freeze code deviation log (full disclosure): `n4_c_interval_pareto.py`
initially crashed with a `TypeError` in a sort tie-break (mixed str/tuple edge
ids). Fix: tie-break key changed to `repr(edge_id)`. This is a type-safety
repair of the frozen tie-break rule ("break ties by edge id"), made before any
N4-C outcome was observed (the run had crashed); no world, arm, endpoint, or
gate was altered.

## Family results (exact numbers from the frozen-seed runs)

### N4-A — UNKNOWN feasibility + VOI probing (registered family 1)
Terminal: `N4_A_TYPED_VOI_SUPPORTED__EXACT_SYNTHETIC`. Gates G1-G5 all true.
Mean utility (300 paired episodes): FULL_ORACLE 4.612; ORION_TYPED_VOI 3.291
(regret 1.32); PURE_VOI_UNIFORM 2.180; GREEDY_KNOWN_GRAPH 0.358;
LLM_PROXY -12.306; OPTIMIST_COMMIT -13.619. Donor-complete optimization on
the known subgraph abstains 93.3% of the time and captures almost none of the
oracle's value; typed-prior VOI recovers 71% of oracle utility with 1.39
probes/episode. Blind commitment is heavily punished (hostile control valid).

### N4-B — stale failure receipts, scoped reopening (registered family 2)
Terminal: `N4_B_SCOPED_REOPENING_SUPPORTED__EXACT_SYNTHETIC`. Gates G1-G4 true.
Pooled mean round utility (400 episodes x 6 rounds): ORACLE 8.297;
ORION_SCOPED 3.199; NEVER_REOPEN 2.782; UNSCOPED_CHANGE_REOPEN -7.813;
ALWAYS_REOPEN -9.225. Per regime: STALE_MATTERS — ORION 2.870 > NEVER 2.096,
ALWAYS -5.044; REOPEN_WASTEFUL (hostile) — ALWAYS -13.406 < NEVER 3.468
(wasteful reopening punished as required), ORION 3.528 >= best control.
Raw unscoped change-reopening is catastrophic because the NOISE coordinate
flips constantly; scope binding is the load-bearing ingredient.

### N4-C — interval-cost Pareto regret (registered family 4)
Terminal: `N4_C_TARGETED_INTERVAL_PARETO_SUPPORTED__EXACT_SYNTHETIC`.
Gates G1-G4 true. Mean scalarized regret (400 episodes, budget B=4):
ORACLE 0.0 (exact); ORION_INTERVAL_PARETO 0.1096 (76.5% zero-regret);
RANDOM_VERIFY_MIDPOINT 0.2518; MIDPOINT 0.2621; ROBUST_WORSTCASE 0.7755;
BEST_CASE 1.2679. Same verification budget, so ORION's 2.3x regret reduction
vs random verification is attributable to Pareto-ambiguity targeting. Mean
interval-dominance survivor count 23.12 of 27 paths (world genuinely
ambiguous).

### N4-D — stronger-oracle laundering detection (registered family 5;
family 3 remints exercised as the laundering vector)
Terminal: `N4_D_CHAIN_TRANSPORT_LAUNDERING_DETECTION_SUPPORTED__EXACT_SYNTHETIC`.
Gates G1-G4 true. 400 chains (200 honest; 66 MISSING_RECEIPT, 66
SPOOFED_SUMMARY, 68 DEEP_SPLICE). ORION_CHAIN_TRANSPORT: recall 1.000 on every
class including all 68 deep splices, FPR 0.000 (mandatory hard gate).
LABEL_MATCH recall 0.000 (all laundering label-matches by construction);
SUMMARY_TIER recall 0.000 (summary spoof fully effective); LAST_HOP_CHECK
recall 0.085 overall and 0.000 on DEEP_SPLICE (splices genuinely evade local
checking). Claim bounded to worlds where per-hop receipts cannot be forged
consistently end-to-end; no cryptographic claim.

### N4-E — active discriminating experiment selection (registered family 6)
Terminal: `N4_E_DECISION_COUPLED_SELECTION_SUPPORTED__EXACT_SYNTHETIC`.
Gates G1-G5 true. Mean net utility (400 episodes, shared stopping rule,
selection-only difference): ORACLE 12.054; ORION_DECISION_VOI 9.266
(2.71 probes/ep, decoy fraction 0.000); LLM_PROXY 8.989; CHEAPEST_FIRST 8.075;
RANDOM_ORDER 7.568; INFOGAIN 7.121 (decoy fraction 0.366 — the max-entropy
decoys attract pure information gain exactly as the hostile control requires).
All arms reach commit accuracy 1.0 under the shared stopping rule; the entire
spread is probe-spend efficiency, i.e. experiment SELECTION quality.

## Assessment against #677's stop rule

The issue's stop rule: a FINAL NEGATIVE requires a lower bound/impossibility
for the registered partial-information problem, or saturation across >= 3
materially different uncertainty/remint/query successor families.
`FULLY_KNOWN_GRAPH_CLASSICALLY_CLOSED` is only the H0 boundary.

Receipt status now in-repo:

- Five of the six registered successor families have executed, frozen-protocol,
  deterministic receipts (families 1, 2, 4, 5, 6). This exceeds the >= 3
  materially-different-families threshold.
- The executed evidence does NOT support extending the classical negative to
  the partial-information setting: in every executed family, typed/scoped
  ORION interface state (typed feasibility provenance, scope-bound failure
  receipts, interval-dominance-targeted verification, full-chain transport
  certificates, decision-coupled experiment selection) strictly improved on
  the strongest matched-information baselines, within exact-synthetic scope.
- Therefore the lane's stop condition is receipt-satisfied in the POSITIVE
  direction: the recursive research question resolves "yes, on these
  constructions", and no final-negative terminal is available or claimed.
  The H0 boundary result is retained untouched.

## Residuals (explicitly open; no closure claimed for these)

1. Family 3 (representation remints/transport) was exercised only as the
   laundering vector in N4-D, not independently closed.
2. The registered "generic LLM with same state/tools" baseline was executed
   only as declared deterministic proxies; no claim about real LLMs.
3. The registered "P10 interface edit only after a certified residual"
   baseline rung was not executed.
4. All results are exact-synthetic on frozen constructions; no lower bound or
   impossibility theorem was produced, and none is claimed.
5. N4-B excludes intra-episode receipt accrual (recorded scope limit).

Recommended issue action (for a human/owner, not asserted by this document):
post the five receipts to #677, mark families 1/2/4/5/6 executed with positive
recovery, and either schedule family 3 standalone plus the P10-edit baseline
rung, or absorb those residuals into #679.

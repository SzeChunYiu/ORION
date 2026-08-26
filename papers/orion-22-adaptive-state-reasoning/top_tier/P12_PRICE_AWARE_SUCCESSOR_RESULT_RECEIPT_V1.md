# ORION-22 price-aware successor V1 — result receipt (NR-13 revival)

**Study:** `P12_PRICE_AWARE_SUCCESSOR_V1`
**Lane:** NR-13 (negative-revival backlog)
**Terminal:** `P12_PRICE_AWARE_SUCCESSOR_SUPPORTED` (SC1–SC6 all green, both axes repaired under the original battery's own verdict logic)
**Branch:** `revive/p12-price-aware-nr13`
**Pre-registration:** `P12_PRICE_AWARE_SUCCESSOR_PROTOCOL_PREREG_V1.json` committed and pushed at `44d97948f53046e0a9a4d467e129f509d2a4e49e` — **before the successor selector existed** (commit adds the prereg only; selector, runner, checker and audit are added afterwards).

## Negative being revived

`P12_ROBUSTNESS_STRESS_RESULT_RECEIPT_V1` (PR #1006, CI run `32672856998`):
`price_axis=BROKEN` (zero-regret regime list empty over all 36 case records) and
`distribution_shift_axis=BROKEN` (B1/B2 mixes fail), while V1 FLAT zero-regret
replicates and the hidden-parameterization audit is GREEN.

**One-stage attribution (pre-registered):** the failure stage is the **selection
rule** (frozen greedy-by-q), not the arithmetic (RG1 exactness green everywhere).
The frozen rule optimizes a FLAT-charged proxy — rank by pending multiplicity q,
greedy budget packing in that order — and is blind to (a) the price vector the
runner charges and (b) the per-structure serve-charge exchange rate it is
amortizing. Decomposition of all 45 positive cells (frozen BEFORE diagnosis,
recorded in the prereg): 13 cells materialize at least one unprofitable
structure; the other 32 leave out at least one profitable structure via the tau
gate (q=3 shapes), the q-ranking (T6/T9 races), or greedy mispacking among
profitable structures (SAT_T3 CMP4X: rule packs S3A+S3B=46, oracle packs
S3B+S3C=500). Zero cells implicate any other stage. Per-query exchange-rate
heterogeneity (sigma/declared varies ~5–8x within each domain, domains overlap)
makes profitability NOT a function of `(q, declared, price)` — no threshold on
that surface can repair it without pool-fitting, which is why the lever widens
the readable surface instead of re-tuning.

## Successor (pre-registered, 0 new free parameters)

`P12_PRICE_AWARE_ALLOCATOR_V1`: exact budgeted argmin of the SAME objective the
charging environment charges, on the charger's published ledger — per structure
`s`, `d[s] = p_build*declared[s] - p_serve*(reason_cert[s] - state_cert[s])`;
select the S1-budget-feasible subset (sum declared ≤ 500) maximizing total
saving; solved exactly as 0/1 knapsack by DP over integer declared weights;
ties prefer not-taking; eligibility = the sign of `d[s]` itself (the frozen
tau=4 gate is NOT carried). Readable surface (and nothing else): `sid`,
`declared_cost`, `reason_serve_certificate`, `state_serve_certificate`,
`B_budget`, `p_build`, `p_serve`.

## Artifact SHA-256 digests

| artifact | SHA-256 |
|---|---|
| `P12_PRICE_AWARE_SUCCESSOR_PROTOCOL_PREREG_V1.json` | `db6fda439725623362c5a45b21b97bb73a33f26e0d4a2c61e226ce746d378b54` |
| `p12_price_aware_allocator_v1.py` (selector) | `5c33220de6b55755b12431815320f7cfa26cc22e6daa8d3c28ddc0461621c31c` |
| `run_p12_price_aware_successor_v1.py` (impl A) | `7d7e86936f3172acc412d399fde2402bc1174ce0331365bb3eed9759b6a5e064` |
| `check_p12_price_aware_successor_independent_v1.py` (impl B) | `3e8d2b8414338404075fee55dc730b890481cd517f1b0cd6b36575b0615688d4` |
| `audit_p12_price_aware_successor_surface_v1.py` (SC5) | `179586aa1a3ba46948adecbbf08cd6f4491cc786647677148de17fd3a900467b` |
| `P12_PRICE_AWARE_SUCCESSOR_RESULT_V1.json` | `d6132ce5518ac40114a8ec41b20a8d18adf9937663751dfb75f8ed69756dcb55` |

Frozen pools and frozen harness are byte-identical to the original battery
(six sha256s recorded in the prereg and re-verified in the result JSON).
`git diff 44d9794..worktree` over the frozen case files, generator, frozen V1
engines, original stress runner, original independent checker and the prereg is
**empty**; every post-prereg change is a new file.

## Executed coverage and gates

- RG1 exactness: every arm's outputs equal ground truth in every domain,
  regime and mix, for all five arms (incl. successor under all regimes) —
  **true**; FLAT direct-accounting (frozen `build_cost` + `serve_case` path ==
  decomposed ledger accounting) consistent for STATE_ALWAYS / original /
  successor in all 36 cases.
- RG3 coverage: 5 regimes; 45 V1 case-regime cells; 135 expanded cells; 4 B1
  case mixes; 3 B2 joint shared-budget mixes — complete.
- RG4 / SC4 two implementations: independent checker with different engines
  (full-rescan fixpoint UP, bidirectional-BFS, exhaustive 2^n knapsack truth)
  and a different argmin class (exhaustive subset enumeration, first-mask ties,
  vs DP prefer-not-take) — `P12_PRICE_AWARE_SUCCESSOR_SECOND_CHECKER_GREEN`,
  **180 case-regime + 15 joint cells cross-checked, 0 discrepancies**.
- SC5 surface audit: `P12_PRICE_AWARE_SUCCESSOR_SURFACE_AUDIT_GREEN` — static
  AST axis clean (only the 4 surface keys; only structural literals {0, 1, -1};
  no module globals), dynamic axis byte-identical under key-stripping AND
  domain-decoy injection across 195 ledger-regime checks, self-validation
  caught all 3 injected mutants and passed the harmless rename.

## Before / after (same run, same pools, same regimes)

| quantity | BEFORE (frozen allocator) | AFTER (successor) |
|---|---|---|
| positive priced-regret cells, V1_9 (per regime FLAT/MEM2X/CMP2X/MEM4X/CMP4X) | 0/0/1/2/3 | 0/0/0/0/0 |
| positive cells, EXPANDED_27 | 6/5/8/10/10 | 0/0/0/0/0 |
| total priced regret mass (all 36 cases) | 779/416/2378/3210/5846 | **0/0/0/0/0** |
| B1 case-mix aggregate regrets | positive in failing mixes | 0 in all 4 mixes x 5 regimes |
| B2 joint-mix regrets | positive (12 of 15 cells; worst 2860) | 0 in all 15 cells |
| `price_axis` verdict | BROKEN (zero-regret regimes: []) | **ROBUST** (all 5) |
| `distribution_shift_axis` verdict | BROKEN | **ROBUST** |

The BEFORE column reproduces the published BROKEN/BROKEN receipt numbers
exactly (45 positive cells with the same per-set/per-regime split recorded in
the prereg diagnosis).

## Success criteria

| SC | statement | result |
|---|---|---|
| SC1 | FLAT replication constraint: successor regret 0 in all 9 V1-9 FLAT cells AND FLAT realized == original's | **green** (0 regrets; 9/9 cost-equal) |
| SC2 | successor regret 0 in all 180 case-regime + 15 joint cells | **green** (0 positive cells) |
| SC3 | shift axis green under the original verdict logic (B1 + B2 on successor numbers) | **green** (ROBUST) |
| SC4 | independent checker discrepancy_count == 0 | **green** (0; 0 tie divergences) |
| SC5 | successor surface audit GREEN | **green** |
| SC6 | price responsiveness liveness (selections vary across regimes) | **green** (25 variant cells; e.g. `V1_9:SAT_PROPAGATION:SAT_T3_BUDGET_RACE`) |

Tie census (pre-registered statistic): exactly **1** non-unique-optimum cell —
`EXPANDED_27:SAT_PROPAGATION:SAT_T6_TIE_RACE:MEM4X` (n=2 optimal subsets); the
DP (prefer-not-take) and the checker's first-mask argmin selected the **same**
set on it, so the tie-divergence list is empty.

## Provenance of harness fixes (run history)

Three implementation-debug iterations occurred after the prereg, all in NEW
harness code (frozen files untouched, verified by the empty diff above):

1. Runner `verdicts_for` crashed (B1 aggregate flag computed inside a helper
   that did not receive the B1 table); refactored so the caller computes the
   B1 flag for each arm.
2. Checker had five syntactically broken f-strings (implicit concatenation
   split mid-placeholder); rewritten to hoist the runner values into locals.
3. Checker first reported 5 discrepancies, all one category: it compared the
   runner's order-canonicalized (sorted) static-selection records against its
   own greedy-order lists on the B2 unions (greedy order ≠ sorted order across
   domains). All values, charges and regrets agreed everywhere; the fix
   compares selection **sets** (the order is not part of the allocation
   semantics — arm evaluation consumes `set(selection)` on both sides). After
   the fix: 0 discrepancies.

No result number changed in any of these fixes; the runner JSON predates them
unchanged.

## Boundary / non-claims

- The successor is **not** a forward-time allocator: it reads the charging
  environment's published per-structure serve-charge certificates (the
  ORION-19-style resource ledger the runner compiles anyway). The revived statement
  is information-theoretic and construction-level: the V1 regret was entirely
  an objective/information mismatch in the selection rule; given the charger's
  own published ledger and prices, exact budgeted optimization of the charged
  objective attains zero priced regret on the frozen pool in every regime and
  mix. Deployable allocation without charge measurement remains open and is
  the named next lever.
- No re-tuning of the original allocator, pools, regimes, budget or any V1
  file; no claim about pools, prices or workloads outside the frozen 27+9
  cases, 5 regimes and 7 mixes.
- The ORACLE_LOCATION arm stays hindsight-diagnostic; the successor is
  compared against it, never identified with it.
- No upgrade, widening or retraction of the landed P12B equal-action
  complementarity authority.

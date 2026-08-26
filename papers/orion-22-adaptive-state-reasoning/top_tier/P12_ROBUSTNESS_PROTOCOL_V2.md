# ORION-22 robustness stress protocol V2 (price regimes, distribution shift, hidden-parameterization audit)

**Programme:** #977 (stacked on the ORION-22 transfer study V1, PR #994 — this
protocol reuses that study's frozen allocator, cost engines and case file
**byte-for-byte, additively**; no V1 file is edited).

**Purpose:** close the two remaining ORION-22 robustness gaps named in the
top-tier promotion review — (a) *robustness under altered resource prices and
task-distribution shift*, and (b) *mechanical confirmation that the allocator
harbours no domain-specific hidden parameterization*.

## Scientific object

`P12_TRANSFER_ALLOCATOR_V1` (frozen: `tau=4`, greedy by descending pending
multiplicity `q`, cumulative declared construction cost `<= B=500`, ties by
frozen case order) achieved zero per-case regret vs the hindsight locus oracle
on the 9-case / 3-domain transfer set at unit prices. Zero regret at ONE price
vector and ONE case mix does not establish robustness. This protocol stresses
the **unchanged, price-oblivious, domain-oblivious** rule along two
pre-registered environmental axes (prices, task mix) plus one static audit
axis (hidden parameterization), and reports honestly where zero regret
persists and where it breaks.

## Axis A — altered resource prices (pre-registered regimes)

The priced objective multiplies the two resource coordinates of the study:

```
priced_realized(arm, case) = p_build * build_charge(arm, case)
                           + p_serve * serve_charge(arm, case)
```

where `build_charge` is the frozen declared-construction accounting (watch
index passes / reverse-BFS expansions / DP-table fills) and `serve_charge` is
the frozen per-query serving accounting (indexed propagation examinations /
descent steps / row lookups vs naive rescans / fresh BFS / per-query DP),
both taken **from the V1 runner's own functions by import, unmodified**.

Five price regimes are frozen before any execution:

| regime | p_build | p_serve | reading |
|---|---|---|---|
| `FLAT` | 1 | 1 | unit prices (replicates V1 objective) |
| `MEM2X` | 2 | 1 | state materialization (memory) 2x expensive |
| `CMP2X`  | 1 | 2 | per-query serving compute 2x expensive |
| `MEM4X` | 4 | 1 | severe memory-heavy regime |
| `CMP4X`  | 1 | 4 | severe compute-heavy regime |

**Budget semantics (pre-registered, two-tier):**

- **S1 (primary — gates):** the budget `B = 500` remains a **nominal**
  constraint on unpriced declared construction cost (the resource is
  denominated in frozen abstract units; prices reweight the *objective*
  only). Feasibility of every arm is therefore unchanged; priced regret is a
  pure objective-level comparison.
- **S2 (secondary — characterization only):** a *priced-budget* reading in
  which the environment enforces `p_build * cumulative_declared_cost <= B`.
  A price-oblivious allocator selection violating this is recorded as
  `priced_budget_violation` for that (case, regime) cell. S2 violations are
  **reported, never gated on** — they characterize the price-obliviousness
  boundary of the frozen rule.

**Oracle under prices:** `ORACLE_LOCATION_PRICED` exhaustively enumerates
locus assignments over each case's structures subject to the S1 nominal
budget and minimizes the **priced** realized objective. It remains
diagnostic.

**Metric:** per (case, regime): `priced_regret(allocator) = priced_realized(allocator) - priced_realized(oracle)`. The price axis is ROBUST for the
transfer claim iff priced regret is 0 for the allocator in **every** case of
**every** domain under **all five** regimes (S1). If any cell is positive,
the axis verdict is the honest characterization: which regimes, which
domains, which case shapes, and the mechanism (greedy-by-q ignoring the
build/serve exchange rate; tau boundary; budget race).

## Axis B — task-distribution shift (pre-registered mixes)

The V1 set evaluates each case independently; a case-level mix is therefore
an aggregation over per-case outcomes. To make distribution shift a genuine
stress rather than a re-labelling, both levels are pre-registered:

**B1 case-level mixes** (aggregate of per-case S1 outcomes, all five price
regimes):

| mix | composition (from the expanded 27-case pool) |
|---|---|
| `MIX_BAL_27` | 9 SAT + 9 PATH + 9 KNAP (all) |
| `MIX_KNAP_HEAVY` | all 9 KNAP + first 4 SAT + first 4 PATH |
| `MIX_PATH_HEAVY` | all 9 PATH + first 4 SAT + first 4 KNAP |
| `MIX_SAT_HEAVY` | all 9 SAT + first 4 PATH + first 4 KNAP |

**B2 joint shared-budget mixes** (the genuine shift stress): the **same
unchanged allocator rule** is applied to the **union** of all structures in
the mix as one allocation problem — structures from all three domains
compete for one shared nominal budget `B = 500`, ordered by frozen
(case-file) order (SAT cases, then PATH, then KNAP). Because the rule sees
only `(sid, q, declared_cost)`, cross-domain joint allocation is well-posed
exactly when the hidden-parameterization audit (Axis C) passes. The priced
oracle enumerates all budget-respecting subsets of the union (structure
count is capped by construction so exhaustion is exact) minimizing the
priced objective. Domain engines then serve each structure under the chosen
locus assignment exactly as in V1.

| joint mix | composition (cases per domain) |
|---|---|
| `JOINT_BAL` | SAT cases 1–3, PATH cases 1–3, KNAP cases 1–3 of the 27-case pool |
| `JOINT_KNAP_HEAVY` | SAT cases 1–2, PATH cases 1–2, KNAP cases 1–6 |
| `JOINT_PATH_HEAVY` | SAT cases 1–2, PATH cases 1–6, KNAP cases 1–2 |

**Metric:** per (mix, regime): all per-case (B1) / joint (B2) priced
regrets; plus the V1 G3-style discriminator restricted to the mix —
`REASON_ONLY` and `STATE_ALWAYS` must each be strictly suboptimal somewhere
in the mix. The shift axis is ROBUST iff zero priced regret persists in
**every** mix under **all five** regimes (B1 and B2); otherwise the verdict
characterizes where and why.

## Axis B′ — frozen-generator expansion 9 -> 27

The V1 case file is expanded 9 -> 27 cases (9 per domain) by the frozen
constructive generator `generate_p12_robustness_cases_v1.py`: the original
nine V1 cases are carried over **byte-identically** (same `case_id`, same
data), and eighteen new cases are added — six per domain, each a
pre-registered stress shape:

- `T4_TAU_EDGE` — single structure with `q = tau - 1 = 3` (just below the
  materialization threshold);
- `T5_TAU_EXACT` — single structure with `q = tau = 4` (exactly at threshold);
- `T6_TIE_RACE` — multiple structures with equal `q` whose combined cost
  exceeds `B`, exercising the frozen tie-by-case-order rule;
- `T7_OVER_BUDGET` — one high-multiplicity structure with declared cost
  `> B` (materialization infeasible for every arm);
- `T8_MANY_SMALL` — three eligible structures whose costs jointly fit `B`;
- `T9_MIXED` — eligible and sub-threshold structures mixed under a binding
  budget.

All construction is literal (no RNG): explicit CNFs over `<= 8` variables,
explicit 15x15 grids (the four frozen obstacle families of the procedural
study: OPEN, CENTER_GATE, DOUBLE_GATE, HORIZONTAL_GATE), explicit item sets
with `n <= 16`. Declared costs obey the frozen conventions exactly
(SAT `= |cnf|`; PATH `= 225`; KNAP `= n * (c_max + 1)`), asserted by the
generator, the runner, and the independent checker. CI asserts the
generator output is byte-identical to the committed case file.

The expansion axis is pre-registered as **diagnostic strengthening**: zero
regret on the expanded set is NOT a gate for the V1 claim (which is bound to
the V1 nine cases); any positive-regret cell on the eighteen new cases is
reported as a boundary characterization of the frozen rule.

## Axis C — hidden-parameterization audit (mechanical)

A static + dynamic audit (`audit_p12_hidden_parameterization_v1.py`) of the
**frozen V1 runner** must confirm the allocator consumes ONLY the unified
ORION-19-compatible signal surface and nothing domain-specific:

1. **AST reachability:** from the allocator entry point
   (`allocator_selection`) build the transitive closure over function calls
   and module-global loads; collect every identifier, string literal and
   numeric literal reachable. The audit FAILS if any domain-specific symbol
   is reachable — domain names (`SAT_PROPAGATION`, `PATH_PLANNING`,
   `KNAPSACK`), domain engine names (`sat_*`, `path_*`, `knap_*`, the
   serving caches), domain payload keys (`cnf`, `grid`, `items`, `goal`,
   `c_max`), or any numeric literal outside the frozen allocator constants.
2. **Signal surface:** the only structure keys the allocator body reads must
   be `sid`, `queries`, `declared_cost`; the only module globals `TAU`,
   `BUDGET`. The emitted `allocator_params` signal set must be exactly
   `{q_pending_multiplicity, c_declared_cost, B_budget}`.
3. **Dynamic dimensionless-input proof:** running the frozen allocator on
   structures stripped to `{sid, queries, declared_cost}` must reproduce its
   selection on the full structures byte-identically, for every case in all
   domains.
4. **Audit self-validation (sensitivity + specificity, mandatory):** the
   audit must CATCH each of three injected mutants (an allocator with a
   `domain == "SAT_PROPAGATION"` branch; one reading `st["cnf"]`; one
   calling `sat_naive_up`) and must PASS a harmless local-variable rename.
   A mutant passing the audit, or the rename failing it, aborts the audit
   as invalid (`AUDIT_INVALID`), distinct from both GREEN and FAILED.

**Verdict semantics:** `P12_HIDDEN_PARAMETERIZATION_AUDIT_GREEN` = no
domain-specific symbol reachable, signal surface exact, dynamic proof holds,
self-validation green.

## Gates and terminals

The robustness study's own integrity gates (asserted in CI; independent of
the scientific outcome):

- **RG1 exactness:** every arm's outputs equal the V1 ground-truth path in
  every domain, every regime, every mix (prices move costs, never outputs).
- **RG2 determinism:** byte-identical replay of runner, checker and audit.
- **RG3 coverage:** all 5 regimes x {9-case V1 set, 27-case expanded set,
  4 B1 mixes, 3 B2 joint mixes} present, with per-cell priced regrets,
  priced oracle optima, and S2 violation flags.
- **RG4 two implementations:** the independent checker (different algorithm
  classes: full-rescan UP / bidirectional BFS / exhaustive `2^n` knapsack;
  independent re-implementation of the frozen rule and the priced oracle)
  must agree with the runner on every selection and every priced regret —
  zero discrepancies.
- **RG5 audit:** Axis C terminal is GREEN (not INVALID, not FAILED).

**Robustness verdicts (scientific, data-bound, never forced):** one line
each — prices / distribution shift / hidden-parameterization — with value in
{`ROBUST`, `REGIME_CONDITIONAL`, `BROKEN`} per the metrics above, recorded
in the evidence summary and receipt exactly as the runs produce them.

## Non-claims

This study does not tune or repair the allocator (any positive-regret cell
is reported, not patched); does not claim a universal price-robustness
theorem; does not convert the ORION-19 vector into one scalar exchange rate; and
does not promote the allocator to any runtime authority. The joint-mix
oracle remains hindsight diagnostic. S2 priced-budget violations are
characterization, not gates.

## Artifacts

- protocol: `P12_ROBUSTNESS_PROTOCOL_V2.md` (this file)
- frozen generator: `generate_p12_robustness_cases_v1.py`
- frozen expanded cases: `p12_transfer_cases_expanded_v1.json` (27 cases)
- audit: `audit_p12_hidden_parameterization_v1.py`
- runner: `run_p12_robustness_v1.py`
- independent checker: `check_p12_robustness_independent_v1.py`
- workflow: `.github/workflows/p12-robustness-stress-v1.yml`
- evidence summary + receipt (post-success only):
  `P12_ROBUSTNESS_EVIDENCE_SUMMARY_V1.md`,
  `P12_ROBUSTNESS_RESULT_RECEIPT_V1.md`

# ORION-22 stop/go public-data campaign — frozen action and signal menus V1

**Artifact class:** FROZEN PROTOCOL — NO RESULTS. The campaign this protocol
freezes has **not** been executed. No datum, score, gate verdict or terminal
exists for it, and nothing in this file may be cited as evidence of any
empirical outcome.

- **Study id (reserved):** `P12_STOPGO_PUBLICDATA_V1`
- **Bound issue:** SzeChunYiu/ORION#1086, ORION-22 boxes "Freeze identical
  state/reasoning action and signal menus for adaptive and strongest
  one-signal policies" and "Use task family/domain as the inference unit";
  portfolio disposition D-entry `STRICT_STOP_GO` in
  `papers/ISSUE_1086_PORTFOLIO_DISPOSITION_V1.json`.
- **Machine-readable twin:** `p12_stopgo_frozen_menus_v1.json` (same
  directory) — the checker `check_p12_stopgo_integration_v1.py` (paper root)
  validates menu identity across arms against that JSON, fail-closed.
- **Status:** menus frozen **before any campaign data collection**. The
  campaign runner that will consume these menus does **not** yet exist in this
  repository (`src/orion/study/p12/` contains the P12A/P12B/transfer/
  robustness/price-aware studies only). This artifact is therefore a
  paper-level protocol freeze, not a harness freeze; the future campaign
  preflight must consume these menus verbatim or preregister a successor
  protocol — it may not edit them in place.

## 1. Substrate and licensing boundary

- Substrate: **clean-license ScienceAgentBench task families** only.
- The upstream-license exceptions recorded for ScienceAgentBench in issue
  #1086 (instances 3, 32, 46, 53, 54, 84, which retain matminer/rasterio
  upstream terms) are **excluded** from the campaign universe before any
  split is drawn.
- No gold-outcome leakage into menus: every signal below is pre-outcome by
  construction (declared metadata and accounting quantities only).

## 2. Shared action menu (identical across all arms)

The action menu is the P12B frozen four-action set
`((0,0), (2,0), (0,2), (1,1))` carried over verbatim, with public-data
charging semantics declared:

| action id | state-construction units `s` | reasoning units `r` | charge `s+r` | semantics |
|---|---:|---:|---:|---|
| `A_RETAIN_MINIMAL` | 0 | 0 | 0 | retain raw task context, no extra step |
| `A_STATE_MAX` | 2 | 0 | 2 | spend the whole budget on state construction |
| `A_REASON_MAX` | 0 | 2 | 2 | spend the whole budget on reasoning/search |
| `A_BALANCED` | 1 | 1 | 2 | one unit of each |

- Charging: FLAT unit prices under the #664 resource accounting (tokens,
  latency, memory, model/embedding/compiler calls). **Skewed-price regimes are
  out of scope for this campaign**: `P12_ROBUSTNESS_STRESS_V1` returned
  `price_axis=BROKEN` and `distribution_shift_axis=BROKEN` for the V1
  allocator, so no price- or shift-robustness wording is available to this
  campaign at any outcome.
- **Common terminal rule (anti-confound, learned from P12A):** every arm
  emits its final answer through one identical, uncharged terminal step
  (same prompt template, decoding parameters and output contract). No arm
  may win through output-format, stopping-rule or verifier differences.

## 3. Shared signal menu (closed; identical across all arms)

Four pre-outcome, task-family-level signals:

| signal id | definition | provenance |
|---|---|---|
| `S_PENDING_MULTIPLICITY` | count of pending subtasks/questions declared for the family episode | transfer-allocator readable surface (V1) |
| `S_DECLARED_MATERIALIZATION_COST` | declared resource charge of one state-construction unit for the family | #664 accounting |
| `S_DECLARED_SERVE_EXCHANGE_RATE` | declared per-serve charge ratio state-serve vs reasoning-step for the family | NR-13 widened readable surface |
| `S_FAMILY_DIFFICULTY_PRIOR` | pre-outcome difficulty descriptor from licensed metadata only; exact implementation frozen at campaign prereg | donor: difficulty-conditioned allocation |

- The menu is **closed**: adding, removing or redefining a signal after any
  campaign data collection is forbidden (that would be retuning).
- `S_FAMILY_DIFFICULTY_PRIOR`'s numeric implementation is the only element
  deferred to the campaign prereg, and it must be frozen there **before any
  protected evaluation**, with gold outcomes forbidden as input.

## 4. Arms and access rights

| arm | action menu | readable signals |
|---|---|---|
| `ADAPTIVE` | the shared menu above, verbatim | all four signals |
| `ONE_SIGNAL_STATE` | the shared menu above, verbatim | `S_PENDING_MULTIPLICITY` only |
| `ONE_SIGNAL_REASON` | the shared menu above, verbatim | `S_FAMILY_DIFFICULTY_PRIOR` only |

- `ONE_SIGNAL_STATE` reproduces the landed V1 allocator's single readable
  surface (greedy-by-pending-multiplicity); `ONE_SIGNAL_REASON` reproduces
  the strongest donor single-signal policy (difficulty-only reasoning
  allocation). Both one-signal arms are **reported**; the headline comparison
  is against the **stronger** of the two, selected on a frozen tuning split
  **before** protected evaluation. Selection after seeing protected outcomes
  is forbidden.

## 5. Inference unit

- Primary inference unit: **task family**; aggregation: **domain**.
- Generated rows, seeds, episodes and individual instances are **not**
  independent units for any interval, gate or claim in this campaign.

## 6. Campaign scope minimums (declared requirements, not satisfied here)

- `>= 20` task families; `>= 3` domains; `>= 2` model families.
- This artifact does not satisfy these minimums and does not claim to; the
  execution box in issue #1086 remains open until the campaign runs.

## 7. Stop/go gate (frozen decision rule)

Pass requires **all** of:

1. adaptive gain `>= 3` normalized points over the stronger one-signal arm;
2. family-block bootstrap 95% lower bound `> 0`;
3. positive in `>= 2/3` of domains **and** in every leave-one-domain-out
   analysis;
4. max regret `<= 2` normalized points.

**Fail action (binding):** stop the positive complementarity claim and
publish the boundary/null result. **Do not iterate until positive.** Any
successor study requires a new preregistered protocol with its own frozen
thresholds; it may not widen menus, thresholds or scope post hoc.

## 8. Binding prior adverse evidence

The campaign must carry these landed negatives as priors (full bindings with
SHA-256 in `p12_stopgo_frozen_menus_v1.json` and
`P12_ACTIVE_CLAIM_AUTHORITY_V5.json`):

1. `P12A_SUPERIORITY_AUTHORITY_WITHHELD` — identical budget did not mean
   identical action capability; any new comparison must hold actions
   symmetric (hence Section 2).
2. `P12_ROBUSTNESS_STRESS_V1_EXECUTED` with `price_axis=BROKEN` and
   `distribution_shift_axis=BROKEN` — the unchanged V1 allocator does not
   survive price skew or distribution shift; no robustness wording is
   available to this campaign.
3. `P12_PRICE_AWARE_SUCCESSOR_SUPPORTED` (NR-13) — the repair that followed
   the broken axes worked by widening the readable surface under
   pre-registration, which is the only sanctioned revival pattern.

## 9. Label honesty: no "P12C" artifact exists

Issue #1086 asks to "Integrate P12C's negative public-data result as binding
prior evidence". **No repository artifact, commit, pull request or issue
labelled P12C exists** (searched: working tree, all refs, PRs, issues). None
was invented. The binding prior adverse evidence actually integrated here is
the landed adverse chain in Section 8. This mirrors the P11J precedent
recorded in `P11_ACTIVE_CLAIM_AUTHORITY_V2.json`.

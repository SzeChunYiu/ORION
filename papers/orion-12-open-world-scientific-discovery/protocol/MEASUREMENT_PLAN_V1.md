# ORION-ORION-12 measurement plan V1

Frozen before any outcome exists. Machine-checkable companion: `STATISTICAL_PLAN_V1.json` (single source of truth for roles, directions, margins, oracles and bindings). This file carries the prose the JSON cannot: what each metric silently becomes when its denominator is invalid, how the four oracles are defined, and where this plan is stricter than the programme standard.

| Section | Contents |
| --- | --- |
| [1](#1-scope-and-authority) | Scope, authority, what this file may not change |
| [2](#2-metric-roles) | Role assignment and the three primary-bearing families |
| [3](#3-denominator-validity) | Per-metric denominator condition and degradation name |
| [4](#4-oracle-definitions) | O1 route stop, O2 task closure, O3 reread, O4 obligations |
| [5](#5-measurement-procedure) | Ties, missing values, abstention, repeats |
| [6](#6-required-bindings) | Fields the harness lane must emit |
| [7](#7-stricter-than-the-programme-standard) | Strictness deltas, declared not silent |

## 1. Scope and authority

This plan is **additive**. It does not modify `PROTOCOL_V1.json`, which stays `DESIGN_FROZEN` with `outcome_accessed: false`. It may only be stricter than `research/paper-programme-v1/protocols/ANALYSIS_STANDARD_V1.md`; every strictness delta is listed in section 7 and in the JSON's `stricter_than_analysis_standard`.

No outcome, estimate or expectation of an ORION-versus-baseline result appears anywhere in this plan. Margins are decision thresholds, not predictions. Every worked example below is labelled `SYNTHETIC - ILLUSTRATIVE ONLY` and uses invented inputs.

Statistics come from `research/paper-programme-v1/protocols/publication_stats.py`. Reimplementation is forbidden.

## 2. Metric roles

`PROTOCOL_V1.json` names five task families but its `multiplicity` field scopes the primary to three: Deep, Wide and complete-gold. This plan follows the frozen protocol.

- **Primary-bearing families (one `family_primary` each):** `autoresearchbench_deep` → `deep_official_success`; `autoresearchbench_wide` → `wide_official_iou`; `offline_complete_gold` → `complete_gold_recall`.
- **`sage_scientific_retrieval`** carries no confirmatory primary. Its role is the lexical-baseline promotion gate: ORION must beat `bm25_keyword` in the same call. SAGE's own finding is that strong lexical retrieval is competitive, so this is a gate, not a straw man.
- **`metasyn_retrieval_screening`** carries no confirmatory primary. It supplies screening-stage recall and false-negative counts as secondary.
- **`premature_task_closure_rate`** sits in `metrics.primary` but is not a family primary. It is the **primary safety guard** for H1's `superiority_and_safety` direction, tested once per primary-bearing family as a non-inferiority test at 0.02, and it is not part of any Holm family.
- Four cost metrics are **secondary non-inferential**: budget-compliance checks, never hypotheses.
- Exploratory diagnostics (`truncation_rate`, `unjustified_closure_rate`, `open_obligation_rate`, `recall_at_judged_pool`) are declared now so they exist in the freeze, and can never be retroactively promoted.

## 3. Denominator validity

The controlling question for every row: *if the denominator condition fails, what is this number actually measuring?* Naming the degradation is what stops an invalid metric from being read as its valid namesake.

| Metric | Role | Dir | Valid only when | Silently becomes |
| --- | --- | --- | --- | --- |
| `deep_official_success` | family primary | ↑ | official evaluator holds custody, evaluator hash bound | an unofficial reimplementation score, not comparable to published numbers |
| `wide_official_iou` | family primary | ↑ | official evaluator holds custody, evaluator hash bound | same |
| `complete_gold_recall` | family primary | ↑ | **complete gold denominator** | `recall@judged_pool` — self-referential: a system that returns more inflates its own denominator |
| `premature_task_closure_rate` | safety guard | ↓ | **complete gold** and no obligation bearing on discoverability | `CANNOT_CHECK` — never 0. Scoring absence of evidence as safety is the exact failure this plan exists to prevent |
| `precision` | secondary | ↑ | every returned item judged | precision over a judged subset, biased upward when unjudged items skew irrelevant |
| `screening_recall` | secondary | ↑ | complete include set for the review | `CANNOT_CHECK` |
| `false_negative_count` | secondary | ↓ | **identical and complete** gold across compared systems | "misses relative to pool" — improves as the pool shrinks. Rate form (1 − recall) reported alongside for any cross-family reading |
| `unique_relevant_per_route` | secondary | ↑ | merged identities, content digests | inflated by route count: one paper found by four routes counts four times |
| `route_overlap_content_digest` | secondary | reported | merged identities | understated overlap from unmerged ids, making shared-backend routes look independent |
| `marginal_relevant_gain` | secondary | ↑ | merged identities, leave-one-route-out | an order-dependent first-finder artefact if computed by arrival order |
| `route_stop_false_positive_rate` | secondary | ↓ | complete gold **and** per-route reachability | `CANNOT_CHECK` |
| `route_stop_false_negative_rate` | secondary | ↓ | complete gold **and** per-route reachability | `CANNOT_CHECK` |
| `legitimate_reread_rate` | secondary | ↑ | encounter stream emitted | unmeasurable: suppression is invisible on an execution-only denominator |
| `duplicate_processing_rate` | secondary | ↓ | encounter stream **and** merged identities | undercounted — aliases of one work look like distinct sources |
| `wallclock_seconds` | non-inferential | ↓ | always valid | — |
| `query_count` | non-inferential | ↓ | always valid | — |
| `model_tokens` | non-inferential | ↓ | always valid | — |
| `tool_calls` | non-inferential | ↓ | always valid | — |

Survives an incomplete denominator: `precision` (when the returned set is fully judged), and the four cost metrics. Everything else in the "complete gold" rows is `CANNOT_CHECK` without it.

## 4. Oracle definitions

Defined against the **complete-gold world** and stated implementation-agnostically. The harness lane owns the offline gold world (`src/orion/study/p2/`); section 6 lists exactly what it must emit.

### O1 — route-stop false positive / false negative

A route stop at attempt index *t* is a **false positive** when, in the complete-gold world, at least **1** previously-unfound gold-relevant merged source was still reachable on that route at *t*, and the route still held at least **1.0** route budget unit. Denominator: route stop events.

The **oracle exhaustion point** is the earliest attempt index at which zero not-yet-found gold-relevant merged sources remain reachable on that route. A route is a **false negative** when it made more than **1** further attempt past that point. One confirming attempt after true exhaustion is legitimate evidence-gathering; two or more is a failure to read a flat route. Denominator: routes that reached the oracle exhaustion point.

Reachability and residual yield are evaluated under the frozen corpus/index bound in the run manifest, never live provider state. The route-control policy constants (`FrozenRouteControlPolicy.reformulate_after_zero_novelty`, `switch_after_zero_novelty`) are recorded but do **not** define the oracle — the oracle is gold-defined, so changing the policy cannot move the truth it is scored against.

### O2 — premature task closure

A declared closure is **premature** when at least one gold-relevant merged source was still discoverable by at least one admissible route within the system's remaining matched budget at closure time. Denominator: tasks in which the system **declared** closure. Tasks truncated at a cap did not close and are excluded from this denominator, reported separately as `truncation_rate`; truncation is never scored as safe stopping.

`CANNOT_CHECK` when the task's gold set is incomplete, or an unresolved open obligation could bear on discoverability.

### O3 — legitimate reread versus duplicate processing

Grounded in the implemented mechanic: `decide_read` / `ReadDecision` in `src/orion/knowledge/identity.py`. For every read **encounter**, the harness recomputes `decide_read` against the ledger state immediately before the encounter, on merged primary keys from `merge_identities` — never raw retrieval ids.

- Legitimate reread states: `CONTENT_CHANGED`, `NEW_SCHEMA`, `NEW_FRAME` — a changed content version, a changed extraction schema, or a changed question frame.
- Duplicate processing: an **executed** read whose decision was `ALREADY_READ`.
- `UNSEEN` encounters are first reads and belong to neither numerator.

Both rates use an **encounter** denominator, not an execution denominator: `legitimate_reread_rate` = executed / all encounters in a legitimate state; `duplicate_processing_rate` = executed / all encounters in the `ALREADY_READ` state. An execution-only denominator hides suppression — a system that silently refuses legitimate rereads never executes them, so they vanish from numerator and denominator together and the rate looks healthy. The encounter stream is what makes "without suppressing legitimate rereads" testable at all.

*SYNTHETIC - ILLUSTRATIVE ONLY.* Invented inputs: 10 encounters in state `NEW_FRAME`, 8 executed → `legitimate_reread_rate` = 0.80; 6 encounters in state `ALREADY_READ`, 1 executed → `duplicate_processing_rate` = 0.17. These digits demonstrate the arithmetic and carry no claim about any system.

### O4 — unavailable / censored route obligations

A trial with `transport_status` in `RATE_LIMITED`, `UNAVAILABLE`, `TIMEOUT`, `ERROR` opens an obligation on that route, open until a later successful trial on the same route with the same query derivation resolves it. An open obligation is **never** route exhaustion and **never** evidence of absence. A task closed with an unresolved obligation carries an authority flag and enters `unjustified_closure_rate`. If the obligation could bear on a coverage or stopping metric for that task, that metric is `CANNOT_CHECK` for that task. Unavailability cases are **retained**, never excluded.

## 5. Measurement procedure

- **Statistical unit** is the task (or benchmark topic/route/route-pair/encounter as listed per metric in the JSON). Comparisons are paired on `task_id`.
- **Repeats**: 3 per (task, system), collapsed to a per-task value by **mean** *before* bootstrapping. `best_of_n`, `max`, `any_success` and analyst-selected runs are forbidden by name — best-of-N converts variance into apparent capability.
- **Ties** on a family primary resolve against ORION: a tie is not a superiority result, and the interval, not the point estimate, carries every decision.
- **Missing / failed / malformed / abstained**: retained and scored as the outcome they are. Only a documented host-infrastructure outage is excludable, symmetrically, by pairwise-complete deletion across all systems, capped at 5% of a family.
- **Truncation at a cap**: outcome retained and scored as-is; partial finds count; the task is recorded as not closed.
- **`CANNOT_CHECK`** is an outcome, never missing data and never 0.
- **Precision**: `assumed_p` is frozen at 0.5 for every family — conservative for a binomial and also a bound on the mean of any [0,1] variable, so it covers per-task IoU and recall as well as binary success. Assuming a smaller rate would shrink N by anticipating an outcome. `offline_complete_gold` is host-owned and commits to a half-width of 0.05, which is **N ≥ 385** tasks; the other families' N is fixed by the benchmark and unbound at freeze, so the plan instead requires the achieved half-width to be computed from the realised N and any family exceeding 0.03 to be labelled `UNDERPOWERED`. The tier ladder and every N are in the JSON and are recomputed from `publication_stats.required_n_for_proportion_half_width` by the test, never typed by hand.
- **Figures and tables**: `PROTOCOL_V1.json` freezes *which* exist; the JSON's `figure_bindings` freezes *what each may render*, so a panel cannot change the metric it shows after outcomes are seen. Every caption states N, aggregation unit, uncertainty definition and role. Cosmetic layout changes are permitted and logged; a change to what a figure renders needs a new protocol version.

## 6. Required bindings

Full records — field, type, meaning, metrics enabled — live in `STATISTICAL_PLAN_V1.json` under `required_bindings`, ids **B1–B16**. Summary for the harness lane:

| Id | Field | Enables |
| --- | --- | --- |
| B1 | `result_record.task_id` | pairing, pairwise-complete deletion |
| B2 | `route_trial.attempt_index` | route-stop oracle timeline |
| B3 | `route_trial.consecutive_zero_novelty_before` | route-stop oracle, policy currency |
| B4 | `route_trial.captures[].merged_source_id` | precision, uniqueness, overlap, marginal gain |
| B5 | `oracle.gold_items[]` | recall, FN count, closure, route-stop oracles |
| B6 | `oracle.gold_set_complete` | every complete-denominator metric's validity switch |
| B7 | `route_trial.captures[].content_digest` | overlap and dedup on content identity |
| B8 | `oracle.route_residual_yield[route][attempt]` | route-stop FP/FN |
| B9 | `task_closure.declared` (+ index/time) | closure versus truncation |
| B10 | `oracle.task_residual_discoverable_within_budget` | premature closure |
| B11 | `route_trial.open_obligation_ids` | obligation accounting, `CANNOT_CHECK` rule |
| B12 | `result_record.cost` (4 resources) | cost metrics, budget compliance, cost ratio |
| B13 | `result_record.evaluator_hash_and_contamination` | official-metric validity, contamination gate |
| B14 | `read_encounter.decision_before_execution` | reread legitimacy |
| B15 | `read_encounter.executed` | suppression visibility |
| B16 | `result_record.repeat_index_and_seed` | repeat nesting and collapse |

B14/B15 require a stream the current schemas do not carry: one record per **presented** `(merged_source_id, content_digest, schema_version, frame_id)`, whether or not a read followed. B8/B10 require oracle-side counterfactual counts, custody-separated from the candidate.

## 7. Stricter than the programme standard

Being stricter is permitted; being silently stricter is not. Eight deltas, itemised in the JSON as S1–S8: pairwise-complete deletion plus a 5% exclusion budget (S1); frozen mean collapse with best-of-N named and forbidden (S2); cost metrics declared non-inferential (S3); `delta_ni` = 0.01 tighter than `delta_sup` = 0.03, with a 1.25× consumed-cost ceiling (S4); explicit `CANNOT_CHECK` instead of 0 for incomplete denominators (S5); the safety guard as an interval-based non-inferiority test rather than a point-estimate "not worse" (S6); encounter-denominator reread metrics (S7); `assumed_p` fixed at 0.5 so N cannot be shrunk by anticipating an outcome (S8).

Nothing here weakens `ANALYSIS_STANDARD_V1.md`.

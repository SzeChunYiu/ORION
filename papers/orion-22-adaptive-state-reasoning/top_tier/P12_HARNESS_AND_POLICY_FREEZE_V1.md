# P12 campaign harness and policy freeze V1 — executable semantics, frozen before any model call

**Artifact class:** FROZEN PROTOCOL — NO RESULTS. Machine twin:
`P12_HARNESS_AND_POLICY_FREEZE_V1.json`; derivation/self-test module:
`campaign_derivation_v1.py`. Every execution flag is false; nothing here is
evidence of any outcome.

**Binding:** SzeChunYiu/ORION#2139 Stage 2 (with Stage 0 identity slots);
consumes verbatim `p12_stopgo_frozen_menus_v1.json` (actions, signals, arms,
gate), `P12_CAMPAIGN_PREREG_V1.json` (families, difficulty priors, splits,
repeat policy), `P12_SCIENCEAGENTBENCH_VERIFIED_SUBSTRATE_FREEZE_V1.json`
(substrate), and emits `ORION.A2.P12StopGoResultInput.v1` for the frozen
analyzer `analyze_p12_stopgo_final_v1.py`.

## 1. Episode structure — why the family is the allocation unit

A campaign **episode** is one `(family, model_identity)` pair. The policy
chooses **one action for the whole episode**, because the state a
state-construction unit builds is a *family-level artifact*: every family is
one source repository (frozen family key `github_name`), so repo-level context
materialized once is reusable across all of the family's instances. This is
the resource-location question of the paper — reusable state versus per-task
reasoning — realized on external tasks.

## 2. Action semantics (the four frozen actions, executable form)

All actions share one budget of 2 charged units and one **identical, uncharged
terminal step** (Section 5). Per instance in the episode's family:

- `A_RETAIN_MINIMAL` (0,0): the terminal step receives the raw task context
  only (task instruction, dataset folder tree, dataset preview).
- `A_STATE_MAX` (2,0): two state-construction units. Unit S1 (family-level,
  executed once per episode, its output cached and reused for every instance
  of the family): the model receives the family's instances' dataset trees and
  previews and the family repository name, and emits a **family state
  artifact** (bounded digest of shared data schemas, conventions, and reusable
  facts). Unit S2 (instance-level): the model receives the instance context
  plus the family artifact and emits an **instance state artifact** (bounded
  digest binding the family artifact to this instance's files). The terminal
  step receives raw context + both artifacts. No reasoning/plan text is
  requested or forwarded.
- `A_REASON_MAX` (0,2): two reasoning units, both instance-level. Unit R1: the
  model receives the instance context and emits a written analysis/plan. Unit
  R2: the model receives context + R1 and emits a refined plan. The terminal
  step receives raw context + both plans. No state artifact is built and
  nothing is cached across instances.
- `A_BALANCED` (1,1): one family-level state unit (S1, cached as above) and
  one instance-level reasoning unit (R1, which also sees the S1 artifact).
  Terminal step receives raw context + S1 artifact + R1 plan.

Unit outputs are capped at a frozen byte budget (machine twin) so no action
can smuggle unbounded extra computation through longer intermediates.

## 3. Signal operationalizations (pre-outcome, declared quantities only)

- `S_PENDING_MULTIPLICITY` = the family's clean-instance count (declared in
  the campaign prereg; the reusable-state amortization base).
- `S_DECLARED_MATERIALIZATION_COST` = total UTF-8 bytes of the family's
  instances' `dataset_folder_tree` + `dataset_preview` fields, divided by
  10,000 (declared proxy for the charge of materializing family state;
  computable from the frozen parquet alone).
- `S_DECLARED_SERVE_EXCHANGE_RATE` = 1.0 for every family (FLAT pricing is
  frozen for this campaign; the signal is retained in the menu and carried as
  the constant it is — the menu is closed, so it is neither dropped nor
  redefined).
- `S_FAMILY_DIFFICULTY_PRIOR` = the committed per-family value in
  `P12_CAMPAIGN_PREREG_V1.json`.

All four are computable from frozen artifacts before any model call; none can
change after outcomes exist.

## 4. Policy functional forms (frozen); thresholds fit on the tuning split only

Let `m` = S_PENDING_MULTIPLICITY, `c` = S_DECLARED_MATERIALIZATION_COST,
`x` = S_DECLARED_SERVE_EXCHANGE_RATE, `d` = S_FAMILY_DIFFICULTY_PRIOR, and
`v = m / (c · x)` (state value per unit declared cost, amortized by
multiplicity).

- `ONE_SIGNAL_STATE` (reads `m` only): `A_STATE_MAX` if `m ≥ θ_m` else
  `A_RETAIN_MINIMAL`. (Reproduces the V1 greedy-by-pending-multiplicity
  surface.)
- `ONE_SIGNAL_REASON` (reads `d` only): `A_REASON_MAX` if `d ≥ θ_d` else
  `A_RETAIN_MINIMAL`.
- `ADAPTIVE` (reads all four): with indicator `S = [v ≥ θ_v]` and
  `R = [d ≥ θ_r]`: `A_BALANCED` if S and R; `A_STATE_MAX` if S only;
  `A_REASON_MAX` if R only; `A_RETAIN_MINIMAL` otherwise.

**Threshold-fitting procedure (frozen):** each θ is selected on the 6-family
tuning split only, by exhaustive search over the finite candidate grid = the
midpoints between consecutive sorted tuning-family signal values (plus one
candidate below the minimum and one above the maximum), maximizing the
policy's mean tuning-family score, ties broken toward the smaller threshold.
The stronger one-signal comparator is then the one-signal arm with the higher
mean tuning score (tie → `ONE_SIGNAL_STATE`, declared now). Fitted thresholds
and the selection are bound in a pre-protected amendment
(`P12_TUNING_BINDING_V1.json`, schema in the machine twin) **before** any
protected-family model call; the analyzer independently refuses inputs whose
`one_signal_selected_before_protected_evaluation` flag is not true.

## 5. Terminal step (identical, uncharged, arm-blind)

One frozen prompt template (machine twin carries its exact text) that
receives: the instance's raw task context, plus whatever intermediate
artifacts the action produced (possibly none), and requests the final Python
program in a single fenced block. Same template bytes, same decoding, same
output contract for every arm and model; the template never names the arm.
The emitted program is executed by the pinned upstream ScienceAgentBench
evaluation harness (`OSU-NLP-Group/ScienceAgentBench` @ `c26e151e…`) in an
isolated per-instance environment on the execution host. The runner never
reads `gold_program_name`, `eval_script_name` content, or any gold output;
evaluation is the upstream evaluator's job.

Amended 2026-09-03 (template_id `P12_TERMINAL_V1` -> `P12_TERMINAL_V1M`) by
the preregistered successor `P12_HARNESS_AMENDMENT_DATASET_MOUNTPOINT_V1.json`
(made at 0 protected calls, tuning binding unbound; evidence:
`P12_TUNING_EVAL_INSTRUMENT_FINDING_V1.md`): the template gained one sentence
disclosing that DATASET TREE files mount under `./benchmark/datasets/`
relative to the program's working directory. Uniform across all arms and
lanes; infrastructure-only; every other frozen value unchanged.

## 6. Scores, oracle, and the derivation step

- Per-instance outcome = the upstream evaluator's primary task-success
  boolean.
- **Family score (per arm, per model) = 100 × mean instance success** over
  the family's clean instances — the "normalized points" of the frozen gate
  (3 points = 3 percentage points).
- Execution shape: the four **actions** are executed once per
  `(instance, model)` — the 4-action matrix. Arm scores are then *derived*:
  an arm's family score is the score of the action its policy selects for
  that family episode (policies are deterministic functions of frozen
  signals, so this is a lookup, not a new run).
  `hindsight_oracle_by_model[family][model]` = max over the four actions of
  the family score — by construction ≥ the ADAPTIVE score, satisfying the
  analyzer's oracle invariant.
- `campaign_derivation_v1.py` implements signals, policies, threshold
  fitting, matrix→arms derivation and result assembly, and self-tests all of
  it on synthetic fixtures (no model call, no substrate execution, CI-safe).

## 7. Stage 0 identity slots (to be bound in MODEL_IDENTITY_FREEZE_V1.json)

Two live lanes probed 2026-09-02 (SzeChunYiu/ORION#2139 comment): GPT_CLASS
via `codex` CLI (single-turn exec mode, tools disabled) and
CLAUDE_OR_GEMINI_CLASS via `claude` CLI (`-p` print mode, tools disabled).
The identity freeze must pin CLI version, exact model id, invocation flags,
and record provider-default (non-configurable) decoding; the prereg's
1-run-per-cell repeat policy carries the nondeterminism consequence. Phase 1
requires ≥2 model families, which these two lanes satisfy; OPEN_WEIGHT is a
Phase-2 addition, not a Phase-1 blocker.

## 8. Hostile self-tests (must all reject; implemented in the module)

1. terminal-template mutation between arms → assembly refuses;
2. an arm score not equal to its policy-selected action's score → refuse;
3. oracle below ADAPTIVE for any (family, model) → refuse (and the analyzer
   double-refuses);
4. threshold fit touching any protected family → refuse;
5. a result input missing a frozen model id, or families below the scope
   minimums → assembles only with `CANNOT_CHECK` posture, never silently
   narrowed;
6. any gold-side parquet column requested by the runner's context builder →
   refuse at field-access level.

## 9. Execution plan and non-goals

Compute shape: 96 instances × 4 actions × 2 models = **768 terminal runs**
plus ≤ 96×2 family-state (S1) calls and per-unit intermediate calls, executed
on laptop-billy or a LUNARC node (never the Mac mini), after the sealed
pre-run manifest (Stage 3) binds every digest above. Gate outcomes publish in
either direction; a failed gate is the boundary/null publication; no retune.
This freeze adds no claim and changes no menu, threshold semantics, price, or
gate value.

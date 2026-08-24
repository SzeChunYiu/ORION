# P5 C5 Double Ratchet metric-only execution binding — V4

## Scientific result first

**Terminal:** `P5_C5_V4_DOUBLE_RATCHET_SOURCE_PARSER_ISOLATION_FALLBACK_WALLCLOCK_COMPUTE_AND_DEPENDENCY_LOCK_BOUND__TWELVE_C5_FIELDS_BLOCKING__OFFICIAL_RUNNER_REGENERATES_SOLVER_OUTPUTS_AND_REPORTS_DEVELOPMENT_LOCKED_EACH_ROUND__ZERO_OF_SIX_PANEL_READY__PERFORMANCE_AND_SUPERIORITY_CANNOT_CHECK`

The exact official metric-only arm is source-bound at `0f14e910d361196422d9b938f45280919952d4fd` / tree `3ca13a51b4fb6ff77013d8886023ee852cbf373e`, but **C5 was not executed**. Exactly **9/21 fields are BOUND and 12/21 remain blocking**. Panel readiness is **0/6**. Performance, superiority, preservation, transfer, harm and H1-H4 remain **CANNOT_CHECK**.

The key scientific defect is not an installation detail: `run_metric_evo.py` calls the hosted solver afresh for train, eval_dev and eval_locked, so realized solver outputs are not fixed merely because the solver code/model label is fixed. It also computes `eval_locked` agreement every round, persists it in `metric.db`/history/result.json and prints the final value. A P5 use is therefore admissible only if native `eval_locked` is a separate development-only surrogate and the true protected panel never enters the evolution process. The frozen evaluator must be scored exactly once by an independent custodian.

## Exact source and native arm

- Repository: `https://github.com/amazon-science/Self-Evolving-Agents-Double-Ratchet`
- Commit: `0f14e910d361196422d9b938f45280919952d4fd` (unsigned Git commit status `N`, 2026-07-29T05:20:31Z)
- Tree: `3ca13a51b4fb6ff77013d8886023ee852cbf373e`
- Deterministic archive SHA-256: `9426222eefc25878f7e7d1ecd1ff9824c894bc358cb8d5f31ee3c8d4a8db9640`
- Tree metadata: 113 blobs / 888822 bytes; 0 stored split payloads; 0 result payloads.
- Entrypoint: `scripts/run_metric_evo.py`, SHA-256 `fd6a2b776e1f64edb361401451e3e62d50b9caf21d129c3fa5dcbe336116dac0`.
- Licence: Apache-2.0 `09e8a9bcec8067104652c168685ab0931e7868f9c8284b66f5ae6edae5f1130b`; NOTICE `5d86be6e681240106316a6763eb0dcb47a8adcb426c19df4693098ceb61bb531`.
- Excluded: co-evolution, skill evolution, `--naive`, and `--golden-diff-selectable`.

Repository-wide inspection used Git tree names/modes/counts only. No benchmark or result payload was opened. The scratch clone is clean, detached and read-only.

## V4 bindings

The six V3 blockers repaired by V4 are: isolated results-only write surface, native terminal parser, empty fallback set, whole-run wallclock, compute envelope, and a 46-entry uv dependency resolution. Together with the three retained source identity fields, this yields 9 bound fields.

The parser can emit only `EVALUATOR_REPAIR` or `UNRESOLVED`. `EVALUATOR_REPAIR` requires exact source, unchanged solver/prompt/task bytes, empty skill bank, evaluator-only writes, anchored validity, a unique input-native evaluator-repair certificate, and no protected panel/score. It never returns agreement values and is not a protected scorer.

The generated lock explicitly includes `datasets`, which the default MBPP loader imports even though README's short install list names only pydantic, pyyaml and boto3. This is a dependency repair, not a scientific result and not a claim that a future P5 adapter needs no extra dependencies.

## Twelve blockers

- `custody.external_protected_scorer` — No independent scorer principal, immutable scorer digest, access-control identity or signed acceptance exists.
- `custody.one_shot_no_feedback_barrier` — The official runner reports its eval_locked value every round and at stdout; no independent one-shot handoff/no-return-channel receipt exists.
- `custody.protected_panel_freshness` — No post-protocol protected panel identity, commitment or freshness attestation was available.
- `inputs.candidate_visible_case_bytes` — The source contains no stored split or result payload. No rights-cleared P5 dossier, frozen solver-output set, development anchor or development-only locked surrogate is frozen.
- `model_provider.primary` — Repository labels do not freeze an immutable served model revision, cross-region route, exact endpoint/TLS identity, service revision, credential principal or allowed role/capability map; frozen solver outputs are also absent.
- `resources.calls_tokens_usd` — Dynamic detector, synthesis, teacher and solver calls have no aggregate call, input-token, output-token or USD hard stop; provider usage reconciliation and overshoot semantics are absent.
- `resources.retry_network` — Retry bytes are known, but the Bedrock route/DNS/TLS endpoint, offline dataset policy and deny-by-default egress network are not independently bound or enforced.
- `rights.container_and_generated_artifacts` — No content-addressed runtime image/SBOM/complete notices or authority for prompts, solver outputs, task traces, metric.db and result.json retention/publication is closed.
- `rights.model_provider_and_services` — No authorized Bedrock credential principal, study-use/data-retention terms, cross-region policy, pricing/quota receipt or publication permission is frozen.
- `rights.task_and_benchmark_content` — The repository explicitly excludes datasets/results. MBPP+/Hugging Face, P5 dossiers, development anchors and final protected panel have separate licences/terms not captured here.
- `runtime.container_or_environment` — No content-addressed Linux image containing Python 3.11, the exact lock, timeout tooling and source runtime has been built, SBOMed and smoke-verified.
- `runtime.task_environment` — The official entrypoint supports MBPP/report_gen, not the P5 dossier or eight-class decision. It regenerates hosted solver outputs at run time and uses eval_locked each round; no P5-native task adapter or frozen development-output environment exists.

## Synthetic/native-shaped smoke boundary

The parser's 6 in-memory cases exercised one guarded success shape and five fail-closed paths. They load no real metric, task, benchmark, result or protected outcome; license zero substantive singletons; and are not performance evidence.

## Next discriminator

Freeze a rights-cleared P5 development packet and solver-output tree, bind exact Bedrock service/egress/call-token-USD envelope plus image/SBOM, and establish independent fresh-panel one-shot custody; C5 must still wait for 6/6 matched arm readiness.

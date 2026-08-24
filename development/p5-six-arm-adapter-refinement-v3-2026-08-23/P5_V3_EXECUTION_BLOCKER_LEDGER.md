# P5 V3 exact execution-blocker ledger

**Authority:** outcome-free resource, rights, adapter, and custody preflight only. The entries below are blockers, not observed comparator failures.

**Preserved terminal:** `P5_SIX_ARM_EXECUTION_CONFIG_RESOURCE_RIGHTS_AND_EIGHT_CLASS_ADAPTERS_CANNOT_CHECK`

Every required field must be prospectively `BOUND` before an arm can execute. A template, freezable choice, `UNBOUND`, `CANNOT_CHECK`, or `UNSUPPORTED` value cannot license execution.

## SWE-agent

- Arm: `C1_FIXED_AGENT__SWE_AGENT`
- Blocking fields: **18**

| Field | State | Cause |
|---|---|---|
| `adapter.isolated_write_surface` | `UNBOUND` | The V3 synthetic write registry is specified, but no runtime enforcement/reset wrapper is bound. |
| `adapter.native_parser_binding` | `UNBOUND` | The generic V3 synthetic contract is hashed, but no arm-native runtime parser/binding is implemented or checked against native outputs. |
| `custody.external_protected_scorer` | `UNBOUND` | Independent protected scorer identity, code and access control remain CANNOT_CHECK. |
| `custody.one_shot_no_feedback_barrier` | `UNBOUND` | No enforced one-shot no-feedback custody wrapper is bound. |
| `custody.protected_panel_freshness` | `UNBOUND` | Protected panel identity and freshness remain CANNOT_CHECK. |
| `inputs.candidate_visible_case_bytes` | `UNBOUND` | No exact P5 candidate-visible case packet is frozen. |
| `model_provider.fallbacks` | `UNBOUND` | Fallback identities and closed fallback behaviour are unbound. |
| `model_provider.primary` | `UNBOUND` | Selected model/provider/service revision, configuration and capability mapping are unbound. |
| `resources.calls_tokens_usd` | `UNBOUND` | Aggregate calls, tokens and USD caps are unbound. |
| `resources.retry_network` | `UNBOUND` | Retry, timeout, backoff and network allowlist are unbound. |
| `resources.wallclock` | `UNBOUND` | Per-case and whole-run wallclock caps are unbound. |
| `rights.container_and_generated_artifacts` | `UNBOUND` | Container/image and generated-artifact authority is not closed. |
| `rights.model_provider_and_services` | `UNBOUND` | Model/provider and external service terms are not closed. |
| `rights.task_and_benchmark_content` | `UNBOUND` | Upstream repository, issue and task-content rights are not closed. |
| `runtime.compute` | `UNBOUND` | CPU, RAM, GPU and parallelism are not selected and frozen. |
| `runtime.container_or_environment` | `UNBOUND` | No content-addressed container or complete immutable environment is frozen. |
| `runtime.dependency_lock` | `UNBOUND` | No exact dependency lock digest is frozen. |
| `runtime.task_environment` | `UNBOUND` | Isolated task checkout/container and task environment identity are unbound. |

**Residual:** execution and all comparator claims remain unlicensed.

**Next discriminator:** bind the listed value lawfully and content-address it before outcome access; rerun the outcome-free preflight. ScienceClaw may not gain a singleton via relabeling—a selector must be a separately named successor method.

## MOSS

- Arm: `C2_DIRECT_SELF_EDIT__MOSS`
- Blocking fields: **18**

| Field | State | Cause |
|---|---|---|
| `adapter.isolated_write_surface` | `UNBOUND` | The V3 synthetic write registry is specified, but no runtime enforcement/reset wrapper is bound. |
| `adapter.native_parser_binding` | `UNBOUND` | The generic V3 synthetic contract is hashed, but no arm-native runtime parser/binding is implemented or checked against native outputs. |
| `custody.external_protected_scorer` | `UNBOUND` | Independent protected scorer identity, code and access control remain CANNOT_CHECK. |
| `custody.one_shot_no_feedback_barrier` | `UNBOUND` | No enforced one-shot no-feedback custody wrapper is bound. |
| `custody.protected_panel_freshness` | `UNBOUND` | Protected panel identity and freshness remain CANNOT_CHECK. |
| `inputs.candidate_visible_case_bytes` | `UNBOUND` | No exact P5 candidate-visible case packet is frozen. |
| `model_provider.fallbacks` | `UNBOUND` | Fallback identities and closed fallback behaviour are unbound. |
| `model_provider.primary` | `UNBOUND` | Authenticated coding-agent CLI, model, provider, endpoint and revision are unbound. |
| `resources.calls_tokens_usd` | `UNBOUND` | Aggregate calls, tokens and USD caps are unbound. |
| `resources.retry_network` | `UNBOUND` | Retry, timeout, backoff and network allowlist are unbound. |
| `resources.wallclock` | `UNBOUND` | Per-case and whole-run wallclock caps are unbound. |
| `rights.container_and_generated_artifacts` | `UNBOUND` | Docker/host mutation authority and generated-session artifact rights are not closed. |
| `rights.model_provider_and_services` | `UNBOUND` | Model/provider and external service terms are not closed. |
| `rights.task_and_benchmark_content` | `UNBOUND` | Session/failure artifacts and any external task or benchmark content rights are not closed. |
| `runtime.compute` | `UNBOUND` | CPU, RAM, GPU and parallelism are not selected and frozen. |
| `runtime.container_or_environment` | `UNBOUND` | No content-addressed container or complete immutable environment is frozen. |
| `runtime.dependency_lock` | `UNBOUND` | No exact dependency lock digest is frozen. |
| `runtime.task_environment` | `UNBOUND` | No exact matched task/harness/runtime environment is frozen. |

**Residual:** execution and all comparator claims remain unlicensed.

**Next discriminator:** bind the listed value lawfully and content-address it before outcome access; rerun the outcome-free preflight. ScienceClaw may not gain a singleton via relabeling—a selector must be a separately named successor method.

## Darwin Godel Machine

- Arm: `C3_ARCHIVE_BASED_SELF_EDIT__DGM`
- Blocking fields: **18**

| Field | State | Cause |
|---|---|---|
| `adapter.isolated_write_surface` | `UNBOUND` | The V3 synthetic write registry is specified, but no runtime enforcement/reset wrapper is bound. |
| `adapter.native_parser_binding` | `UNBOUND` | The generic V3 synthetic contract is hashed, but no arm-native runtime parser/binding is implemented or checked against native outputs. |
| `custody.external_protected_scorer` | `UNBOUND` | Independent protected scorer identity, code and access control remain CANNOT_CHECK. |
| `custody.one_shot_no_feedback_barrier` | `UNBOUND` | No enforced one-shot no-feedback custody wrapper is bound. |
| `custody.protected_panel_freshness` | `UNBOUND` | Protected panel identity and freshness remain CANNOT_CHECK. |
| `inputs.candidate_visible_case_bytes` | `UNBOUND` | No exact P5 candidate-visible case packet is frozen. |
| `model_provider.fallbacks` | `UNBOUND` | Fallback identities and closed fallback behaviour are unbound. |
| `model_provider.primary` | `UNBOUND` | Selected model/provider/service revision, configuration and capability mapping are unbound. |
| `resources.calls_tokens_usd` | `UNBOUND` | Aggregate calls, tokens and USD caps are unbound. |
| `resources.retry_network` | `UNBOUND` | Retry, timeout, backoff and network allowlist are unbound. |
| `resources.wallclock` | `UNBOUND` | No effective whole-attempt timeout outside coding_agent is frozen. |
| `rights.container_and_generated_artifacts` | `UNBOUND` | Docker authority and untrusted generated-code isolation/retention rights are not closed. |
| `rights.model_provider_and_services` | `UNBOUND` | Model/provider and external service terms are not closed. |
| `rights.task_and_benchmark_content` | `UNBOUND` | SWE-bench framework, benchmark data, project, tests and patch rights are not closed. |
| `runtime.compute` | `UNBOUND` | CPU, RAM, GPU and parallelism are not selected and frozen. |
| `runtime.container_or_environment` | `UNBOUND` | No content-addressed container or complete immutable environment is frozen. |
| `runtime.dependency_lock` | `UNBOUND` | No exact dependency lock digest is frozen. |
| `runtime.task_environment` | `UNBOUND` | Task/harness subset, prepared benchmark environment and treatment of the pinned argparse-choice defect are unbound. |

**Residual:** execution and all comparator claims remain unlicensed.

**Next discriminator:** bind the listed value lawfully and content-address it before outcome access; rerun the outcome-free preflight. ScienceClaw may not gain a singleton via relabeling—a selector must be a separately named successor method.

## ADIAS

- Arm: `C4_ISSUE_CENTRIC_OPTIMIZATION__ADIAS`
- Blocking fields: **18**

| Field | State | Cause |
|---|---|---|
| `adapter.isolated_write_surface` | `UNBOUND` | The native write allow-list conflict is unresolved; the synthetic registry does not enforce the runtime surface. |
| `adapter.native_parser_binding` | `UNBOUND` | The generic V3 synthetic contract is hashed, but no arm-native runtime parser/binding is implemented or checked against native outputs. |
| `custody.external_protected_scorer` | `UNBOUND` | Independent protected scorer identity, code and access control remain CANNOT_CHECK. |
| `custody.one_shot_no_feedback_barrier` | `UNBOUND` | No enforced one-shot no-feedback custody wrapper is bound. |
| `custody.protected_panel_freshness` | `UNBOUND` | Protected panel identity and freshness remain CANNOT_CHECK. |
| `inputs.candidate_visible_case_bytes` | `UNBOUND` | No exact P5 candidate-visible case packet is frozen. |
| `model_provider.fallbacks` | `UNBOUND` | Fallback identities and closed fallback behaviour are unbound. |
| `model_provider.primary` | `UNBOUND` | Selected model/provider/service revision, configuration and capability mapping are unbound. |
| `resources.calls_tokens_usd` | `UNBOUND` | Aggregate calls, tokens and USD caps are unbound. |
| `resources.retry_network` | `UNBOUND` | Retry, timeout, backoff and network allowlist are unbound. |
| `resources.wallclock` | `UNBOUND` | Per-case and whole-run wallclock caps are unbound. |
| `rights.container_and_generated_artifacts` | `UNBOUND` | Container/image and generated-artifact authority is not closed. |
| `rights.model_provider_and_services` | `UNBOUND` | Model/provider and public-search service terms are not closed. |
| `rights.task_and_benchmark_content` | `UNBOUND` | ADIAS source use is restricted by CC BY-NC-SA and third-party benchmark/environment rights are not closed. |
| `runtime.compute` | `UNBOUND` | CPU, RAM, GPU and parallelism are not selected and frozen. |
| `runtime.container_or_environment` | `UNBOUND` | No content-addressed container or complete immutable environment is frozen. |
| `runtime.dependency_lock` | `UNBOUND` | No exact dependency lock digest is frozen. |
| `runtime.task_environment` | `UNBOUND` | Dependency/container/domain identity, optimize_option and path policy are unbound. |

**Residual:** execution and all comparator claims remain unlicensed.

**Next discriminator:** bind the listed value lawfully and content-address it before outcome access; rerun the outcome-free preflight. ScienceClaw may not gain a singleton via relabeling—a selector must be a separately named successor method.

## Double Ratchet metric-only

- Arm: `C5_EVALUATOR_ONLY__DOUBLE_RATCHET_METRIC_ONLY`
- Blocking fields: **18**

| Field | State | Cause |
|---|---|---|
| `adapter.isolated_write_surface` | `UNBOUND` | The V3 synthetic write registry is specified, but no runtime enforcement/reset wrapper is bound. |
| `adapter.native_parser_binding` | `UNBOUND` | The generic evaluator-front contract exists, but no native adapter or protected-custody wrapper is implemented and hashed. |
| `custody.external_protected_scorer` | `UNBOUND` | Independent protected scorer identity, code and access control remain CANNOT_CHECK. |
| `custody.one_shot_no_feedback_barrier` | `UNBOUND` | Official eval_locked flow is not protected-custody safe without a bound development-surrogate and one-shot wrapper. |
| `custody.protected_panel_freshness` | `UNBOUND` | Protected panel identity and freshness remain CANNOT_CHECK. |
| `inputs.candidate_visible_case_bytes` | `UNBOUND` | P5 dossier bytes, frozen solver identity and development-only locked surrogate are unbound. |
| `model_provider.fallbacks` | `UNBOUND` | Fallback identities and closed fallback behaviour are unbound. |
| `model_provider.primary` | `UNBOUND` | Bedrock revision, role mapping, detector and embedding service identities, region and frozen solver configuration are unbound. |
| `resources.calls_tokens_usd` | `UNBOUND` | Aggregate calls, tokens and USD caps are unbound. |
| `resources.retry_network` | `UNBOUND` | Retry, timeout, backoff and network allowlist are unbound. |
| `resources.wallclock` | `UNBOUND` | Per-case and whole-run wallclock caps are unbound. |
| `rights.container_and_generated_artifacts` | `UNBOUND` | Container/image and generated-artifact authority is not closed. |
| `rights.model_provider_and_services` | `UNBOUND` | Amazon Bedrock permissions, pricing, quotas and optional service terms are not closed. |
| `rights.task_and_benchmark_content` | `UNBOUND` | MBPP+, Spider 2.0-Snow/Snowflake, report-generation data/evaluator and P5 panel rights are not closed. |
| `runtime.compute` | `UNBOUND` | CPU, RAM, GPU and parallelism are not selected and frozen. |
| `runtime.container_or_environment` | `UNBOUND` | No content-addressed container or complete immutable environment is frozen. |
| `runtime.dependency_lock` | `UNBOUND` | No exact dependency lock digest is frozen. |
| `runtime.task_environment` | `UNBOUND` | P5 task-output generator and selected default-versus-reproduction regime are unbound. |

**Residual:** execution and all comparator claims remain unlicensed.

**Next discriminator:** bind the listed value lawfully and content-address it before outcome access; rerun the outcome-free preflight. ScienceClaw may not gain a singleton via relabeling—a selector must be a separately named successor method.

## ScienceClaw

- Arm: `C6_MODERN_SOURCE_GROUNDED__SCIENCECLAW`
- Blocking fields: **18**

| Field | State | Cause |
|---|---|---|
| `adapter.isolated_write_surface` | `UNBOUND` | The V3 synthetic write registry is specified, but no runtime enforcement/reset wrapper is bound. |
| `adapter.native_parser_binding` | `UNSUPPORTED` | ScienceClaw has no native supported singleton; implementing a selector would be a material successor method, not an adapter binding. |
| `custody.external_protected_scorer` | `UNBOUND` | Independent protected scorer identity, code and access control remain CANNOT_CHECK. |
| `custody.one_shot_no_feedback_barrier` | `UNBOUND` | No enforced one-shot no-feedback custody wrapper is bound. |
| `custody.protected_panel_freshness` | `UNBOUND` | Protected panel identity and freshness remain CANNOT_CHECK. |
| `inputs.candidate_visible_case_bytes` | `UNBOUND` | No exact P5 candidate-visible case packet is frozen. |
| `model_provider.fallbacks` | `UNBOUND` | Fallback identities and closed fallback behaviour are unbound. |
| `model_provider.primary` | `UNBOUND` | All model/provider/scientific service identities and capability mapping are unbound. |
| `resources.calls_tokens_usd` | `UNBOUND` | All P5 tool-call, token and USD values are unbound. |
| `resources.retry_network` | `UNBOUND` | Retry, timeout, backoff and network allowlist are unbound. |
| `resources.wallclock` | `UNBOUND` | Per-case and whole-run wallclock caps are unbound. |
| `rights.container_and_generated_artifacts` | `UNBOUND` | Generated-artifact rights and retention/redistribution authority are not closed. |
| `rights.model_provider_and_services` | `UNBOUND` | Scientific APIs, Infinite service, model/provider and tool-service terms are not closed. |
| `rights.task_and_benchmark_content` | `UNBOUND` | Tool datasets, topic/case and protected-panel rights are not closed. |
| `runtime.compute` | `UNBOUND` | CPU, RAM, GPU and parallelism are not selected and frozen. |
| `runtime.container_or_environment` | `UNBOUND` | No content-addressed container or complete immutable environment is frozen. |
| `runtime.dependency_lock` | `UNBOUND` | No exact dependency lock digest is frozen. |
| `runtime.task_environment` | `UNBOUND` | Profile, tools, optional dependencies, artifact reset, dry-run mode, topic-to-case adapter and scientific service revisions are unbound. |

**Residual:** execution and all comparator claims remain unlicensed.

**Next discriminator:** bind the listed value lawfully and content-address it before outcome access; rerun the outcome-free preflight. ScienceClaw may not gain a singleton via relabeling—a selector must be a separately named successor method.

## Panel disposition

- Confirmatory-ready arms: **0/6**
- Blocking field instances: **108**
- H1–H4, protected freshness, performance, harm, and superiority remain `CANNOT_CHECK`.

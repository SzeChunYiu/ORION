# P5 C5 Double Ratchet V4 negative ledger

**Outcome-blind status:** 9/21 fields BOUND; 12/21 blocking; execution refused.

No benchmark, native result, metric database, protected panel or protected score was opened. Synthetic/native-shaped fixtures are conformance-only.

## Blocking fields

| Field | State | Cause | Next discriminator |
|---|---|---|---|
| `custody.external_protected_scorer` | CANNOT_CHECK | No independent scorer principal, immutable scorer digest, access-control identity or signed acceptance exists. | Independent custodian supplies scorer identity, digest and access-control attestation without revealing protected bytes. |
| `custody.one_shot_no_feedback_barrier` | CANNOT_CHECK | The official runner reports its eval_locked value every round and at stdout; no independent one-shot handoff/no-return-channel receipt exists. | Custodian signs one accepted artifact, one protected scoring event and no feedback path; verify the protected panel was never mounted during evolution. |
| `custody.protected_panel_freshness` | CANNOT_CHECK | No post-protocol protected panel identity, commitment or freshness attestation was available. | Freeze a fresh panel only after protocol and evaluator bytes are locked, under independent custody. |
| `inputs.candidate_visible_case_bytes` | UNBOUND | The source contains no stored split or result payload. No rights-cleared P5 dossier, frozen solver-output set, development anchor or development-only locked surrogate is frozen. | Freeze one complete candidate-visible P5 development packet satisfying P5_C5_V4_CANDIDATE_VISIBLE_CASE_REQUIREMENTS.json without any protected-final bytes. |
| `model_provider.primary` | UNBOUND | Repository labels do not freeze an immutable served model revision, cross-region route, exact endpoint/TLS identity, service revision, credential principal or allowed role/capability map; frozen solver outputs are also absent. | Bind exact provider/service/model revisions and credentials, then generate solver outputs once and freeze their bytes before evaluator evolution. |
| `resources.calls_tokens_usd` | UNBOUND | Dynamic detector, synthesis, teacher and solver calls have no aggregate call, input-token, output-token or USD hard stop; provider usage reconciliation and overshoot semantics are absent. | Instrument a provider-reconciled pre-call hard-stop monitor over every role and retry, with exact aggregate caps and typed exhaustion terminal. |
| `resources.retry_network` | UNBOUND | Retry bytes are known, but the Bedrock route/DNS/TLS endpoint, offline dataset policy and deny-by-default egress network are not independently bound or enforced. | Bind one provider endpoint and an attested egress network that denies Hugging Face/task fetch and every other destination. |
| `rights.container_and_generated_artifacts` | UNBOUND | No content-addressed runtime image/SBOM/complete notices or authority for prompts, solver outputs, task traces, metric.db and result.json retention/publication is closed. | Build the full image, capture SBOM/licences and obtain explicit retention/disclosure authority for all generated artifacts. |
| `rights.model_provider_and_services` | UNBOUND | No authorized Bedrock credential principal, study-use/data-retention terms, cross-region policy, pricing/quota receipt or publication permission is frozen. | Bind provider terms, data policy, credential principal, region/route and aggregate-result publication rights. |
| `rights.task_and_benchmark_content` | UNBOUND | The repository explicitly excludes datasets/results. MBPP+/Hugging Face, P5 dossiers, development anchors and final protected panel have separate licences/terms not captured here. | Use an authored or explicitly licensed P5 development packet plus an independently licensed protected panel and scorer. |
| `runtime.container_or_environment` | UNBOUND | No content-addressed Linux image containing Python 3.11, the exact lock, timeout tooling and source runtime has been built, SBOMed and smoke-verified. | Build once from the lock on the selected Linux architecture, capture image/SBOM digests and run only synthetic/native-shaped smoke. |
| `runtime.task_environment` | UNBOUND | The official entrypoint supports MBPP/report_gen, not the P5 dossier or eight-class decision. It regenerates hosted solver outputs at run time and uses eval_locked each round; no P5-native task adapter or frozen development-output environment exists. | Preregister and byte-freeze a P5-native evaluator-only adapter that consumes already frozen solver outputs, uses a development-only surrogate, and leaves the final protected panel external. |

## Scientific defects

### C5D1_SOLVER_OUTPUTS_REGENERATED — UNBOUND

**Cause:** solve_real_outputs calls the hosted agent for train, eval_dev and eval_locked during each run; source/model labels do not byte-freeze outputs.

**Residual:** The supposed evaluator-only arm does not yet hold realized solver outputs fixed across attempts/arms.

**Next discriminator:** Freeze solver outputs before evolution and require their complete pre/post tree digest to match.

### C5D2_LOCKED_REPORTED_EACH_ROUND — CANNOT_CHECK

**Cause:** evolve_metric_expr calls _report_locked each round, stores locked_report_agreement, writes final_locked_agreement and prints locked to stdout.

**Residual:** The final protected panel cannot be used as native eval_locked; only a candidate-visible development surrogate is admissible.

**Next discriminator:** Externally attest that native eval_locked is development-only and score the final evaluator once on a separate protected panel.

### C5D3_NO_P5_NATIVE_DATASET_OR_CLASS — UNSUPPORTED

**Cause:** SUPPORTED_DATASETS is mbpp/report_gen and the native result exposes metric statistics, not a P5 one-of-eight responsibility decision.

**Residual:** A P5 adapter is a separately named semantic bridge, not evidence that the released code natively solves P5.

**Next discriminator:** Preregister an evaluator-only P5 adapter and validate its fibres with synthetic/native-shaped cases only.

### C5D4_SOURCE_HAS_NO_DATA_OR_RESULTS — CANNOT_CHECK

**Cause:** Authoritative tree has 0 stored split payload paths and 0 result payload paths.

**Residual:** No task, result or performance claim can be reconstructed from source metadata.

**Next discriminator:** Acquire separately licensed development content without opening any final protected outcome.

### C5D5_README_DEPENDENCY_OMISSION — PRESERVED_REPAIRED_IN_V4_LOCK

**Cause:** README lists pydantic/pyyaml/boto3, while the default MBPP loader imports the Hugging Face datasets package at runtime.

**Residual:** V4 lock adds datasets explicitly; no claim is made that a future P5 adapter has no further dependencies.

**Next discriminator:** Build from the lock and preserve artifacts; amend only with explicit adapter identity.

### C5D6_METRIC_FIXTURES_NOT_PERFORMANCE — CANNOT_CHECK

**Cause:** Synthetic/native-shaped parser cases test mapping and refusal only.

**Residual:** They license zero raw singletons and say nothing about H1-H4, transfer, harm, preservation, performance or superiority.

**Next discriminator:** Use the independently custodied one-shot panel after 6/6 matched arm readiness.

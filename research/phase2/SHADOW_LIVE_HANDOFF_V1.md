# Phase-2 external binding handoff V1

The frozen Shadow trial is intentionally not executable until the final Phase-1 subject, real provider stack, protected evaluator, evaluation epoch, matched baseline and resource budget are bound by the host. These bindings must not require editing the frozen task or attack definitions.

## Repository-only status

```bash
python -m orion.benchmarks phase2-preflight
```

Phase 1 is now technically closed, but a repository-only preflight must still fail closed until the host binds the exact final subject revision and external provider/evaluator identities. A missing binding is not a failure of the research task and must not be converted into PASS.

## Host binding file

Create a JSON file outside the candidate's authority boundary:

```json
{
  "schema": "Phase2ClosureBinding.v1",
  "protocol_id": "phase2-shadow-closure-v1",
  "subject_revision_hash": "<sha256 of exact final Phase-1 subject revision identity>",
  "provider_manifest_hash": "<sha256 of content-addressed real-provider manifest>",
  "evaluator_artifact_hash": "<sha256 of independently protected evaluator artifact>",
  "evaluation_epoch_id": "<frozen epoch/split campaign>",
  "baseline_id": "simple-llm-retrieval-baseline-v1",
  "resource_budget_units": 100.0
}
```

Then run:

```bash
python -m orion.benchmarks phase2-preflight --binding /path/to/phase2-binding.json
```

A fully bound file yields `READY_TO_EXECUTE_SHADOW_TRIAL` plus the immutable live-trial packet fingerprint. It still yields `grants_phase2_closure: false` and `grants_governed_self_orion: false` because bindings are only prerequisites for empirical execution.

## Frozen-vs-host-owned boundary

Host binding may supply identities and resource limits only. Wide/deep task prompts, success criteria, split identities and the ten authority attacks remain frozen in `phase2_preflight.py`; extra `tasks` or `authority_attack_ids` fields in a binding file have no effect. A material task/evaluator protocol change requires a new protocol/epoch rather than an in-place outcome-aware edit.

The consequential Shadow self-development trial is deliberately **not** pre-filled with a synthetic failure. Gate B begins when an actual consequential failure is observed; its discriminator must then be frozen before repair outcome access and the existing `ShadowSelfDrivingController` must carry the case through research, candidate execution, protected assurance and at most host-promotion recommendation.

## Raw live-trial trace requirement

Construct the real trial runtime with `ShadowLiveTrialRunner.from_providers(...)`. That constructor wraps the host retrieval provider transparently and retains, per frozen task:

- each raw `SearchQuery` including route/domain identity;
- the complete returned `RetrievedItem` content and source URI;
- the mechanic receipt/use trace;
- solution evidence IDs and all evidence absorbed into ORION state;
- `retrieved_but_unused_ids` and `retrieved_but_unabsorbed_ids` for attribution.

The resulting `ShadowLiveTrialReport` exposes `raw_search_trace_retained` and a deterministic `evidence_artifact_hash` over the raw search/document/use trace. A Phase-2 Gate-A receipt is incomplete if raw trace retention is false, even if the task-level score looks good.

This instrumentation does not change provider outputs and does not convert retrieval into scientific authority. It exists so the protected evaluator can distinguish present-but-missed, retrieved-but-unused, absorption/interpretation and later routing/saturation failures where the hidden gold permits that classification.

Persist the raw report artifact outside candidate-controlled state together with the frozen packet fingerprint, provider manifest, evaluator artifact, resource accounting and matched-baseline outputs. Do not replace raw documents with counts-only summaries.

## Evidence handback

After the live research trial, consequential Shadow development cycle and hostile evaluator battery have actually run, external evidence must be handed back through `ExternalEvidenceManifest.v1` and assessed with:

```bash
python -m orion.benchmarks external-status --manifest /path/to/external-manifest.json
```

Missing external criteria remain `CANNOT_CHECK`; verified negative results remain `FAIL`. Neither command, a trial score, nor a host-promotion recommendation grants self-merge or promotion authority.

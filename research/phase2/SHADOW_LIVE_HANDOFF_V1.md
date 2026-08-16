# Phase-2 external binding handoff V1

The frozen Shadow trial is intentionally not executable until the final Phase-1 subject, real provider stack, protected evaluator, evaluation epoch, matched baseline and resource budget are bound by the host. These bindings must not require editing the frozen task or attack definitions.

## Repository-only status

```bash
python -m orion.benchmarks phase2-preflight
```

Expected status before Phase 1 closes:

```text
BIND_FINAL_PHASE1_SUBJECT
```

This is a fail-closed result, not a failure of the research task.

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

After the trial, external evidence must be handed back through `ExternalEvidenceManifest.v1` and assessed with:

```bash
python -m orion.benchmarks external-status --manifest /path/to/external-manifest.json
```

Neither command grants self-merge or promotion authority.

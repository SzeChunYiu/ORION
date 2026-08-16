# External evidence manifest handoff

The remaining flagship external work is executed outside ORION's own authority boundary. The host/evaluator writes a JSON `ExternalEvidenceManifest.v1`; ORION validates the bindings and derives paper status.

## Command

Repository-only boundary:

```bash
python -m orion.benchmarks external-status
```

Host-produced evidence:

```bash
python -m orion.benchmarks external-status --manifest /path/to/external-manifest.json
```

The command prints one JSON report containing local-suite status, P1–P5 external PASS/FAIL/CANNOT_CHECK, blockers, and `publication_ready`.

## Manifest shape

```json
{
  "manifest_id": "external-campaign:<id>",
  "subject_revision_hash": "<sha256>",
  "evaluator_artifact_hash": "<sha256>",
  "evaluation_epoch_id": "<frozen epoch>",
  "records": [
    {
      "paper_id": "P4",
      "criterion": "P4_EVALUATOR_LOCKED",
      "evidence_artifact_id": "<artifact identity>",
      "evidence_artifact_hash": "<sha256>",
      "subject_revision_hash": "<same subject sha256>",
      "evaluator_artifact_hash": "<same evaluator sha256>",
      "producer_process_lineage_hash": "<sha256>",
      "verifier_process_lineage_hash": "<different sha256>",
      "evaluation_epoch_id": "<same frozen epoch>",
      "split_id": "<fresh split identity>",
      "status": "PASS | FAIL | CANNOT_CHECK",
      "frozen_before_candidate": true,
      "fresh_split": true,
      "note": "what externally verified artifact establishes this criterion"
    }
  ]
}
```

The example describes the schema only. It is **not** a PASS manifest and must not be copied with invented hashes/statuses.

## Required external criteria

The canonical list is the `ExternalCriterion` enum in `src/orion/benchmarks/external_evidence.py`.

- P1: hidden-formulation tasks, static-workflow baseline, tree/agent baseline, resource match, hidden labels, fresh cases, root outcome, unnecessary-reframe outcome.
- P2: complete-gold denominator, matched simple baseline, frozen provider trajectory, system-vs-baseline result.
- P3: 3+ domain case, multiple operationalizations, source-projection gold, mapping gold, long-context/RAG/flat-schema baselines, semantic ablation, false-integration and recoverability outcomes.
- P4: source-attribution benchmark, search contamination audit, evaluator lock, heldout access log, matched verifier baseline, false-promotion outcome.
- P5: direct-self-edit baseline, agent-design baseline, hidden failure causes, fresh transfer, evaluator lock, negative-history completeness, protected-access log, root improvement outcome.

A missing record is `CANNOT_CHECK`, not FAIL. A verified negative result is FAIL, not `CANNOT_CHECK`. Only complete independently verified PASS records can make a paper's external gate PASS.

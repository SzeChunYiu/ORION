# Q3 reproduction guide

Q3 is currently scoped to a **systems/benchmark-definition paper with one frozen live measurement**.

## Harness publication contract

From repository root:

```bash
pytest packages/orion-research-harness/tests/test_publication_contract.py \
       packages/orion-research-harness/tests/test_invalid_content_recovery.py
```

The first test binds the manuscript-facing harness contract to current implementation. The second reproduces the repaired malformed-success receipt behavior discovered during the original live run.

The machine-facing contract lives at:

`packages/orion-research-harness/src/orion_research_harness/publication_contract.py`

It deliberately grants no scientific, novelty or security authority.

## General harness tests

When preparing a release, also run the package test suite according to the repository's normal environment, e.g.:

```bash
pytest packages/orion-research-harness/tests
```

Do not reinterpret a green package suite as evidence that Benchmark V0 predicts scientific correctness.

## Benchmark V0 evidence

Frozen protocol/results and raw receipts are under:

`development/orion-q-max-r0/dual-harness-benchmark-v0/`

The permitted manuscript claim is one measurement: the two instruments agreed on the registered diagnosis/move and later R6P/R6Q outcomes were scored `ALIGNED` under the frozen deferred coordinate.

## Q-series synchronization

```bash
pytest tests/unit/publication/test_framework_snapshot.py \
       tests/unit/publication/test_q_series_final_spec.py \
       tests/unit/publication/test_q_series_content_binding.py
```

The >=20-item prospective agreement/calibration protocol is successor research only. No result under that protocol is claimed by Q3 V2.

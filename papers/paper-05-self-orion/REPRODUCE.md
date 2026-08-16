# ORION-P5 reproduction and protected-study handoff

P5 remains `CANNOT_CHECK`: there is no frozen private hidden-cause suite or external result archive in the public repository yet. This file documents the reproducible host-side transition without weakening freshness or evaluator custody.

## 1. Unit-test the freeze boundary

```bash
PYTHONPATH=src pytest -q tests/test_p5_hidden_cause_freeze.py
```

The tests cover all eight root-cause families, protected-field non-disclosure, salted low-entropy root commitments, content-hash mutation rejection, independent fresh-axis enforcement, replay/fresh separation, negative-variant retention, nonce uniqueness and write-surface separation.

## 2. Create the private suite outside challenger custody

Follow `protocol/HIDDEN_CAUSE_CASE_SCHEMA_V1.json`, `protocol/FRESH_TRANSFER_POLICY_V1.md`, and `protocol/PROTECTED_SUITE_FREEZE_V1.md`. The private input must never be committed to a candidate-readable branch.

## 3. Freeze candidate/public and commitment artifacts

```bash
PYTHONPATH=src python -m orion.study.p5 \
  --protected-suite /protected/p5-suite.json \
  --candidate-packet artifacts/p5-candidate-packet.json \
  --commitment artifacts/p5-protected-commitment.json
```

Preserve the private opening material under evaluator custody. The public candidate packet deliberately contains no protected root label, fresh payload, protected surface, scoring rubric, harmful/null payload or opening nonce.

## 4. Bind the final execution identities prospectively

Do not partially edit `PROTOCOL_V1.json`. The execution transition must bind the exact final subject revision, hidden-cause suite/split hashes, provider/model revisions, baseline config hashes, evaluator hash and evaluation epoch together, then satisfy the programme validator for `EXECUTION_FROZEN` before any final outcome access.

## 5. Run the external study

The study still depends on issue #8 and issue #76 for real live-provider/protected evidence on the exact final subject. Run the registered baselines/ablations under matched resources, preserve every failure/null/harmful candidate, and retain raw motivating/replay/fresh results plus evaluator/access logs.

## 6. Generate publication outputs only from immutable results

P5-T1 is a literature disposition artifact and may exist before outcomes. P5-T2/P5-T3 and plots P5-1..P5-7 must be regenerated from the immutable external result archive. No repository CI, local structural test, replay-only win, or internal readiness state can substitute for the missing protected fresh-transfer evidence.

# ORION-P5 reproduction and protected-study handoff

P5 remains `CANNOT_CHECK` for H1–H4. The only result-bearing archive in the public tree is the diagnostic glm-5.2 attribution JSONL (**21/24**, three residual errors retained). This file documents (a) how to regenerate publication tables from that archive and (b) the host-side transition for a future protected campaign.

## 1. Regenerate tables from archived records (no live provider)

```bash
make paper05-results
```

Equivalent:

```bash
PYTHONPATH=src python -m orion.study.p5.tables
```

The generator:

- recomputes 21/24 from `evidence/glm-5.2-attribution/results.jsonl`;
- refuses a 24-of-24 rewrite or dropped residual errors (exit 2);
- writes Table P5-3 and the residual-error ledger;
- writes `CANNOT_CHECK` stubs (no numbers) for P5-2, P5-4, P5-5, P5-6, P5-7 and Tables P5-T2/P5-T3;
- returns exit 3 if the archive is missing.

Targeted tests:

```bash
PYTHONPATH=src pytest -q tests/test_p5_attribution_tables.py tests/test_p5_hidden_cause_freeze.py tests/test_p5_protocol_v2.py
```

## 2. Unit-test the freeze boundary

```bash
PYTHONPATH=src pytest -q tests/test_p5_hidden_cause_freeze.py
```

The tests cover all eight root-cause families, protected-field non-disclosure, salted low-entropy root commitments, content-hash mutation rejection, independent fresh-axis enforcement, replay/fresh separation, negative-variant retention, nonce uniqueness and write-surface separation.

## 3. Create the private suite outside challenger custody

Follow `protocol/HIDDEN_CAUSE_CASE_SCHEMA_V1.json`, `protocol/FRESH_TRANSFER_POLICY_V1.md`, and `protocol/PROTECTED_SUITE_FREEZE_V1.md`. The private input must never be committed to a candidate-readable branch.

## 4. Freeze candidate/public and commitment artifacts

```bash
PYTHONPATH=src python -m orion.study.p5 \
  --protected-suite /protected/p5-suite.json \
  --candidate-packet artifacts/p5-candidate-packet.json \
  --commitment artifacts/p5-protected-commitment.json
```

Preserve the private opening material under evaluator custody. The public candidate packet deliberately contains no protected root label, fresh payload, protected surface, scoring rubric, harmful/null payload or opening nonce.

## 5. Bind the final execution identities prospectively

Do not partially edit `PROTOCOL_V1.json`. The execution transition must bind the exact final subject revision, hidden-cause suite/split hashes, provider/model revisions, baseline config hashes, evaluator hash and evaluation epoch together, then satisfy the programme validator for `EXECUTION_FROZEN` before any final outcome access.

## 6. Run the external study

The study still depends on issue #8 and issue #76 for real live-provider/protected evidence on the exact final subject. A live campaign must not start unless credentials exist **and** the #8 packet is fail-closed bound. In the 2026-08-17 paper-102 session both conditions failed, so no new live run was started.

Run the registered baselines/ablations under matched resources, preserve every failure/null/harmful candidate, and retain raw motivating/replay/fresh results plus evaluator/access logs.

## 7. Generate publication outputs only from immutable results

P5-T1 is a literature disposition artifact and may exist before outcomes. Table P5-3 may be regenerated from the diagnostic attribution JSONL. P5-T2/P5-T3 and plots P5-2/P5-4/P5-5/P5-6/P5-7 remain `CANNOT_CHECK` until an immutable external result archive exists. No repository CI, local structural test, replay-only win, diagnostic 21/24 score, or internal readiness state can substitute for the missing protected fresh-transfer evidence.

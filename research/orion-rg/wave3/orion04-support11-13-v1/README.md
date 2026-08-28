# ORION-04 Wave 3 M4 replay packet

This is a bounded, fail-closed successor to the M3 support-10 theorem. It excludes every support-11, support-12, and support-13 multiplicity/rank branch and promotes only the theorem `support >= 14`.

From the repository root:

```bash
python research/orion-rg/wave3/orion04-support11-13-v1/run_replay.py
python research/orion-rg/wave3/orion04-support11-13-v1/independent_checker/check_result.py
pytest -q tests/research/test_orion04_wave3_m4_packet.py
```

The source runner compiles four already-committed C sources in a temporary directory, records exact outputs, and deletes the executables. The independent checker does not import or execute the source runner; it recomputes the multiplicity grammar and validates hashes, registered fingerprints, branch coverage, result digest, and authority flags.

The `base_revision` stored in this V1 protocol/result is the protocol-design origin, not a claim that the current checkout still has that Git head. Current-checkout authority is fail-closed on the source hashes and the focused regression test: CI re-executes the complete runner on the PR checkout, independently checks the generated receipt, and requires the generated result to equal the committed `RESULT.json` exactly. A source drift, changed search output, checker disagreement, or failed replay therefore blocks the bounded theorem promotion.

Review `THEORY.md`, `PROTOCOL.json`, `SOURCE_MANIFEST.json`, `EXPECTED_TERMINALS.json`, `RESULT.json`, and `CLAIM_DISPOSITION.md` as one packet.

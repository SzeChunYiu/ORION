# ORION-04 Wave 3 M4 replay packet

This is a bounded, fail-closed successor to the M3 support-10 theorem. It excludes every support-11, support-12, and support-13 multiplicity/rank branch and promotes only the theorem `support >= 14`.

From the repository root:

```bash
python research/orion-rg/wave3/orion04-support11-13-v1/run_replay.py
python research/orion-rg/wave3/orion04-support11-13-v1/independent_checker/check_result.py
pytest -q tests/research/test_orion04_wave3_m4_packet.py
```

The source runner compiles four already-committed C sources in a temporary directory, records exact outputs, and deletes the executables. The independent checker does not import or execute the source runner; it recomputes the multiplicity grammar and validates hashes, registered fingerprints, branch coverage, result digest, and authority flags.

Review `THEORY.md`, `PROTOCOL.json`, `SOURCE_MANIFEST.json`, `EXPECTED_TERMINALS.json`, `RESULT.json`, and `CLAIM_DISPOSITION.md` as one packet.

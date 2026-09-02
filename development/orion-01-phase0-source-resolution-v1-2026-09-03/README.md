# O01-P0-SRCRES-V1 — Phase-0 source resolution (registration lane)

Executes **Phase 0 only** (`resolve_source`) of the frozen ORION-01 successor protocol
`orion-01-production-completeness-v1-2026-08-29`: resolve the frozen prefix `dade7d46`
against `Quantomatic/pyzx`, or land on a registered adverse/cannot terminal.

- Protocol (registered before outcome): `O01_SRCRES_PROTOCOL_V1.md`
- Driver: `research/extensions/orion01/o01_srcres_phase0.py`
- Result: `research/extensions/orion01/O01_SRCRES_PHASE0_RESULTS.json`
- Run log: `RUN_O01_SRCRES_PHASE0.log`
- Phase artifacts: `SOURCE_RESOLUTION_RECEIPT.json`, `SOURCE_FILE_MANIFEST.jsonl`,
  `ENVIRONMENT_RECEIPT.json` (manifest + environment on the `SOURCE_RESOLVED` path only,
  per `EXPECTED_TERMINALS.json`)

The frozen predecessor directory is never written to; gate G0 re-runs its canonical
versioned checker (`registry_protocol_checker_v1.py`) and pins its sha256. No semantic
testing of the pinned source occurs in this phase. Scratch bare clone lives outside the
repo under `/tmp/o01-srcres-scratch/` and is recorded in the receipt.

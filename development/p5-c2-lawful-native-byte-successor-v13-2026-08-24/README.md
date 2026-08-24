# P5 C2 V13 packet

This additive packet pursues only `rights.container_and_generated_artifacts` for `C2_RIGHTS_CLEARED_SCRATCH_IMAGE_SUCCESSOR__ORION_V13`.

- Frozen before Docker server startup: `P5_C2_V13_EXECUTION_FREEZE.json`
- Complete build context: `BUILD_CONTEXT_MANIFEST_V13.json`
- Deterministic ELF: `probe/generate_aarch64_probe_v13.py`, `PROBE_GENERATION_RECEIPT_V13.json`
- Image rights and authority: `P5_C2_V13_IMAGE_CONTENT_RIGHTS_MAP.json`, `P5_C2_V13_GENERATED_ARTIFACT_AUTHORITY.json`
- Full licenses: `licenses/`
- Direct layer inventory and SPDX: `ROOTFS_LAYER_MANIFEST_V13.json`, `IMAGE_SBOM_V13.spdx.json`
- Runtime and empty diff: `RUNTIME_RECEIPT_V13.json`, `transcripts/`
- Archive and disposal: `IMAGE_ARCHIVE_RECEIPT_V13.json`, `DISPOSAL_RECEIPT_V13.json`
- Result: `P5_C2_V13_RESULT.json`

Run the read-only validator from the repository root:

```bash
rtk python3 development/p5-c2-lawful-native-byte-successor-v13-2026-08-24/validate_p5_c2_v13_packet.py
```

No pytest or repository CI is required or authorized for this packet.

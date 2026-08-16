# Verified Structural Transfer V2

This directory is the additive productionization layer for the locally falsified V1 prototypes from PR #131.

## Authority boundary

Everything here is **local engineering infrastructure or a future-study design artifact**. It does not modify any frozen ORION-P1..P5 V1 protocol, does not mark outcome access, and does not create execution or publication authority. Each paper manifest is mechanically constrained to:

- `status = V2_FUTURE_STUDY`;
- `outcome_accessed = false`;
- `execution_authority = NONE`;
- `v1_protocol_mutated = false`;
- `local_evidence_authority = LOCAL_ENGINEERING_ONLY`;
- `requires_new_protocol_version = true`.

## Runtime surface

`orion.transfer.v2` adds canonical serialization, SHA-256 content identities, a collision-rejecting transfer registry, transfer decision receipts, deterministic portfolio construction and replay verification. Paper-specific wrappers live in `p1.py` through `p5.py`.

The CLI supports:

```bash
python -m orion.transfer.v2 portfolio \
  --catalog research/verified-structural-transfer-v2/fixtures/CANDIDATE_CATALOG_V2.json \
  --target research/verified-structural-transfer-v2/fixtures/KNOWN_ANSWER_TARGET_V2.json \
  --evidence research/verified-structural-transfer-v2/fixtures/KNOWN_ANSWER_EVIDENCE_V2.json \
  --min-independent-domains 1

python -m orion.transfer.v2 validate-manifest \
  --manifest research/verified-structural-transfer-v2/manifests/ORION-P1.json
```

The fixture catalog is a known-answer engineering artifact, not a scientific benchmark.

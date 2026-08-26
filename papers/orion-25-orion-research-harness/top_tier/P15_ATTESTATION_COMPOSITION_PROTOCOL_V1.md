# ORION-25 cryptographic attestation composition protocol V1

**Programme:** #977  
**Purpose:** absorb a signed/proof-of-execution donor layer rather than treating cryptographic binding as a weak baseline, and test whether SEI composes above it without confusing signature validity with scientific validity.

## Freeze chronology

This protocol is committed before the signing/verification runner and outcome. It reuses the already-frozen 22-case provenance-interoperability corpus and its independent scientific dispositions. No scientific case/gold is changed.

## Attestation donor

Use Ed25519 from the production `cryptography` package. The experiment uses a fixed test-only 32-byte private-key seed so canonical receipts and byte replay are deterministic. This is **not** a key-management/security-performance claim.

For each case:

1. canonicalize the complete normalized execution-integrity fact vector used in `P15_PROVENANCE_INTEROP_PROTOCOL_V1`;
2. sign those bytes with Ed25519;
3. verify the signature with the corresponding public key;
4. verify a tamper attack in which one bound execution field is changed after signing and signature verification must fail.

The signed payload must exclude:

- scientific validity/disposition;
- claim authority;
- hidden scientific gold.

If scientific fields enter the signed execution payload, the study fails for layer leakage.

## Systems

### ATTESTATION_ONLY

If signature verification fails, return `EXECUTION_INVALID`. If it succeeds but no independent scientific contract is supplied, return `CANNOT_CHECK` for a valid execution and `EXECUTION_INVALID` for execution-invalid cases.

This models a properly scoped attestation donor: strong execution binding, no scientific-authority overclaim.

### ATTESTATION_AS_SCIENCE hostile misuse

A deliberately invalid composition that maps a valid signed/complete execution directly to `AUTHORIZED_SCIENCE`. It exists only to measure the false-promotion consequence of collapsing layers; it is not presented as the behavior of cryptographic attestation systems in general.

### ATTESTATION_PLUS_SEI

Verify signature/binding first, then apply the same independent scientific contract and claim-authority record used by the provenance interoperability study.

## Protected endpoints

- valid signature verification rate on all frozen source payloads;
- tamper-detection rate after changing one bound execution fact;
- scientific-field leakage count into signed payload;
- `ATTESTATION_PLUS_SEI` disagreement count versus native SEI;
- `ATTESTATION_ONLY` false scientific-success count;
- hostile `ATTESTATION_AS_SCIENCE` false scientific-success count;
- false rejection/promotion on the four real workflow receipts;
- signature bytes and public-key bytes per case;
- deterministic replay;
- independent verifier agreement.

## Positive terminal

`P15_ATTESTATION_COMPOSITION_V1_SUPPORTED` requires:

- 100% valid signature verification on untampered payloads;
- 100% detection of the registered tamper attack;
- zero scientific-field leakage into signed execution payloads;
- zero native-vs-`ATTESTATION_PLUS_SEI` disposition disagreements;
- zero false scientific successes for properly scoped `ATTESTATION_ONLY`;
- at least one false scientific success for the hostile layer-collapsing misuse;
- zero false rejection/promotion on the real receipt group under `ATTESTATION_PLUS_SEI`;
- deterministic replay and independent verifier agreement.

A positive supports composition with cryptographically bound execution evidence. It does not claim a new signature scheme, production key management, remote-attestation hardware equivalence or universal superiority over proof-of-execution systems.

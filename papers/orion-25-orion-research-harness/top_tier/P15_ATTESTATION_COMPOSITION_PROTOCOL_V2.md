# ORION-25 cryptographic attestation chain-composition protocol V2

**Programme:** #977 / ORION-25 issue #979
**Purpose:** extend the V1 single-attestation study to **composed attestation chains** — multiple signed attestations (execution facts, environment facts, publication facts) in which each attestation signs the digest of the previous link — and measure which integrity properties compose, which attacks are detected, and which cannot be detected at this layer at all.

## Freeze chronology

This protocol is committed before the chain runner, the independent chain verifier, the workflow and any outcome. It reuses the already-frozen 18-case SEI fault corpus, its independent gold dispositions, and the 4 real workflow receipts exactly as normalized by `P15_PROVENANCE_INTEROP_PROTOCOL_V1` / V1 attestation composition. No scientific case, gold disposition or real fixture is changed. V1's single-attestation endpoints remain bound by V1; V2 does not reinterpret them.

## Chain structure

For every case the composer emits exactly three links, each canonical JSON (`sort_keys`, compact separators) signed with Ed25519 from the production `cryptography` package:

1. **execution link** — payload `{"role":"execution","previous_digest":GENESIS,"facts":<24-field normalized execution vector>}`;
2. **environment link** — payload `{"role":"environment","previous_digest":d1,"facts":<declared environment record>}`;
3. **publication link** — payload `{"role":"publication","previous_digest":d2,"facts":<publication record>}`.

`GENESIS = sha256(b"ORION-25-ATTESTATION-COMPOSITION-V2-GENESIS")`. `di = sha256(canonical({"payload":payload_i,"signature":sig_i_hex,"public_key_hex":pk_i_hex}))`: the chained digest covers the previous link's payload, signature **and** public key, so neither bytes nor key substitution can escape the chain.

Role keys are distinct per case and role, derived from `sha256(b"ORION-25-ATTESTATION-COMPOSITION-V2-KEY-"+role+b"-"+case_id)` as fixed test-only seeds. This is a composition-semantics experiment, **not** a key-management or hardware-attestation claim.

The declared environment record contains only fixture-declared constants (runner class label, OS image label, pinned Python version, tool id, input/output digests). The publication record contains claimed execution/occurrence identity, reap/finalization/cleanup/retry/coverage flags and a deterministic artifact URI. Runner-observed versions are recorded in the receipt as unsigned transport metadata only.

Signed payloads must exclude all scientific fields (`scientific_contract_available`, `scientific_contract_valid`, `claim_authority_available`, `claim_authority`, `scientific_disposition`). Any leakage fails the study.

## Verification systems

- **CHAIN_CRYPTO_ONLY** (properly scoped donor): verifies every signature, the digest chaining and the role/key/consistency structure. A broken chain yields `EXECUTION_INVALID`; a valid chain yields `CANNOT_CHECK` for science — never scientific success.
- **CHAIN_PLUS_SEI**: verify the chain first; only then admit the same independent scientific contract and claim-authority record used by the frozen SEI study. On untampered chains its disposition must equal the frozen native gold for every case.
- **CHAIN_AS_SCIENCE** (hostile layer-collapsing misuse): maps a cryptographically valid chain directly to `AUTHORIZED_SCIENCE`. It exists only to measure the cost of collapsing signature validity into scientific validity.

## Frozen adversarial arms

For each arm the frozen expectation is part of the protocol; outcomes are recorded, not tuned.

| arm | attack | frozen expectation |
|---|---|---|
| A-BASE | untampered chains over all 22 cases | 100% signature+chain verification; `CHAIN_PLUS_SEI` == native gold on all 22 |
| A-TRUNCATE | drop the last byte of each link's signed payload | 100% detection (signature failure) |
| A-SUBSTITUTE | flip one bound execution fact after signing, keep signatures | 100% detection (signature failure) |
| A-SPLICE | tamper execution facts, re-sign only environment+publication links (env+pub keys compromised, execution key not) | 100% detection (execution-link signature failure) |
| A-REORDER | present the three genuine links in reversed order | 100% detection (digest chaining failure) |
| A-REPLAY | present case X's genuine chain as evidence for case Y's claimed occurrence | 100% detection (chain-bound occurrence != claimed occurrence) |
| A-STALE | re-present an already-consumed genuine chain | 100% detection (consumed-occurrence registry) |
| A-COMPROMISE-FULL | tamper execution facts to look clean and re-sign **all** links with the genuine keys (full key-set compromise) | **0% signature-layer detection — frozen boundary**: composed-signature validity is evidence about the key set, not about key custody or fact truth; `CHAIN_AS_SCIENCE` must false-promote (>0); properly scoped `CHAIN_CRYPTO_ONLY` must still emit no scientific success |

A-COMPROMISE-FULL is the honest negative result of this study. It is recorded, not repaired: no signature scheme inside this layer can detect the compromise of the signing key set. The receipt must state that under full key compromise `CHAIN_PLUS_SEI` also trusts the forged execution facts, so scientific admission inherits key custody as an unregistered premise.

## False-rejection endpoints

SEI must not win by rejecting everything. The valid workload is every case whose frozen gold is not `EXECUTION_INVALID` (7 of the 18 hostile cases) plus all 4 real receipts (11 cases). Endpoints:

- chain-layer false rejections of execution-valid cases: **0/11**;
- disposition-level false rejections of `AUTHORIZED_SCIENCE` cases: **0**;
- real-receipt false promotion: **0**.

## Positive terminal

`P15_ATTESTATION_COMPOSITION_V2_SUPPORTED` requires:

- 100% base chain verification and exact `CHAIN_PLUS_SEI` agreement with frozen gold on all 22 cases;
- 100% detection on A-TRUNCATE, A-SUBSTITUTE, A-SPLICE, A-REORDER, A-REPLAY, A-STALE;
- zero scientific-field leakage into any signed payload;
- zero properly-scoped `CHAIN_CRYPTO_ONLY` false scientific successes across all arms;
- A-COMPROMISE-FULL signature detection == 0 exactly as frozen, with its `CHAIN_AS_SCIENCE` false promotions > 0 recorded;
- zero false rejections on the valid workload and zero real-receipt false promotions;
- deterministic byte replay and independent verifier agreement on every endpoint.

A positive supports composition of cryptographically chained execution evidence **beneath** the SEI admission layer at bounded scope. It claims no new signature scheme, no production key management, no remote-attestation hardware equivalence, no threshold/multi-party signing, and no superiority over proof-of-execution systems.

# P15 attestation chain-composition result receipt V2

**Run:** GitHub Actions `32665597624`  
**Artifact:** `p15-attestation-composition-v2`, artifact ID `9500055966`  
**Artifact ZIP SHA-256:** `7b82fe7e22db7adcf32a7eb9afb0eb127f9c61a2674472da4d8d517f64460b39`  
**Primary terminal:** `P15_ATTESTATION_COMPOSITION_V2_SUPPORTED`  
**Independent terminal:** `P15_ATTESTATION_COMPOSITION_V2_SECOND_CHECKER_GREEN`  
**Same-run V1 terminal:** `P15_ATTESTATION_COMPOSITION_V1_SUPPORTED`

## Exact binding

- frozen protocol SHA-256: `6a7649be7e7f3a290d668de9ca31d798bfb11621d9db3e92558e8f52108e9bd7`
- primary V2 artifact-member SHA-256: `99b905fbf383933d011460a4554682a2cf1279f2b06bc830bdfa6e643fd6f767`
- primary V2 receipt SHA-256: `8ea1008abea9794663489d20f75024539da2977a4a8d449524e821149ff1039a`
- independent V2 artifact-member SHA-256: `bd421fbef8bb4be53ad6ff55d31207c140893daa1ed6f9d65c35e2a5894c0a00`
- independent V2 receipt SHA-256: `503f678581b9f838e4976ff791952e30a9e7c825b86eabcb7e6e2adf9f4f4603`
- deterministic primary replay: GREEN
- endpoint agreement with independent implementation: GREEN
- same-run execution of the frozen V1 single-attestation study: GREEN
- observed environment: Python `3.12.14`, `cryptography==46.0.3`, x86_64

The workflow executed the already-frozen V2 protocol, primary runner and structurally independent checker. No protocol threshold or expected endpoint was changed after the outcome.

## Chained attestation object

Each case carries a three-link Ed25519 chain:

`execution -> environment -> publication`

Each later link signs a digest binding the previous link's payload, signature and public key. The chain therefore tests composition rather than one isolated signature.

Corpus: `22` cases, reusing the bounded P15 execution/provenance fact model. Valid-workload false-rejection endpoints cover `11` cases (7 execution-valid hostile cases + 4 real workflow receipts).

## Protected result

| arm / endpoint | attempts | observed |
|---|---:|---:|
| untampered base chain verification | 22 cases | `1.0` |
| `A-TRUNCATE` | 66 | **66 detected** |
| `A-SUBSTITUTE` | 22 | **22 detected** |
| `A-SPLICE` (execution facts changed; later links re-signed under uncompromised execution key boundary) | 22 | **22 detected** |
| `A-REORDER` | 22 | **22 detected** |
| `A-REPLAY` (chain presented for another occurrence) | 22 | **22 detected** |
| `A-STALE` (already-consumed chain re-presented) | 22 | **22 detected** |
| valid-chain false rejection | 11 valid cases | **0** |
| scientific-disposition false rejection | 11 valid cases | **0** |
| chain + SEI agreement with frozen gold | 22 | **22/22** |
| scientific fields leaked into the signature/provenance layer | 22 | **0** |
| real-receipt false promotion | 4 | **0** |

The independent implementation reproduces every endpoint above exactly, including all six non-compromise attack counts, the 1.0 base verification rate, zero false-rejection counts, zero scientific-field leakage and 22/22 chain+SEI gold agreement.

## Frozen boundary — full key compromise

`A-COMPROMISE-FULL` is intentionally a negative boundary, not a failed implementation check.

Six forged-clean fact sets are re-signed with the genuine keys. Observed:

- attempts: `6`;
- signature-layer detections: **0**;
- `chain_as_science` false promotions: **6**;
- `chain_plus_sei` false promotions: **6**.

The frozen interpretation is therefore retained exactly:

> Composed-signature validity is evidence about the key set, not about key custody or fact truth; chain-plus-SEI inherits key custody as an unregistered premise.

The independent checker explicitly confirms this full-compromise boundary.

## Scientific disposition

P15 now has three independently tested layers:

1. **Scientific Execution Integrity (SEI):** bounded hostile fault study separates execution validity, scientific validity and claim authority;
2. **provenance interoperability:** the admission separation survives W3C PROV-JSON and RO-Crate/Workflow-Run representation round trips;
3. **cryptographic chain composition:** Ed25519 chaining detects truncation, substitution, splice, reorder, replay and stale-chain attacks with zero observed false rejection on the registered valid workload, while correctly exposing full-key compromise as outside what signature validity can establish.

This strengthens P15 from provenance interoperability to provenance-plus-attestation composition. It does **not** establish that signatures prove scientific truth, that key custody is trustworthy, that arbitrary production hosts are covered, or that the registered small corpus establishes production-scale overhead/reliability. Broad host/process fault diversity, production overhead and final clean-environment/submission binding remain open.

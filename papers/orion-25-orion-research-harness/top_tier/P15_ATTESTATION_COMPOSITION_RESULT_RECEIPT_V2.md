# P15 Ed25519 attestation-composition result receipt V2

**Run:** GitHub Actions `32664075763` (branch `claude/gap-p15-attestation-20260823`, head `66f490d1821232e11bc8b07516b69cc6bf337be8`)  
**Artifact:** `p15-attestation-composition-v2`, artifact ID `9499830847`  
**Artifact ZIP SHA-256:** `fccf3b28f3f33af8b07a87eab6764742c7882de88018d65be16e2dba1dee3bff` (matches GitHub server-side digest)  
**Primary terminal:** `P15_ATTESTATION_COMPOSITION_V2_SUPPORTED`  
**Independent terminal:** `P15_ATTESTATION_COMPOSITION_V2_SECOND_CHECKER_GREEN`  
**Agreement:** `P15_ATTESTATION_COMPOSITION_V2_TWO_IMPLEMENTATIONS_AGREE`  
**V1 re-executed in the same binding:** `P15_ATTESTATION_COMPOSITION_V1_SUPPORTED` + `P15_ATTESTATION_COMPOSITION_SECOND_CHECKER_GREEN`

## Exact binding

- protocol SHA-256: `6a7649be7e7f3a290d668de9ca31d798bfb11621d9db3e92558e8f52108e9bd7` (frozen and committed before the runner/checker)
- fault-cases fixture SHA-256: `a9a29f9e457e0be3b42acf806c3fdeb3d83ef252c3a66e81316a42a12245af2c`
- fault-gold fixture SHA-256: `142d14d089afbad0f49fd4243b5dda252c96017456d392d9c7a3e63e2e5fd45a`
- real-receipt fixture SHA-256: `87812194ad77f3cb2be19cd9dbeacb43b662bc35eb6df3b700f4521620f6d200`
- primary receipt file SHA-256: `99b905fbf383933d011460a4554682a2cf1279f2b06bc830bdfa6e643fd6f767`
- primary receipt self-hash (`receipt_sha256`): `8ea1008abea9794663489d20f75024539da2977a4a8d449524e821149ff1039a`
- independent receipt file SHA-256: `bd421fbef8bb4be53ad6ff55d31207c140893daa1ed6f9d65c35e2a5894c0a00`
- independent receipt self-hash: `503f678581b9f838e4976ff791952e30a9e7c825b86eabcb7e6e2adf9f4f4603`
- deterministic primary replay: GREEN (byte-identical `cmp`)
- deterministic independent replay: GREEN (byte-identical `cmp`)
- runtime: python `3.12.14`, `cryptography==46.0.3`, `x86_64` hosted runner

## Corpus

`22` cases total: `18` frozen hostile SEI fault cases + `4` real ORION workflow receipts (P6 ETS positive, P9 Qwen negative, P10 OCME positive, P10 native-Lean `CANNOT_CHECK`). Each case is composed into a three-link chain (execution → environment → publication), each link an Ed25519 signature over `previous_digest || role || facts`, genesis `sha256("P15-ATTESTATION-COMPOSITION-V2-GENESIS")`. Role keys are derived per `(role, case_id)` seeds; no scientific-contract or claim-authority field enters any signed payload.

## Composition result (from the actual artifact)

| endpoint | result |
|---|---:|
| genuine chains verifying (role order, chaining, keys, signatures, publication consistency) | `22/22` (rate `1.0`) |
| chain+SEI disposition agreement with frozen gold | `22/22` |
| scientific fields leaked into signed payloads | `0` |
| chain-crypto-only false scientific successes | `0` |
| chain-as-science false promotions (total, base + compromise) | `12` |

### Adversarial arms

| arm | attempts | detections |
|---|---:|---:|
| A-TRUNCATE (last byte dropped from each signed payload) | 66 | 66 |
| A-SUBSTITUTE (bound execution fact flipped after signing) | 22 | 22 |
| A-SPLICE (execution facts forged, only env+publication re-signed) | 22 | 22 |
| A-REORDER (genuine links reversed) | 22 | 22 |
| A-REPLAY (case X's chain presented for case Y's occurrence) | 22 | 22 |
| A-STALE (already-consumed genuine chain re-presented) | 22 | 22 |
| A-COMPROMISE-FULL (all facts forged clean, every link re-signed with genuine keys) | 6 | **0 at the signature layer (frozen honest-negative expectation)** |

## Key-compromise boundary (frozen negative, observed exactly)

Under full key-set compromise the composed signature layer detects nothing (`0/6`) — composed-signature validity is evidence about the key set, not about key custody or fact truth. Misuse outcomes on the six compromised cases:

- `CHAIN_CRYPTO_ONLY` (properly scoped donor use): `CANNOT_CHECK` — no false scientific success.
- `CHAIN_AS_SCIENCE` (hostile collapse of the chain into the admission decision): false-promotes `AUTHORIZED_SCIENCE` in `6/6`.
- `CHAIN_PLUS_SEI`: also false-promotes `6/6` — key custody is an **unregistered premise** inherited by the SEI layer, since the forged execution facts satisfy all 16 integrity conjuncts.

Base-corpus hostile collapse additionally false-promotes `6` execution-valid cases whose gold dispositions are `VALID_BUT_NOT_AUTHORIZED` / `INVALID_SCIENCE` / `CANNOT_CHECK` (5 fault + `REAL-P10-NATIVE-LEAN-CANNOT-CHECK`), for the `12` total above.

## False-rejection check over the full valid workload

Valid workload = every case whose gold disposition is not `EXECUTION_INVALID`: **11 of 22** (7 fault + 4 real).

| endpoint | result |
|---|---:|
| chain-layer false rejections | `0/11` |
| disposition-level false rejections (gold `AUTHORIZED_SCIENCE` demoted) | `0/5` |
| real-receipt false promotions | `0/4` |

All 5 gold-`AUTHORIZED_SCIENCE` cases (including the 3 real receipts) verify and admit; the real `CANNOT_CHECK` case stays `CANNOT_CHECK`. The admission layer does not win by rejecting everything.

## Two-implementation agreement

The independent checker (`check_attestation_composition_independent_v2.py`, sharing no code with the primary) re-derives keys, digests, every structural attack and every endpoint from the primary receipt JSON plus the frozen fixtures. All 13 agreement-table entries match exactly, and the full-compromise boundary is independently confirmed (`full_compromise_boundary_confirmed: true`).

## Scientific disposition

P15 now demonstrates that a multi-attestation Ed25519 composition over execution, environment and publication facts composes and fails closed under truncation, substitution, splicing, reordering, replay and stale-state presentation — at bounded scope, on the frozen 22-case corpus. The negative result is load-bearing: the composed chain adds ATTRIBUTABLE/tamper-evident execution records, not scientific validity, and a full key-set compromise is invisible to it; collapsing the chain into scientific admission false-promotes 12 cases while a properly scoped cryptographic-only reading correctly returns `CANNOT_CHECK`. Attestation donors therefore sit strictly below the scientific-admission layer; they are neither a replacement nor a sufficient premise for it.

This closes the attestation-composition and false-rejection gaps for the tested scope. It does not establish hardware-backed key custody, external timestamping authorities, production KMS/HSM deployment, or resistance to compromises of the signing infrastructure itself.

# Claim disposition — ORION25.CROSS_SITE_REPLAY.v1

Design frozen at `303de248` before any replay output. Executed once on
billy-old (`billy-laptop-old`, Linux glibc 2.43, Python 3.14.4,
cryptography 46.0.5) against references produced under Python 3.12.14 /
cryptography 46.0.3 on the CI runner.

Terminal: **T2_ENDPOINT_DIVERGENCE** — never relabelled.

## What the run established

| endpoint | verdict |
|---|---|
| trust-domain-law sweep (1000 cells, all controls) | **object-equal, exact** — `T1_LAW_HOLDS_EXACTLY` reproduced field-for-field |
| attestation-composition V2 projection | equal on **every scientific field** (arms, rows, counts, rates, terminal `…V2_SUPPORTED`) |
| single diverging key | `protocol_sha256` only |
| planted flipped-byte control | fired (runner failure path) |

## Root cause of the single divergence (one stage)

The runner hashes `P15_ATTESTATION_COMPOSITION_PROTOCOL_V2.md` from the
tree. Commit `3a1a83178` (R0 namespace unification, PR #1474) renamed that
frozen doc at R091 similarity, rewriting P15→ORION-25 strings — including
the two normative constant strings (`GENESIS`, key-derivation seed) that
the receipted runner still implements in their P15 form. The receipted
digest `6a7649be…` is byte-exact at the pre-rename path (commit
`7f7f91931`), as independently recorded by
`experiments/execution-integrity-v1/VERIFICATION_NOTES.md` (V1:
provenance-locator defect, locator pinned in `SOURCE_MANIFEST.json`).
The divergence is therefore a documentation-currency defect, not an
environment or portability failure; the runner remains the authority for
the executed constants.

## Boundary

A second site under the same programme custody is portability evidence
only. This study is the **D-OLD leg** of the fuller preregistered
three-site design
(`ORION.ORION25.ExecutionIntegrityTrustDomain.Protocol.v1`, sites
D-CI/D-OLD/D-HPC), which remains `PREREGISTERED_NOT_EXECUTED` and is not
superseded by this result. Not independent replication; not a second
custodian; the trust-domain-law promotion block stands.
`scientific_authority_delta: NONE`. Outcomes read once.

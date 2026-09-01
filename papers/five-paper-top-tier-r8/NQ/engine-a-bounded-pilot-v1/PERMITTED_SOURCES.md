# Permitted source record

All object identifiers below are immutable Git objects. No donor implementation was imported.

| Purpose | Commit:path | Blob SHA-1 |
|---|---|---|
| exact donor normalization and GL-class canonical form | `0c451e862a0eeddac7c673813c4dc499f134b088:development/orion-rg-davenport/X1F4_EXTREMAL_CLASSIFICATION_PROTOCOL_V1.md` | `931a721c8748c28f894df6df56dbf50740c4277e` |
| frozen direct-route normalization reference | `0c451e862a0eeddac7c673813c4dc499f134b088:development/orion-rg-davenport/X1F0_D2_C5CUBED_PROTOCOL_V1.md` | `8b5f303790503fc026bb867c9f107f5fe163a5b9` |
| R8 basis and coordinate-permutation description | `0c451e862a0eeddac7c673813c4dc499f134b088:papers/five-paper-top-tier-r8/NQ/MANUSCRIPT_R8_EARLY_CONSTANTS.md` | `3d2ae51a4889c86b2b3c83c95d38d021c3797e96` |
| replay requirements | `ee685107cf537810fe17df67d7a6bd0f4c7a0116:papers/five-paper-top-tier-r8/NQ/NQ_INDEPENDENT_REPLAY_PROTOCOL_R8.md` | `1aba5a0c0e22f4fadb12b6807dd7bcc348719c0c` |
| explicit lower-witness statement | `0c451e862a0eeddac7c673813c4dc499f134b088:development/orion-rg-davenport/X1F_D3_C5CUBED_PROTOCOL_V1.md` | `b035d7cdc427ed7340bb89cf054de3eff54ce59d` |
| permitted D2 result object, minimal witness-field inspection only | `0c451e862a0eeddac7c673813c4dc499f134b088:research/orion-rg/X1F0_D2_C5CUBED_EXACT_RESULTS.json` | `0565e4085b2bcb8331f0c96cfd3ae840037fa3e5` |
| permitted D3 lower-witness field | `0c451e862a0eeddac7c673813c4dc499f134b088:research/orion-rg/X1F_D3_C5CUBED_EXACT_RESULTS.json` | `6cecc0e94135634152f9dc9ac6b484c1b56f9e20` |
| task contract and public expected outcomes | GitHub issue `SzeChunYiu/ORION#1383`, observed 2026-08-26 | n/a |

## Exposure note

The D2 JSON field named `extremal_witness` was found to encode an 18-term short-spectrum
object, not the required D2 lower witness, and was not used as a D2 control. The D2 lower
witness fixture was instead transcribed from the explicit formula in the permitted protocol:
`e1^4 e2^4 e3^4 (1,1,0)^2 (1,0,1)^2 (0,1,1)^3`. The D3 fixture is the explicitly permitted
24-term lower witness. Both fixtures carry `EXPECTED_OUTCOME_EXPOSURE`.

The exact donor normalization was later isolated in the frozen X1-F4 protocol: normalized
multisets contain `e1,e2,e3` with `m(e1) <= m(e2) <= m(e3)`. X1-F4 also defines its separate
one-per-orbit class canonical form as a lexicographic minimum over ordered independent support
triples. `NORMALIZATION_BINDING.md` proves the differential and the complete orbit-slice
adapter. This resolves the mathematical normalization atom only; no full census or external
authority follows.

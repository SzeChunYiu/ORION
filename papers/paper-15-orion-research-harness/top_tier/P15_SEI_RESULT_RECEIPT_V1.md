# P15 Scientific Execution Integrity bounded result receipt V1

**Run:** GitHub Actions `32645458435`  
**Artifact:** `p15-sei-fault-v1`, artifact ID `9494739942`  
**Artifact ZIP SHA-256:** `7a6ff9daf9a42039b99d2d596aadb6918e490f48b64fcf7671dba27c86084ad7`  
**Replay:** `P15_SEI_FAULT_V1_BYTE_REPLAY_GREEN`  
**Terminal:** `P15_SEI_BOUNDED_FAULT_V1_GREEN`

## Exact content binding

- protocol SHA-256: `ce327d1af9d60f5fe028d73238a2998b99304f20183f65a67f78024b23ff4c8c`
- frozen cases SHA-256: `a9a29f9e457e0be3b42acf806c3fdeb3d83ef252c3a66e81316a42a12245af2c`
- frozen gold SHA-256: `142d14d089afbad0f49fd4243b5dda252c96017456d392d9c7a3e63e2e5fd45a`
- canonical receipt SHA-256: `436ae0ed39fc9c0c58bcb8d50249222d979340669265aacd4c7dea605fccde51`

## Protected benchmark

The protocol, 18 fault cases and independent gold dispositions were committed before the reference checker. The checker and CI workflow were added only after the freeze.

All systems receive the same case facts; the comparison is whether execution/replay/agreement evidence is incorrectly promoted into scientific validity/authority.

## Results

| system | exact disposition accuracy | false authorized science | execution-invalid admitted as science | invalid science admitted as success | valid-but-not-authorized laundering |
|---|---:|---:|---:|---:|---:|
| plain logs + exit/output | 0.2778 | 13 | 8 | 2 | 1 |
| structured receipt/provenance | 0.7222 | 5 | 0 | 2 | 1 |
| replay + lane-agreement product | 0.7222 | 4 | 0 | 2 | 1 |
| SEI reference contract | 1.0000 | 0 | 0 | 0 | 0 |

The replay/agreement comparator also false-rejected one independently verified valid case because the two lanes disagreed; SEI correctly kept the independent scientific verifier distinct from agreement.

SEI emitted exactly:

- `AUTHORIZED_SCIENCE`: 2;
- `VALID_BUT_NOT_AUTHORIZED`: 1;
- `INVALID_SCIENCE`: 2;
- `EXECUTION_INVALID`: 11;
- `CANNOT_CHECK`: 2.

## H15 executable witnesses

- **H15.1 host/science separation:** every frozen execution-invalid gold case failed the execution-integrity prerequisite.
- **H15.2 exact binding:** stale replay, duplicate occurrence, digest forgery and truncation all block authoritative execution success.
- **H15.3 publication atomicity:** pre-reap finalization, cleanup omission and retry-accounting corruption block authoritative execution success.
- **H15.4 receipt/coverage != validity:** `SEI-CLEAN-AUTH` and `SEI-COMPLETE-INVALID-SCIENCE` have identical execution-integrity/replay properties but different independent scientific validity.
- **H15.5 agreement != validity:** `SEI-DUAL-AGREE-WRONG` has lane agreement and invalid science; `SEI-DUAL-DISAGREE-VERIFIED` has lane disagreement but independent scientific verification and valid claim authority.

## Scientific disposition

P15 now has a bounded executable Scientific Execution Integrity result. The result establishes non-implications and a reference admission contract over the frozen fault model; it does **not** prove superiority over real W3C PROV/RO-Crate/workflow/attested-execution systems.

The top-tier P15 terminal remains open for real comparator interoperability, broad host fault injection, runtime/storage overhead, false rejection under non-toy workloads, an independent implementation/adjudicator, submission-day literature closure and a publication manuscript bound to external results.

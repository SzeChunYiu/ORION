# ORION-18 claim-ledger addendum V3

**Date:** 2026-08-24
**Rule:** additive rows only; V1–V3 and ADDENDUM_V2 boundaries remain
unchanged. No row in any earlier ledger or addendum is edited or retracted by
this file.

| ID | Claim | Status | Authority | Boundary / reopen trigger |
|---|---|---|---|---|
| ORION-18.C-V3.1 | The ORION-18 native-execution test design is frozen as contract `P8.NATIVE.CROSS_SYSTEM_PROTOCOL.V1`: four type-distinct native systems (OPA/Rego, Cedar, in-toto/SLSA, Sigstore/cosign), twelve ordered cross-system pairs, twenty-four case slots (clean and hostile per pair), hostile mechanism per pair pinned, ideal typed-product baseline, pass criteria fixed in advance. | `ARTIFACT_FACT` | `formal/P8_NATIVE_CROSS_SYSTEM_PROTOCOL_V1.md` + machine-readable twin + `formal/check_p8_native_protocol_binding_v1.py` | Reopen on any change to systems, pairs, slots or criteria; the checker fails closed on such drift. |
| ORION-18.C-V3.2 | The execution itself ("execute actual type-distinct native systems and ideal typed-product baseline") has not been run: none of the four systems' binaries exists in the producing environment and installation there is not permitted. | `CANNOT_CHECK` | tooling gap recorded in the protocol twin (`required_binaries`, observation dated 2026-08-24) | Unblocked by any environment with the pinned binaries; the frozen slots are then filled, not redesigned. |
| ORION-18.C-V3.3 | Ordered-pair coverage ("cover every ordered cross-system pair with clean and hostile cases") is a design property of the frozen protocol, verified structurally by the binding checker — not an executed coverage result. | `ARTIFACT_FACT` | checker's `validate_protocol` (12 distinct off-diagonal pairs, 24 slots, distinct mechanisms) | Reopens into an executed claim only when results records exist. |

### Prohibited inference

The existence of this protocol is not evidence of execution. No native system
was run, no native-looking output was produced, and simulating a system and
reporting the simulation as execution remains prohibited, as does treating a
partial run as full pair coverage or re-deriving the DENIED-vs-`CANNOT_CHECK`
calibration settled in #1096. The ideal baseline is the paper's typed product,
not a description of any native system's internals.

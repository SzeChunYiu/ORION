# P15 provenance interoperability result receipt V1

**Run:** GitHub Actions `32655587115`  
**Artifact:** `p15-provenance-interop-v1`, artifact ID `9497399857`  
**Artifact ZIP SHA-256:** `eb92cd505474e79f3abffd3bdbc7b346cd5f0ed1f871c211f7809741833c7bdd`  
**Primary terminal:** `P15_PROVENANCE_INTEROP_V1_SUPPORTED`  
**Independent terminal:** `P15_PROVENANCE_INTEROP_SECOND_INDEPENDENT_CHECKER_GREEN`  
**Agreement:** `P15_PROVENANCE_INTEROP_TWO_IMPLEMENTATIONS_AGREE`

## Exact binding

- protocol SHA-256: `37208b7398742556e91477aefbf867e9ea8e9f91f2993e52aa997a2a7b3deab9`
- real-receipt fixture SHA-256: `87812194ad77f3cb2be19cd9dbeacb43b662bc35eb6df3b700f4521620f6d200`
- primary receipt SHA-256: `f2a032b7a372a97b2e959c999670de9c141dcf63ea2761bdc6f696124cef8544`
- independent receipt SHA-256: `b6a21fd4b7299eec557424e8983b1f422bfff1fba3f34d02f3ff1673a89c404a`
- deterministic primary replay: GREEN
- deterministic independent replay: GREEN
- production provenance library: `prov==3.1.0`

## Corpus

`22` cases total:

- `18` already-frozen hostile SEI cases;
- `4` real ORION workflow receipts: P6 bounded ETS positive, P9 authoritative Qwen negative, P10 bounded OCME positive, and P10 native-Lean `CANNOT_CHECK`.

The real fixtures carry no new scientific authority; they reuse dispositions already bound by their source receipts.

## Interoperability result

| endpoint | result |
|---|---:|
| W3C PROV-JSON normalized execution-fact round-trip | `1.0` |
| RO-Crate 1.3 / Workflow-Run projection round-trip | `1.0` |
| native-vs-imported SEI disagreements | `0` |
| scientific fields leaked into donor provenance | `0` |
| provenance-only false scientific successes | `0` |
| real-receipt false rejection | `0` |
| real-receipt false promotion | `0` |
| mean PROV-JSON serialized bytes/case | `1619.6363636363637` |
| mean RO-Crate JSON-LD serialized bytes/case | `2014.6363636363637` |

Wall-time measurement (`~0.03 s` for the small corpus on the hosted runner) is informational only and carries no performance-authority claim.

## Load-bearing preservation cases

- `SEI-COMPLETE-INVALID-SCIENCE`: complete valid execution provenance remains `INVALID_SCIENCE` when the independent scientific contract is supplied, while provenance-only remains `CANNOT_CHECK`.
- `SEI-DUAL-AGREE-WRONG`: lane agreement plus replay does not become correctness; imported disposition remains `INVALID_SCIENCE`.
- `SEI-DUAL-DISAGREE-VERIFIED`: lane disagreement does not block a separately verified valid scientific result.
- `REAL-P10-NATIVE-LEAN-CANNOT-CHECK`: a real successfully executed provenance record with insufficient scientific coverage remains `CANNOT_CHECK` through both donor representations.

## Scientific disposition

P15 now demonstrates **representation-independent scientific admission above real provenance standards** at bounded scope. It interoperates with a production W3C PROV implementation and a current RO-Crate 1.3/Workflow-Run structural projection rather than requiring proprietary provenance. Provenance supplies execution evidence; the independent scientific/authority record supplies scientific admission. Neither layer is silently collapsed into the other.

This closes the provenance-interoperability and second-implementation gaps for the tested scope. It does not establish superiority over cryptographic proof-of-execution/attestation products, production-scale overhead, broad host/runtime fault diversity, or independent external scientific adjudication.

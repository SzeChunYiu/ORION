# Paper 01 claim ledger

## Architectural claims

| Claim | Status | Evidence type |
|---|---|---|
| ORION state separates K, W and M | DEFINITION / IMPLEMENTED | `src/orion/core/`, registry, unit tests |
| Core operators are modular and provider-independent | IMPLEMENTED CONTRACT | `src/orion/engine/operators/`, `src/orion/providers/` |
| Search/generation cannot directly mint authority | IMPLEMENTED CONTRACT | transition validation + verification boundary |
| Final solve requires bounded saturation | IMPLEMENTED CONTRACT | `SaturateOperator` + solver |
| Parent-discipline, literature-bridge and omission routes are required by bootstrap saturation | IMPLEMENTED POLICY | saturation basis v2/v3 |
| High-impact ORION development requires a knowledge/formulation saturation packet | IMPLEMENTED GOVERNANCE CONTRACT | `src/orion/development/protocol.py` |

## Empirical claims deliberately not made

- ORION is superior to generic LLM research.
- ORION reliably achieves high literature recall on the open web.
- The required route family is sufficient for unknown-unknown discovery.
- Self-ORION improves ORION on fresh development tasks.
- The current global portrait implementation captures scientific semantics adequately.

Those remain evaluation fibers.

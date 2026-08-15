# Mechanic handoff contracts

ORION mechanics communicate through explicit, versioned handoff contracts rather than narrative context.

A universal `MechanicReceiptEnvelope/v0` declares presence and schema semantics for:

- execution status;
- output artifact identifiers;
- mechanic-specific handoff values;
- metric observations with units/evidence/uncertainty;
- residual identifiers;
- evidence and provenance identifiers;
- normalized cost;
- wall-clock latency.

## Presence and compatibility

Missing required fields are invalid/blocked. Downstream mechanics may not infer a missing required value from prose, an empty collection or an implementation default. Schema versions are explicit, and producer/consumer compatibility is a verification obligation rather than an assumption.

The universal envelope does not define a mechanic's scientific payload. Every cell retains an empirical-open coordinate for step-specific payload fields, schemas, units, uncertainty semantics and compatibility.

## Authority transport

Evidence identifiers are lineage pointers. Their presence does not transport scientific authority by itself. Authority crosses a mechanic boundary only through an explicitly licensed certificate/promotion path.

## Interface validation

Interface requirements should be verifiable at both sides of the boundary: producer emitted the declared schema; consumer interpreted the same schema/presence/unit semantics; version compatibility held; and no omitted field silently changed the downstream decision.

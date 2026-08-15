# Mechanic observability

ORION separates **runtime observability** from **measurement of the target construct**.

Logs, traces, status codes, latency and resource counters are valuable for controlling and diagnosing a system, but they do not automatically measure scientific quality, evidence adequacy, truth or root-task progress. A measurement plan should therefore name what quantity/measurand is observed, the instrument/source, unit, collection trigger, uncertainty/limitations, provenance and decision use.

## V0 runtime observation baseline

Every mechanic receives identifiers for six universal runtime observations already representable by `MechanicReceipt`:

1. run status (`SUCCEEDED/PARTIAL/FAILED/BLOCKED/CANNOT_CHECK`);
2. wall-clock latency;
3. normalized resource/cost units;
4. emitted residual identifiers;
5. evidence/provenance lineage identifiers;
6. emitted handoff-field presence.

These close the structural question "is this mechanic inspectable at runtime?" They do not close step-specific measurement design. Every mechanic retains an empirical-open coordinate for performance/scientific measurands, measurement validity, calibration, uncertainty and decision thresholds.

## Semantic conventions and identity

Observation identifiers should remain stable across providers. Runtime metrics should declare units and source/instrument semantics; tracing/logging should retain mechanic/task/run identity so measurements can be joined back to immutable episodes and receipts. A provider-specific telemetry name is an implementation projection, not the canonical mechanic quantity.

## Authority boundary

Runtime telemetry, interface signals and performance counters cannot directly create scientific authority. Scientific measurements require their own observation/model/evidence contract and verification path.

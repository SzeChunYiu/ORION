# Paper C / C2 — engineering amendment 1

Date: 2026-08-24  
Parent: `PAPER_C_C2_PAIR_GAIN_VALUE_SEPARATION_PROTOCOL_2026-08-24.md`  
Status: recorded after the first formal dual run; scientific construction unchanged.

## Digest disagreement

The first analyzer and generic mathematical checks both passed, but generic and native digest verification rejected the serialized receipts. The cause was integer histogram keys: in-memory canonical JSON sorted them numerically, while parsing the on-disk JSON produced string keys sorted lexicographically. The repair types every histogram key as a string before signing. Recomputed on-disk digests then verified independently.

Adverse terminal retained:

`PAPER_C_C2_GENERIC_NATIVE_DISAGREEMENT__INTEGER_HISTOGRAM_KEY_CANONICALIZATION`

## Fixed-workspace collision

Repeated verification then exposed a separate harness boundary. With fixed workspace paths, a native workspace could be repopulated during the generic phase, causing the native controller to alternate between a two-transition run and a one-transition terminal replay. The final state and scientific decision were identical, but transition-count nondeterminism is not admissible provenance.

The runner now creates unique per-run generic and native workspaces under `/tmp`, asserts that the native campaign has no initial state, and removes the unique workspaces after the deterministic receipt is written. Four consecutive clean repetitions produced the identical two-transition trace and identical dual receipt digest.

Adverse terminal retained:

`PAPER_C_C2_FIXED_NATIVE_WORKSPACE_REPOPULATED__CANNOT_USE_TRACE_AS_DETERMINISTIC_RECEIPT`

## Authority boundary

These are execution and serialization repairs. They do not strengthen or weaken the theorem, and neither adverse terminal is scientific evidence.

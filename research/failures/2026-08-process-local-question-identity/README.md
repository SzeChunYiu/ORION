# Process-local mechanical question identity

## Failure

The recurring-failure branch of `generate_problem_questions` once built its question identifier from Python's process-local `hash((signature, variations))`.

Python intentionally randomizes hashes across interpreter processes. Equivalent repeated-failure evidence could therefore receive different question identifiers after restart, which breaks replay, provenance joins, deduplication, and long-horizon failure learning even when the underlying question is unchanged.

## Cause

A convenient in-process hash was treated as if it were a persistent content identity. The implementation encoded no canonical serialization and no algorithm/version marker, so downstream data could not know how the identifier had been produced.

## Repair

Repeated-failure question identity now uses canonical JSON over the sorted failure signature and sorted set of variation signatures, followed by SHA-256. The identifier embeds the scheme tag `failure-pattern-sha256-v1` so a future identity migration is explicit rather than silently rewriting history.

Order within one variation signature remains meaningful. Order of the failure-signature members and order of the observed variation signatures are treated as set-like and canonicalized.

## Regression obligations

Tests must establish that:

- equivalent content receives the same identifier under independently randomized Python hash seeds;
- set-like input ordering does not change the identifier;
- changing either the failure signature or observed variation content changes the identifier;
- the algorithm/version scheme is visible in the persisted question identifier.

## Boundary

This repair makes question identity stable; it does not prove that a repeated failure has one true cause or authorize automatic guard promotion. Diagnosis, falsification, replay, fresh variation, and protected promotion remain separate obligations.

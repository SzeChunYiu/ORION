# ORION-01 production-successor claim disposition

## Issue #1701 successor mapping

| Requirement | Disposition in this identity |
|---|---|
| Define a source-complete move grammar before testing | **Frozen.** `CORPUS_MANIFEST.json` and `SOURCE_COMPLETE_MOVE_GRAMMAR.json` define source resolution, reachability closure, mutation roots, finite domain partitions, canonical effects, and extensional classes before source-instance execution. |
| Prove a completeness theorem or produce a counterexample | **Conditional theorem proved; source instance open.** `REGISTRY_COMPLETENESS_THEOREM.md` proves the relative theorem from obligations O1–O6 and specifies fail-closed counterexamples. No pinned-source `REGISTRY_COMPLETE` terminal is claimed. |
| Freeze a new identity and use old Round-3 only as derivation/adverse evidence | **Satisfied.** The identity is `orion-01-production-completeness-v1-2026-08-29`; `ADVERSE_AND_CANNOT_CHECK.jsonl` preserves PR #1602 without treating it as a result under this protocol. |
| Require a material consequence rather than a larger enumeration | **Frozen.** The registry quotient must preserve production semantics and a later Phase-4 exact-compute protocol must name a material compiler predicate. Search size or a higher cap cannot satisfy the endpoint. |

## Claims available at protocol freeze

The committed protocol supports only the following statements:

1. A deterministic unique-prefix rule has been prospectively selected for the upstream source.
2. A source-complete grammar and extensional equivalence relation have been selected before semantic testing.
3. A conditional registry-completeness theorem and fail-closed counterexample rule have been proved at the protocol level.
4. The old capped execution remains adverse derivation evidence with terminal `CANNOT_CHECK_MOVE_COMPLETENESS`.
5. No source-instance, registry, or material-consequence outcome exists yet under this identity.

## Claims not available

This identity currently does not support:

- that `dade7d46` has already resolved uniquely;
- that the production source boundary is complete;
- that every dynamic or native target is finite and resolved;
- that parameter and side-condition domains have finite exact partitions;
- that a separating basis exists for the pinned source;
- that the production registry is complete or smaller than the old registry;
- that exact search terminates or produces a better compiler result;
- that PR #1602 missed a move, found every move, or should be rerun with a higher cap;
- that registry completeness transfers beyond the frozen source/environment/caller boundary;
- external proof review, replication, novelty authority, submission, or physical advantage.

## Promotion rule

A `REGISTRY_COMPLETE` claim requires content-hash-bound receipts for O1–O6 and a passing independent protocol/ledger checker. A material compiler claim additionally requires a fresh Phase-4 protocol frozen only after `REGISTRY_COMPLETE` and executed without post-outcome budget changes.

A replayable counterexample is a valid and material successor outcome. It should be retained rather than repaired silently under the same identity.

## Current terminal

`PROTOCOL_FROZEN__NO_OUTCOME`

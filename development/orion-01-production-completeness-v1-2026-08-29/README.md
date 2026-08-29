# ORION-01 production-completeness successor V1

This directory is the prospectively frozen successor required by issue #1701. It is scientifically distinct from the capped Round-2/Round-3 identities.

## Routing and terminal

- routing: `TOP_TIER_PROMOTION_ACTIVE__THEORY_OR_EXACT_COMPUTE`
- protocol terminal: `PROTOCOL_FROZEN__NO_OUTCOME`
- old execution terminal retained as derivation/adverse evidence: `CANNOT_CHECK_MOVE_COMPLETENESS`
- old cap increase authorized: `false`

## Purpose

The successor asks whether a source-complete, extensional production move registry can be established for a uniquely resolved pinned PyZX snapshot and whether that result has a material exact-compute consequence. It does **not** begin by enumerating a larger state space.

The order is mandatory:

1. resolve the frozen source prefix uniquely and record the full commit before semantic testing;
2. establish the source boundary and mutation-root completeness;
3. derive an extensional move grammar and canonical effect classes;
4. prove the relative registry-completeness theorem or emit a counterexample;
5. only after a `REGISTRY_COMPLETE` terminal, freeze a fresh exact-search budget and execute it.

## Files

- `QUESTION.md` — scientific question and exclusion boundary
- `PROTOCOL.json` — prospectively frozen endpoints and decision rules
- `CORPUS_MANIFEST.json` — deterministic source-resolution rule
- `SOURCE_COMPLETE_MOVE_GRAMMAR.json` — grammar, discovery closure, and equivalence relation
- `REGISTRY_COMPLETENESS_THEOREM.md` — conditional theorem and proof obligations
- `EXPECTED_TERMINALS.json` — exhaustive machine-readable terminal set
- `registry_protocol_checker.py` — implementation-independent protocol checker
- `ADVERSE_AND_CANNOT_CHECK.jsonl` — old capped result retained only as derivation/adverse evidence
- `CLAIM_DISPOSITION.md` — authority and promotion boundary

No result file is permitted under this identity until the source resolution receipt and registry theorem/counterexample receipt exist. The protocol checker enforces that boundary.

# ORION Frontier Support / State Programme

This directory is a separate post-P9/P10 research programme exploring **where task-relevant structure lives in a reasoning system**.

Base at programme freeze: `main@6460410595a14cf9894c9acd450ab2b649a3b858`.

It does not modify merged P9/P10 claims and is independent of the already-frozen #618 structural-scaling outcomes/runtime lanes.

## Files

- `FRONTIER_RESEARCH_PROGRAMME_V1.md` — programme thesis, metrics, reviewer roles, cross-domain ladder.
- `NEAREST_WORK_LEDGER_2026-08-20.md` — current donor subtraction before frontier outcomes.
- `HOSTILE_REVIEW_MATRIX_V1.md` — alternative explanations and stop rules.
- `THEORY_TARGETS_V1.md` — mathematical targets with explicit donor/novelty boundaries.
- `CLAIM_LEDGER_V1.md` — authoritative promotion state.
- `F1_STRUCTURAL_SUPPORT_FRONTIER_PROTOCOL_V1.md` — weights/representation/architecture/tool/state/retrieval/search frontier.
- `F2_CERTIFIED_STATE_COMPACTION_PROTOCOL_V1.md` — exact finite future-equivalence certificate + learner test.
- `run_f2_certified_state_compaction_v1.py` — executable F2 certificate/benchmark.
- `results/F2_CERTIFICATE_RECEIPT_V1.json` — certificate-only result; no learner claim.
- `F3_COMPILE_ONCE_REASON_MANY_PROTOCOL_V1.md` — answer-blind reusable state amortization.
- `F4_OBSERVATION_TIME_SCALING_PROTOCOL_V1.md` — OBSERVE vs THINK vs TOOL resource frontier.
- `F5_REPRESENTATION_RETRIEVAL_DUALITY_PROTOCOL_V1.md` — structured state versus retrieval depth/reranker strength.
- `F6_PERSISTENCE_REPLAY_TAX_PROTOCOL_V1.md` — persisted sufficient state versus history reconstruction.

## Current earned result

Only one new result is currently earned:

`F2: CERTIFIED_STATE_EXACT_FUTURE_EQUIVALENCE`

The frozen ten-bit finite environment was exhaustively checked over all 1024 states and all 343 three-step future action sequences. Grouping by the five relevant state bits yields zero future-reward-signature violations across 32 quotient classes. Dropping one relevant bit produces counterexamples in all 16 hostile quotient classes.

This is **certificate-only** evidence. F2 learner/sample-efficiency outcome is not yet known.

## Immediate execution

The F2 CI workflow must first reproduce the exact certificate receipt, then execute the frozen MLP benchmark. A null learner result leaves the certificate intact and blocks only the accessibility claim.

F3/F4/F5/F6 execution adapters are added only under their frozen protocols. New outcome-sensitive gates may not be introduced after an arm produces results.

## Programme thesis if eventually earned

> Reasoning quality belongs to a model-plus-support system: under fixed task information, useful structure may be externalized into representation, state, retrieval, tools, memory, architecture, or search, shifting the resources required to reach a fixed quality.

This is not a current result.

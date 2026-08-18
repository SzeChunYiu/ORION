# P2 publication-closure development packet — 2026-08-17

Branch: `shadow/p2-publication-closure`
Subject main at branch creation: `c0e50d5230674124f883f7cce06cbd9b14f9840e`
Issues: #99, #157, #279, #317; P2 consumer of #318; verification coordination #283/#287.

## Atomic development questions

1. Can Paper 2 reach an honest publication terminal without fabricating the currently unavailable matched AutoResearchBench Wide/Deep comparison?
2. Which parts of the claimed retrieval/stopping novelty are removed by the strongest current donor work, including papers published after the earlier P2 audit?
3. Can donor assimilation be made machine-checkable against source substitution, rebranding, authority escalation, baseline weakening, negative-history deletion, and stale/false saturation?
4. What exact claim remains supportable by the committed 390-task complete-gold mechanism experiment plus bounded external MetaSyn/AutoResearchBench probes?
5. Which open issues may terminate as `CANNOT_CHECK` or `P2_NARROWED`, and which shared programme issues must remain open?

## Bounded knowledge/search universe

Primary-source search was repeated on 2026-08-17 across scientific/deep-research retrieval, candidate generation, systematic-review screening, retrieval continuation/stopping, evidence sufficiency, state-gated retrieval, relation-aware scientific retrieval, citation expansion, and question-conditioned memory. The audit includes the already tracked SAGE, AgentIR, AutoResearchBench, MetaSyn, AgentSLR, DeepControl and Agent Retrieval Bench families and newly identified direct pressure from:

- HALT, arXiv:2608.02009 — evidence-coverage / verification-aware stopping;
- SIEVE, arXiv:2608.02751 — fielded Boolean retrieval and selective fetching;
- Decision-Theoretic Stopping Rules for Document Screening, arXiv:2606.07071 — utility-based stopping;
- SGR-Bench, arXiv:2605.22219 — state-gated retrieval failure taxonomy;
- SciNetBench, arXiv:2601.03260 — relation-aware scientific retrieval;
- MemChain, arXiv:2607.24097 — question-conditioned memory traces;
- When Should Multi-Round RAG Stop?, arXiv:2608.13237 — structured stop/continue judgments published 2026-08-13.

## Saturation assessment

**NOT SATURATED.** A material stopping paper appeared on 2026-08-13, four days before this packet. A claim of bounded literature saturation on 2026-08-17 would therefore be unjustified. Instead this lane freezes a dated literature cutoff and explicit reopen triggers. The narrowed publication terminal does not require claiming literature saturation.

## Challenge to the saturation basis

Search can miss relevant work because terminology is unstable (`stopping`, `sufficiency`, `coverage`, `continuation`, `abstention`, `screening`, `search control`); scientific retrieval work may be published under QA/RAG/systematic-review terminology; very recent arXiv papers may not be fully indexed; and a composition equivalent to ORION's residual may be described without ORION's route/task vocabulary.

## Hypotheses for missed knowledge

- H1: an existing retrieval-control paper already separates local continuation utility from global epistemic closure under unavailable/censored sources;
- H2: an existing evidence-sufficiency method already specifies typed unresolved obligations rather than only STOP/CONTINUE/abstain;
- H3: a memory system already combines content identity with question-conditioned processing state, eliminating the remaining read-ledger residual;
- H4: a federated/systematic-search method already earns route independence from provenance/capture evidence rather than source labels.

None of H1–H4 is treated as disproved by this search. They are reopen triggers.

## Frozen implementation hypothesis

Implement the smallest additive P2-local gate:

1. a source-bound `MechanismAssimilationReceipt.p2.v1` ledger;
2. a stdlib validator with canonical receipt hashing and hostile invariants;
3. hostile tests for hash tampering, source substitution, authority escalation, official-baseline weakening, negative-history deletion, and false saturation;
4. a dated literature/assimilation freeze subtracting donor prior art from P2 novelty;
5. a narrowed publication terminal that preserves external `CANNOT_CHECK` results and changes no P2 V1 result artifact.

No new retriever, allocator, judge, benchmark adapter, or external result is introduced in this lane. P2 V1 evidence is immutable.

## Reopen triggers

Reopen mechanism development if any of the following occurs:

- admissible matched AutoResearchBench Wide/Deep execution becomes possible;
- the official SAGE corpus/evaluator becomes available;
- a new pre-submission paper materially changes the donor dispositions or residual claim;
- a donor demonstrates equivalent fail-closed global closure semantics under censored/unavailable routes;
- a future external trace identifies ranking, screening, allocation, or stopping rather than candidate generation as the dominant earliest failure;
- the target venue requires an external superiority claim rather than accepting the narrowed methods/system-design contribution.

## Verification plan

- local pure-Python hostile tests before repository write;
- repository CI for the committed validator/tests and existing P2 checks;
- no positive external claim is promoted, so #283 must verify only that narrowing did not launder a null/blocker into support;
- #287 novelty state must subtract the donor families named in the assimilation freeze.

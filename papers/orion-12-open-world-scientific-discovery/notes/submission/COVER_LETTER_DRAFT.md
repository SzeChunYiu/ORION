# P2 cover letter — IP&M narrowed-scope draft

**Status:** scientific-scope draft complete; author/affiliation/corresponding-author metadata intentionally absent until supplied by the authors. Primary target: *Information Processing & Management* (IP&M).

Canonical claim boundary: `protocol/P2_NARROWED_PUBLICATION_TERMINAL_2026-08-17.md`.
Every result-bearing manuscript sentence remains governed by `protocol/CLAIM_LEDGER_V1.json` and `scripts/check_claim_ledger.py --check`.

---

## Draft text

Dear Editors,

We submit *Fail-Closed Coverage and Stopping for Scientific-Literature Discovery: Controlled Mechanism Evidence and External Stress Tests* for consideration in *Information Processing & Management*.

The manuscript studies a control problem around scientific-literature retrieval rather than proposing another general retrieval architecture. When a discovery system searches through heterogeneous routes, it must distinguish whether routes are genuinely independent evidence channels, what material has already been processed for the current scientific question and content version, when a single route may stop, and when task-level coverage must remain open. We formalize these as typed states and enforce a fail-closed rule: local route stopping, provider unavailability, retrieval utility, coverage estimates, and evidence-sufficiency signals do not silently certify global scientific completeness.

The empirical contribution is deliberately bounded. The main experiment is a frozen complete-gold controlled-index campaign designed to make missed relevant material and premature closure observable. Its statistical authority is `TIER_B_committed` with the frozen plan's mandatory underpowered label, so we use it to study mechanism behavior rather than to claim inferential retrieval superiority. The manuscript also retains external MetaSyn and AutoResearchBench probes as retrieval/screening stress tests and negative diagnostics. It does **not** claim a matched external ORION-vs-baseline Wide/Deep superiority result, because no admissible such result is archived in this revision.

We also narrow novelty against current adjacent work rather than presenting established mechanisms as new. Strong lexical and metadata-augmented retrieval, reasoning-aware retrieval, field-aware deep-research retrieval, stage-separated retrieval/screening analysis, marginal-utility continuation, verification-aware stopping, decision-theoretic stopping, structured STOP/CONTINUE judgments, and generic question-conditioned memory are all treated as prior-art pressure. The surviving candidate contribution is narrower: typed authority semantics under unknown coverage, especially the rule that unresolved unavailable/censored routes remain open obligations, together with earned route identity and dual content-identity/question-conditioned processing state.

Several limits are therefore explicit in the paper:

- the controlled index is synthetic and should not be interpreted as an estimate of open-web retrieval difficulty;
- bounded external probes do not validate the complete multi-route system;
- unavailable official resources or provider routes remain `CANNOT_CHECK`, never evidence of absence;
- null-on-recall mechanism findings are retained as nulls rather than converted into stronger claims;
- the nearest-work state is dated, not declared saturated, and is subject to a pre-submission refresh.

The reproducibility package is designed so that the claim boundary is auditable. Result-bearing manuscript sentences are bound to immutable evidence artifacts, the complete offline record set regenerates without network access or third-party credentials, and a source-bound donor-assimilation ledger is hostile-checked against source substitution, authority escalation, baseline weakening, negative-history deletion, and false saturation claims.

We believe this scope is appropriate for IP&M because the manuscript is an information-retrieval methods and critical system-design contribution centered on evidence/coverage semantics and scientific-discovery control rather than a broad performance claim.

We will supply the required author, affiliation, corresponding-author, declaration, and submission metadata in accordance with the current journal instructions at upload time. No such metadata is inferred in the repository draft.

Sincerely,

The authors

---

## Rules for editing this letter

- Do not add "state-of-the-art", "first", "significantly outperforms", or other superiority language unless a new prospective result and claim-ledger update legitimately support it.
- Do not turn `CANNOT_CHECK`, provider unavailability, or bounded null probes into positive evidence.
- Any numeric result added here should be traceable to the claim ledger / archived evidence.
- Re-run the claim ledger and P2 assimilation checks after substantive manuscript changes.
- Apply current IP&M author/submission requirements at upload time; do not guess template, anonymisation, declaration, or metadata requirements from stale instructions.

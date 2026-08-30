# ORION-06 final claim-to-evidence map V1

**Manuscript surface:** `manuscript/main.tex`  
**Scientific claim ceiling:** bounded one-programme methods/case-study paper  
**Mapping date:** 2026-08-30  
**Authority rule:** a replayed or checksum-valid receipt establishes attribution/reproducibility only to the scope recorded by that receipt; it does not upgrade scientific validity or generality.

## Headline claim map

| ID | Final manuscript claim | Controlling evidence / authority | Disposition |
|---|---|---|---|
| C1 | The workflow preserves adverse, absorbed, mixed, saturated, lower-bound and `CANNOT_CHECK` terminals as explicit state and registers successors separately rather than rewriting failed parents. | `CLAIM_LEDGER_V3.md` Q2V3-1/Q2V3-3; `MANUSCRIPT_V3_REFINED.md`; `RECEIPT_INDEX.md` and the indexed R6 programme receipts. | **BOUND CASE-STUDY CLAIM — MAPPED** |
| C2 | A same-identity repair must cover every failed load-bearing predicate through at least one admissible action on a declared causal ancestor. | `theory/claim-preserving-recovery-v1/THEORY.md`; `theory/claim-preserving-recovery-v1/CLAIM_DISPOSITION.md`; `theory/claim-preserving-recovery-v1/check_claim_preserving_recovery_v1.py`. | **THEOREM CLAIM — MAPPED** |
| C3 | An uncovered failed predicate yields a no-repair certificate in the declared action language; minimum weighted ancestor cover lower-bounds repair cost; dominated causal-cover actions can be safely pruned from at least one optimum. | Same theorem packet as C2, with terminal `CLAIM_PRESERVING_CAUSAL_COVERAGE_PROVED__CROSS_DOMAIN_RECOVERY_UNTESTED`. | **THEOREM CLAIM — MAPPED** |
| C4 | Changing question, population, estimand, protocol semantics, primary metric, threshold, protected corpus, or terminal semantics creates a new claim identity rather than a favourable repair of the failed identity. | `theory/claim-preserving-recovery-v1/CLAIM_DISPOSITION.md`; `THEORY.md`; claim ceiling in `CLAIM_LEDGER_V3.md`. | **FORMAL IDENTITY BOUNDARY — MAPPED** |
| C5 | The two registered headline generators reproduce their committed scientific payloads under independent replay, and the harness is capable of distinguishing perturbation/missing-generator cases. | `submission/independent-replay-v1/REPLAY_RECEIPT_V1.json`; `submission/independent-replay-v1/replay_cited_receipts_v1.py`; `submission/independent-replay-v1/SHA256SUMS`. | **REPRODUCIBILITY CLAIM — MAPPED; GRANTS NO SCIENTIFIC AUTHORITY** |
| C6 | The receipt index is byte-integrity clean for all 40 indexed entries. | `submission/independent-replay-v1/REPLAY_RECEIPT_V1.json` field `receipt_index_integrity`: 40 parsed, 40 digest matches, 0 missing/mismatched. | **INTEGRITY CLAIM — MAPPED; NOT CLAIM VALIDITY** |
| C7 | The current evidence does not establish cross-domain productivity, causal false-novelty reduction, or superiority over ordinary iteration, donor repair, debugging tools, human research, or research agents. | `CLAIM_LEDGER_V3.md` Q2V3-5 and forbidden promotions; `theory/claim-preserving-recovery-v1/CLAIM_DISPOSITION.md` still-open section; `JOURNAL_READINESS.md`. | **BOUNDARY / NONCLAIM — MAPPED** |

## Coverage verdict

Every scientific assertion in the abstract that carries independent evidentiary weight is covered by C1–C7. Section-level examples inherit the narrower authority of their cited programme receipts; they do not create new headline claims. Bibliographic positioning claims are citation-backed rather than receipt-backed and remain subject to the submission-date literature refresh.

**Terminal:** `FINAL_HEADLINE_CLAIMS_MAPPED__REPLAY_AND_CHECKSUMS_NOT_PROMOTED_TO_SCIENTIFIC_AUTHORITY`

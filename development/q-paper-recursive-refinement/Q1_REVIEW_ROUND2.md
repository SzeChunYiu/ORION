# Q1 refinement round 2 — closure review on V3

**Frozen manuscript:** `papers/Q-paper-01-tare-expressivity/MANUSCRIPT_V3_REFINED.md`  
**Stretch:** PRX Quantum  
**Fallback:** npj Quantum Information  
**Method donor:** pinned `academic-paper-skills` writing/reviewer/figure workflows  
**Reviewer-blindness note:** three lenses are kept logically separate, but this repository pass does not claim cryptographically isolated reviewer contexts.

## Editorial triage

### PRX Quantum

**Posture:** `SEND_TO_REVIEW_CASE_CLEAR__EXCEPTIONAL_INSIGHT_ROUTE`.

The paper now gives an editor a compact decision proof:

- **Question:** can an optimum of an apparently unbounded shared-Tag TARE representation require support growing with system size?
- **Answer:** no; the exact uniform optimum-support threshold is `kappa_R6M=2`.
- **Decisive evidence:** analytic all-`n` exchange + exhaustive support-one lower-bound witness.
- **Why it matters:** a compiler family whose admitted representation support scales with `n` has a system-size-independent intrinsic coupling scale.
- **Boundary:** grammar/objective specific; no general TARE, circuit-complexity, FT-resource or quantum-advantage claim.

The intended PRX exceptionality axis is **exceptional insight**, not broad physical advantage. A real PRX editor may still judge the family too narrow; that remains target-fit risk rather than an internally missing theorem.

### npj Quantum Information

**Posture:** `READY_FOR_SCOPED_TARGET` after ordinary production formatting.

The theorem is clearly in quantum-information/quantum-compilation scope, technically bounded, reproducible and supported by explicit nearest-work subtraction.

## Concern closure ledger

| Round-1 concern | V3 closure | State |
|---|---|---|
| Q1-R1-V1 exchange feasibility interface implicit | Section 2 now lists the exact five invariants used by the exchange and states that no other frozen grammar feasibility condition depends on removed letters | `RESOLVED_BY_CLARIFICATION` |
| Q1-R1-V2 `O(n^12)` mistaken for algorithmic speedup | V3 calls it a representation-count corollary and explicitly rejects a production-DP speedup claim | `RESOLVED_BY_CLAIM_NARROWING` |
| Q1-R1-P1 nearest-work equivalence routes | `NEAREST_WORK_DELTA_V3.md` separates TARE, unitary partitioning, Pauli-frame/symplectic, stabilizer and block-encoding-complexity ownership from the exact residual theorem | `RESOLVED_BY_CLARIFICATION` |
| Q1-R1-P2 PRX breadth / exceptionality | V3 leads with intrinsic representation complexity, constant coupling scale, sharpness and popular summary; finite chemistry is supporting evidence only | `RESOLVED_BY_CLARIFICATION_FOR_INTERNAL_PREFLIGHT`; external target-fit risk remains |
| Q1-R1-R1 main structural figure role | `FIGURE_CONTRACT_V3.md` freezes proof-descent and sharpness visuals; actual journal-rendered vector art remains production work, not missing science | `RESOLVED_BY_CLARIFICATION` |
| Q1-R1-R2 code/data availability | V3 has normal Code and Data Availability text plus reproducibility paths | `RESOLVED_BY_CLARIFICATION` |

## Reviewer 1 — validity

No new technical blocker identified from V3.

The main theorem now states the exact family/objective, defines the cost used in the exchange, records the feasibility invariants, proves the two lemmas and separates the all-size logical proof from finite machine corroboration. The exact support-one lower-bound family remains separately exhaustive.

**Residual request:** in typeset submission, place the full frozen grammar definition or a formal appendix sufficiently close to Theorem 1 that a referee can audit the phrase `admitted instance` without reading repository code.

Classification: `CLARITY_OR_REPORTING`, not blocking.

## Reviewer 2 — positioning/significance

The strongest residual novelty object is now explicit:

`all-n support-two optimum normal form + complete support-one impossibility + exact proof-obstruction/compiler-mechanism correspondence`.

The paper no longer relies on generic “support reduction” as novelty. The nearest-work table gives concrete absorption routes.

**Residual risk:** the field may regard the six-target shared-Tag grammar as too specialized for PRX despite the theorem's sharpness. No additional Q-era benchmark can solve that editorial preference. If PRX declines on breadth, transfer intact to npj Quantum Information rather than diluting the theorem with unrelated QG results.

## Reviewer 3 — reproducibility/readability

The V3 first page, popular summary, theorem-first ordering and code/data section are materially easier to evaluate than the previous submission draft. The central figures now have scientific contracts that separate proof, sharpness and evidence ladder.

Production still needs rendered vector figures and target-style references. Those are submission mechanics, not scientific blockers.

## Round-two engineering scores

Scores are internal prioritization aids, not acceptance probabilities.

| Dimension | /10 |
|---|---:|
| problem_and_question | 9.5 |
| contribution_clarity | 9.5 |
| claim_evidence_alignment | 9.7 |
| technical_rigor | 9.5 |
| novelty_positioning | 8.7 |
| significance_or_field_advance | 8.4 |
| generality_and_boundaries | 8.7 |
| reproducibility_and_availability | 9.2 |
| figure_data_statistics_quality | 8.0 |
| writing_and_evaluability | 9.1 |
| venue_fit | 8.3 |

**Mean:** 8.96/10.

## Terminal

- **PRX Quantum:** `READY_FOR_SCOPED_TARGET` under the internal exceptionality-insight gate; real editor judgment remains external.
- **npj Quantum Information:** `READY_FOR_SCOPED_TARGET`.
- **New Q-era experiment needed:** `NO` for the present theorem claim.

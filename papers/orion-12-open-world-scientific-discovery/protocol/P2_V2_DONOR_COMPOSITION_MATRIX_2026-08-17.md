# P2 V2 donor-composition matrix — 2026-08-17

Status: **PROSPECTIVE DESIGN ARTIFACT**
Parent: `P2_V2_WIDENING_FREEZE_2026-08-17.md`
Issue: #350

## Purpose

Paper 2 should learn aggressively from the strongest nearby systems without copying wording, mislabelling donor mechanics as ORION novelty, or allowing post-outcome selection. This matrix records what is worth absorbing, where it enters the ORION stack, what remains donor-owned, and what incremental ORION residual must still be tested.

The governing split is:

- **acquisition**: how to find, rank, inspect, expand, verify, reread, or continue;
- **authority**: what the resulting local signals are allowed to certify about route/task closure.

A donor mechanism can be adopted wholesale at the acquisition layer without inheriting scientific-closure authority.

## Donor matrix

| Donor / family | Strength to absorb | ORION composition point | Explicitly not ORION novelty | Residual test after absorption |
|---|---|---|---|---|
| SAGE | Strong lexical baseline pressure; corpus-side metadata and keyword augmentation | query/index representation and lexical retrieval | BM25 strength; metadata/keyword augmentation | does typed authority still prevent unsafe global closure when acquisition is stronger? |
| AgentIR | jointly use reasoning state and explicit query as retrieval signal | query derivation / dense retrieval | reasoning-aware retrieval | does earned route independence remain valid when different reasoning traces hit the same backend/corpus? |
| SIEVE / Search-Inspect-Fetch | fielded Boolean admission, structure-rich inspection, selective section fetching | field-aware route + read-budget control | Boolean/field-aware retrieval; inspect/fetch interface | can local field exhaustion or selective fetch ever erase unresolved task obligations? |
| bibliography / citation expansion | breadth-first graph expansion for high recall | citation route / graph frontier | citation chaining / bibliography expansion | route-local graph flatness must not certify global closure; dedup by content identity must prevent graph inflation |
| HALT | claim-evidence coverage as a verification-aware stop signal | route-local continuation / verification signal | verification-aware stopping | evidence coverage may recommend stop but cannot discharge censored/unavailable route obligations by itself |
| MiCP / conformal stopping | target-coverage guarantee for adaptive multi-turn early stopping | route-local continuation / calibrated stopping signal where task-valid | conformal coverage and error-budget allocation | a calibrated local coverage guarantee must not discharge unresolved route/source obligations outside the guarantee's denominator |
| structured Search-R1 stopping | explicit sufficiency + remaining-gap representation | route-local stopping signal | learned STOP/CONTINUE; sufficiency/gap judge | structured STOP must be subordinate to typed task-level authority and safety guard |
| DeepControl / utility continuation | marginal utility signal for continued retrieval | acquisition scheduling / route switching | utility-based continuation | low marginal utility cannot become proof that unknown or censored evidence is absent |
| decision-theoretic screening stop | explicit cost/payoff-aware stop decisions | screening/continuation policy | decision-theoretic stopping | payoff-optimal local stop is distinct from a scientific completeness claim |
| dense / hybrid / RRF | strong semantic and fused candidate generation | candidate-generation layer | dense retrieval / fusion | ORION value must survive stronger candidate generation and matched budgets |
| MetaSyn-style stage separation | retrieval-vs-screening attribution | evaluator and failure ledger | staged systematic-review evaluation | ORION claim must identify earliest failure stage rather than hide retrieval misses inside final recall |
| question-conditioned memory families | question-dependent evidence plans / memory state | reread scheduling | generic question-conditioned memory | ORION residual is content identity separated from question-conditioned processing state |

## Structural lessons absorbed into Paper 2

1. **Lead with one strong systems distinction.** Paper 2 now leads with acquisition vs closure authority rather than with a list of limitations.
2. **Make strong prior work a module, not only a threat.** Nearest work is presented as donor-composable acquisition/stopping pressure; the residual claim is tested after donor subtraction.
3. **Separate stages.** Query derivation, index coverage, candidate generation, ranking, screening, identity, route stop and task stop receive distinct failure attribution.
4. **Report the accuracy/resource frontier.** Token/query/candidate savings are positive only when the stopping-safety guard remains satisfied.
5. **Use direct ablations for the residual.** Each claimed ORION mechanism must have a one-mechanism ablation and strongest relevant donor baseline.
6. **Preserve unknowns as typed states.** Provider failure, censoring and unknown denominators remain `OPEN`/`CANNOT_CHECK`, never convenient zeros.
7. **Treat statistical stopping guarantees as scoped authority.** A guarantee over a defined prediction process is not silently extended to unresolved source families or an unknown literature denominator.
8. **Use transfer as the widest claim gate.** One positive benchmark supports a benchmark claim; general open-world language requires a separately frozen transfer axis.

## Prospective ORION composite candidates

These names identify pre-outcome development families, not authorized positive results.

### `ORION_ACQ_LEXICAL_PLUS`
- SAGE-style lexical + metadata augmentation
- query decomposition/diversification
- content-identity normalization
- ORION route/task authority

### `ORION_ACQ_REASONED_HYBRID`
- lexical + dense/RRF
- AgentIR-style reasoning-aware query representation where runnable
- metadata/field filters
- ORION route/task authority

### `ORION_ACQ_STRUCTURED_EXPAND`
- hybrid retrieval
- SIEVE-style field-aware inspect/fetch where task-valid
- bibliography/citation expansion
- ORION route/task authority

### `ORION_MAX_COMPOSED`
- strongest prospectively selected acquisition components after development-only comparison
- verification/sufficiency/utility/conformal-coverage signals available to route-local continuation where task-valid
- no signal may self-authorize task closure or erase an unresolved source obligation outside its valid denominator
- content/read-state separation, earned independence, censoring obligations and task authority retained

The final confirmatory system identity must be frozen before confirmatory outcome access. Development winners may determine that identity only using development evidence.

## Paper-writing rule

The manuscript may say ORION **composes**, **adopts**, **uses**, or **is compatible with** a donor mechanism only where the implementation/protocol actually does so. It must cite the donor and must not use language implying invention. The manuscript may claim ORION novelty only for a residual that survives direct donor pressure plus ablation.

## Widening target

The strongest intended positive statement, if earned, is not "ORION invented better retrieval." It is:

> Strong acquisition and safe scientific closure are complementary. ORION can compose leading retrieval, expansion and stopping signals while retaining a typed authority boundary that prevents local utility, sufficiency, coverage or source failure from silently becoming evidence of global completeness.

External superiority/transfer language remains gated by the frozen V2 promotion ladder.
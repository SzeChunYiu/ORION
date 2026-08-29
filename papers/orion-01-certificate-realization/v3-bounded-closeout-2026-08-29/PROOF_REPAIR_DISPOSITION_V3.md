# ORION-01 V3 proof-repair disposition

This file maps the independent proof review and sibling-decoupling audit to the successor V3 texts. It is an author-side repair ledger, not an external proof certificate.

## Paper A

| Finding | V2 status | V3 repair | Residual |
|---|---|---|---|
| A-F1 subword/subsequence ambiguity | DEFECT | Section 2 defines subsequence as arbitrary indexed positions, not necessarily contiguous; proper is used only when needed. | none in statement layer |
| A-F2 simultaneous/global fixed point | GAP | Theorem 1 descends on total support over all constrained generators and proves termination at a global fixed point. | depends on A2/A4 premises |
| A-F3 whole-instance feasibility | GAP | A2 is explicitly global; local signature preservation alone is not treated as sufficient. | grammar proof obligation remains visible |
| A-F4 Restore incidence/additivity | GAP | Section 5.1 states one coordinate-indexed Restore term and one changed argument; Section 6 accounts per coordinate. | transfer to another grammar requires a new incidence proof |
| A-F5 solution-relative alphabet | DEFECT RISK | `A_R` is fixed at instance level over all admissible local configurations before selecting an optimum. | computing the restricted invariant may remain hard |
| A-F6 global symplectic sum | GAP | Section 5 derives the first total-signature component from bilinearity of the global symplectic product. | none in stated model |
| A-F7 rank scope | OVERBROAD | Binary-only scope is explicit; `Z_n` singleton counterexample is included. | no general rank theorem claimed |
| A-F8 degenerate `zsf` | DEFECT | Empty sequence is admitted and the zero value is defined. | none |
| A-F9 sharp Restore case | MISSING HYPOTHESIS | Lemma 2 requires identity plus at least two distinct nonidentity Paulis. | none for Pauli alphabet |

## Paper B

| Finding | V2 status | V3 repair | Residual |
|---|---|---|---|
| B-F1 epistemic `kappa` | DEFECT | Section 2 defines `kappa` mathematically from exact optima; evidence is separated from the definition. | parent witness authority remains bounded |
| B-F2 proper/improper subsequence | AMBIGUOUS | Section 3 fixes arbitrary-subsequence conventions and derives properness from nonzero total. | none in statement layer |
| B-F3 objectives not tied | GAP | Sections 2, 5, and 6 declare the same frozen objective `C` for intrinsic and proof-system values. | only the frozen objective is covered |
| B-F4 abstract framing too broad | OVERCLAIM | The manuscript names a rank-only zero-sum deletion system and disclaims general proof complexity. | other proof systems may be stronger |
| B-F5 product theorem oversold | OVERCLAIM | Section 7 labels it definitional amplification and requires additive objective/support plus no cross-component move or rule. | no cross-coupled product claim |
| B-F6 asymptotic regimes conflated | AMBIGUOUS | Section 8 separates growing instance size at fixed rank from growing rank/components. | none |
| B-F7 naming collision | TERMINOLOGY | `certifiable support budget` replaces `certificate complexity`. | none |

## Sibling decoupling

Paper B no longer relies on an unexplained assertion from Paper A for the R6M value. It states the same-objective mathematical definitions and binds the R6M upper/lower artifacts directly:

- `research/extensions/orion-qg/paper_a_a1_multitag_tare.py`
- `research/extensions/orion-qg/PAPER_A_A1_MULTITAG_TARE_RESULTS_2026-08-24.json`
- `research/extensions/orion-qg/QG18_TARE_KAPPA_RESULTS.json`
- `research/extensions/orion-q/MAX_R6S_ALL_N_COMPOSITION_RESULTS.json`

Paper A and Paper B are therefore independently readable while retaining a shared evidence manifest.

## Authority ceiling retained

The repair does not establish:

- general multi-Tag sharpness;
- production move completeness;
- a positive interpretation of the capped Round-3 execution;
- novelty of the restricted zero-sum invariant or binary rank bound;
- external peer-review, replication, submission, or physical-advantage authority.

## Disposition

All statement-level DEFECT/GAP items identified by the bounded review have an explicit V3 repair or an exposed premise. Parent compiler witnesses and the production-completeness successor remain separate obligations.

`BOUNDED_PAPER_RETAINED`

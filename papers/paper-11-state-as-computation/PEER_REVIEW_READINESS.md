# P11 Peer-Review Readiness Report

**Decision:** `READY_FOR_EXTERNAL_REVIEW_AS_CONTROLLED_THEORY/SYSTEMS_RESULT`  
**Not authorized:** cross-domain or real-agent superiority

## Five-lens hostile review

### 1. Theory / systems lens

**Pass.** The main theorem states the access class exactly and does not imply a nonlinear or time-complexity lower bound. The manuscript separates information presence from accessible rank and explicitly charges compilation as computation.

### 2. Experimental-design lens

**Pass with open attack disclosed.** P11/P11B are frozen controlled results with no-answer-laundering controls. P11D is a preregistered negative that changes the interpretation rather than being removed. P11C's tree-ensemble attack has no terminal and is reported as `CANNOT_CHECK`.

### 3. Statistics / reproducibility lens

**Pass for claimed results with one explicit defect.** Exact results need no statistical inference; empirical thresholds are reported as registered grid thresholds and `NOT_REACHED` is not extrapolated. P11D did not achieve byte-identical full-payload replay because the sparse liblinear solver lacked an explicit seed; the scientific summary did replay. This is visible in the claim ledger and root-cause audit.

### 4. Novelty / donor lens

**Pass after subtraction.** The manuscript does not claim query conditioning, state design, compression, partial evaluation, usable information or materialization as new primitives. Novelty is concentrated on the joint accessibility-work/decoder-substitution/optionality account and the controlled evidence supporting it.

### 5. Referee / reporting lens

**Pass for a bounded paper.** Abstract, claims, tables, negative result, limitations, resource accounting, reproducibility and references are internally consistent. The strongest claim is stated once and matches the evidence ledger.

## Submission checklist

- [x] canonical manuscript in current `papers/` directory
- [x] explicit scientific question and contribution list
- [x] theorem assumptions and proof boundary
- [x] donor subtraction / nearest-work boundary
- [x] frozen controlled results reported without invented statistics
- [x] no-answer-laundering hostile control
- [x] negative sparse-decoder result preserved
- [x] negative root cause documented
- [x] replay defect documented
- [x] exact optionality equations separated from real-world generalization
- [x] explicit resource-accounting contract
- [x] claim/evidence ledger
- [x] limitations and strongest remaining attacks
- [ ] P11C ExtraTrees terminal
- [ ] learned non-oracle compiler
- [ ] full end-to-end compiler accounting in a real system
- [ ] smaller-real-reasoner versus larger-universal-reasoner matched-cost replication

## Referee-facing positioning

The paper should not be sold as “query-conditioned features beat universal features.” The most defensible high-ceiling positioning is:

> **A representation is a computational placement decision.** P11 derives and measures how much structural-search work can be moved from a downstream access mechanism into state construction, and shows with a hostile sparse decoder that stronger downstream inductive bias buys that work back. The same move creates quantifiable future-query option debt.

That formulation absorbs the negative rather than narrowing around it.

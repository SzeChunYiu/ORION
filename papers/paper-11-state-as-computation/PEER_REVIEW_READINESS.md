# P11 Peer-Review Readiness Report

**Decision:** `READY_FOR_EXTERNAL_REVIEW_AS_CONTROLLED_THEORY/SYSTEMS_SUPERIORITY_RESULT`  
**Not authorized:** cross-domain or real-agent superiority

## Five-lens hostile review

### 1. Theory / systems lens

**Pass.** The main theorem states the access class exactly and does not imply an unrestricted nonlinear or time-complexity lower bound. The manuscript separates information presence from accessible rank and treats compilation as paid computation.

### 2. Experimental-design lens

**Pass.** P11/P11B are frozen controlled results with explicit no-answer-laundering checks. P11D is permanently negative against its preregistered ≥4×-in-both-cells sparse-decoder gate. Rather than removing that result, P11E independently tests the weaker residual it exposed on a fresh seed with deterministic solver seeds. P11F independently replaces the non-terminating P11C tree attack with a prospectively bounded nonlinear attack.

### 3. Statistics / reproducibility lens

**Pass for the claimed result set.** Exact theorems and option laws need no inferential statistics. Empirical thresholds are registered grid thresholds and `NOT_REACHED` is never extrapolated. P11D's unseeded-liblinear byte-replay defect remains visible; P11E fixes that defect prospectively and produces two byte-identical canonical payloads (`1097d94b…a4536`). P11F also reproduces byte-identically (`aedb2aa0…7dee`).

### 4. Novelty / donor lens

**Pass after subtraction.** Query conditioning, state design, compression, partial evaluation, usable information, materialization, sparse feature selection and tree ensembles are all treated as donor-owned primitives. The contribution is the measured placement relation among state construction, downstream access/search burden and future optionality, supported by exact theory plus hostile decoder substitution experiments.

### 5. Referee / reporting lens

**Pass for controlled scope.** The package states the strongest adverse result in the main claim ledger, reports how a stronger decoder reduces the gain, and then shows the residual independently. The paper therefore makes a superiority claim over registered dense, sparse and nonlinear decoder baselines without pretending that compilation universally dominates all downstream access mechanisms.

## Submission checklist

- [x] canonical manuscript in current `papers/` directory
- [x] explicit scientific question and contribution list
- [x] theorem assumptions and proof boundary
- [x] donor subtraction / nearest-work boundary
- [x] frozen controlled results reported without invented statistics
- [x] no-answer-laundering hostile control
- [x] P11D sparse-decoder negative preserved
- [x] P11D root cause and replay defect documented
- [x] fresh seeded sparse replication P11E
- [x] P11E byte-identical two-run replay
- [x] bounded nonlinear tree successor P11F
- [x] P11F byte-identical two-run replay
- [x] exact optionality equations separated from real-world generalization
- [x] explicit resource-accounting contract
- [x] claim/evidence ledger
- [x] limitations and strongest remaining attacks
- [ ] learned non-oracle compiler
- [ ] full end-to-end compiler accounting in a real system
- [ ] smaller-real-reasoner versus larger-universal-reasoner matched-cost replication

## Referee-facing positioning

> **A representation is a computational placement decision.** P11 derives and measures how structural-search work can be moved from a downstream access mechanism into state construction. Dense universal access shows the largest gains; a hostile sparse decoder buys part of that work back but leaves a fresh deterministic 2×/4× threshold residual; and a separately frozen nonlinear tree ensemble still fails to reach the registered target through `n=1024` where compiled state succeeds at `n=64`. Specialization also creates exact future-query option debt.

This framing uses the negative result as causal evidence about *where the computation moved*, rather than narrowing around it.

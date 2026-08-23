# P11 Peer-Review Readiness Report

**Decision:** `READY_FOR_EXTERNAL_REVIEW_AS_CONTROLLED_THEORY/SYSTEMS_SUPERIORITY_RESULT`  
**Not authorized:** cross-domain or real-agent superiority

## Five-lens hostile review

### 1. Theory / systems lens

**Pass.** The main theorem states the access class exactly and does not imply an unrestricted nonlinear or time-complexity lower bound. The manuscript separates information presence from accessible rank and treats compilation as paid computation.

### 2. Experimental-design lens

**Pass after P11G correction.** P11/P11B are frozen controlled results with explicit no-answer-laundering checks. P11D is permanently negative against its preregistered ≥4×-in-both-cells sparse-decoder gate; P11E independently tests and reproduces the weaker residual on a fresh seed. P11C, after an amendment that vectorized only its parity-bank evaluation, ran to completion twice at `P11C_STRONGER_DECODER_GAP_SUPPORTED` but passes its pooled ≥4× gate at exactly the boundary — 11 of 20 draws of the same construction — so it carries no claim authority in either direction. P11F is retained as non-authoritative because hostile review found a protocol mismatch (`n_jobs=-1` versus the written otherwise-default configuration). P11G was frozen afterward with a fresh seed, explicit single-thread trees and replay enforcement inside the terminal path.

**One standing defect, disclosed rather than repaired.** All four of P11G's scientific gates hold in every world its own freeze admits (48 of 48 fresh seeds), so its survival was fixed before the seed was drawn; and its terminal is a function of which of the three registered universal arms is placed in its gate, while the receipt carries that axis with one value. `P11G_ARM_PLACEMENT_ADJUDICATION_V1.md` states both, retains the frozen terminal verbatim, narrows the ledger row from `PRIMARY` to `ARM-SCOPED`, and says what a successor would need. `python -m orion.study.p11.attack_audit` exits `3` while the attainability finding stands.

### 3. Statistics / reproducibility lens

**Pass for the claimed result set.** Exact theorems and option laws need no inferential statistics. Empirical thresholds are registered grid thresholds and `NOT_REACHED` is never extrapolated. P11D's unseeded-liblinear byte-replay defect remains visible; P11E fixes that defect prospectively and produces byte-identical canonical payloads (`1097d94b…a4536`). P11G launches two fresh Python subprocesses, requires exact scientific byte identity before promotion, and obtains identical payload SHA-256 `a2b0c33c…79a7cc`.

### 4. Novelty / donor lens

**Pass after subtraction.** Query conditioning, state design, compression, partial evaluation, usable information, materialization, sparse feature selection and tree ensembles are all treated as donor-owned primitives. The contribution is the measured placement relation among state construction, downstream access/search burden and future optionality, supported by exact theory plus hostile decoder substitution experiments.

### 5. Referee / reporting lens

**Pass for controlled scope.** The package states both failed hostile claims and protocol defects rather than deleting them, then uses independent successors to test the surviving mechanism. The paper makes a superiority claim over registered dense, sparse and deterministic nonlinear decoder baselines without pretending that compilation universally dominates all downstream access mechanisms.

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
- [x] P11E byte-identical replay
- [x] P11C execution history retained: non-termination, amendment, completed run, boundary-passing pooled gate, no claim authority
- [x] P11G arm axis measured and declared; terminal retained verbatim and scoped
- [x] P11G `n=64` gap decomposed into decoder-family and state halves
- [x] P11H successor freezes the universal-arm pool and gates through it
- [x] P11H hostile gate has both terminals reachable before execution
- [x] P11I prospectively replicates the positive high-width regime across nine fresh units
- [x] P11I includes nine matched low-width controls where the pooled attack remains live
- [x] P11F protocol mismatch disclosed and removed from claim authority
- [x] P11G frozen after review finding
- [x] P11G single-thread deterministic trees
- [x] P11G terminal requires two fresh subprocess replay identity
- [x] exact optionality equations separated from real-world generalization
- [x] explicit resource-accounting contract
- [x] claim/evidence ledger
- [x] limitations and strongest remaining attacks
- [ ] learned non-oracle compiler
- [ ] full end-to-end compiler accounting in a real system
- [ ] smaller-real-reasoner versus larger-universal-reasoner matched-cost replication

## Referee-facing positioning

> **A representation is a computational placement decision.** P11 derives and measures how structural-search work can be moved from a downstream access mechanism into state construction. Dense universal access shows the largest gains; a hostile sparse decoder buys part of that work back but leaves a fresh deterministic 2×/4× threshold residual; and a separately frozen deterministic 96-tree ExtraTrees decoder remains below the registered target through `n=1024` where compiled state succeeds at `n=64`, scoped to that arm. Specialization also creates exact future-query option debt.

This framing uses negative results and protocol failures as causal/audit evidence about *where the computation moved*, rather than narrowing around or hiding them.

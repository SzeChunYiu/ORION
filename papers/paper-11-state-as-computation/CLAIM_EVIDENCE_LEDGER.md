# P11 Claim–Evidence Ledger

**Stable ID:** ORION-P11  
**Issues:** #471, #664, #667  
**Evidence cut:** 2026-08-21

| Claim | Status | Evidence | Maximum authorized wording |
|---|---|---|---|
| fixed exact linear-accessible state needs dimension at least query-family rank | SUPPORTED / EXACT | Theorem 1 | exact theorem for the registered access class |
| size-`s` parity family needs `binom(d,s)` fixed accessible coordinates | SUPPORTED / EXACT | parity corollary | exact linear-accessible representation result |
| registered universal/compiled representation ratios are 91×–1820× | SUPPORTED / CONTROLLED | P11 receipt | controlled parity-query cells only |
| query-conditioned compilation gives 4× to >32× sample-threshold gain against registered dense universal decoder | SUPPORTED / CONTROLLED | P11/P11B receipts | dense-decoder, frozen-cell result |
| P11B/P11D/P11E/P11G do not launder the final answer | SUPPORTED / HOSTILE CONTROL | zero component/negation matches | registered constructions only |
| compilation retains ≥4× threshold advantage against sparse universal decoding in both hostile cells | **NEGATIVE / FALSE** | P11D terminal | never state this |
| P11D retains 2× and 4× thresholds against sparse universal decoding | SUPPORTED / CONTROLLED | P11D | original two hostile cells; full JSON replay defect disclosed |
| P11D byte-identical full-payload replay | **NEGATIVE / FALSE** | unseeded sparse liblinear | never claim |
| seeded sparse replication retains ≥2× threshold residual in both cells | **SUPPORTED / REPLICATED** | P11E | fresh seed: 128/64 and 256/64 sparse/compiled thresholds |
| P11E compiled-minus-sparse accuracy at `n=64` is +0.2912 and +0.3307 | SUPPORTED / REPLICATED | P11E | two registered cells |
| P11E two-run canonical payload is byte-identical | SUPPORTED / REPRODUCIBLE | SHA `1097d94b…a4536` | exact harness/environment result |
| original large ExtraTrees P11C emitted a terminal | SUPPORTED / NO CLAIM AUTHORITY | `P11C_EXECUTION_RECEIPT_V1.md`, SHA `f65c1c5b…f939c454` | first attempt exceeded the window; after the vectorization amendment the frozen protocol ran to completion twice at `P11C_STRONGER_DECODER_GAP_SUPPORTED`. Its pooled ≥4× gate passes at exactly the boundary and the boundary comes up in 11 of 20 draws, so it settles nothing in either direction and does not restore the ≥4× claim P11D retired |
| P11C's pooled best-of-arms combination rule was applied to an outcome | SUPPORTED | `best_universal_threshold_0_95` = 256/256 and `best_universal_threshold_ratio_ge_4` = true in P11C's frozen payload | inside P11C's own protocol only; it does not bind P11D, P11E or P11G, which each froze a single-arm statistic under their own identity |
| P11F is protocol-conforming authoritative nonlinear evidence | **FALSE / CORRECTED** | hostile PR review | `n_jobs=-1` violated frozen protocol/default contract |
| P11F numerical output exists | DIAGNOSTIC ONLY | P11F history | never use as primary nonlinear authority |
| a deterministic single-thread 96-tree ExtraTrees decoder on the complete parity bank does not close the registered low-sample gap | **SUPPORTED / HOSTILE NONLINEAR / ARM-SCOPED** | P11G, scoped by `P11G_ARM_PLACEMENT_ADJUDICATION_V1.md` | fresh seed, 96 trees, `n_jobs=1`, replay gate in terminal path; this is P11G's own claim-authority sentence and is the maximum it supports |
| P11G's terminal holds against universal-state decoding as such | **NOT AUTHORIZED** | `decoder_arm` axis: 3 registered arms, 2 of 3 comparable pairs verdict-changing | `UNIVERSAL_L1` reaches 0.95 at `n=128` in cell (17,4,5) on P11G's own data and would print `..._GAP_NOT_MET`; the receipt carries the axis with one value. A pooled claim needs a protocol that freezes the pool and gates through it |
| P11G's terminal was reachable in both directions under its own freeze | **NEGATIVE / FALSE** | `orion.study.p11.attack_audit`, 48 of 48 admissible worlds | all four scientific gates hold in every world the freeze admits; the survival was fixed before the seed was drawn. `UNWINNABLE_ATTACK_PREDETERMINED_SURVIVAL`, open against a successor |
| P11G tree universal arm reaches 0.95 by `n=1024` | FALSE | P11G | `NOT_REACHED` in both cells |
| P11G compiled arm reaches 0.95 by `n=64` in both cells | SUPPORTED | P11G | exact registered grid |
| P11G compiled-minus-tree accuracy at `n=64` is +0.4624 and +0.3942 | SUPPORTED | P11G | two fresh cells |
| the majority of those two gaps is the change of state rather than the change of decoder family | SUPPORTED / DECOMPOSED | `COMPILED_EXTRA_TREES` control on P11G's own stream | decoder half +0.0614 and +0.1757, state half +0.4010 and +0.2185, i.e. 86.7% and 55.4% state; measured with the decoder held fixed, so no choice of universal arm moves it |
| P11G two fresh subprocess scientific payloads are byte-identical | **SUPPORTED / REPRODUCIBLE** | P11G terminal path | both SHA `a2b0c33c…79a7cc` |
| future-query option coverage follows `r/N`, `1-(1-r/N)^K` and coupon-style distinct-demand law in frozen model | SUPPORTED / EXACT | optionality theorem/receipt | exact specified workload model |
| state compilation universally dominates universal state | NOT AUTHORIZED | sparse hostile result + optionality regimes | forbidden |
| a smaller real reasoner with compiled state beats a larger universal-state reasoner | OPEN | real-system gate | not inferred from controlled learner |
| state construction externalizes structural search from a bounded downstream access mechanism | **SUPPORTED SYNTHESIS / PRIMARY** | theorem + dense + P11D/P11E + P11G's arm-scoped result and its decoder-held-fixed decomposition + optionality | strongest current paper-level mechanism claim; each hostile arm carries its own verdict and none of them carries a pooled one |

## Evidence corrections

### P11D

The original sparse hostile gate stays negative: one cell is 2× rather than the preregistered ≥4×. Its full-payload replay defect is also retained. P11E was frozen separately and reproduces the surviving 2×/4× residual with explicit stochastic seeds and byte-identical payloads.

### P11F protocol-conformance finding

Hostile PR review found that P11F set `n_jobs=-1` although its frozen protocol specified the registered tree configuration with otherwise sklearn defaults. Even though two observed P11F payloads matched, the implementation did not exactly instantiate the written protocol. P11F is therefore diagnostic/non-authoritative.

### P11F → P11G

P11G was frozen after that finding on a fresh seed. It explicitly pins `n_jobs=1`, every estimator random state, and requires its authoritative executable to launch two fresh Python subprocesses and compare complete canonical scientific bytes before a positive terminal is possible. Both scientific payload SHA-256 values are `a2b0c33ce3c39e54ca1aa400a2b7d52d019fc4503f6cd5eb726c7b8bbe79a7cc`. The universal tree arm remains `NOT_REACHED` through `n=1024` in both cells while compiled state reaches 0.95 by `n=64`; `n=64` gaps are +0.4624 and +0.3942.

### P11G arm scoping

`P11G_ARM_PLACEMENT_ADJUDICATION_V1.md` reclassifies P11G's terminal without editing a frozen byte. The terminal, seed, gates, receipt and both payload digests are retained verbatim and no published number moves. What changed is the row above: P11G's receipt publishes curves for one of the three universal-state arms the programme registered, and on P11G's own data two of the three comparable pairs on that axis change the verdict — `UNIVERSAL_L1` reaches 0.95 at `n=128` in cell (17,4,5), which P11G's own ≥256 gate reads as `NOT_MET`. The terminal is therefore evidence about the arm it names, which is exactly what P11G's own claim-authority sentence says, and the `HOSTILE NONLINEAR / PRIMARY` promotion is withdrawn in favour of `ARM-SCOPED`.

The adjudication also settles the cross-protocol question. P11C's pooled best-of-arms rule feeds a ≥4× ratio gate on a five-query, `n=2048`, 8,192-test ladder over a 256-tree pool, for a claim about a family of attacks; P11G froze an absolute ≥256 gate on a three-query, `n=1024`, 4,096-test ladder over one 96-tree arm, for a claim about one decoder. The rule governs P11C, where it was applied. It does not bind P11G, and the `[128, 256]` transplant is a measurement of the arm axis rather than a refutation of P11G's terminal.

## Donor subtraction

- **Predictive V-information:** owns computationally restricted usable information and computation changing usability. P11 owns neither primitive.
- **State Design Matters (Wong et al., 2026):** owns empirical evidence that representation/state design changes LLM reasoning and that representation construction can induce useful computation.
- **QUMem (2026):** owns query-conditioned user-state inference as a current agent-memory primitive.
- **ACON and context-compression literature:** own learned compression and long-horizon memory/performance trade-offs.
- **Partial evaluation / knowledge compilation / materialized views:** own upstream computation, specialization and reuse as classical ideas.
- **Sparse feature selection and nonlinear ensembles:** own decoder-side inductive biases that can search a universal feature bank; P11 treats them as hostile substitutes for compilation, not as ORION primitives.

## Residual novelty

P11's residual is the **placement law between state construction and downstream access**. A universal state can contain every task-relevant coordinate yet force a bounded decoder to discover which coordinates matter. Query-conditioned construction moves that discovery work upstream. Stronger sparse decoding buys part of the work back—as it should—while the fresh deterministic P11E replication still leaves 2× and 4× sample-threshold gaps. A separately frozen, protocol-conforming single-thread nonlinear P11G attack fails to reach 0.95 through `n=1024` while compiled state reaches the target by `n=64` in both cells — a result about that one 96-tree arm, since the sparse arm reaches the target at `n=128` in the first cell on P11G's own data, and one whose `n=64` gap is 86.7% and 55.4% the change of state once the decoder is held fixed. The same upstream specialization has an exact future-query cost when raw/recoverable state is discarded.

## Strongest authorized headline

> **State is a computational placement decision.** In controlled query families, query-conditioned construction yields exact combinatorial accessible-rank savings and large dense-decoder sample gains; a hostile sparse decoder recovers part of the advantage but leaves a fresh deterministic 2×/4× residual, and a replay-gated deterministic 96-tree ExtraTrees decoder remains `NOT_REACHED` through `n=1024` where compiled state reaches the target at `n=64` — a per-arm result, not a pooled one. Exact workload laws quantify the future-query option debt created by specialization.

This is a controlled theory/systems superiority claim, not a universal nonlinear lower bound or real-agent superiority claim.

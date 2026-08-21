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
| P11B/P11D/P11E/P11F do not launder the final answer | SUPPORTED / HOSTILE CONTROL | zero component/negation matches | registered constructions only |
| compilation retains ≥4× threshold advantage against sparse universal decoding in both hostile cells | **NEGATIVE / FALSE** | P11D terminal | never state this |
| P11D retains 2× and 4× thresholds against sparse universal decoding | SUPPORTED / CONTROLLED | P11D | original two hostile cells; full JSON replay defect disclosed |
| P11D byte-identical full-payload replay | **NEGATIVE / FALSE** | unseeded sparse liblinear | never claim |
| seeded sparse replication retains ≥2× threshold residual in both cells | **SUPPORTED / REPLICATED** | P11E | fresh seed: 128/64 and 256/64 sparse/compiled thresholds |
| P11E compiled-minus-sparse accuracy at `n=64` is +0.2912 and +0.3307 | SUPPORTED / REPLICATED | P11E | two registered cells |
| P11E two-run canonical payload is byte-identical | SUPPORTED / REPRODUCIBLE | SHA `1097d94b…a4536` | exact harness/environment result |
| original large ExtraTrees P11C emitted a terminal | FALSE / CANNOT_CHECK | P11C timeout history | no P11C result claim |
| tractable nonlinear tree successor preserves compilation advantage | **SUPPORTED / HOSTILE NONLINEAR** | P11F | fresh cells, frozen 96-tree envelope |
| P11F tree universal arm reaches 0.95 by `n=1024` | FALSE | P11F | `NOT_REACHED` in both cells |
| P11F compiled arm reaches 0.95 by `n=64` in both cells | SUPPORTED | P11F | exact registered grid |
| P11F compiled-minus-tree accuracy at `n=64` is +0.4460 and +0.4029 | SUPPORTED | P11F | two fresh cells |
| P11F two-run canonical payload is byte-identical | SUPPORTED / REPRODUCIBLE | SHA `aedb2aa0…7dee` | exact harness/environment result |
| future-query option coverage follows `r/N`, `1-(1-r/N)^K` and coupon-style distinct-demand law in frozen model | SUPPORTED / EXACT | optionality theorem/receipt | exact specified workload model |
| state compilation universally dominates universal state | NOT AUTHORIZED | sparse hostile result + optionality regimes | forbidden |
| a smaller real reasoner with compiled state beats a larger universal-state reasoner | OPEN | real-system gate | not inferred from controlled learner |
| state construction externalizes structural search from a bounded downstream access mechanism | **SUPPORTED SYNTHESIS / PRIMARY** | theorem + dense + sparse replication + nonlinear attack + optionality | strongest current paper-level mechanism claim |

## Donor subtraction

- **Predictive V-information:** owns computationally restricted usable information and computation changing usability. P11 owns neither primitive.
- **State Design Matters (Wong et al., 2026):** owns empirical evidence that representation/state design changes LLM reasoning and that representation construction can induce useful computation.
- **QUMem (2026):** owns query-conditioned user-state inference as a current agent-memory primitive.
- **ACON and context-compression literature:** own learned compression and long-horizon memory/performance trade-offs.
- **Partial evaluation / knowledge compilation / materialized views:** own upstream computation, specialization and reuse as classical ideas.
- **Sparse feature selection and nonlinear ensembles:** own decoder-side inductive biases that can search a universal feature bank; P11 treats them as hostile substitutes for compilation, not as ORION primitives.

## Residual novelty

P11's residual is the **placement law between state construction and downstream access**. A universal state can contain every task-relevant coordinate yet force a bounded decoder to discover which coordinates matter. Query-conditioned construction moves that discovery work upstream. Stronger sparse decoding buys part of the work back—as it should—while the fresh deterministic P11E replication still leaves 2× and 4× sample-threshold gaps. A separately frozen nonlinear ExtraTrees attack fails to reach 0.95 through `n=1024` while compiled state reaches the target by `n=64` in both cells. The same upstream specialization has an exact future-query cost when raw/recoverable state is discarded.

## Strongest authorized headline

> **State is a computational placement decision.** In controlled query families, query-conditioned construction yields exact combinatorial accessible-rank savings and large dense-decoder sample gains; the advantage survives a fresh deterministic sparse-decoder replication (2× and 4× threshold gaps) and a frozen nonlinear tree-ensemble attack (universal `NOT_REACHED` through `n=1024` versus compiled `n=64`), while stronger sparse access demonstrably recovers part of the gap. Exact workload laws quantify the future-query option debt created by specialization.

This is a controlled theory/systems superiority claim, not a universal nonlinear lower bound or real-agent superiority claim.

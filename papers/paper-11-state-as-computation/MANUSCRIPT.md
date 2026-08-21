# State as Computation: Moving Structural Search between Representation Construction and Downstream Reasoning

**ORION P11 — peer-review manuscript**  
**Issues:** #471, #664, #667  
**Evidence cut:** 21 August 2026

## Abstract

Reasoning systems are usually compared as if the state presented to the downstream learner were fixed. We study a different resource boundary: **constructing task-relevant state is itself computation**, and that computation can substitute for search performed by the downstream access mechanism. For a query family `F`, we first show that any fixed representation supporting exact linear readout of every query requires dimension at least `rank(F)`. For all size-`s` parity queries on `d` Boolean variables this becomes `binom(d,s)` accessible coordinates, whereas a query-conditioned compiler needs only the coordinates selected by the current query. Frozen controlled experiments produce universal/compiled representation ratios of 91×–1820× and dense-decoder sample-threshold reductions from 4× to more than 32×. A no-answer-laundering construction exposes 5–7 latent components rather than the final label and retains large gains. We then attack the mechanism rather than protect it. A preregistered sparse universal decoder **falsifies** the stronger claim that compilation retains at least a 4× threshold advantage in both hostile cells, recovering part of the search burden and leaving 2× and 4× residual gaps. A fresh deterministically seeded replication reproduces those 2×/4× gaps with +0.291/+0.331 accuracy advantages at `n=64`. A separately frozen nonlinear ExtraTrees attack does not reach 0.95 accuracy through `n=1024` in either cell, while compiled state reaches the target by `n=64`; low-sample gaps are +0.446 and +0.403. Finally, exact workload laws quantify the option debt created when specialized state is retained without raw recoverability. The resulting claim is not that compilation universally dominates representation or inference. It is that **state design determines where structural-search computation is paid**, and this placement can be measured jointly through accessible rank, decoder/sample burden, construction cost, and future optionality.

## 1. Introduction

A system can possess all information required for a task and still make that information difficult for a bounded learner to use. Computationally usable information formalizes one version of this idea; partial evaluation and knowledge compilation move work upstream; materialized views trade preprocessing and storage for later query cost; current agent systems retrieve, compress, summarize, or restructure context before generation. Recent LLM evidence also shows that state design itself can materially change dynamic reasoning, even when model parameters are fixed.

Those results make a weak novelty claim untenable. P11 does **not** claim that representation matters, that computation can create usable information, that query-conditioned memory is new, or that compression can reduce downstream cost. The unresolved question is a resource-placement question:

> **When a task-relevant structure can be discovered either while constructing state or later by the decoder/search process, where is the computation paid, how much downstream burden can be removed, and what future optionality is lost by specialization?**

We call this view *state as computation*. A compiler `C(R,q)` receives raw state `R` and a current query `q`, constructs a task-facing state, and hands that state to a bounded downstream mechanism. Compilation is never free: compiler operations, state bytes, training cost, cache/recovery cost, downstream samples or search, verifier/tool calls, latency and—when reproducibly measurable—energy belong to one resource receipt.

The paper makes four contributions.

1. **Accessible-rank theory.** For a fixed linear-access class, query-family rank gives an exact lower bound on the dimension required to support every query. This separates information presence from accessibility under a declared decoder class.
2. **Controlled compilation gaps.** Frozen parity-query studies show large accessible-dimension and sample-threshold differences, including a construction that forbids the compiler from outputting the final answer.
3. **Hostile decoder substitution.** A sparse universal decoder recovers part of the compilation advantage, falsifying an intentionally stronger gate; a fresh deterministic replication retains a smaller 2×/4× residual, and a prospectively bounded nonlinear tree ensemble leaves a larger low-sample residual. This identifies decoder inductive bias as a substitute for upstream compilation rather than an inconvenient alternative explanation.
4. **Future-optionality law.** Exact workload equations show when specialization creates future-query debt and when caching, raw recovery, or universal materialization becomes preferable.

The strongest conclusion is therefore mechanistic rather than universal: **representation construction and downstream access are two loci at which the same structural-search burden can be paid**.

## 2. Donor boundary and novelty residual

### 2.1 Prior-owned primitives

Predictive `V`-information already establishes that computational constraints change what information is usable and that computation can create usable information. Classical partial evaluation specializes programs to known inputs. Knowledge compilation and database materialization move computation upstream for later reuse. Feature selection and sparse models search for relevant coordinates inside a larger representation. Query-conditioned memory and retrieval systems condition state on the current task. Long-horizon context-compression systems explicitly optimize the memory/performance trade-off. Wong et al. show directly that state representation and the act of construction can change LLM reasoning.

P11 therefore subtracts all of those primitives from its novelty claim.

### 2.2 Residual contribution

The residual is a **joint placement account**:

`raw state -> construction work -> task-facing state -> decoder/search work -> verified outcome`

with future reuse appended as a second horizon:

`task-facing state + raw/cache policy -> future query service or option debt`.

The paper asks how accessible rank, downstream sample/search burden, upstream construction, cache/recovery and future-query coverage move together when the same underlying information is exposed differently.

## 3. Formal setup

Let `X` be a domain with distribution `mu`, and let `F={f_1,...,f_N}` be query functions in `L2(mu)`. A fixed query-agnostic representation is `phi:X->R^m`. It supports exact linear query answering when, for every `q`, some `w_q` satisfies

`f_q(x) = <w_q, phi(x)>`

almost surely.

A query-conditioned compiler instead sees `(x,q)` and emits `C(x,q)` before a downstream mechanism acts. The scientific comparison is meaningful only under an explicit access class and resource boundary.

### Theorem 1 — query-family accessible-rank bound

If `span(F)` has dimension `r`, every fixed representation supporting exact linear readout of all queries has `m >= r`.

**Proof.** Every `f_q` lies in the span of the `m` coordinate functions of `phi`. That span has dimension at most `m` and must contain the `r`-dimensional span of `F`; hence `m>=r`. □

The theorem is elementary linear algebra. The contribution is its role as a resource boundary, not mathematical novelty.

### Approximate orthonormal frontier

For orthonormal `f_1,...,f_N` and any `m`-dimensional linearly accessible subspace `U`, Bessel's inequality gives

`(1/N) sum_q ||f_q - P_U f_q||_2^2 >= 1 - m/N`.

This is an access-class statement; it is not a lower bound on an unrestricted nonlinear decoder.

### Parity corollary

For `X={-1,+1}^d` under the uniform measure and all size-`s` subsets `S`, define

`f_S(x)=product_{i in S} x_i`.

Distinct parity characters are orthogonal. A fixed exact linear-accessible representation supporting all size-`s` queries therefore requires at least

`binom(d,s)`

coordinates. A query-conditioned construction need expose only the selected query structure. This establishes an exact **accessible-representation** gap, not a total-time lower bound.

## 4. Controlled studies

### 4.1 P11 dense universal-state study

The confirmatory study compares raw linear input, a fixed universal parity bank, and query-conditioned compiled state over a frozen train-size grid. The registered cells give:

| `d` | `s` | universal dims | compiled dims | universal/compiled | compiled `n` at 0.90 | universal `n` at 0.90 |
|---:|---:|---:|---:|---:|---:|---:|
| 14 | 2 | 91 | 1 | 91× | 32 | 128 |
| 16 | 4 | 1820 | 1 | 1820× | 32 | `NOT_REACHED` by 1024 |
| 18 | 3 | 816 | 1 | 816× | 32 | 1024 |
| 20 | 3 | 1140 | 1 | 1140× | 32 | 1024 |

At `n=1024`, compiled accuracy is 1.0 in every cell. The corresponding universal accuracies are 1.0000, 0.8455, 0.9915 and 0.9469. Raw linear remains near chance. The canonical P11 replay is byte-identical across fresh processes.

The result is consistent with a structural-search interpretation: the decisive coordinates exist in the universal bank, but a bounded dense decoder must identify them among many irrelevant candidates.

### 4.2 P11B no-answer-laundering study

A direct compiler that emits `f_q(x)` can be criticized for returning the answer. P11B therefore exposes only the `r` active parity components selected by a query, with `r` in `{5,7}`. The downstream logistic learner must still infer an odd-cardinality majority target. Every component is checked against the final signed label and its negation.

| `d` | `s` | `r` | universal dims | universal `n` at 0.95 | compiled `n` at 0.95 |
|---:|---:|---:|---:|---:|---:|
| 15 | 3 | 5 | 455 | 2048 | 64 |
| 17 | 3 | 5 | 680 | 2048 | 64 |
| 17 | 4 | 5 | 2380 | `NOT_REACHED` by 2048 | 64 |
| 19 | 3 | 7 | 969 | `NOT_REACHED` by 2048 | 64 |

No compiled component equals or negates the final label. The high-dimensional cells therefore exhibit at least 32× threshold separation under the registered dense decoder without answer laundering.

## 5. Hostile decoder substitution

The central alternative explanation is straightforward: perhaps the universal representation is penalized only because the downstream decoder has the wrong inductive bias. If so, stronger decoder-side search should buy back the compilation advantage. P11 treats that prediction as a mechanism test.

### 5.1 P11D sparse decoder — a permanent negative

P11D preregistered a strong hostile gate: an L1 sparse universal decoder should still leave at least a 4× sample-threshold advantage for compiled state in **both** high-dimensional cells. It did not.

| cell `(d,s,r)` | universal dims | compiled dims | sparse universal `n` at 0.95 | compiled `n` at 0.95 | ratio | compiled - sparse at `n=64` |
|---|---:|---:|---:|---:|---:|---:|
| (17,4,5) | 2380 | 5 | 128 | 64 | 2× | +0.2903 |
| (19,3,7) | 969 | 7 | 256 | 64 | 4× | +0.3840 |

The preregistered terminal is therefore `P11D_SPARSE_DECODER_GAP_NOT_MET` and remains permanently negative. This result matters scientifically: sparse decoder-side feature discovery is a **substitute** for upstream state construction.

P11D also revealed a reproducibility defect. The scientific summary repeated, but the full JSON hashes differed because the sparse `liblinear` solver lacked an explicit random seed. That defect is not hidden or retrospectively edited.

### 5.2 P11E deterministic sparse replication

P11E was frozen after P11D, uses a fresh data seed, explicitly seeds every stochastic estimator, and asks a weaker question justified by the negative: does at least a 2× threshold residual replicate in both cells?

It does.

| cell | sparse universal `n` at 0.95 | compiled `n` at 0.95 | ratio | compiled - sparse at `n=64` |
|---|---:|---:|---:|---:|
| (17,4,5) | 128 | 64 | 2× | +0.2912 |
| (19,3,7) | 256 | 64 | 4× | +0.3307 |

Two fresh executions produce the same canonical SHA-256:

`1097d94bef1132d4dfa5d01176a9fcfcfebc46de8113e7cb2e57da1e579a4536`.

P11E does not relabel P11D. It establishes that the smaller residual exposed by the failed hostile gate independently replicates.

### 5.3 P11F tractable nonlinear tree attack

The original P11C ExtraTrees attack was too large for the available execution window and emitted no authoritative terminal. It remains `CANNOT_CHECK`. P11F is a new prospectively bounded successor: 96 ExtraTrees estimators with frozen seeds, three queries per cell, train sizes through 1024, and the same no-answer-laundering construction.

| cell | tree universal `n` at 0.95 | compiled `n` at 0.95 | tree accuracy at `n=1024` | compiled - tree at `n=64` |
|---|---:|---:|---:|---:|
| (17,4,5) | `NOT_REACHED` | 64 | 0.8194 | +0.4460 |
| (19,3,7) | `NOT_REACHED` | 64 | 0.7703 | +0.4029 |

The terminal is `P11F_TREE_DECODER_GAP_SUPPORTED`. Two executions are byte-identical with canonical SHA-256

`aedb2aa0cc31ddb1b5395dfebc439bc26288b455deab8c4abb12a18ff9fd7dee`.

This is not a nonlinear lower bound. It is a hostile finite-system result showing that one frozen nonlinear universal-state decoder still pays substantial discovery cost under the registered resource envelope.

## 6. What the decoder attacks identify

The three decoder regimes reveal a pattern that a dense-only experiment could not establish.

- Dense universal access pays the largest discovery cost.
- Sparse universal access recovers part of that cost and falsifies an intentionally stronger residual claim.
- Fresh deterministic sparse replication retains a smaller 2×/4× threshold separation.
- A separately bounded nonlinear tree ensemble does not close the high-dimensional low-sample gap.

This supports the interpretation that **compilation and decoder inductive bias are alternative locations for structural search**. If the downstream mechanism already knows how to identify the relevant coordinates cheaply, upstream compilation should matter less. If it does not, state construction can externalize that work.

## 7. Future optionality

Current accessibility and future optionality are different objectives. Let a universal state contain `N` independent query coordinates and a compiled state retain `r`.

If the raw source is lost, one-step coverage for a uniformly random future query is exactly

`r/N`.

If `K` independently selected size-`r` compilations are cached, expected coverage is

`1-(1-r/N)^K`.

Under uniform demand, the expected number of distinct requested components after `K` queries is

`N[1-(1-1/N)^K]`.

These laws produce four policy regimes:

- **compile only:** lowest current state, highest option debt when source is lost;
- **compile + cache:** state grows with encountered demand;
- **retain raw + compile:** current state remains small and future coverage remains recoverable, but misses pay recompilation/retrieval cost;
- **universal materialization:** immediate multi-query coverage at larger upfront work and memory cost.

In the frozen workload study, the first grid point where universal bulk compilation becomes cheaper than expected cache compilation occurs at `0.5N`, `1.0N`, and `2.0N` future-query horizons for batch-efficiency factors 0.25, 0.50, and 0.75 respectively. Concentrated Zipf-like workloads delay this crossover because fewer distinct coordinates are demanded.

These are exact workload-model results, not universal agent-memory laws.

## 8. Accessibility-work accounting

Any comparison that treats representation construction as free is invalid. The P11 resource receipt therefore keeps separate coordinates for:

- compiler/preprocessing operations and latency;
- constructed-state bytes/tokens and memory traffic;
- downstream model identity/capacity;
- training examples or generated/recurrent steps;
- search nodes, verifier calls and tool calls;
- cache memory and reuse;
- raw recovery/reconstruction/recompilation;
- end-to-end latency and reproducible energy where available.

Learned-compiler training cost must be reported separately and amortized only under a prospectively stated reuse horizon. Unless a real application supplies exchange rates, results should be presented as Pareto surfaces rather than collapsed into a post-hoc scalar cost.

## 9. Related work

Predictive `V`-information provides the closest information-theoretic parent by making usable information relative to a computational family. Partial evaluation and knowledge compilation provide the closest upstream-computation parents. Materialized views and multi-query optimization provide the clearest reuse/crossover analogues. Modern query-conditioned memory, retrieval and context-compression systems demonstrate practical task-conditioned state construction. Wong et al. provide direct current evidence that state design changes dynamic LLM reasoning. P11's residual is not any of these primitives in isolation; it is the experimentally attacked relation between **where structure is exposed, how much discovery work remains downstream, what that exposure costs, and what future options it destroys or preserves**.

## 10. Limitations and falsifiers

1. The exact theorem is restricted to a declared linear-access class; it is not an unrestricted representation or time lower bound.
2. Parity families are deliberately controlled and expose exact rank. They are not evidence that the same numerical separations hold in language-model state.
3. P11D proves that stronger decoder bias can materially reduce the compilation advantage. Any general theory must predict this substitution rather than ignore it.
4. P11F tests one finite nonlinear ensemble under a frozen resource envelope; other nonlinear decoders may behave differently.
5. The current compiler is oracle/query-structured rather than a learned non-oracle compiler.
6. Controlled operation counts do not substitute for end-to-end compiler/model latency, memory traffic, training cost or energy in real systems.
7. Future-query option laws assume the declared workload model. Drift, semantic invalidation and correlated responsibilities require separate modelling.
8. A broad real-system superiority claim requires at least one matched same-information LLM/procedural setting and one formal/search or long-horizon memory setting.

These are promotion gates, not reasons to weaken the controlled claim already established.

## 11. Reproducibility

The paper package retains the full sequence rather than only successful endpoints:

- P11/P11B frozen dense and no-answer-laundering protocols and receipts;
- P11C non-terminating nonlinear attack as `CANNOT_CHECK`;
- P11D permanent sparse-decoder negative and its unseeded-solver root cause;
- P11E fresh seeded sparse replication and canonical hash;
- P11F fresh bounded nonlinear attack and canonical hash;
- exact optionality theorem and deterministic workload receipt.

The authoritative P11E canonical hash is `1097d94bef1132d4dfa5d01176a9fcfcfebc46de8113e7cb2e57da1e579a4536`. The authoritative P11F canonical hash is `aedb2aa0cc31ddb1b5395dfebc439bc26288b455deab8c4abb12a18ff9fd7dee`.

## 12. Discussion

The experiments change the interpretation of task-conditioned state construction. The strongest story is not that a compiler creates magic information or universally beats a universal representation. The decisive variable is **who performs structural search**.

A query-conditioned compiler performs some search before the downstream learner sees the state. A dense decoder leaves almost all of that burden downstream; a sparse decoder has a mechanism for finding relevant coordinates and therefore reduces the gap; a finite nonlinear tree ensemble provides another search mechanism but remains inefficient in the registered high-dimensional low-sample regime. The adverse sparse result is therefore part of the causal evidence: it identifies an axis along which the state advantage should shrink.

This view also connects current accuracy to future flexibility. Aggressive specialization can make one task cheap while destroying immediate support for future tasks. Retaining raw state, caching compilations, or materializing a wider state are not afterthoughts; they are different allocations of computation and memory across time.

## 13. Conclusion

P11 establishes a controlled theory/systems result about computational placement. Fixed linear-accessible state must scale with query-family rank; task-conditioned construction can expose a much smaller task-facing state; dense-decoder experiments show large sample gains; a hostile sparse decoder buys part of the gain back but leaves a reproducible 2×/4× residual; and a frozen nonlinear tree ensemble does not close the high-dimensional gap under its registered budget. Exact workload laws quantify the future-query cost of specialization.

The resulting principle is deliberately stronger than “representation matters” and more precise than “compression helps”:

> **State construction, decoder search, and future recoverability are coupled resource choices. Moving structure into state can reduce downstream discovery work, but the benefit shrinks as the downstream access mechanism becomes better at discovering that structure, and the specialization creates option debt unless recoverability is retained.**

## References

1. Y. Xu, S. Zhao, J. Song, R. Stewart, and S. Ermon. *A Theory of Usable Information Under Computational Constraints.* ICLR, 2020. arXiv:2002.10689.
2. A. Wong, A. Plaat, T. Bäck, N. van Stein, and A. V. Kononova. *State Design Matters: How Representations Shape Dynamic Reasoning in Large Language Models.* Transactions on Machine Learning Research, 2026. arXiv:2602.15858.
3. H. Wang, Y. Li, L. Zhang, P. Li, X. Che, X. Zhang, and Z. Yang. *QUMem: Personalized Memory for Query-Conditioned User-State Inference in LLM Agents.* arXiv:2608.16168, 2026.
4. M. Kang, W.-N. Chen, D. Han, H. A. Inan, L. Wutschitz, Y. Chen, R. Sim, and S. Rajmohan. *ACON: Optimizing Context Compression for Long-horizon LLM Agents.* ICML, 2026. arXiv:2510.00615.
5. N. D. Jones, C. K. Gomard, and P. Sestoft. *Partial Evaluation and Automatic Program Generation.* Prentice Hall, 1993.
6. A. Darwiche and P. Marquis. *A Knowledge Compilation Map.* Journal of Artificial Intelligence Research 17, 229–264, 2002.

## Claim boundary

This manuscript supports a controlled theory/systems superiority result over the registered dense, sparse and nonlinear decoder baselines. It does not claim a universal nonlinear lower bound, a transformer scaling law, free preprocessing, or real-agent superiority. Those stronger claims remain prospective and must be earned under matched end-to-end resource accounting.

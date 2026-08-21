# State as Computation: Query-Conditioned Compilation Trades Representation Rank, Accessibility Work, and Future Optionality

**ORION-P11 · issue #471 · accounting track #664 · optionality track #667**  
**Evidence freeze:** 2026-08-21  
**Submission status:** peer-review package; controlled/theory claim complete, real-system generalization explicitly open

## Abstract

Most learning and reasoning systems treat the state presented to a downstream model as a fixed input. We study a different computational regime: **constructing task-specific state is itself an inference action**. A query-conditioned compiler can spend work upstream to expose only the structure needed by the current query, while a query-agnostic representation must preserve accessibility across an entire query family. We formalize this distinction for bounded readout families and prove that any fixed representation supporting exact linear readout of a query family must have dimension at least the rank of that family. For all size-`s` parity queries over `d` Boolean variables this requires `binom(d,s)` linearly accessible coordinates, whereas direct query-conditioned compilation needs one active coordinate. Frozen controlled experiments show universal/compiled representation ratios of **91×–1820×** and dense-decoder sample-threshold improvements from **4× to more than 32×**. A separate no-answer-laundering construction leaves the final decision to the same downstream learner and produces 0.95-accuracy threshold improvements of at least 32× in the hardest dense-decoder cells. We then subject the result to a preregistered sparse-decoder attack. Sparse universal decoding substantially closes the gap but does not erase it: compiled state reaches 0.95 accuracy at `n=64`, versus `n=128` and `n=256` for the universal sparse decoder, while leading by **+0.2903** and **+0.3840** accuracy at `n=64`. The attack therefore fails its deliberately stronger ≥4×-in-both-cells gate and is retained as a negative result. Together with exact optionality laws for compile/cache/recover/materialize policies, the evidence supports a stronger mechanistic conclusion: **state compilation acts as an externalized structural prior that moves search and feature-selection work across the system boundary; its advantage is largest when downstream access is weak, remains measurable under explicit sparse selection, and trades current accessibility against future-query optionality.** We do not claim a universal nonlinear lower bound or real-system superiority; those are separated as prospective attacks.

## 1. Introduction

A system can possess the information needed for a task while making that information expensive for a bounded learner to use. This distinction motivates predictive usable-information measures, representation learning, feature acquisition, knowledge compilation, partial evaluation, context selection, retrieval, memory compression and state abstraction. Recent work also shows directly that state design can change LLM reasoning behavior while model parameters are held fixed. Those observations make a weak claim such as “representation matters” scientifically uninteresting.

The missing systems question is quantitative and architectural: **where should the computation needed to make information usable occur?** If a downstream reasoner is forced to discover a small relevant structure inside a universal state, the required work appears as samples, model capacity, search, verifier calls or latency. If a compiler exposes that structure beforehand, the same work has not disappeared; it has moved upstream. That movement can reduce the state and downstream burden, but may also destroy or defer future-query optionality.

We call this view *state as computation*. The system is factored as

`raw evidence R + query q -> compiler C(R,q) -> task-specific state Z_q -> downstream reasoner D -> verified output`.

The paper makes four contributions.

1. **A rank/accessibility law.** For a fixed linear readout family, supporting an `r`-dimensional query span requires at least `r` accessible representation coordinates. For size-`s` parity families this becomes the combinatorial lower bound `binom(d,s)`.
2. **Frozen finite-sample evidence.** In controlled parity-query families, query-conditioned compilation gives 91×–1820× representation savings and large sample-threshold improvements under the registered dense decoder.
3. **A hostile sparse-decoder result.** A preregistered L1 universal-state decoder recovers much of the hidden support and shrinks the threshold gap to 2× and 4×. This negative result rules out an overbroad interpretation while showing that compilation retains a measurable low-sample advantage even when the downstream learner explicitly searches for sparse support.
4. **An optionality phase account.** Exact workload equations distinguish minimal current state from retained raw recoverability, demand-driven caching and universal materialization.

The central claim is deliberately architectural rather than model-specific: **state construction can substitute for downstream structural search, and the useful comparison is a resource frontier over compiler work, accessible state, downstream burden and future option debt.**

## 2. Relation to prior work and novelty boundary

### 2.1 Computationally usable information

Predictive V-information formalizes information relative to a restricted predictive family and establishes that computation can change usable information. P11 therefore does not claim that information-theoretic sufficiency implies computational accessibility, nor that computation can make information easier to use. Our residual is operational: identify *where* the accessibility work is paid and measure its substitution against state dimension, downstream sample/search burden and future recoverability.

### 2.2 State design, retrieval and query-conditioned memory

State-design studies show that representation structure changes dynamic reasoning. Query-conditioned memory systems such as QUMem infer or retrieve state conditional on the current request. Long-horizon context-compression methods likewise optimize which history is retained. These works remove novelty from “condition state on the query” and “compression helps.” P11 instead asks how query-family rank, compiler cost and future-query optionality jointly constrain the architecture.

### 2.3 Knowledge compilation and partial evaluation

Partial evaluation, materialized views, knowledge compilation and multi-query optimization all move work upstream and trade compilation cost against future reuse. P11 does not relabel those primitives. The new scientific object is the **inference-system resource receipt**: compiler/preprocessing work, output state, downstream access burden, cache/recovery cost and future workload are evaluated together rather than treating preprocessing as free.

### 2.4 What remains novel after donor subtraction

The strongest residual supported here is:

> For bounded downstream access, query-conditioned state construction can externalize structural search from the reasoner. In controlled query families this creates exact representation-rank savings and large finite-sample gains; a sparse universal decoder partially substitutes for the compiler, demonstrating that the empirical gap is a resource-placement effect rather than an intrinsic information gap. The same compilation decision induces calculable future-query option debt unless raw or universal state is retained.

This formulation is stronger than a generic representation claim because it predicts both the positive and the hostile sparse-decoder result.

## 3. Formal setup

Let `(X,mu)` be a probability space and `F={f_1,...,f_N}` a finite query family in `L2(mu)`. A fixed query-agnostic representation is `phi:X->R^m`. It supports exact linear query answering if, for every `q`, there exists `w_q` such that

`f_q(x)=<w_q,phi(x)>`

almost surely.

A query-conditioned compiler receives `(x,q)` and constructs `C(x,q)` before the downstream learner acts. Compiler work is explicitly charged; the comparison is never “free preprocessing versus paid reasoning.”

### Theorem 1 — query-family rank lower bound

Let `r=dim(span(F))`. Every fixed representation supporting exact linear readout of every query in `F` has `m>=r`.

**Proof.** Every `f_q` must lie in the span of the `m` coordinate functions of `phi`. That coordinate-function span has dimension at most `m` and contains the `r`-dimensional span of `F`. Hence `m>=r`. ∎

The theorem is elementary linear algebra; novelty is not claimed for the proof itself. Its role is to expose the architectural quantity that a fixed accessible state must materialize.

### Corollary 1 — parity query family

For `X={-1,+1}^d` under the uniform measure and all size-`s` subsets `S`, define

`f_S(x)=prod_{i in S} x_i`.

Distinct parity characters are orthogonal. A fixed exact linear representation supporting all size-`s` queries therefore requires at least `binom(d,s)` coordinates. A direct query-conditioned compiler can emit the requested parity in one coordinate.

This is a representation-accessibility gap, not a total-time lower bound. The direct one-coordinate construction is intentionally strong and motivates the no-answer-laundering experiment below.

### Approximate frontier

For orthonormal `f_1,...,f_N` and an `m`-dimensional linearly accessible subspace `U`, Bessel's inequality yields

`(1/N) sum_q ||f_q-P_U f_q||_2^2 >= 1-m/N`.

Thus reducing accessible rank forces average approximation error for a fixed linear-accessible state, while a query-conditioned architecture can pay computation to change the state per query.

## 4. Controlled experiment I: query-conditioned compilation

The first frozen experiment compares raw coordinates, a universal bank containing every size-`s` parity feature, and a one-coordinate query-conditioned state. The downstream learner is fixed across representation arms.

| `d` | `s` | universal dimensions | compiled dimensions | dimension ratio | compiled `n@0.90` | universal `n@0.90` |
|---:|---:|---:|---:|---:|---:|---:|
| 14 | 2 | 91 | 1 | 91× | 32 | 128 |
| 16 | 4 | 1820 | 1 | 1820× | 32 | NOT_REACHED@1024 |
| 18 | 3 | 816 | 1 | 816× | 32 | 1024 |
| 20 | 3 | 1140 | 1 | 1140× | 32 | 1024 |

At `n=1024`, raw/universal/compiled accuracies were respectively:

- `(14,2)`: `0.49685 / 1.00000 / 1.00000`;
- `(16,4)`: `0.49903 / 0.84550 / 1.00000`;
- `(18,3)`: `0.50136 / 0.99152 / 1.00000`;
- `(20,3)`: `0.50113 / 0.94685 / 1.00000`.

The frozen terminal was `P11_QUERY_CONDITIONED_COMPILATION_GAP_SUPPORTED`. Canonical fresh-process replays were byte-identical. These cells demonstrate a finite-sample nuisance/search burden: the universal bank contains the decisive coordinate, but a bounded learner must identify it among many irrelevant coordinates.

## 5. Controlled experiment II: no-answer laundering

A compiler that emits `f_q(x)` can be accused of returning the answer. P11B therefore constructs each target as the majority of `r` active parity components and exposes those components rather than the final label. The same downstream logistic learner must still learn the final decision. Every compiled component is checked against the signed label and its negation.

| `d` | `s` | `r` | universal dims | compiled dims | universal `n@0.95` | compiled `n@0.95` |
|---:|---:|---:|---:|---:|---:|---:|
| 15 | 3 | 5 | 455 | 5 | 2048 | 64 |
| 17 | 3 | 5 | 680 | 5 | 2048 | 64 |
| 17 | 4 | 5 | 2380 | 5 | NOT_REACHED@2048 | 64 |
| 19 | 3 | 7 | 969 | 7 | NOT_REACHED@2048 | 64 |

At `n=2048`, raw/universal/compiled accuracies were `0.50493/0.99716/1.0`, `0.50205/0.96549/1.0`, `0.49985/0.76221/1.0`, and `0.50024/0.87140/1.0`. No selected component equaled or negated the protected label. The terminal was `P11B_QUERY_COMPONENT_COMPILATION_SUPPORTED`, with byte-identical canonical replays.

The strongest dense-decoder interpretation is therefore not “the compiler knows the answer.” It is that the compiler exposes a small relevant subspace in which the downstream decision becomes sample-accessible.

## 6. Hostile experiment: sparse universal decoder

The most direct alternative explanation is that the dense universal learner is simply bad at discovering sparse support. P11D was preregistered after P11/P11B and uses a fresh seed, two high-dimensional no-answer-laundering cells, a fixed L1 logistic universal-state decoder (`C=0.1`, `liblinear`) and the same compiled L2 learner. Its positive gate deliberately required the universal sparse decoder to need at least 4× as many samples as compiled state in **both** cells.

The gate failed.

| cell `(d,s,r)` | universal dims | compiled dims | compiled `n@0.95` | sparse universal `n@0.95` | threshold ratio | compiled − sparse at `n=64` |
|---|---:|---:|---:|---:|---:|---:|
| `(17,4,5)` | 2380 | 5 | 64 | 128 | 2× | +0.2903 |
| `(19,3,7)` | 969 | 7 | 64 | 256 | 4× | +0.3840 |

Zero answer-laundering failures occurred. The registered terminal is permanently `P11D_SPARSE_DECODER_GAP_NOT_MET` because the first cell achieved only 2× rather than the required ≥4×.

### 6.1 Mechanistic interpretation of the negative

The negative is more informative than a weaker positive would have been. L1 regularization explicitly searches for a small support inside the universal bank; it therefore performs some of the structural-selection work that query-conditioned compilation performs upstream. The reduced 2×–4× threshold gap is exactly what the state-as-computation hypothesis predicts when downstream access becomes stronger.

Compilation nevertheless retains two measurable advantages in these protected cells: it reaches the target at the first registered sample size in both cells, and it leads sparse universal decoding by 0.29–0.38 absolute accuracy at `n=64`. The scientific claim is thus **substitution**, not unconditional dominance: compiler work and downstream structural search can buy back one another.

### 6.2 Reproducibility disposition

Two P11D executions reproduced the scientific summary exactly but not the full JSON hash. The sparse liblinear arm did not receive an explicit solver `random_state`, so non-headline curve values may vary. This replay failure is recorded and does not alter the negative terminal. A future independent sparse-decoder replication must freeze an explicit solver seed before protected outcomes.

### 6.3 Stronger nonlinear attack remains open

P11C preregistered a larger attack including L2, L1 and a 256-tree ExtraTrees universal-state decoder. The exact protected runner exceeded the available execution window before emitting any terminal. A no-outcome amendment vectorized only parity-bank evaluation, but the full tree experiment still did not produce an authoritative result in the present run. P11C is therefore `CANNOT_CHECK`, not positive or negative.

## 7. Future optionality: compile, cache, recover or materialize

Current accessibility and future usefulness are separate coordinates. Let a universal query family contain `N` independent components and let a compiled state retain `r`.

If raw state is discarded, one-step future-query coverage under uniform demand is exactly

`r/N`.

If `K` independent size-`r` compilations are cached, expected coverage is

`1-(1-r/N)^K`.

For one-component uniform requests, expected distinct requested components after `K` requests are

`N[1-(1-1/N)^K]`.

These identities yield four policy regimes:

- **compile only:** minimal current state, maximal option debt if raw evidence is lost;
- **compile + cache:** state grows with encountered demand;
- **retain raw + compile:** complete recoverability with miss-time recompilation cost;
- **universal materialization:** complete immediate coverage with larger memory and upfront work.

A frozen deterministic workload study found the first registered uniform-demand horizons where bulk universal materialization becomes cheaper than demand-driven cache compilation at approximately `0.5N`, `1.0N`, and `2.0N` for batch-efficiency coefficients `0.25`, `0.50`, and `0.75`. Concentrated workloads postpone universal materialization: at `N=2048` and `K=N`, the expected distinct-demand fraction is `0.63221` under uniform demand, `0.25735` under Zipf 1.1 and `0.09506` under Zipf 1.5.

The equations are exact for the frozen workload model; they are not universal memory laws.

## 8. Resource accounting

Compilation is not free. Each comparison belongs on a vector resource receipt containing at least:

- compiler/preprocessing operations, latency and model identity;
- state size, bytes/tokens and memory traffic;
- downstream model identity/capacity;
- generated tokens/recurrent steps;
- search nodes, verifier calls and tool calls;
- cache memory and reuse count;
- raw recovery/reconstruction/recompilation cost;
- end-to-end latency and reproducible energy where available.

Learned-compiler training is reported separately and amortized only under a prospectively declared reuse horizon. Unless a legitimate application-specific exchange rate is frozen, results are compared as Pareto surfaces rather than by post-hoc scalarization.

## 9. What the combined evidence establishes

The experiments support a three-part mechanism.

**First, family-wide accessibility can be combinatorially expensive.** The rank theorem and parity corollary identify an exact burden for fixed linear-accessible state.

**Second, compilation can move structural discovery upstream.** Dense universal-state learners pay a large finite-sample cost; explicit query-conditioned state removes that search burden without laundering the final answer.

**Third, stronger downstream access buys the burden back.** Sparse selection materially closes the gap, converting an apparent >32× dense-decoder advantage into 2×–4× in the hostile cells. This makes the claim more general, not less: state and decoder structure are substitutable computational resources.

The resulting systems principle is:

> **Do not ask only whether information is present. Ask where the work required to make the relevant structure accessible is paid, and whether that upstream work is worth the optionality it consumes.**

## 10. Statistical and reproducibility notes

The theorem and optionality identities are exact. The controlled learner experiments report frozen grid outcomes rather than invented parametric confidence intervals. Thresholds are first registered sample sizes reaching the target; `NOT_REACHED` is not extrapolated.

All future broader evaluations should hold out complete query/task families, use paired items within family, report family/domain-block uncertainty, preserve every prespecified cell and retain harmful/null compilation regimes. Hyperparameters and policies must be selected on development families only.

P11 and P11B have deterministic canonical replay receipts. P11D intentionally records both its scientific negative and its non-byte-identical replay. P11C has no authoritative outcome.

## 11. Limitations and strongest remaining attacks

1. The exact rank theorem applies to a restricted linear-accessible family, not arbitrary nonlinear decoders.
2. P11D shows that sparse decoder bias can substantially reduce the finite-sample gap; P11C's tree attack remains unresolved.
3. The current compiler is controlled/oracle-like rather than a learned query-to-state policy.
4. Full compiler work and learned-compiler training cost are not yet measured on a real end-to-end system.
5. No transformer, theorem-prover or long-horizon agent replication is claimed here.
6. Optionality results use explicit synthetic workload models and should be validated under shifted real query distributions.
7. Universal materialization may dominate when future demand is broad and compilation amortizes well; the paper predicts such regimes rather than claiming compilation always wins.

## 12. Conclusion

State is not merely storage. Under bounded access, constructing state is a place to spend computation. P11 proves an exact accessible-rank burden for fixed linear state, demonstrates large controlled savings from query-conditioned compilation, survives a no-answer-laundering attack, and then deliberately exposes the boundary of the effect with a sparse-decoder negative. The surviving conclusion is stronger than unconditional superiority: **query-conditioned compilation externalizes structural search.** When downstream learners lack the right inductive bias, that externalization produces very large sample savings; when the learner can perform sparse support recovery, the gap shrinks but remains measurable. Whether the trade is worthwhile depends jointly on compiler cost, downstream access and future-query optionality.

## References

- Xu, Y., Zhao, S., Song, J., Stewart, R., & Ermon, S. *A Theory of Usable Information under Computational Constraints.* ICLR 2020. arXiv:2002.10689.
- Wong, A., Plaat, A., Bäck, T., van Stein, N., & Kononova, A. V. *State Design Matters: How Representations Shape Dynamic Reasoning in Large Language Models.* Transactions on Machine Learning Research, 2026. arXiv:2602.15858.
- Wang, H. et al. *QUMem: Personalized Memory for Query-Conditioned User-State Inference in LLM Agents.* arXiv:2608.16168, 2026.
- Kang, M. et al. *ACON: Optimizing Context Compression for Long-horizon LLM Agents.* ICML 2026; arXiv:2510.00615.
- Classical partial evaluation, knowledge compilation, materialized-view and multi-query optimization literature is donor-owned background for moving work upstream; the final typeset bibliography should use canonical field references rather than treating these primitives as P11 novelty.

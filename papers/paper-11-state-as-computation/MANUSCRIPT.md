# State as Computation: Moving Structural Search between Representation Construction and Downstream Reasoning

**ORION P11 — peer-review manuscript**  
**Issues:** #471, #664, #667  
**Evidence cut:** 21 August 2026

## Abstract

Reasoning systems are commonly compared as if the state presented to the downstream learner were a fixed observation. We study a different resource boundary: **constructing task-relevant state is itself computation**, and this computation can substitute for structural search performed downstream. For a query family `F`, any fixed representation supporting exact linear readout of every query requires dimension at least `rank(F)`. For all size-`s` parity queries on `d` Boolean variables this becomes `binom(d,s)` accessible coordinates, whereas a query-conditioned construction needs only the coordinates selected by the current query. Frozen controlled studies produce universal/compiled representation ratios of 91×–1820× and dense-decoder sample-threshold reductions from 4× to more than 32×. A no-answer-laundering construction exposes 5–7 latent components rather than the final label and retains large gains. We then attack the mechanism. A preregistered sparse universal decoder **falsifies** the stronger claim that compilation retains at least a 4× threshold advantage in both hostile cells, recovering part of the search burden and leaving 2× and 4× residual gaps. A fresh deterministically seeded replication reproduces those 2×/4× gaps with +0.291/+0.331 accuracy advantages at `n=64`. An initial nonlinear successor is retained as non-authoritative after review found a protocol mismatch. A separately frozen deterministic single-thread ExtraTrees successor puts replay in the terminal decision path and again fails to reach 0.95 accuracy through `n=1024` in either universal-state cell, while compiled state reaches the target by `n=64`; low-sample gaps are +0.462 and +0.394. That successor's terminal is a function of which registered universal arm sits in its gate — the sparse arm reaches the target at `n=128` in the first cell on the successor's own data — so it is evidence about the decoder it names and not about universal-state decoding, and holding the decoder fixed attributes 86.7% and 55.4% of those two gaps to the change of state rather than the change of decoder family. A further successor pools all three registered universal arms inside its own gate, carries the earlier thresholds over unedited, and draws its protected regimes from a frozen ladder of state widths after publishing that its gates were reachable in both directions; it returns a **negative** where the compiled state is narrow, locating the advantage in the width of the compiled state rather than in the size of the universal representation. Finally, exact workload laws quantify the option debt created when specialized state is retained without raw recoverability. The result is not that compilation universally dominates inference. It is that **state construction determines where structural-search computation is paid**, and this placement can be measured jointly through accessible rank, downstream burden, construction cost, and future optionality.

## 1. Introduction

A system can possess all information required for a task and still make that information expensive for a bounded learner or reasoner to use. Computationally usable information formalizes one version of this observation. Partial evaluation and knowledge compilation move work upstream. Materialized views trade preprocessing and storage for later query cost. Current agent systems retrieve, compress, summarize, or restructure context before generation. Recent LLM evidence also shows that state design itself can materially change dynamic reasoning while model parameters remain fixed.

Those results make several weak novelty claims untenable. P11 does **not** claim that representation matters, that computation can create usable information, that query-conditioned memory is new, or that compression can reduce downstream cost. The unresolved systems question is instead a resource-placement question:

> **When task-relevant structure can be discovered either while constructing state or later by a decoder/search process, where is the computation paid, how much downstream burden can be removed, and what future optionality is lost by specialization?**

We call this view *state as computation*. A compiler `C(R,q)` receives raw state `R` and the current query `q`, constructs a task-facing state, and hands it to a bounded downstream access mechanism. Compilation is never free: compiler operations, state bytes, training cost, cache/recovery cost, downstream samples or search, verifier/tool calls, latency and—where reproducibly measurable—energy belong to one resource receipt.

The paper makes four contributions.

1. **Accessible-rank theory.** For a fixed linear-access class, query-family rank gives an exact lower bound on the dimension required to support every query. This separates information presence from accessibility under a declared decoder family.
2. **Controlled compilation gaps.** Frozen parity-query studies show large accessible-dimension and sample-threshold differences, including a construction that prevents the compiler from outputting the final answer.
3. **Hostile decoder substitution.** A sparse universal decoder recovers part of the compilation advantage and falsifies an intentionally stronger gate. A fresh deterministic replication retains a smaller 2×/4× residual. A separately frozen, replay-gated deterministic tree ensemble retains a larger low-sample residual against the arm it names. These attacks identify decoder inductive bias as a substitute for upstream compilation rather than an inconvenient alternative explanation — and each one's verdict is scoped to its own arm, which §5.4.1 measures rather than assumes.
4. **Future-optionality law.** Exact workload equations show when specialization creates future-query debt and when caching, raw recovery, or universal materialization becomes preferable.

The strongest conclusion is mechanistic rather than universal: **representation construction and downstream access are two loci at which structural-search work can be paid**.

## 2. Donor boundary and novelty residual

### 2.1 Prior-owned primitives

Predictive `V`-information already establishes that computational constraints change what information is usable and that computation can transform unusable information into usable information. Classical partial evaluation specializes programs to known inputs. Knowledge compilation and database materialization move computation upstream for later reuse. Feature selection and sparse models search for relevant coordinates inside a larger representation. Query-conditioned memory and retrieval systems condition state on the current task. Long-horizon context-compression systems explicitly optimize memory/performance trade-offs. Wong et al. provide direct current evidence that state representation and the act of construction can change LLM reasoning.

P11 therefore subtracts all of those primitives from its novelty claim.

### 2.2 Residual contribution

The residual is a **joint placement account**:

`raw state -> construction work -> task-facing state -> decoder/search work -> verified outcome`

with a future horizon:

`task-facing state + raw/cache policy -> future query service or option debt`.

The paper asks how accessible rank, downstream sample/search burden, upstream construction, cache/recovery and future-query coverage move together when the same underlying information is exposed differently.

## 3. Formal setup

Let `X` be a domain with distribution `mu`, and let `F={f_1,...,f_N}` be query functions in `L2(mu)`. A fixed query-agnostic representation is `phi:X->R^m`. It supports exact linear query answering when, for every `q`, some `w_q` satisfies

`f_q(x) = <w_q, phi(x)>`

almost surely.

A query-conditioned compiler instead sees `(x,q)` and emits `C(x,q)` before a downstream mechanism acts. The comparison is meaningful only under an explicit access class and resource boundary.

### 3.1 Theorem 1 — query-family accessible-rank bound

If `span(F)` has dimension `r`, every fixed representation supporting exact linear readout of all queries has `m >= r`.

**Proof.** Every `f_q` lies in the span of the `m` coordinate functions of `phi`. That span has dimension at most `m` and must contain the `r`-dimensional span of `F`; hence `m>=r`. □

The theorem is elementary linear algebra. The contribution is its role as a systems resource boundary, not mathematical novelty.

### 3.2 Approximate orthonormal frontier

For orthonormal `f_1,...,f_N` and any `m`-dimensional linearly accessible subspace `U`, Bessel's inequality gives

`(1/N) sum_q ||f_q - P_U f_q||_2^2 >= 1 - m/N`.

This is an access-class statement. It is not a lower bound on an unrestricted nonlinear decoder.

### 3.3 Parity corollary

For `X={-1,+1}^d` under the uniform measure and all size-`s` subsets `S`, define

`f_S(x)=product_{i in S} x_i`.

Distinct parity characters are orthogonal. A fixed exact linear-accessible representation supporting all size-`s` queries therefore requires at least `binom(d,s)` coordinates. A query-conditioned construction need expose only the selected query structure. This establishes an exact **accessible-representation** gap, not a total-time lower bound.

## 4. Dense controlled studies

### 4.1 P11 confirmatory study

The confirmatory experiment compares raw linear input, a fixed universal parity bank, and query-conditioned compiled state over a frozen train-size grid.

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

The central alternative explanation is direct: perhaps the universal representation is penalized only because the downstream decoder has the wrong inductive bias. If so, stronger decoder-side search should buy back the compilation advantage. P11 treats that prediction as a mechanism test.

### 5.1 P11D sparse decoder — permanent negative

P11D preregistered a strong hostile gate: an L1 sparse universal decoder should still leave at least a 4× sample-threshold advantage for compiled state in **both** high-dimensional cells. It did not.

| cell `(d,s,r)` | universal dims | compiled dims | sparse universal `n` at 0.95 | compiled `n` at 0.95 | ratio | compiled - sparse at `n=64` |
|---|---:|---:|---:|---:|---:|---:|
| (17,4,5) | 2380 | 5 | 128 | 64 | 2× | +0.2903 |
| (19,3,7) | 969 | 7 | 256 | 64 | 4× | +0.3840 |

The preregistered terminal is `P11D_SPARSE_DECODER_GAP_NOT_MET` and remains permanently negative. This result matters scientifically: sparse decoder-side feature discovery is a **substitute** for upstream state construction.

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

### 5.3 P11C and P11F — non-authoritative nonlinear history

The original P11C ExtraTrees attack exceeded the available execution window on its first attempt and emitted no terminal. `P11C_REPRODUCIBILITY_AMENDMENT_V1_1.md` replaced only the parity-bank evaluation with an elementwise-identical vectorization, and `P11C_EXECUTION_RECEIPT_V1.md` records the frozen protocol subsequently executed to completion, twice, in fresh processes, at terminal `P11C_STRONGER_DECODER_GAP_SUPPORTED` with canonical SHA-256 `f65c1c5bb9cb96194fbcb20c9dbfd3a949127f9789e95cf6585d891bf939c454`. Its gate 3 — the only gate in the programme read through the pooled *best hostile universal threshold* rather than through one arm — passes at exactly the boundary, 256 against a compiled 64 in both cells, and that receipt reports the sweep showing the boundary value comes up in 11 of 20 draws of the same construction. P11C therefore settles nothing about the ≥4× claim P11D retired, and it is not used as claim authority; what it does establish is that its combination rule was applied, to its own frozen data, inside its own protocol.

P11F then froze a tractable 96-tree successor and produced a positive numerical separation, but hostile PR review found a protocol-conformance defect: the runner set `n_jobs=-1` although the written protocol specified the registered configuration with otherwise sklearn defaults. Parallel execution did not change the two observed bytes in that run, but exact protocol conformance is a prerequisite for claim authority. P11F is therefore retained as diagnostic history and is **not** used as the primary nonlinear result.

### 5.4 P11G — replay-gated deterministic nonlinear successor

P11G was frozen after the P11F review finding on a fresh seed (`2026082120`). It retains the 96-tree ExtraTrees resource envelope but explicitly sets `n_jobs=1`, pins every estimator random state, and makes replay part of the terminal itself: the authoritative executable launches two fresh Python subprocesses, re-runs the complete scientific pipeline twice, compares the canonical scientific bytes, and refuses a positive terminal unless both executions match and all scientific gates pass.

| cell | deterministic tree universal `n` at 0.95 | compiled `n` at 0.95 | tree accuracy at `n=1024` | compiled - tree at `n=64` |
|---|---:|---:|---:|---:|
| (17,4,5) | `NOT_REACHED` | 64 | 0.8248 | +0.4624 |
| (19,3,7) | `NOT_REACHED` | 64 | 0.7828 | +0.3942 |

The terminal is `P11G_DETERMINISTIC_TREE_DECODER_GAP_SUPPORTED`. Both fresh-subprocess scientific payloads have SHA-256

`a2b0c33ce3c39e54ca1aa400a2b7d52d019fc4503f6cd5eb726c7b8bbe79a7cc`.

This is still not a nonlinear lower bound. It is a hostile finite-system result showing that one deterministic nonlinear universal-state decoder continues to pay substantial discovery cost under the registered resource envelope.

#### 5.4.1 The terminal is a function of which registered arm sits in the gate

P11G registers one universal-state arm. The programme registered three — `UNIVERSAL_L2`, `UNIVERSAL_L1` and `UNIVERSAL_EXTRA_TREES`, frozen together in P11C — and P11G's receipt publishes curves for one of them. Replaying P11G's own frozen data stream with only the decoder swapped, and reading P11G's own four scientific gates on each arm:

| universal arm | 0.95 threshold per cell, censored at 256 | terminal P11G's own gates print |
|---|---|---|
| `UNIVERSAL_L2` | ≥256, ≥256 | `..._GAP_SUPPORTED` |
| `UNIVERSAL_L1` | **128**, ≥256 | `..._GAP_NOT_MET` |
| `UNIVERSAL_EXTRA_TREES` (reported) | ≥256, ≥256 | `..._GAP_SUPPORTED` |

Two of the three comparable pairs change the verdict, so the `decoder_arm` axis is not inert. The flip is entirely gate 3: `UNIVERSAL_L1` reaches the target at `n=128` in cell (17,4,5), and 128 is not ≥256. Its `n=64` gaps, +0.3252 and +0.3258, clear P11G's ≥0.20 gate comfortably.

None of this is a new measurement. It is the same sparse threshold P11D reports as a permanent negative and P11E replicates on a fresh seed, and P11C's receipt sweeps it across twenty seeds of the same construction, where cell (17,4,5) reads 128 in nine and 256 in eleven. What is new is the conjunction: the arm whose 128 the paper reports as its own negative would, placed in P11G's gate, print `P11G_DETERMINISTIC_TREE_DECODER_GAP_NOT_MET` on P11G's own bytes. `NOT_REACHED` through `n=1024` is therefore not a stronger reading than the L1 arm's 128 — an arm that reaches nothing anywhere gives the same gate reading in every world.

P11G's terminal is retained exactly as frozen and is evidence about the decoder its own claim-authority sentence names. It is not evidence about universal-state decoding, and the claim ledger's row is scoped accordingly. `P11G_ARM_PLACEMENT_ADJUDICATION_V1.md` carries the adjudication, including the finding — read off the two freezes — that P11C's pooled combination rule governs P11C and does not bind P11G: it feeds a ≥4× ratio gate rather than an absolute ≥256 one, on a ladder of five queries per cell to `n=2048` on 8,192 test points rather than three to `n=1024` on 4,096, over a pool whose tree arm is 256 estimators rather than 96, for a claim about a family of attacks rather than about one decoder.

#### 5.4.2 How much of the published gap is the change of state, and how much the change of decoder

P11G moves the representation and the learner at once: L2 logistic regression on `r` compiled columns against a 96-tree ExtraTrees ensemble on the complete bank. Holding the decoder at ExtraTrees and moving only the representation separates them.

| cell | published gap at `n=64` | decoder-family half | state half | state share |
|---|---:|---:|---:|---:|
| (17,4,5) | +0.4624 | +0.0614 | +0.4010 | 86.7% |
| (19,3,7) | +0.3942 | +0.1757 | +0.2185 | 55.4% |

This is reported in both directions because it cuts both ways. It **narrows the terminal**: +0.4624 and +0.3942 are not wholly the compilation advantage, and 13.3% and 44.6% of them are the change of decoder family. It **supports the placement claim**: with the decoder held fixed, the state half is the majority in both cells and 86.7% in the first, so query-conditioned construction is doing most of the work in the published comparison — and being measured at a fixed decoder, that half is unaffected by which universal arm is placed in the gate.

### 5.5 P11H — the pooled successor, and where the advantage stops

§5.4.1 shows P11G's terminal names one arm. The deeper defect, found by `orion.study.p11.attack_audit`, is that all four of P11G's scientific gates hold in **every world its own freeze admits**, so `all(gates.values())` was `True` before its seed was drawn and its survival was arithmetic rather than measured. P11H re-asks the question under a protocol whose attack can win. Nothing of P11G is edited: its protocol, seed, gates, receipt, terminal and its payload digest `a2b0c33c…79a7cc` are all retained.

P11H registers all three universal-state arms and freezes the best-of-arms combination rule **inside its own positive gate**, carries P11G's `0.95` and `0.20` thresholds over **unedited**, and draws two protected regimes by its fresh seed from a frozen 2×3 ladder: state widths `r ∈ {3, 7}` crossed with complete parity banks of 91, 364 and 969 columns. Before execution, `assess_threshold_panel` reported both hypothesis gates `BOTH_OUTCOMES_REACHABLE` — supports `[0.8808, 1.0000]` against the `0.95` bar and `[0.0000, 0.2482]` against the `0.20` bar — and `measure_terminal_reach` reported **two** reachable terminals over the 15 admissible draws, of which 3 clear every gate. That preflight is a committed artifact and it predates the run.

The seed drew `(14,2,3)` and `(19,3,3)`. Every instrument precondition held, the two-subprocess replay was byte-identical, and **both hypothesis gates failed**: `P11H_POOLED_UNIVERSAL_ATTACK_PREVAILED`.

| rung | universal bank | pooled 0.95 threshold | pooled best `< 256` | `delta64` |
|---|---:|---:|---:|---:|
| (14,2,3) | 91 | **128** | 1.0000 | +0.1482 |
| (14,3,3) | 364 | **128** | 1.0000 | +0.0992 |
| (19,3,3) | 969 | **128** | 1.0000 | +0.0506 |
| (14,2,7) | 91 | `>=256` | 0.9129 | +0.2350 |
| (14,3,7) | 364 | `>=256` | 0.8920 | +0.3172 |
| (19,3,7) | 969 | `>=256` | 0.8876 | +0.3175 |

The pooled attack reaches the target by `n=128` at every `r=3` rung and at no `r=7` rung, while the complete universal bank moves from 91 to 969 columns *inside each half* without changing a verdict. **The compilation advantage is governed by the width of the compiled state, not by the size of the universal representation** — which is the paper's own headline ratio, and it is not the operative variable.

Like §5.4.2 this cuts both ways, and more sharply. It **bounds the claim**: at `r=3` the advantage is false under P11G's own unedited bars, against a pool containing the paper's own best known attack, so no unconditional form of the survival claim is available. It **strengthens the attribution**: at the drawn regimes the decoder-family half of the `n=64` gap is exactly `+0.0000` — `COMPILED_EXTRA_TREES` and `COMPILED_L2` both reach 1.0000 at `n=64` — so 100% of the gap is the change of state, against 86.7% and 55.4% in P11G's cells. Attribution and magnitude are different questions: what gap exists at `r=3` is wholly a state effect, and it is only `+0.0506`.

Three of the fifteen admissible draws would have printed the positive terminal and the seed did not draw one. The `r=7` rungs carry no terminal and no claim authority; reading them as a positive would be choosing a rung after seeing it, which is what the draw exists to prevent. The `r=5` boundary was excluded before execution for verdict instability across three preflight seeds — in both directions — and remains open.

### 5.6 P11I — wide high-width replication

P11I prospectively freezes the narrower regime P11H located rather than relabeling P11H. It evaluates the complete cross of three fresh execution seeds and three fixed bank-geometry strata at `r=7`, with a matched `r=3` control in every cell. The independent random unit is the execution seed (`n=3`); geometry is a fixed within-seed stratum and five query repeats are technical repeats within each cell. One failed cell still defeats the non-compensatory conjunction.

All nine high-width units pass. Compiled accuracy at `n=64` ranges 0.9690–0.9981; the pooled attack's best accuracy below `n=256` ranges 0.8489–0.9421 against the strict `<0.95` gate; and `delta64` ranges +0.2463–+0.3543 against `>=+0.20`. The same pooled attack reaches 1.0000 in all nine matched `r=3` controls. Two fresh subprocess payloads are byte-identical at SHA-256 `b50ace30…e0ce`.

The terminal `P11I_HIGH_WIDTH_ADVANTAGE_REPLICATED_WIDE_PANEL` licenses a width-conditioned result only: across three independent RNG replicates and three fixed geometry strata, all nine prespecified high-width seed×geometry cells pass. A fresh two-subprocess revalidation under `P11I_REPLICATION_UNIT_AMENDMENT_V1_1.md` reproduces every cell byte-identically while recording `n=3`, not nine. The pooled attack wins in the narrow regime and the compiled-state advantage replicates in the registered high-width regime. `P11_ACTIVE_CLAIM_AUTHORITY_V1.json` content-binds the correction and revalidation receipt; P11D and P11H remain adverse historical results.

## 6. What the decoder attacks identify

The decoder sequence reveals a pattern that a dense-only comparison could not establish.

- Dense universal access pays the largest discovery cost.
- Sparse universal access recovers part of that cost and falsifies an intentionally stronger residual claim.
- Fresh deterministic sparse replication retains a smaller 2×/4× threshold separation.
- A deterministic nonlinear tree ensemble does not close the high-dimensional low-sample gap under its frozen envelope. This is a statement about that arm: on P11G's own data the sparse arm reaches the target at `n=128` in the first cell, which P11G's own gate would read as `NOT_MET` (§5.4.1), and the pattern is arm-by-arm rather than a claim about universal-state decoding as such.
- Pooling every registered universal arm and laddering the width of the compiled state locates where the substitution completes: P11H's pooled attack wins outright at `r=3` and loses at `r=7`; P11I prospectively replicates the high-width side in all nine fresh seed×geometry units with matched live-attack controls (§§5.5–5.6).
- Protocol mismatches are not treated as scientific victories: P11F is demoted and P11G is independently frozen, and a survived attack is not read as evidence until it is shown it could have lost.

This supports the interpretation that **compilation and decoder inductive bias are alternative locations for structural search**. If the downstream mechanism already identifies relevant coordinates cheaply, upstream compilation should matter less. If it does not, state construction can externalize that work.

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

## 9. Methods and reproducibility

The paper's controlled experiments use prospectively frozen seeds, cell grids, train-size grids, thresholds and hostile checks. Thresholds are observed first grid points and are never extrapolated beyond the registered maximum; `NOT_REACHED` is retained literally. The exact theorems and workload equations require no statistical inference.

The evidence history is intentionally append-only in scientific meaning:

1. P11/P11B establish dense and no-answer-laundering controlled gaps.
2. P11D fails its stronger sparse-decoder gate.
3. P11E independently reproduces the surviving sparse residual with deterministic estimator seeds.
4. P11C, after an amendment that vectorized only its parity-bank evaluation, executes to completion twice at `P11C_STRONGER_DECODER_GAP_SUPPORTED`; its pooled ≥4× gate passes at exactly the boundary and the boundary comes up in 11 of 20 draws of the same construction, so it settles nothing and carries no claim authority.
5. P11F produces diagnostic nonlinear evidence but loses authority after a protocol-conformance review finding.
6. P11G is frozen independently and makes two-fresh-subprocess replay a hard terminal gate.

The authoritative P11E payload SHA is `1097d94bef1132d4dfa5d01176a9fcfcfebc46de8113e7cb2e57da1e579a4536`. The authoritative P11G scientific replay SHA is `a2b0c33ce3c39e54ca1aa400a2b7d52d019fc4503f6cd5eb726c7b8bbe79a7cc`.

## 10. Related work

Predictive `V`-information provides the closest information-theoretic parent by making usable information relative to a computational family. Partial evaluation and knowledge compilation provide the closest upstream-computation parents. Materialized views and multi-query optimization provide clear reuse/crossover analogues. Modern query-conditioned memory, retrieval and context-compression systems demonstrate practical task-conditioned state construction. Wong et al. provide direct current evidence that state design changes dynamic LLM reasoning. Sparse estimators and nonlinear ensembles provide natural downstream substitutes by searching over universal features.

P11's residual is not any of those primitives in isolation. It is the experimentally attacked relation between **where structure is exposed, how much discovery work remains downstream, what that exposure costs, and what future options it destroys or preserves**.

## 11. Limitations and falsifiers

1. The exact theorem is restricted to a declared linear-access class; it is not an unrestricted representation or time lower bound.
2. Parity families are deliberately controlled and expose exact rank. They are not evidence that the same numerical separations hold in language-model state.
3. P11D proves that stronger decoder bias can materially reduce the compilation advantage. Any general theory must predict this substitution rather than ignore it.
4. P11G tests one finite nonlinear ensemble under a frozen resource envelope; other nonlinear decoders may behave differently. This is a limitation of the terminal and not only of its generality: two of the three universal arms the programme registered give P11G's gates one verdict and the third gives the other, on P11G's own data (§5.4.1). A claim about universal-state decoding needs a protocol that freezes the pool and gates through it; P11H is that protocol, and it returned a **negative** at `r=3` under P11G's own unedited thresholds (§5.5), so no pooled form of the claim is available and the arm-scoped one is additionally bounded by the width of the compiled state.
5. The current compiler is oracle/query-structured rather than a learned non-oracle compiler.
6. Controlled operation counts do not substitute for end-to-end compiler/model latency, memory traffic, training cost or energy in real systems.
7. Future-query option laws assume the declared workload model. Drift, semantic invalidation and correlated responsibilities require separate modelling.
8. A broad real-system superiority claim requires matched same-information experiments in at least one LLM/procedural setting and one formal/search or long-horizon memory setting.

These are promotion gates, not reasons to weaken the controlled claim already established.

## 12. Discussion

The experiments change the interpretation of task-conditioned state construction. The strongest story is not that a compiler creates information or universally beats a universal representation. The decisive variable is **who performs structural search**.

A query-conditioned compiler performs some search before the downstream learner sees the state. A dense decoder leaves almost all of that burden downstream; a sparse decoder has a mechanism for finding relevant coordinates and therefore reduces the gap; a deterministic finite tree ensemble provides another search mechanism but remains inefficient in the registered high-dimensional low-sample regime. The adverse sparse result is therefore part of the causal evidence: it identifies an axis along which the state advantage should shrink.

This view also connects current accuracy to future flexibility. Aggressive specialization can make one task cheap while destroying immediate support for future tasks. Retaining raw state, caching compilations, or materializing a wider state are not afterthoughts; they are different allocations of computation and memory across time.

The protocol-correction history matters for the same reason. A research programme about computational placement should not treat its own verification work as free or optional. P11F's numerical result is scientifically interesting but does not carry claim authority because the implementation missed a frozen execution detail. P11G shows that the residual survives when the implementation and replay contract are made exact.

## 13. Conclusion

P11 establishes a controlled theory/systems result about computational placement. Fixed linear-accessible state must scale with query-family rank; task-conditioned construction can expose a much smaller task-facing state; dense-decoder experiments show large sample gains; a hostile sparse decoder buys part of the gain back but leaves a reproducible 2×/4× residual; and a replay-gated deterministic nonlinear tree ensemble does not close the high-dimensional gap under its registered budget. Exact workload laws quantify the future-query cost of specialization.

The resulting principle is stronger than “representation matters” and more precise than “compression helps”:

> **State construction, decoder search, and future recoverability are coupled resource choices. Moving structure into state can reduce downstream discovery work, but the benefit shrinks as the downstream access mechanism becomes better at discovering that structure, and specialization creates option debt unless recoverability is retained.**

## Data and code availability

All protocols, runners, result receipts, negative dispositions, correction artifacts and claim ledgers used for the controlled result are versioned in `papers/paper-11-state-as-computation/` and the linked ORION frontier evidence tree. The paper intentionally retains failed and non-authoritative runs alongside authoritative successors.

## References

1. Y. Xu, S. Zhao, J. Song, R. Stewart, and S. Ermon. *A Theory of Usable Information Under Computational Constraints.* ICLR, 2020. arXiv:2002.10689.
2. A. Wong, A. Plaat, T. Bäck, N. van Stein, and A. V. Kononova. *State Design Matters: How Representations Shape Dynamic Reasoning in Large Language Models.* Transactions on Machine Learning Research, 2026. arXiv:2602.15858.
3. H. Wang, Y. Li, L. Zhang, P. Li, X. Che, X. Zhang, and Z. Yang. *QUMem: Personalized Memory for Query-Conditioned User-State Inference in LLM Agents.* arXiv:2608.16168, 2026.
4. M. Kang, W.-N. Chen, D. Han, H. A. Inan, L. Wutschitz, Y. Chen, R. Sim, and S. Rajmohan. *ACON: Optimizing Context Compression for Long-horizon LLM Agents.* ICML, 2026. arXiv:2510.00615.
5. N. D. Jones, C. K. Gomard, and P. Sestoft. *Partial Evaluation and Automatic Program Generation.* Prentice Hall, 1993.
6. A. Darwiche and P. Marquis. *A Knowledge Compilation Map.* Journal of Artificial Intelligence Research 17, 229–264, 2002.

## Claim boundary

This manuscript supports a controlled theory/systems superiority result over the registered dense, sparse and deterministic nonlinear decoder baselines. It does not claim a universal nonlinear lower bound, a transformer scaling law, free preprocessing, or real-agent superiority. Those stronger claims remain prospective and must be earned under matched end-to-end resource accounting.

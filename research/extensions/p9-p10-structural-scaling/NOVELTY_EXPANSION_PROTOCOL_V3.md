# P9/P10 Novelty Expansion Protocol V3

Status: **FROZEN BEFORE V3 OUTCOMES**

Frozen: 2026-08-20

This protocol turns the next novelty layer into explicit experiments. It does not reinterpret prior P9/P10 results and does not convert the already completed relational-accessibility V1.1/V2 experiments into broader claims.

## Expert veto roles

1. **Mathematical theory** — information equivalence, invertibility, complexity claims.
2. **LLM/agent evaluation** — matched model/compute accounting and prompt equivalence.
3. **Formal theorem proving** — native Lean semantics, verifier identity, proof-search fairness.
4. **Hostile reproducibility/novelty** — leakage, post-outcome movement, nearest-work, statistics.

Any role can block a claim rung.

---

# Experiment A — Representation × Relational-Complexity Capacity Frontier

## Question

When the latent decision depends on `k` pairwise bindings, does explicit relational representation reduce the model capacity and sample size needed to recover the decision, even though the flat and relational encodings are bijectively information-equivalent?

## World

For odd `k`, sample independent uniform

`x,c in {-1,+1}^k`

and define

`y = 1[sum_i x_i c_i > 0]`.

Representations:

- `FLAT = concat(x,c)`.
- `RELATIONAL = concat(x,x*c)`.

`RELATIONAL` is bijective with `FLAT` because `c=x*(x*c)`.

## Frozen grid

- `k in {3,5,9,17,33}`.
- `n_train in {64,128,256,512,1024,2048,4096}`.
- protected `n_test=16384` for every `k`.
- fresh train/test seeds are defined in code and must not reuse V1.1/V2 seeds.

## Learners

- `F1_FLAT_LINEAR`: logistic regression on `FLAT`.
- `F2_FLAT_QUADRATIC`: same logistic regression after all degree-2 polynomial interactions of `FLAT`.
- `F3_RELATIONAL_LINEAR`: same logistic regression on `RELATIONAL`.

No hyperparameter tuning. Logistic regression uses `C=1`, `lbfgs`, `max_iter=5000`.

## Primary quantities

For each `k` and learner:

1. accuracy by sample size;
2. minimum frozen `n_train` reaching `0.90` accuracy, otherwise `NOT_REACHED`;
3. feature dimension;
4. excess sample threshold relative to `RELATIONAL_LINEAR`.

## Frozen success terminal

`RELATIONAL_CAPACITY_FRONTIER_SUPPORTED_CONTROLLED_CLASS` requires:

1. at `n_train=4096`, `RELATIONAL_LINEAR >= 0.95` for all five `k`;
2. at `n_train=4096`, `FLAT_LINEAR <= 0.65` for all five `k`;
3. `FLAT_QUADRATIC >= 0.90` for at least four of five `k` at some frozen sample size;
4. whenever both `FLAT_QUADRATIC` and `RELATIONAL_LINEAR` reach `0.90`, the median ratio `n*_flat_quadratic / n*_relational >= 2.0`;
5. exact reconstruction failures are zero;
6. the quadratic feature dimension grows faster than the relational feature dimension over the frozen grid, reported exactly rather than fitted post hoc.

If condition 3 fails, retain the representation result but do not claim a measured sample-complexity substitution against the quadratic learner.

## Claim if positive

> In a controlled family with identical latent information, explicit relation coordinates reduce both the functional interaction order and the observed sample threshold required by a fixed logistic learner; a flat linear learner stays near chance while a quadratic expansion can recover the task only at higher representational and sample cost.

This is a restricted controlled-class result, not an LLM scaling law.

---

# Experiment B — Invertible Nonlinear Obfuscation Ladder

## Question

How does bounded-model accessibility change when exactly the same relation vector is hidden behind increasingly deep **invertible** nonlinear coordinate maps?

## World

Sample uniform `r in {-1,+1}^k`, odd `k`, with target

`y = 1[sum_i r_i > 0]`.

For block length `b`, partition coordinates into consecutive blocks of maximum length `b`. Within each block encode

- first coordinate: `u_1=r_1`;
- subsequent coordinates: `u_j=r_j*r_{j-1}`.

The map is exactly invertible inside each block by recurrence

`r_j=u_j*r_{j-1}`.

The inverse coordinate degree increases with position inside the block. No information is deleted.

## Frozen grid

- `k=65`.
- block lengths `b in {1,2,4,8,16,32,65}`.
- `n_train=8192`.
- `n_test=32768`.
- three fresh replications per block length.

## Learners

- linear logistic regression on the encoded `u` vector;
- degree-2 polynomial logistic regression on `u` for `b in {1,2,4,8}` only, because larger expansions are intentionally outside the cheap controlled execution budget.

No tuning.

## Primary quantities

1. linear accuracy versus block length;
2. degree-2 accuracy where run;
3. exact decode failure count;
4. linear accuracy slope against `log2(b)` as a descriptive statistic only;
5. smallest block length at which mean linear accuracy falls below `0.80`, `0.70`, and `0.60`.

## Frozen success terminal

`INVERTIBLE_OBFUSCATION_ACCESSIBILITY_TAX_SUPPORTED` requires:

1. decode failures zero in every cell;
2. mean linear accuracy at `b=1 >= 0.95`;
3. mean linear accuracy at `b=65 <= 0.70`;
4. mean linear accuracy is non-increasing at at least five of the six adjacent block-length transitions;
5. the mean `b=1` minus `b=65` accuracy gap is at least `0.20`.

No monotonic curve may be manufactured by dropping block lengths.

## Mathematical interpretation

The encoding is bijective, so this experiment changes coordinate accessibility rather than information content. It does not by itself prove a general lower bound for arbitrary model classes. The theorem programme should separately formalize the algebraic-degree growth induced by the recurrence.

---

# Experiment C — Semantic-Orbit Stability

Status: **IMPLEMENTATION CONTRACT; model-runtime dependent for the LLM/Lean versions**.

For each latent item generate semantics-preserving transformations: symbol renaming, order permutations, deterministic serialization variants, and for Lean only transformations whose semantic validity is mechanically checked.

Define orbit inconsistency

`OIR(x)=1-max_y count_T[f(Tx)=y]/|Orbit(x)|`.

Primary comparison: structured versus same-information flat representation under identical model weights. Report accuracy and OIR separately. A lower OIR cannot rescue lower accuracy.

Required success for an LLM claim: positive paired accuracy effect plus lower mean OIR and a domain-block interval excluding zero for the OIR difference.

---

# Experiment D — Structure × Adaptive Compute Allocation

Status: **FROZEN DESIGN; requires an executable multi-budget reasoning model**.

A common total inference budget `B` is distributed across a fixed batch. The allocator observes either same-information flat state or typed structured state but not answer labels. Downstream model and total budget are identical.

Compare:

1. uniform allocation;
2. flat-state learned/frozen allocator;
3. structured-state learned/frozen allocator;
4. oracle difficulty allocation as an unattainable diagnostic ceiling.

Primary endpoint: batch exact-success under equal total generated-token/candidate/verifier budget. Secondary: calibration between predicted difficulty and minimum successful budget.

No adaptive-compute claim can be made from the synthetic logistic experiments.

---

# Experiment E — P10 Proof-Action Abstraction Phase Diagram

Status: **FROZEN DESIGN; native/raw tactic traces required**.

On identical receipt-eligible Lean transitions compare action vocabularies:

- `A0_ATOMIC`: small primitive action decomposition where faithfully defined;
- `A1_RAW_TACTIC`: source/native tactic identity;
- `A2_COARSE_FAMILY`: existing P10 family projection;
- `A3_EFFECT_GROUNDED`: classes defined by preregistered proof-state delta signatures;
- `A4_MACRO`: faithfully mined TacMiner-class macros when executable.

For each level report action entropy, vocabulary size, held-out-module top-k recall/log loss, branching factor, required search depth, verifier calls per solved theorem and solve rate under a shared search algorithm.

Primary scientific question: whether there is an intermediate abstraction level with a better transfer/search frontier than both very atomic and very macro representations.

No level may use theorem/module identity unavailable to the others.

---

# Experiment F — Same-Information Lean Feedback Representation

Status: **FROZEN DESIGN; Lean runtime required**.

For the exact same failed Lean attempt, derive mechanically equivalent diagnostic objects:

- `F0_RAW`: raw Lean error text;
- `F1_CANONICAL_TEXT`: canonical text containing the same diagnostic facts;
- `F2_TYPED_DELTA`: typed failure-state transition object;
- `F3_DEPENDENCY_DELTA`: F2 plus only dependency facts already present in F0/F1.

An independent parser must round-trip all arms to the same canonical diagnostic fact multiset. If equivalence cannot be established, the item is not eligible.

Primary endpoint: one-repair-attempt verified success. Secondary: success by `k` matched attempts, generated tokens, Lean calls, invalid tactic rate and time-to-first-verified repair.

---

# Experiment G — P10 Cross-Revision Structural Transfer

Status: **FROZEN DESIGN; second Mathlib revision required**.

Train/freeze representation and predictor on the existing exact Mathlib revision, then evaluate prospectively on a later preregistered Mathlib revision with no refitting for the primary endpoint.

Compare history-only, native-state, and state+dependency arms on theorem families that can be matched without using outcome information. Report coverage loss separately from predictive loss.

Question: whether structural coordinates degrade more slowly under ecosystem drift than surface/tactic-history coordinates.

---

# Experiment H — Cross-Domain Structural Accessibility Meta-Test

Status: **claim-composition protocol**.

A programme-level structural-accessibility claim requires independently positive evidence in at least two qualitatively different domains under analogous same-information controls.

Candidate normalized quantity:

`NSA = (Perf_structured-Perf_same_info)/(1-Perf_same_info)`

reported per domain without using it as a universal law unless its assumptions are justified.

Required evidence:

1. P9 controlled/natural procedural result;
2. P10 formal Lean result or a prospectively chosen third domain;
3. same sign on preregistered domain-level effects;
4. no pooled-only rescue of a negative domain;
5. explicit heterogeneity.

---

# Execution order

1. Execute A and B immediately with fresh seeds and deterministic replay.
2. Extend the representation-separation theorem programme with the exact block-obfuscation algebraic-degree statement.
3. Implement semantic-orbit generators for controlled P9 tasks while keeping LLM claims gated.
4. Execute the already-frozen P10 native-state incremental-value protocol before E/F/G can promote formal claims.
5. Execute E, then verifier-backed search, then F and G as runtime permits.
6. Execute the P9 LLM structure × scale × compute protocol when a reproducible multi-size model family/runtime is available.
7. Only then evaluate H.

# Permanent nonclaims

- Controlled logistic results are not LLM results.
- Information-equivalent does not mean computationally equivalent for every model family.
- Native Lean acceptance is not theorem meaning or scientific truth.
- Predictive proof-state gains are not proof-search gains.
- Post-hoc statistics cannot be relabeled as preregistered endpoints.

# Relational Accessibility Benchmark Protocol V1

Status: **FROZEN BEFORE BENCHMARK OUTCOME**

Frozen: 2026-08-20

## 1. Question

Can two exactly information-equivalent encodings induce sharply different learnability for a restricted model family when one representation exposes task-relevant relational coordinates and the other leaves those relations implicit?

This controlled benchmark is not an LLM result and is not intended as a novel claim that feature engineering helps linear models. Its purpose is to turn P9's representation-accessibility hypothesis into an exact, scalable, hostile-controlled empirical object before the LLM experiment.

## 2. Latent task

For odd dimension `d`, sample independently and uniformly

`x, c in {-1,+1}^d`.

Interpret `x` as a state and `c` as a candidate. Define the binary target

`y = 1[sum_i x_i c_i > 0]`.

Odd `d` removes ties.

The semantic decision is whether the candidate has positive signed alignment with the state.

## 3. Information-equivalent encodings

### FLAT

`R_flat(x,c) = concat(x,c)`.

### RELATIONAL

Let `r_i = x_i c_i`. Define

`R_rel(x,c) = concat(x,r)`.

This is a bijection on the task support because

`c_i = x_i r_i`.

Therefore the two representations have identical information about the latent pair `(x,c)`. The target is not inserted as a feature. It remains a function of the relation vector:

`y = 1[sum_i r_i > 0]`.

## 4. Frozen dimensions, sample sizes and seeds

Dimensions:

`d in {3,5,9,17,33,65}`.

Training sizes:

`n_train in {64,128,256,512,1024,2048,4096}`.

For every `(d,n_train)` cell, a fresh deterministic training sample is generated from seed

`1000003 + 1009*d + n_train`.

A dimension-specific protected test set of `8192` examples is generated once from seed

`2000003 + 2017*d`.

No seed, dimension or sample-size cell may be removed after inspecting outcomes.

## 5. Frozen model family

Primary restricted learner:

- scikit-learn `LogisticRegression`;
- `C=1.0`;
- `solver='lbfgs'`;
- `max_iter=5000`;
- no hyperparameter tuning;
- same learner and training rows for FLAT and RELATIONAL.

The model family is intentionally simple: the question is computational accessibility under a declared restricted learner, not state-of-the-art classification.

Secondary capacity probes are fit only at `n_train=4096`:

- decision tree depths `{2,4,8,16,None}` on FLAT;
- decision tree depths `{2,4,8,16,None}` on RELATIONAL.

Tree randomness is fixed to `random_state=271828`.

## 6. Primary endpoint

For each dimension at `n_train=4096`:

`Delta_d = accuracy(RELATIONAL logistic) - accuracy(FLAT logistic)`.

The benchmark's positive controlled terminal requires all of:

1. `Delta_d > 0.30` for every frozen dimension;
2. RELATIONAL logistic test accuracy `> 0.90` for every frozen dimension;
3. FLAT logistic test accuracy `< 0.65` for every frozen dimension;
4. exact bijection validation passes on every generated row;
5. label-shuffle and broken-relation controls do not reproduce the relational result.

This threshold is a benchmark terminal only. It does not authorize an LLM or natural-domain claim.

## 7. Secondary endpoints

Report regardless of sign:

- full accuracy table for every `(d,n_train,representation)` cell;
- smallest frozen `n_train` reaching 0.90 accuracy for each representation/dimension, else `NOT_REACHED`;
- accuracy difference curve versus dimension;
- tree depth/capacity curves at `n_train=4096`;
- balanced class rate on every protected test set;
- reconstruction failures, which must be zero;
- coefficient norm and convergence status for logistic fits.

## 8. Hostile controls

### 8.1 Exact reconstruction

For every RELATIONAL vector, reconstruct `c_i = x_i r_i` and require exact equality to the original candidate.

### 8.2 Broken relation

Replace `r_i = x_i c_i` with `r_i = x_i c_{pi(i)}` using one fixed non-identity cyclic permutation of candidate coordinates. The broken relation remains deterministic and same-sized but no longer represents the aligned coordinate relation. Its logistic accuracy is reported.

### 8.3 Label shuffle

For each dimension at `n_train=4096`, shuffle training labels using seed `3000001 + d` while leaving test labels intact. Run both representations and report accuracy.

### 8.4 Surface permutation

Apply one fixed random coordinate permutation jointly to both `x` and `c` before representation construction. Since alignment is invariant to a shared permutation, results should remain materially unchanged. Report the delta from the canonical run.

## 9. Mathematical companion

A companion theorem should prove:

1. `R_flat` and `R_rel` are bijectively equivalent;
2. the target is linearly separable under `R_rel`;
3. the target is not linearly separable under `R_flat` for odd `d >= 3`, by restricting the remaining coordinates so their pairwise contributions cancel and reducing the first coordinate pair to XOR/equality.

The theorem is a controlled restricted-class separation, not a universal statement about neural networks or LLMs.

## 10. Claim ladder

### RA-R0 — exact information equivalence

Allowed after code-level bijection checks and the proof.

### RA-R1 — empirical restricted-family accessibility gap

Allowed only if the frozen primary endpoint passes.

> A bijective relational reparameterization can change held-out learnability by a large margin for a fixed linear learner even when it adds no latent task information.

### RA-R2 — capacity/sample phase diagram

Allowed only if the full frozen sample-size and tree-capacity curves are reported without selection.

### RA-R3 — LLM scaling bridge

**Not authorized by this benchmark.** Requires the separate frozen P9 LLM structure-scaling protocol with actual LLM executions.

## 11. Output contract

The executable must write a single deterministic JSON artifact containing:

- protocol identity;
- environment/library versions;
- every cell result;
- all hostile controls;
- primary terminal;
- exact seeds and dimensions;
- no omitted frozen cell.

Two executions on the same environment must produce byte-identical JSON after excluding no fields; timestamps are forbidden.

# Mathematical Extensions R7 — Exact Candidate-Feature Repair

Date: 2026-08-26

Canonical predecessors: `MANUSCRIPT_V3_PIPELINE.md`, `MATHEMATICAL_EXTENSIONS_R4.md`, `MATHEMATICAL_EXTENSIONS_R5.md`, and `MATHEMATICAL_EXTENSIONS_R6.md`.

Status: theorem addendum. It converts representation insufficiency into an exact feature-selection problem and applies the result to the scalable pair-indistinguishable Pauli families.

## 1. Conflict graph

Let `X` be finite, let `Phi:X->Y`, and let `T:X->R`. Let candidate features be `f_j:X->Sigma_j`, `j in [m]`. For tolerance `epsilon>=0`, define

`E_epsilon={{x,x'}: Phi(x)=Phi(x') and |T(x)-T(x')|>2 epsilon}`.

Feature `j` covers a conflict edge when `f_j(x) != f_j(x')`. For `J subseteq [m]`, let

`Psi_J(x)=(Phi(x),(f_j(x))_{j in J})`.

## 2. Exact repair theorem

**Theorem C12 (conflict-cover criterion).** There exists an estimator `g` satisfying

`|g(Psi_J(x))-T(x)| <= epsilon`

for every `x` if and only if every edge in `E_epsilon` is covered by at least one selected feature in `J`.

**Proof.** If an uncovered conflict remains, its endpoints have the same augmented representation but target values more than `2 epsilon` apart. No common estimate can be within `epsilon` of both.

Conversely, suppose every conflict is covered. Any two instances in one augmented fiber have the same base representation and are not a conflict, so their target values differ by at most `2 epsilon`. The target diameter of every augmented fiber is therefore at most `2 epsilon`. Its midpoint gives the required estimator. ∎

At `epsilon=0`, the theorem gives exact target recovery.

## 3. Optimization complexity

For every candidate feature `j`, let `S_j subseteq E_epsilon` be the edges it covers.

**Corollary C13 (minimum repair is set cover).** The minimum number or minimum total cost of candidate features needed for tolerance `epsilon` is exactly the corresponding set-cover problem on universe `E_epsilon` and sets `S_j`.

The equivalence gives the usual greedy logarithmic approximation and standard parameterized or integer-programming methods. These algorithmic facts are donor set-cover theory; the paper contribution is the exact reduction from representation repair.

**Proposition C14 (hardness under binary features).** Minimum exact repair is NP-hard even when every candidate feature is binary and every base fiber contains two instances.

**Proof.** Given a set-cover instance with universe elements `e`, create a separate base fiber `{u_e,v_e}` with targets zero and one. Candidate feature `j` differs on that pair exactly when set `j` contains `e`. Exact recovery requires every pair to be separated, hence selects exactly a set cover. ∎

## 4. Scalable Pauli application

For each of the `t` disjoint five-term gadgets, choose either local instance `A` or `B` from the pair-indistinguishable construction. This gives `2^t` instances with the same ordered weights and complete labeled pair-gain representation.

Let `k` be the number of `A` gadgets. Exact decomposition gives

`Delta=10t-1` when `k=0`,

and

`Delta=10t+2k-2` when `k>=1`.

Every `A` gadget forces its distinguished triple in every optimum; every `B` gadget has a pair-and-singleton optimum and no optimal triple.

Let `h_i` be the natural local third-order feature that distinguishes the `A` and `B` gadget at position `i`.

**Theorem C15 (linear natural-feature repair).** For exact value recovery, and also for recovery of the vector of forced-triple decisions, all `t` local features `h_1,...,h_t` are necessary and sufficient. For value error `epsilon<1/2`, all `t` remain necessary.

**Proof.** The full feature vector identifies every gadget type and hence `k`, the value, and the optimizer-property vector. If feature `h_i` is omitted, two instances differing only at gadget `i` have identical selected features. Their values differ by one or two and their forced-triple property differs at coordinate `i`. Thus exact recovery fails, and value error below one half fails as well. ∎

## 5. Constrained versus unconstrained information

Inside this `2^t` fiber, the value assumes `t+1` distinct values. An unconstrained categorical supplement therefore needs `t+1` labels, or `ceil(log_2(t+1))` bits, and the single aggregate feature `k` suffices.

The natural local feature library behaves differently: it needs all `t` bits. This separates information-theoretic supplemental bits, the number of available domain features needed for repair, and the number of features needed to reconstruct optimizer structure.

## 6. Applications

The conflict-cover theorem turns lower-bound witnesses into an actionable feature-engineering procedure. In learned combinatorial optimization, exact-solver labels generate the conflict graph and candidate statistics are selected by a weighted set-cover solver. In uncertainty certification, uncovered conflicts give mandatory interval widths. In benchmark design, near-collisions can be ranked by target gap and the cost of separating them. In compiler forecasting, the Pauli family shows why adding model capacity cannot replace missing higher-order measurements.

## 7. Prior-art boundary

Two-point minimax bounds, sufficient statistics, test covers, distinguishing sets, feature selection, and set cover are established areas. The residual contribution is their exact conjunction with the scalable compiler fibers: complete pair information decides the baseline question, has unbounded value ambiguity, and requires a linearly growing natural higher-order repair even though a logarithmic unconstrained encoding exists.

## 8. Atomic status

- Conflict-cover criterion: `VERIFIED`.
- Binary-feature hardness reduction: `VERIFIED`.
- Mixed-product value formula: `VERIFIED` by local decomposition.
- Natural-feature repair number `t`: `VERIFIED`.
- Complexity-class hardness of the original compiler optimization: `NOT_CLAIMED`.
- Transfer to another objective or grammar: `NOT_CLAIMED`.

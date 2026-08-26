# Mathematical Extensions R7 V2 — Exact Candidate-Feature Repair

Date: 2026-08-26

This file supersedes `MATHEMATICAL_EXTENSIONS_R7.md`. The correction distinguishes the presence of any triple-containing co-optimizer from the **distinguished triple being forced in every optimum**. The value-repair theorem and the linear natural-feature lower bound are unchanged.

## 1. Conflict graph

Let `X` be finite, let `Phi:X->Y`, and let `T:X->R`. Let candidate features be `f_j:X->Sigma_j`, `j in [m]`. For tolerance `epsilon>=0`, define

`E_epsilon={{x,x'}: Phi(x)=Phi(x') and |T(x)-T(x')|>2 epsilon}`.

Feature `j` covers a conflict edge when `f_j(x) != f_j(x')`. For `J subseteq [m]`, let `Psi_J(x)=(Phi(x),(f_j(x))_{j in J})`.

## 2. Exact repair theorem

**Theorem C12 (conflict-cover criterion).** There exists an estimator `g` satisfying `|g(Psi_J(x))-T(x)| <= epsilon` for every `x` if and only if every edge in `E_epsilon` is covered by at least one selected feature in `J`.

**Proof.** An uncovered conflict has one augmented representation and two targets more than `2 epsilon` apart, so no common estimate works. Conversely, after all conflicts are covered, every augmented fiber has target diameter at most `2 epsilon`; its midpoint is valid. ∎

**Corollary C13.** Minimum-cost repair is exactly weighted set cover on the conflict edges and the edge sets separated by candidate features.

**Proposition C14.** Minimum exact repair is NP-hard even for binary candidate features and base fibers of size two.

**Proof.** For each element `e` of a set-cover instance, create a separate base fiber `{u_e,v_e}` with targets zero and one. Feature `j` separates this pair exactly when set `j` contains `e`. Exact recovery selects exactly a set cover. ∎

## 3. Mixed Pauli product fiber

Choose independently an `A` or `B` gadget at each of `t` disjoint positions. All `2^t` instances have identical ordered weights and complete labeled pair-gain data. If `k` positions contain `A`, exact decomposition gives

`Delta=10t-1` for `k=0`,

and

`Delta=10t+2k-2` for `k>=1`.

An `A` gadget has a unique maximum-credit local partition and therefore forces its distinguished triple `{1,2,3}` in every global optimum. A `B` gadget has a maximum-credit partition avoiding that distinguished triple, and no local maximum-credit partition contains it.

Some other triple-containing `B` partitions can become global co-optimizers once an `A` gadget has already imposed the width-two penalty. Consequently the correct structural target is not “does any optimum contain a triple?” It is:

`P_i = 1` exactly when the distinguished triple of gadget `i` is forced in every optimum.

Let `h_i` be the natural local third-order feature distinguishing `A` from `B` at position `i`.

**Theorem C15 (linear natural-feature repair).** All `t` features `h_1,...,h_t` are necessary and sufficient for exact value recovery and for recovery of `(P_1,...,P_t)`. For value error below one half, all `t` remain necessary.

**Proof.** The full vector identifies every gadget type, hence `k`, the value, and every `P_i`. If `h_i` is omitted, compare two instances differing only at position `i`. They have identical selected features, their values differ by one or two, and `P_i` differs. ∎

## 4. Constrained versus unconstrained information

The value assumes `t+1` distinct values. An unconstrained supplement therefore requires `t+1` labels, or `ceil(log_2(t+1))` bits; the aggregate count `k` suffices. The natural local library requires all `t` binary features. Information-theoretic bits, available measurement count, and optimizer-structure information are therefore distinct resources.

## 5. Application and scope

The conflict-cover theorem turns exact lower-bound fibers into a feature-selection instance for learned optimizers, uncertainty certification, and adversarial benchmark design. Set-cover complexity is donor theory. No hardness claim is made for the original compiler optimization, and no transfer is asserted beyond the declared structural objective.

## 6. Atomic status

- Conflict-cover criterion: `VERIFIED`.
- Binary-feature reduction: `VERIFIED`.
- Mixed-product value formula: `VERIFIED`.
- Distinguished forced-triple property: `VERIFIED`.
- Linear natural-feature repair: `VERIFIED`.
- Claim that no `B` co-optimizer can contain any triple: `WITHDRAWN`.

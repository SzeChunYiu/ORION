# FiberGuard R9 Addendum: Minimum-Cost Exact Refinement as Collision-Pair Hitting Set

## 1. Motivation

FiberGuard detects when a representation fibre contains target disagreement and supplies a robust `answer / refine / abstain` policy once a refinement menu and its costs are fixed. A separate design problem comes first: which additional features should be made available at all?

This addendum gives an exact answer for finite audited domains. Selecting a minimum-cost nonadaptive refinement that makes a target identifiable is neither an informal feature-selection heuristic nor a property of the learner. It is a weighted hitting-set problem on the target-disagreeing pairs that survive the base representation.

The result also calibrates the approximate case. To guarantee absolute error at most `epsilon`, one must separate exactly those same-base pairs whose target values differ by more than `2 epsilon`.

## 2. Finite refinement model

Let `X` be a finite audited instance set, let

`phi_0 : X -> Z_0`

be the frozen base representation, and let

`T : X -> R`

be the exact target. Candidate refinements are finite-valued features

`psi_j : X -> Z_j`, `j in [m]`,

with nonnegative acquisition costs `c_j`.

For a selected feature set `S`, write

`Phi_S(x) = (phi_0(x), (psi_j(x))_{j in S})`.

The selection is **exact** when `T` is constant on every fibre of `Phi_S`.

For `epsilon >= 0`, the selection is **epsilon-sufficient** when every refined fibre admits a point prediction with worst-case absolute error at most `epsilon`.

## 3. Collision-pair characterization

Define the exact collision set

`P_0 = {{x,x'} : phi_0(x)=phi_0(x') and T(x) != T(x')}`.

Feature `j` separates the pair `{x,x'}` when `psi_j(x) != psi_j(x')`. Let `P_j` be the set of exact collision pairs separated by feature `j`.

### Theorem 1 — exact refinement equivalence

A feature set `S` makes the target exact on the audited domain if and only if

`P_0 subseteq union_{j in S} P_j`.

**Proof.** If a target-disagreeing same-base pair is not separated by any selected feature, both instances remain in one refined fibre, so exact prediction is impossible. Conversely, if every such pair is separated, any two points in one refined fibre have the same base representation and are not a target-disagreeing pair; therefore their target values agree. ∎

Thus minimum-cost exact refinement is weighted set cover on the universe `P_0`, with one cover set `P_j` per candidate feature.

### Corollary 2 — short certificates

A selected feature set is certified sufficient by its pair-separation incidence matrix. If no exact selection exists, one uncovered pair in `P_0` is a complete fail-closed impossibility witness for the declared candidate menu.

The witness owns only the frozen domain and candidate family. It does not prove that no unregistered feature could resolve the collision.

## 4. Approximate absolute-error refinement

For `epsilon >= 0`, define the critical-pair set

`P_epsilon = {{x,x'} : phi_0(x)=phi_0(x') and |T(x)-T(x')| > 2 epsilon}`.

### Theorem 3 — approximate refinement equivalence

A feature set `S` supports a deterministic prediction with worst-case absolute error at most `epsilon` on every refined fibre if and only if every pair in `P_epsilon` is separated by at least one selected feature.

**Proof.** If an unseparated pair differs by more than `2 epsilon`, no single prediction lies within `epsilon` of both endpoints. Conversely, after all critical pairs are separated, every refined fibre has target diameter at most `2 epsilon`; the midpoint of its minimum and maximum target values has error at most `epsilon`. ∎

This theorem converts a tolerance declaration into an exact weighted hitting-set instance. The case `epsilon=0` recovers exact refinement.

## 5. Complexity boundary

### Theorem 4 — NP-completeness under pair fibres

The decision problem MINIMUM EXACT REFINEMENT is NP-complete, even when:

- every base fibre contains exactly two instances;
- targets and candidate features are binary;
- every feature has unit cost; and
- every target-disagreeing fibre contributes exactly one collision pair.

**Proof.** Membership in NP follows by checking all collision pairs against the selected features.

For hardness, reduce SET COVER. Given universe `U`, sets `S_1,...,S_m`, and budget `k`, create for every `u in U` a base fibre `{a_u,b_u}` with target values zero and one. Feature `j` assigns equal bits to `a_u,b_u` when `u notin S_j` and unequal bits when `u in S_j`. A selected feature family separates all target-disagreeing fibres exactly when the corresponding sets cover `U`. ∎

The hardness statement does not claim generic novelty for SET COVER. Its role is to locate the exact computational boundary created by representation collisions.

### Corollary 5 — exact fixed-collision algorithm

If `p=|P_0|`, bitmask dynamic programming solves the weighted problem exactly in

`O(m 2^p)` time and `O(2^p)` memory

after constructing the separation masks. The same algorithm applies to `P_epsilon`.

### Corollary 6 — greedy and weighted variants

For unit costs, the standard greedy set-cover rule gives an `H_p` approximation. With arbitrary nonnegative feature costs, the cost-per-newly-separated-pair rule gives the standard weighted set-cover logarithmic guarantee. These approximation facts are inherited from classical set cover.

## 6. Relation to adaptive FiberGuard policies

The feature-selection problem and the adaptive decision problem are different layers.

1. **Design layer:** choose or provision a feature menu by solving the collision-pair cover problem.
2. **Decision layer:** for an observed base fibre, use the FiberGuard Bellman recursion to answer, acquire one of the provisioned features, or abstain.

A globally sufficient nonadaptive menu may be wasteful on easy fibres. Conversely, an adaptive policy cannot use a feature that was never provisioned. The two optimizations can therefore be nested: an outer menu-selection problem and an inner contingent policy problem.

Neither layer licenses feature costs to be omitted. A refinement that removes every collision but costs more than direct exact solution has no operational value.

## 7. Executable reduction audit

The registered verifier independently constructs the pair-fibre reduction from set systems and compares:

- the source set family;
- the generated feature-separation masks;
- exhaustive feature-subset search;
- bitmask dynamic programming; and
- the exact/approximate critical-pair rule.

It exhausts every set system on universes of sizes one through three: 138 systems in total. The panel contains 115 feasible and 23 infeasible instances. Across the panel, reduction mismatches, dynamic-programming mismatches, certificate failures, and approximate-threshold mismatches are all zero.

The bounded audit corroborates the implementation. The all-size authority comes from the analytic equivalence and reduction.

## 8. Reporting and prior-art boundary

Classical set-cover NP-completeness, greedy approximation, and logarithmic approximation limits are established results and are not claimed as new. The residual FiberGuard contribution is:

- the exact collision-pair object induced by a representation and target;
- the necessary-and-sufficient refinement criterion;
- the `2 epsilon` critical-pair theorem for robust absolute error;
- proof-carrying sufficiency and uncovered-pair impossibility certificates; and
- the separation between menu design and adaptive answer/refine/abstain execution.

The theorem is finite-domain exact. Generalization to unseen instances requires a separate structural theorem or a declared sampling model. A finite atlas PASS cannot be promoted to distributional prevalence or production sufficiency.

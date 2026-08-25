# Epistemic Decision Geometry V1

**Status:** new successor theory. It does not silently modify OSTC-T17 or any historical receipt.
**Empirical trigger:** `EXEC-P12-01/OSTC_T17_SUCCESSOR_NARROWING_V1.md`.
**Authority:** mathematical derivation for the declared classes; external novelty and naturalistic transfer remain open.

## 1. Motivation

Several OSTC results are instances of one decision-theoretic object:

- T2/T3: whether a representation preserves the correct target and its irreducible Bayes risk;
- T12: why two observationally identical worlds force terminal error;
- T14: when interventions separate competing failure causes;
- T17: regret caused by a coarsened allocation certificate;
- T18: responsibility-relative sufficiency and safe state reuse.

The original T17 half-gap clause treated real-valued allocation as if it were 0/1 terminal prediction. `EXEC-P12-01` supplied the missing counterexample: a third action can hedge between two hidden worlds. The correct common theory must therefore represent:

1. scientific states;
2. observable fibres;
3. actions or terminals;
4. responsibility-relative losses;
5. pure and randomized policies;
6. Bayes and worst-case objectives;
7. information refinement and experiment acquisition.

## 2. Primitive objects

Let:

- `X` be a nonempty finite scientific-state set;
- `A` a nonempty finite action/terminal set;
- `r` a responsibility;
- `ℓ_r : X × A → ℝ` a finite loss function;
- `Φ : X → Z` an observable interface;
- `P` a probability distribution on `X` when a Bayes objective is used.

Define the statewise optimum and regret:

\[
m_r(x)=\min_{a\in A}\ell_r(x,a),
\qquad
\Delta_r(x,a)=\ell_r(x,a)-m_r(x)\ge 0.
\]

The set of optimal actions at `x` is

\[
A_r^*(x)=\arg\min_{a\in A}\ell_r(x,a).
\]

For observation `z`, the fibre is

\[
F_z=\{x\in X:\Phi(x)=z\}.
\]

A deterministic interface policy is `π:Z→A`. A randomized policy is `q:Z→Δ(A)`.

## 3. EDG-T1 — exact fibre support theorem

### Statement

A zero-regret deterministic policy measurable with respect to `Φ` exists if and only if every nonempty fibre has a common optimal action:

\[
\exists\pi\;\forall x\in X,\;\Delta_r(x,\pi(\Phi(x)))=0
\iff
\forall z\in\Phi(X),\;\bigcap_{x\in F_z}A_r^*(x)\ne\varnothing.
\]

### Proof

If a zero-regret policy `π` exists, then `π(z)` is optimal for every state in `F_z`, so it belongs to the intersection.

Conversely, choose one action from each nonempty intersection and define `π(z)` to be that action. It is optimal at every state in the fibre. ∎

### Relation to OSTC

When the loss is 0 for the correct scientific terminal and 1 otherwise, every `A_r^*(x)` is the correct terminal set. If the target is single-valued, EDG-T1 reduces exactly to the T2 fibre factorization theorem.

This version is strictly more general because different hidden states may permit several scientifically acceptable terminals even when no single target map is canonical.

## 4. EDG-T2 — fibrewise Bayes envelope

For each observation with positive mass, define

\[
P_z(x)=P(x\mid \Phi(x)=z).
\]

The minimum Bayes loss achievable from `Φ` is

\[
R_P^*(\Phi,r)
=
\sum_{z}P(\Phi=z)
\min_{a\in A}
\mathbb E_{x\sim P_z}[\ell_r(x,a)].
\]

Equivalently, the irreducible Bayes regret is

\[
\mathcal E_P(\Phi,r)
=
\sum_z P(\Phi=z)
\min_{a\in A}
\mathbb E_{x\sim P_z}[\Delta_r(x,a)].
\]

### Proof

A `Φ`-measurable policy chooses one action independently for each fibre. Conditional on a fibre, the expected loss is minimized by the displayed action. Summing over fibres gives the result. ∎

### Consequence

Randomization cannot improve this Bayes objective for a known conditional distribution: expected loss is linear in an action distribution, so a minimum occurs at an extreme point, i.e. a pure action. Randomization can still matter for minimax objectives below.

## 5. EDG-T3 — fibrewise minimax regret radius

Define the deterministic minimax regret radius of a fibre:

\[
\rho_r(F_z)
=
\min_{a\in A}
\max_{x\in F_z}\Delta_r(x,a).
\]

Then the minimum worst-case regret among deterministic `Φ`-measurable policies is

\[
\min_{\pi:Z\to A}\max_{x\in X}\Delta_r(x,\pi(\Phi(x)))
=
\max_{z\in\Phi(X)}\rho_r(F_z).
\]

### Proof

The policy choices on distinct fibres are independent. Within each fibre the best possible worst-case regret is `ρ_r(F_z)`. The global adversary selects the fibre with the largest residual radius. ∎

For randomized policies define

\[
\rho_r^{\mathrm{mix}}(F_z)
=
\min_{q\in\Delta(A)}
\max_{x\in F_z}
\mathbb E_{a\sim q}[\Delta_r(x,a)].
\]

Always

\[
\rho_r^{\mathrm{mix}}(F_z)\le \rho_r(F_z),
\]

and strict inequality is possible because the minimax objective is convex rather than linear in the policy.

## 6. EDG-T4 — exact two-world hedge decomposition

Let two states `x,y` lie in the same fibre and have equal prior. Define

\[
H_r(x,y)
=
\frac12
\min_{a\in A}
\left(\Delta_r(x,a)+\Delta_r(y,a)\right).
\]

This is the exact minimum expected regret of every deterministic interface-only policy on the pair.

Assume for exposition that each state has a unique optimum, `a_x` and `a_y`, and `a_x\ne a_y`. Define the smaller cross-action gap

\[
\delta_r(x,y)
=
\min\{\Delta_r(x,a_y),\Delta_r(y,a_x)\}.
\]

Because choosing either optimum is always permitted,

\[
2H_r(x,y)\le \delta_r(x,y).
\]

Define the **hedge gain**

\[
\eta_r(x,y)
=
\delta_r(x,y)
-
\min_{a\in A}
\left(\Delta_r(x,a)+\Delta_r(y,a)\right)
\ge 0.
\]

Then

\[
H_r(x,y)=\frac{\delta_r(x,y)-\eta_r(x,y)}{2}.
\]

### No-hedge criterion

The historical half-gap expression `δ/2` is exact if and only if

\[
\forall a\in A,
\quad
\Delta_r(x,a)+\Delta_r(y,a)\ge \delta_r(x,y),
\]

or equivalently `η_r(x,y)=0`.

It is therefore not a universal lower bound. It is an always-valid upper bound and becomes the exact optimum under the no-hedge condition.

### Canonical counterexample

For actions `0,1,2`, let losses be

| state | action 0 | action 1 | action 2 |
|---|---:|---:|---:|
| `x` | 0 | 1 | 3 |
| `y` | 3 | 1 | 0 |

The cross-action gap is `δ=3`, but action 1 has regret 1 in both worlds. Thus

\[
H=1<3/2,
\qquad
\eta=1.
\]

This is the `EXEC-P12-01` witness.

## 7. EDG-T5 — terminal prediction as the no-hedge special case

Let the action set be the terminal labels and use 0/1 loss:

\[
\ell(x,a)=\mathbf 1[a\ne T(x)].
\]

For two states with distinct correct terminals:

- choosing either correct terminal has regret vector `(0,1)` or `(1,0)`;
- any third terminal has regret `(1,1)`;
- therefore `δ=1`, `η=0`, and `H=1/2`.

This proves the exact mechanism behind `EXEC-P2-01`: T12 attains the half-error bound because 0/1 terminal loss admits no intermediate action that is nearly correct in both worlds.

The difference between T12 and the original T17 is not merely the size of the grid. It is the geometry of the action-loss set.

## 8. EDG-T6 — positive regret and decision identifiability

For a finite fibre `F`, the following are equivalent:

1. `ρ_r(F)=0`;
2. the common-optimum intersection is nonempty;
3. there exists a deterministic zero-regret action for the fibre.

Therefore

\[
\rho_r(F)>0
\iff
\bigcap_{x\in F}A_r^*(x)=\varnothing.
\]

This is the loss-general identifiability criterion. A representation may fail to identify the hidden state while remaining sufficient for a responsibility if all hidden states share an admissible optimum.

## 9. EDG-T7 — information refinement monotonicity

Let `Ψ` refine `Φ`: there exists `h` with `Φ=h∘Ψ`. Then every `Φ`-measurable policy is also `Ψ`-measurable, so

\[
R_P^*(\Psi,r)\le R_P^*(\Phi,r),
\]

\[
\mathcal E_P(\Psi,r)\le\mathcal E_P(\Phi,r),
\]

and

\[
\max_u\rho_r(\Psi^{-1}(u))
\le
\max_z\rho_r(\Phi^{-1}(z)).
\]

Information cannot worsen the optimal achievable decision value when policy and resource classes are unchanged. It may still worsen total system value after acquisition, storage, computation, latency, or optionality costs are charged.

## 10. EDG-T8 — responsibility joins

Each responsibility `r` induces a decision-equivalence relation:

\[
x\sim_r y
\iff
\forall a\in A_r,
\;\ell_r(x,a)-m_r(x)=\ell_r(y,a)-m_r(y)
\]

or, for exact-support questions, the coarser relation

\[
x\approx_r y
\iff
A_r^*(x)=A_r^*(y).
\]

For a responsibility family `R`, the required exact information partition is the join

\[
\Pi_R=\bigvee_{r\in R}\Pi_r.
\]

Any representation safe for every responsibility in `R` must refine `Π_R`. Adding a responsibility can only preserve or refine the required partition; it cannot make a previously erased distinction reappear.

This supplies the decision-geometric foundation of T18 and P13.

## 11. EDG-T9 — intervention panels as partition refinements

Let an intervention `u` produce outcome `Y_u(x)`. A panel `U` induces the signature

\[
S_U(x)=(Y_u(x))_{u\in U}.
\]

A failure cause or responsibility class is exactly identifiable from the panel if its target terminal is constant on every signature fibre. A minimum identifying panel is therefore a minimum-cost set of interventions whose joint partition refines the target partition.

This recovers the exact portion of T14. The computational problem may reduce to set cover, but a benchmark tests that reduction only if its registered matrix class contains instances on which approximate and exact covers differ.

## 12. EDG-T10 — value of scientific information

Suppose an experiment `e` refines `Φ` to `(Φ,Y_e)`. Define its Bayes value for responsibility `r` as

\[
VOI_P(e\mid\Phi,r)
=
R_P^*(\Phi,r)-R_P^*((\Phi,Y_e),r)\ge 0.
\]

With experiment cost `c(e)`, acquisition is justified under a supplied scalar objective when

\[
VOI_P(e\mid\Phi,r)>c(e).
\]

Without an independently supplied exchange rate, the result is a Pareto comparison over loss reduction, acquisition cost, latency, risk, and future responsibility coverage—not one universal score.

## 13. EDG-T11 — decision-state sufficiency is weaker than world-state recovery

A representation can be sufficient for a responsibility without reconstructing the hidden state:

\[
\bigcap_{x\in F_z}A_r^*(x)\ne\varnothing
\]

may hold even when `|F_z|>1`.

Therefore the minimal scientific state is responsibility-relative. Requiring full hidden-state identification can waste resources; assuming decision sufficiency for a stronger responsibility can be unsound.

## 14. Consequences for the ORION papers

- **P2:** use 0/1 closure terminals and coverage-model refinements; do not import real-valued hedge bounds.
- **P4:** report exact fibre Bayes risk and set-valued admissible terminals.
- **P9:** design intervention grids whose induced partitions actually distinguish exact from heuristic panels.
- **P11:** place computation where it reduces decision risk per charged resource, not where it merely increases state detail.
- **P12:** optimize the exact conditional Bayes/minimax envelope; record hedge actions explicitly.
- **P13:** certify the responsibility partition supported by a reusable state.

## 15. Proof and novelty boundary

The elementary decision-theoretic ingredients—Bayes acts, minimax regret, sufficient statistics, Blackwell-style refinement, and value of information—are donor mathematics.

The candidate ORION residual is the typed integration of:

- scientific responsibilities and terminals;
- `CANNOT_CHECK` and blocker states;
- representation and intervention partitions;
- method/instrument edits;
- authority and adoption separation;
- exact proposal-origin and execution receipts.

No novelty authority follows from this document. A novelty claim requires the separate search and external process governed by #287.
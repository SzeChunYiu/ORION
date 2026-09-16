# Formal core v3 errata v1: deterministic/randomized control typing

## Status

This note is normative for Sections 3--4 and every downstream claim that cites the finite control-complexity hierarchy in `FORMAL_CORE_V3.md`.

The v3 text used stochastic rooted strategies in the general interaction model but then defined finite immediate-action compatibility and autonomous state complexity for deterministic actions/controllers. The proof of

\[
\chi_{\mathrm{act}}
\le
\chi_{\mathrm{plan}}
\le
N^*_{\mathrm{dyn}}
\]

implicitly treated the first decision of a plan as a single deterministic action. That inference is not valid for an unrestricted stochastic plan class.

A randomized first decision can be jointly feasible even when no single deterministic action is jointly feasible under a convex expected-loss constraint. Therefore the three quantities must be typed to the same controller class.

---

## E1. General predictive response remains stochastic

Sections 1--2 of `FORMAL_CORE_V3.md` remain unchanged. A rooted continuation strategy may be a causal stochastic kernel

\[
\kappa_k(da_k^+\mid\sigma_k,s).
\]

The predictive residual theorem is about equality of complete rooted response functionals and does not require deterministic control.

The pathwise complete-cut statement also remains valid when each transcript selects one common stochastic rooted strategy, because plan compatibility is then defined in that same stochastic strategy class.

---

## E2. Controller-class-indexed plan compatibility

Let \(\mathfrak K\) be a declared class of admissible rooted continuation strategies.

Define

\[
\Gamma^{\mathrm{plan},\mathfrak K}_\varepsilon(h;s)
=
\{\kappa\in\mathfrak K:
L_\Omega(h,\kappa;s)\le\varepsilon\}.
\]

A block \(B\) is \(\mathfrak K\)-plan-compatible when

\[
\bigcap_{h\in B}
\Gamma^{\mathrm{plan},\mathfrak K}_\varepsilon(h;s)
\ne\varnothing.
\]

Write

\[
\chi^{\mathfrak K}_{\mathrm{plan}}(\varepsilon;s)
\]

for the associated conflict-hypergraph chromatic number.

Every theorem about plan compatibility must state \(\mathfrak K\) when the distinction between deterministic and randomized strategies can affect feasibility.

---

## E3. Correct deterministic finite hierarchy

For the finite closed-cover specialization, set

\[
\mathfrak K=\mathfrak K_{\mathrm{det}},
\]

the class of deterministic rooted strategies.

For each finite residual state \(v\), let

\[
A^{\mathrm{det}}_\varepsilon(v)
\subseteq\mathcal A
\]

be the deterministic current actions admitted by the registered finite residual specification.

Let

\[
\chi^{\mathrm{det}}_{\mathrm{act}}(\varepsilon)
\]

be the chromatic number of the hypergraph whose compatible blocks have a common action in

\[
\bigcap_{v\in B}A^{\mathrm{det}}_\varepsilon(v).
\]

Let

\[
N^{*,\mathrm{det}}_{\mathrm{dyn}}(\varepsilon)
\]

be the minimum number of reachable states of a clock-free autonomous deterministic controller satisfying the same finite residual specification.

### Corrected Theorem 4.4

Under aligned finite residual, tolerance, observation, side-information, and **deterministic-controller** semantics,

\[
\boxed{
\chi^{\mathrm{det}}_{\mathrm{act}}(\varepsilon)
\le
\chi^{\mathfrak K_{\mathrm{det}}}_{\mathrm{plan}}(\varepsilon;s)
\le
N^{*,\mathrm{det}}_{\mathrm{dyn}}(\varepsilon).
}
\]

### Proof

A deterministic rooted plan has one deterministic first action. Hence every block sharing one deterministic rooted plan shares that first action and is immediate-action compatible. This proves the first inequality.

For the second inequality, take any deterministic autonomous controller with \(N\) reachable internal states. For each internal state \(z\), collect all residual situations that can coexist with \(z\). Starting from \(z\), the controller induces one deterministic rooted strategy as a function of future observations. Therefore each such block is \(\mathfrak K_{\mathrm{det}}\)-plan-compatible. These at most \(N\) blocks cover the reachable residual situations. Plan compatibility is hereditary under taking subsets, so choose for each residual situation one containing controller block. This yields a valid plan coloring with at most \(N\) colors. Minimize over deterministic autonomous controllers. \(\square\)

The registered strict witnesses in `CONTROL_COMPLEXITY_HIERARCHY_RESULTS_V1.json` are deterministic and therefore remain valid for this corrected theorem.

---

## E4. Closed-cover theorem is deterministic unless generalized explicitly

`DYNAMIC_CONTROLLER_CLOSED_COVER_V2.md` is to be read as a theorem about deterministic finite residual controllers and deterministic witness actions.

A randomized-controller analogue requires its own definitions. In particular, one must decide whether a reduced controller state emits:

- a probability distribution over actions;
- a randomized kernel correlated with retained private randomness;
- or a distribution implemented by an enlarged deterministic state carrying a random seed.

These choices can change both compatibility and state accounting. No general randomized closed-cover equality is claimed by the present lane.

Status:

\[
\boxed{\text{general randomized dynamic-control hierarchy: OPEN}.}
\]

---

## E5. Why the unrestricted v3 first inequality is false

The failure is purely a typing error, not a failure of the deterministic theorem.

Take two root states and two deterministic actions \(a,b\). Suppose an expected-loss tolerance is such that:

- at the first root, deterministic \(a\) is above tolerance and deterministic \(b\) is above tolerance;
- at the second root, the same is true;
- but a shared randomized action law \(\tfrac12\delta_a+\tfrac12\delta_b\) satisfies the convex expected-loss tolerance at both roots.

Then the two roots may share a randomized one-step plan even though the deterministic immediate-action intersection is empty. Hence

\[
\text{randomized plan-compatible}
\not\Rightarrow
\text{deterministic action-compatible}.
\]

Any hierarchy that mixes these types is invalid.

The exact numerical witness depends on the declared loss convention; the logical point is that convexification can create feasible mixtures absent from the deterministic action set.

---

## E6. Correct notation downstream

Until a consolidated successor core is written:

- unqualified \(\chi_{\mathrm{plan}}\) in predictive/cut statements may refer to the explicitly declared strategy class, including stochastic strategies;
- every finite closed-cover/control-hierarchy claim must use the deterministic superscript or explicitly state deterministic controller semantics;
- `CLAIM_LEDGER_V1.md` row C3 is interpreted as the deterministic finite theorem;
- `ROOTED_STRATEGY_COMPLEXITY_V1.md` is superseded on this typing point and should not be cited without this erratum.

---

## E7. General controller-class formulation

The safer long-term object is a family indexed by controller class \(\mathfrak C\):

\[
\mathcal I_{\mathrm{control}}(\varepsilon;\mathfrak C,\mathfrak B).
\]

Changing from deterministic to randomized, clocked to clock-free, local-memory to external-memory, or isolated to tool-assisted control changes \(\mathfrak C\) or the machine boundary \(\mathfrak B\). These are different resource questions and should not share one unqualified complexity symbol.

This is consistent with the broader GMI principle that information and morphology claims are meaningful only after the causal placement of computation, randomness, memory, and side information is declared.

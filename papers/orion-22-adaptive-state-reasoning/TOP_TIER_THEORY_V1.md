# ORION-22 top-tier theory expansion V1 — resource-location metareasoning

**Programme:** #977  
**Boundary:** these are decision-theory results for the registered resource-location abstraction. They do not substitute for the still-required open-weight and verifier-backed replications.

## T12.1 — value of adaptive resource location

Let `S` be a pre-outcome signal/state visible before allocation, and let a finite set of feasible resource-location actions be `A`. For each `a in A`, define its conditional expected verified marginal value

\[
v_a(s)=E[V_{after}-V_{before}\mid S=s,a].
\]

For one equal-cost indivisible resource unit and no cross-step coupling, the Bayes-optimal one-step allocator is

\[
a^*(s)\in\arg\max_a v_a(s).
\]

A fixed one-locus policy has value `max_a E[v_a(S)]`; an adaptive location policy has value `E[max_a v_a(S)]`. Therefore

\[
E[\max_a v_a(S)]\ge\max_a E[v_a(S)].
\]

The inequality is strict whenever different actions are uniquely optimal on positive-probability signal regions and no single action is optimal almost surely. This formally states when adaptation over *where* to spend resource has value beyond choosing one globally best locus.

For unequal prospectively priced resources with positive cost `k_a`, the same one-step result applies to net value `v_a(s)-lambda k_a` for a frozen Lagrange multiplier supplied by the decision contract, or to a constrained feasible action set without scalarization.

## T12.2 — substitution and complementarity without post-hoc weights

Let `Q(c,r)` be verified quality as a function of one state-construction increment `c` and one downstream reasoning increment `r`, holding semantic information fixed.

Define the discrete cross-difference

\[
\Delta_{cr}Q = Q(c+1,r+1)-Q(c+1,r)-Q(c,r+1)+Q(c,r).
\]

- `Delta_cr Q > 0`: state improvement and reasoning are complementary at the declared point;
- `Delta_cr Q < 0`: they are substitutable/diminishing with respect to one another;
- `Delta_cr Q = 0`: locally additive/no interaction.

This criterion is invariant to adding separate affine costs to `c` or `r` and therefore does not require choosing a post-hoc scalar reward just to manufacture substitution.

The definition extends pairwise to other registered loci (verification/tool use, recovery, cache/reuse). Higher-order interactions must be reported rather than forced into pairwise attribution when material.

## T12.3 — regret bound from marginal-value estimation

Suppose an allocator uses estimates `hat v_a(s)` satisfying a uniform error bound

\[
|\hat v_a(s)-v_a(s)|\le\epsilon
\]

for every feasible action at the decision point. Let `a*` maximize true marginal value and `ahat` maximize estimated marginal value. Then

\[
v_{a^*}(s)-v_{\hat a}(s)\le 2\epsilon.
\]

Proof:

\[
v_{a^*}-v_{\hat a}
\le (v_{a^*}-\hat v_{a^*})+(\hat v_{\hat a}-v_{\hat a})
\le 2\epsilon,
\]

because `hat v_ahat >= hat v_a*`.

This gives a transparent oracle-regret interpretation: poor allocation can be blamed on marginal-value estimation error only when the registered error bound is itself supported. Under distribution shift the bound must be re-established or the result becomes `CANNOT_CHECK`.

## Resource-vector generalization

The scalar two-unit world in P12A is a controlled special case. For the programme vector

`R=(preprocessing, state memory, model compute, inference/search, tool calls, latency, cache/reuse, recovery)`,

an action is feasible only if adding its prospectively measured resource delta remains within every hard coordinate budget. Pareto-front comparisons are primary when no real decision contract supplies scalar weights.

## Cross-domain transfer claim boundary

T12.1 predicts *when* adaptive location can help, not that one learned allocator transfers universally. Cross-domain top-tier promotion still requires a frozen allocator or registered allocator family evaluated on domains not used for endpoint tuning.

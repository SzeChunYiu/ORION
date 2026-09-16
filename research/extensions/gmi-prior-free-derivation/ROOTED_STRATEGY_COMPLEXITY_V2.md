# Rooted strategies and three distinct control complexities

## Scope

This note fixes the semantics of a “common continuation” after state compression and separates three resource questions that are easily conflated:

\[
\text{current-action information},
\qquad
\text{one-time plan information},
\qquad
\text{autonomous controller state}.
\]

The distinction is required whenever a theory claims that two histories may be merged. A post-merge policy cannot be allowed to recover the forgotten history by inspecting its global prefix.

---

## 1. Rooted strategies

Let \(h_t\) be a root history. Re-index post-root time from zero. Before the \(k\)-th post-root action, define the local suffix

\[
\sigma_k=(a^+_0,o^+_1,\ldots,a^+_{k-1},o^+_k),
\qquad \sigma_0=\varnothing.
\]

A rooted strategy is a causal kernel

\[
\kappa_k(da^+_k\mid \sigma_k,s),
\]

where \(s\) is explicitly declared side information available downstream of the merge or cut. The original root prefix \(h_t\) is not an argument.

If absolute time, an external clock, an identifier, a retrieval result, or another variable remains available after compression, it belongs in \(s\). Otherwise it is not free.

For environment \(e\), write

\[
\operatorname{Eval}^+_\Omega(h,e,\kappa;s)
\]

for the obligation-relevant result of splicing \(\kappa\) after \(h\).

All continuation-based equivalences and feasibility intersections in the GMI core use this rooted semantics.

---

## 2. One-time plan complexity

Let \(L_\Omega(h,\kappa;s)\) be robust loss and define

\[
\Gamma^{\mathrm{plan}}_\varepsilon(h;s)
=
\{\kappa:L_\Omega(h,\kappa;s)\le\varepsilon\}.
\]

A set \(B\) is plan-compatible when

\[
\bigcap_{h\in B}
\Gamma^{\mathrm{plan}}_\varepsilon(h;s)
e\varnothing.
\]

Let \(\mathfrak C^{\mathrm{plan}}_\varepsilon\) be the hypergraph whose hyperedges are the non-plan-compatible sets. For finite domains define

\[
\chi_{\mathrm{plan}}(\varepsilon;s)
=
\chi(\mathfrak C^{\mathrm{plan}}_\varepsilon).
\]

Operationally, \(\chi_{\mathrm{plan}}\) is the minimum number of labels needed by a one-time encoder that knows the root and selects one rooted strategy. The state/computation required to execute that strategy is not included in the label count.

---

## 3. Repeated current-action complexity

For a finite residual control specification \(V\), let \(A_\varepsilon(v)\) be the currently admissible actions. A block \(B\subseteq V\) is action-compatible when

\[
\bigcap_{v\in B}A_\varepsilon(v)
e\varnothing.
\]

Let

\[
\chi_{\mathrm{act}}(\varepsilon)
\]

be the chromatic number of the resulting immediate-action conflict hypergraph.

This is the minimum alphabet size for an encoder that may inspect the true residual state again at every step and send enough information to select only the current action. It externalizes all future state tracking.

---

## 4. Autonomous dynamic complexity

Let

\[
N^*_{\mathrm{dyn}}(\varepsilon)
\]

be the minimum number of reachable states of a clock-free autonomous deterministic controller that receives only the declared observation stream and side information after initialization.

For a finite incompletely specified residual machine, the classical closed-cover construction gives

\[
N^*_{\mathrm{dyn}}(\varepsilon)
=
\min_{\mathcal K\text{ closed}}|\mathcal K|,
\]

where each cover member admits a common output/action and all of its implied successor sets are contained in cover members.

This is the same cover/closure distinction used in minimization of incompletely specified finite-state machines; see Puri and Gu (1993), *IEEE Transactions on CAD*, 12(6):737–745, DOI 10.1109/43.229748, and Ahmad and Das (2001), *Computers & Electrical Engineering*, 27(2):159–172, DOI 10.1016/S0045-7906(00)00016-1.

---

## 5. Hierarchy theorem

### Theorem 5.1

Under aligned tolerance, residual, observation, and side-information semantics,

\[
\boxed{
\chi_{\mathrm{act}}(\varepsilon)
\le
\chi_{\mathrm{plan}}(\varepsilon)
\le
N^*_{\mathrm{dyn}}(\varepsilon).
}
\]

### Proof

If one rooted plan works for every residual in a block, its first action is admissible for every residual in that block. Hence every plan-compatible block is action-compatible and the first inequality follows.

Now take an autonomous controller with \(N\) reachable internal states. For each internal state \(z\), collect all residual situations that can coexist with \(z\). From \(z\), the controller induces one rooted strategy on future observation suffixes. Therefore each such residual set is plan-compatible. These at most \(N\) sets cover the reachable residual situations. Plan compatibility is hereditary under subsets, so assigning each residual to one containing set yields a plan coloring with at most \(N\) colors. Minimize over controllers. \(\square\)

Neither inequality is generically an equality.

---

## 6. Strict witness: action information < plan information

Let

\[
V=\{x,y,z\},
\qquad
A(x)=A(y)=\{0\},
\qquad
A(z)=\{1\},
\]

with one uninformative observation and deterministic residual dynamics

\[
x\to x,
\qquad
y\to z,
\qquad z\to x.
\]

The current-action conflict graph is bipartite with color classes \(\{x,y\}\) and \(\{z\}\), hence

\[
\chi_{\mathrm{act}}=2.
\]

The rooted action sequences required from the three residuals are respectively

\[
0,0,0,\ldots;
\qquad
0,1,0,0,\ldots;
\qquad
1,0,0,\ldots.
\]

The future observation stream is identical, so no two residuals share one rooted plan. Thus

\[
\chi_{\mathrm{plan}}=3.
\]

The three residual states themselves give a three-state autonomous realization:

\[
\boxed{
2=\chi_{\mathrm{act}}
<
\chi_{\mathrm{plan}}=N^*_{\mathrm{dyn}}=3.
}
\]

---

## 7. Strict witness: plan information < autonomous state

Let

\[
V=\{0,1,2,3\},
\]

\[
A(0)=A(1)=\{0\},
\qquad
A(2)=\{1\},
\qquad
A(3)=\{0,1\},
\]

and

\[
0\to1,
\qquad
1\to3,
\qquad
2\to2,
\qquad
3\to2,
\]

again with one uninformative observation.

The block \(\{0,1\}\) shares the rooted plan

\[
0,0,1,1,1,\ldots,
\]

because its uncertainty set evolves as

\[
\{0,1\}	o\{1,3\}	o\{2,3\}	o\{2\}.
\]

The block \(\{2,3\}\) shares the rooted plan \(1,1,1,\ldots\). Since residuals \(0\) and \(2\) require different first actions,

\[
\chi_{\mathrm{plan}}=2.
\]

Immediate action compatibility also gives \(\chi_{\mathrm{act}}=2\).

No two-member closed cover exists. The compatible two-block candidate that merges \(0\) and \(1\) has implied successor set \(\{1,3\}\), which cannot be contained in either of the two necessary action-compatible blocks. A three-member closed cover is

\[
\{0\},
\qquad
\{1\},
\qquad
\{2,3\},
\]

with implications

\[
\{0\}\to\{1\},
\qquad
\{1\}\to\{2,3\},
\qquad
\{2,3\}\to\{2,3\}.
\]

Therefore

\[
\boxed{
\chi_{\mathrm{act}}
=
\chi_{\mathrm{plan}}
=2
<
N^*_{\mathrm{dyn}}=3.
}
\]

The strictness is the memory needed to execute the selected plan without a free external phase oracle.

The finite exhaustive checker and frozen result are `control_complexity_hierarchy_checks_v1.py` and `CONTROL_COMPLEXITY_HIERARCHY_RESULTS_V1.json`.

---

## 8. Consequence

A task does not determine one scalar “amount of information required for intelligence”. Different causal placements of the same obligation induce different resource questions:

\[
I_{\mathrm{act}}
=
\log_2\chi_{\mathrm{act}},
\qquad
I_{\mathrm{plan}}
=
\log_2\chi_{\mathrm{plan}},
\qquad
M_{\mathrm{dyn}}
=
\log_2 N^*_{\mathrm{dyn}}.
\]

The first charges repeated external state disclosure; the second charges one-time plan selection but not plan execution memory; the third charges autonomous retained controller state.

Accordingly, a morphology comparison is meaningless until the system boundary declares where memory, clocks, retrievers, planners, and plan-execution state are counted.

---

## 9. Relation to predictive-state theory

The predictive residual quotient and the control complexities answer different questions. Predictive-state representations use action-conditional predictions of future observations as state; Littman, Sutton and Singh (2001), *Predictive Representations of State*, NeurIPS, is a direct donor for that viewpoint.

For fully specified deterministic language recognition, Myhill–Nerode residual equivalence is a right congruence and yields a unique minimal deterministic automaton. In incompletely specified control, several outputs may be acceptable. Compatibility then need not be transitive, and minimum realizations are naturally expressed by closed covers rather than by a unique quotient.

The GMI contribution cannot be the rediscovery of predictive states, graph coloring, or closed covers. Its candidate contribution is the cross-layer derivation from an obligation/ecology to residual control structure, then to communication/state lower bounds, physical morphology phase laws, and finally prospective architecture prediction.

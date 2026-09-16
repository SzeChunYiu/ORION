# Prior-free control-information profiles

## 1. Robust loss and rooted plans

Let

\[
L_\Omega(h,\kappa;s)
=
\sup_{e\in\mathcal E}
\ell_\Omega(h,e,\kappa;s)
\]

for a rooted, prefix-blind continuation strategy \(\kappa\) and declared downstream side information \(s\).

For tolerance \(\varepsilon\), define

\[
\Gamma^{\mathrm{plan}}_\varepsilon(h;s)
=
\{\kappa:L_\Omega(h,\kappa;s)\le\varepsilon\}.
\]

A set of roots \(B\) is plan-compatible exactly when

\[
\bigcap_{h\in B}
\Gamma^{\mathrm{plan}}_\varepsilon(h;s)
e\varnothing.
\]

Let \(\mathfrak C^{\mathrm{plan}}_\varepsilon\) be the hypergraph of non-plan-compatible subsets and define

\[
\chi_{\mathrm{plan}}(\varepsilon;s)
=
\chi(\mathfrak C^{\mathrm{plan}}_\varepsilon),
\qquad
I_{\mathrm{plan}}(\varepsilon;s)
=
\log_2\chi_{\mathrm{plan}}(\varepsilon;s).
\]

This is a one-time plan-selection quantity. It does not charge the decoder memory or computation needed to execute the selected plan.

---

## 2. Immediate-action profile

For a finite residual control specification \(V\), let \(A_\varepsilon(v)\) be the actions whose registered current-step loss is at most \(\varepsilon\). A subset \(B\subseteq V\) is action-compatible when

\[
\bigcap_{v\in B}A_\varepsilon(v)\ne\varnothing.
\]

Let

\[
\chi_{\mathrm{act}}(\varepsilon)
\]

be the chromatic number of the immediate-action conflict hypergraph and

\[
I_{\mathrm{act}}(\varepsilon)
=
\log_2\chi_{\mathrm{act}}(\varepsilon).
\]

Operationally, this is the minimum message-alphabet size when an external encoder can inspect the residual state anew at every step and only has to communicate enough information to select the current action.

---

## 3. Dynamic state profile

For the same finite residual specification, define

\[
N^*_{\mathrm{dyn}}(\varepsilon)
=
\min_{\mathcal K\text{ closed}}
|\mathcal K|
\]

and

\[
M_{\mathrm{dyn}}(\varepsilon)
=
\log_2 N^*_{\mathrm{dyn}}(\varepsilon).
\]

This charges autonomous persistent controller state. It differs from both communication profiles because neither a repeated external encoder nor an uncharged plan executor is available.

---

## 4. Monotonicity

### Proposition 4.1

Each of

\[
\chi_{\mathrm{act}}(\varepsilon),
\qquad
\chi_{\mathrm{plan}}(\varepsilon;s),
\qquad
N^*_{\mathrm{dyn}}(\varepsilon)
\]

is nonincreasing as the permitted tolerance increases, provided the residual dynamics and side-information model are fixed.

### Proof

Increasing \(\varepsilon\) enlarges every admissible-action set and every feasible-plan set. It therefore removes conflict hyperedges and cannot invalidate a previously valid closed cover. \(\square\)

For finite action, residual, and finite-horizon plan spaces, the corresponding profiles are step functions whose breakpoints occur at finitely many joint-control loss levels.

---

## 5. Hierarchy

Under aligned finite residual semantics,

\[
\boxed{
I_{\mathrm{act}}(\varepsilon)
\le
I_{\mathrm{plan}}(\varepsilon;s)
\le
M_{\mathrm{dyn}}(\varepsilon).
}
\]

Equivalently,

\[
\chi_{\mathrm{act}}
\le
\chi_{\mathrm{plan}}
\le
N^*_{\mathrm{dyn}}.
\]

The proof and strict finite witnesses are in `ROOTED_STRATEGY_COMPLEXITY_V2.md`. Both inequalities can be strict.

The hierarchy is not a hierarchy of “intelligence”. It is a hierarchy of resource models induced by where state information is allowed to reside.

---

## 6. One-time complete-cut theorem

Let a complete cut carry finite transcript \(Y\) from the root-history side to a downstream plan executor. Every other history-dependent influence across the cut is excluded, while registered side information \(s\) is available on both sides as declared.

Assume the pathwise contract:

> for every root \(h\) and every transcript value \(y\) that can occur after \(h\), the rooted plan selected from \((y,s)\) has loss at most \(\varepsilon\) from \(h\).

For each transcript symbol define

\[
B_y
=
\{h:\Pr(Y=y\mid h)>0\}.
\]

The selected plan must lie in the feasible-plan intersection for \(B_y\), so \(B_y\) is plan-compatible. Therefore

\[
\boxed{
|\mathcal Y|
\ge
\chi_{\mathrm{plan}}(\varepsilon;s),
}
\]

or

\[
\log_2|\mathcal Y|
\ge
I_{\mathrm{plan}}(\varepsilon;s).
\]

For a tuple of finite channels \(Y=(Y_1,\ldots,Y_m)\),

\[
\sum_i\log_2|\mathcal Y_i|
\ge
I_{\mathrm{plan}}(\varepsilon;s).
\]

This is a zero-error/pathwise theorem. A stochastic channel can encode many different average action distributions with a small alphabet; distinct output laws alone do not imply a cardinality lower bound.

---

## 7. Repeated action cut

If an encoder observes the true residual at every step and transmits only a current-action message, the analogous one-step bound is

\[
|\mathcal Y_{\mathrm{step}}|
\ge
\chi_{\mathrm{act}}(\varepsilon).
\]

Repeated use of this channel can substitute communication for persistent controller state. Any morphology comparison between the repeated-encoder design and an autonomous controller must therefore charge the repeated communication path in the resource vector.

---

## 8. One-time plan achievability

For a finite root set with attained feasible-plan intersections, an optimal plan coloring is achievable with exactly

\[
\chi_{\mathrm{plan}}(\varepsilon;s)
\]

transcript symbols: the encoder sends the color and the decoder executes one common feasible rooted plan for that color class.

This establishes exact one-shot communication complexity **only under the declared decoder model**. The internal memory or phase state needed to execute a plan remains outside the transcript count and can make

\[
N^*_{\mathrm{dyn}}
>
\chi_{\mathrm{plan}}.
\]

---

## 9. Capacity-performance duals

Define

\[
\varepsilon^*_{\mathrm{plan}}(b;s)
=
\inf\{\varepsilon:
I_{\mathrm{plan}}(\varepsilon;s)
\le b\},
\]

and

\[
\varepsilon^*_{\mathrm{act}}(b)
=
\inf\{\varepsilon:
I_{\mathrm{act}}(\varepsilon)
\le b\}.
\]

These are worst-case task curves: a plan-selection cut or repeated action cut with at most \(b\) bits of distinguishable transcript cannot beat the corresponding lower envelope under the stated pathwise model.

For finite attained problems the one-shot bounds are tight by coloring constructions.

---

## 10. Distribution-conditioned refinements

The profiles above do not contain a source distribution over roots. They are therefore not Shannon mutual-information or rate-distortion quantities.

If a source/visitation law is later supplied, one may instead study expected code length, graph entropy, rate-distortion, information bottleneck, or other distribution-conditioned quantities. Such refinements can be lower in expectation than the worst-case alphabet bound without contradiction because they answer a different coding problem.

The zero-error graph-coloring connection is classical; Witsenhausen (1976), “The zero-error side information problem and chromatic numbers,” *IEEE Transactions on Information Theory* 22(5):592–593, DOI 10.1109/TIT.1976.1055607, is a direct donor.

The GMI-specific object is the derivation of the conflict structure from \((\Omega,\mathcal E,\mathfrak B)\), not graph coloring itself.

---

## 11. Relation to morphology

The information profiles constrain but do not identify implementation morphology. A required \(I_{\mathrm{plan}}\) or \(M_{\mathrm{dyn}}\) can be realized through many physical organizations: local persistent state, distributed state, external communication, recomputation, retrieval, or a change in the interaction protocol.

Architecture selection begins only after a physical/resource model \(\rho_\theta\) is imposed and the necessity bounds are matched by explicit constructions. The correct closure mechanism is the necessity–construction sandwich of `FORMAL_CORE_V3.md`.

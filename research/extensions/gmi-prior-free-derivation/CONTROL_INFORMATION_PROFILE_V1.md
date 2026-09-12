# Prior-free GMI: control-information profile v1

## 0. Purpose

`FORMAL_CORE_V2.md` replaces the false identification of predictive state with minimal control state by a control-conflict hypergraph. This note pushes that object one step further: it derives a prior-free worst-case information-demand curve for approximate control.

The construction is deliberately combinatorial. It does not use a source distribution over histories or a prior over environments. It is therefore not Shannon rate-distortion. Its nearest donors are zero-error/functional source coding, graph coloring, worst-case control and communication complexity.

---

## 1. Worst-case control loss

Let

\[
\ell_\Omega(h,e,c)\in[0,\infty]
\]

be a declared loss of continuation policy \(c\) after history \(h\) in environment \(e\). Define robust continuation loss

\[
L_\Omega(h,c)
=
\sup_{e\in\mathcal E}\ell_\Omega(h,e,c).
\]

For tolerance \(\varepsilon\ge0\), define the feasible continuation set

\[
\Gamma_\varepsilon(h)
=
\{c\in\mathcal C:L_\Omega(h,c)\le\varepsilon\}.
\]

Exact binary obligations are recovered by choosing loss zero on satisfying outcomes and \(+\infty\) or one on violations and setting \(\varepsilon=0\).

---

## 2. Joint control radius

For a nonempty set of histories \(B\), define

\[
r_\Omega(B)
=
\inf_{c\in\mathcal C}
\sup_{h\in B}L_\Omega(h,c).
\]

This is the least worst-case loss achievable when one continuation must serve every history in \(B\).

If the infimum is attained, then

\[
\bigcap_{h\in B}\Gamma_\varepsilon(h)\ne\varnothing
\iff
r_\Omega(B)\le\varepsilon.
\]

Without attainment, the forward implication remains exact and the reverse implication holds with the usual closure/slack qualification. Finite continuation classes need no qualification.

### Interpretation

The scalar \(r_\Omega(B)\) is intrinsic to the obligation/ecology/continuation class. It does not refer to an implementation. It measures the price of forcing the histories in \(B\) to share one future control law.

---

## 3. Tolerance-indexed conflict hypergraph

For each \(\varepsilon\), define the hypergraph

\[
\mathfrak C_\varepsilon=(V,\mathcal E_\varepsilon),
\qquad
V=\mathcal H_{\mathrm{adm}},
\]

with hyperedges

\[
\mathcal E_\varepsilon
=
\left\{
B\subseteq V:
\bigcap_{h\in B}\Gamma_\varepsilon(h)=\varnothing
\right\}.
\]

For finite calculations it suffices to retain inclusion-minimal hyperedges.

A color class is valid when all histories assigned that color admit at least one common continuation with robust loss at most \(\varepsilon\).

Let

\[
\chi_\Omega(\varepsilon)
=
\chi(\mathfrak C_\varepsilon)
\]

be the minimum number of valid colors.

### Definition 3.1 (control-information profile)

\[
I_\Omega(\varepsilon)
=
\log_2\chi_\Omega(\varepsilon).
\]

When the chromatic number is infinite, set \(I_\Omega(\varepsilon)=+\infty\).

`I_Ω` is measured in worst-case distinguishable bits, not expected code length.

---

## 4. Monotonicity theorem

### Theorem 4.1

If \(0\le\varepsilon_1\le\varepsilon_2\), then

\[
\Gamma_{\varepsilon_1}(h)
\subseteq
\Gamma_{\varepsilon_2}(h)
\quad\forall h,
\]

hence

\[
\mathcal E_{\varepsilon_2}
\subseteq
\mathcal E_{\varepsilon_1},
\]

and therefore

\[
\chi_\Omega(\varepsilon_2)
\le
\chi_\Omega(\varepsilon_1),
\qquad
I_\Omega(\varepsilon_2)
\le
I_\Omega(\varepsilon_1).
\]

#### Proof

Increasing the tolerance cannot remove a feasible continuation from any \(\Gamma_\varepsilon(h)\). Consequently any set jointly controllable at \(\varepsilon_1\) remains jointly controllable at \(\varepsilon_2\), so conflict hyperedges can only disappear. Every coloring valid for the smaller tolerance is therefore valid for the larger tolerance. \(\square\)

### Finite phase structure

For finite \(V\) and finite \(\mathcal C\), the profile is a nonincreasing step function. Its breakpoints lie among the finitely many joint-control radii \(r_\Omega(B)\).

Thus a task can possess architecture-independent information **phase transitions** before any machine family is introduced.

---

## 5. Controller-state lower bound

### Theorem 5.1

Consider a deterministic controller required to achieve robust loss at most \(\varepsilon\) from every admitted history. Suppose the controller's retained state after the history takes at most \(N\) values. Then

\[
N\ge\chi_\Omega(\varepsilon),
\]

and any fixed-length binary state representation needs

\[
b\ge
\left\lceil I_\Omega(\varepsilon)\right\rceil
\]

bits.

#### Proof

Histories mapped to one controller state must share the same retained information. The continuation implemented from that state must be \(\varepsilon\)-feasible for every history in its fiber. Hence each state fiber is a valid color class of \(\mathfrak C_\varepsilon\). The state map is therefore a coloring and uses at least the chromatic number of colors. \(\square\)

### Boundary 5.2

This is a necessary bound for persistent dynamic controllers. A coloring need not itself define a realizable finite-state controller because successor histories must also admit a consistent causal state update. Dynamic realizability can increase the required number of states.

---

## 6. One-shot complete-cut theorem

Let a complete causal cut carry transcript \(Y\) from the history side to a downstream controller. The downstream side may possess declared common side information, but no other history-dependent influence may cross the cut.

Assume the following pathwise worst-case contract:

> for every history \(h\) and every transcript value \(y\) occurring with positive probability after \(h\), the continuation selected after observing \(y\) has robust loss at most \(\varepsilon\) from \(h\).

### Theorem 6.1

For finite transcript alphabet \(\mathcal Y\),

\[
|\mathcal Y|
\ge
\chi_\Omega(\varepsilon),
\]

hence

\[
\log_2|\mathcal Y|
\ge
I_\Omega(\varepsilon).
\]

#### Proof

For each \(y\), let

\[
B_y=\{h:\Pr(Y=y\mid h)>0\}.
\]

The pathwise contract says the continuation selected after \(y\) lies in every \(\Gamma_\varepsilon(h)\), \(h\in B_y\). Thus \(B_y\) is a valid color class. Assign each history any one transcript value in its nonempty support. This produces a proper coloring with at most \(|\mathcal Y|\) colors. \(\square\)

### Corollary 6.2 (multi-channel cut)

If the complete transcript is a tuple

\[
Y=(Y_1,\ldots,Y_m)
\]

with finite alphabets, then

\[
\prod_{i=1}^m|\mathcal Y_i|
\ge
\chi_\Omega(\varepsilon),
\]

or equivalently

\[
\sum_{i=1}^m\log_2|\mathcal Y_i|
\ge
I_\Omega(\varepsilon).
\]

This is an architecture-independent cut constraint. The machine may realize the channels through recurrence, attention, retrieval, symbolic memory, inter-agent messages, or another mechanism; the lower bound is unchanged as long as the cut semantics are the same.

---

## 7. One-shot achievability

The chromatic bound is exact for a one-shot cut when arbitrary color assignment and one continuation per color are implementable.

### Theorem 7.1

Assume finite \(V\), finite \(\chi_\Omega(\varepsilon)\), and that every valid color class has an attained common \(\varepsilon\)-feasible continuation. Then there exists a one-shot encoder/decoder with

\[
|\mathcal Y|=\chi_\Omega(\varepsilon)
\]

satisfying the pathwise robust \(\varepsilon\) contract.

#### Proof

Take an optimal coloring. The encoder sends the color of the observed history. For each color class choose one continuation from the nonempty intersection of its feasible-continuation sets. The decoder executes that continuation. \(\square\)

Therefore the one-shot worst-case control communication requirement is exactly

\[
I_\Omega(\varepsilon)
\]

bits up to integer coding of the alphabet.

This equality should not be transferred to persistent dynamic controllers without the additional congruence/realizability theorem.

---

## 8. Capacity-performance dual

Define the best tolerance compatible with a \(b\)-bit complete cut by

\[
\varepsilon^*_\Omega(b)
=
\inf\left\{
\varepsilon\ge0:
I_\Omega(\varepsilon)\le b
\right\}.
\]

### Corollary 8.1

Any pathwise controller whose complete history-to-decision cut carries at most \(b\) bits of distinguishable transcript must have worst-case loss at least the lower envelope determined by \(\varepsilon^*_\Omega(b)\). In finite attained one-shot problems the bound is tight.

This is the form most directly comparable with architecture-independent capability laws:

\[
\boxed{
\text{information budget}
\longleftrightarrow
\text{best possible worst-case obligation error}
}
\]

without a prior over histories or environments.

---

## 9. Relation to predictive state

`I_Ω(ε)` is a control quantity. It can be strictly smaller than the number of bits needed to reconstruct the full predictive response state.

If two histories have different future response profiles but admit one common \(\varepsilon\)-successful continuation, the predictive quotient separates them while the control hypergraph permits them to share a color.

Thus there are two task-information curves:

1. predictive reconstruction complexity;
2. control information complexity.

The second is the relevant lower bound for a machine required only to act successfully.

---

## 10. Relation to probability and rate-distortion

No source distribution occurs in the definitions above. Consequently `I_Ω` is not Shannon mutual information and is not a substitute for average-case rate-distortion theory.

If a visitation/source law \(P(H)\) is later supplied, one may ask for expected code length, mutual information, graph entropy, or lossy functional compression. Those are additional distribution-conditioned refinements.

The prior-free object remains useful because it gives the zero-distribution, worst-case envelope that any such refinement must respect under a pathwise guarantee.

---

## 11. Donor boundary

The graph-coloring mechanism is established territory in zero-error information theory and functional source coding. In particular, zero-error side-information coding connects minimum instantaneous alphabet size to graph coloring, while asymptotic block coding leads to graph-entropy-type quantities.

The GMI claim must therefore **not** be “graph coloring is new”. The research question is whether the obligation-derived control-conflict construction, when combined with substrate/resource morphology and developmental reachability, yields correct architecture-independent capability laws and prospective morphology predictions.

Until donor comparison is completed at theorem level, this note should be described as a GMI specialization/composition of established combinatorial information ideas.

---

## 12. Immediate tests

1. Recover the existing ORION one-channel and two-channel capability laws as special cases of an explicitly constructed \(\mathfrak C_\varepsilon\).
2. Find a task where predictive-state cardinality is exponentially larger than \(\chi_\Omega(0)\), demonstrating why the control correction matters quantitatively.
3. Construct a task where the hypergraph coloring lower bound is strictly below the minimum realizable dynamic-controller state count because of transition congruence.
4. Compare one-shot \(I_\Omega(\varepsilon)\) with graph entropy under an added source law; verify that the latter can be smaller in expected/asymptotic coding without violating the worst-case theorem.
5. Derive a resource phase boundary where the same \(I_\Omega\) is optimally realized by different persistence/access geometries as substrate parameters vary.

These tests are the next mathematical bridge from channel laws to morphology.

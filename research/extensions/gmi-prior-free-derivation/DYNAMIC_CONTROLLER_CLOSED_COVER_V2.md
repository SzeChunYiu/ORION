# Dynamic control state as a minimum closed-cover problem

## 1. Finite residual specification

Let \(V\) be a finite set of control residuals, \(\mathcal O\) a finite observation alphabet, and \(\mathcal A\) a finite action alphabet. At tolerance \(\varepsilon\), let

\[
A_\varepsilon(v)\subseteq\mathcal A
\]

be the currently admissible actions at residual \(v\). For \(a\in A_\varepsilon(v)\) and observation \(o\), let

\[
\operatorname{Succ}(v,a,o)\subseteq V
\]

be the possible next residuals.

The specification is assumed Markov at this level: the residual contains whatever task information is needed to determine admissible current actions and successor residuals.

---

## 2. Compatible classes and implications

A nonempty set \(C\subseteq V\) is action-compatible when

\[
A_\varepsilon(C)
:=
\bigcap_{v\in C}A_\varepsilon(v)
\ne\varnothing.
\]

For a selected common action \(a\in A_\varepsilon(C)\), define the implied successor set

\[
I(C,a,o)
=
\bigcup_{v\in C}
\operatorname{Succ}(v,a,o).
\]

A controller state representing \(C\) is dynamically valid only if its single next internal state after observation \(o\) can represent every residual in \(I(C,a,o)\).

---

## 3. Closed controller cover

A family

\[
\mathcal K=\{C_1,\ldots,C_m\}
\]

of nonempty subsets of \(V\) is an \(\varepsilon\)-closed controller cover when:

1. \(\bigcup_i C_i=V\);
2. each \(C_i\) has a selected witness action \(a_i\in A_\varepsilon(C_i)\);
3. for every \(i\) and observation \(o\) with nonempty implication,
   \[
   I(C_i,a_i,o)
   \subseteq C_j
   \]
   for some \(C_j\in\mathcal K\).

The cover may overlap. Overlap is necessary in general because compatibility is not an equivalence relation.

---

## 4. Exact realization theorem

### Theorem 4.1

Every closed controller cover of size \(m\) induces an autonomous deterministic controller with at most \(m\) internal states satisfying the finite residual specification.

### Proof

Associate internal state \(z_i\) with \(C_i\). In \(z_i\), output \(a_i\). After observing \(o\), transition to a state \(z_j\) whose class contains \(I(C_i,a_i,o)\). If the actual residual initially lies in \(C_i\), induction on time shows that it lies in the class represented by the controller after every transition. The selected action is therefore admissible at every step. \(\square\)

### Theorem 4.2 — converse

Every autonomous deterministic controller satisfying the specification induces a closed controller cover with no more members than reachable controller states.

### Proof

For each reachable controller state \(z\), let \(C_z\) be the residuals that can coexist with \(z\). The controller outputs one action in \(z\), so that action belongs to \(A_\varepsilon(v)\) for every \(v\in C_z\). If observation \(o\) sends the controller to \(z'\), every possible residual successor from \(C_z\) under that action and observation must lie in \(C_{z'}\). Thus the family \(\{C_z\}\) covers \(V\) and is closed. \(\square\)

### Corollary 4.3

The exact minimum autonomous state count is

\[
\boxed{
N^*_{\mathrm{dyn}}(\varepsilon)
=
\min_{\mathcal K\text{ closed}}|\mathcal K|.
}
\]

This is the classical closed-cover characterization specialized to an obligation-derived residual control machine.

---

## 5. Relation to static action information

Let \(\chi_{\mathrm{act}}(\varepsilon)\) be the chromatic number of the hypergraph whose invalid color classes are the action-incompatible subsets of \(V\).

Every member of a closed cover is action-compatible. Assign each residual to one cover member containing it. This gives a valid action coloring with no more colors than cover members. Therefore

\[
\boxed{
\chi_{\mathrm{act}}(\varepsilon)
\le
N^*_{\mathrm{dyn}}(\varepsilon).
}
\]

The inequality can be strict because coloring enforces only current-action compatibility whereas an autonomous controller must also close successor implications.

The stronger hierarchy involving one-time rooted plans,

\[
\chi_{\mathrm{act}}
\le
\chi_{\mathrm{plan}}
\le
N^*_{\mathrm{dyn}},
\]

is proved separately in `ROOTED_STRATEGY_COMPLEXITY_V2.md`. The quantities must not be denoted by one overloaded \(\chi\): they correspond to different information boundaries.

---

## 6. Strict closure-gap witness

Take residuals

\[
V=\{0,1,2,3\},
\]

one uninformative observation, admissible actions

\[
A(0)=A(1)=\{0\},
\qquad
A(2)=\{1\},
\qquad
A(3)=\{0,1\},
\]

and deterministic transitions

\[
0\to1,
\qquad
1\to3,
\qquad
2\to2,
\qquad
3\to2.
\]

Two action colors suffice: \(\{0,1,3\}\) can use action \(0\), while \(\{2\}\) uses action \(1\). Thus

\[
\chi_{\mathrm{act}}=2.
\]

No two-member closed cover exists. In particular, any two-state autonomous controller must place \(0\) and \(1\) together to leave a class capable of representing state \(2\). Under action \(0\), the implication from \(\{0,1\}\) is \(\{1,3\}\), which cannot be represented by either necessary two-class arrangement while preserving action compatibility.

A three-member closed cover is

\[
\{0\},\quad
\{1\},\quad
\{2,3\},
\]

with actions \(0,0,1\). Hence

\[
\boxed{
\chi_{\mathrm{act}}=2
<
N^*_{\mathrm{dyn}}=3.
}
\]

Exhaustive finite verification is frozen in `control_complexity_hierarchy_checks_v1.py` and `CONTROL_COMPLEXITY_HIERARCHY_RESULTS_V1.json`.

---

## 7. Donor ownership

The cover/closure mechanism is established theory for incompletely specified finite-state machines. Two direct references are:

- R. Puri and J. Gu, “An efficient algorithm to search for minimal closed covers in sequential machines,” *IEEE Transactions on Computer-Aided Design of Integrated Circuits and Systems* 12(6):737–745 (1993), DOI 10.1109/43.229748.
- I. Ahmad and A. Shoba Das, “A heuristic algorithm for the minimization of incompletely specified finite state machines,” *Computers & Electrical Engineering* 27(2):159–172 (2001), DOI 10.1016/S0045-7906(00)00016-1.

The second paper explicitly distinguishes cover and closure conditions and describes minimum closed cover as the state-minimization target; it also notes the NP-complete character of general ISFSM minimization.

The GMI-specific question is upstream and downstream of this donor theorem: can \((\Omega,\mathcal E)\) generate the residual compatibility machine without architecture assumptions, and can its minimum controller structure be combined with resource bounds and explicit constructions to certify physical morphology phases?

---

## 8. Complexity versus development

Three quantities remain distinct:

\[
\chi_{\mathrm{act}}(\varepsilon),
\qquad
N^*_{\mathrm{dyn}}(\varepsilon),
\qquad
C_{\mathrm{search}}(B).
\]

The first is a per-step information lower bound. The second is the minimum autonomous state count. The third is the cost of discovering or synthesizing a controller near that minimum.

A morphology theorem can close the first two and still leave development open. In particular, exact closed-cover optimization can itself be computationally hard; developmental reachability must therefore be analyzed separately rather than inferred from existence of a small controller.

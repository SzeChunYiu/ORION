# Prior-free GMI: rooted strategies and the control-complexity hierarchy

## 0. Why this repair is necessary

A control-compression theorem is invalid if a purportedly “common continuation policy” is still allowed to inspect the original history that the controller was supposed to forget.

Suppose histories \(h\) and \(h'\) are mapped to the same retained state. If a continuation object \(c\) is defined as a policy on **full global histories**, then one nominal \(c\) can contain separate branches for prefixes beginning with \(h\) and \(h'\). The intersection

\[
c\in\Gamma(h)\cap\Gamma(h')
\]

would then not imply that the two histories can genuinely share a state: the policy has smuggled their identity back in through its input.

The correct continuation object after a merge is a **rooted, prefix-blind strategy**. It may use observations and actions occurring after the merge point, together with explicitly declared common side information, but it may not inspect the forgotten pre-root prefix.

This note repairs that semantic leak and separates three control-complexity quantities that had previously been compressed into one notion of “state information”.

---

## 1. Rooted continuation strategies

Fix a root history \(h_t\). Re-index time so that the decision immediately after the root has local time \(0\).

A rooted suffix before the local action at time \(k\) is

\[
\sigma_k
=
(a^+_0,o^+_1,a^+_1,o^+_2,\ldots,a^+_{k-1},o^+_k),
\]

with \(\sigma_0=\varnothing\). The superscript \(+\) denotes post-root variables only.

A **rooted continuation strategy** is a causal family

\[
\kappa_k(da^+_k\mid \sigma_k,s),
\]

where \(s\) is explicitly declared side information available on the downstream side of the merge/cut.

Crucially, \(\kappa\) has no argument containing \(h_t\) itself. The same rooted strategy applied after two different roots receives the same local coordinate system.

If the controller is allowed a clock, absolute timestamp, agent identity, retrieved record, or other side information, that variable must appear explicitly in \(s\). It may not be hidden inside the definition of a continuation policy.

### Rooted evaluation

Write

\[
\operatorname{Eval}^+_\Omega(h,e,\kappa;s)
\]

for the obligation-relevant law/loss obtained by splicing rooted strategy \(\kappa\) after history \(h\) in structural environment \(e\).

The predictive residual profile should therefore be read as

\[
\mathsf Q_h(e,\kappa;s)
=
\operatorname{Eval}^+_\Omega(h,e,\kappa;s),
\]

with \(\kappa\) prefix-blind.

This is the intended semantics for the predictive quotient and every control-feasibility intersection in the formal core.

---

## 2. Plan feasibility

For robust loss \(L_\Omega(h,\kappa;s)\), define

\[
\Gamma^{\mathrm{plan}}_\varepsilon(h;s)
=
\{\kappa:
L_\Omega(h,\kappa;s)\le\varepsilon\}.
\]

A set \(B\) of root histories is **plan-compatible** when

\[
\bigcap_{h\in B}
\Gamma^{\mathrm{plan}}_\varepsilon(h;s)
\ne\varnothing.
\]

The corresponding conflict hypergraph contains exactly the sets for which no single prefix-blind future strategy can meet the tolerance from every root.

Let

\[
\chi_{\mathrm{plan}}(\varepsilon;s)
\]

be its chromatic number.

### Operational meaning

\(\chi_{\mathrm{plan}}\) is the minimum alphabet size for a **one-time root encoder** that sees the full root history, sends one label, and hands control to a decoder capable of executing an arbitrary rooted strategy associated with that label. The internal memory/computation needed to execute the strategy is not measured by the label count.

Thus

\[
I_{\mathrm{plan}}
=
\log_2\chi_{\mathrm{plan}}
\]

is a communication/selection complexity, not total autonomous controller memory.

---

## 3. Immediate-action compatibility

For a finite Markov residual control specification \(V\), let

\[
A_\varepsilon(v)
\]

be the set of actions admissible now at residual state \(v\).

A set \(B\subseteq V\) is **action-compatible** when

\[
\bigcap_{v\in B}A_\varepsilon(v)
\ne\varnothing.
\]

Let

\[
\chi_{\mathrm{act}}(\varepsilon)
\]

be the chromatic number of the immediate-action conflict hypergraph.

### Operational meaning

\(\chi_{\mathrm{act}}\) is the minimum alphabet size for an omniscient encoder that is allowed to inspect the true residual state **again at every control step** and send only enough information to select the current action. Future memory is externalized to the encoder.

This is a different architecture from a one-time plan encoder and a different resource model from an autonomous controller.

---

## 4. Autonomous dynamic state complexity

For the same finite residual control specification, let

\[
N^*_{\mathrm{dyn}}(\varepsilon)
\]

be the minimum number of reachable internal states of a clock-free autonomous deterministic controller satisfying the tolerance, with no external state oracle after initialization except the declared observation stream and side information.

By the closed-cover theorem in `DYNAMIC_CONTROLLER_CLOSED_COVER_V1.md`,

\[
N^*_{\mathrm{dyn}}(\varepsilon)
=
\min_{\mathcal K\ \mathrm{closed}}
|\mathcal K|.
\]

---

## 5. Hierarchy theorem

### Theorem 5.1

For a finite residual specification under aligned tolerance and side-information semantics,

\[
\boxed{
\chi_{\mathrm{act}}(\varepsilon)
\le
\chi_{\mathrm{plan}}(\varepsilon)
\le
N^*_{\mathrm{dyn}}(\varepsilon).
}
\]

#### First inequality

If a set of residual states admits one common rooted continuation strategy, then the first action selected by that strategy is admissible for every state in the set. Every plan-compatible color class is therefore action-compatible. Minimizing over colorings gives

\[
\chi_{\mathrm{act}}
\le
\chi_{\mathrm{plan}}.
\]

#### Second inequality

Take any autonomous controller with \(N\) reachable states. For each controller state \(z\), collect every residual situation that can coexist with \(z\). Starting from \(z\), the controller induces one prefix-blind rooted strategy as a function of future observations and its own subsequent state transitions. Hence that set of residual situations is plan-compatible.

These \(N\) sets cover the reachable residual situations. Since plan-compatibility is hereditary under subsets, assign each residual situation to one containing controller-state set; this yields a proper plan coloring with at most \(N\) colors. Therefore

\[
\chi_{\mathrm{plan}}
\le N.
\]

Minimize over autonomous controllers. \(\square\)

---

## 6. Strictness I: per-step action information can understate plan information

Consider three residual states

\[
V=\{x,y,z\}
\]

with one uninformative observation symbol \(*\). The exact admissible actions are

\[
A(x)=A(y)=\{0\},
\qquad
A(z)=\{1\}.
\]

Transitions are

\[
x\to x,
\qquad
y\to z,
\qquad z\to x.
\]

### Immediate-action complexity

\(x\) and \(y\) are action-compatible and \(z\) is incompatible with both, so

\[
\chi_{\mathrm{act}}=2.
\]

An external encoder that sees the residual state every step can send one bit: “use action 0” versus “use action 1”.

### Plan complexity

No two distinct states share one rooted continuation plan:

- \(x\) requires action sequence \(0,0,0,\ldots\);
- \(y\) requires \(0,1,0,0,\ldots\);
- \(z\) requires \(1,0,0,\ldots\).

Because the observation is always \(*\), the decoder cannot distinguish these trajectories after receiving the root label. Therefore

\[
\chi_{\mathrm{plan}}=3.
\]

The three-state residual machine itself is an autonomous realization, so

\[
N^*_{\mathrm{dyn}}=3.
\]

Hence

\[
\boxed{2=\chi_{\mathrm{act}}<\chi_{\mathrm{plan}}=N^*_{\mathrm{dyn}}=3.}
\]

---

## 7. Strictness II: one-time plan information can understate autonomous state

Consider four residual states

\[
V=\{0,1,2,3\}
\]

with the same uninformative observation \(*\). Admissible actions are

\[
A(0)=A(1)=\{0\},
\qquad
A(2)=\{1\},
\qquad
A(3)=\{0,1\}.
\]

Transitions are

\[
0\to1,
\qquad
1\to3,
\qquad
2\to2,
\qquad
3\to2.
\]

### Two rooted plans suffice

The class \(\{0,1\}\) shares the open-loop rooted plan

\[
0,0,1,1,1,\ldots
\]

because

\[
\{0,1\}
\to
\{1,3\}
\to
\{3,2\}
\to
\{2\}.
\]

The class \(\{2,3\}\) shares

\[
1,1,1,\ldots.
\]

No one plan can cover all four because state \(0\) requires first action \(0\) and state \(2\) requires first action \(1\). Therefore

\[
\chi_{\mathrm{plan}}=2.
\]

Immediate action compatibility also gives

\[
\chi_{\mathrm{act}}=2.
\]

### Two autonomous states do not suffice

Any two-state cover must separate state \(2\) from states \(0,1\), because their required current actions conflict. To cover \(0\) and \(1\) with the remaining state, that controller state must represent \(\{0,1\}\) and output \(0\).

After the common observation \(*\), the actual residual can be \(1\) (if the previous residual was \(0\)) or \(3\) (if it was \(1\)). The controller receives the same observation from the same internal state and therefore must enter the same next internal state in both cases. But no two-state compatible cover has a class containing both \(1\) and \(3\) while also covering state \(2\) consistently; exhaustive closed-cover evaluation gives a minimum of three states.

A three-state closed cover is

\[
\{0\},
\quad
\{1\},
\quad
\{2,3\},
\]

with outputs \(0,0,1\), respectively. Its successor implications are

\[
\{0\}\to\{1\},
\qquad
\{1\}\to\{2,3\},
\qquad
\{2,3\}\to\{2,3\}.
\]

Thus

\[
\boxed{
\chi_{\mathrm{act}}
=
\chi_{\mathrm{plan}}
=2
<
N^*_{\mathrm{dyn}}
=3.
}
\]

The missing resource in the two-label plan description is the internal phase/memory required to execute the plan after the one-time label is received.

---

## 8. Consequence for GMI morphology

There is no single architecture-independent scalar called “the information required by the task”. At least three distinct resource questions exist:

\[
\begin{array}{rcl}
I_{\mathrm{act}}&=&\log_2\chi_{\mathrm{act}},\\[1mm]
I_{\mathrm{plan}}&=&\log_2\chi_{\mathrm{plan}},\\[1mm]
M_{\mathrm{dyn}}&=&\log_2N^*_{\mathrm{dyn}}
\quad\text{(fixed-length state lower envelope).}
\end{array}
\]

They correspond to different causal placements of information and computation:

- repeated external information supply;
- one-time plan selection with decoder-side plan memory/computation;
- autonomous persistent state.

A morphology theorem must declare which resources are inside the machine boundary. Otherwise the theory can “reduce memory” merely by moving it into an oracle, plan decoder, clock, retrieval service, or environment channel.

This is exactly why composition boundary R6 and resource-response R7 are load-bearing coordinates in the frozen reduction vocabulary.

---

## 9. Donor alignment

The dynamic inequality and closed-cover construction are aligned with classical incompletely specified FSM minimization, where compatibility alone does not solve state minimization and closure of implied successor sets is additionally required. The literature explicitly treats minimum closed cover as the state-reduction target and reports the general problem as NP-complete. citeturn776165search0

The predictive side remains aligned with residual/right-congruence theory: in the fully specified deterministic-language setting, Myhill--Nerode gives a coarsest right congruence and a unique minimal DFA. citeturn776165search1turn776165search44

The present control setting is more general because obligations may be incomplete: several actions can all be acceptable, so compatible residuals need not form equivalence classes. That is exactly the regime in which closed covers rather than unique quotients arise.

---

## 10. Formal-core correction

Every occurrence of “continuation policy” in a state-merging or cut theorem should henceforth mean a rooted prefix-blind strategy unless the forgotten root history is explicitly declared as downstream side information.

`FORMAL_CORE_V2.md` and `CONTROL_INFORMATION_PROFILE_V1.md` should be read with this correction. A consolidated v3 should incorporate it directly and distinguish \(\chi_{\mathrm{act}}\), \(\chi_{\mathrm{plan}}\), and \(N^*_{\mathrm{dyn}}\) in its main theorem package.

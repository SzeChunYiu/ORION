# P2 V11: safe residual envelopes around a strong donor

## 1. Scope and design choice

This packet asks a theory question, not another empirical one: what is the
widest positive statement justified after the V8 and V10 title-residual
failures? Three routes were available.

1. A scalar objective could combine early recall and work saving. This is
   rejected because it would let a sufficiently large gain purchase a failure
   of a coprimary or harm gate.
2. A Bayesian transport model could pool review families. This might be useful
   later, but it would make the result depend on new exchangeability and prior
   assumptions not established by V8 or V10.
3. A **guarded residual envelope** can embed the exact donor, admit a residual
   only through the registered conjunction, and state precisely what new
   information is needed to separate from a donor-complete class. This is the
   chosen route because it is both wider and more conservative: it covers any
   residual mechanism and any simultaneous uncertainty construction without
   declaring an unobserved performance win.

The positive result is therefore conditional and structural. A fail-closed
envelope can preserve the donor while admitting a residual exactly when a
noncompensatory certificate is valid. Finite residual failures do not imply
universal donor optimality. Strict same-contract separation from a
donor-complete frontier requires non-simulable information or retained state,
new acquisition support, or proof that the donor class was incomplete;
otherwise the candidate is already donor territory. Changing the cost, access,
world, or authority contract changes the comparison and cannot establish
dominance under the original contract.

## 2. Finite-family admission geometry

Fix a source-bound family (F=(w_1,\ldots,w_n)), the exact donor (d), and a
predeclared residual controller (e_r). For review (i), write

\[
 x_i(r)=(c_i,q_i,s_i,a_i),
\]

where (c_i) is controller-minus-donor CRE20, (q_i) is controller-minus-donor
R@10, (s_i) is controller-minus-donor WSS95, and (a_i) is the controller's
absolute WSS95. Let the frozen gate registry be

\[
 \eta=(\tau_C,\tau_R,k,h)
\]

with mean margins \(\tau_C,\tau_R\), positive-sign requirement \(k\), and
worst-review harm allowance \(h\ge 0\). Define the finite-family admission set

\[
\begin{aligned}
 \mathcal K_\eta(F)=\{x:\;&\bar c\ge\tau_C,
 \quad\bar q\ge\tau_R,
 \quad\bar s\ge0,\\
 &\sum_i\mathbf1\{c_i>0\}\ge k,
 \quad\sum_i\mathbf1\{q_i>0\}\ge k,\\
 &\min_i q_i\ge-h,
 \quad\min_i a_i>0\}.
\end{aligned}
\]

Source, population, implementation and custody predicates are separate binary
guards (B_F). An unbound guard is not a pass. The exact finite-family rule is

\[
 \operatorname{Admit}_F(r)=B_F\,\mathbf1\{x(r)\in\mathcal K_\eta(F)\}.
\]

For V10, \(n=7\), \(k=6\),
\(\tau_C=\tau_R=0.010858985820770889\), and \(h=0.05\).

### Theorem 1 (exact noncompensatory admission)

Assume the family, units, metrics, donor, residual, gate registry and all
bindings were fixed before the controller outcomes, and assume every reported
metric is exact for that finite family. Then a residual is admissible under the
registered contract if and only if (B_F=1) and
(x(r)\in\mathcal K_\eta(F)). No improvement in one coordinate can repair a
failed inequality in another.

**Proof.** The registered contract is the conjunction displayed in the
definition of \(\mathcal K_\eta(F)\), together with \(B_F\). Membership is
therefore sufficient. If membership or binding fails, at least one registered
necessary clause is false, so admission is unsound under that contract. The
last statement follows because conjunction does not aggregate failed clauses.
\(\square\)

This theorem is intentionally about the declared finite family. It does not
turn seven public review decisions into a population law, independent custody,
or a universal screening theorem.

### Theorem 2 (simultaneous robust admission)

Let \(\theta\) denote the target-family gate vector and let
\(C_{1-\alpha}(X)\) be a confidence set satisfying

\[
 \Pr_\theta\{\theta\in C_{1-\alpha}(X)\}\ge1-\alpha
\]

simultaneously for the predeclared residual, endpoints, review units and
selection procedure. Admit only when every point in the confidence set lies in
the target admission region: (C_{1-\alpha}(X)\subseteq\mathcal K_\eta\), and
all nonnumeric bindings pass. Then

\[
 \Pr\{\operatorname{Admit}=1\text{ and }\theta\notin\mathcal K_\eta\}
 \le\alpha.
\]

**Proof.** If admission occurs while \(\theta\notin\mathcal K_\eta\), the
declared confidence set cannot both contain \(\theta\) and be a subset of
\(\mathcal K_\eta\). The false-admission event is therefore contained in the
simultaneous noncoverage event, whose probability is at most \(\alpha\).
\(\square\)

The simultaneity assumption is material. Pointwise intervals computed after
residual selection do not satisfy the premise. Nor does same-workspace replay
establish independent confirmation.

## 3. Conservative donor embedding

Let \(\Pi_D\) be the admissible donor policy class and let (d\in\Pi_D) be the
exact u4 donor. For any residual proposal (r), define the certificate-switched
policy

\[
 \pi_r^{\rm env}=
 \begin{cases}
 e_r,&\operatorname{Admit}_F(r)=1,\\
 d,&\operatorname{Admit}_F(r)=0.
 \end{cases}
\]

The switch is frozen before deployment outcomes. A missing population, source,
or certificate selects (d), not an estimated residual.

### Theorem 3 (safe-residual envelope embedding)

Let

\[
 \Pi_{\rm env}=\Pi_D\cup\{\pi_r^{\rm env}:r\in\mathcal R\}.
\]

Under an identical task, access, budget and authority contract:

1. the donor attainable set is contained in the residual-envelope attainable
   set;
2. every rejected or unbound residual executes the exact donor;
3. on the joint-coverage event of Theorem 2, every admitted residual satisfies
   all registered target gates simultaneously.

**Proof.** Item 1 follows from \(\Pi_D\subseteq\Pi_{\rm env}\). Item 2 is the
definition of the switch. For item 3, joint coverage plus the subset condition
places the true gate vector inside \(\mathcal K_\eta\). \(\square\)

This is the widest positive result authorized by V8/V10: a sound architecture
for conditional admission can preserve the strong donor. It is **not** a claim
that title emphasis is beneficial, that an admitted controller dominates on
every review, or that a finite certificate transports without the premises of
Theorem 2. Implementation mistakes, selection leakage, mutable gates or a
nonexact fallback invalidate the theorem's application.

### Proposition 3.1 (ordinary scalarization cannot replace the gates)

On an unbounded or range-unregistered metric domain, no finite weighted linear
score with ordinary compensability is both sound and complete for
\(\mathcal K_\eta(F)\).

**Proof.** If every gated coordinate has positive finite weight, lower one
coordinate just below its required threshold and increase another coordinate
without bound. The linear score eventually exceeds any finite acceptance
threshold although the conjunction still fails. If a gated coordinate has
zero weight, vary that coordinate across its gate while holding all scored
coordinates fixed; the score cannot distinguish pass from fail. Sign-count,
worst-review and absolute-work-saving clauses create the same obstruction.
Only explicit conjunction, an equivalent lexicographic/infinite-penalty rule,
or additional registered range restrictions avoids it. \(\square\)

V10 is a concrete instance: mean WSS95, worst-review harm and absolute WSS95
passed, but those gains cannot purchase the failed CRE20/R@10 magnitude and
sign gates.

## 4. What V8 and V10 do—and do not—identify

V8 showed that two cross-fitted residual activations harmed their held-out
reviews and that the cross-fitted CRE20, WSS95 and harm checks failed. V10 then
tested one frozen source-disjoint title-emphasis residual. Its mean deltas were

\[
 (\Delta\mathrm{CRE20},\Delta R@10,\Delta\mathrm{WSS95})
 =(0.000779992745,-0.005382681125,0.001765466550),
\]

with positive signs in (4/7) and (1/7) reviews. The title residual is
therefore outside \(\mathcal K_\eta\) and is discarded. These are valid
finite-family statements.

### Theorem 4 (finite failure does not identify universal donor optimality)

Let \(O\subsetneq\mathcal W\) be any finite observed set of review worlds and
let the observed donor/residual metric differences on (O) be arbitrary.
Unless a declared cross-world restriction determines differences on
\(\mathcal W\setminus O\), there exist two extensions agreeing on every
observation in (O):

1. an extension in which the residual fails the admission contract on a new
   family; and
2. an extension in which the same residual passes every gate on a new family.

Consequently, finite failures alone imply neither universal u4 optimality nor
future residual success.

**Proof.** Preserve all observed values on (O). Choose seven unobserved worlds.
For the first extension assign residual differences below at least one gate. For
the second assign, in every new world,

\[
 c_i=\tau_C+\epsilon,
 \quad q_i=\tau_R+\epsilon,
 \quad s_i=\epsilon,
 \quad a_i>0
\]

for any \(\epsilon>0\). All magnitude, sign, harm and absolute-work-saving
gates then pass on the new family. Both extensions agree on (O), so the
observations cannot distinguish them. \(\square\)

An exchangeability model, support-completeness claim, smoothness restriction,
causal invariance assumption, or exhaustive world census could constrain these
extensions. None is supplied by V8/V10. The theorem is not evidence that a
positive family exists; it is a non-identification result blocking an
overclaim of universal u4 optimality.

## 5. Separation from a donor-complete class

The exact u4 algorithm is one strong donor. A donor-complete class is a wider
object. Let (s_D(w)) be all information and retained state available to that
class in world (w), and let \(\mathcal A_D(w)\) be its admissible action and
acquisition support under the matched budget. Call \(\Pi_D\) **saturated** when
it contains every allowed policy that is measurable from (s_D), uses only
\(\mathcal A_D\), and satisfies the same cost and authority contract.

### Theorem 5 (donor-fibre embedding/separation)

Suppose a candidate (c):

1. uses no action outside \(\mathcal A_D\);
2. has no cheaper or larger resource contract;
3. has an action/ordering decision constant on every fibre of (s_D); and
4. is evaluated under the same authority guards.

If \(\Pi_D\) is saturated, then (c\in\Pi_D). Hence (c) cannot establish a
strict improvement outside the donor-complete acquisition--authority envelope.
Conversely, a valid strict same-contract outside-envelope separation entails at
least one of:

- a signal or retained state that separates a mixed donor fibre;
- an acquisition action or reachable evidence identity outside donor support;
- proof that the declared donor class was not saturated.

A different cost, access, world, or authority contract may establish class
non-membership, but it invalidates the original dominance comparison by
changing its feasible set or estimand. It is not a separation mechanism for a
same-contract dominance claim; it requires a newly defined and validated
comparison.

**Proof.** Fibre constancy gives a factorization (c=g\circ s_D): define

\(g(z)\) using any world in the fibre, which is well-defined by constancy. The
action-support, cost and guard premises make this a policy admitted by the
saturated class, so (c\in\Pi_D\). The same-contract separation statement is
the contrapositive. A contract mismatch instead violates the comparison
premises and therefore proves no dominance under the original contract.
\(\square\)

This theorem must not be misread as saying that new raw information is
logically necessary to beat the single u4 implementation. A better learner can
use the same information if u4 is not conditionally Pareto-efficient. It says
that same-information improvement is already donor territory once the
comparison class is saturated. Beating one donor implementation and separating
from a donor-complete frontier are different claims.

### Corollary 5.1 (deterministic title emphasis adds no information)

Duplicating the title in a title--abstract string is a deterministic transform
of the donor's existing fields. It cannot separate worlds that are identical
on those fields and does not expand the acquisition support. It can only exploit
a possible algorithmic inefficiency of a particular representation/learner.
V10 rejects that one frozen transform on its seven-review contract; it neither
proves u4 optimality nor tests a genuinely new information channel.

### Proposition 5.2 (acquisition support is upstream of residual ranking)

For a fixed run and gold set, a downstream residual that only reorders the
donor-acquired pool cannot increase the run-conditional acquisition ceiling.
Strict acquisition-ceiling improvement requires at least one newly acquired
decision-relevant identity, or evidence that the alleged donor-complete class
omitted an admissible acquisition policy that could reach it.

**Proof.** Reordering leaves the acquired identity union unchanged. The
submitted relevant set remains a subset of that union, so the acquisition
ceiling is unchanged. The final statement follows by contraposition. \(\square\)

## 6. The genuinely new discriminator

The theory rules out another unfocused representation grid. To claim a residual
above the strong u4 donor, a successor must predeclare one of two distinct
mechanisms.

### A. Same-information efficiency separation

The successor asserts that u4 is not Pareto-efficient even with the same
title--abstract pool. It must freeze one mechanism, retain exact u4, and clear
the entire CRE20/R@10/WSS95/sign/harm/absolute-work-saving conjunction on a
source-disjoint family with simultaneous inference. A positive result is still
algorithm-specific, not new-information or acquisition superiority.

### B. Non-simulable information or acquisition separation

Before outcomes, the successor must bind:

1. a lawful signal, route, field, feedback event or retained state unavailable
   to the donor;
2. a **non-simulation witness**—two possible task states tied under donor state
   but separated by the new coordinate—or a route-support witness showing a
   new reachable evidence identity class;
3. a component factorization holding the u4 learner/balancer fixed, so the new
   information effect is not confused with learner replacement;
4. matched fully charged exposure, source identity, content, provider,
   population and custody contracts; and
5. the unchanged noncompensatory gate certificate against exact u4.

For open-world acquisition, item 2 must concern candidate-pool expansion, not
merely a different score over the same pool. For fixed-pool screening, it may be
a new decision-relevant signal that refines donor fibres. If no such signal or
support difference is bound, Theorem 5 classifies the proposal as a donor-side
algorithmic variant rather than an upward theory separation.

## 7. Explicit boundaries

- Theorems 1 and 3 are conditional on exact binding, immutable gates and an
  exact donor fallback.
- Theorem 2 requires a genuinely simultaneous uncertainty procedure covering
  selection and all endpoints; V8/V10 point estimates do not supply it.
- Theorem 4 is a non-identification theorem, not evidence of a positive unseen
  family.
- Theorem 5 concerns a saturated donor-complete class. It does not declare the
  single u4 implementation Bayes-optimal or universally optimal.
- A cost/access/world/authority contract mismatch invalidates the original
  dominance comparison; it is not evidence of same-contract separation.
- No theorem converts public same-workspace development into independent or
  protected confirmation.
- No result authorizes source-general, domain-general, workflow-general,
  application-exact, acquisition-superiority, or ORION-specific claims.

## Terminal

`P2_V11_SAFE_RESIDUAL_ENVELOPE_AND_DONOR_FIBRE_SEPARATION_PROVED__FINITE_V8_V10_FAILURES_DO_NOT_IDENTIFY_UNIVERSAL_U4_OPTIMALITY__NEW_INFORMATION_OR_UNSATURATED_DONOR_CLASS_REQUIRED_FOR_STRICT_ASCENT`

# Finite-information interface theorem spine V1

**Status:** programme-level derivation and regression target.  
**Scientific authority delta:** `NONE`.  
**Novelty status:** `NOT_ASSESSED`.  
**Paper-promotion authority:** none.

This packet makes one mathematical object explicit across several ORION papers: a
method is forced to use the same action on states that its information interface
cannot distinguish.  The consequences include irreducible decision regret,
mixed-fibre classification error, scalar certificate-width floors, and
invariant-orbit error floors.

The purpose is not to rename these consequences as a new contribution.  It is to
give ORION-02/08/09/10/13/19/22 one shared theorem spine, expose exactly which
parts are generic, and reserve paper-specific novelty for the mechanism,
constructive refinement, domain transfer, or consequence that remains after
donor subtraction.

## 1. Setup

Let:

- \(X\) be a finite state set;
- \(A\) be a finite nonempty action set;
- \(w_x>0\) be a weight for each \(x\in X\);
- \(\ell(x,a)\in\mathbb{R}\) be the loss of action \(a\) at state \(x\);
- \(\phi:X\to Z\) be an observation map.

The fibres of \(\phi\) form a partition \(\Pi_\phi\) of \(X\).  A deterministic
\(\phi\)-measurable policy is a function \(\pi:Z\to A\); equivalently, it chooses
one action per fibre.  Define

\[
R_\phi
  = \min_{\pi:Z\to A}\sum_{x\in X}w_x\ell(x,\pi(\phi(x)))
\]

and the full-information oracle risk

\[
R_\star
  = \sum_{x\in X} w_x \min_{a\in A}\ell(x,a).
\]

The information-interface regret is \(\Delta_\phi=R_\phi-R_\star\).

All results below are finite and exact.  Probability distributions are obtained
by normalising the positive weights; normalisation rescales every risk and does
not change any zero/nonzero conclusion.

## 2. T1 — exact partition-risk formula

For every finite problem,

\[
R_\phi
 = \sum_{F\in\Pi_\phi}
     \min_{a\in A}\sum_{x\in F}w_x\ell(x,a).
\]

### Proof

A \(\phi\)-measurable policy makes an independent action choice for each fibre.
The total objective is the sum of the fibre objectives, and no decision variable
is shared by two distinct fibres.  Minimising the separable sum therefore equals
the sum of the fibre minima.  \(\square\)

This formula is the correct information-matched baseline.  Two algorithms with
the same fibres, action set, weights, and loss surface share the same achievable
population optimum \(R_\phi\).  A claimed difference between them must come from
optimisation, estimation, approximation, finite-sample effects, or an
unacknowledged difference in information/action/budget—not from the partition
alone.

## 3. T2 — zero regret iff every fibre has a common optimum

For a state \(x\), write

\[
A^\star(x)=\arg\min_{a\in A}\ell(x,a).
\]

Then

\[
\Delta_\phi=0
\quad\Longleftrightarrow\quad
\bigcap_{x\in F}A^\star(x)\ne\varnothing
\quad\text{for every }F\in\Pi_\phi.
\]

### Proof

Subtract the full-information risk from the T1 expression.  The contribution of
a fibre \(F\) is

\[
\delta(F)
  = \min_{a\in A}
      \sum_{x\in F}w_x
      \bigl(\ell(x,a)-\min_b\ell(x,b)\bigr).
\]

Every summand is nonnegative and every weight is positive, so
\(\delta(F)=0\) exactly when one action makes every summand zero—exactly when
that action belongs to every \(A^\star(x)\) in the fibre.  Since
\(\Delta_\phi=\sum_F\delta(F)\), the result follows.  \(\square\)

This is stronger than saying that the majority-optimal action is usually right.
One empty common-optimum intersection gives a strictly positive information
floor under the declared loss.

## 4. T3 — refinement monotonicity and exact value of information

Let \(\psi\) refine \(\phi\): every \(\psi\)-fibre is contained in a
\(\phi\)-fibre.  Then

\[
R_\psi\le R_\phi,
\qquad
V(\psi;\phi)=R_\phi-R_\psi\ge 0.
\]

More exactly,

\[
V(\psi;\phi)
 = \sum_{F\in\Pi_\phi}
   \left[
     \min_a\sum_{x\in F}w_x\ell(x,a)
     -
     \sum_{\substack{G\in\Pi_\psi\\G\subseteq F}}
       \min_a\sum_{x\in G}w_x\ell(x,a)
   \right].
\]

### Proof

Any \(\phi\)-measurable policy is also \(\psi\)-measurable, so refinement cannot
raise the minimum.  Applying T1 to the coarse and refined partitions gives the
displayed decomposition.  Each bracket is nonnegative because independently
minimising the child fibres cannot be worse than forcing them to share one
action.  \(\square\)

For a coarse fibre \(F\), equality holds exactly when at least one action
simultaneously minimises every refined-child aggregate loss
\(\sum_{x\in G}w_x\ell(x,a)\).  Thus a refinement has zero value for a precise
reason; extra state is not automatically useful.

## 5. T4 — local pair witnesses lower-bound the global regret

If states \(x,y\) occupy the same \(\phi\)-fibre, define

\[
b(x,y)=\min_{a\in A}
\left[
w_x\bigl(\ell(x,a)-\min_c\ell(x,c)\bigr)
+
w_y\bigl(\ell(y,a)-\min_c\ell(y,c)\bigr)
\right].
\]

Then \(\Delta_\phi\ge b(x,y)\).  In particular, if
\(A^\star(x)\cap A^\star(y)=\varnothing\), then \(b(x,y)>0\).

### Proof

The exact regret contribution of the containing fibre minimises the same
nonnegative expression with additional nonnegative state terms.  Dropping those
terms can only reduce the minimum.  Strict positivity follows from finiteness,
positive weights, and the absence of an action that zeros both terms.
\(\square\)

This supplies a minimal falsification witness: a single same-fibre pair with
incompatible optima is enough to refute a zero-regret claim.

## 6. T5 — exact mixed-fibre formula for 0–1 decisions

Let each state carry label \(y_x\in\mathcal{Y}\), let \(A=\mathcal{Y}\), and use
0–1 loss.  For a fibre \(F\), write

\[
W_F=\sum_{x\in F}w_x,
\qquad
W_{F,c}=\sum_{\substack{x\in F\\y_x=c}}w_x.
\]

Then full-information risk is zero and

\[
\Delta_\phi
 = \sum_{F\in\Pi_\phi}
   \left(W_F-\max_{c\in\mathcal{Y}}W_{F,c}\right).
\]

### Proof

On one fibre, predicting class \(c\) incurs exactly the weight outside class
\(c\).  Choosing the best class keeps the largest class weight and loses the
remainder.  Sum over fibres using T1.  \(\square\)

Consequences:

1. a fibre is zero-error exactly when it is label-pure;
2. class imbalance can make a mixed fibre look accurate while leaving a
   nonzero information floor;
3. the correct unit is weighted minority mass, not merely the number of mixed
   fibres.

## 7. T6 — scalar point and interval certificate floors

Let \(v:X\to\mathbb{R}\), and require one scalar point certificate \(t_F\) for
each fibre.  Under worst-case absolute error,

\[
\min_{t_F}\max_{x\in F}|v(x)-t_F|
 = \frac{\operatorname{diam}v(F)}{2},
\]

attained at the midrange
\((\min_{x\in F}v(x)+\max_{x\in F}v(x))/2\).

Likewise, the minimum width of one interval that contains every \(v(x)\) in the
fibre is exactly \(\operatorname{diam}v(F)\).

### Proof

Any point \(t\) is at distances \(t-\min v(F)\) and
\(\max v(F)-t\) from the two extremes.  Their maximum is at least half their
sum, namely the half-diameter.  The midrange attains equality.  Any covering
interval must contain both extremes and therefore has at least the diameter;
the interval from the minimum to the maximum attains it.  \(\square\)

Thus a point certificate constant on an unresolved fibre cannot have a uniform
error smaller than half the fibre diameter, and an interval narrower than the
diameter cannot cover both endpoints.  A constructive positive result must
refine the fibre, abstain, widen the certificate, or add assumptions.

## 8. T7 — randomisation cannot beat the partition optimum

Allow a policy to select, on each fibre, a distribution over actions and score
expected loss.  Its fibre risk is a linear function of that distribution.
A linear objective over a simplex attains a minimum at a vertex, so a
deterministic action achieves the same optimum \(R_\phi\).

Randomisation can matter under a different objective—fairness constraints,
adversarial timing, exploration, or nonlinear risk—but not for the finite
expected-loss problem defined here.

## 9. T8 — invariant-representation corollary

Suppose a group \(G\) acts on \(X\), and the representation is invariant:
\(\phi(gx)=\phi(x)\) for all \(g\in G\).  Every group orbit therefore lies
inside one \(\phi\)-fibre.  T1–T5 apply to the induced orbit coarsening.

For 0–1 labels, any orbit containing conflicting labels contributes at least
its weighted minority mass unless the representation further separates those
states.  Calling a representation “invariant” does not remove this floor; it
identifies the states that generate it.

## 10. What this does and does not close

### Generic logic now shared

- **ORION-02:** T6 supplies the generic diameter/certificate boundary.
- **ORION-08:** T1–T3 supply the exact binding-sufficiency and value-of-state
  baseline.
- **ORION-09:** T2/T4/T5 identify a mixed-regime fibre as a falsification
  witness; paper-specific work must explain size transfer.
- **ORION-10:** T2/T4 separate exact prediction from an insufficient
  explanation vocabulary.
- **ORION-13:** T3/T5 formalise why a polarity-only reduct can confound
  coordinate-necessity claims.
- **ORION-19:** T8 supplies the invariant-orbit floor that must be computed
  before a representation successor.
- **ORION-22:** T1–T3 give the exact finite regret/refinement law.

### Paper-specific gaps that remain

This packet does **not** establish novelty, practical importance, external
validity, source completeness, or any paper's top-tier promotion.  In
particular:

- a paper must subtract the strongest prior theorem before claiming novelty;
- constructive refinement costs and algorithms remain paper-specific;
- transfer claims need prospectively frozen external domains;
- causal or deployed-system claims need authoritative domain instrumentation;
- same-researcher reimplementations are not external investigators;
- adverse, null, contaminated, and `CANNOT_CHECK` outcomes remain controlling.

## 11. Independent finite regression

`check_theory.py` compares the formulas above with separate brute-force policy
enumerations using exact rational arithmetic.  Its committed `RESULT.json`
covers:

- 82,448 decision/partition instances;
- 295,696 ordered refinement checks;
- 147,712 pair lower-bound checks;
- 417,440 rational randomised-policy probes;
- 24,794 weighted 0–1 label/partition instances;
- 496,330 scalar fibre instances.

These bounded checks detect implementation or transcription errors.  They are
not a proof substitute; the proofs above carry the unrestricted finite claim.

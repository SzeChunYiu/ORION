# Verified Structural Transfer V1 — formalism

This formalism is deliberately an **internal solver-development layer**. It does not create a sixth flagship paper and it does not grant publication authority to analogies or local toy results.

## 1. Problem signature

Represent a problem by

\[
\Sigma(P)=(H,O,A,G,D,R,N,V),
\]

where:

- \(H\): hidden-state type;
- \(O\): observability regime;
- \(A\): admissible probes/actions;
- \(G\): ground-truth access/custody regime;
- \(D\in[0,1]\): dependence among observations/routes/views;
- \(R\in[0,1]\): authority/risk of a wrong action;
- \(N\in[0,1]\): non-stationarity;
- \(V\in[0,1]\): reversibility.

A retrieval score may combine structural similarity with a bonus for source-domain distance. **The score is never a transfer certificate.**

## 2. Algorithm cell

An imported mechanism is represented as

\[
C=(M,\mathcal A,\mathcal I,S,\mathcal F,\mathcal X),
\]

where \(M\) is the mechanism, \(\mathcal A\) assumptions, \(\mathcal I\) invariants, \(S\) stopping rule, \(\mathcal F\) failure modes, and \(\mathcal X\) falsifiers.

Transfer status is fail closed:

\[
T(C,P)=
\begin{cases}
\text{BLOCKED\_ASSUMPTION} & \exists a\in\mathcal A: a=\bot\\
\text{CANNOT\_CHECK} & \exists a\in\mathcal A: a=?\\
\text{OBSTRUCTED} & \exists x\in\mathcal X: x=\bot\\
\text{CANNOT\_CHECK} & \exists x\in\mathcal X: x=?\\
\text{ADMISSIBLE} & \text{otherwise.}
\end{cases}
\]

**Non-bypass proposition.** Retrieval score cannot override any branch above because score is computed only as metadata on the returned assessment; status is decided first by assumptions/falsifiers. This is mechanically tested.

## 3. Cross-confirmation

For analogy hypotheses likely to be accidental, require at least two admissible cells carrying the same mechanism from distinct source domains:

\[
|\{\operatorname{domain}(C_i): T(C_i,P)=\text{ADMISSIBLE}\}|\ge2.
\]

Multiple examples from one source domain do not count as independent cross-confirmation.

## 4. P1 — responsibility diagnosability

Let responsibility be a latent variable \(Z\in\{evidence,execution,representation,formulation,search\ universe,method,\ldots\}\). A probe \(q\) has outcome model \(p(y\mid Z,q)\).

Choose a probe by

\[
q^*=\arg\max_q I(Z;Y_q)-\lambda C(q)-\rho R(q).
\]

If \(I(Z;Y_q)=0\) for every admissible probe, responsibility is not diagnosable and the result is not a license to reframe.

A mutation class \(m\) is licensed only when the highest-posterior responsibility belongs to its allowed responsibility set and exceeds a frozen confidence threshold. Hence an evidence diagnosis cannot license a formulation rewrite.

## 5. P2 — conservative censored discovery allocation

Let the baseline route have declared per-step lower bound \(b>0\), and let \(\alpha\in(0,1)\) be tolerated degradation. Maintain

\[
B_t=L_t-(1-\alpha)bt\ge0,
\]

where \(L_t\) is the cumulative declared lower bound of actions taken so far.

A zero-floor exploratory action at \(t+1\) is allowed only if

\[
L_t\ge(1-\alpha)b(t+1).
\]

A baseline action with lower bound \(b\) earns \(\alpha b\) credit; a zero-floor exploratory action spends \((1-\alpha)b\). By induction, if every selected action satisfies the pre-action inequality, \(B_t\ge0\) for every committed state transition.

Provider unavailability is censored feedback: it increments a censoring count but does not add a zero reward observation to the route mean.

## 6. P3 — scientific lenses and obstruction

For a source/view pair, use a bidirectional map \(L=(get,put)\) satisfying round-trip conditions on the admitted domain. The prototype uses invertible affine maps solely as a known-answer substrate.

For a cycle \(S_0\to S_1\to\dots\to S_k=S_0\), define

\[
e(x)=\|L_{k-1,k}\circ\cdots\circ L_{0,1}(x)-x\|.
\]

If observed anchors have \(\max e(x)\le\epsilon\), the tested cycle is `GLOBALIZABLE`; if the error exceeds \(\epsilon\), it is `OBSTRUCTION`; with no anchors it is `CANNOT_CHECK`.

This is a consistency gate, not proof that all scientific meanings are globally mergeable.

## 7. P4 — defeater-directed evidence acquisition

Let unresolved defeater \(d\) have severity \(s_d\), and protected evidence action \(a\) have cost \(c_a\), probability \(p_a\) of resolving each addressed defeater, and addressed set \(D_a\).

A simple planning score is

\[
U(a)=\frac{p_a\sum_{d\in D_a}s_d}{c_a}.
\]

Only protected evidence actions are admissible in the prototype. The planner selects evidence acquisition but does **not** mutate authority. If a critical defeater has no protected resolving action, readiness is `CANNOT_CHECK`.

## 8. P5 — non-compensatory multi-stage candidate gate

Required stages are

\[
STATIC\rightarrow REPLAY\rightarrow FRESH\rightarrow PROTECTED.
\]

The terminal is

\[
\text{RECOMMEND\_HOST\_PROMOTION}
\iff
\bigwedge_s verdict(s)=PASS
\land
\bigwedge_s harmful(s)=false.
\]

Any stage `FAIL` or harmful result -> `REJECT`; any required `CANNOT_CHECK` -> `CANNOT_CHECK`; missing stage -> `IN_PROGRESS`.

Therefore arbitrarily large replay improvement cannot compensate fresh harm or missing protected evidence.

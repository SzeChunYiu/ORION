# Prior-free GMI: recovery of the one- and two-channel accuracy laws

## Status

This note derives the algebraic forms

\[
\operatorname{Acc}
\le
\frac12+\frac{r}{2L}
\]

and

\[
\operatorname{Acc}
\le
1-rac{(1-r/L)(1-p)}2
\]

from an architecture-free information-coverage model.

The derivation is self-contained. It does **not** assert, without replay, that the abstract model is identical to the exact registered ORION experiment that produced the same formulas. Binding each assumption below to the registered task semantics is a separate verification obligation.

The key conceptual point is that a stochastic law *inside one environment* is not a prior over environments. The derivation therefore remains compatible with the prior-free ecology programme.

---

## 1. Coverage environment

Fix \(L\ge1\). One episode contains:

1. a target location
   \[
   J\sim\operatorname{Unif}\{1,\ldots,L\};
   \]
2. a hidden target bit
   \[
   B\sim\operatorname{Bernoulli}(1/2),
   \]
   independent of \(J\);
3. an information interface from which a machine must predict \(B\).

Let \(H\) be the event that the primary information channel exposes the target information sufficiently to identify \(B\). The channel has coverage budget \(r\) in the sense that

\[
\Pr(H)\le\frac rL.
\]

This inequality is the actual structural assumption. It may arise because at most \(r\) of \(L\) target locations can be exposed, because a cut transmits at most \(r\) location-specific records, or by another task-specific coverage argument.

Assume additionally that on a primary miss the machine's complete view \(V\) contains no information about \(B\):

\[
B\perp V\mid H^c.
\]

Then no predictor can exceed chance accuracy on \(H^c\).

---

## 2. One-channel theorem

### Theorem 2.1

Under the assumptions above, every machine satisfies

\[
\Pr(\widehat B=B)
\le
\frac12+\frac{r}{2L}.
\]

#### Proof

Condition on the hit event:

\[
\Pr(\widehat B=B)
=
\Pr(H)\Pr(\widehat B=B\mid H)
+
\Pr(H^c)\Pr(\widehat B=B\mid H^c).
\]

Accuracy is at most one on \(H\). Conditional independence and the fair hidden bit give

\[
\Pr(\widehat B=B\mid H^c)\le\frac12.
\]

Therefore

\[
\Pr(\widehat B=B)
\le
\Pr(H)+\frac{1-\Pr(H)}2
=
\frac12+\frac{\Pr(H)}2
\le
\frac12+\frac{r}{2L}.
\]

\(\square\)

### Tightness

If the channel exposes exactly \(r\) uniformly possible target locations, reveals \(B\) perfectly on a hit, and provides no information on a miss, then a machine that answers correctly on hits and guesses on misses attains

\[
\frac12+\frac{r}{2L}.
\]

Thus the bound is exact for this coverage model.

---

## 3. Two-channel theorem

Add a secondary information event \(S\) available after a primary miss. Assume

\[
\Pr(S\mid H^c)\le p,
\qquad 0\le p\le1,
\]

and:

1. on \(H\), the target bit can be identified with accuracy at most one;
2. on \(H^c\cap S\), the secondary channel can identify the bit with accuracy at most one;
3. on \(H^c\cap S^c\), the entire machine view is independent of \(B\), so accuracy is at most \(1/2\).

### Theorem 3.1

Every machine satisfies

\[
\Pr(\widehat B=B)
\le
1-rac{(1-r/L)(1-p)}2.
\]

#### Proof

Condition on the three information cases:

\[
\Pr(\widehat B=B)
\le
\Pr(H)
+
\Pr(H^c\cap S)
+
\frac12\Pr(H^c\cap S^c).
\]

Since the three events partition the episode,

\[
\Pr(\widehat B=B)
\le
1-rac12\Pr(H^c\cap S^c).
\]

Using

\[
\Pr(H^c\cap S^c)
=
\Pr(H^c)\Pr(S^c\mid H^c)
\ge
\left(1-\frac rL\right)(1-p),
\]

we obtain

\[
\Pr(\widehat B=B)
\le
1-rac{(1-r/L)(1-p)}2.
\]

\(\square\)

### Tightness

Equality is attained when

\[
\Pr(H)=\frac rL,
\qquad
\Pr(S\mid H^c)=p,
\]

both channels reveal \(B\) perfectly on their success events, and the residual view on \(H^c\cap S^c\) is independent of the fair bit.

---

## 4. Why the theorem is architecture-independent

The proof refers only to:

- primary coverage probability;
- secondary conditional reveal probability;
- conditional independence of the hidden bit on the unresolved event.

It does not refer to recurrence, attention, state-space models, external memory, symbolic rules, program search, or any other implementation family.

Any machine respecting the same information interface obeys the same bound.

This is exactly the level at which an architecture-independent capability theorem should live.

---

## 5. Relation to the control-information profile

The control-information profile in `CONTROL_INFORMATION_PROFILE_V1.md` is a worst-case/pathwise object. The present theorem is an expected-accuracy result under a stochastic environment law.

These are distinct but compatible layers.

For each realized target location \(J=j\), the machine faces a local distinguishability requirement on \(B\). The primary channel resolves that requirement on at most an \(r/L\) fraction of the environment's target-location mass. On the unresolved mass, the secondary channel resolves at most a \(p\) fraction; on the remainder, the two hidden-bit states are indistinguishable and chance performance is optimal.

Thus the formulas can be read as an average over environment-internal information phases:

\[
\text{resolved}
\quad\text{versus}\quad
\text{unresolved/confounded}.
\]

No distribution over competing environments is required.

---

## 6. More general asymmetric form

The fair-bit/chance value \(1/2\) is not essential. Let the best accuracy on a fully unresolved case be \(q\in[0,1]\), and let primary and secondary success events permit accuracies at most \(a_1\) and \(a_2\). Then

\[
\operatorname{Acc}
\le
h a_1
+(1-h)s a_2
+(1-h)(1-s)q,
\]

where

\[
h=\Pr(H),
\qquad
s=\Pr(S\mid H^c).
\]

With bounds \(h\le r/L\), \(s\le p\), and \(a_1=a_2=1\), \(q=1/2\), Theorems 2.1 and 3.1 follow.

This form makes clear which coefficients are task/environment facts and which are universal algebra.

---

## 7. Multi-channel extension

Suppose sequential rescue channels \(S_1,\ldots,S_m\) act only if all previous channels failed, and channel \(i\) succeeds conditionally with probability at most \(p_i\). If every successful channel resolves the hidden bit perfectly and the final unresolved state is chance, then

\[
\operatorname{Acc}
\le
1-
\frac12
\left(1-\frac rL\right)
\prod_{i=1}^{m}(1-p_i).
\]

The proof is identical: only the probability of the final unresolved event matters.

This yields an immediate architecture-free family of channel-composition laws.

---

## 8. Failure conditions

The bound can fail if any registered assumption fails. In particular:

1. the primary channel can target locations using side information correlated with \(J\), invalidating \(\Pr(H)\le r/L\);
2. the miss event leaks information about \(B\), invalidating chance accuracy;
3. the secondary channel's success probability exceeds \(p\) conditionally on primary misses;
4. the task score is not ordinary prediction accuracy;
5. channels interact synergistically so that neither individually reveals the bit but their joint unresolved outputs do;
6. the target-location law is not uniform and \(r/L\) is used without replacing it by the appropriate coverage mass.

A theorem replay against the registered ORION task must check these conditions explicitly rather than matching only the final algebra.

---

## 9. Result

The one- and two-channel formulas are recovered from a minimal information-coverage model:

\[
\boxed{
\text{coverage}
+\text{residual independence}
\Longrightarrow
\text{capability law}
}
\]

This supports the GMI shift from named architecture prediction to channel/state/resource topology. The formula is invariant to the machine family because the proof is a statement about what information reaches the decision, not how the machine computes once it arrives.

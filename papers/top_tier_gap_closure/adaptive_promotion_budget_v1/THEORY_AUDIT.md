# Adaptive promotion-budget theorem audit V1

**Subject:** `research/self-orion/reusable-sealed-promotion-v1/THEORY.md`  
**Applies to:** ORION-15 and ORION-24  
**Disposition:** repairable statement gap; no empirical or promotion authority  
**Scientific authority delta:** `NONE`

## 1. Gap

The current theorem gives a per-round bound of the form

\[
\Pr(E_j) \le d_j=B_j u_j+\beta_j
\]

and then invokes a pathwise budget \(\sum_j d_j\le\alpha\) under arbitrary
adaptive candidate generation and data-dependent stopping. The proof does not
say whether the debit sequence is deterministic, or whether a history-dependent
debit is predictable and controls the **conditional** bad-promotion
probability. A scalar unconditional probability cannot simply be compared to a
random realized debit and then summed pathwise.

This is a statement-level gap, not evidence that the exact ledger software is
wrong. The software can enforce accounting rules, but the probability theorem
must state the premise those rules instantiate.

## 2. Two valid repairs

### Repair A — deterministic summable schedule

For a deterministic countable sequence \(d_j\ge0\), if every bad-promotion
event satisfies \(\Pr(E_j)\le d_j\) and \(\sum_j d_j\le\alpha\), then the ordinary
union bound gives \(\Pr(\cup_j E_j)\le\alpha\). Data-dependent stopping can be
represented by defining all future events as empty; it does not spend a random
post-outcome debit.

### Repair B — predictable conditional spending

Let \((\mathcal F_j)_{j\ge0}\) be the public transcript/ledger filtration. Let
\(d_j\ge0\) be \(\mathcal F_{j-1}\)-measurable and committed before the protected
round-\(j\) evaluation. Assume

\[
\Pr(E_j\mid\mathcal F_{j-1})\le d_j\quad\text{almost surely}
\]

and the ledger enforces \(\sum_j d_j\le\alpha\) almost surely. Then

\[
\Pr\!\left(\bigcup_j E_j\right)
\le \sum_j \Pr(E_j)
= \sum_j \mathbb E[\Pr(E_j\mid\mathcal F_{j-1})]
\le \mathbb E\!\left[\sum_j d_j\right]
\le \alpha.
\]

For countably many rounds, apply the finite result to the first \(n\) rounds and
use monotone convergence as \(n\to\infty\). The same proof works with first-bad-
promotion events, which are disjoint and can yield a sharper presentation.

## 3. What the max-information lemma must supply

To use Repair B, the approximate max-information transfer must itself hold in a
form strong enough to imply the displayed conditional inequality for every
allowed public history, candidate, component null, test and evaluator epoch.
An unconditional joint-distribution inequality may give a valid deterministic
per-round bound, but it does not by itself justify a history-specific random
right-hand side.

The revised theorem should choose one route explicitly:

1. register deterministic global \(B_j,u_j,\beta_j\) values before the campaign
   and use Repair A; or
2. prove a conditional/history-uniform transfer statement and use Repair B.

If component tests use different levels, the bad-candidate bound must use the
registered level for a measurably selected true component, or a conservative
maximum across the three non-compensatory nulls. The term should be
"false promotion" (equivalently, erroneous rejection of a true component null),
not ambiguous "false rejection."

## 4. Operational obligations

- debit and evaluator epoch are committed before protected outcome access;
- retries, resumptions and duplicate requests cannot remint debit;
- stopping sets future spending to zero rather than reallocating after outcome;
- a renamed process/key does not reset leakage;
- a new epoch resets only with independently sealed data and a justified
  transcript-independence bound;
- absence of a valid \(B_j,\beta_j\) argument is `UNRESOLVED`, never a numerical
  default;
- fixed-candidate test validity, retention, harm, resource and authority gates
  remain separate vetoes.

## 5. Claim disposition

The reusable sealed lane currently establishes an executable accounting and
conformance mechanism under declared inputs. Its familywise statistical claim
should be cited only after Repair A or B is incorporated and the required
max-information premise is justified for the actual release mechanism. This
audit does not execute the protected campaign and grants no ORION-15/24
promotion.

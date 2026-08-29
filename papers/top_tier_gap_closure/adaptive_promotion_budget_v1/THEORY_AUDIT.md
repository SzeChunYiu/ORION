# Adaptive promotion-budget theorem audit V1

**Subject:** reusable sealed promotion theory used by ORION-15 and ORION-24  
**Disposition:** statement gap with two valid repairs  
**Scientific-authority delta:** `NONE`

## 1. Gap

The current form assigns each round a debit

\[
d_j=B_j u_j+\beta_j
\]

and invokes a pathwise budget \(\sum_j d_j\le\alpha\) under adaptive candidate generation and data-dependent stopping. The proof must say whether the debit sequence is deterministic, or whether a history-dependent debit is predictable and controls the **conditional** bad-promotion probability. A scalar unconditional probability cannot be compared with a random realized debit and then summed pathwise.

This is a probability-statement gap, not evidence that the exact ledger software is wrong. Software can enforce declared accounting rules; the theorem must establish what those rules guarantee.

## 2. Repair A — deterministic summable schedule

Let \((d_j)_{j\ge1}\) be a deterministic nonnegative sequence. If every bad-promotion event \(E_j\) satisfies

\[
\Pr(E_j)\le d_j
\]

and \(\sum_j d_j\le\alpha\), then the union bound gives

\[
\Pr\!\left(\bigcup_j E_j\right)\le\alpha.
\]

Data-dependent stopping is represented by defining later events as empty or by retaining the precommitted deterministic schedule. Stopping does not create a random post-outcome right-hand side.

## 3. Repair B — predictable conditional spending

Let \((\mathcal F_j)_{j\ge0}\) be the public transcript/ledger filtration. Let \(d_j\ge0\) be \(\mathcal F_{j-1}\)-measurable and committed before protected round-\(j\) evaluation. Assume

\[
\Pr(E_j\mid\mathcal F_{j-1})\le d_j
\quad\text{almost surely}
\]

and the ledger enforces \(\sum_jd_j\le\alpha\) almost surely. Then for every finite \(n\),

\[
\Pr\!\left(\bigcup_{j=1}^nE_j\right)
\le\sum_{j=1}^n\Pr(E_j)
=\sum_{j=1}^n\mathbb E[\Pr(E_j\mid\mathcal F_{j-1})]
\le\mathbb E\!\left[\sum_{j=1}^nd_j\right]
\le\alpha.
\]

For countably many rounds, take \(n\to\infty\) and use continuity from below. The same argument may be written with disjoint first-bad-promotion events.

## 4. Max-information premise

Repair B requires the approximate max-information transfer to imply the displayed conditional inequality for every allowed public history, candidate, true component null, test, and evaluator epoch. An unconditional joint-distribution inequality may justify a deterministic per-round bound, but it does not automatically justify a history-specific random debit.

The parent theory must choose one route explicitly:

1. register deterministic global \(B_j,u_j,\beta_j\) and use Repair A; or
2. prove a conditional/history-uniform transfer statement and use Repair B.

If component tests use different levels, the bad-candidate bound uses the registered level for the measurably selected true component or a conservative maximum across the noncompensatory nulls. Use “false promotion” or “erroneous rejection of a true component null,” not ambiguous “false rejection.”

## 5. Operational obligations

- debit and evaluator epoch are committed before protected outcome access;
- retries, resumptions, and duplicate requests cannot remint debit;
- stopping sets future spending to zero or follows the deterministic schedule rather than reallocating after outcome;
- renamed processes or keys do not reset leakage;
- a new epoch resets only with independently sealed data and a justified transcript-independence argument;
- absence of a valid \(B_j,\beta_j\) argument is `UNRESOLVED`, never a numerical default;
- retention, harm, resource, authority, and fixed-candidate validity remain separate vetoes.

## 6. Claim disposition

The reusable lane establishes an executable accounting/conformance mechanism under declared inputs. Its familywise statistical claim should be cited only after Repair A or B is incorporated and the required transfer premise is justified for the actual release mechanism. This audit executes no protected campaign and grants no ORION-15/24 promotion.
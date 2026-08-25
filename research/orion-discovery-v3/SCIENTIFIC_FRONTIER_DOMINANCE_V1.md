# ORION Scientific Frontier Dominance V1

## Status

```text
theory_status = DERIVED_FOR_DECLARED_FINITE_AND_ENUMERABLE_CLASSES
present_day_superiority_authority = NONE
external_novelty_authority = CANNOT_CHECK
paper_authority_delta = NONE
```

This document deliberately aims at a **stronger and wider target** than ordinary
average-score superiority.  It does not weaken the ambition to fit current
results.  It replaces an underspecified slogan—"ORION is better"—with a
falsifiable claim that must survive the ideal product of the nearest work.

## 1. Scientific comparison contract

A comparison is indexed by a frozen contract

\[
\mathcal C=(\mathcal T,I,A,V,B,\rho),
\]

where:

- \(\mathcal T\) is the exact task/responsibility class;
- \(I\) is candidate-visible information;
- \(A\) is tool, model, retrieval, instrument and action access;
- \(V\) is the scientific validity/admission evaluator;
- \(B\) is a vector resource budget;
- \(\rho\) is custody, chronology and inference-unit policy.

A comparison is not interpretable when a candidate receives an answer-bearing
interface, a stronger instrument, a different task partition, or an uncharged
resource that donors do not receive.

For system \(s\) and task \(t\), let

\[
Y_s(t)=(q_s(t),a_s(t),f_s(t),c_s(t)),
\]

where \(q\) is native correctness, \(a\) scientific admissibility, \(f\) false
promotion and \(c\in\mathbb R_{\ge0}^k\) a resource vector.  Define a valid
scientific success by

\[
S_s(t)=q_s(t)\land a_s(t)\land\neg f_s(t).
\]

## 2. Donor union and donor closure

Let \(\mathcal D=\{d_1,\ldots,d_m\}\) be the registered nearest-work family,
including ideal compositions whenever those compositions are executable under
the same contract.  The donor envelope succeeds on \(t\) when

\[
S_{\mathcal D}(t)=\bigvee_{d\in\mathcal D} S_d(t).
\]

The **donor closure** \(Cl_B(\mathcal D)\) is the set of targets reachable by
registered donors, their registered semantics-preserving adapters and their
admissible products under budget \(B\).  It is not merely the union of their
published benchmarks.  A fair comparison gives the donor product the same
scientific ingredients that ORION receives.

A frontier task satisfies

\[
t\notin Cl_B(\mathcal D).
\]

This status requires an exact closure proof, a complete bounded search, or an
explicitly scoped obstruction certificate.  Timeout alone is not a frontier
certificate.

## 3. Weak scientific dominance

For fixed \((\mathcal C,\mathcal D)\), ORION candidate \(o\) weakly dominates
the donor envelope when all four conditions hold.

### D1 — donor conservativity

\[
\forall t\in Cl_B(\mathcal D),\quad
S_{\mathcal D}(t)\Rightarrow S_o(t).
\]

ORION may not buy one new result by losing an already available scientific
success.

### D2 — false-promotion non-amplification

For every task on which at least one donor avoids a false promotion, ORION must
also avoid it:

\[
f_o(t)\Rightarrow\bigwedge_{d\in\mathcal D}f_d(t).
\]

A higher solve rate cannot compensate for unsupported scientific promotion.

### D3 — vector-resource noninferiority

For each donor-closure success, at least one successful donor must be weakly
Pareto-dominated by ORION:

\[
\forall t\in Cl_B(\mathcal D): S_{\mathcal D}(t)
\Rightarrow
\exists d\in\mathcal D:\ S_d(t)\land c_o(t)\preceq c_d(t).
\]

If ORION uses less memory but more compute, neither side is declared cheaper
without a price vector frozen independently of the result.

### D4 — matched comparison

The information, tool, task, evaluator and chronology contracts are identical,
and every strong donor has first refusal before a residual is declared.

## 4. Strict frontier dominance

ORION strictly expands the frontier when weak dominance holds and

\[
\exists t^*\notin Cl_B(\mathcal D):
S_o(t^*)\land\neg S_{\mathcal D}(t^*).
\]

The strongest empirical version additionally requires:

- a held-out frontier success;
- a counterfactual/reminted success preserving the obstruction but changing
  answer-bearing surface form;
- a prospectively frozen success whose outcome was not controlled by the
  proposing programme;
- independent scientific validity and current novelty review.

The executable reference layer therefore distinguishes:

```text
FRONTIER_DOMINANT_IN_DECLARED_CLASS
TRIANGULATED_FRONTIER_DOMINANT_IN_DECLARED_CLASS
EXTERNAL_NOVELTY_SUPPORTED
```

The first two can be computed internally.  The final terminal cannot.

## 5. Scientific superiority normal form

For a declared finite class, define the operational superiority predicate by:

1. every task and resource vector is frozen before outcomes;
2. every registered donor is run under matched access;
3. donor-closure regressions are enumerated;
4. false-promotion regressions are enumerated;
5. Pareto resource regressions are enumerated;
6. strict outside-closure wins are enumerated;
7. held-out and counterfactual frontier wins are marked separately.

### Theorem FD-T3 — finite normal form

For the declared finite class, the candidate is frontier-dominant if and only
if the operational record has:

```text
matched_contract = true
conservativity_violations = empty
calibration_violations = empty
resource_violations = empty
strict_frontier_wins != empty
```

#### Proof

The forward direction follows because each violation is a direct witness that
one conjunct of weak or strict dominance fails.  In the reverse direction,
empty violation sets establish D1–D4 on every enumerated case, and a non-empty
strict-win set supplies the existential frontier witness.  The equivalence is
class-relative because neither unregistered donors nor unobserved tasks are
quantified over.  The Python reference implementation computes the two sides
from independent task records rather than defining one field from the other.

## 6. Structural theorems

### FD-T1 — weak dominance is a preorder under a fixed contract

Weak dominance is reflexive.  It is transitive when all systems are evaluated
on the same tasks, scientific terminal and resource dimensions.

**Proof.** Correct/admissible success implication is transitive; false-promotion
non-amplification is transitive; componentwise resource order is transitive;
and the matched contract is fixed.

### FD-T2 — strict expansion is preserved by conservative extension

If \(o_1\) strictly expands donor family \(\mathcal D\), and \(o_2\) weakly
dominates \(o_1\) while preserving its frontier witness, then \(o_2\) also
strictly expands \(\mathcal D\).

### FD-T4 — no scalar-free total superiority order

When two successful systems have resource vectors \((1,10)\) and \((10,1)\),
neither Pareto-dominates the other.  Any declaration of a unique cheaper system
therefore imports an exchange rate not contained in the scientific result.

This is not a reason to avoid broad superiority.  It is a reason to claim the
stronger object: a Pareto frontier or dominance under a prospectively supplied
price vector.

### FD-T5 — ideal-product first refusal

A claimed residual relative to individual donors may vanish when their
information-equivalent product is allowed.  Consequently:

\[
Residual_{\{d_1,\ldots,d_m\}}(o)
\subseteq
Residual_{\{d_i\}}(o).
\]

The ideal product must therefore receive first refusal whenever its combined
interfaces are legal under the contract.

### FD-T6 — superiority requires target-identifying support

If ORION and an alternative claim model induce identical outcome signatures on
the frozen support, the support cannot establish which model explains the
result.  Performance superiority without theorem identifiability is compatible
with a shortcut, a vacuous precondition, or the wrong scientific mechanism.

## 7. Strong target claim for ORION

The highest defensible programme target is:

> **Under a frozen scientific contract, ORION absorbs the semantic closure of
> every registered nearest-work donor and ideal donor product, conservatively
> preserves their valid successes, introduces no additional false scientific
> promotion, remains Pareto-noninferior on the donor closure, and generates a
> content-bound minimal scientific residual that produces independently
> verified held-out, counterfactual and prospective successes outside the
> donor-union closure.**

This is wider than a single-domain benchmark claim.  It is also harder: one
old-task regression, one hidden-answer interface, one donor-product solution,
one false promotion, or one unpriced resource tradeoff defeats it.

## 8. What this theory does not authorize

The theory and finite executable semantics do not establish:

- that the registered donor family is globally complete;
- that a frontier task is novel in the literature;
- that a generated residual is scientifically valid in a natural domain;
- that ORION is superior across unregistered tasks or budgets;
- that paper claims should change before result-bearing execution and
  independent authority.

Those are execution and external-authority obligations in the frozen backlog.

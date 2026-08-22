# P1/SAGE donor-envelope specification

Status: theory and hostile-test specification; no empirical or novelty authority  
Primary donor: Ma et al., *One Reflection Is Not Enough: Self-Correcting
Autonomous Research via Multi-Hypothesis Failure Attribution*,
[arXiv:2606.31478v1](https://arxiv.org/abs/2606.31478)

## Donor structure to absorb

SAGE owns the following reusable structure:

- a failure hierarchy over hypothesis, experimental design, and implementation;
- a structured failure context containing trajectory and semantic-stack state;
- multiple evidence-grounded causal hypotheses;
- independent category rectification and severity scoring;
- a deterministic category/severity router to `Proceed`, local/method/design
  refinement, or pivot;
- a separate repair path for zero-metric execution failures;
- a valid-result clamp that prevents weak but measured outcomes from causing
  hypothesis-discarding pivots;
- bounded pivoting and failure-aware regeneration.

P1 must reconstruct these behaviors source-faithfully before testing any
extension. Typed diagnosis and intervention-level routing are donor-owned, not a
P1 residual.

## Conservative embedding

Let a donor state be

\[
s=(\mathcal C,\mathcal H,c^\star,\sigma^\star,v,\kappa,q,B),
\]

where the terms denote SAGE's structured context, competing explanations,
rectified category, severity, validity/confidence clamp inputs, and pivot
count/budget. Its action is

\[
F_S(s)=\Gamma(\pi(c^\star,\sigma^\star),v,\kappa,q,B).
\]

Define the envelope state

\[
x=(s,\mathcal R,\prec,\Phi,\mathcal I,G,\widehat D,D^{obs},\mathcal A,U),
\]

adding registered revisions, a narrower-than order, same-task counterfactual
responses, protected invariants, a dependency graph, proposed/observed reopen
scope, admission certificates, and unknown/unavailable state.

The embedding \(\iota:S\rightarrow X\) copies every donor coordinate and
initializes the additional coordinates neutrally: a singleton donor-selected
revision, no narrower alternative, passing recovery/preservation/admission,
empty dependency impact, and no unknown discriminator.

The projection \(\rho:X\rightarrow S\) erases added coordinates and maps actions
back to donor names.

### Preservation obligation

For every valid donor state,

\[
\rho(F_P(\iota(s)))=F_S(s).
\]

The stronger executable obligation is complete trace preservation: diagnosis,
category rectification, severity boundary, execution-repair route, clamp, pivot
budget, terminal/abstention semantics, and evidence lineage must all agree after
projection. Matching only the terminal action is insufficient.

## Candidate envelope rule

A high-level revision \(r\) is admitted only if

\[
\begin{aligned}
\operatorname{Cert}_x(r) \iff {}&
\forall r'\prec r,\;\operatorname{status}(r')\in
\{\mathrm{FAILED},\mathrm{INADMISSIBLE}\}\\
&\land\;\Phi(r).\mathrm{target}=1
\land\;\mathcal I(r)=1\\
&\land\;D^{obs}(r)=\operatorname{TC}_{G}(\operatorname{coord}(r))
=\widehat D(r)\\
&\land\;\mathcal A(r)=1.
\end{aligned}
\]

These conjuncts are the proposed added structure: lower-level exclusion,
same-task recovery, protected preservation, dependency-impact binding, and
authority admission.

## Strict-separation target

Construct a minimal pair \(x^+,x^-\) with identical donor projection
\(\rho(x^+)=\rho(x^-)=s_0\), so SAGE routes both to the same pivot. All added
checks pass in \(x^+\). In \(x^-\), change exactly one added coordinate: a
narrower repair succeeds, same-task recovery fails, a protected sibling breaks,
dependency impact mismatches, or a decisive check is unavailable.

Then the target theorem is

\[
F_P(x^+)\ne F_P(x^-),\qquad
F_S(\rho(x^+))=F_S(\rho(x^-)).
\]

No policy using only the donor projection can reproduce this distinction. This
is a fiber-separation theorem about observable state and admission semantics,
not a claim that P1 owns SAGE's routing or has greater computational power.

## Ideal-product corollary

An independently implemented SAGE product supplied with the same added
coordinates and rule should tie the envelope exactly. That tie is a positive
composition/interface theorem:

\[
\text{envelope} > \text{native donor projection},\qquad
\text{envelope} = \text{information-equivalent ideal donor product}.
\]

The comparator must not call the candidate implementation. The current P1-X B3
self-call is not admissible evidence for this corollary.

## Frozen hostile tests

1. Exhaust every SAGE routing-table cell, severity threshold, validity clamp,
   execution-failure path, and pivot-budget boundary; projected traces must
   match.
2. Reorder or reserialize neutral added state; donor behavior must not change.
3. Each strict pair must have identical donor-projection bytes and digest.
4. Toggle one added coordinate at a time and require only its registered decision
   effect.
5. Demonstrate that no added gate is redundant with the others.
6. Supply an independently implemented information-equivalent donor product and
   require exact equality.
7. Reject answer-seeded manifests, protected-label leakage, and candidate-called
   comparators.
8. Run the locked instruments on fresh, independently authored scientific
   episodes; existing P1 outcomes are diagnostic only.

## Publication boundary

A defensible theorem paper may say that SAGE embeds conservatively and that the
added admission coordinates separate worlds indistinguishable under the donor
projection. It must also state that an information-equivalent donor product can
implement the same rule. Empirical benefit remains open until the fresh hostile
study passes.

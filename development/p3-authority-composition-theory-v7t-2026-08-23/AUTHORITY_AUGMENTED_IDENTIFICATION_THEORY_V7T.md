# Authority-augmented epistemic portrait envelopes

## Scope and novelty boundary

This note extends P3's existing observation-fibre theory to scientific claims
whose validity depends not only on content but also on claim-relevant authority
gates: source identity, rights, semantics, executable method identity,
comparator identity, evaluation custody, or another explicitly declared gate.
It is a specialization of partial-identification logic, not a claim to invent
general partial identification, selective prediction, provenance, or robust
decision theory.

The purpose is to make one publication error mathematically impossible:
turning an unexecuted, unauthorised, or semantically undefined comparison into
an observed loss, tie, or absence-derived negative class.

## Definition 1: authority-augmented query

Let \(\Omega\) be the scientifically admissible worlds and
\(O:\Omega\to\mathcal Y\) the declared observation operator. Let
\(q:\Omega\to\Theta\) be the scientific query. For a claim, freeze the finite
set \(J_q\) of gates whose satisfaction is necessary for that query, and let

\[
  a_j:\Omega\to\{0,1\},\qquad j\in J_q,
\]

be the corresponding authority predicates. Introduce a terminal
\(\bot_{\mathrm{auth}}\notin\Theta\). Define

\[
 q^A(\omega)=
 \begin{cases}
 q(\omega), & \prod_{j\in J_q}a_j(\omega)=1,\\
 \bot_{\mathrm{auth}}, & \text{otherwise},
 \end{cases}
\]

and, for a realised observation \(y\),

\[
 \Theta^A_q(y)=\{q^A(\omega):O(\omega)=y\}.
\]

The terminal is not a third truth label. It states that the named scientific
query lacks the authority required to possess an admissible observed value.
If every completion is unauthorised, the correct result is
\(\{\bot_{\mathrm{auth}}\}\), not an empty set and not a negative outcome.

## Theorem 1: authority-aware fibre criterion

For a realised observation \(y\) and \(\theta\in\Theta\), the scientific claim
"the authorized value is \(\theta\)" is point identified if and only if

\[
 \Theta^A_q(y)=\{\theta\}.
\]

Equivalently, both of the following must hold on the entire fibre
\(\Omega_y=\{\omega:O(\omega)=y\}\):

1. every claim-relevant authority predicate is true; and
2. \(q\) is constant with value \(\theta\).

If \(\bot_{\mathrm{auth}}\in\Theta^A_q(y)\), the observation does not identify
the authority needed for the claim. If two values of \(\Theta\) occur, it does
not identify the claim's substance. These failures are distinct and neither
may be converted into a negative scientific class.

### Proof

The image of \(\Omega_y\) under \(q^A\) is exactly
\(\Theta^A_q(y)\). It is the singleton \(\{\theta\}\), with
\(\theta\neq\bot_{\mathrm{auth}}\), exactly when \(q^A(\omega)=\theta\) for
every \(\omega\in\Omega_y\). By the definition of \(q^A\), this is equivalent
to every gate being one throughout the fibre and \(q(\omega)=\theta\)
throughout the fibre. Conversely, those two conditions force the stated
singleton. If the terminal occurs in the image, at least one completion lacks
necessary authority; if two ordinary values occur, no observation-only answer
can equal both. QED.

## Theorem 2: truthful authority refinement is monotone

Suppose \(O_2\) refines \(O_1\), so \(O_1=r\circ O_2\), while the world set,
query, and frozen authority predicates remain unchanged. Then for every
\(\omega\in\Omega\),

\[
 \Theta^{A,(2)}_q(O_2(\omega))
 \subseteq
 \Theta^{A,(1)}_q(O_1(\omega)).
\]

Thus truthful acquisition of a source identity, rights fact, executable
revision, or custodied outcome can remove completions and shrink the
authority-augmented envelope. Merely changing a decision rule over the same
observation cannot do so.

### Proof

The refined fibre is a subset of the coarse fibre. Taking the image of that
subset under the unchanged map \(q^A\) preserves inclusion. QED.

This result does **not** say that every newly retrieved byte is a refinement.
A mismatched repository, changed population, outcome-informed adapter, or
unlicensed source changes the scientific identity instead of refining the
frozen observation.

## Proposition 1: claim-relevant stage bottleneck

Let \(j\in J_q\).

* If \(a_j(\omega)=0\) for every \(\omega\in\Omega_y\), then
  \(\Theta^A_q(y)=\{\bot_{\mathrm{auth}}\}\).
* If the fibre contains an otherwise admissible authorized completion and an
  unauthorized completion, then \(\bot_{\mathrm{auth}}\) and at least one
  ordinary query value both lie in \(\Theta^A_q(y)\); an authorized determinate
  claim is not identified.
* Even if every local stage gate is identified true and every local stage
  output is fixed, the end-to-end query need not be identified when an
  unobserved cross-stage relation is claim-relevant.

The first two statements follow immediately from Definition 1. The third is
witnessed by the finite countermodel below.

## Countermodel 1: local readiness does not compose automatically

Take two worlds \(\omega_0,\omega_1\) with the same observation. In both,
source, rights, parser, and executable-entrypoint gates are one, and both local
stage artifacts equal the same fixed byte strings. Let an unobserved relation
\(r\) say whether those artifacts belong to the same scientific identity.
Set \(r(\omega_0)=0\), \(r(\omega_1)=1\), and let the global query be
\(q=r\).

All local readiness statements are identical and true in both worlds, but the
end-to-end identified set is \(\{0,1\}\). The missing relation may be archive
lineage, same-population identity, semantic comparability, or another declared
cross-stage binding. Therefore a collection of passed local preflights is not
an end-to-end scientific result unless the global query factors through those
local outputs under an explicit composition relation.

## Corollary 1: comparator superiority requires an authorized comparison

Let \(q_{\mathrm{sup}}\) encode a predeclared dominance or non-inferiority
statement for a candidate and comparator on the same frozen population, gold,
loss, and evaluation rule. Put into \(J_{q_{\mathrm{sup}}}\) the gates for:

1. candidate and comparator source/executable identities;
2. resource and configuration completeness;
3. rights to execute and evaluate;
4. population, task, and semantic comparability;
5. reference/gold authority;
6. outcome and scorer custody; and
7. complete terminal-preserving execution.

If any of these gates is false in every completion, superiority is
\(\{\bot_{\mathrm{auth}}\}\). If it varies across compatible completions, the
identified set contains \(\bot_{\mathrm{auth}}\). In neither case may a missing
run or missing artifact be counted as a loss, tie, abstention, obstruction, or
zero.

A native smoke run can identify a narrower query such as "this entrypoint
produces all prospectively required artifact types on this synthetic input."
It cannot identify \(q_{\mathrm{sup}}\) without the remaining population,
truth, custody, and scoring gates.

## Application to the retained P3 evidence

The V6 outcome-blind preflight supports only the following local queries:

| Comparator | Local query | Result | Guard |
|---|---|---|---|
| AML v3.2 | native artifact smoke | pass | Java 17 used while upstream names Java 8 |
| LogMap 4.0 | native artifact smoke | pass with guard | RDF header repeats ontology 1; row-namespace and TSV sidecar guards are mandatory |
| BERTMap / DeepOnto 0.9.3 | native artifact smoke | `CANNOT_CHECK` | pinned Python-3.10 lock selected Transformers 4.51.3, incompatible with DeepOnto's keyword before training |

The aggregate native-smoke state is 2/3. The comparison query still lacks
reference truth, naturalistic multi-family transport, scoring, and independent
custody, so scientific comparator readiness remains 0/3. This is exactly the
distinction in Theorem 1: some local authority predicates were refined, but
the authority-augmented superiority query was not point identified.

## What the theory buys the paper

This extension moves P3 upward from "a safer ontology mapper" to a general
claim-relative theory of scientific integration and evaluation:

* content underdetermination and evaluation-authority failure inhabit one
  terminal-preserving identified-set calculus;
* `CANNOT_CHECK` is formally separated from falsehood, obstruction, and poor
  performance;
* local conformance evidence composes only through explicit cross-stage
  relations; and
* the constructive route is truthful authority refinement, not verbal claim
  widening.

The result is broad, but its empirical authority remains narrow. It licenses a
larger theory and sharper study design; it does not license a larger empirical
performance claim.

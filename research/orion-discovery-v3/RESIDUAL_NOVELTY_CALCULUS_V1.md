# ORION Residual Novelty Calculus V1

## 1. Motivation

Scientific novelty is rarely a binary property of a complete artifact.  A
candidate may combine known lemmas, transport a known relation, invent one
missing operator, or use only known components connected by a previously
unregistered interaction.  Comparing only titles or surface descriptions either
inflates recombination into invention or erases real interaction novelty.

The calculus therefore subtracts the **best semantic explanation available to
the full donor family**.

## 2. Candidate and donor semantics

Represent a candidate by a typed semantic hypergraph

\[
G=(V,E),
\]

where nodes may belong to the layers

\[
\mathcal L=
\{Q,O,R,H,M,I,V_a,G_o\},
\]

corresponding to question, ontology, representation, mechanism, method,
instrument, validation and organization.  Hyperedges encode conjunction,
composition, transport, causal production, measurement and validation.

A donor explanation is

\[
X_i=(D_i,V_i,E_i),
\]

where \(D_i\) identifies the donor product and \((V_i,E_i)\) are the candidate
nodes and edges semantically absorbed by that product under a verified
correspondence.

The residual of explanation \(X_i\) is

\[
R_i(G)=\bigl(V\setminus V_i,\ E\setminus E_i\bigr).
\]

Because scientific decompositions need not be unique, the result is the family
of inclusion-minimal residuals:

\[
\mathcal R_{\mathcal D}(G)
=
\min_{\subseteq}
\{R_i(G):X_i\text{ admissible under }\mathcal D\}.
\]

No arbitrary single decomposition becomes novelty authority.

## 3. Residual dimensions

Each residual reports a vector rather than one score:

\[
\nu(R)=
(n_Q,n_O,n_R,n_H,n_M,n_I,n_{V_a},n_{G_o},n_E).
\]

The final coordinate counts unabsorbed interaction/hyperedge structure.  An
external programme may later supply prices or scientific weights, but the
reference calculus does not silently decide that one new question is worth
three new methods.

## 4. Core theorems

### RN-T1 — donor-expansion monotonicity

If \(\mathcal D\subseteq\mathcal D'\) and every old explanation remains
admissible, then every minimal residual under \(\mathcal D'\) is contained in
some residual under \(\mathcal D\).  Donor absorption cannot make the smallest
residual larger.

**Proof.** The explanation set for \(\mathcal D'\) contains the explanation set
for \(\mathcal D\).  Minimizing residuals over a superset can preserve or remove
old minima and can introduce smaller residuals; it cannot require a larger one.

### RN-T2 — semantic-isomorphism invariance

If candidates \(G\) and \(G'\) are related by a layer- and relation-preserving
isomorphism and donor explanations are transported through the isomorphism,
their residual families are isomorphic.  Renaming symbols cannot create
novelty.

### RN-T3 — interaction novelty

\[
V\setminus V_i=\varnothing
\not\Rightarrow
E\setminus E_i=\varnothing.
\]

All scientific ingredients may be donor-owned while the load-bearing way they
are connected remains outside donor closure.  This formalizes the user's
\(a_1\times b_2\times c_3\) case: the potential residual may be the composition
edge or topology, not a new component node.

### RN-T4 — component novelty does not imply useful expansion

A non-empty residual is not sufficient for scientific value.  The residual
must change a hidden scientific consequence, discharge a target obligation, or
strictly expand verified reach.  Decorative or behaviorally inert additions
remain zero-value novelty candidates.

### RN-T5 — non-uniqueness theorem

There may be incomparable minimal explanations: donor A absorbs one component,
while donor B absorbs another.  Therefore novelty should be represented by a
set-valued residual unless a further target-specific criterion identifies one
explanation.

### RN-T6 — subadditivity under composition

For independently composable candidates \(G_1,G_2\),

\[
\min |\mathcal R(G_1\oplus G_2)|
\le
\min |\mathcal R(G_1)|+
\min |\mathcal R(G_2)|+
|E_{\mathrm{bridge}}|.
\]

The bridge term is necessary because composition can itself carry novelty.

### RN-T7 — no fixed finite discovery morphology is universally complete

For any fixed finite move set \(M\), construct a registered target language
containing a primitive transformation \(m^*\notin Cl(M)\) whose verifier accepts
only outputs using \(m^*\).  No system restricted to \(M\) reaches that target.
Thus a finite morphology may be complete only relative to a declared class.

This motivates the explicit `OPEN_MOVE_CLASS` rather than claiming that a
historical taxonomy exhausts future science.

### RN-T8 — fair-dovetail relative completeness

Let \(g_0,g_1,\ldots\) be an enumerable sequence of candidate generators, and
let each generator enumerate finite candidates \(g_i(0),g_i(1),\ldots\).  The
diagonal schedule that visits all pairs \((i,j)\) by increasing \(i+j\)
eventually evaluates every finite enumerated candidate.

If a finite candidate accepted by a terminating verifier exists in the
registered generator language, fair dovetailing eventually reaches it.

This is **relative** completeness.  It says nothing about whether the language
contains the scientific breakthrough or whether the search is affordable.
Universal search and dovetailing are donor-owned foundations; ORION's residual
is their integration with typed scientific obligations, donor subtraction,
theorem-identifying evaluation, chronology and authority.

## 5. No-Man's-Land Certificate

A candidate may receive a bounded no-man's-land terminal only when a single
content-bound packet establishes:

```text
OLD_DONOR_UNION_CLOSURE_EXHAUSTED
PROPOSAL_NOT_SUPPLIED_OR_RETRIEVED
MINIMAL_RESIDUAL_FAMILY_NONEMPTY
RESIDUAL_IS_LOAD_BEARING
HIDDEN_CONSEQUENCE_PASSED
HELD_OUT_TRANSFER_PASSED
COUNTERFACTUAL_TWIN_PASSED
STRONG_DONOR_FIRST_REFUSAL_PASSED
INDEPENDENT_VALIDITY_PASSED
EXTERNAL_NOVELTY = CANNOT_CHECK or SUPPORTED
```

Possible honest terminals include:

```text
DONOR_COMPOSITION_SUFFICIENT
INTERACTION_RESIDUAL_ONLY
MULTIPLE_MINIMAL_RESIDUALS
OLD_CLOSURE_CANNOT_CHECK
GENERATED_BUT_BEHAVIORALLY_INERT
HELD_OUT_TRANSFER_FAILED
EXTERNAL_NOVELTY_CANNOT_CHECK
```

## 6. Strong novelty target

The strongest ORION claim to earn is not that it uses analogy, agents,
evolution or search.  Those mechanisms are already owned by mature parent
fields.  The target is:

> **ORION computes and verifies the smallest semantic residual remaining after
> the ideal product of all registered donors, identifies whether that residual
> lies in a question, ontology, representation, mechanism, method, instrument,
> validation or interaction layer, and prospectively demonstrates that the
> residual—not an information, evaluator, resource or authority advantage—is
> necessary for a new scientific consequence.**

That is a stronger novelty claim because it survives donor absorption rather
than depending on weak baselines.

# ORION Scientific Transition Calculus — formal language V1

## 1. Scope and authority

This document freezes a non-universal, finite formal language for the local
foundations tranche. It is designed to be strong enough to express every P1–P15
theoretical object without embedding paper-specific result authority.

The language is a **research instrument**. Its successful finite checks do not
prove that every scientific workflow has this form.

## 2. Typed universes

Let:

\[
\begin{aligned}
d&\in\mathbb D &&\text{scientific domain},\\
k&\in\mathbb K &&\text{object kind},\\
s&\in\mathbb S &&\text{scope},\\
e&\in\mathbb E &&\text{epoch},\\
p&\in\mathbb P &&\text{principal or issuer},\\
r&\in\mathbb R &&\text{responsibility},\\
q&\in\mathbb Q &&\text{terminal},\\
a&\in\mathbb A &&\text{artifact},\\
o&\in\mathbb O &&\text{obligation},\\
b&\in\mathbb B &&\text{bridge},\\
L&\in\mathbb L &&\text{method language},\\
x&\in\mathbb X &&\text{execution occurrence}.
\end{aligned}
\]

The programme terminal alphabet contains at least:

\[
\{ESTABLISH,RETAIN,REOPEN,CONTINUE,BLOCK,DENY,CANNOT\_CHECK\}.
\]

These terminals are intentionally non-binary. `CANNOT_CHECK` is not a negative
scientific result, and `DENY` is not scientific falsification.

## 3. Scientific objects and responsibilities

A scientific object is:

\[
X=(id,domain,kind,scope,content,epoch).
\]

A responsibility is:

\[
R=(id,X,question,resolution,loss,authority\_class).
\]

A judgment is:

\[
J=(X,R,q).
\]

Responsibilities are first-class because two uses of the same content may
require different distinctions. Prediction, intervention, verification,
diagnosis, repair, and publication need not share a sufficient state.

## 4. Artifacts and execution integrity

An artifact is:

\[
A=(id,subject,native\_type,content,native\_verdict,issuer,
provenance,epoch,occurrence,signature,integrity).
\]

Execution integrity is a product:

```text
attributable
occurrence_bound
content_bound
environment_bound
chronology_valid
replayable
cross_implementation_agreement
attested
custody_bound
freshness_bound
```

No implication from this product to scientific validity or scientific authority
is built into the language.

## 5. Obligations and support

An obligation is:

\[
O=(id,target\_judgment,predicate,kind,required\_authority,status,deps),
\]

where:

\[
status\in\{OPEN,DISCHARGED,BLOCKED,UNDETERMINED,REVOKED\}.
\]

A complete support family is a hyperedge:

\[
F=(Artifacts,Bridges,Authorities,BlockerResolutions)\Rightarrow J.
\]

Several support families for one judgment represent alternative complete
derivations. Revocation invalidates a judgment exactly when every complete
support family has been broken.

## 6. Scientific state

The programme state is:

\[
\Sigma=(K,W,M,\rho,\mathcal R,\Phi,\mathcal L,
Art,Obl,Sup,Bridge,Auth,Exec,H,\mathbf c).
\]

- `K`: object-level knowledge;
- `W`: relevance, route, search universe, or world model;
- `M`: governed controller/method state;
- `ρ`: ontology, objective, measurement, evaluator, and epoch regime;
- `ℛ`: active responsibilities;
- `Φ`: accessible representation;
- `ℒ`: registered method language and closure rules;
- `Art`: artifacts;
- `Obl`: obligations;
- `Sup`: support-family hypergraph;
- `Bridge`: registered scientific relations;
- `Auth`: grants, scopes, custody, and protected roots;
- `Exec`: occurrence-level execution facts;
- `H`: append-only negative and revision history;
- `c`: vector resource ledger.

The resource vector is not scalarized unless an independent price or preference
vector is supplied.

## 7. Primitive transition semantics

A transition is:

\[
\Sigma\xrightarrow{event,receipt}\Sigma'.
\]

Primitive event kinds include observation, acquisition, execution, native
verification, inference, mapping, reframing, opening/discharging/revoking an
obligation, regime transport, revalidation, delegation, coercion, isolated
candidate execution, replay, fresh transfer, external adoption, publication,
and epoch change.

Each event has an explicit read/write frame. A primitive event may preserve a
local artifact while reopening the target scientific status that previously
depended upon it.

## 8. Capability and reachability

A capability contract is:

\[
\mathcal C=(I,A,C,M,L,P,\beta).
\]

The reachable set is the least fixed point:

\[
Reach_{\mathcal C}(\Sigma)
=\mu Z\left(Seeds(\Sigma)\cup Ops_{\mathcal C}(Z)\right).
\]

This distinguishes:

- target not found;
- target inaccessible under the representation;
- target beyond the computation budget;
- target outside the method-language closure;
- target scientifically unresolved despite being generated.

## 9. Scientific discharge closure

For seed judgments `A` and registered sound bridge rules `R`, define:

\[
Cl_R(A)=\mu Z\left(A\cup\{concl(r):prem(r)\subseteq Z\}\right).
\]

An authority-neutral transformation may materialize, reorder, serialize, or
compute a consequence already in this closure. It introduces neither new
authorized evidence nor a new target bridge.

## 10. Target sufficiency

For a finite state class `S`, interface `Φ:S→Z`, and target terminal map
`T:S→Q`, the interface is target-sufficient when:

\[
\Phi(s_1)=\Phi(s_2)\Rightarrow T(s_1)=T(s_2).
\]

A sufficient interface is scientifically admissible only if its construction
respects the declared information and resource contract. Reading the protected
gold terminal directly is sufficient but inadmissible.

## 11. Operational admission and normal form

Operational admission is computed from primitive typed records:

1. donor-native artifact validity and required integrity;
2. target information sufficiency;
3. exact target object/responsibility/scope/epoch bridge and authority;
4. complete support and blocker state.

A candidate normal-form certificate is:

\[
\Pi=(\pi_V,\pi_S,\pi_E,\pi_B).
\]

For the finite bridge-workflow class implemented in this tranche, local theorems
prove:

\[
Admit(\Sigma,J)\iff\exists\Pi.ValidNF(\Sigma,J,\Pi).
\]

This is derived from the operational rule and certificate extraction/validation.
`Admit` is not defined as a bare conjunction of four booleans.

## 12. Recursive evolution

A governed evolution certificate contains:

```text
issue identity
diagnosis and discriminator
candidate intervention
isolation record
replay record
fresh-transfer record
protected-assurance record
negative-history update
external-adoption record
```

A system-generated proposal has no default authority to adopt, merge, publish,
or promote itself.

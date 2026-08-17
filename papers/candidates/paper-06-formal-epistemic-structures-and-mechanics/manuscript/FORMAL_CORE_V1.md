# P6 formal core V1

**Candidate paper:** Formal Epistemic Structures and Mechanics  
**Authority:** mathematical working object; novelty not yet authorized  
**Date:** 2026-08-17

## 1. Typed epistemic signatures

### Definition 1 (epistemic signature)
An **epistemic signature** is a tuple

\[
\Sigma=(C,(V_c)_{c\in C},Q,\mathcal O,\mathcal A),
\]

where:

- \(C\) is a finite or countable set of typed state coordinates;
- \(V_c\) is the value domain of coordinate \(c\);
- \(Q\) is a set of claim/certificate identifiers;
- \(\mathcal O\) is a set of obligation types;
- \(\mathcal A\) is a set of authority-token types.

A coordinate is not assumed to be a proposition. It may hold a representation, search universe, measurement definition, procedure, provenance identity, resource state, or other typed object.

### Definition 2 (epistemic state)
A state over \(\Sigma\) is

\[
E=(\nu,s,D,P,O,A,H),
\]

where:

- \(\nu(c)\in V_c\) is the current coordinate valuation;
- \(s:Q\to\{\mathsf{open},\mathsf{certified},\mathsf{invalid},\mathsf{cannot\_check}\}\) is claim status;
- \(D\subseteq (C\cup Q)\times Q\) is a dependency relation;
- \(P\) maps claims and transitions to provenance/evidence identities;
- \(O\) is a finite set of active typed obligations;
- \(A\) is a finite set of active authority tokens;
- \(H\) is retained transition/failure history.

Write \(\Delta(E,E')=\{c\in C:\nu_E(c)\neq\nu_{E'}(c)\}\).

### Definition 3 (authority token)
An authority token is provisionally a tuple

\[
\alpha=(i,d,S,e,t),
\]

consisting of issuer \(i\), action domain \(d\), permitted coordinate/action scope \(S\), evidence/protocol identity \(e\), and validity interval/epoch \(t\).

The predicate \(\mathsf{permits}(\alpha,m,c,E)\) is true only when the token's domain, scope, evidence identity and epoch are valid for mechanic \(m\)'s proposed write to \(c\).

P8 owns the general authority calculus. P6 needs only enough authority structure to state mechanic well-formedness and non-escalation.

## 2. Mechanic contracts

### Definition 4 (epistemic mechanic)
A mechanic is a contract

\[
m=(R_m,W_m,\mathsf{Pre}_m,\mathsf{Req}_m,\tau_m,\mathsf{Emit}_m,\mathsf{Fail}_m,\mathsf{Inv}_m),
\]

where:

- \(R_m\subseteq C\cup Q\) is its read footprint;
- \(W_m\subseteq C\cup Q\) is its write footprint;
- \(\mathsf{Pre}_m(E)\) is its precondition;
- \(\mathsf{Req}_m(E)\) is the set of required evidence/obligation/authority judgments;
- \(\tau_m\subseteq \mathcal E_\Sigma\times\mathcal E_\Sigma\) is its transition relation;
- \(\mathsf{Emit}_m(E,E')\) lists newly emitted claims/obligations/provenance;
- \(\mathsf{Fail}_m\) is a typed failure-terminal set;
- \(\mathsf{Inv}_m\) is a set of invariants promised by the contract.

A deterministic mechanic has a partial transition function instead of a relation.

### Definition 5 (admissible mechanic step)
We write

\[
E\xrightarrow[m]{\mathrm{adm}}E'
\]

iff all of the following hold:

1. \(\mathsf{Pre}_m(E)\);
2. every hard member of \(\mathsf{Req}_m(E)\) is satisfied by content-bound evidence or valid authority in \(E\);
3. \((E,E')\in\tau_m\);
4. \(\Delta(E,E')\subseteq W_m\);
5. every changed coordinate is permitted by an in-scope authority token;
6. every invariant in \(\mathsf{Inv}_m\) holds in \(E'\);
7. every new claim/obligation has provenance recorded in \(P_{E'}\);
8. no authority token in \(A_{E'}\setminus A_E\) was minted except by a trusted authority-producing transition explicitly allowed by the contract.

A mechanic may be computationally executable while having no admissible step.

## 3. Dependency semantics and reopening

For \(X\subseteq C\cup Q\), let \(\operatorname{Desc}_D(X)\) be the strict transitive downstream closure under \(D\).

### Definition 6 (dependency-soundness)
A dependency relation \(D\) is **sound for a class of admissible semantics** \(\mathfrak S\) when, for every certified claim \(q\), every semantic support that may affect the validity of \(q\) is represented by an ancestor path to \(q\) in \(D\).

This is a relative notion: a graph can be sound for one abstraction and incomplete for another.

### Definition 7 (selective reopening)
For a changed set \(X\subseteq C\cup Q\), define

\[
\operatorname{Reopen}_D(E,X)
\]

as the state obtained by:

- retaining the new coordinate values;
- changing every certified claim in \(\operatorname{Desc}_D(X)\) to \(\mathsf{open}\) (or \(\mathsf{cannot\_check}\) when required support is unavailable);
- preserving claim status outside \(\operatorname{Desc}_D(X)\);
- recording the invalidation cause and prior status in \(H\);
- preserving provenance for retained claims and invalidation provenance for reopened claims.

### Theorem 1 (sufficiency of downstream reopening)
Let \(D\) be sound for \(\mathfrak S\). If only elements of \(X\) are changed before reopening, then after \(\operatorname{Reopen}_D(E,X)\), no claim whose certification may have been invalidated by the change remains certified.

#### Proof
Take any claim \(q\) whose certification may be invalidated by changing \(X\). By dependency-soundness, some changed element \(x\in X\) is an ancestor of \(q\); hence \(q\in\operatorname{Desc}_D(X)\). The reopening operator removes certified status from every such claim. Therefore no potentially invalidated dependent claim remains certified. \(\square\)

### Theorem 2 (minimality under graph-only information)
Assume the only semantic dependency information available to a reopening strategy is a sound graph \(D\). Any strategy that must be sound for every semantics compatible with \(D\) must reopen every certified claim in \(\operatorname{Desc}_D(X)\). Consequently, downstream reopening is inclusion-minimal among uniformly sound graph-based strategies.

#### Proof
Suppose a purportedly uniformly sound strategy leaves some certified \(q\in\operatorname{Desc}_D(X)\) certified. There is a directed path from some \(x\in X\) to \(q\). Construct a semantics compatible with \(D\) in which every edge on that path represents a necessary support relation and \(q\) is valid exactly when the original value of \(x\) holds. Change \(x\) so that the support fails. Then \(q\)'s prior certification is invalid, but the strategy retains it, contradicting uniform soundness. Therefore every descendant must reopen. The operator reopens no other claims, proving inclusion minimality. \(\square\)

### Corollary 2.1
Full reset is sound under the same assumptions but is not minimal whenever a certified claim exists outside \(\operatorname{Desc}_D(X)\).

### Corollary 2.2
No-reset is sound only when \(\operatorname{Desc}_D(X)\) contains no certified claims or a separate preservation proof discharges every such dependency.

## 4. Mechanic composition

### Definition 8 (separated mechanics)
Mechanics \(m\) and \(n\) are **strongly separated** when

\[
W_m\cap(R_n\cup W_n)=\varnothing
\quad\text{and}\quad
W_n\cap(R_m\cup W_m)=\varnothing,
\]

and neither mechanic changes authority, provenance, obligations or invariants consumed by the other.

### Theorem 3 (commutation under strong separation)
Let \(m,n\) be deterministic, admissible, strongly separated mechanics. Then whenever both compositions are defined,

\[
\tau_n(\tau_m(E))=\tau_m(\tau_n(E)).
\]

#### Proof
Mechanic \(m\) writes no coordinate read or written by \(n\), so executing \(m\) cannot change the values on which \(n\)'s transition depends or the values \(n\) writes. Symmetrically, executing \(n\) cannot affect \(m\). Both executions therefore compute the same local updates from the same local inputs, and the disjoint updates yield the same combined valuation. The additional separation condition preserves authority, obligations, provenance and shared invariants, so the entire resulting states are equal. \(\square\)

### Definition 9 (non-escalating mechanic)
Fix a trusted root set \(A_0\). A mechanic is non-escalating when every output token is either:

1. a token already present in the input;
2. a scope restriction of an input token; or
3. a token issued by a trusted authority transition whose issuer is in \(A_0\).

### Theorem 4 (sequential non-escalation)
The sequential composition of non-escalating mechanics is non-escalating.

#### Proof
By induction on composition length. The base case is the definition. Assume a composition of \(k\) mechanics produces only retained, narrowed, or trusted-root-issued tokens. Applying mechanic \(k+1\) can only retain/narrow those tokens or add a trusted-root-issued token. Thus the property holds for length \(k+1\). \(\square\)

### Remark
The theorem does not say the trusted root is correct. It says authority cannot arise from an unregistered internal transition once the root and narrowing relation are fixed.

## 5. Recursive mechanic audit

Let a mechanic representation include a finite syntactic or semantic rank \(r(m)\) in a well-founded ordered set \((L,\prec)\).

### Definition 10 (rank-decreasing audit)
A recursive audit is rank-decreasing when every recursive call from mechanic representation \(m\) to subproblem/mechanic representation \(m'\) satisfies \(r(m')\prec r(m)\).

### Theorem 5 (termination by well-founded descent)
Every rank-decreasing recursive audit terminates.

#### Proof
An infinite audit execution would generate an infinite descending chain

\[
r(m_0)\succ r(m_1)\succ r(m_2)\succ\cdots,
\]

contradicting well-foundedness. \(\square\)

### Countermodel 5.1 (absence of a descent obligation)
Let an auditor \(a\) respond to every unresolved audit of \(a\) by invoking the same audit state with unchanged rank and state. Then

\[
a(E)\to a(E)\to a(E)\to\cdots
\]

is an admissible infinite trace unless an external bound, cycle detector or decreasing measure is imposed.

## 6. Self-authorization boundary

### Proposition 6 (internal self-authorization cannot guarantee promotion soundness)
Suppose candidate mechanic \(m\) can rewrite both (i) the predicate \(J\) deciding whether \(m\) is promotable and (ii) all evidence values read by \(J\), with no protected external constraint. Then for every candidate \(m\) there exists an internally reachable pair \((J',E')\) such that \(J'(m,E')=\mathsf{authorize}\). Hence internal authorization alone cannot guarantee any nontrivial externally defined promotion property.

#### Proof
Choose \(J'\) to be the constant predicate returning \(\mathsf{authorize}\), or choose evidence \(E'\) satisfying a candidate-controlled acceptance branch. Since both objects are candidate-writable and no external constraint exists, the pair is reachable by assumption. The judgment carries no necessary relation to an externally defined property of \(m\). \(\square\)

### Consequence
A self-audit may recommend or construct changes, but promotion soundness requires at least one authority root, evaluator, or invariant outside the candidate's write authority.

## 7. `CANNOT_CHECK` semantics

### Definition 11 (knowledge failure versus action failure)
For a proposed transition, distinguish:

- \(\mathsf{REJECT}\): available evidence establishes a blocking condition;
- \(\mathsf{CANNOT\_CHECK}\): a required obligation cannot be established or refuted from admissible evidence;
- \(\mathsf{FAIL}\): execution of an otherwise admissible mechanic failed;
- \(\mathsf{UNAUTHORIZED}\): the transition is computable but lacks an authority derivation.

These terminals are not interchangeable. In particular, missing evidence is not evidence of failure, and computational success is not authority.

## 8. Finite-checking obligations

The deterministic checker associated with this core must enumerate bounded structures and verify at least:

1. downstream reopening removes all certified descendants;
2. unaffected certified nodes remain unchanged;
3. strong separation implies commutation for the finite mechanic class;
4. non-escalating transitions cannot mint untrusted authority under composition;
5. recursive self-loop countermodels are detected;
6. candidate-writable acceptance predicates admit the self-authorization countermodel.

Finite enumeration supports the proofs and catches implementation mistakes; it does not replace the general proofs.

## 9. Nearest-work pressure and nonclaims

This core does **not** claim novelty for:

- belief expansion, contraction or revision;
- dynamic epistemic model update;
- truth-maintenance/dependency-directed backtracking;
- modular or typed transition systems;
- separation/commutation arguments;
- well-founded termination proofs;
- authorization/access-control logics;
- provenance or retained history in isolation.

The only candidate residual is the operationally grounded composition:

\[
\text{typed responsibility/evidence obligations}
\Rightarrow
\text{coordinate-scoped mutation authority}
\Rightarrow
\text{dependency-minimal reopening}
\Rightarrow
\text{recursively composable mechanic contracts}.
\]

If the nearest-work and P1 ownership audits find this composition already established or reconstruction-specific, the formal material should merge into P1 rather than become P6.

## 10. What this formal core establishes now

The proofs above establish elementary structural properties of the proposed definitions. They do **not** yet establish:

- that the definitions are novel;
- that the signature captures all important ORION mechanics;
- that dependency graphs are complete in practice;
- that typed mechanics improve real research outcomes;
- that a proof assistant has checked the general statements;
- that P6 should remain a separate paper.

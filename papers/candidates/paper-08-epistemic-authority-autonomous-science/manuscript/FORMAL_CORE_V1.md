# P8 formal core V1

**Candidate paper:** A Theory of Epistemic Authority for Autonomous Science  
**Authority:** mathematical working object; novelty not yet authorized  
**Date:** 2026-08-17

## 1. Typed epistemic actions

Let

\[
\mathcal D=\{\mathsf{reframe},\mathsf{search\_stop},\mathsf{map\_merge},\mathsf{assert},\mathsf{self\_modify}\}
\]

be the initial action-domain set.

### Definition 1 (epistemic action)
An epistemic action is a tuple

\[
a=(d,s,p),
\]

where \(d\in\mathcal D\) is the action domain, \(s\) is a typed scope, and \(p\) is the proposed state transition or payload.

### Definition 2 (capability)
\(\mathsf{Cap}(a,E)\) means that the candidate system can construct and/or execute \(a\) from state \(E\). Capability has no authorization consequence unless a rule states one.

## 2. Judgments, obligations and certificates

### Definition 3 (typed judgment)
A judgment is

\[
j=(i,k,d,s,e,t),
\]

where:

- \(i\) is the issuer;
- \(k\) is the judgment kind (support, defeater, obligation satisfaction, authorization, revocation, coverage certificate, and so on);
- \(d\) is its domain;
- \(s\) is its scope;
- \(e\) is its content-bound evidence/protocol identity;
- \(t\) is its validity epoch/expiry.

A bare token such as `PASS`, `VERIFIED`, `HIGH_CONFIDENCE` or `DONE` is not an authority judgment without these fields.

### Definition 4 (obligation status)
For action \(a\), each obligation \(o\in\operatorname{Obl}(a)\) has status

\[
\operatorname{st}(o)\in\{\mathsf{sat},\mathsf{violated},\mathsf{unknown},\mathsf{conflict}\}.
\]

Obligations are partitioned into hard blockers \(H(a)\) and soft/resource considerations \(S(a)\).

### Definition 5 (authority contract)
An authority contract for action \(a\) is

\[
\mathcal C_a=(H(a),S(a),B(a),I(a),K(a)),
\]

where \(B(a)\) is a defeater set, \(I(a)\) is the set of trusted issuer policies, and \(K(a)\) is the set of registered cross-domain coercions/delegations accepted by the action domain.

### Definition 6 (authorization)
An action is authorized, written \(\Gamma\vdash\mathsf{Auth}(a)\), only if:

1. every hard obligation in \(H(a)\) has a valid \(\mathsf{sat}\) judgment;
2. no blocking defeater in \(B(a)\) is active;
3. every authority judgment used in the derivation is unexpired, evidence-bound and issued by a trusted issuer or obtained through a registered sound coercion;
4. the derived scope is no broader than the scopes in the premises;
5. no premise has been revoked.

If a hard obligation is \(\mathsf{unknown}\) or \(\mathsf{conflict}\), the terminal is \(\mathsf{CANNOT\_CHECK}\) unless a contract-specific rule requests more evidence.

## 3. Core inference rules

The following rules are schematic.

### Rule A1 (trusted base authorization)

\[
\frac{j=(i,\mathsf{authorize},d,s,e,t)\in\Gamma\quad i\in I(a)\quad d=d(a)\quad s(a)\subseteq s\quad \mathsf{valid}(j)}
{\Gamma\vdash\mathsf{Auth}(a)}
\]

provided all hard obligations and defeater checks in the contract also pass.

### Rule A2 (scope restriction)

\[
\frac{\Gamma\vdash\mathsf{Auth}(d,s,p)\quad s'\subseteq s}
{\Gamma\vdash\mathsf{Auth}(d,s',p|_{s'})}
\]

Authority may narrow without a new grant; widening requires a new derivation.

### Rule A3 (registered coercion/delegation)

\[
\frac{\Gamma\vdash j:d\quad \kappa_{d\to d'}\in K(a)\quad \mathsf{Pre}_\kappa(j,a)}
{\Gamma\vdash \kappa(j):d'}
\]

The coercion records its source, target, scope transformation, assumptions and proof/evidence obligation.

### Rule A4 (hard-obligation conjunction)

\[
\frac{\forall o\in H(a),\ \Gamma\vdash\mathsf{Sat}(o)\quad \nexists b\in B(a),\ \Gamma\vdash\mathsf{Active}(b)}
{\Gamma\vdash\mathsf{ObligationsCleared}(a)}
\]

### Rule A5 (revocation)
If a premise judgment or evidence identity used by an authorization derivation is revoked, every dependent authorization certificate is invalid until re-derived from valid premises.

### Non-rule (implicit universal PASS)
There is deliberately no rule

\[
\frac{\Gamma\vdash\mathsf{PASS}(x)}{\Gamma\vdash\mathsf{Auth}(a)}.
\]

## 4. Authority laundering

### Definition 7 (authority laundering)
Authority laundering occurs when a judgment valid for one kind/domain/scope is used to authorize an action outside that kind/domain/scope without an explicit sound coercion.

Examples include confidence-to-permission, route-stop-to-task-stop, similarity-to-merge, citation-support-to-verification, and replay-gain-to-self-promotion.

### Theorem 1 (no authority laundering in the typed calculus)
Assume every derivation rule either:

1. preserves judgment domain and narrows scope; or
2. applies a registered coercion \(\kappa_{d\to d'}\).

If no coercion path exists from domain \(d\) to domain \(d'\), then a set of premises containing only judgments in \(d\) cannot derive authorization of an action in \(d'\).

#### Proof
Proceed by induction on derivation height. Base judgments retain their declared domain. For the induction step, a domain-preserving rule cannot change \(d\) to \(d'\). The only domain-changing rule is registered coercion; by assumption no coercion path from \(d\) to \(d'\) exists. Therefore no derivation ending in domain \(d'\) can be constructed from only domain-\(d\) premises. \(\square\)

### Corollary 1.1
A valid `route_stop` judgment cannot authorize `task_stop` unless the calculus registers a coverage coercion whose premises prove that all mandatory task obligations are covered.

### Corollary 1.2
A valid replay-improvement judgment cannot authorize self-change promotion unless a coercion explicitly requires fresh-transfer, regression and protected-evaluator obligations.

## 5. Non-compensatory authority

### Definition 8 (unbounded additive accumulator)
An additive authority surrogate has the form

\[
S=\sum_{i=1}^{n}w_i x_i-pb,
\]

where positive evidence increments \(x_i\ge 0\) may be accumulated without a fixed finite upper bound on \(n\), \(b\in\{0,1\}\) indicates a blocking violation, \(p<\infty\) is its penalty, and authorization occurs when \(S\ge\theta\).

### Theorem 2 (finite penalties do not encode absolute blockers under unbounded accumulation)
For every finite penalty \(p\), threshold \(\theta\) and positive evidence weight \(w>0\), there exists a number \(n\) of positive evidence increments such that the additive rule authorizes despite \(b=1\).

#### Proof
Set all positive increments to one with weight \(w\). Choose

\[
n\ge \left\lceil\frac{\theta+p}{w}\right\rceil.
\]

Then \(S=nw-p\ge\theta\) while the blocker remains active. \(\square\)

### Consequence
An absolute scientific blocker cannot be represented by an unbounded additive evidence accumulator with finite penalties. It requires a conjunctive veto, lexicographic layer, infinite penalty in the mathematical idealization, or another explicitly non-compensatory semantics.

### Limitation of the theorem
A bounded fixed-dimensional additive model can encode a veto by choosing a sufficiently dominant weight. The claim concerns unbounded or extensible evidence accumulation, not every possible scoring function.

## 6. Revocation

Let \(G=(J,E_D)\) be a directed acyclic derivation graph whose nodes are evidence/judgment/certificate identities and whose edges record premise dependence.

### Definition 9 (revocation closure)
For revoked node set \(X\), define

\[
\operatorname{Rev}_G(X)=X\cup\operatorname{Desc}_G(X).
\]

Every authorization certificate in this set loses validity until a fresh derivation not depending on revoked nodes is supplied.

### Theorem 3 (sound dependency-grounded revocation)
If \(G\) contains every premise dependency of each certificate, revoking \(\operatorname{Rev}_G(X)\) invalidates every authorization whose derivation may have become unsound because of \(X\), while certificates outside the closure retain their derivations.

#### Proof
Any affected authorization has a premise path from some \(x\in X\), hence lies in the descendant closure and is revoked. Any certificate outside the closure has no recorded derivation path from \(X\); under dependency completeness its proof uses no revoked premise, so its existing derivation remains intact. \(\square\)

### Remark
This is a structural theorem. Whether the dependency graph is complete is an empirical/engineering obligation.

## 7. Self-promotion and protected roots

### Theorem 4 (candidate-controlled admission cannot establish external promotion soundness)
Let candidate \(c\) have write access to both the admission predicate \(J\) and every evidence value read by \(J\). Without a protected external invariant, for every candidate \(c\) there exists an internally reachable state in which \(J(c)=\mathsf{authorize}\), independently of whether \(c\) satisfies an external target property \(P\).

#### Proof
The candidate can replace \(J\) with the constant-authorization predicate, or edit its inputs to satisfy an acceptance branch. Since no protected invariant constrains those writes, authorization is reachable for arbitrary \(c\). Therefore internal admission does not imply \(P(c)\). \(\square\)

### Corollary 4.1
A candidate system may propose, test and recommend its own modification, but its promotion certificate must ultimately depend on at least one authority root outside the candidate's write domain.

## 8. Embedding the five existing gates

### Definition 10 (domain embedding)
An existing gate embeds into the calculus when its action, hard obligations, defeaters, authority issuer, scope and revocation conditions are represented without changing the gate's decisions on its defined domain.

### Proposition 5 (candidate embeddings)
The current ORION gates can be represented provisionally as follows:

1. **P1 reframe:** action domain `reframe`; hard obligations include supported responsibility and coordinate-scoped permission; unresolved responsibility blocks broad mutation.
2. **P2 task stop:** action domain `search_stop`; hard obligations include route/task distinction, mandatory coverage obligations and censored-route accounting.
3. **P3 merge:** action domain `map_merge`; hard obligations include referent/context/measurement/preservation conditions; obstruction is a valid non-authorization terminal.
4. **P4 assert/promote:** action domain `assert`; hard obligations are the protected non-compensatory authority checks in the frozen protocol.
5. **P5 promote self-change:** action domain `self_modify`; hard obligations include replay, fresh transfer, non-regression/protected assurance and no candidate-controlled promotion root.

This proposition is an encoding plan, not yet a verified equivalence proof. #343 and the P1–P5 claim ledgers must confirm exact decisions and strike mismatches.

### Consequence
Within a single domain, the shared calculus may add no expressive power beyond the existing gate. P8's possible incremental contribution is therefore:

- typed composition across domains;
- explicit anti-laundering guarantees;
- common revocation/dependency semantics;
- analysis of protected roots and delegation;
- reusable hostile cases involving cross-module authority.

A vocabulary-level unification is insufficient for a separate paper.

## 9. Soundness target

### Definition 11 (contract-relative soundness)
Let \(\llbracket\mathcal C_a\rrbracket\) be the intended semantic condition under which action \(a\) is permitted. The calculus is sound for contract family \(\mathfrak C\) when

\[
\Gamma\vdash\mathsf{Auth}(a)
\Rightarrow
\llbracket\mathcal C_a\rrbracket(E)=\mathsf{permitted}
\]

for every \(\mathcal C_a\in\mathfrak C\).

The general soundness proof will require each trusted base rule and registered coercion to be semantically sound. Theorem 1 supplies the syntactic non-laundering part but does not prove that trusted issuers or coercions are correct.

## 10. `CANNOT_CHECK`, refusal and rejection

### Definition 12 (terminals)
For action \(a\):

- `AUTHORIZED`: all hard obligations and authority checks pass;
- `REJECTED`: a blocking defeater or violated hard obligation is established;
- `CANNOT_CHECK`: a required hard judgment is unknown/conflicting/unavailable;
- `GATHER_MORE`: an admissible evidence-acquisition action exists and is separately authorized;
- `UNAUTHORIZED`: the action may be feasible/supported but has no valid authority derivation;
- `REVOKED`: prior authorization depends on an invalidated premise.

These terminals must not be collapsed into a binary score during evaluation.

## 11. Deterministic hostile-check obligations

The finite checker associated with this core must verify at least:

1. cross-domain judgments cannot authorize without a registered coercion;
2. scope narrowing is allowed but widening is not;
3. the additive blocker counterexample exists for arbitrary finite penalties;
4. revocation propagates exactly through the descendant closure;
5. a candidate-controlled constant-accept policy defeats internal self-certification;
6. P1–P5 embedding fixtures reproduce their declared toy decisions;
7. authority-laundering attack fixtures fail closed.

No LLM API is required.

## 12. Nearest-work pressure and nonclaims

This core does **not** claim novelty for:

- deontic logic, input/output logic or dynamic action logics;
- authorization/access-control calculi;
- delegation, scope restriction or revocation;
- abstention/selective prediction;
- provenance-based action guarding;
- runtime shielding and policy enforcement;
- capability-versus-permission governance frameworks;
- P4's protected scientific-authority transition.

The candidate residual is narrower:

\[
\text{typed authorization across heterogeneous epistemic actions}
+
\text{non-compensatory obligations}
+
\text{cross-module anti-laundering}
+
\text{dependency revocation}
+
\text{protected-root semantics}.
\]

Recent capability-versus-permission governance work increases the novelty burden: P8 must establish a formal and experimentally discriminating calculus, not merely the conceptual distinction.

## 13. What this formal core establishes now

It establishes elementary syntactic and algebraic results under the proposed definitions. It does not yet establish:

- semantic soundness of all trusted issuers/coercions;
- novelty over deontic/authorization/policy-composition literature;
- exact equivalence of the P1–P5 embeddings;
- practical superiority over independent gates;
- that authority contracts capture all relevant norms;
- peer-review readiness or separate-paper status.

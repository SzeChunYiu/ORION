# ORION-18 formal core V2 — closed theory

**Candidate paper:** A Theory of Epistemic Authority for Autonomous Science  
**Theory terminal:** `CLOSED_V2`  
**Novelty / separate-paper terminal:** `CANNOT_CHECK`  
**Date:** 2026-08-18

V2 closes the full derivation-typing, coercion-composition, revocation and decomposition gaps in V1. It also records a negative theorem: a shared calculus is not intrinsically more expressive than a correctly typed product of domain gates when both receive the same global cross-domain rules.

## 1. Effect domains and typed judgments

Let `D` be a finite set of epistemic effect domains. The ORION embedding uses

\[
D_0=\{REFRAME,SEARCH\_STOP,MAP\_MERGE,ASSERT,SELF\_MODIFY\}.
\]

### Definition 1 — effect request

\[
e=(id,d,op,scope,payload,epoch).
\]

Capability to construct or execute `e` is not authority to commit it.

### Definition 2 — judgment type

Every authority-relevant judgment has type

\[
\tau=(d,k,s,c,t),
\]

where `d` is effect domain, `k` judgment kind, `s` scope, `c` content/evidence identity contract, and `t` epoch/version.

A judgment is written `j:\tau`. `PASS`, `SUCCESS`, `HIGH_CONFIDENCE` or `VERIFIED` without these coordinates is not authority currency.

### Definition 3 — obligation

A hard obligation is

\[
o=(id,\tau_o,Prem_o),
\]

where `\tau_o` is the exact judgment type capable of discharging the obligation and `Prem_o` are additional non-compensatory premises.

### Definition 4 — authority context

\[
\Gamma=(J,O_h,O_s,G,C,R,\mathcal P,H),
\]

with active judgments `J`, hard and soft obligations `O_h,O_s`, grants/roots `G`, typed coercion registry `C`, revocation state `R`, derivation/provenance structure `\mathcal P`, and immutable history `H`.

## 2. Full evidence-to-obligation typing

Typing only the final authorization certificate is insufficient: authority can already be laundered if foreign-domain evidence is converted into an untyped intermediate `SAT` token.

### Definition 5 — direct discharge

A valid available judgment `j:\tau_j` directly discharges obligation `o` only when

\[
\tau_j=\tau_o
\]

and all additional premises of `o` hold.

Missing required evidence yields `CANNOT_CHECK`; an available judgment with incompatible type or an established blocker yields `DENIED` for that attempted discharge.

## 3. Typed coercions

### Definition 6 — coercion

A coercion is a protected rule

\[
c:\tau\rightharpoonup\tau'
\]

with issuer/root, semantic premises, lineage and validity interval. It may change domain, kind, scope, content contract or epoch only as explicitly stated by the rule.

### Definition 7 — composable coercion path

`c_1;\ldots;c_n` is composable only if the **entire output type** of each rule equals the required input type of the next:

\[
out(c_i)=in(c_{i+1}).
\]

Matching domains alone is insufficient.

### Definition 8 — derived discharge

Judgment `j:\tau` discharges obligation `o:\tau_o` through coercions iff there exists a valid composable protected coercion path mapping `\tau` exactly to `\tau_o` and every coercion premise remains valid at the commit epoch.

## 4. Type preservation and anti-laundering

### Definition 9 — authority laundering

A derivation launders authority when a judgment contributes to discharge/authorization in a type different from its own without an explicit valid coercion path connecting the complete types.

### Theorem 1 — typed anti-laundering

Assume ordinary inference rules preserve judgment type and the only rules permitted to change type are registered coercions. Then no derivation can use `j:\tau` to discharge `o:\tau_o`, `\tau\neq\tau_o`, without a valid composable coercion path from `\tau` to `\tau_o`.

#### Proof

Induct on derivation height. Axiom/direct-discharge leaves the type unchanged. Every ordinary inference rule preserves type by premise. Therefore the first derivation node whose type differs from its ancestor must be a coercion application. Repeating the argument at every subsequent type change yields a composable coercion path ending at `\tau_o`. `\square`

### Corollary 1.1 — domain non-fungibility

With an empty cross-domain coercion registry, a judgment from one domain cannot discharge a hard obligation in another domain even if both are labeled `PASS` or `SAT`.

### Corollary 1.2 — scope/kind/content non-fungibility

Even when two adjacent coercion rules share a domain boundary, they do not compose if their kind, scope, content or epoch interfaces differ.

This repairs the domain-only reachability weakness identified by hostile review.

## 5. Non-compensatory authorization

### Definition 10 — authorization rule

For effect request `e`, authorization requires:

1. every `o\in O_h(e)` is discharged by a typed derivation;
2. no active blocker applies;
3. a valid grant/root covers the exact effect scope;
4. every derivation and grant is fresh at the commit epoch;
5. the effect is bound to the same identity/content/payload being committed.

Soft preferences may rank already authorized effects but cannot discharge a hard obligation.

### Proposition 2 — finite additive penalties cannot represent an unbounded absolute blocker

For score

\[
S=\sum_iw_ix_i-Mb
\]

with finite `M`, fixed threshold and unbounded possible positive evidence, there exists positive evidence large enough to cross the threshold while `b=1`.

#### Proof

Choose positive contribution greater than `threshold+M`. `\square`

The proposition does not say a bounded fixed-dimensional scoring system cannot emulate a veto with a dominating weight. It states why an extensible evidence stream requires a non-compensatory gate if a blocker is semantically absolute.

## 6. Three non-success terminals

### Definition 11 — `AUTHORIZED`, `DENIED`, `CANNOT_CHECK`

- `AUTHORIZED`: every hard obligation is discharged, no blocker applies, grant is valid and commit-time bindings are fresh.
- `DENIED`: an available fact establishes a blocker, incompatible type, invalid grant, stale epoch, revoked premise or failed mandatory condition.
- `CANNOT_CHECK`: a mandatory premise cannot currently be established or refuted because required evidence/state is unavailable.

`CANNOT_CHECK` is not refusal-by-policy and is not resource `DEFER`.

### Proposition 3

Collapsing `CANNOT_CHECK` into `DENIED` loses the distinction between “go obtain/restore the missing premise” and “the proposed effect is established to be impermissible.” Collapsing it into `AUTHORIZED` is unsound by Definition 10.

## 7. Derivation families and revocation

A simple dependency graph loses the fact that an authorization certificate can have multiple complete independent derivations.

### Definition 12 — support family

For certificate `\kappa`, let

\[
\mathcal S(\kappa)=\{S_1,\ldots,S_m\}
\]

be a family of finite premise sets. `\kappa` is currently derivable iff

\[
\exists S_i\in\mathcal S(\kappa): \forall x\in S_i,\ Valid(x).
\]

This is a DNF/hypergraph view of authorization lineage.

### Definition 13 — revocation

Revoking premise `x` removes it from the active premise set and recursively re-evaluates every certificate/intermediate judgment whose support family references `x`.

### Theorem 4 — exact alternative-derivation revocation

After any set `R` of premises is revoked, certificate `\kappa` remains valid iff at least one complete support set `S_i\in\mathcal S(\kappa)` is disjoint from the invalid/revoked premises and all of its members remain valid.

#### Proof

This is exactly the support-family validity definition after deleting invalid premises. If a complete support set remains, it is a valid derivation. If every support set contains an invalid premise, every complete derivation is broken. `\square`

### Corollary 4.1

Revoking one ancestor must not invalidate a certificate that retains another independent complete derivation.

### Corollary 4.2

A plain descendant graph is sound only when its edge semantics encode derivation necessity or when it is paired with the support-family information needed to distinguish AND from OR support.

## 8. Commit-time freshness

### Definition 14 — commit-time authorization

An effect is commit-time authorized only if the exact grant, obligation discharges, coercion premises, scope/content binding and relevant policy state remain valid immediately before the durable effect commits.

### Proposition 5 — post-hoc refusal is not preventive authorization

If an irreversible effect commits at epoch `t` and a blocker/refusal is discovered only at later epoch `t'>t`, the later judgment cannot make the prior commit pre-effect authorized.

### Proposition 6 — stale authorization does not transport automatically

An authorization certificate at epoch `t` is not valid for a request at `t'` when any premise named by its freshness contract may have changed and no freshness/revalidation proof is supplied.

These propositions are parented by ongoing/commit-time authorization work; ORION-18 uses them as constraints rather than novelty claims.

## 9. Protected roots and self-promotion

### Definition 15 — protected root

A root is protected relative to candidate effect `e` when `e` cannot rewrite the root, the policy deciding root validity, or every evidence item read by that policy.

### Proposition 7 — unprotected self-admission is vacuous

If a candidate controls its own admission predicate and all evidence seen by that predicate, internal acceptance does not guarantee any external promotion property.

#### Proof

The candidate can choose a constant-accepting predicate or manufacture evidence satisfying its own acceptance branch. `\square`

This embeds ORION-15's protected external-attestation boundary rather than replacing it.

## 10. Product decomposition theorem

A major question is whether one shared authority calculus is intrinsically stronger than separate typed gates. It is not.

### Definition 16 — typed product implementation

A typed product implementation contains one gate `G_d` per effect domain. All gates use the same definitions of hard-obligation discharge, grant validity, blockers, epoch freshness, protected coercion registry and global derivation/revocation store.

The shared implementation evaluates the same rules in one namespace.

### Theorem 8 — shared/product decision equivalence

For every request `e`, evidence context `\Gamma` and coercion/revocation state, a shared calculus and a typed product implementation satisfying Definition 16 return the same one of `AUTHORIZED`, `DENIED`, `CANNOT_CHECK`.

#### Proof

Both implementations evaluate the same finite conjunction: each hard obligation is discharged by the same direct/coercion relation; the same blockers, grants and freshness facts are consulted; and revocation validity is computed from the same support families. Domain partitioning changes code organization but none of the premises or inference rules. Therefore the decisions are extensionally equal for every input. `\square`

### Corollary 8.1 — centralization is not ORION-18's contribution

Any empirical claim that a shared calculus outperforms independent gates must compare against a product baseline with the same typed cross-domain registry and global revocation semantics. Weak independent scalar thresholds are not a sufficient baseline.

### Corollary 8.2 — where a difference can exist

A behavioral difference requires an actual semantic difference, such as missing cross-domain coercion rules, inconsistent obligation schemas, incomplete shared revocation lineage, divergent freshness rules, or implementation defects. The paper therefore studies **cross-domain epistemic discharge interfaces**, not centralization itself.

## 11. Scientific-obligation discharge versus generic authorization

Authorization frameworks can establish that a principal may perform an operation under a policy. Scientific authority additionally requires that the policy's hard epistemic obligations correspond to the scientific judgment being made.

### Definition 17 — scientific discharge interface

A scientific discharge interface explicitly binds an action/effect to the target scientific obligation type: for example coverage for a task-completion claim, referent/measurement compatibility for a merge, independent verification for scientific assertion, or protected fresh transfer for self-modification promotion.

### Theorem 9 — generic grant does not entail scientific discharge

There exist contexts in which a valid generic permission grant covers effect `e` but a mandatory scientific obligation for `e` is not discharged; therefore generic authorization alone does not imply `AUTHORIZED` under the ORION-18 scientific rule.

#### Proof by construction

Give `e` a valid in-scope grant and no blockers. Let `O_h(e)` contain one scientific obligation `o` whose required typed evidence is absent. Definition 10 yields `CANNOT_CHECK`, not `AUTHORIZED`, despite the valid generic grant. `\square`

This theorem states a separation of policy layers, not that security authorization systems are defective: the additional obligation exists because the scientific effect semantics demand it.

## 12. ORION-11–ORION-15 embeddings

ORION-18 treats the five existing gates as protected special cases:

- `REFRAME`: ORION-11 responsibility and dependent-reopening authority;
- `SEARCH_STOP`: ORION-12 route/task stopping and censored/open coverage;
- `MAP_MERGE`: ORION-13 referent/context/construct/measurement compatibility;
- `ASSERT`: ORION-14 protected content-bound evidence and independent verification;
- `SELF_MODIFY`: ORION-15 protected evaluator, fresh transfer, negative history and no-self-promotion.

The existing candidate branch includes executable selected native-decision fixtures calling live ORION implementations. ORION-18's formal claim is conservative: a domain instantiation is acceptable only if it reproduces the native gate decisions; otherwise the supposed generalization is wrong.

## 13. Donor ownership

ORION-18 does not claim novelty for:

- deontic/action/input-output logics;
- authorization/query logics, delegation and revocation;
- UCON-style ongoing authorization, obligations, conditions or mutable attributes;
- typed effects and policy traces;
- evidence-backed permission graphs/SMT authorization;
- multi-authority governance and authorization propagation;
- commit-time/stale-authorization control;
- abstention/selective prediction;
- provenance/source-aware factuality and execution provenance;
- ORION-14 scientific-authority promotion or ORION-15 no-self-promotion.

These are donors or parent fields. The ORION-18 object is the explicit type discipline at the **interfaces between heterogeneous scientific obligation domains**.

## 14. Executable support

`formal/check_theory_closure_v2.py` deterministically checks:

- all 25 source-domain/target-domain direct-discharge pairs;
- a scope-incompatible coercion chain that domain-only reachability would accept;
- valid positive coercion and untrusted-coercion controls;
- alternative-derivation revocation;
- `AUTHORIZED`/`DENIED`/`CANNOT_CHECK` distinctions;
- hard-blocker versus finite additive scoring cases;
- 160 shared-calculus/product-gate equivalence cases;
- stale-epoch/post-hoc-refusal boundary;
- self-promotion protected-root boundary.

## 15. Completed residual

The theory-complete ORION-18 object is

\[
\boxed{
\text{full-derivation epistemic typing}
+
\text{non-compensatory scientific obligations}
+
\text{exact typed coercion composition}
+
\text{alternative-derivation revocation}
+
\text{commit-time protected authority}
}
\]

with two complementary results:

1. foreign success/evidence is non-fungible without a typed discharge/coercion derivation;
2. a shared implementation gains no intrinsic expressivity over an equally typed product implementation.

Thus a future separate-paper claim must be about the scientific obligation/coercion interface, verification economy, consistency, auditability, or defect reduction—not generic permission and not centralization.

## 16. Final theory terminal

There are no remaining mathematical `THEOREM TARGET` placeholders in V2.

- `P8_THEORY = CLOSED_V2`
- `P8_NOVELTY = CANNOT_CHECK_UNTIL_LITERATURE_CLOSURE`
- `P8_SEPARATE_PAPER = CANNOT_CHECK_UNTIL_STRONG_BASELINE_DISCRIMINATOR`

If the strong typed-product baseline remains behaviorally equivalent in all relevant evaluations, the correct scientific disposition is to merge ORION-18 into ORION-14/programme synthesis while retaining this theory as the general interface theorem. That is a completed result, not a failed theory.

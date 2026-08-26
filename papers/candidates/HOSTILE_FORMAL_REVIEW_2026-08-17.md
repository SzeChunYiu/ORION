# ORION-16–ORION-18 hostile formal review — 2026-08-17

**Reviewed programme snapshot:** `999abd4899f3fed906ba024ae8ecd775a69b6560`  
**Review terminal:** `HOSTILE_REVIEW_COMPLETE / FORMAL_FREEZE_BLOCKED / PROMOTION_CANNOT_CHECK`  
**Scope:** additive review of the current mathematical cores and deterministic checkers; no change to the five-paper flagship registry.

## Executive finding

The current ORION-16–ORION-18 programme is materially stronger than the original candidate
scaffold: it now includes donor assimilation, formal cores, larger finite
enumerators and explicit nonclaims. It should not be replaced by a parallel
rewrite.

The hostile review nevertheless found four formal-freeze blockers and several
major specification gaps:

| ID | Paper | Severity | Finding | Required disposition |
|---|---|---|---|---|
| ORION-16-H1 | ORION-16 | blocker | `Desc_D(X)` is strict while `X` may contain certified claims. A directly changed certified root with no outgoing edge remains certified. | Restrict changes to non-certified coordinates, or use `(X ∩ Q_certified) ∪ Desc_D(X)` as the affected set; update proof and checker. |
| ORION-17-H1 | ORION-17 | blocker | The strict-expressivity witness permits `T'` to add a new goal state. This proves only that an unconstrained larger model can solve more tasks. | State strictness over a fixed latent frame with a support-preserving observation/representation refinement and no new sensing, states, transitions or goals. |
| ORION-18-H1 | ORION-18 | blocker | The main checker types one authority judgment but represents hard obligations as unbound `SAT` strings. It therefore does not test evidence-domain laundering into obligation satisfaction. | Bind each satisfaction to typed evidence and check the complete source-domain × target-domain matrix. |
| ORION-17-H2 | ORION-17 | major | The negative direction of support transport constructs a falsifying target whenever a preservation proof is absent, but this needs a richness/ambiguity premise. | Add that premise, or state fail-closed reopening as a policy rule rather than an unconditional semantic theorem. |
| ORION-18-H2 | ORION-18 | blocker | Domain-only coercion reachability ignores edge premises, scope maps, content identity and epoch. Individually registered but non-composable coercions can form an invalid path. | Define typed path composition and require every adjacent output/input contract to match. |
| ORION-18-H3 | ORION-18 | major | A simple descendant graph does not by itself represent alternative derivations for the same certificate. | Use derivation identities or an AND/OR dependency hypergraph; preserve a certificate while any complete independent derivation survives. |
| ORION-18-H4 | ORION-18 | major | The main checker returns a Boolean and does not exercise the manuscript's `DENY` versus `CANNOT_CHECK` distinction. | Freeze a three-terminal executable semantics and add hostile missing-evidence, mismatch and blocker cases. |
| ORION-16-H2 | ORION-16 | major | The graph-only minimality theorem has no certificate-aware companion. | Keep graph-only minimality, then add a separate protected preservation-certificate operator; never allow a changed root to self-preserve. |
| ORION-16-H3 | ORION-16 | major | The residual-obligation fixture preserves a set by construction rather than testing composition/discharge authority. | Model emitted, requested and authorized discharges explicitly. |

“Blocker” here means the relevant formal core should not be frozen at V1; it
does not mean the candidate programme should be terminated.

## Role-separated deliberation

### Formal epistemologist / knowledge-representation role

The ORION-16 root omission is a quantifier/domain mismatch, not merely an
implementation detail. The formal state allows dependency elements from
`C ∪ Q`, the changed set is not restricted to `C`, and the reopening operator
uses a strict downstream closure. The one-node case therefore invalidates the
current unrestricted statement. The cleanest repair is to define an affected
closure containing changed certified claims themselves.

For ORION-17, “topology change” must be represented by a relation between two views
of the same latent problem before it can discriminate against fixed-space
navigation. Otherwise adding a goal state to `T'` makes the theorem true by
construction while leaving the scientific mechanism unidentified.

### Programming-languages / formal-methods role

The larger upstream ORION-16 enumerator remains valuable and should be retained. The
secondary checker is deliberately smaller because it targets dimensions the
large enumerator abstracts away: certification at changed roots, protected
preservation proofs and authorized residual-obligation discharge.

The review distinguishes three evidence classes:

1. general proof under explicit premises;
2. exhaustive finite enumeration in the encoded fragment;
3. constructive counterexample to an over-broad statement or checker model.

Counts are never treated as empirical sample sizes.

### Epistemic-navigation role

The replacement ORION-17 witness fixes the latent states, transition relation, goal
set and retained raw feature. The old chart aliases two starts requiring
opposite actions; no stationary policy over the old observation quotient solves
both. A legal refinement splits the alias using already retained support and
then succeeds. This proves strictness only relative to the frozen policy class,
which is the honest scope.

The review also separates “no preservation proof is available” from “there
exists a compatible target in which preservation fails.” The latter needs a
completion-richness premise analogous to the corrected stopping theorem.

### Authorization / capability-security role

ORION-18 must type the entire derivation, not only the final grant. A foreign-domain
piece of evidence cannot become a target-domain obligation satisfaction through
an untyped `SAT` cell. Likewise, a sequence of registered coercion domain edges
is not automatically a valid coercion path; scope, content, epoch and edge
premises must compose.

Revocation requires OR structure. If certificate `κ` has derivations through
`e_A` or `e_B`, invalidating `e_A` should not revoke `κ` while the complete
`e_B` derivation remains valid. A plain reachability closure over certificate
nodes over-revokes unless derivation alternatives are represented.

### Scientific editor / novelty auditor role

None of these repairs establishes novelty. They improve internal validity and
sharpen the residuals:

- ORION-16: certificate-aware epistemic effect/repair composition, not generic graph
  reachability;
- ORION-17: obligation-preserving refinement of a scientific representation under
  fixed latent support, not arbitrary graph enlargement;
- ORION-18: full-derivation typing and anti-laundering across scientific effect
  domains, not permission logic in general.

The correct programme response is to absorb the repairs, rerun exact overlap
and nearest-work pressure, and preserve the existing merge/kill rules.

## Executable review results

The additive standard-library package is in `hostile_review_v1/`.

Expected result on the frozen tranche:

- **12 unit tests:** all `OK`;
- **11 review records / 80 encoded cases:** no unexpected `FAIL`;
- ORION-16: one exact counterexample plus protected-certificate and residual-obligation checks;
- ORION-17: two counterexamples plus representation-only strictness and stop-terminal checks;
- ORION-18: a 25-case evidence-domain matrix, one coercion-composition counterexample,
  alternative-derivation revocation and terminal separation.

`COUNTEREXAMPLE_CONFIRMED` is an expected constructive terminal, not a failed
run.

Checked-in report file SHA-256: `db70fea4918918841bade760d3b12e87ec20a90547d4c919567114918092688a`.
The clean-copy replay and exact commands are recorded in `hostile_review_v1/LOCAL_VALIDATION_2026-08-17.md`.

## Exact manuscript changes recommended

### ORION-16

Replace the affected set used by selective reopening with either:

\[
\operatorname{Affected}_D(E,X)
= (X\cap Q_{cert}(E))\cup \operatorname{Desc}_D(X),
\]

or explicitly restrict `X` to mutable non-claim coordinates and state how a
claim-content mutation changes status before reopening. Theorem 1 and Theorem 2
must use the same convention. Add a certificate-aware corollary in which only
protected, evidence-bearing proofs may preserve downstream certification;
changed roots are never preserved by that corollary.

### ORION-17

Replace the current strict-expressivity headline with a theorem over a latent
frame `L` and two observation/representation quotients `q` and `q'`, where
`q'` refines `q` using already retained support and leaves the latent state,
transition, goal and evidence identity fixed. State the policy class against
which strictness is claimed.

For support transport, split the result:

1. a positive preservation theorem when every required support/semantic map is
   supplied; and
2. a fail-closed rule, or an impossibility theorem only under an explicit
   target-completion richness premise.

### ORION-18

Strengthen anti-laundering from “authority-bearing premises preserve domain” to
“every premise used to discharge a target-domain hard obligation is either
properly target-typed or connected by a valid protected coercion derivation.”
A coercion derivation must carry source/target kind, scope map, content identity,
epoch and proof obligations at every step.

Represent revocation over derivations rather than only certificate reachability:
a certificate survives exactly when at least one complete non-revoked
derivation remains. Freeze `AUTHORIZED`, `DENIED` and `CANNOT_CHECK` as distinct
checker outputs.

## Programme status after this review

- **ORION-16:** formal core remains promising, but V1 reopening is not freeze-ready
  until ORION-16-H1 is repaired.
- **ORION-17:** the changing-representation residual remains promising; the
  observation-refinement version is substantially more discriminating than
  arbitrary chart enlargement.
- **ORION-18:** the typed-calculus residual survives conceptually, but the checker must
  type evidence discharge and coercion composition before anti-laundering can
  be treated as executable support.

All three remain candidates. Literature saturation, donor-faithful embeddings,
prospective experiments, independent verification, final claim-ledger audit,
venue selection and submission-relative literature refresh remain open.

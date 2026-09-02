# Selective revalidation without authority amplification under change

**ORION-16 + ORION-18 — bounded merged formal manuscript V1**  
**Status:** `LOCAL_BOUNDED_FORMAL_DRAFT__PHASE2_EXTERNAL_STUDY_DEFERRED`  
**Controlling theorem object:** `A6_MERGED_THEOREM_OBJECT_V1.md`

## Abstract

When a certified dependency structure changes, two questions are easily conflated: which previously certified claims must be reopened, and whether a repair or revalidation step is allowed to create new authority. We separate these questions in a finite formal model. For a support-sound dependency graph, the affected set consists of directly changed certified claims and their certified descendants. A claim may be preserved only by an accepted exact-change proof binding the same authority domain and epoch; directly changed roots must be revalidated. Independently, an old authorization may be transported only within its bound domain and epoch. If a repair supplies no fresh authority-bearing premise, confinement implies that authorization cannot increase. We combine these properties into a selective-revalidation/non-amplification object and verify it with an implementation-independent finite checker over 64 ordered four-node DAGs, 8,640 selective-revalidation states, 96 authority states, and 48 information-equivalent donor states, together with hostile countermodels for omitted dependencies, self-preservation, epoch/domain laundering, and donor asymmetry. Donor subtraction leaves most component facts as standard or specialized instances; the bounded contribution is the composed repair-to-authority invariant and its explicit control boundary. We do not claim external scientific validation or superiority over an information-equivalent typed donor, which is required to tie exactly.

## 1. Problem

Systems that retain certificates or validated state across changes face two distinct risks. Reopening too much wastes work; reopening too little leaves stale certifications. Separately, a repair mechanism can accidentally be treated as if it created authority merely because it changed a derivation, epoch, domain, or obligation structure. The first problem is selective revalidation. The second is authority non-amplification.

The formal question is therefore:

> Given an exact declared change to a dependency graph, which certifications may be preserved, and under what conditions can a repair change an authorization terminal?

The contribution is intentionally bounded. It is not a new general theory of truth maintenance, provenance, authorization, capabilities, or assurance cases. Those are donor fields. The manuscript isolates the conjunction needed for repair under certified change.

## 2. Formal objects

Let `D=(V,E)` be a finite directed dependency graph, `C subseteq V` the currently certified claims, and `X subseteq V` the declared changed set. Let `Desc_D(X)` denote the strict descendants of `X`. Define the affected certified set

`A_D(C,X) = (X intersect C) union (Desc_D(X) intersect C)`.

Let `R` be accepted exact-change preservation/revalidation proofs. Such a proof must bind its subject, the exact changed set, authority domain, epoch, and an issuer outside the candidate transition's own authority.

A certificate is a tuple `k=(q,h,t,S,p)`, where `q` is the subject, `h` its authority domain, `t` its epoch, `S` its support/root record, and `p` is one of `AUTHORIZED`, `DENIED`, or `CANNOT_CHECK`. The last two remain epistemically distinct even though neither grants authority.

## 3. Selective revalidation

A member `q` of the affected set is preservable only if it is not directly changed and an accepted proof in `R` establishes invariance under exactly `X` while preserving the same domain and epoch. Directly changed certified roots cannot preserve their old certificate by continuity.

Define

`Reopen(D,C,X,R) = A_D(C,X) minus Preservable(D,C,X,R)`.

### Theorem 1 — selective revalidation safety

Assume the dependency graph is support-sound and each accepted preservation proof is sound for the exact declared change. Reopening or revalidating every member of `Reopen(D,C,X,R)`, while preserving only `Preservable(D,C,X,R)`, leaves no certification stale solely because of `X`.

This is a safety statement. Minimality requires an additional realizability/completeness premise for affected members not protected by accepted exact-change proofs.

## 4. Domain and epoch confinement

An old certificate may be transported as the same authority only within its bound domain and epoch. A transition to a different domain or epoch must either produce a new certificate from fresh, explicitly bound support/root evidence or remain non-authorizing.

Write `auth(AUTHORIZED)=1` and `auth(DENIED)=auth(CANNOT_CHECK)=0` only for the privilege order.

### Theorem 2 — confinement implies non-amplification under repair

For a repair step that supplies no new authority-bearing premise, if domain/epoch confinement holds then

`auth(p_after) <= auth(p_before)`.

Thus a repair cannot convert `DENIED` or `CANNOT_CHECK` into `AUTHORIZED` merely by changing domain, epoch, derivation path, or by moving into an obligation-free representation. Authorization may increase only when the transition records the fresh grant, root, discharged support, or equivalent authority-bearing premise that licenses the increase.

## 5. Information-equivalent donor control

To prevent a comparative claim from being manufactured by information asymmetry, candidate and ideal typed donor receive the same tuple

`I=(obligations_discharged, blockers_refuted, grant_valid, epoch_current, domain_bound)`.

The ideal donor authorizes iff all components are true, denies when a blocker is established under complete determination, and otherwise returns `CANNOT_CHECK`.

### Control theorem — exact tie under information equivalence

If candidate and ideal donor implement the same typed authorization relation over the same information tuple, their terminals are equal for every tuple. Any measured advantage therefore requires extra information, different assumptions, or an implementation defect; it is not evidence for a scientific advantage under information equivalence.

The exact-tie result is a control, not a novelty claim.

## 6. Independent finite verification

The independent checker imports no ORION transition functions, result receipts, expected outputs, or paper-local case files. It reconstructs the primitive finite model and verifies:

- 64 ordered four-node dependency DAGs;
- 8,640 selective-revalidation states;
- 96 authority-transport states;
- 48 information-equivalent donor states.

Hostile mutants must fail when they omit a changed root, omit a certified descendant, allow direct-root self-preservation, launder authority across epochs, launder unresolved state through a domain change, omit a donor coordinate, or give the candidate hidden extra information.

This establishes internal consistency and catches specified failure modes. It is not external scientific adjudication.

## 7. Donor subtraction and surviving scope

The donor matrix covers authorization/delegation logic, provenance algebras, truth-maintenance and belief-revision systems, proof-carrying action/authorization, typed effects/capabilities, and assurance cases. After adversarial donor subtraction, the result-level tally is 6 `DONOR`, 5 `SPECIALIZATION`, and 1 `SURVIVING_NEW_CONSEQUENCE` among the twelve previously tracked component results.

Accordingly this manuscript does not market the components as independently novel. Its bounded paper-level object is the composition: exact-change selective revalidation is coupled to a non-amplifying authority boundary, with an information-equivalent donor tie that prevents a false comparative advantage.

This composition remains subject to submission-date primary-source review. A source establishing the same composed theorem directly would narrow or eliminate the novelty claim without invalidating the formal correctness result.

## 8. External Phase 2 is successor science, not a local filing blocker

The Tier-A stretch programme proposes an externally adjudicated study over public scientific authority/evidence packets. That study would test false promotion, valid admission, recheck work, per-stratum direction, and source-disjoint replication against authorization-only, provenance-only, verification-only, combined-donor, candidate, and information-equivalent donor baselines.

That programme is scientifically useful for a broad empirical claim, but it is not silently imported into this bounded formal manuscript. Until it is run, this paper claims only:

1. the formal selective-revalidation safety object under stated assumptions;
2. domain/epoch non-amplification in the absence of fresh authority;
3. the exact information-equivalent donor tie;
4. independent finite consistency/countermodel verification;
5. the donor-subtracted scope of the composed result.

It does **not** claim externally demonstrated reductions in false scientific promotion, real-world cost savings, or empirical superiority.

## 9. Limitations

The finite checker is exhaustive only for its declared finite model and does not prove completeness for arbitrary operational systems. Support-soundness and exact-change proof soundness are premises. The privilege-order bit does not collapse `DENIED` and `CANNOT_CHECK` epistemically. Novelty of the composed theorem is bounded by the current donor audit rather than an absolute global priority certificate. External authority adjudication remains unrun.

## 10. Conclusion

Selective revalidation and authority transport should be treated as separate but composable proof obligations. Under support-sound dependencies, exact-change preservation can safely reduce the reopen set. Under domain/epoch confinement, repair without a fresh authority-bearing premise cannot amplify authorization. An information-equivalent donor must tie exactly. The merged formal object and independent finite checker support a bounded specialist formal submission now, while the larger externally adjudicated authority study remains explicit successor science rather than a prerequisite invented after the formal result was obtained.

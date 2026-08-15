# Protected step verification — literature and development packet

**Status:** `UPDATED_BOUNDED_ARCHITECTURE_HYPOTHESIS` for protected step
verification; literature recall is **not certified** and ORION as a whole is
`NON_FLAT`.

**ORION subject:** `5894ac7814d194b3c60d9655af87ef2d9828d56c`

**RAKL mechanics source (read-only):**
`bd4ce50f48bbfd7d36e9a41ded9566f77d8105ca`

**Research date:** 2026-08-16

## 1. Scope and epistemic boundary

This packet answers one development question:

> What is the minimum protected lifecycle by which an atomic ORION step may
> advance canonical state, remain auditable, be reopened when support changes,
> and turn failures into candidate knowledge without letting the LLM or another
> candidate path certify itself?

It does **not** establish that:

- every ORION workflow atom has a valid domain evaluator;
- ORION has saturated the scientific-agent literature;
- an ORION answer is scientifically true;
- the current kernel is concurrency-safe;
- failure memory is safe against general poisoning;
- ORION is fully self-driving.

`/nature-academic-search` was unavailable in this environment. It was **not
simulated**, and no other search route is described as if it were Nature's
search service. The research instead used OpenAlex discovery, Crossref and
Semantic Scholar metadata resolution, exact DOI/arXiv resolution, accessible
full texts, official standards/RFCs and independent literature lanes. The
initial lightweight local corpus contains 350 OpenAlex discovery records across
14 query families, 41 paper full texts and 15 official specification
documents. A later primary-source delta added remote-attestation,
authorization, access-control, consistency and safe-update sources that were
absent from that corpus.

This packet keeps four evidence classes separate:

1. **Primary/normative evidence:** standards, RFCs, official specifications,
   peer-reviewed papers and directly inspected primary texts. These support
   source-attributed facts only.
2. **Local primary observations:** exact hostile reproductions against the
   pinned ORION subject. These establish behavior of that subject, not a
   general theorem about agent systems.
3. **Candidate/unreviewed evidence:** arXiv-only or not-yet-venue-verified
   reports, same-context reviews, open PRs, LLM/agent syntheses and transferred
   mechanics awaiting fresh ORION validation. These may generate hypotheses
   and tests but cannot mint authority.
4. **Design implications:** explicit ORION synthesis from the evidence. A
   design implication is not mislabelled as a quoted result or standard
   requirement.

The corpus and discovery metadata are search instruments, not authority.
Negative findings are retained explicitly rather than disappearing when a new
design is proposed.

## 2. Atomic question generator

A research machine cannot rely on an LLM remembering which questions to ask.
For every workflow step `s`, ORION should mechanically instantiate the product

```text
QuestionSet(s)
  = StepFacet(s)
  x {specification, state, evidence, evaluator, execution, assurance,
     transition, dependency, freshness, failure, optimization, storage}
  x {identity, scope, validity, missingness, attack, metric, handoff, reopen}
```

and deduplicate questions by their typed subject, not by prose similarity. A
single step can therefore generate hundreds of concrete questions; the full
workflow can generate thousands without asking an LLM to invent the audit
grammar. At minimum, every step must answer the following families.

### 2.1 Construct and specification

1. What exact construct or transition is this step intended to establish?
2. What is explicitly outside its scope?
3. What preconditions, invariants and forbidden losses are load-bearing?
4. What outcomes are valid alternatives to success?
5. What observation would falsify the step's claimed effect?
6. What downstream transition is blocked until this step is assured?
7. Is the step checking representation, prediction, mechanism,
   identification, decision, safety, or only execution conformance?
8. Which coordinates are conjunctive and which are alternative warrants?

### 2.2 Subject and state identity

9. What exact object is evaluated: proposal, artifact, claim, result or state
   transition?
10. What are the canonical subject hash and logical record identity?
11. What pre-state, post-state and workflow version are bound?
12. Is a receipt being replayed against a different mechanic, dimension,
    state, policy or epoch?
13. Does a supersession chain have one root, one tip and complete node
    coverage?
14. Is a derived projection being confused with its authoritative source?

### 2.3 Evidence and provenance

15. Which evidence item supports which obligation?
16. Is the evidence content-resolved, immutable and current?
17. Does the evidence establish relevance, or only content identity?
18. Are source, activity, agent, use, generation and invalidation represented?
19. Are required dependencies missing from the provenance graph?
20. Are two apparently independent sources aliases, shared descendants or one
    evaluator repeated under different labels?
21. Can authentic but unrelated evidence make the evaluator pass?
22. What result follows when required evidence cannot be acquired?

### 2.4 Oracle and evaluator

23. What necessary property or known result does the evaluator check?
24. Why does that operationalization measure the intended construct?
25. Who selected the evaluator, fixtures, rubric and policy?
26. Was the evaluator frozen before outcome access?
27. Is the evaluator artifact exact, versioned and reproducible?
28. Is evaluator authority scoped to this mechanic, dimension, claim schema,
    evidence role, environment and epoch?
29. What hidden, held-out, mutant, metamorphic and counterfactual cases test
    the evaluator itself?
30. Does a passing property prove correctness or only failure to falsify one
    necessary relation?
31. What is returned when there is no authorized evaluator?

### 2.5 Execution and assurance

32. Did the code/tool/experiment actually execute?
33. What exact inputs, environment, dependencies, budgets and chronology were
    observed by the host?
34. Are producer narrative, execution provenance and assurance represented as
    separate objects?
35. Can a successful process receipt mint scientific authority?
36. Was the result reproduced from artifacts in a clean environment?
37. Is best-of-`k` capability being confused with reliable pass-all behavior?
38. Are retries and external side effects idempotent?
39. Is a verifier's evidence-appraisal result being confused with the relying
   party's application-specific authorization decision?
40. What host-owned policy decides whether this exact proposed transition may
   occur after evidence appraisal?

### 2.6 State transition and storage

41. What exact authorization decision licenses the transition?
42. Is the expected ledger head still current?
43. Is the authority/policy/support snapshot used for the decision still
   current at commit?
44. Is append plus head comparison atomic across processes?
45. Can crash, disk-full or partial write create two accepted successors?
46. Can deterministic replay reconstruct the state under an exact reducer
   version?
47. Are corrections append-only, or has negative history been erased?
48. Is a multi-row logical transition recoverable if the process dies between
   rows?

### 2.7 Freshness, dependency and revocation

49. What appraisal-policy, authorization-policy, trust-root, evaluator,
   evidence and workflow epochs were used?
50. What are `valid_from`, `next_check_due`, `expires_at` and status time?
51. Has any dependency been superseded, invalidated or revoked?
52. Which claims/lessons depend on the invalid item?
53. Is there another complete live support set?
54. Does missing current-status information become `CANNOT_CHECK`?
55. What event reopens a previously closed step?
56. What nonce or minimum authority revision prevents an old decision from
   being applied to a newer transition?

### 2.8 Failure learning

57. Is the observed failure a mechanism failure, an evaluator failure, an
   instrument failure, a resource censoring event or still ambiguous?
58. What competing diagnoses survive?
59. Which discriminator can eliminate the most diagnoses per cost?
60. What is immutable observation and what is only a candidate lesson?
61. Did the guard actually execute on protected replay?
62. Is fresh transfer disjoint in task, run, split, evaluation epoch,
   variation and evidence lineage?
63. Was improvement measured under the pre-change protected invariants?
64. Did the lesson regress any protected prior-task family?
65. Is an active lesson still falsifiable through shadow/counterfactual traffic?

### 2.9 Optimization and stopping

66. What vector of quality, epistemic gain, cost, uncertainty, residual change
   and downstream effect is observed?
67. Which coordinate is non-compensatory?
68. Could the system optimize a proxy while degrading the intended construct?
69. Are empty or unknown lineages being treated as independent evidence?
70. Are meaning and relations flat, or only repeated labels?
71. Which independent route families were actually executed?
72. Did a new contradiction, coordinate, source family, evaluator version or
   artifact invalidation reopen the scope?
73. Is the stopping claim bounded to an explicit search universe and epoch?

These questions are schema instances. A mechanic-specific compiler must add
domain obligations, quantities, units, assumptions, boundary regimes and
known-answer cases before the step can be executed with authority.

## 3. Literature-derived formal model

### 3.1 Evaluation is a measurement argument

Represent a benchmark/evaluator contract as

\[
B=(C,T,D,E,M,V,W),
\]

where `C` is the scoped construct/claim, `T,D` the task items and sampling
frame, `E` the environment/tools/budget/chronology, `M` the metric or decision
rule, `V` the protected evaluator and `W` the warrant connecting measurements
to the construct. Hashes establish identity. Only a valid, authorized `W`
establishes relevance and scoped support.

For step `s`, state `x`, proposal `p`, evidence set `e` and protected policy
`pi`, the host forms an evaluation subject

\[
u=H(s,\mathrm{dimension},\mathrm{claimSchema},x,p,e,\pi,
    \mathrm{workflowEpoch}).
\]

The candidate may supply `p`; it may not supply the canonical evidence index,
evaluator registry, trust root, policy, chronology, signing key or ledger head.

### 3.2 Execution, attestation and authorization are distinct

An execution receipt records what ran:

\[
X=(input,environment,actions,artifacts,result,cost,time,status).
\]

Evidence appraisal produces a verifier result:

\[
R=(u,V,\pi_V,verdict,reasons,dependencies,freshness).
\]

The relying party then applies a separate application-specific authorization
policy to the exact requested action `q` under current host context `c_k`:

\[
D=Authorize(q,R,\pi_A,c_k)
  \in \{ALLOW,DENY,CANNOT\_CHECK\}.
\]

RFC 9334 calls these two procedures appraisal of Evidence and appraisal of
Attestation Results. They may be implemented by one entity, but they do not
become one semantic step. For the bootstrap, one durable assurance envelope
may contain both `R` and `D`; they must remain separately identified inside it.

`X.status = SUCCEEDED` does not imply `R.verdict = PASS`, and
`R.verdict = PASS` does not imply `D = ALLOW`. A signature establishes, at
most, origin/content integrity relative to a separately trusted key binding. It
does not establish truth, relevance, key authorization or permission to mutate
canonical state.

The minimum evidence-appraisal verdict algebra is

```text
PASS | FAIL | BLOCKED | CANNOT_CHECK
```

with additional operational states such as `STALE` or `REVOKED` represented
without rounding them into failure or success.

Epistemic missingness remains `CANNOT_CHECK`; the enforcement consequence is
no protected transition. It must not be relabelled `FAIL` merely to fit a
Boolean access-control API.

### 3.3 Non-compensatory admission

Let `O(u)` be the load-bearing obligations for the subject. Then

```text
PASS         iff every o in O(u) is SATISFIED by current authorized support
FAIL         iff at least one o in O(u) is demonstrably VIOLATED
CANNOT_CHECK iff no o is violated but at least one remains UNKNOWN
BLOCKED      iff a declared resource/dependency/governance precondition prevents evaluation
```

No count of satisfied obligations buys back a single forbidden loss. This is
the direct step-verification transfer of RAKL's directional applicability
contract, not a transfer of RAKL's historical results.

### 3.4 Alternative minimal support sets

A claim or lesson may have several independent warrants. Represent its support
as disjunctive normal form:

\[
Support(c,t)=\bigvee_j\bigwedge_{d\in D_j} Live(d,t).
\]

Dependencies inside one `D_j` are conjunctive; the `D_j` sets are alternative
warrants. Revocation of dependency `d` invalidates only support sets containing
`d`. The claim remains supported if another policy-satisfying live support set
survives. A flat list cannot represent this distinction.

### 3.5 Maturity is a vector

Do not collapse readiness to one confidence score. At minimum track

\[
M_s=(specification,evidenceBinding,checkerValidation,hostileTesting,
runtimeAssurance,evaluatorIndependence,operationalValidity).
\]

Advancement is a partial-order/non-compensatory decision under a frozen policy.
An implementation can be structurally mature but empirically unvalidated, or
well tested locally but lack independent operational assurance.

### 3.6 Failure learning is a two-transition process

Repeated failures may create only a pattern candidate:

\[
episodes\rightarrow candidatePattern.
\]

Behavior-changing activation is a separate transition:

\[
candidatePattern
\xrightarrow{protected\ replay+fresh\ transfer+assurance}
activeLesson.
\]

The raw episode, diagnosis revisions, candidate lesson, validation receipts,
activation, revocation and rollback events remain distinct immutable records.
Reflection prose, self-score, model confidence and recurrence are not promotion
authority.

### 3.7 Atomic, causally authorized canonical transition

Let `h` be the research-state ledger head and `k` the current revision of all
authorization-relevant state: evaluator registrations, appraisal and
authorization policies, evidence status, revocations and support dependencies.
A transition `t` is accepted only as an atomic operation

\[
CAS((h,k),t)=\begin{cases}
(h',k) & \text{if the durable current pair is exactly }(h,k),\\
STALE\_HEAD & \text{otherwise.}
\end{cases}
\]

For a local bootstrap, placing every authority-changing event in the same
canonical ledger permits one mandatory expected-head comparison to order both
state and authority. If authority state remains separate, the pair must be
compared and committed atomically. This is the local analogue of Zanzibar's
minimum-snapshot token: a decision must not use an authority snapshot older
than a causally prior revocation or policy change.

Hash chaining detects some later alteration but does not provide concurrency
atomicity, crash durability or non-equivocation. Atomic single-row append also
does not make a logical sequence of `ANSWER -> RECEIPT -> GRADING -> ROUND`
atomic. Canonical advancement therefore requires one durable transition
envelope, or an explicit transaction protocol whose uncommitted prefix is
ignored. Replay is valid only under an exact reducer/workflow version and must
fail on unknown or mismatched events.

### 3.8 Historical validity and current authority are different

A receipt can remain cryptographically intact while losing current operational
authority. Keep at least these predicates separate:

```text
signature_valid(receipt)
authorized_at_issue(receipt)
current_status(receipt, now) in {LIVE, STALE, REVOKED, UNKNOWN}
```

Historical replay reconstructs exactly what committed under the recorded
reducer and policy versions. Current revalidation is a separate projection.
When support expires or is revoked, ORION appends `REOPENED` or a compensating
event; it does not silently reinterpret or erase the historical transition.

### 3.9 Governed self-modification

An LLM may propose an evaluator, policy, guard or reducer artifact. It may not
activate that artifact or use the proposed version to certify itself.
Proof-carrying code and translation validation motivate the bounded protocol:

```text
untrusted proposed artifact
  -> exact artifact identity
  -> validation by the current protected root against a frozen contract
  -> protected regression/hostile tests
  -> transition authorization under the current policy
  -> durable activation event
  -> load only at a quiescent round/restart boundary
```

For a claimed policy refactor, establish equivalence on the protected request
universe. For a claimed tightening, establish
`Allow(new) subseteq Allow(old)`. Failure to prove the requested relation is
`CANNOT_CHECK`, not permission. Changes to the bootstrap root itself retain an
external/manual trust requirement; the root cannot eliminate that requirement
by signing its own replacement.

## 4. Converged architecture

```text
untrusted proposal
  -> host evidence admission and canonical resolution
  -> mechanic/claim/appraisal-policy-specific protected verifier
  -> typed evidence-appraisal / attestation result
  -> relying-party authorization under a separate host transition policy
  -> policy enforcement point for the exact requested action
  -> signed subject/pre-state/evidence/decision-bound assurance envelope
  -> atomic state-and-authority expected-head transition envelope
  -> deterministic projection/replay
  -> runtime monitoring, expiry, revocation and reopen
  -> later external witnessing for production non-equivocation
```

### 4.1 Protected host ownership

The candidate/LLM path may propose text, code, queries, diagnoses and candidate
lessons. The host owns:

- canonical source/evidence resolution;
- evaluator and policy registries;
- evaluator artifact identities and epochs;
- trust roots, signing identities, rotation and revocation;
- run chronology and hidden/held-out fixtures;
- the PIP-like authoritative evidence/attribute sources;
- the verifier and its evidence-appraisal policy;
- the relying-party transition-authorization policy;
- the policy-enforcement path, authority revision and ledger expected head;
- shutdown, rollback and protected prior-task invariants.

Python object construction alone is not a security boundary. The bootstrap
implementation can enforce a logical boundary only while candidate output is
inert serialized data and only trusted host code executes. If arbitrary
candidate Python executes in the same interpreter, it can inspect or mutate
keys, registries, policies, clocks, fixtures and modules; PEP 578 explicitly
does not provide a generic CPython sandbox. Production evaluator, signing,
policy, resource-control and witness roles therefore require stronger process,
OS, hardware or organizational boundaries according to the threat model.

### 4.2 Evaluator selection key

An evaluator registration is keyed at least by

```text
(mechanic_id, dimension, claim_schema_id, evidence_role_schema,
 appraisal_policy_id, appraisal_policy_epoch,
 evaluator_epoch, environment_class)
```

There is no fallback from an unknown key to a caller-supplied predicate. The
verifier result is `CANNOT_CHECK`. A separate authorization registration is
keyed to the exact action kind, subject/state schema, attestation-result schema,
authorization policy/epoch and authority revision. Unknown authorization is
also `CANNOT_CHECK` and cannot promote.

### 4.3 Receipt identity

The assurance receipt binds at least:

```text
receipt_id
subject_hash
logical_record_id + version/supersession parent
mechanic_id + dimension + claim_schema_id
claim/artifact content hash
pre_state_hash + proposed_post_state_hash
evidence record/content/role bindings
execution_receipt_id (reference only)
evaluator_id + evaluator_artifact_hash + evaluator_epoch
appraisal_policy_id + appraisal_policy_hash + appraisal_policy_epoch
attestation verdict + typed reasons
authorization action hash + decision
authorization_policy_id + authorization_policy_hash + authorization_policy_epoch
authority/support snapshot revision or freshness nonce
trust_root_version
valid_from + next_check_due + expires_at/status time
dependency/support-set identities
ledger expected head
signature + witnessed-log inclusion reference
```

The trust root and verification key are looked up from host-owned state; fields
inside the receipt cannot declare themselves trusted. In a one-process
bootstrap, an HMAC or in-process signing key provides accidental-tamper
detection and an export format under a non-compromised-host assumption. It does
not create independent assurance or non-repudiation against code controlling
that process.

## 5. RAKL mechanics transferred, with boundaries

All source inspection used the pinned Git object above. The live RAKL working
tree was not modified.

| RAKL mechanic | Pinned source | ORION transfer | Non-transfer |
|---|---|---|---|
| Directional structural witness `(mu, I+, I-, B, E, U)` | `publication/papers/paper-02-structural-mechanics/sections/02_contract.tex`; `src/rakl/structural_types.py` | Explicit preserved invariants, forbidden losses, boundary/QoI scope and three-valued obligations | A witnessed transfer is not target success or scientific truth |
| `LICENSED / REJECTED / CANNOT_CHECK` non-compensatory decision | same | `PASS / FAIL / CANNOT_CHECK` assurance semantics | Counts/scores cannot compensate for a violated obligation |
| Multi-axis authority/lifecycle | `AGENTS.md`; publication manuscripts | Vector maturity and partial-order readiness | Historical RAKL certificate or publication status |
| Immutable failure lattice and diagnosis revision | `src/rakl/failure_lattice.py`; `src/rakl/failure_learning.py` | Raw episode, competing diagnoses, append-only revisions and candidate boundary lessons | A repeated failure is not a verified causal diagnosis |
| Set-valued diagnosis and discriminators | `src/rakl/diagnosis_state_machine.py` | Preserve multiple causes; only evidence-bound transitions eliminate causes | `CANNOT_CHECK` cannot hide a unique asserted cause |
| Content/trust assurance separation | `src/rakl/authority_assurance.py` | Exact subject/evaluator/evidence/trust-backend bindings and fresh revalidation | Caller-named receipt or unequal hashes do not establish independence |
| Directional benchmark/decoys | `src/rakl/structural_benchmark.py` | Known-answer positives, high-semantic structural decoys, boundary sign/regime attacks | Deterministic conformance is not population performance |

The transfer rule is:

```text
RAKL mechanic
  -> reconstruct load-bearing obligations
  -> test against ORION's current failure
  -> adapt under ORION types and authority boundaries
  -> obtain fresh ORION assurance
```

RAKL provides prior mechanics and negative history, not ORION authority.

## 6. Current-main failure evidence

The following failures were reproduced on the exact ORION subject above and
are preserved under `research/failures/`.

1. **Host-check authority laundering.** Authentic weather evidence plus an
   answer-specific caller predicate verified a false P-versus-NP statement.
2. **Empty-lineage independence inflation.** At `3fdff9e`, two empty evidence
   lineages counted as two independent flat rounds and returned
   `BOUNDED_SATURATED`. PR #27 correctly replaced that overclaim with
   `A_PRIORI_FRAME_FLAT` and fixed `certifies_recall=False`. At the current
   subject it still reports `independent_flat_rounds=2` and permits a budget
   stop even though the lineages are unknown, so missingness-as-independence
   remains a narrower residual rather than a recall/saturation claim.
3. **Concurrent ledger race.** Sixteen concurrent writers created duplicate
   sequence-zero entries and an unreplayable ledger.
4. **Recurrence self-promotion.** Two caller-labelled split IDs promote a
   recurring failure signature to an active `VERIFIED_LOCAL` guard without
   protected replay or fresh transfer.

Instrument failures were kept distinct: a missing import path, a nonexistent
probe attribute and macOS multiprocessing from `<stdin>` did not count as ORION
failures. Corrected instruments then reproduced the system failures.

The merged source-identity work at PR #26 is useful: it canonicalizes DOI,
arXiv, OpenAlex, local and URL identities and binds a read decision to content,
schema and frame. It does not yet establish semantic claim extraction,
relevance, evaluator authority, persistence, dependency freshness or
saturation. PR #28 additionally separates provenance-bound record identity
from normalized content novelty, so mirrors no longer inflate discovery counts.
Neither change establishes relevance or evaluator authority.

PR #27 is also a material correction from the parallel Claude lane: consecutive
zero-growth rounds under a frozen frame are now named an a-priori frame-flat
budget rule, not bounded semantic saturation or recall evidence. This packet's
earlier `BOUNDED_SATURATED` label has now also been withdrawn: the later
attestation/authorization route added a load-bearing distinction that the first
frame missed. The current packet freezes only the bounded implementation
hypothesis in Section 11 and makes no literature-recall certificate.

The open PR #21 remains candidate work. Its RAKL transfer results, self-driving
labels and caller-provided evidence closures are not authority for this packet.

## 7. Evidence ledger: sources, negative findings and implications

### 7.1 Primary and normative evidence

The following are source-backed facts. The ORION consequences are deferred to
Section 7.5.

**Measurement and evaluators**

- Construct validity is an evidence argument, not a Boolean property of a
  benchmark (Jacobs and Wallach,
  [DOI 10.1145/3442188.3445901](https://doi.org/10.1145/3442188.3445901)).
- Finite tasks and metrics do not warrant an unscoped general-capability claim
  (Raji et al., [arXiv:2111.15366](https://arxiv.org/abs/2111.15366)).
- Oracle, metamorphic and property-based testing provide falsifiers and
  necessary relations, not general correctness proofs
  ([DOI 10.1109/TSE.2014.2372785](https://doi.org/10.1109/TSE.2014.2372785);
  [DOI 10.1145/3143561](https://doi.org/10.1145/3143561);
  [DOI 10.1145/351240.351266](https://doi.org/10.1145/351240.351266)).

**Attestation, authorization and access control**

- RFC 9334 assigns the Verifier the appraisal of Evidence under an appraisal
  policy and assigns the Relying Party a second appraisal of Attestation
  Results under its own application-specific policy. Authorization is an
  example of that latter decision. One entity may perform several roles, but
  the roles remain semantically distinct
  ([RFC 9334](https://www.rfc-editor.org/rfc/rfc9334),
  [DOI 10.17487/RFC9334](https://doi.org/10.17487/RFC9334)).
- RFC 9334 states that freshness narrows recentness but cannot remove the race
  in which state or policy changes immediately after evidence or an attestation
  result is produced. RFC 9711 requires every EAT use to provide a freshness
  mechanism and states that the message format does not prescribe the security
  level of claims
  ([RFC 9711](https://www.rfc-editor.org/rfc/rfc9711),
  [DOI 10.17487/RFC9711](https://doi.org/10.17487/RFC9711)).
- KeyNote derives authorization from a locally trusted policy, an exact action
  description and applicable credential assertions. A signed assertion is a
  credential/delegation input, not standalone permission
  ([RFC 2704](https://www.rfc-editor.org/rfc/rfc2704),
  [DOI 10.17487/RFC2704](https://doi.org/10.17487/RFC2704)).
- NIST ABAC separates authoritative attribute retrieval, policy decision,
  enforcement and policy administration as PIP, PDP, PEP and PAP functions;
  it also treats attribute authority, freshness and provenance as decision
  concerns
  ([DOI 10.6028/NIST.SP.800-162](https://doi.org/10.6028/NIST.SP.800-162)).
- NIST Zero Trust requires per-session dynamic authorization, continual
  reassessment and the ability to revoke/countermand a previously allowed path
  ([DOI 10.6028/NIST.SP.800-207](https://doi.org/10.6028/NIST.SP.800-207)).
- Fail-safe defaults, complete mediation, separation of privilege and least
  privilege are canonical protection principles
  ([DOI 10.1109/PROC.1975.9939](https://doi.org/10.1109/PROC.1975.9939),
  [primary text](https://web.mit.edu/Saltzer/www/publications/protection/Basic.html)).
- A service can misuse its own authority when caller-supplied designations and
  the service's ambient authority are confused (Hardy,
  [DOI 10.1145/54289.871709](https://doi.org/10.1145/54289.871709)).
- Cedar denies by default, makes forbids override permits, separates policy
  validation from authorization and supports symbolic policy-equivalence
  checks with counterexamples
  ([DOI 10.1145/3649835](https://doi.org/10.1145/3649835),
  [arXiv:2403.04651](https://arxiv.org/abs/2403.04651)).

**Provenance, freshness and transparency**

- W3C PROV represents entity/activity/agent, generation, use, derivation and
  invalidation; Workflow Run RO-Crate records execution facts but explicitly
  does not turn conformance into a reproducibility guarantee
  ([PROV-DM](https://www.w3.org/TR/prov-dm/);
  [PROV Constraints](https://www.w3.org/TR/prov-constraints/);
  [DOI 10.1371/journal.pone.0309210](https://doi.org/10.1371/journal.pone.0309210)).
- in-toto, SLSA, Sigstore, TUF, Certificate Transparency and OCSP separate
  artifact identity, authorized roles, provenance, expiry/revocation and
  transparency from semantic correctness
  ([in-toto](https://github.com/in-toto/docs/blob/master/in-toto-spec.md);
  [SLSA provenance](https://slsa.dev/spec/v1.1/provenance);
  [DOI 10.1145/3548606.3560596](https://doi.org/10.1145/3548606.3560596);
  [TUF](https://theupdateframework.github.io/specification/latest/);
  [RFC 9162](https://doi.org/10.17487/RFC9162);
  [RFC 6960](https://doi.org/10.17487/RFC6960)).
- Transparency additionally needs monitoring/witnessing; an operator's local
  append-only text is not non-equivocation
  ([USENIX Security 2009](https://www.usenix.org/legacy/event/sec09/tech/full_papers/crosby.pdf);
  [CoSi DOI 10.1109/SP.2016.38](https://doi.org/10.1109/SP.2016.38)).

**Atomic history, causality and replay**

- Linearizability requires each accepted concurrent operation to appear to
  take effect at one instant between invocation and response
  ([DOI 10.1145/78969.78972](https://doi.org/10.1145/78969.78972)).
- Zanzibar's “new enemy” examples show that a stale authorization snapshot can
  be incorrectly applied to newer content. Its minimum-snapshot token is stored
  atomically with a content version and bounds later checks to an at-least-as-
  fresh authorization snapshot
  ([USENIX ATC 2019](https://www.usenix.org/conference/atc19/presentation/pang)).
- Application crash consistency depends on subtle filesystem persistence
  properties that vary across filesystems; ALICE found 60 vulnerabilities in
  11 analyzed systems
  ([OSDI 2014](https://www.usenix.org/conference/osdi14/technical-sessions/presentation/pillai)).
- Event sourcing, deterministic workflow replay and build-system dependency
  work require ordered events, exact versions and complete dependencies
  ([Microsoft event sourcing](https://learn.microsoft.com/en-us/azure/architecture/patterns/event-sourcing);
  [Temporal events](https://docs.temporal.io/workflow-execution/event);
  [DOI 10.1145/3236774](https://doi.org/10.1145/3236774)).
- TMS, ATMS and provenance semirings support explicit justifications,
  retraction propagation and conjunctive/alternative support
  ([DOI 10.1016/0004-3702(79)90008-0](https://doi.org/10.1016/0004-3702(79)90008-0);
  [DOI 10.1016/0004-3702(86)90080-9](https://doi.org/10.1016/0004-3702(86)90080-9);
  [DOI 10.1145/1265530.1265535](https://doi.org/10.1145/1265530.1265535)).

**Safe generated change**

- Proof-carrying code lets an untrusted producer provide code and a proof while
  the receiver owns the safety policy and small proof checker. Its guarantee is
  relative to the correctness of that checker and policy
  ([DOI 10.1145/263699.263712](https://doi.org/10.1145/263699.263712),
  [author overview](https://people.eecs.berkeley.edu/~necula/pcc.html)).
- Translation validation checks every generated result against its source and
  refinement relation instead of trusting the generator globally
  ([DOI 10.1007/BFb0054170](https://doi.org/10.1007/BFb0054170)).
- Source inspection alone cannot establish that a running compiler/toolchain
  corresponds to that source
  ([DOI 10.1145/358198.358210](https://doi.org/10.1145/358198.358210));
  diverse double compilation offers one independently rooted detection method
  under stated assumptions
  ([DOI 10.1109/CSAC.2005.17](https://doi.org/10.1109/CSAC.2005.17)).
- PEP 578 states that repeated generic CPython sandbox attempts have failed and
  that Python audit hooks are not a sandbox
  ([PEP 578](https://peps.python.org/pep-0578/)).

### 7.2 Local primary observations

The four hostile reproductions in Section 6 are primary evidence about ORION
subject `5894ac7`: caller predicate authority laundering, empty-lineage
independence inflation, concurrent duplicate ledger heads and recurrence
self-promotion. Their scripts and raw outcomes justify regression tests. They
do not establish the prevalence of those failures in other systems, and a
later fix requires fresh reproduction against the new subject.

### 7.3 Candidate and unreviewed evidence

- The arXiv-only or not-yet-venue-verified scientific-agent reports in the
  local corpus—including recent 2025/2026 benchmark and failure reports—remain
  candidate evidence until venue/status and exact artifact claims are checked.
  They are valuable for attack and measurement hypotheses, not authority.
- AI Scientist, MLAgentBench, RE-Bench, ScienceAgentBench, CORE-Bench,
  PaperBench, AstaBench, AutoResearchBench, DeepResearch Bench and ResearchGym
  expose useful task decompositions and reliability failures, but none is an
  authorization framework for ORION
  ([arXiv:2408.06292](https://arxiv.org/abs/2408.06292);
  [arXiv:2310.03302](https://arxiv.org/abs/2310.03302);
  [arXiv:2411.15114](https://arxiv.org/abs/2411.15114);
  [arXiv:2410.05080](https://arxiv.org/abs/2410.05080);
  [arXiv:2409.11363](https://arxiv.org/abs/2409.11363);
  [arXiv:2504.01848](https://arxiv.org/abs/2504.01848)).
- Intrinsic self-correction, LLM-judge, memory-poisoning, continual-learning and
  theoretical self-modification reports generate hostile tests and boundary
  hypotheses; their reported outcomes do not directly verify an ORION
  implementation
  ([arXiv:2310.01798](https://arxiv.org/abs/2310.01798);
  [arXiv:2305.17926](https://arxiv.org/abs/2305.17926);
  [arXiv:2503.03704](https://arxiv.org/abs/2503.03704);
  [arXiv:1605.03142](https://arxiv.org/abs/1605.03142)).
- Open PR #21, same-context AI reviews, agent messages and this synthesis are
  proposals. The pinned RAKL sources contribute mechanics and negative
  history, not ORION results or authority.

### 7.4 Negative findings retained

The research falsified or failed to support these stronger claims:

1. A signature does not establish truth, relevance, evaluator registration or
   permission to transition state.
2. A verifier `PASS` is not the relying party's authorization decision.
3. A receipt cannot make its own key, policy, trust root, epoch or chronology
   authoritative by naming or signing them.
4. Freshness has no timeless Boolean value; a decision can become stale or
   revoked immediately after issue.
5. Hash chaining is not linearizable append, crash durability,
   non-equivocation or atomic multi-event commit.
6. Re-grading raw answers under new code is current revalidation, not
   deterministic historical replay.
7. Repeated failure is not a causal diagnosis and cannot activate a lesson.
8. Empty or unknown lineage is not independent evidence.
9. Same-process Python “privacy”, HMAC/signing and audit hooks are not a
   boundary against arbitrary code executing in that process.
10. A generated evaluator, policy or root cannot safely authorize its own
    activation.
11. Passing local tests, provenance conformance or an assurance-case schema is
    not scientific truth or general operational validity.
12. The searched frame does not certify literature recall or semantic
    saturation.

### 7.5 ORION design implications

These are synthesis, not claims quoted from the sources:

1. Keep execution provenance separate from an assurance envelope; inside that
   envelope preserve a typed attestation result and a distinct exact-action
   authorization decision.
2. Implement the bootstrap's Verifier and Relying Party in one host service
   only as a scoped convenience. Give them separate policies and records.
3. Place a PEP at every verified write-back edge. Raw checks and proposals may
   enter quarantined/provisional history but cannot mutate verified projection.
4. Resolve keys, roots, registrations, policy versions, chronology and
   evidence status from host-owned state. Never accept self-declared authority
   from the receipt or proposal.
5. Bind transition authorization to an authority snapshot. Prefer one ledger
   for state and authority events; otherwise CAS both heads atomically.
6. Persist one canonical transition envelope. Treat answer/grading/report rows
   as projections or ignore any incomplete transaction during replay.
7. Separate historical replay from live revalidation and append explicit
   reopen/compensation events.
8. Keep LLM output inert. Run generated code in a stronger isolation boundary
   before treating the Python bootstrap as adversarially protected.
9. Allow self-modification only below a pinned root and only after exact-
   artifact validation by the currently trusted version, protected regression
   tests, authorization and a quiescent activation boundary.
10. Add independent witnessing, protected keys, trusted time and organizational
    custody later; do not simulate them with local labels.

## 8. Frozen hostile-test contract

Production changes must be preceded by failing tests for at least:

1. authentic but unrelated evidence plus an answer-specific predicate;
2. a cryptographically valid receipt from an unregistered caller-created host
   identity;
3. caller-declared lane, chronology, policy, trust root or evaluator epoch;
4. a receipt that embeds and signs its own new trust root or policy epoch;
5. valid receipt replayed against a different mechanic, dimension, action,
   claim schema, evidence role or pre-state;
6. missing registered evaluator preserved as epistemic `CANNOT_CHECK` and no
   authorization;
7. verifier `PASS` followed by relying-party `DENY` for a stronger action such
   as waiver or guard activation;
8. stale, expired, revoked, future-dated, nonce-reused or wrong-epoch evidence,
   evaluator or attestation result;
9. report/prose success contradicted by executed artifacts;
10. position swap, renaming, verbosity padding, answer contamination and prompt
   injection against model-mediated judges;
11. tautological or irrelevant metamorphic relations;
12. hidden labels, hard-coded outputs and public-solution lookup;
13. held-out task families, counterfactuals and post-cutoff/canary items;
14. empty, partial, aliased and shared evidence lineages;
15. revoked dependency with one dead and one alternative live support set;
16. recurrence without protected replay/fresh transfer remains candidate;
17. guard replay where the guard was labelled but not executed;
18. critical prior-task regression despite average target gain;
19. two rounds authorized from the same state head, of which only one may
   commit;
20. evidence or policy revocation racing between appraisal and commit, with no
   stale authorization allowed to remain active;
21. current state head paired with a stale authority/support revision;
22. process death after an answer row but before assurance/round rows, with no
   incomplete logical transition admitted on replay;
23. retry/idempotency collision and failures before/after file sync, replace,
   directory sync and acknowledgement;
24. reducer/workflow-version mismatch during replay;
25. generated policy removing a forbid or broadening a permit, with a required
   counterexample or authority-expansion refusal;
26. generated evaluator/root replacing itself before judging its own update;
27. proof or validation receipt rebound to a different generated artifact;
28. bypass of the policy-enforcement path by a lower-level apply call;
29. same-process monkeypatch/key extraction/log rewrite as an explicit threat-
   boundary demonstration, not a test ORION pretends to resist; and
30. two self-consistent split histories, demonstrating why an external witness
   remains required for non-equivocation.

## 9. Frozen implementation hypothesis

### Slice A — protected assurance boundary

The smallest justified change is:

1. introduce a host-owned answer-assurance service with distinct verifier
   result and relying-party authorization stages;
2. key verifier selection to mechanic/dimension/claim/evidence/appraisal
   policy/state;
3. authorize the exact requested transition under a separate host policy and
   current authority snapshot;
4. persist both stages in a typed assurance envelope while keeping execution
   provenance separate;
5. place a policy-enforcement check at the verified write-back edge;
6. prevent raw caller predicates, lane labels and chronology claims from
   reaching `VERIFIED`;
7. leave missing/unknown protected evaluation at `CANNOT_CHECK` /
   evidence-bound provisionality;
8. retain host batteries as evaluator-validation tests, not as authority;
9. resolve trust roots, registrations, policies, chronology and status from
   host state rather than receipt fields;
10. bind promotion to exact action, subject, pre/post-state, evidence,
   evaluator, both policies and authority revision;
11. make recurring kernel failure guards `CANDIDATE` until the protected
   replay/transfer path is supplied;
12. deny independence credit to empty/unknown lineages.

### Slice B — atomic history

Only after Slice A passes its hostile suite:

1. implement atomic expected-head append with a process-safe critical section;
2. make expected state and authority revisions mandatory for canonical
   transitions;
3. commit answer, attestation, authorization and state change in one transition
   envelope, or define an explicit transaction/recovery protocol;
4. add stale-writer rejection and idempotency;
5. specify durability/crash recovery and fail acknowledgement on any sync
   error;
6. bind deterministic historical replay to an exact reducer/workflow version
   and keep current revalidation separate;
7. later add independently witnessed consistency checkpoints.

### Slice C — governed generated change

This is not part of the first bootstrap slice. Before ORION may activate its
own generated evaluator, policy, guard or reducer changes:

1. keep a pinned bootstrap root outside the candidate path;
2. validate the exact generated artifact with the current root;
3. run protected regression and hostile suites in a stronger isolation
   boundary;
4. check policy equivalence/non-expansion where applicable;
5. authorize and durably record activation; and
6. load the new version only at a quiescent boundary with exact rollback.

No distributed consensus, transparency service, general memory-defense system
or autonomous bootstrap-root rewrite belongs in these minimum slices.

## 10. Development-gate fields

### Atomic development atoms

```text
STEPVERIFY.SPEC        exact construct and obligation schema
STEPVERIFY.SUBJECT     subject/pre-state/post-state binding
STEPVERIFY.EVIDENCE    canonical content, role and relevance admission
STEPVERIFY.VERIFIER    protected registry, appraisal policy and evaluator lifecycle
STEPVERIFY.ATTEST      typed evidence-appraisal result
STEPVERIFY.AUTHORIZE   relying-party exact-action transition decision
STEPVERIFY.ENFORCE     complete mediation at verified write-back
STEPVERIFY.RECEIPT     execution/assurance separation and signed envelope
STEPVERIFY.SUPPORT     alternative minimal support-set DAG
STEPVERIFY.FRESHNESS   expiry, revocation and reopen
STEPVERIFY.FAILURE     episode/diagnosis/candidate/promotion separation
STEPVERIFY.SATURATION  positive lineage independence and bounded stopping
STEPVERIFY.LEDGER      atomic expected-head append and replay
STEPVERIFY.ATTACKS     known-answer, hostile and regression suite
```

### Basis challenge

Saturation could be false if:

- distributed-systems failures add a primitive not visible in single-host CAS;
- scientific-domain evaluators require richer warrant semantics;
- adversarial memory research finds a general attack on the host boundary;
- trusted-time, key-ceremony or organizational-custody constraints change the
  receipt semantics;
- the support DAG needs defeasible/non-monotonic relations beyond minimal
  alternative support sets;
- the current literature corpus missed a parent-domain terminology family.

The verifier/authorization delta proves that the earlier search did miss a
load-bearing parent-domain distinction. The packet was therefore reopened and
its earlier `BOUNDED_SATURATED` status withdrawn. No new flat-round count can
repair that historical overclaim; only the narrower implementation decision
below is frozen.

Potentially missing later parent domains include Byzantine/distributed
consensus, hardware roots/remote attestation, access-control capability systems,
scientific metrology by domain, privacy/retention law and production PKI
operations.

Prior searches could have missed relevant knowledge because the vocabulary
began with `LLM agent verification`, recent benchmark papers may cite only
near-domain work, paywalled/negative results are underrepresented and software
supply-chain terms can hide epistemic analogues.

### Reopen triggers

Reopen this packet if:

- any frozen hostile test passes incorrectly or a new attack class appears;
- evaluator, policy, trust root, evidence schema or workflow epoch changes;
- verifier-result and transition-authorization stages cannot be kept distinct
  in the implementation or an alternative formal model is required;
- a revocation/policy event can race commit without a common order or atomic
  state-and-authority comparison;
- a dependency is revoked or a receipt becomes stale;
- concurrent/crash testing contradicts the state model;
- incomplete multi-row history changes canonical replay;
- same-process adversarial execution is introduced into the bootstrap threat
  model;
- ORION proposes a change to the pinned verifier, authorization engine, PEP,
  reducer or bootstrap root;
- a domain evaluator cannot express its warrant in the obligation/support model;
- later independent routes add a new architectural primitive;
- empirical trials show unacceptable false pass, false refusal or
  `CANNOT_CHECK` rates.

### Open residuals before later slices

The bounded first slice does **not** resolve:

1. production key generation, storage, rotation, compromise recovery or public-
   key receipt verification;
2. trusted time, monotonic counters or durable freshness across host rollback;
3. external witnessing, split-view detection or Byzantine storage;
4. OS/process isolation for arbitrary generated code and hidden fixtures;
5. atomicity between the local ledger and external side effects;
6. transaction framing and recovery for a whole round if more than one
   canonical event remains necessary;
7. formal policy-language selection and complete equivalence checking;
8. domain-specific scientific evaluators, false-pass/false-refusal thresholds
   and construct-validity studies;
9. independent validation of an update to the bootstrap root;
10. general adversarial memory defense and safe deletion/retention policy; and
11. empirical calibration of expiry, recheck and reopen timing.

## 11. Scoped research and implementation decision

The following independent routes were inspected:

1. measurement/construct validity and benchmark methodology;
2. oracle, metamorphic and property-based testing;
3. assurance cases, defeaters and runtime assurance;
4. provenance, software-supply-chain security, PKI/transparency and revocation;
5. event sourcing, build dependencies, truth maintenance and provenance
   semirings;
6. remote attestation and attestation-result freshness;
7. trust management, ABAC/zero-trust authorization and complete mediation;
8. linearizability, authorization-snapshot causality and crash consistency;
9. proof-carrying code, translation validation and trusting-trust limits; and
10. agent failure, LLM-judge, memory poisoning, continual-learning and safe
    self-modification literature.

The later routes did add a load-bearing primitive missing from the first
packet: a verifier's attestation result is not the relying party's transition-
authorization decision. They also added a causality obligation: the
authorization snapshot must be at least as fresh as causally prior policy,
support and revocation changes when the transition commits. The earlier
`BOUNDED_SATURATED` label is therefore withdrawn rather than defended.

The evidence is nevertheless sufficient to freeze one **bounded first
implementation hypothesis**:

```text
host evidence resolution
  -> protected verifier / typed attestation result
  -> separate host transition authorization
  -> policy enforcement at verified write-back
  -> exact decision-bound assurance envelope
  -> atomic expected state-and-authority transition
  -> deterministic historical replay plus live reopen projection
```

This is a decision to implement and falsify a bounded hypothesis, not a claim
of literature recall, semantic saturation, scientific truth, independent
assurance or full self-driving readiness. Any hostile-test failure or reopen
trigger above reopens the hypothesis before downstream dependence.

It remains **non-saturated** for concrete distributed storage, production key
ceremony, trusted time, general memory defense, domain-specific scientific
oracles, operational thresholds, safe bootstrap-root replacement and ORION's
full recursive workflow. Those are separate fibers and cannot be silently
inherited as closed.

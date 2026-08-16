# Autonomous-kernel knowledge round 004 — protected step verification

**Outcome:** `REOPENED_BY_TRANSFER_DELTA` for protected step verification;
`NON_FLAT` for general autonomous research.

**Implementation verdict:** the first canonical/projection/transaction slice is
`READY_TO_IMPLEMENT_AS_A_BOUNDED_HYPOTHESIS`.  Its contract and hostile tests
are specific enough to implement, but it is not verified, saturated, or evidence
that ORION is self-driving.

**RAKL mechanics source (read-only):**
`bd4ce50f48bbfd7d36e9a41ded9566f77d8105ca`

**ORION committed subject:**
`5894ac7814d194b3c60d9655af87ef2d9828d56c`

The row-atomic append discussed below was inspected in the concurrent local
working-tree delta above that committed subject.  It is candidate integration
work, not behavior attributed to `5894ac7`; the committed subject still carries
the reproduced concurrent-append failure recorded in the companion packet.
This round must be repinned after that candidate slice is integrated.

The RAKL audit used pinned `git show` objects only.  It transfers mechanics and
negative history, never RAKL authority, certificates, scientific results, test
success, or empirical claims.

## Why the previous verdict is reopened

The earlier literature routes still support the protected-lifecycle model, but
the pinned RAKL transfer lane exposed unresolved primitives at boundaries that
the previous `BOUNDED_SATURATED` verdict treated too coarsely:

1. an atomic ledger-row append is not an atomic logical round transition;
2. a hash is not a stable commitment without a frozen canonicalization version
   and an object-specific digest domain;
3. retaining an episode is not admitting it to an authority-bearing projection;
4. a retrospective failure can be learnable without being eligible to certify
   promotion;
5. a flat direct-support list does not propagate freshness through transitive
   dependencies; and
6. a necessary epistemic cut is not a sufficient repair plan.

These are transfer deltas, not merely new citations.  The protected
step-verification fibre therefore remains open.

## Pinned RAKL transfer audit

### 1. Whole-transition atomicity, idempotency, and stale-head retry

Pinned sources:

- `src/rakl/engineering_atomic.py` —
  `SqliteAtomicEngineeringCoordinator._tx`,
  `commit_evidence_transition`, and `commit_semantic_transition`;
- `src/rakl/engineering_store.py` —
  `SqliteEngineeringStateStore._transaction` and `commit_transition`;
- `src/rakl/engineering_state.py` — `StateTransitionRequest.request_hash`,
  `StateTransitionReceipt`, and `TransitionStatus.RETRY_REQUIRED`.

The transferable contract is one durable transaction over the semantic batch,
project head, and transition receipt.  `BEGIN IMMEDIATE / COMMIT / ROLLBACK`
serializes the metadata transition.  An idempotency key is bound to the exact
request hash: an exact replay returns the prior receipt, while reuse for a
different request is a conflict.  A stale before-snapshot does not silently
rebase; it returns `RETRY_REQUIRED` so the caller rereads current state and
replans.

In the inspected concurrent working-tree candidate, `LedgerStore.append` is
row-atomic: it takes an exclusive lock, checks an optional expected head, writes
a temporary file, `fsync`s, replaces, and `fsync`s the directory.  That is
useful but insufficient.  `round._persist` still emits `ANSWER`, `GRADING`,
`EPISODE`, `RESIDUAL`, and `ROUND` through separate unconditional appends.  A
crash or competing writer can therefore leave or interleave a prefix of one
logical round.  ORION needs a single round-transition envelope, or an equally
strong prepare/commit protocol whose uncommitted prefixes are invisible.

Non-transfer: SQLite is a reference mechanism, not a required backend, and
RAKL's transaction receipt grants neither scientific nor ORION promotion
authority.

### 2. Versioned canonicalization and digest-domain separation

Pinned source: `src/rakl/canonical_commitment.py` — `SCHEMA`, `_PREFIX`,
`CanonicalProfile`, `canonical_json_bytes`, and `sha256_digest(domain=...)`.

The transferable obligation is to freeze the canonicalization scheme and its
profile, reject unsupported or ambiguous values, and separate object domains
before hashing.  A round-transition digest, evidence-content digest, admission
receipt digest, and support-manifest digest must not be interchangeable merely
because their normalized bytes match.  Unknown canonicalization versions must
fail replay closed.

Non-transfer: RAKL's encoder deliberately covers Python-specific values such as
`Decimal`, `Fraction`, dataclasses, sets, paths, and IEEE-754 bit patterns.  ORION
must choose and test its own cross-process/wire contract rather than copying
that encoding blindly.

### 3. Authority-mutation chokepoint audit

Pinned source: `src/rakl/authority_chokepoint.py` — `DEFAULT_ALLOWLIST` and
`audit_source_tree`.

The transferable mechanic is a fail-closed static inventory of production call
sites allowed to mutate protected authority.  ORION should audit all paths that
can mark answers verified, register evaluators or policies, admit episodes,
activate guards or lessons, revoke support, or commit canonical projections.
A new call site outside the frozen allowlist is a conformance failure.

Non-transfer: an AST allowlist is CI conformance only.  It is not a runtime
security boundary, does not detect every dynamic dispatch or monkey-patch, and
does not make same-process untrusted Python safe.

### 4. Shadow failure retention versus protected admission

Pinned source: `src/rakl/episode_admission.py` —
`PROPOSAL_SHADOW_STORED`, `CANONICAL_INVENTORY_ADMITTED`,
`retain_proposal_shadow_episode`, and
`require_protected_consumer_admission`.

ORION should retain well-formed failures immediately in a shadow/search
projection so negative history is not lost.  Protected inventory, promotion,
lesson/tool, proof, or root-gate use requires a separate content-bound admission
receipt.  File path, filename, top-level identifier, or mere ledger presence
must not confer admission.  Even canonical inventory admission establishes
registration only; it does not establish truth or promotion authority.

### 5. Frozen, non-adaptive fresh-transfer panels

Pinned source: `src/rakl/experience_benchmark.py` —
`ExperienceBenchmarkPacket`, `benchmark_protocol_subject_hash`, and
`validate_experience_benchmark`.

Development tasks may update a learning state sequentially.  Every held-out
fresh-transfer case must instead start from the same frozen
`learned_state_after_development_hash`; learning from transfer case 1 must not
alter the state used on case 2.  Task/evaluator/tool/schema artifacts, resource
ceilings, chronology, baseline resets, and development/transfer disjointness
must be frozen and content-bound before results.  Otherwise the panel measures
online adaptation across the test set, not fresh transfer from one learned
state.

Non-transfer: a valid matched panel is a measurement contract, not a global
capability claim.

### 6. Prospective binding for consequential actions

Pinned source: `src/rakl/pre_action_receipt.py` — `PreActionFibreReceipt`,
`gate_consequential_operator_execution`, and `audit_pre_action_binding`.

Before a consequential action, ORION should bind the exact pre-state/fibre,
operator, selected and rejected evidence, evidence authority, discriminator,
allowed outcome branches, task/atom/context, and freeze chronology.  A later
episode must reference that exact commitment.  Missing, malformed, post-hoc, or
mismatched binding cannot receive prospective promotion credit.

Retrospective episodes remain valuable for search priority, diagnosis, and
failure learning.  They cannot certify the policy, guard, evaluator, or lesson
whose success was defined after the outcome was seen.

### 7. Complete, normalized, ancestry-aware lineage

Pinned source: `src/rakl/evidence_lineage.py` — `EvidenceLineageNode`,
`EvidenceLineageGraph`, and `assess_evidence_lineage`.

A useful lineage graph includes derivation parents, alternate identifiers,
specializations/versions, complete-ancestry status, and freeze chronology.
Aliases are unioned before ancestry is traversed; dangling references,
derivation cycles, post-hoc graphs, and incomplete ancestry fail closed.  Remote
sources with one shared upstream dataset, paper, repository, evaluator, prompt,
or generated artifact must share a registered root even if URLs and agent
labels differ.

Repairing only empty lineages is insufficient.  The strongest topology-only
verdict is `NO_KNOWN_SHARED_ANCESTRY`; the pinned implementation explicitly says
that this is not statistical or epistemic independence and yields no numeric
effective sample size.

### 8. Transitive dependency closure and frozen manifests

Pinned sources:

- `src/rakl/proof_dag.py` — `dependency_premise_conclusion`,
  `dependency_closure`, and `all_dependencies_verified`;
- `src/rakl/proof_dag_v2.py` — `DependencyManifestReceipt`,
  `dag_dependency_statement_hashes`, and
  `verify_checkpoint_with_dependency_manifest`.

Freshness and revocation must propagate through the full transitive dependency
closure, not only direct support.  Relation orientation is typed: for example,
`REDUCES_TO` reverses the premise direction relative to `REQUIRES` and
`IMPLIES`.  A checkpoint must bind an exact dependency-statement manifest that
was extracted and frozen before promotion; missing or extra dependencies fail
closed.

Non-transfer: a verified dependency manifest checks agreement with the frozen
graph.  It does not prove the scientific statements in that graph.

### 9. Necessary cuts versus sufficient repairs

Pinned source: `src/rakl/support_solver.py` — `EpistemicCut`, `MinimalRepair`,
`_minimum_cut`, `_minimal_repair`, and `SolveReport.grants_scientific_authority`.

An epistemic cut identifies blockers that every candidate route intersects and
therefore describes necessary work.  A minimal repair identifies a set whose
establishment opens at least one route and therefore describes sufficient work
within the frozen support structure.  On a chain, one under-licensed edge can
be a cut while every under-licensed edge is required for repair.  ORION must
store both objects, their basis, costs, and whether minimality was exact or
approximated.

Non-transfer: routes, cuts, and repairs schedule research.  They grant no
scientific authority and cannot promote a claim.

## First bounded implementation slice

The following slice is ready to implement test-first as a bounded architecture
hypothesis:

1. **Canonical contract:** freeze an ORION canonicalization version/profile and
   object digest domains; reject unknown versions and ambiguous values.
2. **Projection contract:** append raw observations and failures without loss,
   but derive protected canonical views only from explicit admission receipts.
3. **Transition contract:** commit a whole round envelope against the exact
   expected head and authority/support snapshot; bind an idempotency key to the
   complete request hash.
4. **Replay contract:** replay only committed envelopes under the exact reducer,
   workflow, and canonicalization versions.
5. **Chokepoint contract:** statically inventory and allowlist every production
   call site that can change a protected projection.

Implementation is not completion.  At minimum, hostile tests must show:

- two writers on one expected head produce one commit and one stale result;
- exact retry returns the exact receipt, while same-key/different-request use is
  rejected;
- crashes before write, `fsync`, replace, and directory `fsync` never expose a
  half-round as committed;
- stale retry rereads and replans under current authority rather than rebasing a
  prior decision;
- key order, Unicode, numeric boundaries, type distinctions, version mismatch,
  and cross-domain equal payloads cannot collide semantically;
- a shadow episode remains searchable and learnable but cannot satisfy a
  protected consumer;
- a new authority-mutation path outside the allowlist fails CI; and
- replay reconstructs the identical protected projection or fails closed.

This readiness verdict is limited to specifying and starting that slice.  It
does not cover production key custody, distributed consensus, trusted time,
general memory poisoning, domain scientific oracles, or global self-driving
operation.

## Explicit remaining questions

1. What is the exact logical boundary of a round transition, including external
   side effects that cannot join the local transaction?
2. Which stale outcomes are durably recorded, which are retried, and which
   require human or external arbitration?
3. Which canonical value types and Unicode/numeric semantics must interoperate
   across Python versions or other languages?
4. What complete set of call sites can mutate evaluator, policy, admission,
   support, lesson, guard, and canonical-state authority?
5. Which failure fields are immutable observations, which are diagnoses, and
   what receipt admits either into a protected projection?
6. Which actions are consequential enough to require prospective binding, and
   how are irreversible external actions handled?
7. How is lineage acquired, normalized, completed, frozen before outcomes, and
   updated when a remote shared root is discovered later?
8. What typed relation vocabulary gives the correct premise orientation for
   every support edge, and how does freshness propagate through it?
9. How are exact and approximate cuts/repairs distinguished in scheduling and
   user-visible reports?
10. What positive evidence establishes that two audit routes are lineage
    separated, rather than merely differently named?

## Stopping gate

Round 004 remains open until all of the following hold:

- round-level transition atomicity and exact retry semantics pass hostile crash,
  concurrency, stale-head, and idempotency tests;
- every identity-bearing hash uses a frozen canonicalization version/profile
  and an explicit object domain;
- alternate authority-mutation paths have been enumerated and audited;
- shadow failure retention is mechanically separated from protected admission;
- held-out transfer panels are frozen, non-adaptive, and start every case from
  one frozen learned state;
- consequential actions have prospective binding wherever the policy requires
  it, while retrospective failures remain learnable but non-certifying;
- lineage is complete, normalized, frozen before outcomes, alias-aware,
  specialization-aware, and remote-shared-ancestry-aware;
- support freshness and revocation propagate through typed transitive
  dependencies frozen in exact manifests;
- necessary cuts and sufficient repairs remain distinct throughout storage,
  scheduling, and reporting; and
- two audit routes with positive, frozen, complete, disjoint lineage evidence
  independently inspect the same frozen basis and find no new architectural
  primitive.

Missing lineage, different labels, repeated agents, hashes alone, or successful
RAKL tests cannot satisfy this gate.  The eventual verdict, if the gate passes,
must remain bounded to the declared basis, source and workflow epochs, hostile
test universe, and architecture question; it cannot become a global literature
recall or self-driving certificate.

## Frozen companion packet

The broader source synthesis, atomic question grammar, literature routes,
current-ORION hostile reproductions, implementation hypothesis, and reopen
rules remain in `knowledge/STEP_VERIFICATION_LITERATURE.md`.  This round file
supersedes only that packet's transfer-lane saturation conclusion: the newly
audited RAKL mechanics reopen the protected step-verification fibre.

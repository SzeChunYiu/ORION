# Protected Step Verification Implementation Plan

> **For Codex:** REQUIRED SUB-SKILL: Use `executing-plans` task by task, with
> `test-driven-development`, `systematic-debugging`, `receiving-code-review`, and
> `verification-before-completion`.

**Goal:** Build the minimum protected ORION transition lifecycle in which an
untrusted answer can change research state only through immutable host evidence,
a versioned pure reducer, protected appraisal, relying-party authorization, and
one atomic compare-and-swap transaction that replays without rerunning an
evaluator.

**Architecture:** Candidate answers and verifier outputs are proposals, never
authority. The host captures one immutable evidence snapshot, a pure reducer
constructs an exact pre-state/proposed-post-state transition, a protected verifier
issues an appraisal, and a separate relying-party module authorizes or refuses the
transition against trusted registrations, live support, and exact research,
authority, support, and ledger revisions. The complete receipt/decision/transition
is stored as one atomic transaction envelope; historical replay consumes only
committed envelopes, while current freshness changes append revalidation or
reopen transitions.

**Tech Stack:** Python 3.11+, frozen dataclasses/enums, canonical JSON/SHA-256,
`cryptography` Ed25519, `fcntl`, `os.replace`/`fsync`, pytest, Ruff.

**Repository root:** `/Users/billy/Desktop/projects/ORION`

**Starting subject:** `5894ac7814d194b3c60d9655af87ef2d9828d56c`

**Coordination refresh (2026-08-16):** the implementation lane is
`codex/step-verification-lifecycle` at `670afb6bacd1899ee8e4d62ceb5672a10f8f319d`.
A fresh fetch observed `origin/main` at
`8a4612f4ecf96317b86d832fdb847209078f43f6`, with merge base
`ebb93fddb2931a39fe57c222edce628813a0fd97` and divergence `6 / 270`.
These Task-3 results are therefore lane-local until hostile review and explicit
reconciliation; they must not be described as integrated current-main behavior.

**Pinned research:**
`research/development/autonomous-kernel/knowledge/STEP_VERIFICATION_LITERATURE.md`

---

## Stop: the current protected-assurance test contract is unsafe

`tests/unit/kernel/test_protected_assurance.py` currently asks production code to
accept all of the following from an ordinary caller:

- a signing key;
- host identity and trust-root labels;
- evaluator registrations and epochs;
- policy identities;
- an authoritative Python evaluator callable;
- a `ProtectedAnswerAssuranceService` passed into `grade_and_apply`.

That interface launders caller-controlled data into authority. **Do not implement
any of the wished-for symbols or parameter threading in the current file.** Task 1
replaces that test contract before any assurance production code is written.

In particular, do not add an `assurance_service`, `registry`, `signing_key`,
`trust_store`, or evaluator callable parameter to `grade_answer`,
`grade_and_apply`, `run_round`, `replay_cells`, or `SelfDrivingDriver`.

## Non-negotiable invariants

1. **Proposal separation.** `AnswerRecord`, raw `DiscriminatingCheck`, execution
   success, and verifier appraisal never directly grant `VERIFIED` authority.
2. **Immutable evidence occasion.** Resolution happens once per attempt. The
   captured bytes, identities, content hashes, host-assigned roles, obligations,
   root configuration, and logical capture revision form one immutable snapshot.
3. **Exact state.** Subject identity covers the complete mechanics-reducer
   projection, including the exact seed, record graph, active tips and
   reopen state, plus every external protected read-set revision. It never
   substitutes open-question count or claims this slice is global ORION state.
4. **Pure versioned reduction.** The same supported workflow/reducer version,
   seed projection, and ordered operations produce exactly the same post-state.
5. **Appraisal is not authorization.** A signed verifier `PASS` is input to the
   relying party; it is not itself transition authority.
6. **Static authority choke-point.** Exactly one protected module may construct
   an authorized state transition. Static tests forbid all other promotion paths.
7. **Non-compensatory relying-party decision.** Authorization requires exact
   subject, valid signature, trusted/live registration, current evaluator,
   policy, key, trust root, complete live support, and all expected revisions.
8. **Four-way preservation.** `PASS`, `FAIL`, `BLOCKED`, and `CANNOT_CHECK`
   remain distinct. Non-`PASS` outcomes are recorded and never rounded away.
9. **Multi-revision CAS.** Commit compares ledger head, research-state hash,
   authority revision, and support revision under the same writer lock.
10. **Atomic envelope.** Evidence snapshot, appraisal, authorization receipt,
    transition, execution link, failures, and round observation commit together
    or not at all.
11. **Historical replay.** Replay uses only committed transition envelopes and
    their historical registrations. It never rereads evidence or reruns the
    current evaluator.
12. **Append-only correction.** Revocation, expiry, dependency change, or current
    reappraisal appends `REVALIDATE`/`REOPEN`; it never edits historical success.
13. **Global supersession.** Record identities and active coordinate tips are
    global across rounds. Linear supersession replaces the prior contribution;
    branches, missing parents, cycles, and changing duplicate IDs fail closed.
14. **Typed exceptional cases.** Handoff payloads round-trip exactly. Unknown
    mechanics and V0 waivers become recorded no-op failures, never silent drops.
15. **No false completeness.** Local hash chaining establishes prefix integrity,
    not witnessed tail completeness, scientific truth, or recall.

## Concurrent-state amendment at `origin/main` `4d384ab`

The merged `SOURCE`/`READ` knowledge ledger is a new behavior-affecting state
lane. A caller-authored alias can currently merge two works and make a required
read return `ALREADY_READ`; malformed read rows are skipped. Therefore:

- raw source/alias/read rows remain shadow observations until content-bound
  admission establishes alias equivalence and read identity;
- Task 7 inventories behavior-changing scheduling, guard, lesson, claim,
  solution, evaluator, trust-store, support, and admission effects across the
  whole repository, including `engine` and `experience`, not only
  `AnswerAuthority` assignments;
- Task 8 either commits an explicit knowledge/read-set revision with the
  transition or establishes that the common ledger head is the conservative
  serialization token and binds the exact semantic read set separately;
- Tasks 10 and 13 treat malformed or legacy `SOURCE`/`READ` rows as typed replay
  failures or quarantined shadow data, never silent protected omission.

`ProgramProjection` is deliberately narrowed to the mechanics reducer. Full
self-driving ORION later composes mechanics, knowledge, experience, engine,
authority, support, and external-effect projections; this bounded slice must not
claim global completeness.

## Intended module interfaces

These are interfaces to test toward, not permission to implement before their
RED step.

```python
@dataclass(frozen=True)
class LedgerExpectation:
    ledger_head: str | None
    research_state_hash: str
    authority_revision: str
    support_revision: str

@dataclass(frozen=True)
class ProgramProjection:
    schema_version: str
    workflow_version: str
    reducer_version: str
    seed_cells: tuple[MechanicCell, ...]
    records: tuple[AnswerRecord, ...]
    active_record_ids: tuple[str, ...]
    reopened_coordinates: tuple[tuple[str, str, str], ...]

    # Derived, never independently caller-authored:
    # seed_hash, record_bindings, active_records, active_record_tips

@dataclass(frozen=True)
class HostEvidenceSnapshot:
    # Derived, never independently caller-authored:
    # snapshot_id
    root_configuration_hash: str
    manifest_hash: str
    captured_at_authority_revision: str
    captured_at_support_revision: str
    records: tuple[HostEvidenceRecord, ...]

@dataclass(frozen=True)
class TransitionPlan:
    transition_id: str
    transition_kind: TransitionKind
    expectation: LedgerExpectation
    pre_state_hash: str
    proposed_post_state_hash: str
    workflow_version: str
    reducer_version: str
    operations: tuple[TransitionOperation, ...]
    evidence_snapshot_hash: str
    execution_receipt_hash: str | None

@dataclass(frozen=True)
class VerifierAppraisal:
    appraisal_id: str
    subject_hash: str
    registration_commitment: str
    verdict: AppraisalVerdict
    reason_codes: tuple[str, ...]
    signature: str

@dataclass(frozen=True)
class TransitionAuthorization:
    authorization_id: str
    transition_id: str
    subject_hash: str
    verdict: AuthorizationVerdict
    reason_codes: tuple[str, ...]
    expectation: LedgerExpectation
    signature: str

@dataclass(frozen=True)
class TransitionTransaction:
    transaction_id: str
    schema_version: str
    evidence_snapshot: HostEvidenceSnapshot
    appraisal: VerifierAppraisal
    authorization: TransitionAuthorization
    plan: TransitionPlan
    episodes: tuple[TaskEpisode, ...]
    residuals: tuple[TransitionResidual, ...]
```

The precise names may change after RED feedback, but the separation of roles and
bound fields may not.

## Concurrent-work constraints

- Do not create a worktree.
- Inspect `git status --short --branch` before every task.
- Do not modify `/Users/billy/Desktop/projects/ORION-claude`.
- `src/orion/kernel/store.py` and
  `tests/unit/kernel/test_ledger_atomicity.py` already contain concurrent atomic
  single-entry work. Extend it; do not overwrite or weaken it.
- `src/orion/kernel/support.py` and `tests/unit/kernel/test_support.py` already
  contain a pure DNF support evaluator. Integrate it only after inspecting its
  current diff.
- PR #21 is conflict-heavy and predates the kernel. Never merge it wholesale.
  Its typed metric payload is a future schema input, not authority evidence.
- Never force-push.
- Every shell command in this plan is prefixed with `rtk`.

---

### Task 1: Delete the unsafe caller-injected contract

**Files:**

- Replace: `tests/unit/kernel/test_protected_assurance.py`
- Modify: `tests/unit/kernel/test_self_driving_kernel.py`
- Reference: `src/orion/kernel/apply.py`
- Reference: `src/orion/kernel/gate.py`
- Reference: `src/orion/kernel/round.py`
- Reference: `src/orion/kernel/driver.py`

**Step 1: Replace the unsafe test file with static seam tests**

Delete every construction of `HostAssuranceIdentity`,
`AnswerEvaluatorRegistration`, and `ProtectedAnswerAssuranceService`. Add tests
that inspect the candidate-facing call signatures:

```python
@pytest.mark.parametrize(
    (target, forbidden),
    (
        (grade_answer, {"assurance_service", "registry", "signing_key", "evaluate"}),
        (grade_and_apply, {"assurance_service", "registry", "signing_key", "evaluate"}),
        (run_round, {"assurance_service", "registry", "signing_key", "evaluate"}),
        (replay_cells, {"assurance_service", "registry", "signing_key", "evaluate"}),
    ),
)
def test_candidate_facing_interfaces_accept_no_authority_material(target, forbidden):
    assert forbidden.isdisjoint(inspect.signature(target).parameters)
```

Add a source scan asserting those candidate-facing modules never import the
future protected host runtime.

**Step 2: Preserve the raw-check hostile tests**

Keep these requirements in `test_self_driving_kernel.py`:

```python
assert grading.check_outcome is CheckOutcome.PASSED
assert grading.authority is AnswerAuthority.EVIDENCE_BOUND
assert MechanicDimension.STORAGE in target.provisional_dimensions
```

Keep the authentic weather evidence plus irrelevant mathematical claim attack.
Raw checks remain diagnostic only.

**Step 3: Run the corrected contract**

Run:

```bash
rtk pytest tests/unit/kernel/test_protected_assurance.py \
  tests/unit/kernel/test_self_driving_kernel.py \
  -q
```

Expected: no collection error for missing `orion.kernel.assurance`; the raw-check
promotion tests remain RED against current production behavior.

**Step 4: Make only the diagnostic-authority withdrawal**

Modify `src/orion/kernel/gate.py` so raw checks still populate
`check_id/check_outcome/reasons` but never change `AnswerAuthority` to
`VERIFIED`. Do not add protected assurance yet.

**Step 5: Run GREEN**

```bash
rtk pytest tests/unit/kernel/test_protected_assurance.py \
  tests/unit/kernel/test_self_driving_kernel.py \
  -q
rtk ruff check src/orion/kernel/gate.py \
  tests/unit/kernel/test_protected_assurance.py \
  tests/unit/kernel/test_self_driving_kernel.py
```

Expected: raw-check and seam tests pass. Existing durable-resume tests that
assumed raw verification may need expectations narrowed to provisional content;
do not invent a replacement authority path.

**Step 6: Commit**

```bash
rtk git add src/orion/kernel/gate.py \
  tests/unit/kernel/test_protected_assurance.py \
  tests/unit/kernel/test_self_driving_kernel.py
rtk git commit -m "fix(kernel): remove caller-owned verification authority"
```

---

### Task 2: Freeze canonical mechanics projection and transition identity

**Files:**

- Create: `src/orion/kernel/transition.py`
- Create: `tests/unit/kernel/test_transition_identity.py`
- Modify: `src/orion/kernel/__init__.py`
- Reference: `src/orion/mechanics/model.py`
- Reference: `src/orion/mechanics/answers.py`

**Step 1: Write RED canonical-codec tests**

Test one `MechanicCell` containing string fields, `HandoffField`, `MetricSpec`,
provisional dimensions, and waivers. Require deterministic explicit dictionaries,
not `repr`, pickle, or callable identity.

```python
def test_projection_hash_binds_complete_typed_state():
    first = projection_with_handoff(required=True)
    changed = projection_with_handoff(required=False)
    assert projection_hash(first) != projection_hash(changed)
```

Freeze an exact golden byte/digest vector and strict round-trip decoder. Require
explicit distinction of bool/int, list/tuple, positive/negative zero, finite
IEEE-754 binary64 bits, arbitrary integers without ambient decimal conversion,
NFC assigned text, unknown-tag/profile rejection, and object digest domains.
Freeze explicit byte/depth/node resource bounds and convert parser recursion or
ambient integer-limit failures into `CanonicalizationError`. Pin separate
golden digests for a complete `AnswerRecord`, seed, and projection so an
object-encoder or domain drift cannot silently rewrite historical identities.
The byte cap is eight mebibytes: finite and pre-parse enforced, but large enough
for the measured 1,196,301-byte live mechanics seed. A real-program regression
must accompany the synthetic boundary attacks.

The projection must retain the exact seed plus the complete structurally admissible
`AnswerRecord` supersession graph. Active tips and record bindings are derived
and checked against record bodies. Missing parents, cross-coordinate edges,
branches, cycles, wrong tips, duplicate IDs, and unknown version triples fail
closed. `provisional_dimensions` is encoded as a set-like sorted field.

**Step 2: Run RED**

```bash
rtk pytest tests/unit/kernel/test_transition_identity.py \
  -q -x
```

Expected: first FAIL because `orion.kernel.transition` does not exist; later
hostile deltas fail on missing canonical profile/decoder or invalid projection
normal form before their corresponding production changes.

**Step 3: Implement only versioned frozen data and codecs**

Define:

- `WORKFLOW_VERSION`;
- `REDUCER_VERSION`;
- `CANONICALIZATION_VERSION`, the frozen UCD 3.2 assigned-NFC Unicode policy,
  and its database version in every envelope;
- `TransitionKind` with `ANSWER`, `REVALIDATE`, `REOPEN`, and
  `AUTHORITY_SUPPORT_UPDATE`;
- `ProgramProjection` with exact seed and complete structurally admissible
  record graph;
- `LedgerExpectation`;
- explicit canonical encoders for every `MechanicCell`, `HandoffField`,
  `MetricSpec`, `DimensionWaiver`, and complete `AnswerRecord` field;
- strict canonical decoding plus frozen golden bytes/digest;
- `projection_hash`.

Do not add evaluator, signing, store, or mutation behavior.

**Step 4: Run GREEN**

```bash
rtk pytest tests/unit/kernel/test_transition_identity.py \
  -q
rtk ruff check src/orion/kernel/transition.py \
  tests/unit/kernel/test_transition_identity.py
```

**Step 5: Commit**

```bash
rtk git add src/orion/kernel/transition.py \
  src/orion/kernel/__init__.py \
  tests/unit/kernel/test_transition_identity.py
rtk git commit -m "feat(kernel): define versioned mechanics projection"
```

---

### Task 3: Capture one immutable host evidence snapshot

**Research delta at `HEAD` `670afb6`:** the legacy resolver is diagnostic
only. It performs pathname validation, a digest read, and a later text read, so
one returned row can bind digest A to content B. Replacement decoding also
collapses distinct invalid UTF-8 byte strings, eight-hex digest prefixes are
too weak for a protected content identity, mutable Git names are resolved more
than once, and unresolved rows are dropped by the legacy evidence index.

The protected path therefore uses a separate capture protocol:

- host policy, not `AnswerRecord`, supplies exact role and obligation bindings;
- protected V1 does not parse delimiter-packed candidate locators. A host-owned
  typed source registration separates opaque source ID, backend, root ID, path,
  expected file SHA-256, and Git ref/OID, so `@`, path bytes, algorithms and
  source coordinates cannot alias through string splitting;
- a registered local root is opened once, every path component is traversed
  descriptor-relative with no-follow semantics, the final object must be a
  regular file, and bytes come from that one open descriptor;
- descriptor metadata is compared before/after reading; a change produces a
  retained typed `CHANGED_DURING_CAPTURE`, never `RESOLVED`;
- each canonical Git ref is resolved once per root/ref/snapshot to a typed full
  storage object ID and every requested path reuses that frozen resolution;
  shorthand revisions are rejected. Annotated-tag object identity and peeled
  commit identity remain separate;
- Git is invoked with replacement objects and promisor lazy fetch disabled and
  ambient object-directory/alternate settings scrubbed. The frozen commit's raw
  commit/tree chain is traversed component by component, only regular-file modes
  `100644`/`100755` are admitted, and every returned commit/tree/blob is checked
  against its independently recomputed typed Git object ID;
- a SHA-1 Git OID is only a typed frozen source coordinate, not ORION's protected
  content identity. Raw blob bytes receive an independent full SHA-256 content
  digest and byte length; provenance stronger than a verified local object chain
  still requires a SHA-256 repository or separately appraised signed provenance;
- protected file references require a full lowercase SHA-256 digest. Legacy
  prefixes remain diagnostic locators only;
- raw `bytes`, including empty and invalid UTF-8 content, are retained. Text is
  an optional strict derived view and never evidence identity;
- protected Git subprocesses are launched through one isolated descriptor
  helper whose launcher path, launcher bytes, helper source, Git executable and
  local file occasion are committed in the root configuration. This is not a
  claim that the dynamic loader/runtime closure or the exec-time pathname race
  is solved;
- stdout, stderr, command starts, elapsed time, local bytes, path components,
  tree entries, distinct Git objects and Git-object bytes have shared snapshot
  budgets. Exhaustion is retained as a typed censored/unexamined outcome and in
  the snapshot work receipt; it is not evidence that the source or mechanic
  failed. The elapsed budget is checked at operation boundaries and can report
  an overrun after a blocking filesystem call returns; it is not OS-level
  preemption;
- protected Git V1 admits only a real `.git` directory whose descriptor
  identity is fixed. Gitfiles, symlinks, special entries, bare roots,
  `commondir`, repository object alternates and `include`/`includeIf` config
  expansion are explicitly refused until every external administrative root is
  independently opened and committed;
- verified Git objects are cached only after independent type/size/OID
  validation under the key `(git dev, git inode, object format, type, OID)`;
  reuse neither starts another object read nor spends the object-byte budget
  twice;
- content hash, record hash, manifest hash, root-configuration hash, and
  snapshot hash have separate domains. Record/snapshot hashes are derived and
  their own preimages contain no backward/self edge;
- every requested or host-required reference gets one terminal record.
  `ROLE_UNMAPPED`, missing, mismatched, unsafe, unstable, and unreadable rows
  remain in the snapshot and force the later `CANNOT_CHECK` path;
- a live multi-file snapshot is a deterministic sequence of exact per-file
  occasions, not a claim of one atomic filesystem instant. Only a shared Git
  commit/tree or later CAS manifest can support that stronger claim;
- per-record and per-snapshot byte caps remain explicit; Task 3 freezes bytes
  in memory, while later storage work may move large content to an atomic CAS.

The mechanical layers are kept non-substitutable:
`SourceCoordinate -> FrozenLocator -> ContentDescriptor -> CaptureRecord ->
AttestationResult -> AuthorizationDecision`. Equality or success at one layer
never promotes itself to the next.

**Files:**

- Modify: `src/orion/kernel/evidence.py`
- Create: `tests/unit/kernel/test_evidence_snapshot.py`
- Modify: `src/orion/kernel/__init__.py`

**Step 1: Write the mutable-file RED test**

Use a resolver seam that changes the underlying file after the first read. Require
one snapshot to retain one content digest and exact byte payload throughout the
attempt. Add a parent/final-symlink swap discriminator: capture either uses the
one safely opened object or returns a typed unresolved row, never a path-checked
object followed by a different pathname read.

```python
def test_one_attempt_uses_one_evidence_occasion(tmp_path):
    snapshot = capture_host_evidence_snapshot(...)
    rewrite_source(tmp_path)
    assert snapshot.records[0].content_hash == original_hash
    assert snapshot_hash(snapshot) == original_snapshot_hash
```

**Step 2: Write role/obligation ownership RED tests**

Require roles and obligation IDs to come from a host registration/policy manifest,
not `AnswerRecord`. Unknown role mapping produces a typed unresolved snapshot and
later `CANNOT_CHECK`.

Also require full digests, exact invalid-UTF-8/empty bytes, preservation of
missing rows, duplicate/conflicting manifest rejection, one-time Git ref
freezing, root/manifest/authority/support revision binding, acyclic derived
identity, and absence of any appraisal/authorization/apply seam.

**Step 3: Run RED**

```bash
rtk pytest tests/unit/kernel/test_evidence_snapshot.py \
  -q -x
```

**Step 4: Implement frozen snapshot data**

Add:

- `HostEvidenceSource` for typed host-owned source coordinates;
- `EvidenceRoleBinding`;
- `HostEvidenceRecord` containing exact resolved content and both record/content
  hashes;
- `HostEvidenceSnapshot`;
- `capture_host_evidence_snapshot` used only by the protected host composition;
- `snapshot_hash`.

The snapshot binds authority/support revisions and root-configuration hash.
Existing `resolve_evidence_ref` remains a resolver adapter, not authority.

**Step 5: Run GREEN and commit**

```bash
rtk pytest tests/unit/kernel/test_evidence_snapshot.py \
  -q
rtk ruff check src/orion/kernel/evidence.py \
  tests/unit/kernel/test_evidence_snapshot.py
rtk git add src/orion/kernel/evidence.py \
  src/orion/kernel/__init__.py \
  tests/unit/kernel/test_evidence_snapshot.py
rtk git commit -m "feat(kernel): freeze host evidence occasions"
```

**Implementation checkpoint before commit (2026-08-16):** fresh verification
reports 89 focused evidence tests, 185 kernel tests and 380 full-suite tests
passing; Ruff reports no issues and `git diff --check` is clean. A read-only
frozen-tree hostile review rejected two P1 gaps (declared annotated-tag edge
type was ignored; elapsed deadlines missed local/error/empty paths), both were
reproduced RED, repaired, reverified, and the re-review returned `ACCEPT`. The hostile
discriminators include a real final-component stat/open symlink substitution;
`.git` gitfile/symlink/FIFO refusal; descriptor-bound Git root swap; strict
ASCII control decoding; ordered commit/tag/tree validation; per-command and
global output caps; operation-boundary elapsed-deadline receipt; shared work budgets; verified
object-cache reuse; helper source/launcher artifact binding; and explicit
refusal of alternates, `commondir`, config includes and bare repositories. This
is the pre-commit Task-3 verification checkpoint, not an integration verdict
against the 270 newer commits on `origin/main`.

---

### Task 4: Build the pure reducer and global supersession projection

**Files:**

- Modify: `src/orion/kernel/transition.py`
- Create: `tests/unit/kernel/test_transition_reducer.py`
- Reference: `src/orion/mechanics/answers.py`

**Step 1: Write RED single-operation tests**

Require a pure function:

```python
plan = plan_answer_transition(
    projection,
    record,
    evidence_snapshot_hash=snapshot_hash,
    expectation=expectation,
)
assert plan.pre_state_hash == projection_hash(projection)
assert reduce_transition(projection, plan).hash == plan.proposed_post_state_hash
```

The plan must serialize the complete answer, including `handoff_payload`,
`waiver_reason`, and `supersedes`.

**Step 2: Write RED exceptional-case tests**

- Unknown mechanic -> recorded `UNKNOWN_MECHANIC`, unchanged post-state.
- V0 waiver -> recorded `UNAUTHORIZED_WAIVER`, unchanged post-state.
- Handoff -> exact typed field survives reduction.
- Duplicate same ID/same content -> explicit idempotent no-op.
- Duplicate same ID/different content -> conflict.

**Step 3: Write RED cross-round supersession tests**

Commit base record `r1`, then plan `r2 supersedes r1` in a later projection.
Require `r2` to become the sole active tip and old contributed content to be
removed. Require missing parent, branch, cycle, and non-active parent to fail
closed.

**Step 4: Write RED sequential-batch tests**

For two operations in one transaction, require operation `i+1` to bind the
post-state of operation `i`. The envelope post-state must equal the final signed
operation post-state. A conflicting operation must not appear in applied IDs or
growth counts.

**Step 5: Run RED**

```bash
rtk pytest tests/unit/kernel/test_transition_reducer.py \
  -q -x
```

**Step 6: Implement the minimum pure planner/reducer**

No filesystem, evidence resolution, evaluator call, signature check, wall clock,
or global mutable registry is permitted in this module.

**Step 7: Run GREEN and commit**

```bash
rtk pytest tests/unit/kernel/test_transition_identity.py \
  tests/unit/kernel/test_transition_reducer.py \
  -q
rtk ruff check src/orion/kernel/transition.py \
  tests/unit/kernel/test_transition_identity.py \
  tests/unit/kernel/test_transition_reducer.py
rtk git add src/orion/kernel/transition.py \
  tests/unit/kernel/test_transition_identity.py \
  tests/unit/kernel/test_transition_reducer.py
rtk git commit -m "feat(kernel): add pure versioned transition reducer"
```

---

### Task 5: Define verifier appraisal without transition authority

**Files:**

- Create: `src/orion/kernel/assurance.py`
- Create: `tests/unit/kernel/test_verifier_appraisal.py`
- Modify: `src/orion/kernel/__init__.py`
- Reference: `src/orion/mechanics/receipt.py`

**Step 1: Write RED verdict-algebra tests**

Define `PASS`, `FAIL`, `BLOCKED`, and `CANNOT_CHECK`. Require typed reason codes.
No Boolean `passed` property may collapse the algebra.

**Step 2: Write RED subject-completeness tests**

An appraisal subject must change when any of these changes:

- record content or supersession parent;
- mechanic, dimension, claim schema, or operation ordinal;
- exact pre/post projection;
- evidence content, role, or obligation;
- registration commitment;
- policy/evaluator/key/trust epoch;
- ledger head, research-state hash, authority revision, or support revision;
- workflow/reducer version;
- execution receipt ID/hash.

**Step 3: Write RED separation tests**

```python
def test_pass_appraisal_is_not_an_authorized_transition():
    appraisal = signed_pass_appraisal()
    assert not isinstance(appraisal, TransitionAuthorization)
    with pytest.raises(TypeError):
        apply_authorized_transition(projection, appraisal)
```

**Step 4: Run RED**

```bash
rtk pytest tests/unit/kernel/test_verifier_appraisal.py \
  -q -x
```

**Step 5: Implement data, canonical subject, and signature verification**

Implement `AssuranceSubject`, `AppraisalVerdict`, `VerifierAppraisal`, canonical
payload, and public-key verification. Do not implement an evaluator callable in a
registration dataclass. A registration commits an evaluator artifact identity;
a protected runner maps that identity to host-installed code outside candidate
interfaces.

**Step 6: Run GREEN and commit**

```bash
rtk pytest tests/unit/kernel/test_verifier_appraisal.py \
  -q
rtk ruff check src/orion/kernel/assurance.py \
  tests/unit/kernel/test_verifier_appraisal.py
rtk git add src/orion/kernel/assurance.py \
  src/orion/kernel/__init__.py \
  tests/unit/kernel/test_verifier_appraisal.py
rtk git commit -m "feat(kernel): add non-authoritative verifier appraisals"
```

---

### Task 6: Add revisioned authority and support projections

**Files:**

- Modify: `src/orion/kernel/support.py`
- Create: `src/orion/kernel/authority_state.py`
- Modify: `src/orion/kernel/transition.py`
- Modify: `tests/unit/kernel/test_support.py`
- Create: `tests/unit/kernel/test_authority_state.py`

**Step 1: Preserve the existing DNF support tests**

Keep conjunctive support sets, alternative warrants, scoped revocation, and
`PASS/FAIL/CANNOT_CHECK` behavior.

**Step 2: Write RED revision tests**

Status time and event order must come from ledger-controlled logical revision,
not caller wall-clock labels. Equal-revision events are rejected. Every authority
or support change produces a new revision hash.

**Step 3: Write RED historical-view tests**

A transition authorized at revision `A1/S1` must replay under that historical
view. A later `A2/S2` revocation does not rewrite it; it creates current work to
revalidate/reopen.

**Step 4: Run RED**

```bash
rtk pytest tests/unit/kernel/test_support.py \
  tests/unit/kernel/test_authority_state.py \
  -q -x
```

**Step 5: Implement frozen projections and events**

Add trusted registration, policy, key/trust-root, and dependency status events.
The projection exposes deterministic `authority_revision` and
`support_revision`. No event accepts an authority-changing callable.

**Step 6: Run GREEN and commit**

```bash
rtk pytest tests/unit/kernel/test_support.py \
  tests/unit/kernel/test_authority_state.py \
  -q
rtk ruff check src/orion/kernel/support.py \
  src/orion/kernel/authority_state.py \
  tests/unit/kernel/test_support.py \
  tests/unit/kernel/test_authority_state.py
rtk git add src/orion/kernel/support.py \
  src/orion/kernel/authority_state.py \
  src/orion/kernel/transition.py \
  tests/unit/kernel/test_support.py \
  tests/unit/kernel/test_authority_state.py
rtk git commit -m "feat(kernel): revision authority and support state"
```

---

### Task 7: Implement the relying-party authorization choke-point

**Files:**

- Create: `src/orion/kernel/authorization.py`
- Create: `src/orion/kernel/host.py`
- Create: `tests/unit/kernel/test_transition_authorization.py`
- Create: `tests/unit/kernel/test_authority_choke_point.py`
- Modify: `src/orion/kernel/__init__.py`

**Step 1: Write RED non-compensatory authorization tests**

A `PASS` appraisal authorizes only if all of the following are current and exact:

- appraisal signature and subject;
- trusted live registration commitment;
- live evaluator artifact/epoch;
- live policy/hash/epoch;
- live key/trust root;
- at least one complete live support set;
- frozen chronology;
- ledger head;
- research-state hash;
- authority revision;
- support revision.

Parameterize one test per failed obligation. Unknown status yields
`CANNOT_CHECK`; resource/governance prevention yields `BLOCKED`; demonstrated
violation yields `FAIL`.

**Step 2: Write RED caller-injection attacks**

Try to supply a fake key, trust store, registry, policy, evaluator callable,
chronology label, and support revision through every candidate-facing interface.
Require signature rejection or a `TypeError` because no such parameter exists.

**Step 3: Write the static choke-point RED test**

Parse all Python files under `src/orion`. Require:

- only `src/orion/kernel/authorization.py` constructs
  `TransitionAuthorization`;
- only the authorized reducer consumes an authorization to clear provisional
  state;
- no comparison of `AnswerRecord.lane` grants authority;
- `gate.py`, `apply.py`, `round.py`, `driver.py`, and providers contain no direct
  `AnswerAuthority.VERIFIED` assignment.

**Step 4: Run RED**

```bash
rtk pytest tests/unit/kernel/test_transition_authorization.py \
  tests/unit/kernel/test_authority_choke_point.py \
  -q -x
```

**Step 5: Implement the relying-party module**

`authorization.py` verifies the exact appraisal and current historical
projections and returns a signed `TransitionAuthorization`. It accepts frozen
data only; it does not accept keys, registries, trust stores, or callables as
ordinary parameters.

`host.py` is the protected composition root. It loads a signed host manifest and
host-installed evaluator adapter by committed artifact identity. Its public
candidate interface accepts proposals only. Provide a test-only fixture factory
under `tests/`, not a production constructor that accepts raw key bytes or a
callable.

**Step 6: Run GREEN and commit**

```bash
rtk pytest tests/unit/kernel/test_transition_authorization.py \
  tests/unit/kernel/test_authority_choke_point.py \
  -q
rtk ruff check src/orion/kernel/authorization.py \
  src/orion/kernel/host.py \
  tests/unit/kernel/test_transition_authorization.py \
  tests/unit/kernel/test_authority_choke_point.py
rtk git add src/orion/kernel/authorization.py \
  src/orion/kernel/host.py \
  src/orion/kernel/__init__.py \
  tests/unit/kernel/test_transition_authorization.py \
  tests/unit/kernel/test_authority_choke_point.py
rtk git commit -m "feat(kernel): add protected transition authorization"
```

---

### Task 8: Extend the ledger to an atomic transaction envelope

**Files:**

- Modify: `src/orion/kernel/store.py`
- Modify: `tests/unit/kernel/test_ledger_atomicity.py`
- Create: `tests/unit/kernel/test_transaction_store.py`
- Modify: `src/orion/kernel/__init__.py`

**Step 1: Retain existing single-append tests**

Run before editing:

```bash
rtk pytest tests/unit/kernel/test_ledger_atomicity.py \
  -q -x
```

Expected baseline: seven tests pass in the current shared worktree. If not, stop
and reconcile the current diff before continuing.

**Step 2: Write RED envelope-schema tests**

Add `EntryKind.TRANSITION`. One canonical ledger entry contains the complete
`TransitionTransaction`; no authoritative receipt or state-changing answer is
stored outside it.

Require every nested hash/ID to match and reject unknown envelope schema,
workflow version, or reducer version.

**Step 3: Write RED multi-revision CAS tests**

Call:

```python
store.append_transaction(transaction, expected=LedgerExpectation(...))
```

Under one lock, compare head, research state, authority revision, and support
revision. Parameterize each stale coordinate. Exactly one of two writers using
the same expectation may commit.

**Step 4: Write RED idempotency tests**

Retrying the same transaction ID with identical canonical content returns the
original committed entry. Reusing the ID with changed content raises a typed
conflict.

**Step 5: Write RED crash tests**

Inject failures:

- while writing the temporary file;
- after file fsync and before replace;
- after replace and before directory fsync;
- stale temporary left by a killed writer.

Old or new complete ledger is acceptable according to the acknowledged phase;
a partial transaction is never acceptable.

**Step 6: Run RED**

```bash
rtk pytest tests/unit/kernel/test_ledger_atomicity.py \
  tests/unit/kernel/test_transaction_store.py \
  -q -x
```

**Step 7: Implement the minimum extension**

Reuse the stable sidecar lock, canonical encoder, same-directory temporary,
file fsync, atomic replace, directory fsync, and stale-temp cleanup already in
`store.py`. Do not introduce a second ledger implementation.

Inside the lock:

1. replay and verify the current ledger;
2. derive the current research/authority/support projection;
3. compare all expected revisions;
4. validate transaction canonical identity;
5. append the one complete envelope;
6. persist atomically.

**Step 8: Run GREEN repeatedly and commit**

```bash
rtk pytest tests/unit/kernel/test_ledger_atomicity.py \
  tests/unit/kernel/test_transaction_store.py \
  -q -x
rtk pytest tests/unit/kernel/test_transaction_store.py \
  -q -x
rtk pytest tests/unit/kernel/test_transaction_store.py \
  -q -x
rtk ruff check src/orion/kernel/store.py \
  tests/unit/kernel/test_ledger_atomicity.py \
  tests/unit/kernel/test_transaction_store.py
rtk git add src/orion/kernel/store.py \
  src/orion/kernel/__init__.py \
  tests/unit/kernel/test_ledger_atomicity.py \
  tests/unit/kernel/test_transaction_store.py
rtk git commit -m "feat(kernel): atomically commit transition envelopes"
```

---

### Task 9: Integrate the protected propose-to-commit path

**Files:**

- Modify: `src/orion/kernel/apply.py`
- Modify: `src/orion/kernel/gate.py`
- Modify: `src/orion/kernel/round.py`
- Modify: `src/orion/kernel/driver.py`
- Modify: `src/orion/kernel/host.py`
- Modify: `tests/unit/kernel/test_self_driving_kernel.py`
- Create: `tests/unit/kernel/test_protected_transition_flow.py`

**Step 1: Write RED positive-control flow**

Through the protected host composition only:

```text
proposal
-> one evidence snapshot
-> pure plan
-> protected appraisal
-> relying-party authorization
-> append_transaction CAS
-> committed projection
```

Require relevant storage evidence and the registered host evaluator to close one
question only after a committed authorization.

**Step 2: Write RED non-`PASS` preservation tests**

For `FAIL`, `BLOCKED`, `CANNOT_CHECK`, evaluator exception, unknown registration,
and stale revisions:

- content may remain proposal/evidence-bound;
- no verified closure occurs;
- the complete decision/reasons commit;
- failure episodes remain available for learning.

**Step 3: Write RED sequential/batch exactness tests**

Require each accepted operation to consume the prior accepted post-state. The
transaction post-state must equal pure reducer replay and every accepted signed
subject. Conflicted or refused records must not appear in applied/verified IDs.

**Step 4: Write RED stale-writer tests**

Change ledger, research, authority, or support revision between appraisal and
commit. Require rejection of the old authorization and a complete new snapshot,
plan, appraisal, and authorization. Never reuse the old receipt.

**Step 5: Run RED**

```bash
rtk pytest tests/unit/kernel/test_protected_transition_flow.py \
  -q -x
```

**Step 6: Refactor round orchestration**

`grade_and_apply` remains a proposal/conformance module and never promotes.
`run_round` requests a transaction through the protected host composition and
returns committed outcomes only. Remove the current sequence of independent
`ANSWER`, `GRADING`, `EPISODE`, `RESIDUAL`, and `ROUND` appends.

Use exact projection hashes in episodes; remove `open:<count>` as state identity.
Serialize full `TaskEpisode` content in the envelope.

**Step 7: Run GREEN and commit**

```bash
rtk pytest tests/unit/kernel/test_protected_transition_flow.py \
  tests/unit/kernel/test_self_driving_kernel.py \
  -q
rtk ruff check src/orion/kernel/apply.py \
  src/orion/kernel/gate.py \
  src/orion/kernel/round.py \
  src/orion/kernel/driver.py \
  src/orion/kernel/host.py \
  tests/unit/kernel/test_protected_transition_flow.py \
  tests/unit/kernel/test_self_driving_kernel.py
rtk git add src/orion/kernel/apply.py \
  src/orion/kernel/gate.py \
  src/orion/kernel/round.py \
  src/orion/kernel/driver.py \
  src/orion/kernel/host.py \
  tests/unit/kernel/test_protected_transition_flow.py \
  tests/unit/kernel/test_self_driving_kernel.py
rtk git commit -m "feat(kernel): govern answer transitions end to end"
```

---

### Task 10: Replace re-evaluation replay with deterministic historical replay

**Files:**

- Create: `src/orion/kernel/replay.py`
- Create: `tests/unit/kernel/test_transition_replay.py`
- Modify: `src/orion/kernel/driver.py`
- Modify: `src/orion/kernel/report.py`
- Modify: `src/orion/kernel/scheduler.py`
- Modify: `src/orion/kernel/__init__.py`

**Step 1: Write the no-evaluator RED test**

Use evaluator/evidence adapters that raise if invoked. Replay a committed
transaction and require the exact post-projection without calling either.

**Step 2: Write crash-prefix RED tests**

Legacy `ANSWER` rows, orphan receipt-like rows, and transactions lacking a valid
terminal envelope must not change state. This retires the current failure where
an answer with zero completed rounds mutates replayed cells.

**Step 3: Write strict-version RED tests**

Unknown transition schema, workflow version, reducer version, pre-state hash,
operation order, authorization binding, or post-state hash raises typed replay
failure. Never silently skip a malformed state-changing row.

**Step 4: Write payload-completeness RED tests**

Handoff fields, active supersession tips, reopened coordinates, full episodes,
execution links, and residuals must round-trip. Include `MetricSpec` even if no
current committed answer uses the future PR #21 `metric_payload` path.

**Step 5: Run RED**

```bash
rtk pytest tests/unit/kernel/test_transition_replay.py \
  -q -x
```

**Step 6: Implement replay**

Replay starts from an exact versioned seed and consumes only `TRANSITION`
envelopes. It verifies historical registration/signature commitments recorded in
the envelope/projection, applies the pure reducer, and checks exact post-state.
It does not resolve current evidence or rerun current policy/evaluator code.

Reports, scheduler yields, completed-round count, and guard learning must derive
from committed transaction decisions, not loose joins over old entry kinds.

**Step 7: Run GREEN and commit**

```bash
rtk pytest tests/unit/kernel/test_transition_replay.py \
  tests/unit/kernel/test_self_driving_kernel.py \
  -q
rtk ruff check src/orion/kernel/replay.py \
  src/orion/kernel/driver.py \
  src/orion/kernel/report.py \
  src/orion/kernel/scheduler.py \
  tests/unit/kernel/test_transition_replay.py
rtk git add src/orion/kernel/replay.py \
  src/orion/kernel/driver.py \
  src/orion/kernel/report.py \
  src/orion/kernel/scheduler.py \
  src/orion/kernel/__init__.py \
  tests/unit/kernel/test_transition_replay.py
rtk git commit -m "feat(kernel): replay only committed historical transitions"
```

---

### Task 11: Append revalidation and reopen transitions

**Files:**

- Modify: `src/orion/kernel/transition.py`
- Modify: `src/orion/kernel/host.py`
- Modify: `src/orion/kernel/replay.py`
- Create: `tests/unit/kernel/test_revalidation.py`

**Step 1: Rewrite the current evidence-change expectation as RED**

Historical replay must still reconstruct the original committed state after a
working-tree artifact changes. Only an explicit current revalidation attempt may
capture new evidence and append a new decision.

**Step 2: Write RED dependency/status cases**

- One revoked dependency with another complete live support set -> remains live.
- No complete support and one unknown/stale dependency -> `CANNOT_CHECK` and
  reopen according to policy.
- All alternatives demonstrably broken -> `FAIL` and reopen.
- Key/policy/evaluator/trust-root revocation -> current revalidation required.

**Step 3: Write RED append-only history test**

After reopen, both the original authorized transition and later reopen transition
remain addressable. No historical receipt or verdict changes.

**Step 4: Run RED**

```bash
rtk pytest tests/unit/kernel/test_revalidation.py \
  -q -x
```

**Step 5: Implement current revalidation orchestration**

Revalidation is a new protected attempt with a new evidence snapshot,
appraisal, relying-party authorization, multi-revision expectation, and atomic
envelope. `REOPEN` removes the active tip from current support/closure projection
or marks the dimension provisional without deleting prior content/history.

**Step 6: Run GREEN and commit**

```bash
rtk pytest tests/unit/kernel/test_revalidation.py \
  tests/unit/kernel/test_transition_replay.py \
  -q
rtk ruff check src/orion/kernel/transition.py \
  src/orion/kernel/host.py \
  src/orion/kernel/replay.py \
  tests/unit/kernel/test_revalidation.py
rtk git add src/orion/kernel/transition.py \
  src/orion/kernel/host.py \
  src/orion/kernel/replay.py \
  tests/unit/kernel/test_revalidation.py
rtk git commit -m "feat(kernel): append protected revalidation and reopen"
```

---

### Task 12: Keep failure lessons and stopping evidence non-authoritative

**Files:**

- Modify: `src/orion/kernel/driver.py`
- Modify: `src/orion/kernel/guards.py`
- Modify: `src/orion/kernel/saturation.py`
- Modify: `tests/unit/kernel/test_self_driving_kernel.py`

**Step 1: Preserve recurrence as candidate-only**

Require repeated failure variations to create a `CANDIDATE` guard only. Caller
split IDs, round labels, or recurrence counts cannot activate behavior.

```python
assert guard.authority is LessonAuthority.CANDIDATE
assert not guard.active
```

Protected guard activation is a separate transition and remains out of this
minimum slice unless its replay/fresh-transfer evaluator exists.

**Step 2: Require positive observed lineage**

Empty/unknown lineages receive zero independence credit. Preserve
`certifies_recall is False` and a-priori-frame-only stopping semantics.

**Step 3: Bind growth to committed results**

Only applied authorized transition operations count as verified closures.
Conflicted appraisals, evidence-bound proposals, and uncommitted attempts do not
count. Failure/residual novelty still counts as observed negative knowledge.

**Step 4: Run RED/GREEN**

```bash
rtk pytest tests/unit/kernel/test_self_driving_kernel.py \
  -q
rtk ruff check src/orion/kernel/driver.py \
  src/orion/kernel/guards.py \
  src/orion/kernel/saturation.py \
  tests/unit/kernel/test_self_driving_kernel.py
```

**Step 5: Commit**

```bash
rtk git add src/orion/kernel/driver.py \
  src/orion/kernel/guards.py \
  src/orion/kernel/saturation.py \
  tests/unit/kernel/test_self_driving_kernel.py
rtk git commit -m "fix(kernel): keep learned behavior and stopping claims scoped"
```

---

### Task 13: Add explicit legacy-ledger migration quarantine

**Files:**

- Create: `src/orion/kernel/migration.py`
- Create: `tests/unit/kernel/test_legacy_migration.py`
- Modify: `src/orion/kernel/cli.py`
- Modify: `src/orion/kernel/report.py`
- Modify: `src/orion/kernel/__init__.py`

**Step 1: Write RED legacy-state tests**

A non-empty legacy ledger containing `ANSWER/GRADING/ROUND` but no versioned
transition genesis returns `MIGRATION_REQUIRED`. Legacy answers never mutate the
new projection and old raw `VERIFIED` labels never survive as authority.

**Step 2: Write RED proposal-import tests**

Migration preserves the old chain hash and row identities as an immutable archive
reference, imports legacy answers as proposals only, marks prior closures
provisional/reopened, and is deterministic/idempotent.

Repository JSONL answer files remain proposal inboxes; they are not silently
converted into authorized transitions.

**Step 3: Run RED**

```bash
rtk pytest tests/unit/kernel/test_legacy_migration.py \
  -q -x
```

**Step 4: Implement quarantine and CLI status**

`status`/`report` may inspect legacy rows. `run` refuses until an explicit
migration transaction is committed. Do not modify the old file in place; retain
a digest-addressed archive or require the operator to preserve it.

**Step 5: Run GREEN and commit**

```bash
rtk pytest tests/unit/kernel/test_legacy_migration.py \
  -q
rtk ruff check src/orion/kernel/migration.py \
  src/orion/kernel/cli.py \
  src/orion/kernel/report.py \
  tests/unit/kernel/test_legacy_migration.py
rtk git add src/orion/kernel/migration.py \
  src/orion/kernel/cli.py \
  src/orion/kernel/report.py \
  src/orion/kernel/__init__.py \
  tests/unit/kernel/test_legacy_migration.py
rtk git commit -m "feat(kernel): quarantine legacy replay authority"
```

---

### Task 14: Integration, hostile replay, and reconciliation

**Files:**

- Modify: `tests/integration/test_repo_answer_records.py`
- Create: `tests/integration/test_protected_kernel_lifecycle.py`
- Modify: all changed kernel files only as required by observed failures
- Update: relevant `research/failures/*/README.md`

**Step 1: Refresh concurrent state**

```bash
rtk git fetch --prune origin
rtk git status --short --branch
rtk git ls-remote origin refs/heads/main \
  refs/heads/self-orion/rakl-transfer-v1
```

If `origin/main` changed, inspect every new diff before rebasing or merging.
Never touch the Claude worktree and never force-push.

**Step 2: Run the targeted authority lifecycle**

```bash
rtk pytest tests/unit/kernel/test_protected_assurance.py \
  tests/unit/kernel/test_transition_identity.py \
  tests/unit/kernel/test_transition_reducer.py \
  tests/unit/kernel/test_evidence_snapshot.py \
  tests/unit/kernel/test_verifier_appraisal.py \
  tests/unit/kernel/test_authority_state.py \
  tests/unit/kernel/test_transition_authorization.py \
  tests/unit/kernel/test_authority_choke_point.py \
  tests/unit/kernel/test_ledger_atomicity.py \
  tests/unit/kernel/test_transaction_store.py \
  tests/unit/kernel/test_protected_transition_flow.py \
  tests/unit/kernel/test_transition_replay.py \
  tests/unit/kernel/test_revalidation.py \
  tests/unit/kernel/test_legacy_migration.py \
  tests/unit/kernel/test_self_driving_kernel.py \
  -q
```

**Step 3: Run integration tests**

```bash
rtk pytest tests/integration/test_repo_answer_records.py \
  tests/integration/test_protected_kernel_lifecycle.py \
  -q
```

Require:

- committed repository answers remain proposal/evidence-bound unless protected
  host registrations independently authorize them;
- the weather attack remains provisional;
- raw checks never promote;
- transaction conflict/race produces one winner;
- crash prefix never changes projected state;
- replay calls no evaluator;
- handoff and cross-round supersession round-trip;
- revocation appends reopen;
- recurrence stays candidate-only;
- empty lineage receives no independence credit.

**Step 4: Stress concurrency repeatedly**

```bash
rtk pytest tests/unit/kernel/test_ledger_atomicity.py \
  tests/unit/kernel/test_transaction_store.py \
  -q -x
rtk pytest tests/unit/kernel/test_ledger_atomicity.py \
  tests/unit/kernel/test_transaction_store.py \
  -q -x
rtk pytest tests/unit/kernel/test_ledger_atomicity.py \
  tests/unit/kernel/test_transaction_store.py \
  -q -x
```

**Step 5: Run full verification**

```bash
rtk pytest -q
rtk ruff check src/orion/kernel/assurance.py \
  src/orion/kernel/authority_state.py \
  src/orion/kernel/authorization.py \
  src/orion/kernel/evidence.py \
  src/orion/kernel/host.py \
  src/orion/kernel/migration.py \
  src/orion/kernel/replay.py \
  src/orion/kernel/store.py \
  src/orion/kernel/support.py \
  src/orion/kernel/transition.py \
  tests/unit/kernel \
  tests/integration/test_repo_answer_records.py \
  tests/integration/test_protected_kernel_lifecycle.py
rtk git diff --check
```

Repository-wide Ruff has a pre-existing `F403` baseline in
`src/orion/mechanics/__init__.py`. Do not claim global Ruff cleanliness unless a
separately scoped fix lands. Every changed Python file must be clean.

**Step 6: Independent review**

Review, from the committed diff rather than agent summaries:

- static authority choke-point;
- absence of caller-supplied keys/registries/callables;
- immutable evidence occasion;
- exact pre/post and batch ordering;
- appraisal-versus-authorization separation;
- all four verdicts;
- multi-revision CAS;
- transaction atomicity/idempotency;
- replay without evaluator execution;
- append-only revalidation/reopen;
- migration quarantine;
- exact failure-record claims.

**Step 7: Commit final integration evidence**

```bash
rtk git add tests/integration \
  research/failures \
  docs/plans/2026-08-16-protected-step-verification.md
rtk git commit -m "test(kernel): verify protected transition lifecycle"
```

## Explicit non-goals

This minimum does not implement distributed consensus, production PKI ceremony,
trusted wall-clock time, a public transparency log, general memory-poisoning
defense, domain-complete scientific evaluators, or autonomous policy mutation.
A local hash chain cannot prove that a valid tail was not removed; claim only
local prefix integrity unless an independent monotonic witness is later added.

## Reopen triggers

Reopen research and the affected task before implementation if:

- a domain evaluator cannot express its warrant without candidate-supplied
  authority material;
- one immutable evidence snapshot cannot represent the evidence occasion;
- the support model needs non-DNF defeasibility;
- authority/support state cannot share an atomic revision/CAS domain with the
  research transition;
- a sequential reducer cannot reproduce an appraised batch post-state;
- crash injection contradicts the file transaction model;
- an unknown workflow/reducer/schema version must be migrated;
- current main or PR #21 changes `AnswerRecord`, typed metric/handoff payloads,
  store semantics, or the protected host composition.

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
3. **Exact state.** Subject identity covers the complete research projection,
   including active record tips and reopen state, not open-question count alone.
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
    seed_hash: str
    cells: tuple[MechanicCell, ...]
    record_bindings: tuple[tuple[str, str], ...]
    active_record_tips: tuple[tuple[str, str, str], ...]
    reopened_coordinates: tuple[tuple[str, str, str], ...]

@dataclass(frozen=True)
class HostEvidenceSnapshot:
    snapshot_id: str
    root_configuration_hash: str
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

### Task 2: Freeze canonical projection and transition identity

**Files:**

- Create: `src/orion/kernel/transition.py`
- Create: `tests/unit/kernel/test_transition.py`
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

Also change active record tips while leaving cell content identical and require a
different projection hash.

**Step 2: Run RED**

```bash
rtk pytest tests/unit/kernel/test_transition.py \
  -q -x
```

Expected: FAIL because `orion.kernel.transition` does not exist.

**Step 3: Implement only versioned frozen data and codecs**

Define:

- `WORKFLOW_VERSION`;
- `REDUCER_VERSION`;
- `TransitionKind` with `ANSWER`, `REVALIDATE`, `REOPEN`, and
  `AUTHORITY_SUPPORT_UPDATE`;
- `ProgramProjection`;
- `LedgerExpectation`;
- explicit canonical encoders for every `MechanicCell`, `HandoffField`,
  `MetricSpec`, `DimensionWaiver`, and active-record field;
- `projection_hash`.

Do not add evaluator, signing, store, or mutation behavior.

**Step 4: Run GREEN**

```bash
rtk pytest tests/unit/kernel/test_transition.py \
  -q
rtk ruff check src/orion/kernel/transition.py \
  tests/unit/kernel/test_transition.py
```

**Step 5: Commit**

```bash
rtk git add src/orion/kernel/transition.py \
  src/orion/kernel/__init__.py \
  tests/unit/kernel/test_transition.py
rtk git commit -m "feat(kernel): define versioned research projection"
```

---

### Task 3: Capture one immutable host evidence snapshot

**Files:**

- Modify: `src/orion/kernel/evidence.py`
- Create: `tests/unit/kernel/test_evidence_snapshot.py`
- Modify: `src/orion/kernel/__init__.py`

**Step 1: Write the mutable-file RED test**

Use a resolver seam that changes the underlying file after the first read. Require
one snapshot to retain one content digest and byte/string payload throughout the
attempt.

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

**Step 3: Run RED**

```bash
rtk pytest tests/unit/kernel/test_evidence_snapshot.py \
  -q -x
```

**Step 4: Implement frozen snapshot data**

Add:

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
rtk pytest tests/unit/kernel/test_transition.py \
  tests/unit/kernel/test_transition_reducer.py \
  -q
rtk ruff check src/orion/kernel/transition.py \
  tests/unit/kernel/test_transition.py \
  tests/unit/kernel/test_transition_reducer.py
rtk git add src/orion/kernel/transition.py \
  tests/unit/kernel/test_transition.py \
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
  tests/unit/kernel/test_transition.py \
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

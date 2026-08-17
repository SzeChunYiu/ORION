# Development packet — issue #209 Phase-3 protocol pre-freeze

Status: **pre-registration only.** This packet and the modules it describes close
no gate, grant no authority and activate no code path. Issue #209 remains blocked
on issue #76 (Phase-2 closure).

## Development question

Issue #209 requires that the Phase-3 task class, governance protocol, matched
baseline, metric set and escalation conditions all be *frozen before outcome
access*. The dependency (#76) is still open. So the question is: what can be
authored now that is genuinely a pre-registration, and how is it kept inert until
an external host acts?

Authoring the protocol after #76 closes would not be a pre-registration — the
issue pool, the comparative outcomes and the statistics would all be selectable
after the fact. Pre-freezing while the dependency is open is the only ordering
under which the study is valid.

## Atomic fibres

1. define ordinary framework development against protected/constitutional work,
   by kind identity rather than by description;
2. freeze inclusion/exclusion rules for the sampled issue pool;
3. keep the sampling epoch and issue-pool fingerprint unbound until a host binds
   them;
4. require unresolved and failed sampled tasks to be preserved;
5. state what ORION owns versus what a worker may do under a bounded contract;
6. keep `OPEN`/`CANNOT_CHECK`/`ESCALATED` as first-class cycle terminals;
7. freeze a matched external-development baseline with explicit budget, retry and
   intervention matching;
8. predeclare the metric set with a designated primary efficacy endpoint, a
   primary safety endpoint, an interval method, alpha, a minimum effect size and
   a multiplicity rule;
9. represent the Phase-2 terminal subject and evidence receipt as *typed unbound*
   values, never fabricated ones;
10. give the Step-5 hostile battery real code to attack, and make each check
    differential rather than refusal-by-default.

## Incumbent mechanics and negative history

The Phase-2 machinery already establishes every convention this work needs, and
it is extended rather than duplicated:

- `orion.self_orion.phase2_preflight` — a pre-outcome protocol module with no
  PASS state and `grants_*` properties hardwired `False`. `phase3_preflight`
  mirrors its shape, including the staged binding order and the "identity, not
  count" lesson recorded in its comments (a gate that counted ten caller strings
  admitted ten fabricated attack ids).
- `orion.self_orion.phase2_io` — bindings are loadable from a host-owned file;
  the frozen protocol content itself stays code-owned and is only emitted.
  `phase3_io` follows this exactly, so a tampered binding file can move an
  identity but cannot retune the statistics or reopen the task class.
- `orion.self_orion.readiness` — `EvidenceStatus` (`PASS`/`FAIL`/`CANNOT_CHECK`)
  is imported rather than re-declared, and the module's note that there is no
  `GOVERNED_SELF_ORION` stage inside ORION is honoured: no new readiness stage is
  introduced.
- `orion.self_orion.evidence_admission` — `Phase2EvidenceReceipt` remains the
  binding whose hash a host will later bind into the Phase-3 authority boundary.

Negative history consulted: the Phase-2 preflight scar (counting strings
certifies the caller, not the attacks) and the repository's rule that caller
declaration booleans cannot create a PASS.

## Motivating defect — a real instance, not an invented category

The Step-5 battery is grounded in a defect confirmed on merged `main` rather
than in a category name.

`src/orion/self_orion/phase2_preflight.py` gates its three external identities
with `_sha256`, which is `len(value) == 64 and all(character in "0123456789abcdef" ...)`
— a **format** check. `assess_phase2_preflight` applies that check plus a
not-all-zeros test to `subject_revision_hash`, `provider_manifest_hash` and
`evaluator_artifact_hash`, then returns `READY_TO_EXECUTE_SHADOW_TRIAL`.
Nothing compares any of the three against a frozen expected value, so
`("a"*64, "b"*64, "c"*64)` certifies the Phase-2 live campaign as ready to
execute. The module's own test `test_binding_order_requires_subject_then_provider_then_evaluator`
performs exactly that substitution and asserts it advances.

Two divergent wide-task registries also exist in the tree —
`phase2:wide:microglia-complement-cross-disease` in `phase2_preflight.py` and
`P5.LIVE.WIDE.stopping-rule-source-families` in `live_packet.py`. Whether a
merged workflow rebuilds the packet from the second while the freeze declares
the first is a routing question I did not verify; it belongs to the issue-8
lane. The format-only gate above I did verify directly on `origin/main`.

**Repair of the Phase-2 module is not in this lane** (issue 8 owns it). What is
in this lane is making the class impossible to reintroduce in Phase 3.

### The generalizable class

*A registry or declared identity that exists but is never consulted is not a
gate.* Well-formed is not bound.

The bitter detail is the part worth designing against: that module records this
exact lesson verbatim in a comment above its attack-id check, and the identical
defect sits ten lines below it, in the same function, on the identity bindings.
**A lesson recorded in a comment does not propagate to sibling checks.**

### What this protocol does about it

1. `Phase3ProtocolInvariant` makes the class machine-readable
   (`DECLARED_IDENTITIES_MUST_BE_COMPARED`, `WELL_FORMED_IS_NOT_BOUND`,
   `FROZEN_REGISTRIES_MUST_BE_CONSULTED_BY_IDENTITY`,
   `EVERY_BINDING_CARRIES_ITS_OWN_HOSTILE_TEST`) and serializes it into the
   frozen protocol artifact, so it travels with the protocol rather than living
   in a comment.
2. `assess_phase3_preflight` takes a host-owned `Phase3ExternalExpectation` and
   **compares** every declared identity against it. With no expectation there is
   nothing to compare against, so well-formed values stop at
   `COMPARE_AGAINST_EXTERNAL_EXPECTATION` no matter how correctly shaped.
3. `test_every_expectation_field_is_compared` enumerates the expectation
   dataclass's fields reflectively and perturbs each one. A binding added later
   without a matching comparison fails the suite instead of silently widening
   the gate — this is the anti-recurrence device, and it does not depend on a
   future author reading a comment.
4. The no-alarm case is asserted throughout: a correct, fully bound, fully
   matched input must reach `REQUEST_EXTERNAL_PHASE3_AUTHORIZATION` with zero
   blockers, so fail-closed is distinguishable from broken-shut.

## Saturation assessment

The bounded question is not "is Governed Self-ORION ready?" — that is exactly
what may not be answered here. It is "can the Phase-3 study be frozen such that
no later actor can select the task class, the metric set or the statistics after
seeing outcomes, and such that nothing self-activates when #76 closes?"

Saturated when: every protected work kind is excluded by enum identity; every
statistic is a number rather than a placeholder; every external identity is the
repository's unbound sentinel; and every authority boundary has a differential
hostile test.

## Challenge to the saturation basis

A pre-freeze that looks complete can still fail in four ways, each of which has a
test:

- metric *names* frozen but the analysis left open — defeated by a designated
  primary endpoint, alpha, interval method and minimum effect size;
- a hostile screen that rejects everything — defeated by pairing every attack
  with an otherwise-identical clean control that must clear the same check;
- an unbound field quietly filled with a plausible value — defeated by asserting
  the sentinel and by refusing to construct a host expectation from it;
- a committed JSON artifact drifting from the code — defeated by a drift test
  comparing parsed dicts (not file bytes, which a whitespace edit would break).

## Miss hypotheses

- a future protected work kind is added to the enum but not to the exclusion
  list (covered: exclusion is checked against `PROTECTED_WORK_KINDS` by set
  difference and names the missing kind);
- a cycle terminates `RESOLVED` on missing evidence (covered by H05, with the
  companion test that abstention on the same missing evidence is *admissible*);
- negative-history laundering by relabelling rather than deletion (covered by a
  same-count, plausible-ids attack);
- worker output phrased as an authorization (covered by H06, which treats any
  non-empty declared grant as an escalation attempt regardless of wording).

## Reopen triggers

Reopen this freeze if: #76 closes on evidence bound to a subject this protocol
cannot address; an external host declines the promotion-authority binding; the
metric set proves unmeasurable during a dry run *before* any outcome is observed;
or a review shows the task class admits work that touches a protected surface.
Any change after outcome access invalidates the pre-registration and must create
a new versioned protocol id rather than amend `-v1`.

## Frozen implementation hypothesis

Three additive stdlib-only modules under `orion.self_orion`:

- `phase3_preflight` — the versioned protocol (task class, governance contract,
  matched baseline, metric set, statistics policy, escalation conditions,
  authority boundary) plus `assess_phase3_preflight`, whose most favourable
  status is `REQUEST_EXTERNAL_PHASE3_AUTHORIZATION` — a request, not a grant;
- `phase3_authority` — a fail-closed screen for a governed-cycle promotion
  request whose decision enum has no member expressing a promotion;
- `phase3_io` — emission of `Phase3ProtocolFreeze.v1` and loading of
  `Phase3HostBinding.v1` (host identities only).

Plus the canonical artifact `development/phase3/PHASE3_PROTOCOL_FREEZE_v1.json`
and two test modules: known-answer tests for the protocol and the differential
Step-5 hostile battery.

## Handoff when #76 closes

No code added here reads issue state, polls a dependency, or self-activates. When
#76 closes on merged Phase-2 evidence, a **human host** writes a
`Phase3HostBinding.v1` file containing the exact Phase-2 terminal subject
revision, the Phase-2 evidence receipt hash, the external promotion-authority
identity and the protected custody lineage, then binds the sampling epoch and
issue-pool fingerprint. Until that file exists and an external authority acts on
the resulting request, `assess_phase3_preflight` reports
`BIND_PHASE2_TERMINAL_EVIDENCE` and every `grants_*` property is `False`.

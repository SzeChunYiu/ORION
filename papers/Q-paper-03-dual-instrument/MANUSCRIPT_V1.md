# Dual-Instrument Research Control: Host-Capability Receipts, Typed Campaign Controllers, and a Controller–Host Agreement Benchmark

**Manuscript V1 — 2026-08-21.** Candidate Paper Q3 per
`papers/Q-paper-02-recursive-recovery/PUBLICATION_PLAN.md`. Every factual
statement in this manuscript is bound to a committed file in this repository; paths are
cited inline. Claims are bounded by the accompanying `CLAIM_LEDGER.md`. Nothing in this
paper grants scientific, novelty, promotion, or R6 authority.

## Abstract

LLM-driven research loops routinely produce conclusions that cannot be replayed, audited,
or cross-checked: the tool calls are ephemeral, the reasoning is free text, and there is no
second instrument to disagree with. We present a dual-instrument architecture and the first
measurement of a new benchmark class built on it. The first instrument,
`orion-research-harness` (`packages/orion-research-harness/`), lets any tool-capable host
session drive a deterministic research kernel through immutable, digest-bound capability
receipts: every host request has a content-derived identity, every result is bound to the
exact request, successful receipts are immutable, orchestration failures are recoverable
without erasing history, and protected reference data is guarded by construction. The
second instrument is a typed campaign controller on the same receipt substrate: production
epistemic-control modules — not an LLM — make each decision over receipt-transcribed
observations, and every state, decision, and transition carries all authority booleans
false by construction. Benchmark V0
(`development/orion-q-max-r0/DUAL_HARNESS_AGREEMENT_BENCHMARK_V0_PROTOCOL.md`) poses the
same live frontier question — which epistemic layer is responsible for the remaining gap in
a receipted quantum-compilation programme — to both instruments under a protocol frozen
before either outcome existed, with divergence defined as data, not failure. In the first
instance the verdict is AGREE: both instruments independently diagnosed the
representation-regime-characterization layer and selected regime characterization as the
next move, with the typed controller's revision gate independently withholding the
not-yet-licensed representation-split revision; the deferred coordinate, scored later
against two independently launched frontier lanes (R6P, R6Q), is ALIGNED. We document two
open harness defects found in live use and one repaired the same day, and bound all claims
to a single question instance: this is a benchmark definition with a first measurement, not
an evaluation study.

## 1. Introduction

An autonomous or semi-autonomous research loop built around a large language model has two
structural problems that are independent of how capable the model is.

First, **provenance**: the loop's external interactions — searches, file reads, code
executions, model completions — are usually transient. When a conclusion is challenged, the
exact inputs that produced it cannot be re-materialized; the run cannot be replayed, and a
re-run is a different experiment. Second, **cross-instrument control**: when the only
decision-maker in the loop is an LLM, there is no independent instrument against which its
diagnosis can be checked. Agreement with itself (self-consistency, resampling) is not
independence, and comparison against ground truth is unavailable exactly where research
loops matter most — at a live frontier where no ground truth exists yet.

This paper addresses both problems with committed, replayable artifacts:

1. An **instrument contract** in which a research kernel never performs an external action
   directly. It emits a deterministic, content-addressed capability request; the
   surrounding host services it; the result is ingested as an immutable receipt
   digest-bound to the exact request; and the kernel replays deterministically from the
   receipt store (`packages/orion-research-harness/README.md`,
   `packages/orion-research-harness/HOST_PROTOCOL.md`).
2. A **typed campaign controller** on the same substrate in which the per-cycle decision is
   made by production epistemic-control modules over typed observations, with no LLM and no
   free-text reasoning in the decision path
   (`packages/orion-research-harness/src/orion_research_harness/campaign_control.py`).
3. A **controller–host agreement benchmark**: the same frozen frontier question is posed to
   an LLM-host-driven lane and to the typed-controller lane, and the recorded quantity is
   inter-instrument epistemic agreement — with later frontier outcomes serving as deferred
   scoring (`development/orion-q-max-r0/DUAL_HARNESS_AGREEMENT_BENCHMARK_V0_PROTOCOL.md`).

The instruments were verified live on 2026-08-21: a full host-driven end-to-end drive of
every command and capability kind
(`development/orion-research-harness/E2E_HOST_DRIVE_VERIFICATION_2026-08-21.md`), and a
campaign-layer drive of a real receipted research chain terminating in an honest frozen
negative (`development/orion-q-max-r0/HARNESS_R6_DRIVE_VERIFICATION_2026-08-21.md`).
Benchmark V0 was then executed with both lanes' raw receipts archived and the verdict
recorded verbatim
(`development/orion-q-max-r0/dual-harness-benchmark-v0/DUAL_HARNESS_AGREEMENT_BENCHMARK_V0_RESULTS.json`).

## 2. Instrument architecture

### 2.1 The host-capability receipt contract

The harness separates the scientific kernel from every capability it does not own. The
kernel (`OrionRuntime`/`OrionSolver`, reached through
`packages/orion-research-harness/src/orion_research_harness/runner.py` and
`recursive_runner.py`) requests capabilities; the host supplies them. The contract has five
load-bearing properties, each implemented in a specific committed module.

**Deterministic request identity.** A request's identity is derived from its content:
`request_id = "hostreq:" + sha256(canonical_json({session_id, capability, payload}))`
(`request_id_for`, `packages/orion-research-harness/src/orion_research_harness/protocol.py`
lines 40–52, over the canonical JSON of lines 18–23). The same logical need always maps to
the same identity within a workspace session, which is what makes replay possible: on
re-solve, the kernel re-derives the identity and finds the existing receipt instead of
re-asking the host.

**Digest binding.** Requests and results are self-validating. `CapabilityRequest.validate`
recomputes both the request id and the request digest from content and rejects mismatches
(`protocol.py` lines 131–149). `CapabilityResult.validate` recomputes the result digest and
cross-checks `request_id` and `request_digest` against the exact request being answered
(`protocol.py` lines 244–272). A result cannot be attached to a different request than the
one it answered.

**Immutability.** The workspace persists every receipt with create-only semantics: a
temp file is written, fsynced, and `os.link`ed into place, and an existing file is never
replaced (`_write_json_create`,
`packages/orion-research-harness/src/orion_research_harness/workspace.py` lines 30–48).
Re-ingesting the identical result is idempotent; ingesting different content for the same
request raises `"result already exists with different content or executor"`
(`workspace.py` lines 279–294). Both behaviors were exercised live (steps 24b/24c of
`development/orion-research-harness/E2E_HOST_DRIVE_VERIFICATION_2026-08-21.md`).

**Failure as orchestration condition, never as evidence.** A missing result raises the
control signal `HostCapabilityRequired`; a failed result raises `HostCapabilityFailed`
(`packages/orion-research-harness/src/orion_research_harness/broker.py` lines 29–53).
These are `BaseException` control signals documented in-code as "not scientific evidence";
the CLI maps them to exit codes 2 and 3
(`packages/orion-research-harness/src/orion_research_harness/cli.py` lines 304–311).
`HOST_PROTOCOL.md` correspondingly forbids the host from turning an unavailable tool into
evidence against the kernel. Broker-side result validation is strict per capability kind:
`LLM_COMPLETE` output shape, `WEB_SEARCH` items with non-empty `source_uri` and content,
and `VERIFY_EVIDENCE` failing closed with the rule that a passing verification must carry
at least one certificate id (`broker.py` lines 90–231).

**Retry-failed recovery with protected history.** Because a failed receipt binds to its
deterministic identity, a transient orchestration failure (dead interpreter, missing
module) would otherwise pin the workspace to that failure forever — a real defect observed
live and repaired the same day (section 6, D1). The repair,
`orion-harness retry-failed` / `ResearchWorkspace.archive_failed_result`
(`workspace.py` lines 330–358), moves the failed receipt bytes-unchanged to
`results/archived/<request>.failed-<n>.json` and makes the identity pending again. Only
**failed** results may be archived; successful receipts stay immutable
(`workspace.py` line 342; regression tests in
`packages/orion-research-harness/tests/test_retry_failed.py`).

Local capabilities (`FILE_READ`, `FILE_WRITE`, `FILE_LIST`, `SHELL`, `PYTHON`) are confined
to the workspace's project root by `_confined`
(`packages/orion-research-harness/src/orion_research_harness/local_tools.py` lines 26–34;
escape attempt verified live in E2E step 24a), process tools are opt-in per workspace,
`SHELL` never uses `shell=True`, output is bounded and drained continuously, process groups
are killed on timeout, and nonzero exits are persisted as failed receipts
(`local_tools.py` lines 157–269). The README states explicitly that this is process
safety, not an OS sandbox (`packages/orion-research-harness/README.md`, "Local capabilities
and process safety"; the live `SHELL` receipt records `"sandboxed": false`).

The full contract was verified end-to-end by a live host session on 2026-08-21: all 12 CLI
commands, all 8 implemented capability kinds, deterministic replay with zero new host
requests on re-solve, both failure lanes, tamper rejection, and path containment — 26
requests and 25 results archived under
`development/orion-research-harness/e2e-2026-08-21-receipts/`, with the package test suite
at 30/30 (`development/orion-research-harness/E2E_HOST_DRIVE_VERIFICATION_2026-08-21.md`).

### 2.2 The typed campaign layer

Campaigns add a persistent multi-cycle control loop above the same workspace and receipt
protocol (`packages/orion-research-harness/README.md`, "Persistent scientific campaigns").
The cycle is:

frozen campaign state → production responsibility/revision/computation control → selected
registered capability → digest-bound host/local result → strict result-contract validation
→ evidence admission and protected-custody checks → immutable next state and cycle receipt.

**Frozen manifests and hash-chained state.** A campaign manifest is validated
(`validate_manifest`,
`packages/orion-research-harness/src/orion_research_harness/campaign_control.py` lines
73–282) and frozen: re-saving with different content is rejected
(`workspace.py` lines 457–475), and `decide_campaign` refuses to decide if the manifest
digest no longer matches the state's frozen `manifest_digest`
(`campaign_control.py` lines 398–399). Campaign state, decisions, and transitions are
digest-signed objects (`CampaignState`, `CampaignDecision`, `CampaignTransition` in
`packages/orion-research-harness/src/orion_research_harness/campaign_protocol.py`), and
each transition binds `before_state_digest`, `decision_digest`, the capability request and
result digests, and `after_state_digest` (`campaign_runner.py` lines 485–514), so a
campaign's history is a verifiable chain of immutable receipts.

**Native typed decisions.** The per-cycle decision is composed exclusively from production
ORION control modules — `orion.transfer.v2.epistemic_responsibility`,
`interface_adequacy`, `higher_order_epistemic_mechanics`, `epistemic_computation`, and
`orion.self_orion.revision_gate` / `epistemic_control`
(imports at `campaign_control.py` lines 5–26; composition in `decide_campaign`, lines
395–486). The manifest supplies typed hypotheses with discriminating expected-observation
sets, interface checks, revision mechanics, and computation actions; the modules perform
the discrimination. There is no LLM call and no free-text reasoning anywhere in this path.

**Strict result contracts.** A capability result is admitted as evidence only through the
manifest's declared contract: `DIRECT_JSON` or `SHELL_JSON_TOKEN` parsing, required payload
values compared with exact type equality (a `"false"` string does not pass a `False`
check), and typed evidence transforms
(`packages/orion-research-harness/src/orion_research_harness/campaign_runner.py` lines
59–184). A malformed `success=true` result becomes `CAPABILITY_CONTRACT_FAILED` and cannot
change observations or advance the campaign (`campaign_runner.py` lines 312–332, 432–443).

**Protected custody.** Protected references (path, git blob id, strict boolean `released`)
travel in campaign state. Before any capability executes, `_protect_unreleased_refs` scans
the capability payload, its declared read paths, and — for `SHELL` invocations of a Python
script — the resolved script's full text for any unreleased protected path or blob
substring, raising `PermissionError` on contact (`campaign_runner.py` lines 187–239).
Release is only possible through an explicit
`release_protected_refs_on_success` declaration validated against known refs
(`campaign_runner.py` lines 242–263). In every committed campaign receipt in this paper the
reserved stretched-N2 DUCC2 subject (blob `6ab53f2a83c1f8ab5cc3bf4309525fb1ec7421dd`)
remains `released: false` and was never opened.

### 2.3 Authority boundaries: all grants false by construction

The architecture treats authority as something a receipt can never mint. Three independent
mechanisms enforce this:

1. Every campaign state, decision, and transition serializes with the six authority fields
   — `grants_scientific_authority`, `grants_novelty_authority`,
   `grants_adoption_authority`, `grants_promotion_authority`, `grants_merge_authority`,
   `grants_global_task_stop_authority` — hard-coded false (`_authority_false`,
   `campaign_protocol.py` lines 13–24), and deserialization rejects any object where one is
   not false (`_require_authority_false`, lines 76–79).
2. The campaign runner recursively scans every admitted capability payload and rejects any
   nested key from the forbidden set (including `r6_authority` and
   `grants_revision_authority`) whose value is `True` — "capability attempted authority
   escalation" (`campaign_runner.py` lines 18–56).
3. The stated contract — a host result, navigation result, or campaign capability never
   grants scientific, revision, novelty, adoption, promotion, merge, or global-stop
   authority by itself — is documented in
   `packages/orion-research-harness/README.md` ("Authority boundary") and
   `HOST_PROTOCOL.md`, and terminal names carry it explicitly (e.g.
   `R6_PROSPECTIVE_VERDICT_RECORDED__NOT_SELF_AUTHORIZING`).

## 3. The campaign layer driving a real research chain

Before the benchmark, the typed instrument was exercised on the real ORION-Q MAX-R6
programme (`development/orion-q-max-r0/HARNESS_R6_DRIVE_VERIFICATION_2026-08-21.md`). The
`orion-q:max-r6-live` campaign
(`packages/orion-research-harness/src/orion_research_harness/domains/orion_q/max_r6.py`)
drove four cycles — N0 `COMPUTE:DONOR_CLOSURE_PACKET`, N1 `REV:CHANGE_INTERFACE`, N2
`REV:GROW_METHOD_LANGUAGE`, then the frozen prospective replay
`COMPUTE:R6_PROSPECTIVE_REPLAY` — terminating in
`R6_PROSPECTIVE_VERDICT_RECORDED__NOT_SELF_AUTHORIZING` with recorded observations
`R6_EARNED = NO`, `R6_PROTECTED_SUBJECT_ACCESSED = NO`
(receipts under `development/orion-q-max-r0/harness-r6-drive-2026-08-21/`, summarized in
`CAMPAIGN_RUN_RECEIPT.json`). The instrument recorded a frozen scientific **negative** —
the joint exact compiler did not strictly beat the frame-only donor on any open subject, so
the protected subject was correctly never opened — demonstrating that the control loop
neither manufactures positives nor converts resource exhaustion into closure. The same
verification session raised the package suite from 88 passed / 2 failed (plus one
collection error) to 98/0 with the repairs enumerated in that document's section 3.

## 4. Benchmark definition: controller–host agreement

The benchmark protocol
(`development/orion-q-max-r0/DUAL_HARNESS_AGREEMENT_BENCHMARK_V0_PROTOCOL.md`) was frozen
on 2026-08-21 **before either lane's outcome existed**, with authority declared
benchmark/diagnostic only.

**Question.** Both lanes receive the identical live frontier question: given the committed
R6 receipts through R6O (family saturation; support dominance verified with a refutation at
the Tag-repair gap; enlarged-donor closure refuted by a converse frame-for-Tag regime;
chemistry donor-exact on all recorded optima), which epistemic layer is responsible for the
remaining gap, and what is the correct next research move?

**Lane A — generic harness, host-driven.** An `orion-harness` workspace in the default
recursive-solve mode with `--max-iterations 3`; a live LLM session acts as external host
and services capabilities **only** with evidence drawn from committed repository receipts —
file paths cited in every `WEB_SEARCH` item, no external web. The verified reconstruct
summary and terminal constitute Lane A's answer.

**Lane B — typed campaign controller.** A frozen campaign manifest
(`packages/orion-research-harness/src/orion_research_harness/domains/orion_q/post_r6o_diagnosis.py`)
whose initial observations are transcribed verbatim from committed receipts with per-field
provenance recorded in the module docstring; the decision is made by the production control
modules in one native cycle, with no LLM in the loop. The protocol requires that the
manifest not encode the answer: every hypothesis must be observation-discriminable, and at
least three materially different responsible layers must be representable. The committed
manifest represents four: `RESP:CURRENT_SEARCH_INCOMPLETE`,
`RESP:DONOR_FAMILY_INCOMPLETE`, `RESP:REPRESENTATION_REGIME_UNCHARACTERIZED`, and
`RESP:METHOD_LANGUAGE_INADEQUATE`, each with a genuine survival region in observation
space and each bound to a typed revision mechanic mapped to a recording capability, so any
native outcome could have completed the cycle.

**Fixed comparison coordinates.** (1) diagnosed responsible layer; (2) selected next move;
(3) evidence basis; (4) agreement with the two independently launched frontier lanes (R6P
donor-extension, R6Q regime-characterization), scored only after A and B are recorded;
(5) cost profile.

**Outcome space.** AGREE / PARTIAL / DISAGREE — all valid. Divergence between instruments
is defined as **data**, not failure: a DISAGREE outcome would be recorded verbatim with
both lanes' raw receipts, exactly as an AGREE is. The benchmark is reusable: future waves
re-pose new frontier questions to both lanes under the same frozen protocol and accumulate
an agreement series.

This is deliberately a different measured quantity from task-success benchmarking. No
ground truth for the frontier question exists at measurement time; the benchmark measures
whether two architecturally different instruments — an LLM-hosted replayable solve and a
typed non-LLM controller — reach the same diagnosis and move, with the frontier's later
outcomes providing deferred, receipt-bound scoring for one coordinate.

## 5. The first measurement

All values below are quoted from
`development/orion-q-max-r0/dual-harness-benchmark-v0/DUAL_HARNESS_AGREEMENT_BENCHMARK_V0_RESULTS.json`
and the two lane receipts.

**Lane A** (receipt
`development/orion-q-max-r0/dual-harness-benchmark-v0/DUAL_HARNESS_LANE_A_RECEIPT.json`;
full workspace archived under `.../dual-harness-benchmark-v0/lane-a-receipts/`):
diagnosed layer `REPRESENTATION_REGIME_CHARACTERIZATION`; selected move
`REGIME_PREDICATE_CHARACTERIZATION_PRIMARY__WEIGHT2_CLOSURE_COMPLEMENTARY`; answer summary
verbatim: "Responsible layer: representation-regime characterization (gap is neither
optimization deficiency nor donor incompleteness alone; the missing object is a decidable
boundary criterion). Next move: execute the regime-predicate characterization as primary
with the weight-2 closure test as complementary probe, then a prospective fresh-subject
test." The solver terminal was `COMPLETE` with `solution_status: CANNOT_CHECK` — the
bounded-saturation accounting honestly reports incomplete route coverage at the iteration
bound (the same behavior documented as a non-defect in the E2E verification) — while the
diagnosis is carried by the verified reconstruct summary bound to four verified evidence
items. Cost: 13 host capability receipts.

**Lane B** (receipt `development/orion-q-max-r0/DUAL_HARNESS_LANE_B_RECEIPT.json`):
identified hypothesis `RESP:REPRESENTATION_REGIME_UNCHARACTERIZED` with defeated
hypotheses `RESP:CURRENT_SEARCH_INCOMPLETE`, `RESP:DONOR_FAMILY_INCOMPLETE`, and
`RESP:METHOD_LANGUAGE_INADEQUATE`; selected move `COMPUTE:REGIME_CHARACTERIZATION`;
terminal `POST_R6O_DIAGNOSIS_RECORDED__NOT_SELF_AUTHORIZING`; decision digest
`d6ba348c0ee0d5098ea4a7fa52d8e021d4f34dc3ee7920b3e40495188b1b3904` under manifest digest
`064ead57c2e1b1f02426dfea4f5a1184cb95440db52b77c1642964e135757ed4`; decided by the six
production module functions listed in the receipt's `provenance.decided_by`. Cost: one
native cycle, sub-second decision after manifest construction. Every authority boolean in
the decision, state, and transition is false, and the protected stretched-N2 reference
remains `released: false`.

**The revision-gate mechanism.** The most diagnostic mechanics detail is that Lane B's
framework itself withheld the unlicensed move. The revision mechanic bound to the
surviving hypothesis, `REV:SPLIT_REPRESENTATION_REGIME`, carries the hard requirement
`OBLIGATION:REGIME_MEMBERSHIP_PREDICATE_FROZEN`, whose obligation state is `UNRESOLVED`
because the receipts show no frozen regime-membership predicate exists
(`post_r6o_diagnosis.py`, manifest phase `D0`). Under the production fail-closed
semantics, the revision gate returned `status: UNRESOLVED` with reason
`NO_ADMISSIBLE_WITH_UNRESOLVED_CANDIDATES`, and the composed control selected the
characterization computation instead, with reason
`REVISION_NOT_YET_SELECTABLE_OPTIONAL_COMPUTE_AVAILABLE`
(`DUAL_HARNESS_LANE_B_RECEIPT.json`, `decision.revision` and `decision.control`). The
controller did not merely pick the same answer as Lane A; it derived "characterize before
you split" from the typed obligation structure — computation must precede revision because
the revision's license does not yet exist. The obligation lives on the revision mechanic
bound to a specific hypothesis, not phase-wide, so the computation is reached only when
that hypothesis is the identified survivor.

**Verdict.** AGREE on all scored coordinates. Coordinate 1: both name the
representation-regime-characterization layer. Coordinate 2: both select regime
characterization as the primary move (Lane A additionally ranks the weight-2 closure test
as complementary; Lane B's mechanics reach it only after the predicate obligation
resolves). Coordinate 3: overlapping-by-construction — both lanes were grounded
exclusively in the committed R6N/R6O/R6M receipt corpus, Lane A through path-cited
verified `WEB_SEARCH` items, Lane B through typed observations transcribed with per-field
provenance.

**Deferred scoring by frontier outcomes.** Coordinate 4 was scored after the two
independently launched frontier lanes landed, and is recorded as **ALIGNED**: R6Q found an
exact regime-membership predicate — authority
`MAX_R6Q_REGIME_PREDICATE_EXACT__TWO_TRADE_CHARACTERIZATION_ON_VERIFIED_DOMAINS__NOT_R6`
(`research/extensions/orion-q/MAX_R6Q_REGIME_PREDICATE_RESULTS.json`) — and R6P, the
complementary move Lane A ranked second, restored family closure at support two on all
verified domains — authority
`MAX_R6P_WEIGHT2_FRAME_DONOR_CLOSURE_VERIFIED__FAMILY_CLOSURE_RESTORED_AT_SUPPORT_TWO_ON_VERIFIED_DOMAINS__NOT_R6`
(`research/extensions/orion-q/MAX_R6P_WEIGHT2_FRAME_DONOR_CLOSURE_RESULTS.json`). Neither
instrument selected the defeated moves (further search, donor absorption alone,
method-language growth), and the outcomes did not reward them either. We stress the
boundary: one aligned instance is anecdotal support for the benchmark's construct, not
evidence of predictive validity.

## 6. Instrument defects observed in live use

An instrument paper owes its readers the instrument's failure modes. Three defects were
encountered during the 2026-08-21 live drives on this branch; one was repaired the same
day, two remain open at the time of writing.

**D1 (repaired): failed-receipt pinning.** A transient environment failure (system
`python` without numpy) produced a failed receipt permanently bound to its deterministic
request identity; every rerun replayed the failure and the campaign workspace was
unrecoverable by design
(`development/orion-q-max-r0/HARNESS_R6_DRIVE_VERIFICATION_2026-08-21.md`, sections 2–3).
Repair: the `retry-failed` mechanism of section 2.1, landed with regression tests
(`packages/orion-research-harness/tests/test_retry_failed.py`); the originally poisoned
workspace was healed live with the new command and then completed its full chain.

**D2 (open): recursive decompose crash on a malformed-successful receipt.** The broker
validates the capability **envelope** of an `LLM_COMPLETE` result — output must be a
string or an object with string `content` — and converts violations into a structured
`HostCapabilityFailed` (`broker.py` lines 108–125). But the **semantic** parse of
`content` happens later, in the reasoner: `LLMResearchReasoner._call` executes
`json.loads(response.content)` and raises
`ValueError("LLM returned invalid JSON for {task}")` on failure
(`src/orion/providers/reasoner/llm.py` lines 33–48). In the recursive solve path this
parse is first reached at root decomposition (`solve_root` →
`problem_planner.decompose`,
`packages/orion-research-harness/src/orion_research_harness/recursive_runner.py` line 423;
`decompose_problem` in `src/orion/providers/reasoner/recursive_llm.py` lines 248–271), and
`run_problem_recursive` catches only `HostCapabilityRequired`, `HostCapabilityFailed`, and
two specific `RuntimeError` sentinels (`recursive_runner.py` lines 819–857). A host that
ingests `success=true` with well-formed envelope but non-JSON `content` therefore crashes
the solve with an unstructured traceback instead of the documented exit-3
`HOST_CAPABILITY_FAILED` outcome; the CLI adds no further handling
(`packages/orion-research-harness/src/orion_research_harness/cli.py` lines 282–311).

**D3 (open): successful-malformed receipts are unrecoverable.** The receipt in D2 is
`success=true`, and successful receipts are deliberately immutable:
`archive_failed_result` refuses them — "only failed results may be archived for retry"
(`workspace.py` line 342) — and ingesting corrected content for the same request is
rejected as tampering (`workspace.py` line 293). Because request identity is
deterministic, every subsequent solve re-derives the same identity and replays the same
malformed receipt, so the workspace is permanently pinned to the crash of D2 (or, in the
campaign layer, to a permanent `CAPABILITY_CONTRACT_FAILED` — the campaign path degrades
gracefully rather than crashing, `campaign_runner.py` lines 432–443, but likewise cannot
free the identity). The recovery contract of section 2.1 covers only the
failed-receipt lane by design; there is currently no sanctioned recovery for a
successful-but-semantically-malformed receipt short of abandoning the workspace (a fresh
workspace mints a new `session_id` and therefore fresh identities, `workspace.py` lines
159–196).

Both open defects require a host error to trigger — `HOST_PROTOCOL.md` obliges hosts to
return schema-conforming content — and neither can corrupt scientific state: D2 halts the
run, and D3's campaign-side manifestation is an explicit contract failure that admits no
evidence. They are nonetheless real instrument defects: the failure is reported in the
wrong lane (crash instead of structured failure), and the custody guarantee
(immutability) currently over-constrains recovery. Per the repository's own rule
(`packages/orion-research-harness/README.md`, "Authority boundary"), the repair path is to
fix the harness under the development protocol and replay the unchanged scientific gates,
not to weaken any contract post-hoc.

## 7. Limitations

**Single instance.** Benchmark V0 contains exactly one question instance with verdict
AGREE. No agreement rate, no statistics, and no reliability claim for either instrument
follow from it (`DUAL_HARNESS_AGREEMENT_BENCHMARK_V0_RESULTS.json`, `claim_boundary`). The
publication plan gates submission on at least 2–3 further instances
(`papers/Q-paper-02-recursive-recovery/PUBLICATION_PLAN.md`, Paper Q3).

**The Lane A host is an LLM session.** Lane A's independence from Lane B is architectural
(different decision procedure, different failure modes), not total: the generic lane's
capabilities were serviced by a live LLM session, and the same class of system authored the
free-text summaries that were then verified against receipts. The lanes share the receipt
corpus by construction (coordinate 3 is "overlapping", not independent).

**Manifest construction is human/LLM-authored.** The Lane B decision is native and typed,
but the manifest — hypotheses, expected-observation sets, obligation states, transcribed
observations — was authored by a person/LLM session from committed receipts. The protocol
constrains this (the manifest must not encode the answer; at least three materially
different layers must be representable; every hypothesis must be
observation-discriminable, and the shadow control shows the configured alternates), and
the transcription is per-field auditable against the cited receipts
(`post_r6o_diagnosis.py` docstring), but manifest authorship remains a channel through
which framing can influence the native decision. Measuring sensitivity to adversarial or
sloppy manifests is future work.

**Deferred scoring is not ground truth.** Coordinate 4 scores agreement with what the
frontier subsequently rewarded on this programme's own frozen gates; it is not an external
gold label.

**Scope of the harness guarantees.** Replay is replay of recorded receipts, not
re-execution determinism of hosts; local process tools are confined but not OS-sandboxed;
`GITHUB` is documentation-only surface with no implementation
(`E2E_HOST_DRIVE_VERIFICATION_2026-08-21.md`, "Ground truth established first").

## 8. Related work

Agent-benchmark literature predominantly measures **task success against ground truth**:
held-out answers, unit tests, environment goal states, or human preference labels. That
paradigm requires the truth to be known to the benchmark author. The quantity measured
here is different: **inter-instrument epistemic agreement on live frontier questions where
no ground truth exists yet**, with the frontier's own later, receipt-bound outcomes used
as deferred scoring for one coordinate. The nearest neighbors — self-consistency
resampling, LLM-as-judge, and multi-agent debate — compare an LLM with itself or with
another LLM; both sides share one substrate and correlated failure modes. Benchmark V0's
lanes differ in kind: one is an LLM-hosted replayable solve, the other a typed controller
with no LLM in the decision path, so agreement carries information that same-substrate
consensus does not. On the infrastructure side, the receipt contract is related to
provenance/workflow-reproducibility systems, but couples provenance to **control**:
deterministic request identity is what forces replay, immutability is what makes the
record trustworthy, and the authority booleans make the record non-self-authorizing. The
repository's own methodology paper (candidate Q2,
`papers/Q-paper-02-recursive-recovery/MANUSCRIPT_DRAFT_V1.md`) claims the
negative-recovery discipline; this paper claims only the instrument contract and the
agreement-benchmark class, per the anti-overlap boundary fixed in
`papers/Q-paper-02-recursive-recovery/PUBLICATION_PLAN.md`. A fresh hostile
novelty search dated at submission is a standing gate for this paper (same plan,
"Sequencing and shared obligations") and has not yet been run for Q3 specifically.

## 9. Reproducibility

Everything cited is committed on branch `claude/orion-harness-verification-b17qdj`:

- Instrument: `packages/orion-research-harness/` (code, `README.md`, `HOST_PROTOCOL.md`,
  tests; suite 98/0 after the section-3 repairs of
  `development/orion-q-max-r0/HARNESS_R6_DRIVE_VERIFICATION_2026-08-21.md`). Install:
  `python -m pip install -e 'packages/orion-research-harness[dev]'`.
- E2E drive receipts: `development/orion-research-harness/e2e-2026-08-21-receipts/`
  (26 requests, 25 results, 3 problems, runs, notes; every receipt self-validates against
  its digests).
- Campaign drive receipts: `development/orion-q-max-r0/harness-r6-drive-2026-08-21/`
  (4 cycles, hash-chained states and transitions, `CAMPAIGN_RUN_RECEIPT.json`).
- Benchmark: frozen protocol, both lane receipts, Lane A workspace archive, results file —
  all under `development/orion-q-max-r0/` as cited in sections 4–5. Lane B replays with
  `orion-harness campaign-run <workspace> orion-q:post-r6o-diagnosis --max-cycles 4`
  (the receipt's `provenance.run_command`); the manifest digest in any replay must equal
  `064ead57c2e1b1f02426dfea4f5a1184cb95440db52b77c1642964e135757ed4` or `decide_campaign`
  refuses to decide.
- Deferred-scoring receipts: `research/extensions/orion-q/MAX_R6P_*.json`,
  `MAX_R6Q_REGIME_PREDICATE_RESULTS.json`.

Because receipts are digest-bound and immutable, verification does not require re-running
any lane: a reviewer can recompute every digest, re-derive every request identity, and
re-execute the Lane B decision from the frozen manifest and transcribed observations.

## 10. Claim boundary

This paper claims: (i) the receipt-replay orchestration contract as implemented and
live-verified; (ii) the typed campaign-control layer with authority-false-by-construction
receipts, exercised on a real research chain that it honestly terminated in a frozen
negative; (iii) the controller–host agreement benchmark class, its frozen V0 protocol, and
its first measurement — verdict AGREE, coordinate 4 ALIGNED — as a benchmark definition
with one instance.

It does not claim: statistical reliability of either instrument; predictive validity of
agreement; scientific, novelty, promotion, or R6 authority for any receipt discussed
(every cited terminal and authority string is explicitly `NOT_R6` /
`NOT_SELF_AUTHORIZING`); security properties beyond the documented process-safety scope;
or a defect-free instrument — sections 6 (D2, D3) are open defects. The permitted claim
set is enumerated row-by-row in
`papers/Q-paper-03-dual-instrument/CLAIM_LEDGER.md`.

# Phase-2 closure gap inventory V1

Read-only audit of issue #76 against merged `main`. **This document closes no gate, checks no
checkbox, and grants no authority.** It records what exists, what has never been exercised, and
what is blocked on someone outside the code.

- Audited subject: `main@86ebc024d2b7f0cde69c6b0ba129d3283a8a3c67` (the #232 merge). `main` advanced
  to `c881cded` during the audit; every classification below is stated as of `86ebc024` and each
  cites its basis so it can be re-checked against a later head.
- Audit date: 2026-08-17
- Companion record: `research/phase2/PHASE1_TERMINAL_SUBJECT_ANCHOR_V1.json`
- Merged receipt-persistence PRs: #216, #219, #223, #229, #230 — **and #231**, which #76 omits and
  issue #159 lists.

## 1. The discriminating question

> Is the exact final Phase-1-derived subject already bound anywhere in the repository?

**No.** Two objects must be kept apart:

| | Object | State |
|---|---|---|
| (a) | **Phase-1 terminal anchor** — commit `7983401847ea2b33706aacbf6e45b6bc63a60d0d`, tree `fd86b448…`, PR #86, CI run `31946971360` (`ci`, conclusion `success`), declared in issue #75 comment `5307421385` | Real, verifiable, bindable — now bound by the companion JSON record |
| (b) | **Phase-2 closure subject** — the subject a closure run freezes via `freeze_phase2_binding()` | **Does not exist.** No closure run has occurred, so there is no subject to bind |

Issue #76's dependency line asks for evidence bound to "the exact final Phase-1-derived subject
used [in the] closure run". That subject is produced *by* the run, at run time. It could not be
authored here, and authoring a stand-in would be the `UNBOUND_EXECUTION_REPORT`-class mislabel that
got PR #207 quarantined (#212). What is bindable now is the anchor plus the derivation predicate:

> a future `RepositorySubjectAttestation.v1` `S` is Phase-1-derived **iff**
> `git merge-base --is-ancestor 7983401847ea2b33706aacbf6e45b6bc63a60d0d <S.commit_oid>` exits 0.

Ancestry is necessary, not sufficient — #76 also requires that every evidence family bind the *same*
`subject_revision_hash`. The predicate must be re-evaluated at audit time, not once.

**Scope of the absence claim.** Verified: the anchor commit, its tree, its CI run id, and the
Phase-1 terminal string appear in **zero tracked text files** at `main@86ebc024` (`grep -rI`, plus a
`find`-by-basename sweep over `*phase2*`/`*receipt*`/`*evidence*` — 57 files, all machinery or
tests, no data records). Not verified, and not claimed: that no such binding ever existed on any
branch or in any earlier commit. The clone was `--depth 50`, so full-history `git log -S` was not
run, and `grep -rI` skipped the `papers/paper-02-*/evidence/ci_mirror/*.zip` binaries. The claim
that matters for #76 is the merged-main one, and that is the one made.

## 2. Two discriminators applied throughout

**"P2" is overloaded.** `papers/paper-02-*` and `.github/workflows/p2-*.yml`
(autoresearchbench, live-provider-preflight, metasyn) are **Paper 2**, not **Phase 2**. Likewise
`P4`/`P5` in PR titles are papers. The genuine Phase-2 surfaces are
`src/orion/self_orion/phase2_*`, `tests/unit/self_orion/test_phase2_*`, `research/phase2/`,
`.github/workflows/phase2-empirical.yml` and `.github/workflows/p5_phase2_live_execution.yml`.
Counting `p2-live-provider-preflight.yml` as gate-A evidence would be a false positive.

**A passing test is not gate evidence.** Gates A–F ask for properties demonstrated *on the frozen
closure subject*. Merged tests proving the machinery behaves correctly are real, but with respect to
a gate they are `STRUCTURE_ONLY`. `BLOCKED_EXTERNAL` is reserved for items whose blocker is
provisioning, not code.

## 3. Gate inventory

Legend: **ME** merged evidence · **SO** structure only · **AB** absent · **BX** blocked external.

### Dependency issues named by roadmap #208

#76's real evidence dependencies are issues, not only its own gate text. States verified
2026-08-17 against the single-issue endpoint:

| Issue | State | Bearing on #76 |
|---|---|---|
| #8 | **open** | Gate A. The primary blocker |
| #59 | **closed** | Gate C's battery exists and its issue is closed. The open question is only whether its evidence binds the exact closure subject — it does not (see gate C) |
| #102 | **open** | P5 journal readiness; supplies the staged-acceptance and claim-contraction substrate gates D/E lean on |
| #159 | **open** | "Execute protected hidden-cause fresh-transfer campaign … and close #8/#76 dependencies". Maps onto gate B's fresh-transfer item and gate E. Its own terminal is conditional on #8 and #76 |

**#159 already records what #76 omits.** It carries "failed pre-outcome provider-entitlement
evidence preserved as `CANNOT_CHECK` rather than laundered into a negative result", and its open
line is "a valid, merged, result-bearing hidden-cause fresh-transfer campaign exists on the exact
final subject". #76's gate text has no equivalent row. #159 also lists **#231** among the merged
receipt-persistence PRs; #76 lists only #216/#219/#223/#229/#230.

**#8 is the only remaining *named issue* blocker — that is not the same as being close.** Gates
B, D, E and F are not independently blocked; they are blocked *through* A, because each requires
artifacts a closure run produces. Clearing #8 does not clear them, it unblocks them. And gate A is
not blocked solely on #8's external credential: run `32002591296` proved two code-side blockers
inside it (§6.1).

### Dependency (gate text)

| # | Item | Class | Basis |
|---|---|---|---|
| D0 | Final Phase-2 evidence bound to the exact final Phase-1-derived subject | **AB** | No closure-run subject exists; see §1. Anchor + predicate now in `research/phase2/PHASE1_TERMINAL_SUBJECT_ANCHOR_V1.json`, which is not itself the required binding |

### A. Frozen live-provider research trial (issue #8, **open**)

| # | Item | Class | Basis |
|---|---|---|---|
| A1 | Real LLM + real retrieval + protected verification boundary | **BX** | `.github/workflows/p5_phase2_live_execution.yml` (PR #185, #190) has run 4 times from `main`; **all 4 failed, at three distinct stages** — see §6.1. At the current head the blocker is external (no resolvable model), so `BX`; but a code-side blocker is also proven, and the discrimination between them is not settled — see the A4/A7 rows and §6.1 |
| A2 | ≥1 wide-literature and ≥1 deep-target task | **SO** | `src/orion/self_orion/live_packet.py` (`build_frozen_live_trial_packet`); workflow asserts `wide_task_count`/`deep_task_count` ≥ 1 |
| A3 | Task/provider/model/retrieval/evaluator/resource/split frozen before outcome access | **SO** | `src/orion/self_orion/phase2_freeze.py`, `subject_binding.py` (PR #91), `phase2_preflight.py` |
| A4 | Raw queries, documents, answer-use trace, mechanic episodes retained | **SO** | `src/orion/self_orion/live_trial.py`. **Defect demonstrated:** run `32002591296` executed the trial and reported `raw_search_trace_not_retained_for_every_task` as a blocker — the retention requirement is checked and currently not met. `SO` still holds literally (never exercised on *the closure subject*), but this row is a known code-side gap, not merely an unexercised one |
| A5 | Present-but-missed / retrieved-but-unused / interpretation / routing / saturation distinguished | **SO** | Taxonomy present in `src/orion/self_orion/live_packet.py` (`PRESENT_BUT_MISSED`, `RETRIEVED_BUT_UNUSED`, `SATURATION`, …) |
| A6 | Matched simple LLM+retrieval baseline under resource parity | **SO** | `src/orion/self_orion/baseline.py`, `live_campaign_factory.py`; workflow blockers `live_trial_resources_not_matched`, `matched_baseline_task_coverage_incomplete` |
| A7 | Null/harmful results preserved | **SO** | `src/orion/self_orion/live_trial.py`. **Defect demonstrated:** the same run reported `live_trial_failure_history_incomplete`, with both `comparison_statuses` `BLOCKED`. Same caveat as A4 |
| A8 | Exact live artifact merged and bound to the same subject as the rest of the evidence | **AB** | No live-trial artifact is merged. `papers/orion-15-self-orion/phase2/LIVE_EXECUTION_TRIGGER.txt` is a trigger, not a result |

### B. Shadow self-development trial

All eleven items are downstream of a consequential failure **observed in a real gate-A run**, which
has not happened. Machinery: `src/orion/self_orion/development_trial.py` (PR #109),
`live_shadow_development.py` (PR #94), `development_driver.py`, `change_control.py`.

| # | Item | Class | Basis |
|---|---|---|---|
| B1 | Detect the failure | **SO** | `development_trial.py`; requires a real A-run failure — synthetic does not count per the runbook |
| B2 | Preserve immutable episode/history | **SO** | `evolution_archive.py`, `development_trial.py` |
| B3 | Localize competing responsibility hypotheses | **SO** | `development_trial.py` (28 `hypothes`/`discriminator` sites) |
| B4 | Search current ORION/RAKL + external nearest work | **SO** | `research_loop.py`, `knowledge_runtime.py`, `rakl_transfer.py` |
| B5 | Freeze discriminator before repair outcome | **SO** | `development_trial.py` |
| B6 | Propose candidate change through worker/provider | **SO** | `live_shadow_development.py` |
| B7 | Execute in isolated candidate environment | **BX** | Needs `ORION_PROTECTED_SANDBOX_URL` / `_TOKEN` / `_ARTIFACT_HASH`; no protected sandbox is provisioned |
| B8 | Compare against incumbent under matched resources | **SO** | `baseline.py`, `development_trial.py` |
| B9 | Motivating replay + independent fresh transfer / protected assurance | **BX** | Needs `ORION_PROTECTED_DEVELOPMENT_EVALUATOR_URL` / `_TOKEN` |
| B10 | Retain failed/harmful alternatives + negative-history recurrence | **SO** | `development_trial.py`, `phase2_terminal_receipts.py` (PR #106) |
| B11 | Result can only recommend host promotion, never self-merge | **SO** | `change_control.py`, `development_trial.py` enforce it; there is no *result* to characterise. The absence of a self-merge primitive is a merged code property, not gate evidence |

### C. Hostile authority/evaluator trial (issue #59, **closed** — see §4)

All ten frozen attacks exist in `src/orion/self_orion/authority_trial.py` (`_ATTACKS`,
`AUTHORITY_ATTACK_IDS`, PR #152) in the same order as #76 lists them, each with a required
outcome (`REJECT` ×9, `CANNOT_CHECK` ×1). None has been executed against a Phase-2 closure subject.

| # | Item | Class | Basis |
|---|---|---|---|
| C1 | Wrong-source/correct-fact | **SO** | `authority_trial.py` attack 0 |
| C2 | Content substitution | **SO** | attack 1 |
| C3 | Source conflation | **SO** | attack 2 |
| C4 | Weak/self-authored checker | **SO** | attack 3 |
| C5 | Same-lane verifier | **SO** | attack 4 |
| C6 | Cited-but-unused evidence | **SO** | attack 5 |
| C7 | Benchmark/search contamination | **SO** | attack 6 |
| C8 | Evaluator/guard modification | **SO** | attack 7 |
| C9 | Held-out leakage | **SO** | attack 8 |
| C10 | Correct `CANNOT_CHECK` under insufficient evidence | **SO** | attack 9 |

The one live authority campaign that exists —
`papers/orion-14-verified-scientific-discovery/protocol/PROTECTED_RUN_BINDINGS_V2.json` (PR #144,
#165) — binds `subject_commit f6e51b5c8f905382b8e2f5568d9035fc14241aa1`, a **Paper-4** subject, and
carries `campaign_execution_authorized: false`, `outcome_accessed: false`. It is real merged
evidence for Paper 4 and is **not** admissible for #76's gate C, which requires the exact closure
subject.

### D. Empirical readiness receipts

| # | Item | Class | Basis |
|---|---|---|---|
| D1 | Content/lineage-bound `ReadinessEvidenceRecord`/external-manifest for the actual frozen subject | **AB** | Zero record instances in the tree; only the type in `src/orion/self_orion/readiness.py` and its tests |
| D2 | Self-verification rejected | **SO** | `readiness.py` (PR #68) — distinct producer/verifier lineage required |
| D3 | Post-hoc evaluator changes rejected/versioned | **SO** | `readiness.py` `evaluator_artifact_hash`; `evidence_admission.py` (#216, #219) |
| D4 | Mixed subject revisions rejected | **SO** | `readiness.py` `subject_revision_hash`; `phase2_campaign.py` cross-binding |
| D5 | Non-fresh splits rejected where freshness required | **SO** | `readiness.py` `fresh_split` |
| D6 | Caller declaration booleans cannot create PASS | **SO** | `evidence_admission_io.py` (#223), `evidence_audit_cli.py` (#229) |

### E. Failure-learning replay

| # | Item | Class | Basis |
|---|---|---|---|
| E1 | Repaired + replayed + fresh-transfer tested | **SO** | `phase2_terminal_receipts.py` `FailureReplayReceipt.v1` path `REPAIRED_REPLAYED_FRESH_TRANSFER` (PR #106) |
| E2 | Retained explicit unresolved/blocking fibre with discriminator/reopen condition | **SO** | same module, path `RETAINED_BLOCKING_FIBRE` |
| E3 | Same failure class does not recur unnoticed in the closure run | **SO** | `FrozenFailureIndex.v1` + campaign audit; no closure run to audit. `papers/orion-15-self-orion/protocol/P5_NEGATIVE_HISTORY_CHAIN_V1.json` (PR #230) self-declares `status: PROSPECTIVE_FROZEN`, `empirical_authority: "NONE"` |

### F. Final integration

| # | Item | Class | Basis |
|---|---|---|---|
| F1 | Papers/claim ledgers updated with local vs live/external evidence boundary | **SO** | All five `papers/paper-0*/README.md` carry a local-vs-external boundary, but none can record the Phase-2 live/external boundary because no live Phase-2 result exists. Crediting this now would credit a pre-run state |
| F2 | Phase-2 evidence binds the exact closure subject revision | **AB** | Same as D0 |
| F3 | Full CI green on the exact main merge | **SO** | `FinalCIEvidence.v1` exists in `phase2_terminal_receipts.py`; the `ci` workflow runs green on main routinely, but there is no closure merge to bind. Note: the only `phase2-empirical.yml` success (run 17, head `981db365`, branch `agent/phase2-empirical-execution`) took the **"Record blocked empirical execution"** branch and skipped "Protected custody is ready" — a green run that certifies the blockage, not the gate |
| F4 | External artifact manifest reproducibly derives PASS/FAIL/CANNOT_CHECK without declaration booleans | **SO** | `src/orion/benchmarks/external_evidence.py`, `evidence_audit_cli.py` (#229) |
| F5 | Issue #8 and all evidence dependencies closed, or explicitly retained as genuine external blockers | **AB** | #8 is open and no retention record exists in the tree. The underlying blocker is external (A1), but the *record* required by this item is absent |

## 4. Counts

| Class | Count |
|---|---|
| `MERGED_EVIDENCE` | **0** |
| `STRUCTURE_ONLY` | **36** |
| `ABSENT` | **5** |
| `BLOCKED_EXTERNAL` | **3** |
| Total sub-items | **44** |

Zero `MERGED_EVIDENCE` is not a claim that the machinery is missing — it is dense, tested and
merged. It follows from every #76 sub-item being conditional on a closure run that has not
happened. This is issue #76's own sentence, measured: *architecture readiness is not empirical
closure.*

## 5. What remains blocked, and on whom

**Operator / host — provisioning.** Nothing in code advances gates A or B until these exist. The
failed run `32003937947` is the proof that the code path is otherwise reached.

- Gate A: a usable reasoner+evaluator provider pair. The Copilot lane returned `MODEL_UNAVAILABLE`
  for all five candidates; the alternate lane needs `OPENAI_API_KEY`. Also
  `ORION_PROTECTED_VERIFIER_URL` / `_TOKEN` / `_ARTIFACT_HASH`, `ORION_PHASE2_EVALUATION_EPOCH_ID`.
- Gate B: `ORION_PROTECTED_SANDBOX_URL` / `_TOKEN` / `_ARTIFACT_HASH`,
  `ORION_PROTECTED_DEVELOPMENT_EVALUATOR_URL` / `_TOKEN`.
- Gate C: `ORION_AUTHORITY_ATTACK_EXECUTOR_URL` / `_TOKEN` / `_ARTIFACT_HASH`,
  `ORION_AUTHORITY_EVALUATOR_URL` / `_TOKEN`.

**External evaluator / reviewer.** Gate D's records require a verifier lineage distinct from the
producing lane; gate F's terminal audit is explicitly a host/external-reviewer act.

**Downstream, correctly blocked.** #209 (Phase 3) is blocked on #76; #210 (Phase 4) on #209 (#208).

**Partly blocked on code, contrary to first appearance.** No gate is waiting on a *missing module*,
but run `32002591296` proves two code-side blockers inside gate A (`raw_search_trace_not_retained…`,
`live_trial_failure_history_incomplete`), and the Copilot candidate model list is hardcoded. Those
belong to a development lane, not to the operator. See §6.1.

**Prior work adjacent to this record.** `research/development/mechanic-answer-loop/candidate-answers/ABSORB.EVIDENCE_BIND.v0.md`
(claude lane) already argues the content-identity contract used here: every load-bearing identity on
an authority path must be a lowercase SHA-256 content digest, and human display labels are
inadmissible *even when placed in fields named `*_hash`*. The anchor record follows it — where a
digest was not computed it records `null` plus a `NOT_COMPUTED` status and the reason, never a
label standing in for a hash.

## 6. Discrepancies against issue #76's own text

1. **#76 does not record that gate A has already been executed once, and returned `FAIL`.** Four
   `main` runs of `p5-phase2-live-execution` (2026-08-17, PRs #185/#190) failed, at three distinct
   stages — the attribution differs per run and must not be generalised:

   | Run | id | head | Failed at | Attribution |
   |---|---|---|---|---|
   | 1 | `32000698181` | `44427fcc` | step 5, "Check secret-safe live bindings" | Secrets absent. Predates #190's Copilot lane, so it cannot have failed at the model probe |
   | 2 | `32002199600` | `cfa79640` | step 8, "Freeze bindings and execute matched wide/deep trial" | Trial reached |
   | 3 | `32002591296` | `6c7d2afb` | step 8, same | **Trial actually executed** — see below |
   | 4 | `32003937947` | `e5d78490` | step 8, "Probe and freeze explicit Copilot model pair" | Probe `CANNOT_CHECK`, all five candidates `MODEL_UNAVAILABLE`, exit 3; trial step `skipped` |

   Run 3 is the substantive one, and its subject is legitimate: `6c7d2afb` **is an ancestor of
   `main`** (92 ahead, 0 behind) and therefore satisfies the Phase-1 derivation predicate. This was
   a real trial on a real main-line Phase-1-derived subject. It froze that subject and executed the
   matched wide/deep trial,
   emitting a `P5_PHASE2_SAFE_SUMMARY` with `issue_8_gate: "FAIL"`, exit 4:
   `subject_commit_oid 6c7d2afbae96057ffa821ff538ff913e962066c8`,
   `subject_revision_hash 8ec1d9c46b8515b3eed494ff765f94b0748f3e0e28bbd9fbb6e24dadad06a389`,
   `packet_fingerprint b9658d23…`, `provider_mode "github-copilot-cli-external"`,
   `wide_task_count 1`, `deep_task_count 1`, `protocol_id "phase2-shadow-closure-v1"`,
   `grants_self_promotion false`, `comparison_statuses ["BLOCKED","BLOCKED"]`, blockers
   `raw_search_trace_not_retained_for_every_task` and `live_trial_failure_history_incomplete`.

   Three consequences. **(i)** Gate A is not purely provisioning-blocked: run 3 stood the live
   boundary up and failed on trace/failure-history retention, which is code-side. **(ii)** The only
   real Phase-2 live-execution evidence that exists lives in **expiring GitHub Actions logs**,
   merged nowhere and bound to no retained artifact — the same unbound-execution shape that got
   #207 quarantined as `UNBOUND_EXECUTION_REPORT` (#212). If it is worth anything it should be
   mirrored before it expires; if it is worth nothing it should be said so explicitly. **(iii)** A
   `FAIL` here is legitimate Phase-2 material by #76's own text ("a failure that does not improve
   is still valid Phase-2 evidence if attribution, preservation and non-promotion are correct") —
   but only once bound to the closure subject, which `6c7d2afb` is not.

   Run 4's regression has a further code-side component: `COPILOT_REASONER_MODEL_CANDIDATES` and
   `COPILOT_EVALUATOR_MODEL_CANDIDATES` are **hardcoded tuples** at
   `src/orion/providers/live_phase2.py:29-41` under `explicit_models_only: true`. "All models
   unavailable" may therefore be a stale candidate list rather than an entitlement fact. Whether
   the blocker is the account or the list is not discriminated here; it is queued.
2. **Gate C cites issue #59, which is closed.** #59 is titled "P8 — Verified Scientific Discovery
   hostile authority/evaluator benchmark" and its live evidence binds the Paper-4 subject
   `f6e51b5c…`. Its closure does not satisfy #76's gate C, which demands the exact closure subject.
   Reading #59's closed state as gate-C progress would be a subject-identity error of exactly the
   class #76 warns about.
3. **`RepositorySubjectAttestation.v1` has no derivation field.** It binds `commit_oid`, `tree_oid`
   and per-blob content hashes of `HEAD`, but nothing asserts the subject is Phase-1-derived.
   #76's dependency line is therefore not mechanically checkable by the merged machinery — the
   companion JSON supplies the predicate; an executable checker is queued.

4. **Roadmap #208's blocker list is stale, and stale in a way that inflates the blocker count.**
   Two of its three named #76 blockers were already resolved. Verified 2026-08-17:

   | Claim in #208 | Verified state |
   |---|---|
   | #211 open, "current main still n=20" | PR #211 `merged=false` (head `fd7e0391`, **diverged** from main). But PR **#232** `merged=true` at `86ebc024`, which **is** an ancestor of main and carries `task_count: 390` ≥ TIER_B `required_n` 385. **TIER_B is met; #211 is not a blocker** |
   | #194 blocking, citing red CI run `32002655946` | PR #194 `merged=true` at `c4ba5515`, which **is** an ancestor of main (32 ahead, 0 behind). The cited red run's head `4b334043` (branch `claude/p2-gate`) is **diverged** from main — a superseded head |

   Two verification traps produced that staleness, and both apply to every row of this inventory:

   - **`merged` is `null` on the pull-request LIST endpoint** and carries its true value only on the
     single-PR endpoint. Use `gh api repos/SzeChunYiu/ORION/pulls/<N> -q .merged`. Reading the list
     would report #232 unmerged when it is merged.
   - **A cited red CI run may have run on a head that is not an ancestor of `main`.** Get the head
     with `gh api repos/SzeChunYiu/ORION/actions/runs/<id> -q .head_sha`, then
     `git merge-base --is-ancestor <head_sha> origin/main`. A red on a superseded head is not a
     blocker. The same check is what promotes run `32002591296` from "some CI log" to evidence on a
     Phase-1-derived main-line subject.

   Generalised: **before classifying anything blocked or absent, check whether another lane's PR
   superseded it.** A closed-unmerged PR in one lane does not mean the work never landed.

   Two further method notes for anyone re-running this audit. `rtk`-wrapped `git`/`grep` compresses
   output and has silently returned empty results elsewhere in the fleet; every count in this
   document that a classification rests on was re-checked with `/usr/bin/git grep -l … | wc -l`.
   And an absence claim needs a justified scope, not merely a search that returned nothing — §1
   states the scope of this document's absence claim and what it does not cover.

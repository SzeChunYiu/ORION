# ORION-Q harness verification and harness-driven R6 chain — 2026-08-21

Verifying/driving session: Claude Code (claude lane), branch `claude/orion-harness-verification-b17qdj`
Base under test: `shadow/orion-q-max-r0` @ `23c9ab12` (R6M freeze tip), merged into the claude branch for repair and execution.
Method: isolated `git archive` checkout + private venv first (per `AGENTS.md`), then fixes and the live drive on the claude branch.

## 1. What "the ORION-Q harness" is

There is no second harness package. `ORION_Q_RESEARCH_HARNESS_V1_ERRATUM_1.md` withdrew the separate
`research/extensions/orion-q/harness/` engine and converged on the shared
`packages/orion-research-harness` with a domain adapter at
`src/orion_research_harness/domains/orion_q/max_r6.py` plus the campaign layer
(`campaign_protocol.py`, `campaign_control.py`, `campaign_runner.py`).

## 2. Isolated verification results (pre-repair)

- Test suite at the shadow tip: **88 passed, 2 failed**, plus one collection error
  (`test_orion_q_numeric_regressions.py` imports numpy, which the package did not declare —
  violating the erratum's own "usable without quantum dependencies" gate).
  - `test_execution_coverage.py::test_external_governance_rejects_authority_escalation`:
    the strict governance scan installed by `governance_hardening.py` (a deliberate strengthening)
    changed the rejection message; the older test's regex went stale. Behavior correct, test stale.
  - `test_hardening.py::test_cli_returns_nonzero_for_host_and_local_capability_failures`:
    CLI `solve` now defaults to the recursive runner, whose first request identity differs from the
    legacy `run_problem` identity the test seeded, so the seeded failure receipt was never replayed
    (exit 2 instead of 3). Contract intact on the `--single-pass` path; the test asserted across flows.
- Campaign e2e (fresh workspace, numpy present): **works**. `orion-q:max-r6-live` runs
  N0 → `COMPUTE:DONOR_CLOSURE_PACKET` → N1 → `REV:CHANGE_INTERFACE` → N2 →
  `REV:GROW_METHOD_LANGUAGE` → `P10_RESULT`, protected stretched-N2 subject never opened,
  all authority booleans false — matching hostile gates 18–20 of the V1 protocol.
- Live defect found: a *transient environment* failure (system `python` without numpy) produced a
  failed receipt permanently bound to the deterministic request identity, after which every rerun
  replayed the failure — the campaign workspace was unrecoverable by design.

## 3. Repairs landed on this branch

1. Stale governance regex updated to accept the strict-scan message (behavior unchanged).
2. Exit-code test now pins **both** solve flows: legacy `--single-pass` replay of the seeded
   failure (exit 3) and the recursive default seeded through its own pending request (2 → then 3).
3. `numpy` declared as the `orion-q` optional extra; the numeric regression test now
   `importorskip`s, so the base package remains installable and green without quantum deps.
4. New recovery mechanism: `orion-harness retry-failed <workspace> [request_id]` +
   `ResearchWorkspace.archive_failed_result`. Only **failed** results can be archived (successful
   receipts stay immutable); the failed receipt moves bytes-unchanged to
   `results/archived/<request>.failed-<n>.json` and the identity becomes pending again.
   Regression tests in `tests/test_retry_failed.py`; the originally poisoned campaign workspace was
   healed live with this command and then completed its full chain.
5. Suite after repairs: **98 passed / 0 failed** (94 pre-existing+fixed, 4 new).

## 4. Harness-driven R6 chain (the honest current verdict)

The frozen prospective R6 gate (`max_r6_exact_tare3_prospective_replay.py`, blob-frozen by
`orion-q-max-r6-exact-tare3-prospective.yml` — all frozen blob identities verified intact on this
branch) was previously CI-only. The campaign manifest now registers it as
`orion_q.r6_prospective_replay`, exactly as the V1 protocol anticipated ("verification/replay steps
may be registered after their protocol is frozen"): `P10_RESULT` became a working phase whose hard
obligation `R6_PROSPECTIVE_GATE_EVALUATION` forces `COMPUTE:R6_PROSPECTIVE_REPLAY`, terminating in
`R6_VERDICT` (`R6_PROSPECTIVE_VERDICT_RECORDED__NOT_SELF_AUTHORIZING`).

Full four-cycle drive receipts are archived under `harness-r6-drive-2026-08-21/`. Final recorded
observations include:

```text
R6_EARNED = NO
R6_PROSPECTIVE_AUTHORITY = MAX_R6_NOT_EARNED__PROTECTED_SUBJECT_NOT_OPENED
R6_PROTECTED_SUBJECT_ACCESSED = NO
```

Decomposition of the negative, from the frozen receipts:

- pre-access gate `open_pre_prospective_ready = False` because the underlying exact TARE-3 joint DP
  returned `development_supported = false`: every gate passes except
  `joint_beats_frame_only_strong_on_at_least_one_subject = false` — the joint exact compiler does
  not strictly beat the frame-only donor on any open subject.
- Consequently the protected stretched-N2 subject was, correctly, never opened.

This is a **frozen scientific negative**, not an orchestration failure. Per
`MAX_R6M_EXACT_THREE_TARE2_SHARED_FACTOR_DP_PROTOCOL.md`, no gate may be lowered post-outcome.

## 5. What R6 still requires (open work, in lane order)

1. Implement the frozen-but-unimplemented donor/DP lanes: R6I (exact rank-2 shared-Tag DP),
   R6K (shared-Tag Restore-factor DP), R6L (three-TARE2 shared-factor donor, with Erratum 1),
   R6M (exact three-TARE2 shared-factor joint DP). Only protocol freezes exist at the tip;
   `research/extensions/orion-q/` has no `max_r6i/k/l/m` scripts yet.
2. A two-subject-strict R6M positive would make the coupled three-M2 compiler eligible for
   circuit-resource instantiation, donor/literature closure and novelty subtraction — each behind
   its own pre-outcome freeze.
3. Only then may a **new** stretched-N2 prospective protocol be frozen and executed
   (primary + structurally independent replay). R6 promotion stays a protected evaluator;
   no harness receipt can set it, by design.

## 6. Claim boundary

This record verifies orchestration and repairs infrastructure. It creates no scientific authority,
no novelty credit, and does not alter any frozen protocol or blob-pinned artifact.

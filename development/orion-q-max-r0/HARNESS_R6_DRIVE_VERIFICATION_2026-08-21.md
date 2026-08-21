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

## 5. R6I/R6K/R6L/R6M execution (added later on 2026-08-21)

All four frozen successor lanes were implemented exactly to their protocols and executed the
same day (receipts in `research/extensions/orion-q/MAX_R6{I,K,L,M}_*_RESULTS.json`; each script
re-run independently with a bit-identical receipt):

- **R6L** (`MAX_R6L_THREE_TARE2_SHARED_FACTOR_DONOR_POSITIVE__ABSORB__NOT_R6`): donor-lane
  positive, all 17 gates true. Establishes the Erratum-1 conservative donor floors (H4 = 12,
  N2 = 12) and post-absorption donor floors (H4 = 8, N2 = 9), rotation coordinate 9.
- **R6I** (`MAX_R6I_EXACT_RANK2_SHARED_TAG_DP_NEGATIVE__NOT_R6`): the exact rank-2 shared-Tag
  optimum ties the absorbed weight-one R6H donor envelope on all 10 partitions of both
  subjects (delta 0, strict 0/10). All hostile DP-vs-brute panels exact.
- **R6K** (`MAX_R6K_EXACT_RANK2_SHARED_TAG_RESTORE_FACTOR_DP_NEGATIVE__NOT_R6`): the joint
  rank-2 shared-Tag + factored-Restore optimum collapses onto the R6J donor values on every
  partition of both subjects (0 strict points). Per-configuration DP-vs-brute equality
  verified on 4 panels × 54 configurations.
- **R6M** (`MAX_R6M_EXACT_THREE_TARE2_SHARED_FACTOR_DP_NEGATIVE__NOT_R6`): the exact 9-bit
  joint DP over three arbitrary anticommuting M2 frames collapses onto the weight-one R6L
  donor on all 30 chemistry matchings (C_R6M = C_R6L exactly; H4 best 8, N2 best 9; strict
  0/15 on both subjects; rotation 9 never worse than incumbent).

Scientific reading: within the frozen open subjects, every registered residual coupled
representation optimization beyond the absorbed donors has **provably zero value** — the exact
DPs saturate onto the donor envelopes. The protected stretched-N2 subject was never opened by
any lane.

## 6. What R6 still requires after this saturation

R6M's development conjunction is negative, so per its own protocol the coupled three-M2
compiler is **not** eligible for circuit-resource instantiation or a new stretched-N2
prospective freeze. Reaching R6 now requires a materially different method-language or
representation move (a new frozen protocol beyond the R6B..R6M grammar family), not more
optimization inside it. R6 promotion stays a protected evaluator; no harness receipt can set
it, by design.

## 7. Claim boundary

This record verifies orchestration and repairs infrastructure. It creates no scientific authority,
no novelty credit, and does not alter any frozen protocol or blob-pinned artifact.

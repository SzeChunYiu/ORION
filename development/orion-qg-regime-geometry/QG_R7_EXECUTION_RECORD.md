# QG-3 / R7 execution record — first run of the positive-forecast instrument

Date: 2026-08-21
Programme: ORION #740 → child #745 (merged via PR #746)
Registry role: **residual R7** — the frozen hunt for a real trade-regime chemistry batch
Terminal: **`QG3_NO_POSITIVE_PREDICTION_IN_FROZEN_SCAN`**
Authority: `ORIONQG_R7_REAL_TRADE_HUNT_EXECUTED__TERMINAL_QG3_NO_POSITIVE_PREDICTION_IN_FROZEN_SCAN__NOVELTY_NOT_AUTHORIZED__NOT_R6`
Machine receipt: `research/extensions/orion-qg/QG_R7_REAL_TRADE_HUNT_RESULTS.json`

This lane carries the label "QG-3" from its own charter. In the wave-1 closure packet's
registry it is the **R7** instrument; wave-1's own QG-3 (boundary prospective) is a
different, already-completed experiment.

## 1. What was run, in what order

The step order is taken verbatim from `.github/workflows/orion-qg-qg3.yml`. Executed
locally rather than in CI; the workflow's two lineage assertions (checkout of the exact
protected head, merge-base against `QG3_FROZEN_BASE`) are CI-only guards and were not
re-implemented. The frozen base revision is still bound inside the stage-1 packet and
checked by both admission lanes.

1. `pytest -q packages/orion-research-harness/tests/test_qg3_positive_forecast.py`
   → 5 passed. (Native campaign control validated before any subject was touched.)
2. `python development/orion-qg-regime-geometry/run_qg3_dual_harness.py`
   → stage 1 executed as a content-bound `PYTHON` capability inside the generic harness,
   then Lane A (generic admission) and Lane B (native typed campaign).
   Wall clock 1952 s. Wrote `artifacts/orion-qg-qg3-stage1.json` and
   `artifacts/orion-qg-qg3-dual-admission.json`.
3. `python research/extensions/orion-qg/qg3_exact_referee.py --output artifacts/orion-qg-qg3-result-run1.json`
4. same again to `...-run2.json`
5. `cmp artifacts/orion-qg-qg3-result-run1.json artifacts/orion-qg-qg3-result-run2.json`
   → exit 0, byte-identical (both sha256 `abc75246a616…`).
6. The workflow's "Enforce honest terminal and positive gates" assertion block, run
   verbatim → `ALL_WORKFLOW_GATES_PASS`.

Stage-1 digest bound by every downstream artifact:
`0a62b73a94b3e40ef85c7cce560727f96419bfe07a806a4697ed533cc8a0f294`.

## 2. Stage-1 census

Frozen scan cap 12, R6R eligibility and `(n_qubits, path)` order, molecule exclusions
`{H2, H2O, H4, LiH, N2}` plus the R6R Benzene blob `5c02c72b…`. 30 eligible fresh
entries existed; the frozen cap took the first 12.

- **12 candidates scanned, 12 admitted, 0 skipped.** No candidate failed batch
  admission, so there are no skip reasons to report.
- All 12 are Benzene DUCC2/DUCC3 batches: 2 × 12 qubits, 4 × 14 qubits, 6 × 16 qubits.
- 15 canonical matchings per admitted candidate → **180 matchings evaluated
  structurally** (`C_R6L`, `C_Dplus`, `f_B`, R6Q features, predicted two-trade cost).
- **`positive_matching_found` is false for all 12.** Not one matching anywhere in the
  frozen scan had `predicted_C_DP < C_R6L`. `positive_found = false`, `selected = null`.

Custody gates in the sealed packet: `dp_call_count = 0`, `no_dp_calls = true`,
`protected_unread = true`, `predicate_binding_exact = true`, `freshness_pass = true`,
`admission_gates_pass = true`, `ground_truth_opened = false`, `novelty_authority = false`.

The protected stretched-N2 discriminator
(`N2/cc-pVTZ/6Elec_6Orbs/1.5_Eq-3.1020au/DUCC2/N2.cc-pvtz.ducc.results.txt`) never
became a candidate and was never read — the whole N2 molecule is excluded from
candidacy upstream.

## 3. Both admission lanes

| Lane | Decision | Detail |
| --- | --- | --- |
| A — generic ORION research harness | `NO_POSITIVE` | all 12 custody checks true; positive checks false because there is no positive to check |
| B — native ORION-Q typed campaign | `NO_POSITIVE` | terminal phase `NO_POSITIVE_RECORDED` |

`both_open = false`; the lanes agree; both are bound to the same stage-1 digest. This is
the honest concordant negative, not a disagreement.

## 4. Stage 2

The referee program ran twice and both runs produced byte-identical output. **Ground
truth never opened.** With `positive_found = false`, `_honest_terminal` returns
`QG3_NO_POSITIVE_PREDICTION_IN_FROZEN_SCAN` before the subject is re-admitted and
before `r6m.exact_r6m_matching` is reached, so no unrestricted DP executed in stage 2
either. `ground_truth_opened = false` in the result, as the workflow's own gate requires
for any non-refuted terminal.

Because no positive was selected, the "unseen subject" freshness question is never
raised, so no subject-level custody cross-check is load-bearing. The registries that
*would* have been checked (the six boundary-receipt blobs, the three R6R-era committed
blobs, the R6R Benzene blob, the protected path) are recorded in the receipt.

## 5. Interpretation against the wave-1 census

This is a **publishable prospective confirmation of the wave-1 census on fresh
subjects**, not an instrument failure.

`QG3_BOUNDARY_PROSPECTIVE_RESULTS.json` recorded `LIBRARY_SCAN_ALL_DONOR_EXACT`: all 90
real library matchings it refereed were donor-exact in both prediction and exact DP
truth, while positive split/borrow regimes appeared only in its engineered synthetic
track (seed 20260824, 4 split + 4 borrow at n = 3). The wave-1 reading was that trade
regimes need weight-2 structure that these DUCC batches do not produce.

This run extends that census in the direction that matters:

- Six of the twelve candidates (2 × 12 q, 4 × 14 q) are exactly the batches that already
  carry committed unrestricted-DP ground truth in the boundary receipt, all donor-exact.
  Stage 1 recomputed only their structural predictors — no DP — and reproduced the same
  donor-exact verdict on all 90 of their matchings.
- The other six (all 16 qubits: `10Elec_8Orbs`, `6Elec_8Orbs`, `8Elec_8Orbs` × DUCC2/DUCC3
  in Benzene cc-pVDZ) are **genuinely unread** — outside the boundary receipt, outside the
  R6R-era blob list, and beyond wave-1's scan cap of 6. All six admitted cleanly, and all
  **90 of their matchings are predicted donor-exact** as well.

So the donor-exact census now covers 180 real-library matchings across 12 batches at
12, 14 and 16 qubits, with the 16-qubit tier newly added and prospectively sealed under
DP-forbidden custody. The negative is informative precisely because the instrument was
built to find a positive and had every opportunity: every candidate admitted, nothing was
skipped, and the selector would have stopped at the first `(candidate, matching)` pair
with `predicted_C_DP < C_R6L`.

Per the frozen protocol, **the cap and order may not be changed after this outcome.**
Any continuation of the R7 hunt needs a newly frozen protocol — a larger cap, subjects
beyond Benzene, or batches built to carry weight-2 structure.

## 6. Plumbing fixes made during execution

Both are wall-clock/transport only. No scientific parameter, threshold, scan cap, gate,
candidate ordering, exclusion list or predicate was touched. Recorded verbatim in the
receipt's `execution_notes`.

**PLUMBING-1 — harness process ceiling.**
`local_tools.py` hard-clamped every SHELL/PYTHON capability to 120 s
(`timeout = min(max(int(payload.get("timeout", 60)), 1), 120)`), which killed stage 1.
A calibration probe measured one 16-qubit candidate at 213.1 s (168.0 s `try_admit` +
45.1 s `stage1_predict`), so the 12-candidate scan cannot fit. Added
`_MAX_PROCESS_TIMEOUT_SECONDS = 7_200` and used it in place of the literal `120`; gave
`run_qg3_dual_harness._run_local` a `timeout` parameter (default 120, unchanged) and
passed `timeout=7200` for the stage-1 call only. Lane A's admission call and both Lane B
capability timeouts are untouched. Raising the ceiling only *permits* longer timeouts —
every caller requesting ≤ 120 s is unaffected and the 60 s default is unchanged. All 139
harness tests still pass.

**PLUMBING-2 — transient egress failure.**
A `urllib.error.HTTPError: HTTP Error 502: Bad Gateway` from the session egress proxy
aborted a scan ~1490 s in. The proxy status endpoint recorded a matching upstream relay
failure at 2026-08-21T21:00:23Z, and a direct probe returned 502 and then succeeded
moments later. The frozen fetch path had no retry, and `r6r.try_admit` catches only
`(AssertionError, RuntimeError)`, so one transient error killed the whole scan. Added a
bounded retry helper `_read_source_bytes` in `max_r4d_h2o_ducc_confirmation.py`
(4 attempts, linear backoff) that retries **only** transient transport failures and
re-raises immediately on 401/403/407 and any 4xx, per the proxy's rule that policy
denials must be reported rather than retried. `fetch_source` now calls it. The git blob
SHA-1 equality check against the pinned blob id is unchanged, so a retry can change only
whether a fetch succeeds, never what its bytes are allowed to be.

Run attempts: (1) killed at the 120 s ceiling; (2) killed at a raised 1500 s ceiling
after 1501 s; (3) exited 1 on the transient 502 after ~1490 s; (4) completed in 1952 s —
this is the run the artifacts and the receipt bind.

## 7. Standing limits

`novelty_authority = false`, `physical_quantum_advantage_claim = false`,
`r6_authority = false`. The novelty-threat freeze
(`QG3_NOVELTY_THREAT_FREEZE_2026-08-21.md`) remains at
`NO_CLOSE_PARENT_FOUND_FOR_EXACT_COMPILATION_FAMILY_REGIME_GEOMETRY_AS_DEFINED__NOVELTY_NOT_AUTHORIZED`,
which is a search result, not a novelty certificate. Nothing here is a physical quantum
advantage, a new quantum algorithm, or a theorem across compilation families.

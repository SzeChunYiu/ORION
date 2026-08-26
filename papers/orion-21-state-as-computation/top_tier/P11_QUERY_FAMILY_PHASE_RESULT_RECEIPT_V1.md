# ORION-21 query-family placement/phase result receipt V1

**Run:** GitHub Actions `32663348906` (workflow `p11-query-family-phase-binding-v1`, conclusion: success)
**Artifact:** `p11-query-family-phase-binding-v1`, artifact ID `9499617317`
**Head SHA:** `ed5a2ac76bda9468cc801d52ffaa881ced7d7681` (branch `claude/gap-p11-query-phase-20260823`, pull request #996)
**Terminal (frozen rule, as executed):** `P11_QUERY_FAMILY_PHASE_V1_GATE_NOT_MET` (primary runner exit code 1 — the frozen rule asserts on the positive terminal; capture is verdict-agnostic and the run itself is green)
**Replay:** byte-identical rerun of the frozen runner (cmp green, exit codes identical)
**Independent verifier:** structurally independent NumPy implementation agrees on every support count, per-query verdict, mean (≤1e-12) and break-even horizon; its frozen gate also returns `SECOND_CHECKER_GATE_NOT_MET` (exit 1)

## Exact binding

- protocol SHA-256 (as recorded in both receipts): `16147dd984776994279623cde3847bbeb48ec198e8b491d5644c68dc40e1f995`
- frozen runner executed byte-for-byte from `papers/orion-21-state-as-computation/top_tier/run_query_family_phase_v1.py` (freeze: #978, commit `9fc55f68`)
- primary receipt SHA-256: `9a1f1f9b62955296bcff891f1f93f97af03448d311ae63b62a95d407e3de138f`
- independent receipt SHA-256: `b1e92a6be419a26d442fd0e0e6a8026279a70686e3f6b7b09ea64700b8742760`
- binding manifest SHA-256: `0c944d6215d0f8e993e31685c2fe20f5539558a05aa4d5b8a1caf876c7e36d06`
- environment: numpy 2.3.2, scikit-learn 1.7.1 (pinned in workflow)
- no frozen file modified by this PR; no threshold retuned; negative retained per programme rule

The committed raw JSONs in this directory (`p11_query_family_phase_primary_v1.json`, `p11_query_family_phase_independent_v1.json`, `p11_query_family_phase_binding_v1.json`) are byte-identical copies of the run artifact; the SHA-256s above apply to them.

## Per-query outcome table (ten pre-frozen responsibilities, five-fold mean balanced accuracy)

| query `q_j` (digit==j) | LINEAR uni | LINEAR comp | LINEAR Δ | LINEAR QS | RBF Δ | RBF QS | KNN Δ | KNN QS |
|---|---:|---:|---:|---|---:|---|---:|---|
| q0 | 0.9916 | 0.9888 | -0.0028 | Y | -0.0028 | Y | -0.0056 | Y |
| q1 | 0.9652 | 0.9198 | -0.0455 | N | -0.0368 | N | -0.0246 | N |
| q2 | 0.9968 | 0.9294 | -0.0675 | N | +0.0024 | Y | -0.0152 | Y |
| q3 | 0.9422 | 0.8945 | -0.0477 | N | -0.0448 | N | -0.0507 | N |
| q4 | 0.9855 | 0.9655 | -0.0200 | Y | +0.0103 | Y | -0.0015 | Y |
| q5 | 0.9767 | 0.9528 | -0.0239 | N | -0.0262 | N | -0.0256 | N |
| q6 | 0.9833 | 0.9651 | -0.0182 | Y | -0.0194 | Y | -0.0167 | Y |
| q7 | 0.9793 | 0.9585 | -0.0208 | N | -0.0102 | Y | -0.0102 | Y |
| q8 | 0.8576 | 0.7958 | -0.0617 | N | -0.0895 | N | -0.0815 | N |
| q9 | 0.9454 | 0.9157 | -0.0296 | N | -0.0367 | N | -0.0355 | N |

Quality-supported (QS) = `compiled_mean >= universal_mean - 0.02` (frozen). Support counts: **LINEAR 3/10, RBF 5/10, KNN 5/10**.

## Frozen-gate evaluation (preregistered decision rule, unchanged)

| gate component | requirement | observed | verdict |
|---|---|---|---|
| LINEAR support | >= 8/10 | 3/10 | FAIL |
| stronger-class support (max of RBF, KNN) | >= 8/10 | 5/10 (RBF), 5/10 (KNN) | FAIL |
| memory-crossover identity | 16U<=64 iff U<=4 on all U in 1..10 | holds on all 70 phase rows (both implementations) | PASS |
| future-query specialization cost | >0 for COMPILE_CACHE at U<10, 0 reconstruction for UNIVERSAL | holds | PASS |
| **composite positive terminal** | all of the above | — | **NOT MET** |

## Phase read (compile-vs-retain-raw boundary)

The negative is responsibility-limited, not resource-limited:

1. **Responsibility axis.** Only 3/10 digit responsibilities (q0, q4, q6) keep a 16/64-coordinate learned compilation within the frozen −0.02 quality tolerance under LINEAR access. The failures are graded, not binary: q7 (−0.0208) and q5 (−0.0239) miss by less than 0.004, while q8 (−0.0617) and q2 (−0.0675) lose 3× the tolerance. q4 sits exactly on the boundary (−0.0200, supported by the frozen inclusive `>=`). Responsibilities whose raw universal accuracy is already weakest (q8: 0.858, q3: 0.942, q9: 0.945) are precisely those that lose most under compilation — the 16 selected coordinates drop exactly the discriminative structure the harder responsibilities needed.
2. **Access-class axis.** Stronger decoders recover q2 and q7 (RBF and KNN reach 5/10, RBF even gains +0.0024 on q2) but cannot rescue q1, q3, q5, q8, q9 under any access class. The single-responsibility aggregate placement from the earlier learned-compiler result does **not** generalize to a ten-query family: compile-tolerance is a property of the (responsibility × access class) pair, and at most half the family qualifies even under the strongest attack.
3. **Resource axis (frozen identities all hold).** Memory crossover is exactly U≤4 (16·4=64); LINEAR break-even horizon grows linearly in U (1917 at U=1 → 19169 at U=10, = 1437.6·64/48·U + 1 rounded down/up per frozen formula); future-query arrival costs COMPILE_CACHE one fresh fit (92006.4 inspections) while UNIVERSAL reconstructs nothing. On the frozen H grid, compiled total touches first fall below universal at H=2500 (U=1..2), H=10000 (U=3..5) and only H=25000 (U=6..10) — compiling wins on touches only at long horizons and wins on memory only at U≤4; the joint win region (U≤4 AND H≥break-even(U)) is non-empty but narrow.

**Boundary statement:** on non-synthetic digits, a query-specific 16/64 learned compilation is quality-supported only for an easy minority of responsibilities (3/10 LINEAR; 5/10 under stronger access) — below the preregistered 8/10 family bar — while every frozen resource identity holds; therefore the compile-vs-retain-raw boundary is set by responsibility-level query diversity, not by resource accounting. Retain the raw 64-float state unless the responsibility family is small (U≤4) AND each member is individually compile-tolerant.

Selection stability (folds): per query, 1–5 distinct 16-coordinate selections out of 5 folds with 13–16-coordinate intersections (q0 identical across all folds; q3 different in every fold). Unstable selection does not align with failure (q8: 3/5 distinct) — failure tracks universal difficulty, not selector noise.

## Phase-diagram numbers (frozen U/H grids)

- state-memory crossover: COMPILE_CACHE stores <= UNIVERSAL exactly for `U <= 4` (16·4 = 64 floats); for `U >= 5` compiled materialization exceeds the shared 64-float universal state. Confirmed exactly on the frozen grid.
- LINEAR break-even horizons (service-touch savings vs compiler-fit charge, mean n_train = 1437.6): U=1:1917, U=2:3834, U=3:5751, U=4:7668, U=5:9585, U=6:11501, U=7:13418, U=8:15335, U=9:17252, U=10:19169 (break-even grows linearly in U; every break-even lies within the frozen H grid's top end — touch-win cells exist for all U, but only at H=25000 once U>=6).
- future-query arrival at midpoint: COMPILE_CACHE pays one fresh compiler fit (1437.6·64 = 92006.4 inspections) + materialization; UNIVERSAL pays zero state reconstruction.

## Scientific disposition

`GATE_NOT_MET` — negative retained, no retuning, thresholds as frozen in #978. The earlier single-responsibility learned-compiler placement claim does not extend to a ten-responsibility family on digits; the phase diagram (memory crossover, linear break-even growth, nonzero future-query tax) is confirmed exactly, so the placement question on this domain resolves on the quality axis against compilation at family scale. This is a boundary characterization of the ORION-21 compile/cache/materialize option on digits, not a refutation of the resource identities themselves.

## Reconciliation with prior failed run 32661332644 (added 2026-08-23, post-binding)

An earlier execution harness, `.github/workflows/p11-query-family-phase-v1.yml` (frozen with the protocol/runner/checker in #978), already executed this study on PR #994's head `aedcaf93` at 2026-08-23T19:31:51Z: run `32661332644`, conclusion FAILURE.

- **Classification: the failure IS the preregistered negative, not a harness defect.** The run installed the identical pinned environment (numpy 2.3.2, scikit-learn 1.7.1), executed the identical frozen runner blob (`7b5d13fe1abb8a9351cf0481c26b079b8f877098` at both `aedcaf93` and this receipt's executed head `ed5a2ac7`), ran the full study, and failed only at the runner's own terminal assert `assert positive` (line 78) — exactly the `GATE_NOT_MET` outcome bound above. The benign `f_classif` constant-feature warnings in its log match this run's.
- **Why that run is not the bound receipt:** its failure occurred before the upload-artifact step (no artifacts exist), and the assert's message — which carried the full receipt repr — was line-truncated out of the GitHub log, so no per-query table is recoverable from it.
- **Record:** run `32661332644` is the first observation of the negative; runs `32663348906` (bound) and `32664737225` (final-head re-verification) are the authoritative verdict-agnostic captures of the same frozen execution.
- **Hygiene note for the fold-in pass:** the older workflow red-Xes by design on this negative (its replay step asserts the positive terminal). Retiring or annotating it is a post-#993 ledger decision, not a study change; this PR leaves it untouched.

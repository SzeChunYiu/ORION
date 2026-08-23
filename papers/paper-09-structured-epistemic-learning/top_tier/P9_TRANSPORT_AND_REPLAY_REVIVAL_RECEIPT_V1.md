# P9 transport + replay revival receipt V1 (NR-04 / NR-06)

**Programme:** #977 · **Backlog:** `research/paper-programme-v1/NEGATIVE_REVIVAL_BACKLOG_V1.md` lanes NR-04, NR-06
**Discipline:** RAKL revival — attribute to ONE stage, apply the matching lever, re-test. All work local
single-script (no pytest/suite/xdist). No frozen cell, gold, target, cost, receipt, or terminal was edited.

## NR-04 — D-A cell `CANNOT_CHECK`: quality-transport below the 0.965 target

### One-stage attribution (measured, `evidence/P9_NR04_TRANSPORT_STAGE1_ATTRIBUTION.json`)

| Candidate stage | Measurement | Verdict |
|---|---|---|
| representation-repair channel | `cbrt(x^3) == x` bitwise: max abs/rel reconstruction error `0.0`; identical fitted coefficients; probe/protected accuracies identical to the native standardized representation (`0.9721448` / `0.9555556`) | **lossless — not the stage** |
| evaluation channel | single-split binomial sd `0.0098` vs decision margin `|0.96384 − 0.965| = 0.0012` → **noise-to-margin 8.47**; re-draw distribution mean `0.9644`, sd `0.0095`, `50.5%` of draws ≥ target | **lossy by construction — the stage** |

The V1 protocol transports a single-split point accuracy across a threshold the fixed dataset
cannot resolve: the D-A prediction/gold mismatch is channel noise (a Bernoulli ≈ 0.5 realization),
not a property of any intervention arm. This confirms and localizes the V2 ledger receipt's "no
accounting rule can move it": the immovable object is the measurement channel, not the accounting
and not the repair.

### Lever (pre-registered before re-run)

`P9_CAUSAL_DIAGNOSTIC_TRANSPORT_PROTOCOL_V2.md` (SHA-256 `a6742ad73a79a4a67d7cf0faaf423f311244a996f3e8dd73da7a2197f5d19f1a`):
transport the **quality level** — mean accuracy over `R = 24` pre-registered stratified partition
re-draws (seeds `20261101+k` / `20261201+k`), full per-arm pipeline re-executed per draw; identical
cells, targets, costs, access classes; decision rule unchanged in form. One global constant, no
cell-specific tuning; registered after stage-1 attribution but before any V2 outcome.

### Re-test (`run_causal_diagnostic_transport_v2.py` → `evidence/P9_CAUSAL_DIAGNOSTIC_TRANSPORT_V2_RUN.json`)

| Endpoint | V1 (before) | V2 (after) |
|---|---|---|
| diagnostic accuracy | `4/5` | **`5/5`** |
| D-A prediction vs protected gold | `ACCESSIBILITY` vs `CANNOT_CHECK` (mismatch) | **`CANNOT_CHECK` = `CANNOT_CHECK`** |
| probe/protected decision agreement | 4/5 cells | **5/5 cells** |
| false compute escalation (diagnostic vs generic) | 0 vs 4 | 0 vs 4 |
| mean registered-cost regret | 0.0 | 0.0 |
| D-A transported levels (probe/protected) | point `0.9721`/`0.9556` | level `0.96356`/`0.96435` (both < `0.965`) |

Terminal: `P9_CAUSAL_DIAGNOSTIC_TRANSPORT_V2_GATE_NOT_MET` — the V1-mirroring conditions all pass,
but the pre-registered **half-draw decision-stability** clause fails on D-A (protected half-1 level
`0.9662 ≥ 0.965` while half-0 reads `0.9625`). The gate is not weakened post-outcome.

### Why D-A stays `CANNOT_CHECK` (mechanistic reason)

The repaired arm's true held-out level is `693/719 = 0.96384` (pooled), `0.9644` (re-draw mean) —
below the frozen `0.965` target by ≈ `0.0006`, i.e. **0.17σ of the best possible estimator on 719
held-out samples** (pooled binomial se `0.0069`). The level-target ordering is unresolvable at this
dataset size by ANY transport channel; V2 makes the verdict stable at the registered depth and
makes the unresolvability itself measurable. The cell is genuine, not an artifact to retune away.

### Remaining negative / boundary

- D-A cell terminal remains `CANNOT_CHECK` (now with quantified margin-unresolvability); the full
  V2 positive terminal is withheld by its own stability clause.
- No claim of a universal LLM diagnostic; the protected Qwen scaling negative
  (`LLM_STRUCTURE_SCALING_FRONTIER_NOT_SUPPORTED`) was not repaired, re-run, or touched.

## NR-06 — D1v1.2 locked-env replay: archived 0.50 vs locked reproduction 0.75

### One-stage attribution (`revive_p9_nr06_replay_consistency.py` → `evidence/P9_D1V1_2_ARCHIVE_NUMERICAL_REPLAY_CONSISTENCY_2026-08-23.json`)

| Channel | Test | Result |
|---|---|---|
| data serialization (ordering/dedup/type tags) | regenerate frozen dataset; compare manifest digest to archive | **identical** (`sha256:2775…c19c`) — no data delta exists |
| numerical solver | re-run selection+fit+protected prediction under the archive-matching stack (python 3.13.12 / numpy 2.4.4 / sklearn 1.8.0 / scipy 1.17.1) | **exact per-case reproduction of all four arms** (TSB: config `logistic-C1`, accuracy `0.5`, one distinct prediction, 128/128 predictions equal to archive) |

The failing "locked" replay ran `uv.lock`'s stack (python 3.12.13 / numpy 2.5.2 / **sklearn 1.9.0**
/ scipy 1.18.0) — **newer than the archive's numerical environment, which the archived result JSON
never recorded**. On the degenerate TYPED_SERIALIZED_BAG design (one effective feature after
domain-disjoint tokens vanish), an lbfgs micro-delta flips the 32/128 knife-edge cases whose
runner-up is the truth — the recorded 0.50→0.75 gap.

### Classification and lever

**Infrastructure defect (fixable): the replay lock was never bound to the archive's numerical
environment.** Lever: pin the replay channel to the archive-matching stack. Demonstrated: byte-level
agreement — dataset digest equal, all selected configs equal, all four arms' protected prediction
vectors equal, TSB accuracy `0.5` with the constant predictor restored.

### Boundary (not upgraded by the fix)

- `P9_D1V1_2_LOCKED_ENV_REPRODUCTION_FAILED` stays append-only; nothing is relabelled PASS.
- The reproduced `0.5` is still the modal-class prior on an unresponsive comparator
  (`P9_D1V1_2_DIVERGENCE_ROOT_CAUSE_2026-08-23.json`): the fix restores replay **consistency**, not
  the **validity** of that number as a representation measurement.
- The scientific repair (order/multiplicity-preserving serialization) stays with the frozen
  successor `P9.D1V1_3.ORDERED_MULTIPLICITY_ROBUSTNESS` (`PROSPECTIVE_FROZEN_NOT_EXECUTED`;
  protected inputs still absent).

## Artifacts

| File | Role |
|---|---|
| `top_tier/revive_p9_nr04_stage1_attribution.py` + `evidence/P9_NR04_TRANSPORT_STAGE1_ATTRIBUTION.json` | stage-1 attribution measurements |
| `top_tier/P9_CAUSAL_DIAGNOSTIC_TRANSPORT_PROTOCOL_V2.md` | pre-registered V2 transport protocol |
| `top_tier/run_causal_diagnostic_transport_v2.py` + `evidence/P9_CAUSAL_DIAGNOSTIC_TRANSPORT_V2_RUN.json` | V2 re-test (receipt SHA-256 `662b772a3b6a929b8afe5112bfff28c10b0d4709e018abf4755391bbd6495ab2`) |
| `top_tier/revive_p9_nr06_replay_consistency.py` + `evidence/P9_D1V1_2_ARCHIVE_NUMERICAL_REPLAY_CONSISTENCY_2026-08-23.json` | NR-06 replay-consistency check |
| `evidence/P9_TRANSPORT_AND_REPLAY_REVIVAL_RECEIPT_V1.json` | machine-readable receipt |

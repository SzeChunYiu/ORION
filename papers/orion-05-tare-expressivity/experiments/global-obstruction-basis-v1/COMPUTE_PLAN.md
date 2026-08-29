# ORION05.GLOBAL_OBSTRUCTION_BASIS.v1 — compute plan (DESIGN; LUNARC execution only)

HARD CONSTRAINT: no census or control solve runs on the Mac. Local use is
limited to `--smoke` (0 solver instances). The paper's own solver is the only
optimizer; single-threaded pure-Python stdlib.

## Workload

| Item | Count | Per-item cost assumption |
|---|---|---|
| Census instances (C(15,6), n=2) | 5,005 | 1 × `solve_six_targets(max_support=2)` — **>100 s observed locally, unknown tail**; plus 1 × `max_support=1` solve (≪1 s; 12³ triples) and classification (ms) |
| CONTROL_GATE solver controls | 3 | same shape as census instances |
| Predicate controls / smoke | — | negligible; runs anywhere |

Structure per max_support=2 solve at n=2: B(2)=120 ordered pairs → 120³ =
1.728M triples × 2 orientations (accelerated by the solver's `n<=2`
small-tag bitmask path) × 4 relative permutations × 15 matchings.
Deterministic; memory footprint small (well under 1 GiB).

## Timeout policy (unknown tail is assumed, not hoped away)

- Primary pass: per-instance SIGALRM timeout **1800 s** → per-instance
  terminal `TIMEOUT` (row preserved, never rewritten).
- Requeue pass: all `TIMEOUT` rows re-run once with **21,600 s** (6 h).
- Still `TIMEOUT` after requeue → campaign terminal
  `CANNOT_CHECK_INCOMPLETE_CENSUS` (a partial census never grades T1/T4).

## Core-hour estimate

- Expected: 5,005 × (100–400 s) ≈ **140–560 core-hours**.
- Hard ceiling (every instance hitting the 1800 s primary timeout):
  5,005 × 1800 s ≈ **2,500 core-hours**; requeue pass worst-case adds
  `n_timeout × 6 h` (budget approval threshold: abort and reassess if
  primary-pass timeout fraction exceeds 10%).
- Recommendation: request ~600 core-h initially; extend on evidence.

## SLURM sketch (conventions copied from `rounds/r13-parent-certificate-ordering/run_orion05_r13_lunarc.sbatch`)

Order of operations (each step gates the next):

1. `--smoke` on the login-adjacent node (seconds): import, sha256 binding,
   enumeration counts, predicate controls.
2. `CONTROL_GATE` job (1 task, 3 instances, ≤3 h): the three R6O planted
   positives + corrupted-basis firing. Any failure → stop
   (`CANNOT_CHECK_CONTROL_FAILURE`).
3. Census array. With `--array-chunk 15`: 334 tasks × 15 instances; worst
   case per task 15 × 1800 s = 7.5 h → walltime 08:00:00.

```bash
#!/bin/bash
#SBATCH --job-name=o05-gob-v1
#SBATCH --account=<ACCOUNT>            # e.g. lu2026-2-51 as in R13
#SBATCH --partition=<PARTITION>        # e.g. lu48
#SBATCH --qos=normal
#SBATCH --nodes=1 --ntasks=1 --cpus-per-task=1
#SBATCH --mem=4G
#SBATCH --time=08:00:00
#SBATCH --array=0-333%100
#SBATCH --output=<LOGDIR>/%x-%A_%a.out
#SBATCH --error=<LOGDIR>/%x-%A_%a.err
set -euo pipefail
cd <FROZEN_CHECKOUT>                    # dedicated clean checkout at base_commit
export PYTHONHASHSEED=0 OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 \
       MKL_NUM_THREADS=1 NUMEXPR_NUM_THREADS=1
PYTHON=<VENV>/bin/python               # python >= 3.11; stdlib-only workload
$PYTHON <RUNNER> --repo-root . \
  --out-dir <RESULT_DIR> \
  --array-chunk 15 --timeout-s 1800
```

Requeue pass: same script with `--timeout-s 21600`, `--time=12:00:00`,
array restricted to the failed indices (resume logic skips valid files, so
re-submitting the full range is also safe, just wasteful).

4. Aggregation job (1 task, minutes): collate `instances/inst_*.json`,
   assert 5,005 valid rows, compute gap census, shape census
   (pinned/unpinned split), orbit-consistency check under the n=2 symmetry
   group, decide the campaign terminal per the frozen decision-rule order,
   emit `RESULT.json` + `SHA256SUMS` (raw rows never rewritten).

## Resumability / determinism

- One JSON file per instance (`instances/inst_%04d.json`, atomic
  tmp+rename); valid files are never recomputed → arrays can be killed and
  resubmitted freely.
- No RNG anywhere; identical inputs → identical bytes for all
  non-timing fields. Timing fields are excluded from result digests.
- Receipt rule (R12 discipline): raw per-instance JSON + deterministic
  aggregate + SHA256SUMS; adverse and timeout rows preserved verbatim.

## Explicitly out of scope for this compute plan

- The compiler/search-consequence lane of #1649 (separate successor
  protocol; must be frozen after this campaign's terminal, with
  information-matched baselines and all information costs charged per the
  R13 cost-accounting discipline).
- Any n≥3 extension (e.g. re-running the QG-7 fourth-regime witnesses
  through this pipeline): per-instance cost grows like B(n)^3 ≈ n^9
  (n=3 is ≈170× the n=2 triple count); not budgeted here — would need its
  own frozen amendment and timing pilot.

# P1 Live-Provider Campaign Integrity Note

Campaign completed 2026-08-17T08:55:59Z (PID 89706, worktree `/Users/billy/Desktop/projects/ORION-wt/p1-live`)

## Archive Contents

| File | Size | Records |
|------|------|---------|
| raw/test_runs.jsonl | 2.5MB | 2880 |
| raw/test_scored.jsonl | 3.9MB | 2880 |
| P1-T2_baseline_ablation_results.json | 925KB | - |
| P1-T2_baseline_ablation_results.md | 23KB | - |
| P1-T3_failure_taxonomy.json | 18KB | - |
| P1-T3_failure_taxonomy.md | 5KB | - |
| campaign.stale-run.log | 304B | - |

## Arithmetic

2880 records = 12 systems × 48 cases × 5 stochastic repeats

Systems: 5 baselines + 5 ablations + 1 ORION + 1 live provider
Split: TEST (48 cases)

## Score vs CANNOT_CHECK Breakdown

| Status | Records | Percent |
|--------|---------|---------|
| SCORED | 2794 | 97.0% |
| CANNOT_CHECK | 86 | 2.9% |

**CANNOT_CHECK Root Causes:**
- `PROVIDER_ERROR: AuthenticationError`: 78 records
- `PROVIDER_ERROR: RateLimitError`: 4 records
- `PROVIDER_ERROR: InternalServerError`: 4 records

All CANNOT_CHECK records belong to `orion_live_provider` only.

## Cascade Timeline

1. Campaign started: 2026-08-17T08:23:10Z
2. Raw records written: 2026-08-17T10:55:57
3. Tables generated: 2026-08-17T10:55:58
4. Campaign log closed: 2026-08-17T08:55:59Z

The provider credential failed partway through execution (record ~163), causing 78 consecutive `AuthenticationError`s. The campaign never recovered — all subsequent live-provider attempts hit CANNOT_CHECK.

## Frozen Reduction

The P1-T2 table reduces stochastic repeats per-case before computing intervals:
- 25/48 cases have at least one SCORED repeat (frozen reduction produces a rate)
- 23/48 cases are fully CANNOT_CHECK (no repeats scored)
- Offline systems: 0 CANNOT_CHECK records

## Table Status

| Table | Status | Reason |
|-------|--------|--------|
| P1-T2_baseline_ablation_results | **PARTIAL** | 23 cases CANNOT_CHECK (provider API failures) |
| P1-T3_failure_taxonomy | **OK** | Failure taxonomy complete across scored trials |

## Determinism

Archived tables are reproducible at HEAD. The only difference between archived and regenerated tables is the `provenance.generated_utc` timestamp written by `tables.py:_provenance()`. After nullifying this field, regenerated tables are bit-identical to archived.

**Generating commit:** `0cf4e8d82771252de94be8c696a3f39fd3191019` ("Merge pull request #222", 2026-08-17 10:14:55 +0200)

**Regeneration recipe:**
```bash
cd /path/to/ORION
git checkout 0cf4e8d82771252de94be8c696a3f39fd3191019
export PYTHONPATH=$(pwd)/src
python3 -m orion.study.p1.tables \
  --archive papers/paper-01-recursive-epistemic-reconstruction/results/raw/test_scored.jsonl \
  --out papers/paper-01-recursive-epistemic-reconstruction/results
```

Note: Point `--archive` at `test_scored.jsonl` directly, not the `raw/` directory, because `load_records()` loads all `.json/.jsonl` files in a directory and `test_runs.jsonl` lacks the `schema_version` field required by the reader.

## Digests

- test_runs.jsonl: `7fd6dae6df56b6e43240bac025208ee5`
- test_scored.jsonl: `8ebcb759e4ee7564c3c9bef0d5a98bdb`
- P1-T2_baseline_ablation_results.json: `50f36a9d6cfac3f753bc54b4b3aac745`
- P1-T3_failure_taxonomy.json: `5a8e2f45718b043e35de27a188872eeb`

## Provenance

- Suite fingerprint: `21b461d89280631b93b766d6fb000c7f9f5fbeccee7cb6664f238c2c5c8e6420`
- Subject revision: `0cf4e8d82771252de94be8c696a3f39fd3191019`
- Provider: `https://api2.cmkey.cn` (GLM-5.2)
- Execution mode: `EXECUTION_FROZEN`

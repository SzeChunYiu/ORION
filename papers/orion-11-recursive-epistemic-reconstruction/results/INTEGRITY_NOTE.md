# ORION-11 campaign integrity and recovery note

This note separates the failed first live-provider attempt from the current
authoritative archive. The first incident is immutable negative execution
history; it is not the status of the recovered result set.

## Current authoritative snapshot

The current archive contains the complete frozen design:

| Item | Current value |
|---|---:|
| systems | 12 |
| TEST cases | 48 |
| stochastic repeats | 5 |
| expected records | 2,880 |
| run records with status `OK` | 2,880 |
| score records with status `SCORED` | 2,880 |
| run-level or score-level `CANNOT_CHECK` | 0 |
| ORION-11-T2 table status | `OK` |
| ORION-11-T3 table status | `OK` |

Arithmetic: `12 systems x 48 cases x 5 repeats = 2,880 records`.

The live-provider recovery landed in `c881cded`; regenerated complete tables
landed in `61fd591f`. The current raw archive is the authority for missing-data
counts. Every ORION-11-T2 row records `cannot_check_cases: 0`.

### Current SHA-256 bindings

| Artifact | SHA-256 |
|---|---|
| `raw/test_runs.jsonl` | `83cc652ce8a6dbeab6cb664af42ca36dee2704ef58ee7e6ea32cd060ea9fc17e` |
| `raw/test_scored.jsonl` | `f37db6247dd1f5883e443b6d7b454e099759cb26baa3e09f74e7fd275e4d7f7b` |
| `P1-T2_baseline_ablation_results.json` | `4f1fb7f6c551f9ce8e24fb00dfc56b5254c39cf796c858be7a1581b1d92b886b` |
| `P1-T2_baseline_ablation_results.md` | `83eddd8da074a0ba0491981da33ca78e58069a85530cb61d53d376dacf96be58` |
| `P1-T3_failure_taxonomy.json` | `bfb6fe00b0e12d3777e3761489e265d0a2d19547c56e89099f445a938c5842ae` |
| `P1-T3_failure_taxonomy.md` | `df6c07150f68ab89bf0c4ccca8d909244356c135d409745c3db82a584ec062a7` |

The ORION-11-T2 digest includes the status-ontology correction documented by
`P1-T2_STATUS_ONTOLOGY_CORRECTION_V1.json`. The raw records, primary rates,
intervals, effects, and registered ORION-11 hypothesis verdicts are unchanged.

## Historical provider-failure incident

Commit `85d32db0` preserved the first failed attempt. It contained 2,794 scored
records and 86 `CANNOT_CHECK` records, all in `orion_live_provider`:

| Cause | Records |
|---|---:|
| `PROVIDER_ERROR: AuthenticationError` | 78 |
| `PROVIDER_ERROR: RateLimitError` | 4 |
| `PROVIDER_ERROR: InternalServerError` | 4 |

At that historical ref, 23 of 48 live-provider cases had no scored repeat and
ORION-11-T2 was correctly `PARTIAL`. Those facts describe the failed attempt only.
They must not be copied into a report about the recovered archive.

### Historical SHA-256 bindings at `85d32db0`

| Artifact | SHA-256 |
|---|---|
| `raw/test_scored.jsonl` | `4bd84af34fcce458aba3c020c2505f7d9027f77752a2cb3f09143e9e2f1e7334` |
| `P1-T2_baseline_ablation_results.json` | `eca27e929eceb804476d07ae37e3e92dfffd8ced06f2958e20968612d8047a9b` |
| `P1-T2_baseline_ablation_results.md` | `d8134bcac836c935c94db199820232d2c46c1c0dcd10b44f2396e3690411b4c6` |
| `P1-T3_failure_taxonomy.json` | `71c406c6ac1b2c023e8c463e71a4c8fc39773ae0dcf9c4742f7618be8588634c` |
| `P1-T3_failure_taxonomy.md` | `13976526790a57726f2e980498225bcdb973fc4322730e97c29a257d15b5627c` |

## Status semantics

- `CANNOT_CHECK` means the metric is applicable but required evidence or an
  observable denominator is missing. It is never rendered as zero.
- `NOT_APPLICABLE` means the frozen case scope excludes the metric family. It
  is not evidence for or against a claim.
- `DESCRIPTIVE_ONLY` means an effect and uncertainty were reported for a
  comparator row with no registered hypothesis. It is not a hypothesis verdict.
- `NOT_SUPPORTED` remains the historical registered H1 outcome. The recovered
  provider records and the status-ontology correction do not reverse it.

## Deterministic regeneration

```bash
export PYTHONPATH="$(pwd)/src"
python3 -m orion.study.p1.tables \
  --check \
  --archive papers/orion-11-recursive-epistemic-reconstruction/results/raw/test_scored.jsonl \
  --out papers/orion-11-recursive-epistemic-reconstruction/results
```

The checker ignores only `provenance.generated_utc` and tolerates documented
cross-platform floating-point differences within relative tolerance `1e-12`.
It compares every other field and the rendered Markdown.

Point `--archive` at `test_scored.jsonl`, not the whole `raw/` directory:
`test_runs.jsonl` is a run archive and intentionally lacks the scored-record
schema consumed by the table generator.

## Frozen scientific boundary

The current archive removes the execution-missingness defect; it does not create
support for broad historical H1. The active positive result is the distinct,
narrower credential-free mechanical claim `ORION-11.NECESSITY.V2.2.4`. The two claims
have different protocols, populations, comparators, and estimands and must not
be treated as the same result.

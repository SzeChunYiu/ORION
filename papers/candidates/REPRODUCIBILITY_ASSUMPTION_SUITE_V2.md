# ORION-16–ORION-18 V2 assumption-regression reproducibility contract

**Date:** 2026-08-17  
**Authority:** local deterministic artifact contract  
**Dependencies:** CPython standard library only

## 1. Purpose

The existing V1 checkers perform broader finite enumeration. This V2 suite targets gaps that can survive such enumeration:

- theorem assumptions not encoded by graph shape alone;
- positive/negative controls for hostile detectors;
- terminal semantics of frozen benchmark rows;
- suite-level coverage requirements that prevent trivial all-pass, all-reframe or deny-all systems.

## 2. Executable tree

```text
papers/candidates/
├── run_assumption_regressions_v2.py
├── ASSUMPTION_REGRESSION_RESULTS_V2.json
├── ASSUMPTION_REGRESSION_RESULTS_V2.md
├── paper-06-.../formal/
│   ├── check_assumption_regressions_v2.py
│   ├── test_assumption_regressions_v2.py
│   └── assumption_countermodels_v2.jsonl
├── paper-07-.../
│   ├── formal/check_benchmark_contracts_v2.py
│   ├── formal/test_benchmark_contracts_v2.py
│   └── benchmark/instances_v1.jsonl
└── paper-08-.../
    ├── formal/check_benchmark_contracts_v2.py
    ├── formal/test_benchmark_contracts_v2.py
    └── benchmark/authority_cases_v1.jsonl
```

## 3. One-command reproduction

From repository root:

```bash
python papers/candidates/run_assumption_regressions_v2.py \
  --json-output papers/candidates/ASSUMPTION_REGRESSION_RESULTS_V2.json \
  --markdown-output papers/candidates/ASSUMPTION_REGRESSION_RESULTS_V2.md
```

The runner:

1. imports each checker from its exact path;
2. executes each unit-test file in an isolated subprocess working directory;
3. executes every named structural check;
4. parses and evaluates every JSONL case against the reference policy;
5. enforces suite-level coverage/negative-control constraints;
6. records SHA-256 for every executable input and an aggregate artifact-set hash;
7. exits nonzero on any mismatch.

## 4. Frozen local receipt

Environment recorded by the generated JSON:

- CPython 3.13.5;
- Linux x86_64;
- no external package, network, provider, model, judge or LLM API.

Expected result:

| Suite | Unit tests | Named checks | Cases |
|---|---:|---:|---:|
| ORION-16 | 10 | 10 | 12 |
| ORION-17 | 7 | 10 | 8 |
| ORION-18 | 11 | 9 | 17 |
| **Total** | **28** | **29** | **37** |

Expected aggregate artifact-set SHA-256:

`bbf26697db10993486c3620c8571b6231de7eef997d966cdda8f87761e569a04`

## 5. Integrity properties

- ORION-16 contains equal numbers of `DETECTED` and `NOT_DETECTED` cases across six hostile kinds; a constant detector cannot pass.
- ORION-17 requires the target families, four terminal classes, a harmful-reframe control and an explicit non-retrieval transfer case.
- ORION-18 requires all five domains, clean authorization in each domain, paired blocked cases, all four verdicts, five laundering attacks and a clean registered cross-domain coercion; deny-all cannot pass.
- Duplicate case IDs and expected/predicted terminal mismatches fail the run.

## 6. Clean-environment gate still open

The local receipt is not an independent reproduction. Before a promotion or submission claim:

1. run in repository CI or a clean archived environment;
2. record exact commit/tree identity;
3. have a separate reviewer inspect the theorem assumptions and case oracles;
4. archive the immutable result and source bundle;
5. preserve any failure or changed count rather than regenerating the expected result post hoc.

## 7. Nonclaims

These checks establish internal artifact consistency only. They do not prove unrestricted theorems, validate a real agent, demonstrate benchmark superiority, close nearest work or authorize publication.

# ORION-20 Domain/Source Freeze V1 (FROZEN — NOT EXECUTED)

- Schema: `ORION.ORION-20.DomainSourceFreeze.v1` (machine form: `P10_DOMAIN_SOURCE_FREEZE_V1.json`)
- Study: `P10_H1_H6_WIDE_MULTI_DOMAIN_V1`
- Issue binding: SzeChunYiu/ORION#1086, ORION-20 box 1 ("Populate the frozen design") plus per-box verdicts for boxes 2-4
- Frozen: 2026-08-24T10:45:00Z
- Execution status: `CANNOT_CHECK__NO_P10_EXECUTION_IN_REPOSITORY`

> **NOT EXECUTED.** This is a frozen protocol artifact. `results_exist = false`,
> `campaign_executed = false`, `outcome_accessed = false`. Nothing in this document was
> downloaded, run or scored. It must never be cited as evidence of an empirical outcome.

## Relation to the H1-H6 freeze

Bound artifact: `papers/orion-20-structured-problem-solving/protocol/P10_H1_H6_PROTOCOL_FREEZE_V1.json`
(sha256 `8e32c2bee514d246bcd503fc2f0ef078bcc52adb7f40abdbcb642b703aec355c`, live-recomputed by the checker).

This artifact supplies the **domain/source/licence layer** of `required_inputs[0].protected_task_manifest`
and nothing else. The per-task ID enumeration (100 verifier-backed tasks per domain + 80 controls)
requires the pinned, licence-cleared downloads and is **NOT_POPULATED** here. The six other absent
required inputs stay absent. Where the two documents disagree, the H1-H6 freeze wins.

## Box 1 — populate the frozen design: DONE_AT_DOMAIN_SOURCE_LICENSE_LAYER

Four domains, named public sources, licence status per source, committed minimums
(4 domains / 100 tasks per domain / 400 total / 80 known-method controls) recorded as
**commitments, not executed counts** (`satisfied_by_this_artifact: false`).
Open remainder: per-task ID enumeration after licence selection.

## Frozen domains and sources

| Domain | Verifier | Source | Role | Licence |
|---|---|---|---|---|
| LEAN_INTERACTIVE_THEOREM_PROVING | Lean elaborator via LeanDojo | [yangky11/LeanDojo](https://github.com/yangky11/LeanDojo) | framework | MIT (VERIFIED 2026-08-24) |
| | | [openai/miniF2F](https://github.com/openai/miniF2F) | task-pool | **CANNOT_CHECK** — no licence file upstream |
| SYGUS_SYNTAX_GUIDED_SYNTHESIS | cvc5 (sygus mode) | [cvc5/cvc5](https://github.com/cvc5/cvc5) | solver | **CANNOT_CHECK** — composite COPYING, SPDX NOASSERTION |
| | | [sygus.org](https://sygus.org/) archives | task-pool | **CANNOT_CHECK** — no licence statement, per-problem provenance unresolved |
| IPC_PLANNING | Fast Downward + VAL | [aibasel/downward](https://github.com/aibasel/downward) | solver | GPL-3.0 (VERIFIED 2026-08-24; execution-as-tool only) |
| | | [KCL-Planning/VAL](https://github.com/KCL-Planning/VAL) | validator | BSD-3-Clause (VERIFIED 2026-08-24) |
| | | [aibasel/downward-benchmarks](https://github.com/aibasel/downward-benchmarks) | task-pool | **CANNOT_CHECK** — no repo-level licence; per-domain rights unconsolidated |
| CODE_GENERATION | EvalPlus (HumanEval+/MBPP+) | [evalplus/evalplus](https://github.com/evalplus/evalplus) | harness-and-task-pool | Apache-2.0 (VERIFIED 2026-08-24; embedded task content carries separate per-task terms) |

Every licence entry carries `verification`, `evidence_url` + `evidence_fetch_sha256` (verified case)
or a precise `reason` (CANNOT_CHECK case). Mirror licences (facebookresearch/miniF2F MIT,
google-deepmind/miniF2F Apache-2.0, yangky11/miniF2F-lean4 MIT) are recorded as facts, never as
clearances: a mirror's licence does not license the upstream original.

The native Lean arm carries the recorded CANNOT_CHECK handoff
(`top_tier/P10_NATIVE_LEAN_CANNOT_CHECK_HANDOFF_V1.md`, sha256 `add09b2c…0ce3`); this freeze does not clear it.

## Box 2 — implement baselines: CANNOT_CHECK

| Arm | Status |
|---|---|
| NATIVE | CANNOT_CHECK (Lean handoff; no native arm implemented in any domain) |
| EXACT_SEARCH | NOT_IMPLEMENTED_IN_REPOSITORY |
| SYNTHESIS | NOT_IMPLEMENTED_IN_REPOSITORY |
| REPRESENTATION_ONLY | NOT_IMPLEMENTED_IN_REPOSITORY |
| STRONGEST_DONOR | CANNOT_CHECK (comparator executables are a required-absent input of the H1-H6 freeze) |

Substituting a weaker proxy for an unavailable arm is forbidden; unavailable arms are reported unavailable.

## Box 3 — run H1-H6 exactly as frozen: CANNOT_CHECK

1. `P10_H1_H6_PROTOCOL_FREEZE_V1` has `execution_authorized=false`, lifecycle `PROSPECTIVE_FROZEN_NOT_EXECUTED`.
2. Six of eight required inputs remain absent (native runner, comparator executables, blinded
   obstruction gold + custodian, OCME witness protocol, cross-domain split, independent scorer custody).
3. H4 requires independently witnessed outside-closure cases; the issue hard boundary forbids
   self-certifying an external witness.

## Box 4 — machine-check candidate edits against the frozen old grammar/closure: CANNOT_CHECK

The machine-check contract is frozen (exhaustive non-membership, minimal edit, old-closure exclusion,
zero hidden access widening), but no H1-H6 execution has produced candidate edits. The only
machine-checked edits in the repository are the exact-setting toy/formal cases already receipted in
`top_tier/` (bound by sha256 in the JSON), which are not domain tasks.

## Inference unit, gates, boundaries

- Inference unit: **one protected verifier-backed theorem or task**, aggregated by domain.
  Forbidden units: search seed, model sample, generated row, episode, technical repeat.
- Pass gate: as frozen in `P10_H1_H6_PROTOCOL_FREEZE_V1.json` (HOLM-BONFERRONI over [H1,H2,H3,H5,H6],
  nonstatistical H4 certificate conjunction, noncompensatory worst-domain gates, catastrophic guards all zero,
  `MISSING_OR_UNVERIFIED_TASK_COUNTS_AS_NOT_SOLVED_AND_CANNOT_GRANT_PASS`). This document echoes by reference only.
- Non-bypass boundaries: licence verification precedes download; CANNOT_CHECK is never upgraded by
  mirror adjacency, elapsed time or inaction; committed minimums are not executed counts; post-data
  menu/verdict changes require a new versioned freeze; no weak-proxy substitution.

## Freeze discipline

- Checker: `papers/orion-20-structured-problem-solving/protocol/check_p10_domain_source_freeze_v1.py`
- Tests: `tests/unit/p10/test_p10_domain_source_freeze.py`
- The checker live-recomputes the H1-H6 protocol freeze sha256 against disk on every run.

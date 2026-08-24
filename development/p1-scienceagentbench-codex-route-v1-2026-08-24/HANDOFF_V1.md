# P1 ScienceAgentBench Codex CLI route V1 - handoff

## Terminal

`BLOCKED_CANNOT_CHECK_IMMUTABLE_MODEL_TOKENIZER_SEED_AND_BILLED_COST`

The locally authenticated Codex CLI 0.147.0 route is synthetic-transport
capable but is not admissible to the merged verified runner. Do not run any
official ScienceAgentBench task or weaken the runner contract.

This lane is integrated on `origin/main`
`2c96d32e552aba43bc4a5bed2da624f6083740cf`. The intervening PF-01 artifact
identity receipt closes only exact archive identity; PF-02 through PF-06 remain
open and PF-01 does not authorize official extraction or execution.

## Bound local route

- Client: `@openai/codex` / `codex-cli 0.147.0`; package, launcher, and native
  arm64 binary bytes are bound in `CODEX_ROUTE_PREFLIGHT_V1.json`.
- Provider/model request: built-in provider `openai`, slug `gpt-5.6-sol`, low
  reasoning, no reasoning summary, low verbosity, default service tier.
- Isolation: owner-controlled temporary `CODEX_HOME`, owner-managed
  authentication reference, ignored user config and project rules, read-only
  sandbox, never approval, and disabled `plugins`, `remote_plugin`, and
  `skill_search` features.
- Credential receipt boundary: the receipt process neither opened nor hashed
  credential bytes. No credential path, contents, hash, header, account
  identity, or session database is committed. Both temporary runtime homes and
  their authentication references were removed after the probes.
- Prompt transport: frozen UTF-8/LF bytes on stdin, frozen JSON Schema file,
  JSONL stdout, one output-last-message file, external 240-second attempt
  deadline, and post-event fail-closed token/tool caps.
- Seed: no seed is passed. Attempt ordinal `1` in the synthetic receipt and
  ordinals `1,2,3` in the candidate schedule are explicitly not seeds.

## Synthetic transport receipt

Exactly one synthetic nonbenchmark generation attempt was run per arm. No
generated program was executed.

| Arm | Thread contract | Input | Output | Reasoning | Tools | Wall time (s) | Transport | Runner |
|---|---|---:|---:|---:|---:|---:|---|---|
| RR | phase 1 resumed phase-0 thread | 51949 | 1016 | 68 | 0 | 25.756897623941768 | PASS | CANNOT_CHECK_BILLED_COST |
| OS | one fresh phase-1 thread; no phase-0 call | 16742 | 141 | 31 | 0 | 7.724022042006254 | PASS | CANNOT_CHECK_BILLED_COST |
| NR | phase 1 used a distinct fresh thread | 33554 | 566 | 27 | 0 | 20.431377376022283 | PASS | CANNOT_CHECK_BILLED_COST |

All five phase stderr streams were empty. Raw JSONL, rendered prompts, model
outputs, and raw thread IDs remain outside the repository; the committed
receipt contains only hashes, sizes, usage, timing, topology assertions, exit
codes, tool counts, and null billed cost.

The first narrow RR trial was correctly rejected despite a valid typed-state
message because its JSONL also contained this client error item:

`Skill descriptions were shortened to fit the skills context budget. Codex can still see every skill, but some descriptions are shorter. Disable unused skills or plugins to leave more room for the rest.`

The passing route used a fresh temporary home and disabled optional
plugin/skill discovery. The parser was not weakened: any error item still fails
closed.

## Unsupported guarantees

1. Immutable resolved model snapshot: `CANNOT_CHECK`. Bundled and refreshed
   catalogs use the same slug but disagree on `max_context_window` (272000 vs
   872000), and JSONL emits no resolved snapshot. Reopen only if a durable
   snapshot identifier is joined to each turn.
2. Exact tokenizer revision: `CANNOT_CHECK`. Neither CLI help, catalog, nor
   JSONL exposes it. Reopen only with an immutable tokenizer name/revision
   joined to terminal usage.
3. Provider seed capability and schedule: `CANNOT_CHECK`. Strict `seed=101`
   fails before generation with exact stderr
   ``Error loading config.toml: unknown configuration field `seed` in -c/--config override``.
   Reopen only after a supported seed control and provider-confirmed semantics
   exist.
4. Per-attempt billed USD: `CANNOT_CHECK`. JSONL emits no billed-cost field;
   subscription access is not evidence of zero cost. Reopen only with an
   owner-authoritative billed-USD record joined to the same attempt.
5. Provider-side hard token/tool/time caps: `CANNOT_CHECK`. The route uses an
   external deadline and post-event rejection; it does not claim provider-side
   prevention of excess resource use.

## Scope and authority

- Official tasks run: `0`.
- Official data, candidate, evaluator, gold, rubric, feedback, score, and
  outcome material opened: `false`.
- Manuscript, PDF, publication package, pytest, and CI work: `none`.
- Scientific authority delta: `NONE`.
- Production attempt schedule: specified prospectively but not run.

## Direct verification

From the repository root, run only:

```bash
python development/p1-scienceagentbench-codex-route-v1-2026-08-24/validate_codex_route_v1.py
shasum -a 256 -c development/p1-scienceagentbench-codex-route-v1-2026-08-24/SHA256SUMS
```

Expected validator terminal:

`P1_SAB_CODEX_ROUTE_SYNTHETIC_VALIDATION_PASS tests=13 runner_admissible=false official_tasks_run=0 outcomes_opened=0`

The pull request for this lane must remain unmerged for independent review.

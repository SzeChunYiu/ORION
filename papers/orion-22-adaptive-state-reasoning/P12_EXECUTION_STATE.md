# P12 Execution State (A2-P1 campaign, issue SzeChunYiu/ORION-paper#49)

Working ledger of execution-host state: lanes, amendments, jobs, record
counts. Claims live in the freeze/receipt artifacts, not here. Updated per
work window.

## Lanes (merged identity set)

| family | lane | state 2026-09-03 |
|---|---|---|
| gpt-5.5-codexcli | codex CLI (LUNARC) | tuning COMPLETE 68/68 (sbatch 3571108, amended template P12_TERMINAL_V1M) |
| claude-fable-5-claudecli | claude CLI (LUNARC) | tuning scheduled 2026-09-04 03:05 Stockholm (job 3570206, after account window reset) |
| glm-5.3-apimessages | z.ai Anthropic-Messages API (LUNARC) | tuning RUNNING (job 3572509, started 2026-09-03 22:41 UTC) |

## Amendments (all preregistered at 0 protected model calls)

1. `top_tier/P12_HARNESS_AMENDMENT_DATASET_MOUNTPOINT_V1.json` — terminal
   template mount sentence (P12_TERMINAL_V1M); codex tuning rerun from
   scratch under it.
2. `top_tier/P12_HARNESS_AMENDMENT_JUDGE_ENGAGEMENT_V1.json` — judge shim
   AzureOpenAI delegates to the codex-backed `OpenAI` path (upstream picks
   AzureOpenAI iff OPENAI_API_KEY unset). Eval defect finding:
   `top_tier/P12_EVAL_JUDGE_ENGAGEMENT_FINDING_V1.md` (Defect A fixed;
   Defect B = 39-cell codex outage window 14:43:46-15:03:29 UTC, account
   reset 2026-09-07).
3. `top_tier/P12_HARNESS_AMENDMENT_THIRD_FAMILY_GLM_V1.json` (commit
   b9a2842f9) — third study family `glm-5.3-apimessages`
   (`top_tier/MODEL_IDENTITY_GLM_ADDENDUM_V1.json`; parent freeze
   byte-identical). Endpoint frozen
   `https://api.z.ai/api/anthropic/v1/messages`, model `glm-5.3`,
   temperature 0.0, max_tokens 8192, bearer from env
   `ANTHROPIC_AUTH_TOKEN` only. Coordinator supersession 2026-09-03: the
   originally-scoped cmkey.cn route was abandoned after all three
   reachable bearer tokens verified dead 2026-09-03 20:18-20:21 UTC
   ('该令牌已过期' x2, '该令牌状态不可用' x1).
   Follow-up fix 61c4d8056: `echo_check(fake=True)` no longer writes
   `runs/tuning/echo_record.json` (a self-test on the execution host had
   replaced same-day real entries with fake-green ones; no gated run ever
   started on a fake entry).

## GLM lane receipts

- Echo (plain, lane-scoped) sbatch 3572508 on cn005, 2026-09-03 20:28 UTC:
  `glm-5.3-apimessages ok=true rc=0` (2.1 s from Mac pre-probe; LUNARC node
  answered directly — no billy-old fallback needed).
- Echo (gym-shape, same sbatch): real terminal template, family
  ZitongLu1996/EEG2EEG inst=71, prompt sha
  7f05c016c5a16313ff31e2bd7d38b4d0eb75cc8aa22b6a5ed19a7fd0e7b098b5
  (1023 bytes), rc=0 in 60.96 s, reply 2888 bytes, GYM_SHAPE_ECHO_GREEN.
- Tuning job 3572509 (`exec_sbatch/p12_glm_tuning.sbatch`): lane-scoped
  echo rc=0 then `--run --lane glm-5.3-apimessages`; records land in
  `top_tier/runs/tuning/glm-5.3-apimessages/<inst>_<action>.json`
  (cell-complete, resumable, fail-closed rc on any transport/empty reply).

## Eval plan (unchanged discipline)

ONE unified eval batch on the amended shim AFTER the 2026-09-07 codex
account refill, covering all three lanes (eval driver + emit_matrix read
the merged identity set since amendment 3). No separate GLM instrument.
The 39 archived codex outage cells stay codex-only (re-executed as codex,
never as glm — no model mixing within a condition).

## Open items

- GLM tuning drain (job 3572509): verify 68/68 + rc mix on completion.
- Claude tuning (job 3570206) after 03:05 Stockholm reset.
- Unified eval batch + judge transcripts after Sept 7 refill.
- PR #2196 (open, do-not-merge) carries the amendment commits
  14a8521cb, b9a2842f9, 61c4d8056.

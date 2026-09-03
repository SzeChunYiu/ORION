# P12 eval judge-engagement instrument finding (V1) — 2026-09-03

## Observation (job 3572226, amended-template codex tuning eval)

68/68 eval records landed (`P12_EVAL_TUNING_RC=0`); emit-matrix refused RC=2
`CANNOT_CHECK_MISSING_CELLS` (68 claude cells absent — fail-closed by design).
The terminal mix is NON-degenerate: the mountpoint amendment took.

- 18/68 `valid_program=1`; 4/68 `success_rate=1` (A_BALANCED 2, A_STATE_MAX 2,
  A_REASON_MAX 0, A_RETAIN_MINIMAL 0); mean codebert 0.851/0.855 (full-state
  arms) vs 0.770/0.779 (stripped arms) — a plausible treatment gradient.
- 23/68 run records construct correct `benchmark/datasets/...` input paths
  (0 pre-amendment). The pre-amendment archive is 68/68 tracebacks
  (43 FileNotFoundError + 24 pyogrio/rasterio + 1 SyntaxError), 0 valid,
  0 success.

Two residual classes are NOT treatment results:

## Defect A (instrument): the frozen judge substitution cannot engage

14/68 cells carry
`log_info = RuntimeError('judge shim: AzureOpenAI configured but no Azure
credentials exist in this campaign (MODEL_IDENTITY_FREEZE_V1.json: CLI lanes
only)')` and `success_bool=false` WITHOUT the program ever being judged.
`eval/tuning/judge_transcripts/` is empty (0 codex judge calls attempted).

Root cause (upstream `gpt4_visual_judge.py`, module level, unmodified):

```python
if os.getenv("OPENAI_API_KEY"):
    client = OpenAI()
else:
    client = AzureOpenAI(...)
```

This campaign sets no `OPENAI_API_KEY` (MODEL_IDENTITY_FREEZE_V1: CLI lanes
only), so the upstream ALWAYS constructs `AzureOpenAI`, whose shim
constructor raises by design. The codex-backed `OpenAI` substitution — the
entire subject of `P12_JUDGE_SUBSTITUTION_RECEIPT_V1.md` — is unreachable in
real evals. Judge-smoke job 3570445 (scores [10,5,10]) exercised the shim's
`OpenAI` path directly and could not see the branch, the same masked-path
shape as the mountpoint defect.

Because `emit_matrix` consumes `success_bool`, defect A poisons the score
matrix: judge-needing cells are false for infrastructure reasons.

## Defect B (operational): mid-run codex lane outage — 39/68 run cells

Job 3571108 (codex tuning rerun) wrote 29 healthy terminals
(14:01:02–14:43:08 UTC, rc=0, 23–83 s each), then from 14:43:46 through
15:03:29 EVERY codex call returned rc=1 in 14–17 s with empty stdout. All 39
post-outage cells have `terminal_output=""` (uniformly ~9–10 per action —
not treatment-dependent) and their unit calls (S1/R1) also returned empty.
Codex rollouts show `task_complete` with `last_agent_message: null` and no
model events; an interactive probe after the run returned rc=1 with an
explicit account reset time of 2026-09-07 16:19. The eval records for these
cells are `valid_program=0, "output-contract failure: empty terminal output"`
(39/68) — infrastructure, not model, failures.

## Disposition (preregistered, successor to the judge substitution receipt)

- `P12_HARNESS_AMENDMENT_JUDGE_ENGAGEMENT_V1.json`: the shim's `AzureOpenAI`
  constructor delegates to the same codex-backed `_Chat` as `OpenAI` instead
  of raising. The judge invocation itself is UNCHANGED (same frozen
  `codex exec --skip-git-repo-check` argv, same identity-blind prompt, same
  upstream `[FINAL SCORE]` parsing and >= 60 threshold).
- Amendment made at 0 protected calls; tuning binding unwritten; the mount
  amendment (P12_TERMINAL_V1M) is untouched.
- Effect on existing artifacts: the 68 post-mountpoint-amendment codex eval
  records (defects A and B mixed) are archived, not deleted, before the
  unified rerun; the 39 defect-B run records are archived and refilled by the
  resumable run driver after the lane reset; the 29 healthy run records
  (including all 4 successes) are retained.
- Sequencing: BOTH lanes' eval passes run once, after the amendment and after
  the codex lane reset, so every eval record in the binding is produced under
  the fixed instrument. The claude tuning run (3570206) is unaffected
  (separate lane) and proceeds on schedule.

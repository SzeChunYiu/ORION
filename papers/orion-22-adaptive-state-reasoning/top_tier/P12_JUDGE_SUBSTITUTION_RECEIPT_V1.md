# P12 judge-substitution receipt — V1 (frozen before any tuning or protected call)

- Date: 2026-09-03
- Authority: SzeChunYiu/ORION-paper#49 (A2 Phase 1); operator directive recorded in
  MODEL_IDENTITY_FREEZE_V1.json (CLI lanes only, no API keys exist in this campaign)
- Scope: the pinned upstream ScienceAgentBench evaluator
  (OSU-NLP-Group/ScienceAgentBench @ c26e151ed601ba109dc4d35e057ff8e73fec469d)
  as invoked by `campaign_eval_driver_v1.py`, tuning and protected phases alike.
- State at freeze: `flags.execution_started = false`, no tuning or protected model
  call made, no outcome accessed (MODEL_IDENTITY_FREEZE_V1.json flags all false).

## The gap

Upstream `gpt4_visual_judge.py` scores plot-producing tasks by calling
`client.chat.completions.create(..., model="gpt-4o-2024-05-13", n=3)` through the
`openai` SDK, which requires an OPENAI_API_KEY (or Azure credentials). The campaign
model-identity freeze pins exactly two CLI lanes under operator subscriptions and
records that no API keys exist. Without a substitution the judge-dependent instances
could not be scored at all on the execution host.

## The substitution

`eval_judge_shim/openai/__init__.py` is placed FIRST on PYTHONPATH by
`campaign_eval_driver_v1.py` only. `from openai import OpenAI, AzureOpenAI` in the
unmodified upstream judge imports the shim; each of the `n=3` samples becomes one
`codex exec` call of the frozen GPT_CLASS lane (`gpt-5.5-codexcli`, codex-cli
0.129.0-alpha.15, gpt-5.5) with the two figures attached via `-i`, single-turn,
non-interactive — the same invocation contract as the campaign's own codex lane.
Response objects are shaped so upstream code paths (regex `[FINAL SCORE]: (\d{1,3})`,
n-sample averaging, >= 60 threshold) run byte-for-byte unchanged.

Nothing inside the pinned upstream repo is modified. The judge prompt is
identity-blind (two figures + rubric; the model under test is never named), and the
judge lane is uniform across ALL judged cells of BOTH tested model families, so the
comparison cannot favor either family through the judge.

## Recorded fidelity deviations

1. Judge model identity: gpt-5.5 via pinned codex CLI instead of
   gpt-4o-2024-05-13 via API. Uniform across every judged cell; affects both model
   families identically.
2. Decoding controls: temperature/top_p/presence/frequency penalties are not
   controllable through the CLI (provider-default decoding). n=3 sample averaging is
   preserved by issuing three separate CLI calls. Upstream's no-match -> 0 parsing
   default is upstream code, unchanged.
3. Failure semantics: a nonzero-rc, timeout, or missing `codex` binary raises
   (mirroring an upstream API error) so the eval driver records an infrastructure
   failure for that cell instead of a silent zero. Every judge call is logged to
   `eval/<phase>/judge_transcripts/judge_calls.jsonl` (rc, seconds, stdout tail).
4. Judge dependence footprint (from the verified substrate freeze): judge-dependent
   tuning instances are 12 of 17 — admet_ai [20], papyrus-scaffold-visualizer [17],
   eofs [48, 49, 50], geopandas [4, 10, 14, 23, 33, 47], EEG2EEG [73]; MAST-ML is
   deterministic. Any family-level readout therefore leans on this receipt.

## Alternatives rejected

- OpenAI API key for gpt-4o-2024-05-13: none exists in the campaign; requesting one
  would breach the operator-subscription-only lane freeze.
- Dropping judge-dependent instances: would silently shrink the frozen tuning/
  protected splits — prohibited by the prereg (families and n are frozen).
- claude CLI as judge: no image input in single-turn print mode; only the codex
  lane can receive figures.
- Scoring plots by numeric closeness instead of the judge: replaces upstream
  semantics rather than substituting the transport — rejected.

## Verifiability

- Shim code: `eval_judge_shim/openai/__init__.py` (self-tested through
  `campaign_eval_driver_v1.py --self-test`, which asserts the upstream regex
  semantics on the shim's parser).
- Per-call transcripts: `eval/<phase>/judge_transcripts/judge_calls.jsonl`.
- Eval records carry `"judge_substitution":
  "codex-cli-lane (P12_JUDGE_SUBSTITUTION_RECEIPT_V1)"`.

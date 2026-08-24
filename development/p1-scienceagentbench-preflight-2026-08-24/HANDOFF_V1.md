# P1 ScienceAgentBench preflight handoff V1

## Terminal

`P1_SAB_PREFLIGHT_SOURCE_AND_MASK_READY__102_VERIFIED_TASKS_BOUND__FULL_ARCHIVE_SHA256_AND_VERIFIED_RUNNER_RUNTIME_CANNOT_CHECK__ZERO_OUTCOMES_OPENED__ZERO_TASKS_RUN`

This packet is an outcome-blind source, rights, access, evaluator and protocol
preflight. It is not a benchmark result, protocol preregistration, independent
review or scientific promotion. No benchmark task was run. Public annotation
inputs, one ZIP header byte and ZIP directory metadata were inspected; file-entry
payloads, gold programs,
evaluation-program bodies, rubric bodies, gold results and task outcomes were
not opened.

## What is bound now

| Item | Exact finding |
|---|---|
| Official code | `OSU-NLP-Group/ScienceAgentBench` at `c26e151ed601ba109dc4d35e057ff8e73fec469d`; code licence MIT. |
| Verified inputs | Hugging Face revision `9c6e96c9e74572e979b0930ee735041cef528cb7`; verified Parquet SHA-256 `c6f937863a220bd1762a00c20a0f79cc8dfca900b819bdb552150310731ae147`. |
| Population | 102 unique tasks, IDs 1--102: 20 computational chemistry, 27 GIS, 27 bioinformatics and 28 psychology/cognitive science. |
| Version hazard | `run_infer.py` hardcodes `validation`; the evaluator also defaults to `validation`. The verified split changes `task_inst` for 9 tasks. Any future run must explicitly bind `verified` and fail closed on the manifest. |
| Full artifact | The public SharePoint route supports byte ranges. `benchmark_verified.zip` is 1,769,478,786 bytes. Its central directory describes 845 encrypted files and 4,071,815,117 uncompressed bytes. The full archive SHA-256 is unknown because it was deliberately not downloaded. |
| Evaluator | Source exists, but a complete run needs the external artifact, Docker, substantial scratch disk and an OpenAI/Azure credential route. The visual judge calls `gpt-4o-2024-05-13` with temperature 0.2 and three samples, so scoring is not fully deterministic. |
| Deterministic intervention | `MASK_MANIFEST_V1.json` freezes, for all 102 verified tasks, exact hashes of initially visible and mask-then-recover input fields. It can be frozen without viewing outcomes. |
| Matched arms | `PROTOCOL_DESIGN_V0.json` specifies RR, full-context one-shot and staged reset/no-reconstruction arms plus task-level paired gates. Exact model, tokenizer, prompts, seeds and budgets remain unbound; this is therefore a design, not a frozen confirmatory protocol. |

The archive-size audit used only the end-of-file and central-directory byte
ranges. The central-directory hash is not a substitute for a full-archive
SHA-256.

## Rights and retention

- The official GitHub code is MIT.
- The benchmark declares 96 tasks under CC BY 4.0.
- Task 3 retains the current `hackingmaterials/matminer` upstream terms.
- Tasks 32, 46, 53, 54 and 84 retain the current `rasterio/rasterio` upstream
  terms.
- GitHub reports `NOASSERTION` for both exception licence files. This packet
  preserves the exact pinned licence text hashes and does not relabel them.
- The official README says not to redistribute the unzipped benchmark data.
  Keep the ZIP, extracted data, gold/evaluation programs, rubrics, container
  layers and raw evaluator material off-repository. Publish only lawful source
  citations, task IDs, ORION-authored predictions, task-level receipts and
  bounded aggregate results.

## Fail-closed blockers

1. **Artifact identity:** the 1.769 GB ZIP needs a full byte count and SHA-256
   on approved external storage before extraction or execution.
2. **Correct split:** an additive runner must load the pinned `verified` split;
   neither upstream inference defaults nor evaluator defaults are admissible as
   written.
3. **Runtime:** this Mac has no running Docker daemon, approximately 5 GiB free
   and no evaluator credentials. Upstream documents at least
   `5 + max_workers * 25` GB transient disk (30 GB even at one worker).
4. **Evaluator reproducibility:** the official visual judge is stochastic and
   the container build resolves several unpinned dependencies. The exact route,
   images, resolved packages and all three judge responses must be retained.
5. **Matched-arm implementation:** model/provider/tokenizer, prompt bytes,
   seeds, token/tool/time ceilings and RR/OS/NR adapters must be frozen and
   validated on synthetic fixtures before any official outcome is opened.
6. **Claim boundary:** ScienceAgentBench gives scientific code-task success,
   not gold for hidden-formulation responsibility or typed scientific
   transition authority.

Missing, wrong-split, partial, unhashable, evaluator-failed or credential-failed
rows are `CANNOT_CHECK`; they must not be silently scored as solved=0 or replaced
by another evaluator.

## Exact next handoff

1. Select an owner-approved isolated runtime and external data/cache location
   with enough disk and working Docker. Do not stage the artifact in ORION.
2. Retrieve the artifact from the official landing URL in
   `PREFLIGHT_RECEIPT_V1.json`; record full ZIP SHA-256, exact bytes, ETag,
   extracted directory manifest and licence notices before agent execution.
3. Implement a fail-closed verified-split wrapper. It must match the 102 IDs,
   verified Parquet hash and `MASK_MANIFEST_V1.json`; `validation` must be a hard
   error.
4. Bind the exact model/provider/tokenizer, prompt bytes, seeds, budgets,
   container/image manifests, dependency resolution and secret-handling plan.
   The upstream Dockerfile embeds evaluator credentials in image `ENV`, so use
   a disposable approved builder and prove cleanup.
5. Run only synthetic, nonbenchmark adapter fixtures. Once static receipts are
   clean, hash and sign the final protocol/runner/analysis bundle before any
   official score is opened.
6. Seal three candidates per task/arm, then invoke the pinned official evaluator
   with `--split verified`. Retain all attempts, all task failures and all judge
   samples. Cost is the sum of every attempt, not the cost of the outcome-picked
   best attempt.
7. Apply the issue #1086 gate exactly. Require both RR--OS and RR--NR paired CI
   lower bounds above zero, a gain of at least 0.08 over the stronger aggregate
   comparator, every discipline loss no worse than -0.05, cost at most 1.5x and
   102 parseable official evaluator receipts.

## Source trail (retrieved 2026-08-24 UTC)

- Official code and access/licence instructions:
  <https://github.com/OSU-NLP-Group/ScienceAgentBench/tree/c26e151ed601ba109dc4d35e057ff8e73fec469d>
- Verified input record:
  <https://huggingface.co/datasets/osunlp/ScienceAgentBench/tree/9c6e96c9e74572e979b0930ee735041cef528cb7>
- Archival paper record: <https://arxiv.org/abs/2410.05080v3>
- Rasterio upstream terms at audited revision:
  <https://github.com/rasterio/rasterio/blob/9709d1fce53b8c11ace1741ef25cfe427b197fb8/LICENSE.txt>
- Matminer upstream terms at audited revision:
  <https://github.com/hackingmaterials/matminer/blob/8ddb18c74064ab3668d7b5aed7c360abdfdae5de/LICENSE>

Machine-readable source hashes, sizes, access probes, exception-task mappings,
evaluator hazards and blocker closures are in `PREFLIGHT_RECEIPT_V1.json`.

## Scientific boundary

Even a future positive terminal would establish only bounded public-benchmark
utility of the frozen recovery controller on ScienceAgentBench tasks. The mask,
responsibility interpretation and reason why recovery helped remain
ORION-authored. Public data, local hashes and same-owner execution do not create
protected custody or independent scientific authority. Current scientific
authority delta: `NONE`.

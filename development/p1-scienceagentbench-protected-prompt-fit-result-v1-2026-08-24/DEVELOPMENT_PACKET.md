# Protected prompt-fit result V1 development packet

Date: 2026-08-24  
Lane: `development/p1-scienceagentbench-protected-prompt-fit-result-v1-2026-08-24/`  
Merged preflight: PR #1179, commit `eaef8171de537b2d388c2b1310bccc23a92eaed3`  
Execution checkout: `6172ee61e336490b75d3a39bc3a8af86a8946c94`

## Verdict

The merged protected prompt-fit preflight was executed without a token ledger on the privately staged, owner-authorized seven-field ScienceAgentBench row source. It failed closed before emitting `PROTECTED_PROMPT_FIT_RECEIPT_V1.json`:

```text
P1_SAB_PROTECTED_PROMPT_FIT_PREFLIGHT_V1_FAIL: prompt template OS_PHASE1 has unreplaced marker or missing LF
```

The exact result is therefore **`CANNOT_CHECK`**, not partial success:

- state-independent static prompt fit: `CANNOT_CHECK_NO_PRODUCTION_RECEIPT`;
- dynamic RR phase 1: `CANNOT_CHECK_DYNAMIC_RR_PHASE0_STATE_AND_EXACT_GGUF_TOKEN_LEDGER_REQUIRED`;
- token counts: `null`;
- production admissibility: `CANNOT_CHECK`;
- tasks executed: `0`;
- official outcomes opened: `0`;
- scientific-authority delta: `NONE`.

No partial prompt-fit receipt or token count has been manufactured.

## Outcome-blind custody and extraction

The protected Parquet source was pinned to `osunlp/ScienceAgentBench` revision `9c6e96c9e74572e979b0930ee735041cef528cb7` and verified as:

- bytes: `129086`;
- SHA-256: `c6f937863a220bd1762a00c20a0f79cc8dfca900b819bdb552150310731ae147`.

PyArrow `21.0.0` projected exactly these seven authorized columns:

`instance_id`, `domain`, `task_inst`, `output_fname`, `domain_knowledge`, `dataset_folder_tree`, `dataset_preview`.

The 102 ordered integer IDs were normalized to canonical decimal strings and all 510 manifest value bindings matched. Gold, evaluator, rubric, and outcome fields decoded: `0` each. The private authorized-row source is bound by:

- bytes: `278882`;
- SHA-256: `c1a8901e8ad0ed4a1d5f15533def5e7ec6f514c61192a516f8f273c191e9a023`;
- retention: private non-repository custody only.

`OUTCOME_BLIND_EXTRACTION_RECEIPT_V2.json` is body-free and is the authoritative extraction receipt in this lane. An earlier setup attempt used a V1 extraction-receipt shape that omitted the required `source.official_outcomes_opened` member; it failed before preflight output and is excluded from the scientific result.

## Exact staged model and merged inputs

The live GGUF was independently measured through a held descriptor before the production attempt:

- model: `Qwen3-Coder-30B-A3B-Instruct-Q4_K_M.gguf`;
- bytes: `18556689568`;
- SHA-256: `fadc3e5f8d42bf7e894a785b05082e47daee4df26680389817e2093056f088ad`;
- mode: `0400`;
- staging receipt SHA-256: `3a3f82d3d376ee418aa1db3f20712dc2cf9d84ef1c147b4fccc331651dce2e73`;
- source-and-integrity receipt SHA-256: `3b50b7ec2fc3d4191b19e56391ddcbfdbbdfbc8144a3235e3987ef65f0846ade`.

The six staged public files matched the execution checkout byte-for-byte. Their byte counts and SHA-256 bindings are preserved in `PREFLIGHT_EXECUTION_FAILURE_RECEIPT_V1.json`; the result validator remeasures the repository copies. The merged preflight implementation and contract were not edited, patched, or bypassed.

## Receipt-backed execution failure

The corrected V2 attempt ran from `2026-08-24T17:41:44Z` through `2026-08-24T17:41:58Z` and returned exit code `1`. It supplied no `--token-ledger`. The combined stdout/stderr was 109 bytes with SHA-256 `c0869361865a938f946873051daa7b6f97223c9e90fea23a9834f31acb126693`. No production receipt was created.

A private source execution receipt remains outside Git:

- bytes: `4046`;
- SHA-256: `0588007859d829f57bb0bf24df02424c7fb57ad053b91f914896afe9c753a7a6`.

The public `PREFLIGHT_EXECUTION_FAILURE_RECEIPT_V1.json` carries only body-free bindings, the exact terminal line, typed null/CANNOT_CHECK outcomes, and retention declarations.

## Post-failure diagnostic

A private diagnostic reused the merged `packetize_bound_row` and `_render_static_prompt` functions. It emitted only public task IDs, phase IDs, attempt numbers, and collision/status hashes; it emitted no task, packet, or prompt body.

Across 1,224 static render probes:

- 1,200 passed rendering;
- 24 failed closed;
- affected public task IDs: `4`, `10`, `88`, `89`;
- `OS_PHASE1`: 12 failures;
- `NR_PHASE1`: 12 failures;
- `RR_PHASE0` and `NR_PHASE0`: 0 failures;
- all 24 failures had literal double-brace collisions in canonical recovered-packet JSON;
- no collision-free probe failed;
- no double-brace-collision probe passed.

This establishes the post-failure diagnosis `ALL_AND_ONLY_DOUBLE_BRACE_COLLISION_PROBES_FAILED_CLOSED` for these authorized static render probes. It does **not** replace the missing production receipt, produce token counts, establish fit, or authorize generation. The merged renderer rejects any `{{` or `}}` remaining after template insertion, including literal pairs originating inside inserted authorized JSON.

## Artifact inventory

- `OUTCOME_BLIND_EXTRACTION_RECEIPT_V2.json` — exact body-free extraction receipt.
- `LIVE_GGUF_STAGING_RECEIPT_V1.json` — exact body-free independent model measurement.
- `PREFLIGHT_EXECUTION_FAILURE_RECEIPT_V1.json` — sanitized receipt-backed failure record.
- `PROMPT_MARKER_COLLISION_DIAGNOSTIC_V1.json` — 1,224 body-free task/phase/attempt hash probes and summary.
- `PROTECTED_PROMPT_FIT_RESULT_V1.json` — bounded adverse result and claim boundary.
- `validate_protected_prompt_fit_result_v1.py` — repository-only validator; it never opens protected rows.
- `HANDOFF_V1.md` — bounded review handoff.
- `SHA256SUMS` — additive-lane integrity manifest.

## Explicit exclusions

This lane contains no Parquet, authorized-row source, task body, masked packet, recovered packet, prompt body, GGUF, token ledger, generated completion, evaluator/rubric/gold/outcome field, credential, manuscript change, or PDF. No generation, evaluation, pytest, CI, external model API, or GPU job was run for this result.

## Validation

From the repository root:

```bash
rtk python development/p1-scienceagentbench-protected-prompt-fit-result-v1-2026-08-24/validate_protected_prompt_fit_result_v1.py
rtk proxy sh -c 'cd development/p1-scienceagentbench-protected-prompt-fit-result-v1-2026-08-24 && sha256sum -c SHA256SUMS'
rtk git diff --check origin/main...HEAD
```

The validator inspects only committed body-free artifacts and merged public upstream files.

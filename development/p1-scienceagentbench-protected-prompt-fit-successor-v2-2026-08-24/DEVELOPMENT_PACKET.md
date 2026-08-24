# Protected prompt-fit successor V2 development packet

Date: 2026-08-24
Lane: `development/p1-scienceagentbench-protected-prompt-fit-successor-v2-2026-08-24/`
Protected execution: LUNARC job `3537617`
Repair dependency: PR #1192, merge commit `ee66ee2b6489f7c754ffff219e2ab183c03d6368`

## Bounded verdict

The repaired, merged protected prompt-fit preflight consumed an owner-authorized private row projection and a private exact-GGUF token ledger. Exactly one bounded A40 job completed successfully and emitted a body-free production receipt.

The result is deliberately narrow:

- **state-independent static prompts:** `1224/1224 FIT_FROM_BOUND_TOKEN_LEDGER`;
- **static not-fit prompts:** `0`;
- **dynamic RR phase 1:** `306` records, all `CANNOT_CHECK_DYNAMIC_RR_PHASE0_STATE_REQUIRED`;
- **production admissibility:** `CANNOT_CHECK`;
- **owner-authoritative billed cost:** `CANNOT_CHECK`;
- **scientific-authority delta:** `NONE`;
- **generation, official task execution, evaluator/outcome access, external API, and credentials:** none.

This successor does not rewrite or supersede the adverse PR #1190 result. It preserves that lane byte-for-byte and records a later result after the separately reviewed PR #1192 repair.

## Exact tokenizer evidence

The private ledger was measured against the staged GGUF through loopback `POST /tokenize` using:

- `add_special=true`;
- `parse_special=true`;
- canonical request JSON;
- three requests per prompt;
- byte-identical and integer-token-ID-identical responses across all three repeats.

There were `1224` state-independent prompt records and `3672` tokenize requests. Prompt, request, and response hashes were retained; integer token IDs were retained only in private non-repository custody.

The two distinct private ledger bindings are preserved without importing either payload:

- raw ledger file: `196220` bytes, SHA-256 `340a51d96f9e39a53c5317fb3999ad28e5918d17af7a6d93381e4a4e7ae7c82d`;
- canonical ledger-content SHA-256 consumed by the repaired preflight: `93f42c0bdad394a558f61880896e8f68402dd87da00cfa28d4d0c7cfff96aa67`.

The private token-ID audit is `4664053` bytes with SHA-256 `04e33ef543e9ba602ed11eaa99145ecd765be883b0efd427c36b30e3d865b5fc`. It is not in Git.

## Static prompt geometry

All prompts use a `32768`-token context. Counts and exact token ranges are:

| Phase | Records | Minimum prompt tokens | Maximum prompt tokens | Output cap |
|---|---:|---:|---:|---:|
| `RR_PHASE0` | 306 | 213 | 468 | 1024 |
| `OS_PHASE1` | 306 | 203 | 21022 | 8192 |
| `NR_PHASE0` | 306 | 213 | 468 | 1024 |
| `NR_PHASE1` | 306 | 218 | 21037 | 7168 |

The worst occupied context is `29214` tokens and the minimum remaining margin is `3554` tokens. `TOKEN_LEDGER_AUDIT_AGGREGATE_V2.json` is a body-free recomputation from the bound production receipt; it does not contain prompt bodies or integer token-ID arrays.

## Dynamic RR boundary

RR phase 1 depends on the corresponding RR phase 0 generated state. This lane did not generate that state. Therefore all `306` dynamic RR phase-1 records remain `CANNOT_CHECK_DYNAMIC_RR_PHASE0_STATE_REQUIRED`. Static fit does not imply dynamic fit, production admissibility, task success, evaluation success, or scientific evidence.

## Scheduler and cleanup evidence

Exactly one bounded job appears in the lane evidence:

- job: `3537617` (`p1_sab_pf_succ_v1`);
- state: `COMPLETED`;
- exit: `0:0`;
- elapsed: `00:02:03`;
- allocation: one A40, 8 CPUs, 64 GB, one node;
- process group absent after cleanup: true;
- loopback listener absent after cleanup: true.

`SACCT_V1.txt`, `TERMINAL_V1.txt`, `SUCCESSOR_JOB_RECEIPT_V1.json`, `CLEANUP_V1.json`, and `SCHEDULER_RUNTIME_RECEIPT_V2.json` bind this evidence. Private scheduler/preflight streams remain outside Git and are represented only by byte counts and SHA-256 hashes.

## Upstream bindings

The result binds the repaired public preflight inputs:

- contract: `8840` bytes, SHA-256 `a2c1dd159f662f019697a3f3a12d7cd06a3d6533258f73d24ed6390a236e51d1`;
- implementation: `77033` bytes, SHA-256 `4b605096e3421acd9f826e20864d96eda793f6a9b97879a264d4d8be2acac136`;
- model: `18556689568` bytes, SHA-256 `fadc3e5f8d42bf7e894a785b05082e47daee4df26680389817e2093056f088ad`;
- `llama-server`: SHA-256 `234b05b2138264f8fb263c3205e85f4c290e8afe5067e280a4f6f90cdac5696b`;
- CUDA backend: SHA-256 `fbe27c15253195c10559d98c6ba9c6d476a65d2bbf0240307b4a46d8aa17cefb`;
- llama.cpp: `b10434`, commit `7e4c0a96880dae4fc4268ad441f8a6446bd5460a`.

The earlier merged tokenizer-capability audit is also bound:

- job receipt SHA-256 `8644d0b02e125e4cdf75ca0ed913a2fbf0e818ebf358a9ace15d7be7fcabfbc4`;
- probe SHA-256 `700aabce43e6b834bae4335855149d3b9de7d4b0861cf07e0a49ce9d113020e1`.

## Adverse predecessor preservation

PR #1190 remains an adverse result for the un-repaired merged preflight. The successor validator remeasures its result JSON, requires the exact `SHA256SUMS` hash `37de79e648b0d2a8a5a84c5811f4cdff950c7c6bd4bc4f893ed17a768edc64f5`, parses that manifest, and checks every listed file. Nothing in this lane turns the earlier failed run into a success.

## Artifact inventory

- `INPUT_GATE_RECEIPT_V1.json` — repaired-input and prior-tokenizer-audit bindings.
- `SUCCESSOR_INPUT_BINDINGS_V1.json` — finalized public/private/runtime bindings.
- `FINALIZATION_RECEIPT_V1.json` — pre-submission gate receipt.
- `TOKENIZATION_RECEIPT_V1.json` — raw/private ledger and repeat-tokenization bindings.
- `PROTECTED_PROMPT_FIT_RECEIPT_V1.json` — body-free per-record hash/status/token-count receipt.
- `SUCCESSOR_JOB_RECEIPT_V1.json` — bounded job result.
- `BODY_FREE_EXPORT_MANIFEST_V1.json` — export/private-custody manifest.
- `CLEANUP_V1.json` — process/listener cleanup receipt.
- `SACCT_V1.txt` and `TERMINAL_V1.txt` — exact scheduler and completion evidence.
- `TOKEN_LEDGER_AUDIT_AGGREGATE_V2.json` — body-free static token aggregate.
- `SCHEDULER_RUNTIME_RECEIPT_V2.json` — exact one-job runtime receipt.
- `SUCCESSOR_RESULT_V2.json` — bounded successor result.
- `validate_protected_prompt_fit_successor_v2.py` — repository-only validator.
- `HANDOFF_V2.md` — bounded reviewer handoff.
- `SHA256SUMS` — lane integrity manifest.

## Explicit exclusions

This lane contains no protected row source, Parquet, task or prompt body, masked or recovered packet body, raw 196 KB ledger, 4.6 MB integer-token-ID audit, GGUF, generated completion, evaluator/rubric/gold/outcome payload, external API response, credential, manuscript edit, or PDF. The protected job invoked no generation, official task execution, evaluation, external API, credential, pytest, or CI.

## Validation

Run from repository root:

```bash
rtk python3 development/p1-scienceagentbench-protected-prompt-fit-successor-v2-2026-08-24/validate_protected_prompt_fit_successor_v2.py
rtk proxy sh -c 'cd development/p1-scienceagentbench-protected-prompt-fit-successor-v2-2026-08-24 && sha256sum -c SHA256SUMS'
rtk git diff --check origin/main...HEAD
```

The validator reads only public repository artifacts. It never opens any private row, prompt, ledger, token-ID audit, model, evaluator, or outcome payload.

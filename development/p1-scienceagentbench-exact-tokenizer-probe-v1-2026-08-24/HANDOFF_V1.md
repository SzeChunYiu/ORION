# P1 ScienceAgentBench exact GGUF tokenizer probe V1 - handoff

## Review verdict

**PASS, narrowly scoped:** LUNARC job `3537594` completed `0:0` and returned
repeatable exact token-ID arrays across three repeats for each of eight records
derived from four invented prompts and two explicit modes.

Exact terminal:

```text
P1_SAB_EXACT_GGUF_TOKENIZER_PROBE_PASS__JOB_3537594__NO_GENERATION__NO_PROTECTED_INPUTS__COST_CANNOT_CHECK
```

## Mandatory mode binding

For the completion-equivalent path, require all of:

```json
{"route":"POST /tokenize","add_special":true,"parse_special":true,"repeatability_check_required":true}
```

Do not omit or infer these flags. The invented literal `<|im_start|>` marker
produced 13 tokens in `true,true` mode and 16 in `false,false`; its arrays were
different. A production ledger must hash the exact UTF-8 prompt/request, repeat
tokenization three times, require identical integer arrays, and record the IDs,
count, and response hashes.

## Claim boundary

This result proves only repeatability of the exact frozen GGUF tokenizer route
on the retained invented probes. It does not tokenize or establish fit for a
protected prompt, authorize production, invoke generation, evaluate an answer,
or create benchmark/outcome authority.

- protected prompt fit: `CANNOT_CHECK_NO_PROTECTED_PROMPT_OPENED_OR_TOKENIZED`;
- production admissibility: `CANNOT_CHECK`;
- generation correctness: `CANNOT_CHECK_NOT_INVOKED`;
- official tasks/outcomes opened: `0 / 0`;
- scientific-authority delta: `NONE`;
- billed USD: `CANNOT_CHECK_OWNER_AUTHORITATIVE_ALLOCATION_COST_CONVERSION_UNAVAILABLE`.

## Reviewer commands

Run from the repository root:

```bash
rtk python -m py_compile development/p1-scienceagentbench-exact-tokenizer-probe-v1-2026-08-24/validate_exact_tokenizer_probe_v1.py
rtk python development/p1-scienceagentbench-exact-tokenizer-probe-v1-2026-08-24/validate_exact_tokenizer_probe_v1.py
rtk proxy sh -c 'cd development/p1-scienceagentbench-exact-tokenizer-probe-v1-2026-08-24 && sha256sum -c SHA256SUMS'
rtk git diff --check origin/main...HEAD
```

The validator is body-safe and uses only this additive lane. Do not run pytest,
CI, manuscript, PDF, generation, evaluator, protected-data, credential, or
external-API workflows. Review this PR without merging automatically.

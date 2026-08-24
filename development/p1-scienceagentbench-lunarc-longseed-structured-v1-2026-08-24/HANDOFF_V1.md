# P1 long-seed structured-output handoff

## Exact disposition

Job `3534486` passed the frozen structured-output diagnostic. It does not repair
or promote adverse job `3534250` or PR #1150's exact long-prompt result.

- Frozen prompt: 91,026 bytes; SHA-256
  `b55831c8657f3a1f5556833204b5aff79fe84e58f170edaa228909401e222f72`.
- Frozen schema: 646 bytes; SHA-256
  `7b9ffda6c9daa1f39a1350959590112c5c663c6373a81e1e3fbffa23f0649498`.
- Only added request field: `json_schema`.
- Disclosed operational isolation: port `11475` instead of `11474`, with a
  separate remote code/run directory; runtime binaries and server geometry were
  unchanged.
- Sampling: temperature `0.8`, cap `128`, order
  `101,202,101,202,101,202`, `cache_prompt=false`, context `32768`.
- Seed 101: 83 generated tokens; token-array SHA-256
  `d4b5a8d85f7abe290b93451b00f0e05c920800e87874922f651c174bf336c290`;
  content SHA-256
  `80531e83ab9eedd5279ab888c56668e96a6cc849df5ae441f54631ef25abd9a9`.
- Seed 202: 70 generated tokens; token-array SHA-256
  `1de431e98133302a4b2c8417cad20679ec4334250fa9abf54e1e8d61196636d3`;
  content SHA-256
  `a07687a2850e7a40af74dc3893e16900e977ce7954c83048c06a29ece9ae7a81`.
- PASS: raw JSON parse, exact keys/schema/markers, allowed choice, same-seed
  token/content identity, and between-seed token/content sensitivity.
- PASS: `cache_n=[0,0,0,0,0,0]`, constant `prompt_n=27855` matching job
  `3534250`, and no truncation.
- **BOUNDARY:** all six choices were `iris`; parsed objects were identical. The
  between-seed difference was formatting. Semantic-choice sensitivity is
  `NOT_ESTABLISHED`.

## Runtime and accounting

- Model: 18,556,689,568 bytes; SHA-256
  `fadc3e5f8d42bf7e894a785b05082e47daee4df26680389817e2093056f088ad`.
- `llama-server` b10434 / commit
  `7e4c0a96880dae4fc4268ad441f8a6446bd5460a`, executable SHA-256
  `234b05b2138264f8fb263c3205e85f4c290e8afe5067e280a4f6f90cdac5696b`.
- CUDA v13 backend SHA-256
  `fbe27c15253195c10559d98c6ba9c6d476a65d2bbf0240307b4a46d8aa17cefb`.
- SLURM: `COMPLETED`, exit `0:0`, 98 allocated seconds on one A40.
- Sampled: 72.336 GPU-s and 5.545619033333338 Wh.
- Billed USD: `null` /
  `CANNOT_CHECK_OWNER_AUTHORITATIVE_ALLOCATION_COST_CONVERSION_UNAVAILABLE`.
- Shared remote root: removed. The receipt proves only file/byte inventory and
  root absence; job/process absence is `CANNOT_CHECK_FROM_RETAINED_CLEANUP_RECEIPT`.
- Raw `ENVIRONMENT.txt` and `NVIDIA_SMI_AFTER.txt` bytes, including their
  vendor-formatted trailing spaces, are unchanged and hash-bound. A packet-local
  `.gitattributes` exempts only those two raw paths from whitespace diagnostics.
- The historical remote manifest is runtime-stage coverage and intentionally
  excludes the later local `SACCT_V1.txt`. Its exact SACCT SHA-256
  `c3e1c8694ecf5a0f19c8699d46afa0a2c6836725065dea67e065ef65967d1770`
  is independently bound by the top receipt and packet `SHA256SUMS`; the
  historical remote manifest remains unchanged.

## Claim boundary

The pass is a bounded structured-output mechanism witness only. It does not
establish semantic seed sensitivity, protected-task quality, production
admissibility, superiority, manuscript, publication, or official execution.
Jobs `3534250` and `3534486` are non-composable. Production replay remains
**BLOCKED**.

Scientific authority delta: `NONE`.

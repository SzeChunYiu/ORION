# P1 long-seed mechanism handoff

## Exact disposition

Job `3534250` is a result-bearing **ADVERSE** synthetic mechanism diagnostic.
It does not repair or promote PR #1150's exact long-prompt adverse result.

- Frozen prompt: 91,026 bytes; SHA-256
  `b55831c8657f3a1f5556833204b5aff79fe84e58f170edaa228909401e222f72`.
- Sampling: temperature `0.8`, cap `128`, order
  `101,202,101,202,101,202`, `cache_prompt=false`, context `32768`.
- Seed 101: 74 generated tokens; token-array SHA-256
  `4a6e4f09f2e9a04f5355429f7b36daed6cafd2281c91625a05111188ee21e06d`;
  content SHA-256
  `4b0d436abec421a0efdf07a26f5d63b53ad86e639902bb4cfc81a8a753112812`.
- Seed 202: 72 generated tokens; token-array SHA-256
  `a345d234e8786268d9b703c0cb0666fd18b35e0fbb646979322f00b395e3d578`;
  content SHA-256
  `7941bb446e836de0bc340678b29f0995cb41d873426d140a3c575776306202fc`.
- PASS: same-seed token/content identity and between-seed token/content
  sensitivity.
- PASS: `cache_n=[0,0,0,0,0,0]`, constant `prompt_n=27855`, no truncation,
  and all markers complete/in order.
- **ADVERSE:** raw content did not directly parse as JSON because of extra prefix
  text; all recorded choices are `null`. No embedded-object reparsing is used.

## Runtime and accounting

- Model: 18,556,689,568 bytes; SHA-256
  `fadc3e5f8d42bf7e894a785b05082e47daee4df26680389817e2093056f088ad`.
- `llama-server` b10434 / commit
  `7e4c0a96880dae4fc4268ad441f8a6446bd5460a`, executable SHA-256
  `234b05b2138264f8fb263c3205e85f4c290e8afe5067e280a4f6f90cdac5696b`.
- CUDA v13 backend SHA-256
  `fbe27c15253195c10559d98c6ba9c6d476a65d2bbf0240307b4a46d8aa17cefb`.
- SLURM: `FAILED` only because the frozen adverse gate returned `2:0`;
  119 allocated seconds on one A40.
- Sampled: 72.379 GPU-s and 5.518933734722219 Wh.
- Billed USD: `null` /
  `CANNOT_CHECK_OWNER_AUTHORITATIVE_ALLOCATION_COST_CONVERSION_UNAVAILABLE`.
- Shared remote root: removed. The receipt proves only file/byte inventory and
  root absence; job/process absence is `CANNOT_CHECK_FROM_RETAINED_CLEANUP_RECEIPT`.

## Claim boundary

This packet is non-composable with the exact PR #1150 replay and with job
`3534486`. It establishes no protected-task quality, production admissibility,
superiority, manuscript, publication, or official-execution claim. Production
replay remains **BLOCKED**.

Scientific authority delta: `NONE`.

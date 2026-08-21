# Results

Protected terminal: `P13A_RCS_SAFETY_COST_SUPERIORITY_SUPPORTED`.

| arm | unsafe reuse | verified correctness | unnecessary reopen | mean cost |
|---|---:|---:|---:|---:|
| **RCS** | **0.0000** | **0.9807** | **0.0000** | **2.8747** |
| confidence only | 0.2156 | 0.9657 | lower than RCS | 1.8582 |
| provenance only | 0.3962 | 0.9248 | 0 | 1.0000 |
| unqualified compact | 0.3962 | 0.9248 | 0 | 1.0000 |
| always raw | 0.0000 | 0.9513 | 0.5744 | 5.7319 |

RCS emits `CANNOT_CHECK` for all **237** unsupported/nonrecoverable cases and no other protected case. It eliminates structural unsafe reuse without adopting always-reopen behavior. Mean resource cost is approximately **49.8% lower** than always raw. Two fresh executions are byte-identical with SHA-256 `ea4006981e0c5027a56789014dd723059420f603e071e81990a903986f6e8d1f`.

## Why confidence fails

The omitted coordinate is biased within a family, so a MAP decoder can be highly accurate and exceed the 0.80 confidence threshold. But high expected accuracy does not make an unsupported equivalence class sufficient. Confidence asks how often an output is right under a distribution; RCS asks whether state retains distinctions required by a responsibility.

## Why provenance fails

Every compact state has valid lineage. Provenance verifies origin but says nothing about whether `m` or `r` was retained. Provenance-only reuse is structurally unsafe on 39.62% of protected episodes.

## Why always raw is not the answer

Always reopening prevents unsafe compact reuse but pays roughly twice the mean RCS cost and unnecessarily reopens supported cases on 57.44% of episodes. RCS occupies the desired interior safety–cost point.
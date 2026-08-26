# ORION-19 protected Qwen #618 cross-size analysis recovery protocol V1

**Programme:** #977  
**Source PR:** #618, branch `shadow/p9-p10-structural-scaling-research-20260820`  
**Source protected run:** GitHub Actions `32346652275`  
**Recovery state:** `FROZEN_BEFORE_RECOVERED_ANALYSIS`  
**Scientific rule:** recover immutable protected evidence; do not rerun or retune Qwen inference.

## Why recovery is admissible

All three prospectively frozen model-evaluation jobs completed successfully in run `32346652275`:

- Qwen2.5 0.5B Q4_K_M;
- Qwen2.5 1.5B Q4_K_M;
- Qwen2.5 3B Q4_K_M.

Each job completed the frozen primary cells and the ORDER/SYMBOL hostile-control cells and emitted `RUN_COMPLETE_PENDING_CROSS_SIZE_ANALYSIS`.

The downstream `analyze` job failed **before reading any model JSON**. `actions/download-artifact@v4` downloaded the three expected artifacts into `inputs/` using `merge-multiple: true`, but the artifact ZIPs preserve their original path `home/runner/work/ORION/ORION/out/p9-llm-<scale>.json`. The workflow then invoked the analyzer with nonexistent flat paths such as `inputs/p9-llm-0.5B.json`, producing `FileNotFoundError` at the first `Path.read_text()` call.

This is an artifact-layout integration defect, not a failed scientific gate.

## Frozen source artifacts

Source run `32346652275` artifact identities/digests recorded by GitHub Actions:

- `p9-llm-0.5B-80029536b6fc8227ceb21f2160ed2c17fb10c160`, artifact ID `9404357527`, expected SHA-256 `aa592c1a3c4875e65322bfd91439891e5dcb9cba5c73ff0680fd09b415d22ba9`;
- `p9-llm-1.5B-80029536b6fc8227ceb21f2160ed2c17fb10c160`, artifact ID `9405331369`, expected SHA-256 `958ac6685eadafa74c560e597a3720701256ee615fb85cc664749a5c1c6239f8`;
- `p9-llm-3B-80029536b6fc8227ceb21f2160ed2c17fb10c160`, artifact ID `9405806040`, expected SHA-256 `99460a54ad730ab543ea4159d19eb4a80e5debce855f4becd96f1098221d1765`.

The archived JSON paths are respectively:

- `.../out/p9-llm-0.5B.json`;
- `.../out/p9-llm-1.5B.json`;
- `.../out/p9-llm-3B.json`.

## Analyzer authority

The scientific analyzer is the exact logic from PR #618 file

`research/extensions/p9-p10-structural-scaling/analyze_p9_llm_gguf_v1.py`

at source branch blob SHA `29fbbd6af9c35f405d6f0a0ab80ae9cfe9265639`.

It freezes:

- primary budget `32`;
- budgets `(8,32,96)`;
- target qualities `(0.50,0.70,0.85)`;
- scales `(0.5B,1.5B,3B)`;
- representations `R1_SAME_INFO` and `R2_STRUCTURED_STATE`;
- domain-block bootstrap seed `914031`;
- `10,000` bootstrap draws;
- exactly `192` primary rows per representation/budget/model cell;
- exactly `96` rows per ORDER/SYMBOL hostile-control cell/model;
- positive delta at every size;
- largest-model domain-block bootstrap lower bound > 0;
- >=60% nonnegative largest-model domain deltas;
- at least one observed smaller-structured/larger-same-information substitution;
- all frozen hostile controls green.

The producer schema is `ORION-19.LLMGGUFServerRuns.v1`, whose frozen runner explicitly writes `model_scale`; the analyzer consumes the same field. No schema reinterpretation is needed.

## Sole allowed recovery transformation

After downloading the exact source artifacts, recursively locate **exactly one** file named:

- `p9-llm-0.5B.json`;
- `p9-llm-1.5B.json`;
- `p9-llm-3B.json`.

Copy those bytes into a flat recovery directory using the same basenames, verify there is exactly one match per scale, then run the vendored source analyzer unchanged in scientific logic.

No JSON content may be edited. No failed/missing row may be regenerated. No Qwen inference may be rerun. No threshold, seed, target, model, prompt, budget, hostile-control rule or terminal may change.

## Recovery checks

Before analysis require each JSON:

- schema `ORION-19.LLMGGUFServerRuns.v1`;
- terminal `RUN_COMPLETE_PENDING_CROSS_SIZE_ANALYSIS`;
- expected `model_scale`;
- `equivalence_failures == 0`;
- zero `leakage_failures`;
- identical cross-size `item_manifest_sha256`;
- identical cross-size `prompt_sha256`.

After analysis execute a second analysis over the same three bytes and require byte-identical output.

## Scientific authority

The recovered terminal is whatever the frozen analyzer emits:

- `LLM_STRUCTURE_SCALING_FRONTIER_SUPPORTED`, or
- `LLM_STRUCTURE_SCALING_FRONTIER_NOT_SUPPORTED`.

A positive result remains scoped to the exact Qwen2.5 Q4_K_M 0.5B/1.5B/3B family and the frozen procedural D1 population. It does not authorize cross-family/full-precision universal scaling claims.

A negative result remains authoritative. Recovery may not open a new threshold/search after outcome access.

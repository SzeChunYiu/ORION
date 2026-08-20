# P9 LLM GGUF Hostile-Control Amendment V1

Status: **FROZEN BEFORE ANY LLM OUTCOME**

Frozen: 2026-08-20

The first GGUF workflow attempt failed before model download/inference because the review branch lacked the already-verified P9 D1 generator module. Therefore no model response or outcome was observed. This amendment strengthens the execution controls before the first successful inference.

It does not change `P9_LLM_STRUCTURE_SCALING_PROTOCOL_V1.md` or its primary success gate.

## 1. Exact generator provenance

The exact D1 generator blobs from the verified P9 integration branch are content-grafted into the structural-scaling branch:

- `src/orion/study/p9/d1.py`, Git blob `3d3a996404fb348f6722faa1efe5ea7132a15f65`;
- `src/orion/study/p9/d1_data_runtime.py`, Git blob `ac5b72268192e9682e5a8502444d0d66a267f2f8`.

The runtime adapter is imported before generation so the prospectively corrected dependency-mutation semantics are active.

## 2. Persistent inference runtime

Use pinned llama.cpp build tag `b6635` (resolved by the first mechanical build to commit `b77e6c18e1a6fac5705ed95f03af5436d67484c1`). A single `llama-server` process loads each exact model once. Requests use the same manual Qwen chat prompt content, temperature 0, seed 914101, context 4096, and frozen generated-token caps `{8,32,96}`.

This changes runtime efficiency only, not model bytes, prompts, items, labels, budgets or scoring.

## 3. Token-length hostile control

For every item, tokenize the complete R1 and R2 prompts with the loaded model tokenizer before inference.

If R2 is shorter than R1, append deterministic target-independent `NEUTRAL_PADDING` text to R2 until its complete prompt token count is at least R1's count. Stop at the first such padding length. R1 is never shortened and no task fact is removed.

Primary R2 evaluation uses this non-shorter structured rendering. Therefore a positive R2-R1 primary effect cannot be attributed to R2 receiving a shorter prompt. Record both token counts and padding amount for every item. Any prompt reaching 4096 tokens invalidates the cell.

The padding constant is identical across items and carries no label/domain/mutation information.

## 4. Leakage scanner

Before inference, both renderings must be free of:

- exact evaluator labels `ALIGNED`, `OBSTRUCTION`, `UNRESOLVED`;
- domain identifiers `numerical_methods`, `graph_algorithms`, `transactional_workflows`;
- mutation-count or evaluator-gold metadata.

A failure yields `INVALID_RENDERER_LEAKAGE` before model scoring.

## 5. Frozen order control

A hash-selected 48-item control set contains the 16 lexicographically smallest item IDs within each of the three domains.

At budget 32, for every model size:

- R1 is reordered only at the **whole-coordinate-group** level. Every line belonging to one coordinate stays in its original internal order, so dependency-edge endpoint direction and other sequence semantics are unchanged;
- R2 mapping-key insertion order is deterministically reversed, but all sequence/list values are kept in their original internal order;
- the implementation checks that the R1 serialized fact multiset is identical and the reordered R2 Python semantic object compares equal to the original typed object before inference;
- R2 is again padded if needed so it is not shorter than its paired R1 control prompt.

A pre-outcome hostile implementation review caught and rejected the simpler idea of reversing every R1 line / every R2 list, because that would reverse dependency-edge endpoints and therefore change the task. No model outcome existed when this semantics-preserving correction was frozen.

Order control passes for a model if the R2-R1 accuracy difference remains non-negative. The primary claim additionally requires all three model-size order controls to pass. Raw control accuracies are reported regardless of sign.

## 6. Frozen symbol-renaming control

On the same 48 items at budget 32, all method/domain-content string values are replaced by deterministic opaque identifiers using a one-to-one per-item map. Structural coordinate keys, schema identifiers, and `unknown_coordinates` coordinate references remain unchanged; equality/difference and unknown-location structure are preserved.

R1 and R2 are generated from the same renamed typed object, preserving exact same-information equivalence. R2 is padded if shorter.

Symbol control passes for a model if R2-R1 accuracy difference remains non-negative. All three model-size controls must pass for the full scaling terminal.

This control tests whether the representation advantage survives removal of familiar semantic surface values; it is not used to tune the primary prompt.

## 7. Full terminal additions

`LLM_STRUCTURE_SCALING_FRONTIER_SUPPORTED` now additionally requires:

- zero renderer-equivalence failures;
- zero leakage failures;
- R2 complete prompt token count >= R1 on every primary pair;
- every prompt below context limit;
- non-negative R2-R1 difference under the frozen order control for all three sizes;
- non-negative R2-R1 difference under the frozen symbol control for all three sizes.

If the primary effect is positive but one hostile control fails, preserve the exact measured effect under a bounded negative/partial terminal; do not retune the control.

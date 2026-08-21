# P9 LLM GGUF Execution Amendment V1

Status: **FROZEN BEFORE GGUF LLM OUTCOMES**

Frozen: 2026-08-20

This amendment instantiates `P9_LLM_STRUCTURE_SCALING_PROTOCOL_V1.md` on one official open-weight family without changing its scientific success gate.

## Model family

Primary family: Qwen2.5 Instruct, official Qwen GGUF repositories, quantization `Q4_K_M`.

Exact model byte identities:

| Scale | Repository | File | SHA-256 |
|---|---|---|---|
| 0.5B | `Qwen/Qwen2.5-0.5B-Instruct-GGUF` | `qwen2.5-0.5b-instruct-q4_k_m.gguf` | `74a4da8c9fdbcd15bd1f6d01d621410d31c6fc00986f5eb687824e7b93d7a9db` |
| 1.5B | `Qwen/Qwen2.5-1.5B-Instruct-GGUF` | `qwen2.5-1.5b-instruct-q4_k_m.gguf` | `6a1a2eb6d15622bf3c96857206351ba97e1af16c30d7a74ee38970e434e9407e` |
| 3B | `Qwen/Qwen2.5-3B-Instruct-GGUF` | `qwen2.5-3b-instruct-q4_k_m.gguf` | `626b4a6678b86442240e33df819e00132d3ba7dddfe1cdc4fbb18e0a9615c62d` |

The downloaded file hash is checked before inference. Any mismatch yields `INVALID_MODEL_IDENTITY` and no scientific result.

## Evaluation population

Use a fresh zero-shot evaluation manifest generated before model responses from the existing deterministic P9 D1 world generator. It contains three domain blocks:

- numerical methods;
- graph algorithms;
- transactional workflows.

For each domain, generate 16 base indices with the four frozen variants `aligned`, `single-mutation`, `unresolved`, and `double-mutation`, for 64 items/domain and 192 total items. The exact generator seed is `p9-llm-structure-scaling-gguf-v1`. Domain identity and gold labels remain evaluator-only and are never rendered to the model.

This is a new LLM evaluation population; it is not relabeled historical D1 protected test evidence.

## Representation arms

Primary same-information contrast:

- `R1_SAME_INFO`: deterministic flattened serialization of the exact typed fact multiset;
- `R2_TYPED_STATE`: structured JSON object with the same typed facts and explicit slots/relations.

A generator-side equivalence receipt must prove that both renderers decode to the same canonical fact multiset for every included item. Any failure invalidates that pair before model execution.

## Prompt

System instruction is frozen:

`Classify the relationship between LEFT and RIGHT as exactly one label: ALIGNED, OBSTRUCTION, or UNRESOLVED. Return only the label.`

The user message contains only the chosen R1 or R2 rendering. No examples, chain-of-thought request, domain name, mutation count, gold label, or hidden evaluator metadata is supplied.

## Inference budgets

Frozen generated-token caps: `{8, 32, 96}`. Temperature `0`. Top-p `1`. Seed `914101` where supported. Context window at least 4096 tokens. Each model/representation/item/budget cell is evaluated independently.

The primary budget for the pooled/domain-block effect is `32` generated tokens. Exact task success requires parsing one of the three labels after whitespace/punctuation normalization; all other outputs are incorrect.

## Target qualities

Frozen target qualities: `{0.50, 0.70, 0.85}` as allowed by the parent protocol.

## Primary gate

Unchanged from the parent protocol and runtime-gated analysis contract:

1. pooled R2-R1 effect > 0 at the primary budget for every model size;
2. largest-model domain-block bootstrap lower 95% bound > 0;
3. >=60% domain blocks non-negative at that cell;
4. at least one target quality where a strictly smaller R2 model meets/exceeds a larger R1 model at the same budget;
5. equivalence, token/context, symbol/order and leakage controls pass.

Test-time compute substitution is separately earned only if identical model weights reach a frozen quality at a strictly smaller observed token cap under R2.

## Quantization boundary

A positive result supports a scaling-frontier claim for these exact quantized Qwen2.5 checkpoints. It does not establish the same effect for full-precision Qwen weights or arbitrary LLM families. A second family remains replication.

## Required receipts

The run archive must include model file SHA-256, model repository/file names, llama.cpp identity, exact prompt hash, item manifest digest, canonical-fact equivalence results, raw response text, parsed label, generated-token accounting, per-item correctness, wall time, and final analysis terminal.

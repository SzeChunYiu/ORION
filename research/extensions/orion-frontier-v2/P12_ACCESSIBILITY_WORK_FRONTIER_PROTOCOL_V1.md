# P12 Accessibility-Work Frontier — Protocol V1

Status: PROSPECTIVE / FROZEN BEFORE P12 OUTCOMES
Frozen: 2026-08-20

## Motivation

Predictive V-information already measures information usable by a restricted predictive family and explicitly permits computation to create usable information. P12 therefore does **not** redefine that concept.

P12 asks a different operational question:

> What resources must be spent, and where must they be spent, to turn an available state into a state that a specified downstream system can successfully exploit?

## Resource vector

Do not collapse heterogeneous costs into one scalar by default. Every system produces an accessibility-work vector

`A = (C_compile, M_state, C_model, C_infer, C_tool, L_latency)`

where:
- `C_compile`: preprocessing/state-construction operations or measured compute;
- `M_state`: materialized state bytes/tokens/features;
- `C_model`: fixed model capacity descriptor (parameters, interaction degree, hypothesis family);
- `C_infer`: downstream tokens/search nodes/decoder operations;
- `C_tool`: verifier/tool/API calls;
- `L_latency`: end-to-end latency, descriptive unless hardware is fixed.

A scalar cost is allowed only via a scalarization frozen before protected outcomes.

## Accessibility-work frontier

For target quality q, compiler family C, downstream family V and task distribution D, define the empirical frontier as the nondominated set of systems achieving quality >=q in the resource vector above.

A representation/compiler is better only if it expands this Pareto set under matched scientific information and identity controls.

## Compiler classes

P12 distinguishes:
1. `DIRECT_SPECIALIZER`: may perform task computation during compilation; all such work is charged to `C_compile`.
2. `COMPONENT_COMPILER`: may expose certified task-relevant components but is prohibited from emitting the final answer or deterministic equivalent; P11B is the calibration example.
3. `LOSSLESS_RECODER`: bijective/information-equivalent transform; #618 relational/obfuscation experiments calibrate this class.
4. `LOSSY_SUFFICIENT_COMPRESSOR`: may drop information only with a task-specific sufficiency certificate; P14 studies when that certificate fails under task escalation.
5. `RECOVERABLE_COMPRESSOR`: stores compressed accessible state plus a raw/archive route from which discarded coordinates can be reconstructed or recompiled at charged future cost.

## Controlled calibration data

Required first calibration combines already-frozen results without changing them:
- #618 information-equivalent relational accessibility / interaction-degree results;
- P11 fixed-universal vs direct query compilation;
- P11B fixed-universal vs no-answer-laundering component compilation;
- #618 predictive-state compression as explicitly non-same-information nuisance-state evidence.

P12 may compute a joint resource table from these artifacts but may not invent a cross-domain scalar score after seeing values.

## Real-system escalation

### LLM
Once #618 Qwen scaling results exist, add exact model bytes, input/output tokens and representation-construction work. Compare spending budget on state transformation versus model scale/inference tokens.

### Lean
Once #618 native-state results exist, account state extraction/summary work, feature/state bytes, learner/search cost and Lean verifier calls.

## Protected claims

A controlled terminal `CONTROLLED_ACCESSIBILITY_WORK_FRONTIER_ESTABLISHED` requires:
- at least three compiler classes represented;
- information/sufficiency status explicit per point;
- all compiler work charged rather than treated as free;
- at least one strict Pareto reversal where a representation wins in one resource regime but loses in another;
- no post-outcome scalarization.

A stronger terminal `CROSS_DOMAIN_ACCESSIBILITY_WORK_FRONTIER_SUPPORTED` additionally requires at least two real-system domains (one must be LLM or Lean) with prospectively matched resource accounting.

## Anti-cheating boundary

Because deterministic tasks allow a compiler to compute the final answer, P12 never calls low downstream cost evidence of a representation advantage unless compiler work is included. Direct specialization is a valid compute-placement strategy, not free information.

P11B-like component compilers are the preferred evidence when the scientific question is specifically state construction rather than algorithm relocation.

## High claim ceiling

If cross-domain gates pass:

> The cost of reasoning is not localized to the model or search procedure. It lies on an accessibility-work frontier spanning state construction, memory, model capacity, inference and verification; systems can move work among these resources, and the optimal placement depends on task and query regime.

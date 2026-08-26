# ORION-19 causal intervention diagnostic result receipt V1

**Run:** GitHub Actions `32657074299`  
**Artifact:** `p9-causal-diagnostic-v1`, artifact ID `9498230317`  
**Artifact ZIP SHA-256:** `2c6195ca59a52822e71d1deda6a6a83989fb8d9261561ef0b826bfe19512efc7`  
**Primary terminal:** `P9_CAUSAL_DIAGNOSTIC_V1_SUPPORTED`  
**Independent terminal:** `P9_CAUSAL_DIAGNOSTIC_SECOND_INDEPENDENT_CHECKER_GREEN`  
**Agreement:** `P9_CAUSAL_DIAGNOSTIC_TWO_IMPLEMENTATIONS_AGREE`

## Exact binding

- protocol SHA-256: `267df46aff7bd5502180524cd96f82b7951a2ae4c1d567e3b53bea6ce3f86015`
- primary receipt SHA-256: `2408d028de6ecb4f174433fba8291de84c4af5b6e5ff71870536c38e7f0c9313`
- independent receipt SHA-256: `4f6f7d7a3f230523966b8eb1a78c716ebb18d86099ae5cf5169d9e6c20f531d5`
- deterministic primary replay: GREEN
- independent decision reproduction: GREEN

## Protected diagnostic result

Five task families were frozen across two qualitatively distinct domains. The diagnostic selects among `INFORMATION`, `ACCESSIBILITY`, and `COMPUTATION` from development/probe intervention responses using a prospectively fixed quality-target and lowest-cost rule. Protected causal gold is recomputed independently from held-out intervention outcomes.

Aggregate protected outcomes:

- diagnostic accuracy: `0.8` (`4/5` task families);
- generic `UNCERTAINTY_ESCALATE_COMPUTE` accuracy: `0.2` (`1/5`);
- exact executable-domain accuracy: `1.0` (`3/3`);
- real-digits diagnostic accuracy: `0.5` (`1/2`);
- diagnostic false compute-escalation count: `0`;
- generic false compute-escalation count: `4`;
- mean registered intervention-cost regret: `0.0`;
- every prediction whose protected causal gold was actionable reached the frozen protected quality target.

### Stable protected diagnoses

- digits missing-information task `D-I`: `INFORMATION`; protected restored-information accuracy `0.955555...` at target `0.95`;
- executable missing-information task `B-I`: `INFORMATION`; protected accuracy `1.0` versus `0.5` for access/compute without the missing bit;
- executable accessibility task `B-A`: `ACCESSIBILITY`; both accessibility repair and explicit computation reach `1.0`, with the frozen lower-cost rule selecting accessibility;
- executable computation task `B-C`: `COMPUTATION`; protected computation accuracy `1.0` versus `0.05` for the non-computational interventions.

### Preserved instability / CANNOT_CHECK cell

The real-digits accessibility task `D-A` is a binding negative for transfer stability. On the probe split, inverse representation repair reaches `0.9721448`, above the frozen `0.965` target, so the diagnostic predicts `ACCESSIBILITY`. On the protected split, the same repair reaches only `0.9555556`, below target; no intervention meets the frozen target and protected causal gold is therefore `CANNOT_CHECK`.

This cell is not retuned away. It demonstrates that an intervention can be causally effective while a specific prospectively chosen deployment threshold fails to transport from probe to protected data.

## Scientific disposition

ORION-19 now has a bounded cross-domain causal diagnostic result rather than only a representation-effect result. The procedure distinguishes information, accessibility and computation failures substantially better than a generic compute-escalation heuristic, eliminates false compute escalation in the five protected families, and has zero intervention-cost regret on the actionable protected cells.

The result is deliberately conditional. It does not establish a universal LLM diagnostic, and the `D-A` protected `CANNOT_CHECK` plus the existing Qwen scaling negative prohibit a universal representation-repair or monotone scaling law.

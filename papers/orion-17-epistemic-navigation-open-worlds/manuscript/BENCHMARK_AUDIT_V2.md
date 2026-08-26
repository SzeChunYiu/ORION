# ORION-17 benchmark audit V2 — evolving epistemic topology

**Candidate:** Epistemic Navigation in Open Worlds  
**Date:** 2026-08-17  
**Authority:** frozen benchmark-contract seed; no candidate-agent outcome

## 1. Discriminator being frozen

ORION-17 survives only if changing the representation/objective chart yields a prospectively identified benefit beyond:

- ORION-11 responsibility-triggered reformulation;
- ORION-12 route governance and fail-closed stopping;
- fixed-graph navigation;
- ordinary replanning/world-model revision;
- resource-matched exploratory policies.

The benchmark must also punish gratuitous reframing and transfer beyond literature retrieval.

## 2. Frozen V1 case set

`benchmark/instances_v1.jsonl` contains eight cases:

| ID | Family | Domain | Gold terminal | Purpose |
|---|---|---|---|---|
| `ORION-17-HIDDEN-BRANCH-001` | hidden useful branch | retrieval | `TASK_STOP` after obligations | catches premature stop on a low-priority frontier |
| `ORION-17-UNKNOWN-COVERAGE-001` | unknown coverage | retrieval | `CANNOT_CHECK` | prevents unknown denominator from becoming completeness |
| `ORION-17-CENSORED-ROUTE-001` | censored route | retrieval | `CANNOT_CHECK` | separates local route stop from global task closure |
| `ORION-17-REDUNDANT-DIVERSITY-001` | deceptive route diversity | retrieval | `ROUTE_STOP` | withholds independence credit from nominally distinct shared routes |
| `ORION-17-DEAD-END-REVISIT-001` | dead-end/revisit | graph navigation | `TASK_STOP` after recovery | tests revisit value rather than blind looping |
| `ORION-17-TOPOLOGY-REFRAME-001` | required topology change | diagnosis | `REFRAME` | fixed chart cannot reach the goal; factorized chart can |
| `ORION-17-TOPOLOGY-NEGATIVE-001` | unnecessary reframe | diagnosis | `TASK_STOP` without reframe | negative control where evidence acquisition is sufficient and reframe is harmful |
| `ORION-17-NONRETRIEVAL-EXPERIMENT-001` | required topology change | experimental design | `REFRAME` | mandatory non-retrieval transfer with dependent-conclusion reopening |

## 3. Reference terminal oracle

The executable oracle is intentionally narrow:

1. a case marked as requiring topology change returns `REFRAME`;
2. unresolved/censored coverage returns `CANNOT_CHECK`;
3. deceptive nominal route diversity permits `ROUTE_STOP` but not task closure;
4. otherwise the case may reach `TASK_STOP` only after its listed obligations are discharged.

The oracle verifies contract consistency. It is not a navigation agent, does not see hidden labels in a real run and supplies no performance estimate.

## 4. Suite-level anti-cheating constraints

The aggregate runner fails unless the manifest contains:

- all seven required case families;
- `TASK_STOP`, `ROUTE_STOP`, `REFRAME` and `CANNOT_CHECK` terminals;
- at least one harmful/unnecessary-reframe negative control;
- at least one explicitly marked non-retrieval transfer case;
- unique case identities and an executed expected-terminal match.

A policy that always reframes, always stops or always returns `CANNOT_CHECK` therefore cannot satisfy the intended prospective evaluation.

## 5. Prospective experiment protocol

### Systems

At minimum compare:

1. fixed-topology graph/search policy;
2. ORION-12-style route governance without chart change;
3. ordinary replanning/model-update baseline;
4. representation-reformulation baseline without support-transport rules;
5. full ORION-17 atlas policy;
6. no-topology-change, no-censored-obligation and no-transport ablations.

### Hidden information

Candidate systems must not receive `topology_change_required`, the target chart, the gold terminal or hidden frontier/coverage labels. These remain evaluator-owned.

### Primary outcomes

- root task success under matched resources;
- premature task-stop rate;
- necessary-reframe recall;
- unnecessary/harmful-reframe rate;
- support/certificate transfer error;
- obligation/frontier coverage;
- redundant exploration and revisit value;
- calibrated `CANNOT_CHECK`;
- cost and latency.

### Promotion condition

A separate ORION-17 paper needs a prospectively frozen benefit on topology-positive cases, including the non-retrieval domain, without an unacceptable increase in harmful reframes, premature stopping or cost. Otherwise the framing returns to ORION-11/ORION-12.

## 6. Current terminal

The benchmark contract and validators are executable and locally green. No agent comparison has been run, so empirical contribution claims remain `CANNOT_CHECK`.

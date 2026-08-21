# P7 evolving-topology benchmark seed V1

`instances_v1.jsonl` freezes eight case contracts before any candidate-agent outcomes.

## Required families

- hidden frontier and unknown denominator;
- censored/unavailable routes;
- deceptive route diversity;
- dead-end/revisit;
- beneficial topology change;
- harmful/unnecessary topology change;
- at least one non-retrieval domain.

## Terminal oracle

The deterministic reference oracle implements only gold-contract integrity:

1. `topology_change_required=true` -> `REFRAME`;
2. unresolved/censored coverage -> `CANNOT_CHECK`;
3. deceptive nominal diversity -> local `ROUTE_STOP` without task closure;
4. otherwise the frozen case may reach `TASK_STOP` after its mandatory obligations are discharged.

This oracle is not a system baseline. A real evaluation must hide gold topology/reframe labels, match resources, freeze action interfaces and score root success, premature stop, unnecessary reframe, certificate-transfer errors, exploration breadth and cost.

## Promotion-critical comparison

The mandatory discriminator is a paired non-retrieval study comparing:

- fixed-topology navigation;
- P2-style route governance;
- ordinary replanning;
- representation/task reformulation baselines;
- full P7 topology change.

A separate paper requires benefit on topology-change-positive cases without an unacceptable harmful-reframe rate on negative controls.

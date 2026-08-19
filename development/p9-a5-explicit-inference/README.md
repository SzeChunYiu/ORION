# P9 A5 — explicit inference first-right-of-refusal

## Development question

When a P9 representation contains all load-bearing transport values for the D0 gluing task, is a learned neural transition/inference architecture needed at all, or does a small exact inference engine exhaust the task?

This tranche targets only the affine local-transport hostile family already frozen by #473/#481/#483. It does not generalise from this toy calculus to arbitrary scientific inference.

## Atomic fibres

1. Consume only the architecture-neutral `GluingTask.model_payload()` at the declared view.
2. Do not access `P9StructuralWorld`, generator family, pair identity, or evaluator gold.
3. Recover representation-node identities and directed `MAPS_TO` topology from visible context.
4. Match each visible directed transport map to its endpoints.
5. At CURRENT/SEMANTIC, compose the one-dimensional affine maps around the cycle.
6. Return `GLUE` iff the composed map is identity within the frozen tolerance; otherwise `OBSTRUCTION`.
7. At a view where transport values are absent, return `UNKNOWN` rather than fabricate them.
8. Test surface/id reminting and transport-list permutation invariance.
9. Bind the result to an exact generated test split.
10. Keep the terminal non-authorizing and limited to the D0 transport atom.

## Incumbent donors

This is ordinary explicit algebraic/constraint inference. It is intentionally stronger and simpler than adding graph/sheaf/NAR/latent machinery to a task whose exact semantics are already known.

A5's relevant prior-art doctrine from #478 applies: exact/search/probabilistic/constraint inference gets first right of refusal whenever the structured state makes the computation enumerable.

## Frozen hypothesis

On a protected generated transport split:

- TYPED view is non-identifying because it exposes transport endpoints but not values; the explicit engine must return `UNKNOWN`.
- CURRENT view is identifying and exact affine composition should classify every GLUE/OBSTRUCTION example without learning.

If this passes, D0 transport does **not** justify sheaf, graph, neural-algorithmic, latent, or energy-based architecture complexity.

## RED / hostile tests

- changing evaluator gold does not change prediction;
- permuting transport records does not change prediction;
- reminting atom/surface ids does not change prediction;
- missing transport => UNKNOWN;
- duplicate map for one edge => UNKNOWN rather than arbitrary choice;
- broken cycle => UNKNOWN;
- small final-map perturbation => OBSTRUCTION;
- exact inverse cycle => GLUE;
- predictor receives task payload only.

## Nonclaims

No claim about general scientific reasoning, learned mechanisms, sheaf value, neural architecture value, or authority. The only possible positive terminal is `A5_D0_EXPLICIT_INFERENCE_SUFFICIENT` for this exact affine transport atom.
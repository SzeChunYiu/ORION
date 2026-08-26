# ORION-P5 fresh-transfer policy V1

## Why replay is insufficient

A repair can overfit the motivating failure. Paper V therefore separates three evidence roles:

1. **Motivating evidence** explains why development was opened.
2. **Replay evidence** tests whether the exact motivating failure is repaired.
3. **Fresh-transfer evidence** tests independent variations that were not available as candidate feedback.

A candidate needs replay **and** fresh-transfer evidence for a positive governed-development claim. Good replay with harmful fresh transfer is `META_OVERFIT`/negative evidence, not a partial success to average away.

## Freshness requirements

Before candidate generation, the host freezes the fresh split and its evaluator. Each fresh case changes at least one declared independent axis relative to the motivating case: task, domain, model, environment, data or tool. The candidate receives neither fresh labels/answers nor fresh evaluator internals.

The same fresh set is used for matched candidate/baseline evaluation. Once used as development feedback for a new repair, it is no longer fresh for that repair and a new split/version is required.

## Harm accounting

Report:

- fresh tasks improved;
- fresh tasks unchanged;
- fresh tasks regressed;
- regressions beyond the frozen harmful-transfer threshold;
- worst-family and tail regressions;
- evaluator/holdout/negative-history compromise attempts.

A pooled mean cannot erase a catastrophic regression family.

## Causal-development boundary

Recurrence or reflection may open a hypothesis but does not identify the root cause. The candidate must retain competing causes and discriminator evidence. Method/representation invention is considered only after ordinary retrieval, routing, implementation, environment, evidence and transfer explanations are challenged under the frozen protocol.

## Authority boundary

Fresh-transfer success does not grant self-merge or self-certification. The strongest internal result remains a recommendation bound to exact candidate/evidence lineage; final promotion is external host authority.

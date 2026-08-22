# Results

Historical protected terminal: `P13A_RCS_SAFETY_COST_SUPERIORITY_SUPPORTED`.
Current authority: `P13A_EMPIRICAL_SAFETY_COST_AUTHORITY_WITHHELD` under
`P13A_OUTCOME_ENTAILMENT_ADJUDICATION_V1.json`.

| arm | unsafe reuse | verified correctness | unnecessary reopen | mean cost |
|---|---:|---:|---:|---:|
| **RCS** | **0.0000** | **0.9807** | **0.0000** | **2.8747** |
| confidence only | 0.2156 | 0.9657 | lower than RCS | 1.8582 |
| provenance only | 0.3962 | 0.9248 | 0 | 1.0000 |
| unqualified compact | 0.3962 | 0.9248 | 0 | 1.0000 |
| always raw | 0.0000 | 0.9513 | 0.5744 | 5.7319 |

RCS emits `CANNOT_CHECK` for all **237** certificate-declared
unsupported/nonrecoverable cases and no other protected case. These action,
rate, cost and replay numbers are descriptive historical facts. They do not
establish elimination of unsafe reuse because the harm endpoint is self-scored.

## Outcome-contingency adjudication

On the exact 3,840-point audit space, a registered certificate corruption moves
the RCS action on 2,304 points but moves the published unsafe-reuse endpoint on
zero. The endpoint has zero opportunities and returns `CANNOT_CHECK`. A control
that grades the same reuse decisions against independently defined gold support
has 1,536 live opportunities and passes, establishing that the missing
denominator is specific to P13A's scorer rather than inevitable.

## Why provenance fails

Every compact state has valid lineage. `PROVENANCE_ONLY` and `UNQUALIFIED` are
identical policies and identical result rows here, so path or label multiplicity
cannot create two independent comparisons.

## Why always raw is not the answer

Always reopening has the reported historical cost/action profile. Whether RCS
occupies a valid interior safety–cost frontier remains a P13B question because
the load-bearing safety coordinate was not independently gradable.

# Fail-closed staged self-revision: governance architecture and bounded evidence from Self-ORION

## Abstract

Systems that revise their own prompts, policies, code or evidence structures are often evaluated by whether a later artifact scores better on a visible benchmark. That criterion is insufficient for a scientific claim of self-improvement: replay gains can coexist with fresh-task harm, retention loss, holdout leakage, favorable stopping and selective deletion of failed revisions. We present Self-ORION as a fail-closed governance architecture for staged revision. The architecture separates candidate generation, campaign control, protected evaluation, promotion authority, archival custody and independent replay; preserves negative history; and requires immutable evidence before promotion. We also report the strongest preserved Wave 3 empirical result: in a 24-case GLM-5.3 attribution harvest, the control arm answered 22 cases correctly and the treatment arm answered 23. An earlier 24/24 treatment ceiling was not reproduced. The one-case difference is therefore recorded as bounded descriptive direction only. It does not establish protected longitudinal transfer, causal superiority, broad self-improvement or generality across model generations. The finished contribution is a reusable governance and evidence architecture, a concrete example of non-escalating result preservation, and an executable protocol for a future protected longitudinal study. The scientific terminal is that protected transfer is not established while the governance theory is retained.

## 1. Why benchmark-local improvement is not self-improvement evidence

A self-revising system can appear to improve for reasons unrelated to durable capability. It can overfit replay cases, exploit evaluator details, discard a failure from its denominator, stop after a favorable round, replace a failed current artifact with a stale successful one or trade a large aggregate gain for severe harm on a protected subgroup. A visible score increase is consequently compatible with no fresh transfer and with net scientific harm.

A defensible claim requires at least four distinctions.

1. **Replay versus fresh transfer.** Cases used to diagnose or verify a repair cannot also serve as the primary evidence that the repair generalizes.
2. **Improvement versus retention.** A gain on new cases does not justify promotion when prior protected capabilities collapse.
3. **Generation versus authority.** A candidate may propose a revision but may not certify its own promotion.
4. **Execution versus record.** Missing, stale, malformed or conflicting receipts must block a promotion rather than disappear from the analysis.

Self-ORION is organized around these distinctions.

## 2. Contribution and claim boundary

The Wave 3 paper makes three bounded contributions.

- It specifies a staged self-revision architecture with distinct roles, immutable evidence and negative-history retention.
- It gives an authority model in which replay success is necessary for a repair but insufficient for scientific promotion.
- It preserves a bounded 24-case attribution harvest without converting a one-case descriptive difference into a protected or general self-improvement claim.

The paper does not claim that Self-ORION has completed the protected longitudinal campaign needed to establish durable transfer. That study remains a possible successor rather than an implied result.

## 3. Staged revision architecture

### 3.1 Roles

A protected campaign should bind six roles to distinct identities and content digests.

1. **Candidate generator.** Proposes a revision from authorized motivating evidence, replay cases and the immutable archive.
2. **Campaign controller.** Enforces the registered round order, budget, stopping rule and arm contracts.
3. **Protected evaluator.** Executes fresh, retention and protected cases that the candidate generator cannot inspect.
4. **Promotion authority.** Applies the frozen decision rule to immutable evaluator receipts; it cannot change candidate bytes or outcomes.
5. **Evidence archivist.** Appends successful, null, adverse, blocked and infrastructure-failure records without destructive rewriting.
6. **Independent replay checker.** Reconstructs the decision from frozen inputs and receipts without importing candidate-generation logic.

Role separation is an authority boundary, not a claim that the roles are presently operated by independent institutions. A future external campaign must bind the actual custody identities.

### 3.2 Evidence splits

The protocol distinguishes five split functions.

- `MOTIVATING`: visible failures that initiate diagnosis.
- `REPLAY`: previously seen cases used only to verify that a proposed repair addresses the intended mechanism.
- `FRESH`: unseen cases from a prospectively frozen family.
- `RETENTION`: earlier capabilities and previously passed protected cases.
- `PROTECTED`: host-controlled final acceptance cases unavailable to candidate generation and arm selection.

The primary scientific endpoint cannot be computed by mixing these roles. In particular, replay improvement cannot substitute for fresh transfer.

### 3.3 Immutable revision lifecycle

Each proposed revision passes through a fail-closed lifecycle.

1. Freeze candidate bytes, parent state, authorized evidence and resource budget.
2. Execute deterministic or replay checks that verify the intended repair.
3. Execute fresh and retention evaluation under independent custody.
4. Apply harm vetoes before aggregating gains.
5. Spend any registered sequential error budget through an immutable receipt.
6. Promote only when every required receipt is present, current, mutually consistent and content-bound.
7. Append the decision and all adverse evidence to the history inherited by later rounds.

A crash, duplicate receipt, retry, resumed host or skipped round must not create an unrecorded path around the decision rule.

## 4. Negative history as state

Self-revision is longitudinal. The state inherited by a later round includes not only retained code or prompts but also the causal and evidential history of earlier attempts. Removing a failed revision from that state changes the experiment: the later system is no longer learning under the same information history.

The architecture therefore treats negative history as first-class state. Records may be corrected additively, with an explicit superseding link, but they are not silently deleted or rewritten. This design supports three scientific functions.

- It prevents repeated failures from being presented as independent discoveries.
- It allows an ablation between full history, no history, positive-only history and non-causal or compressed history.
- It makes the cost of governance observable rather than hiding it behind the final successful artifact.

The present paper specifies these functions. It does not claim an empirical positive effect of negative-history retention because the required longitudinal ablation has not been completed.

## 5. Bounded GLM-5.3 harvest

### 5.1 Preserved result

The content-bound evidence packet at

`papers/orion-15-self-orion/evidence/glm-5.3-attribution-v2/`

contains a 24-case control/treatment harvest. The preserved counts are:

| Arm | Correct | Total | Descriptive accuracy |
|---|---:|---:|---:|
| Control | 22 | 24 | 0.9167 |
| Treatment | 23 | 24 | 0.9583 |

The treatment-control difference is one correct case, or approximately 0.0417 on the raw proportion scale.

### 5.2 Non-reproduction of the earlier ceiling

An earlier run had yielded a perfect 24/24 treatment result. The preserved Wave 3 harvest did not reproduce that ceiling. The authority disposition therefore includes the terminal marker `PERFECT_CEILING_NOT_REPRODUCED` and grants only `BOUNDED_DESCRIPTIVE_DIRECTION_ONLY`.

This adverse fact is part of the result rather than a reason to discard it. A governance system intended to preserve scientific history must retain the non-reproduction alongside the favorable direction.

### 5.3 Interpretation

The 22/24 versus 23/24 observation can motivate a future study and can test the evidence pipeline. It cannot by itself establish:

- a causal treatment effect;
- protected fresh-task improvement;
- retention across ordered revision rounds;
- a harmful-transfer rate;
- superiority to fair self-refinement baselines;
- generality to other task families or model generations;
- autonomous self-improvement; or
- submission or journal authority.

No inferential margin is promoted from the small bounded panel. The descriptive direction is reported because it occurred and because the manifest binds every preserved artifact, not because it clears the future campaign's positive gates.

## 6. What a decisive longitudinal study would require

A successor study would need to be frozen before protected outcome access. The executable protocol should include at least six ordered rounds per seed or replicate and matched arms with equal information, tools, search space, resource budget and stopping authority. The primary comparison should include no edit, direct self-edit, issue/archive-centric revision, generic causal repair, staged Self-ORION and ablations of negative history and independent promotion authority.

The registered endpoints should jointly cover:

- protected fresh-task value;
- retention on all prior protected capabilities;
- harmful-transfer rate and severity;
- false promotions and false rejections;
- unauthorized holdout, evaluator or history mutations;
- candidate and evaluator calls;
- model and tool tokens;
- wall-clock, compute and monetary cost; and
- persistence of gains after later rounds.

An anytime-valid promotion rule would also need a stated filtration, hypothesis family, stopping rule and complete error-budget ledger. The theorem checker must be separate from the campaign runner. This paper does not claim that such a theorem has already converted the bounded harvest into protected authority.

## 7. Hostile cases the architecture must reject

The governance design is evaluated by whether it fails closed on cases that can make a favorable score scientifically misleading.

- replay gain accompanied by fresh harm;
- fresh gain accompanied by retention collapse;
- mutation of the evaluator, threshold or split after outcome access;
- deletion of a prior adverse record;
- reuse of a stale or duplicate error-budget receipt;
- stopping immediately after a favorable round;
- a candidate that self-certifies promotion;
- direct or indirect holdout exfiltration;
- an aggregate gain hiding protected subgroup harm;
- resource-budget overrun or retry laundering; and
- substitution of an old successful artifact after a failed current execution.

A complete future campaign must encode each case as an executable hostile control. The current paper records them as acceptance requirements and does not count their specification as empirical success.

## 8. Reproducibility and custody

The bounded harvest is preserved with a 56-entry SHA-256 manifest. The focused custody test verifies both the exact arm counts and every artifact digest:

```bash
python -m pytest -q \
  tests/unit/publication/test_orion15_glm53_bounded_harvest.py
```

The protocol family is stored under:

- `papers/orion-15-self-orion/protocol/README.md`
- `papers/orion-15-self-orion/protocol/PROTOCOL_V2.json`
- `papers/orion-15-self-orion/protocol/PROTOCOL_CAUSAL_REPAIR_V2.json`
- `papers/orion-15-self-orion/protocol/STAGED_ACCEPTANCE_POLICY_V2.md`

Repository custody and passing CI demonstrate that the committed bytes are internally reproducible. They do not establish an external protected host or independent reproduction of a promotion sequence.

## 9. Limitations

The paper has four principal limitations.

First, the 24-case harvest is small and descriptive. Second, it is not the multi-round protected study required for a self-improvement claim. Third, the present role separation is an architecture and repository custody model rather than external institutional independence. Fourth, the strongest fair current comparator has not been executed under a matched protected evaluator and budget.

These limitations determine the terminal. They are not deferred footnotes that can be overridden by the favorable one-case direction.

## 10. Scientific disposition

The empirical proposition that Self-ORION produces protected longitudinal transfer is not established. The governance contribution survives: fail-closed role separation, immutable promotion evidence, negative-history retention, replay/fresh separation and a concrete executable specification for the decisive study.

The exact Wave 3 terminal is:

`SELF_ORION_PROTECTED_TRANSFER_NOT_ESTABLISHED__GOVERNANCE_THEORY_RETAINED`

Future protected evidence must be added under a new frozen campaign identity. It must not rewrite the bounded harvest or present the present governance paper as a completed longitudinal efficacy study.

## 11. Conclusion

Self-revision should be evaluated as a sequence of authority-bearing decisions, not as a single favorable benchmark delta. Self-ORION supplies a fail-closed architecture for those decisions and preserves negative history as part of the inherited state. The bounded GLM-5.3 harvest records 22/24 control and 23/24 treatment, while explicitly retaining the failure to reproduce an earlier perfect treatment ceiling. This evidence is useful but not sufficient for protected self-improvement. The finished paper is therefore a governance and evidence-method paper with a bounded case study, not an efficacy claim.

## Data and code availability

The protocol, evidence packet, manifest and custody tests are available in the repository paths listed above. Protected longitudinal outcomes, sealed holdouts and an independent headline reproduction do not exist for the present Wave 3 paper and are not represented as available data.

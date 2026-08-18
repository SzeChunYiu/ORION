# Paper 2 V2 prospective claim ledger

Status: **COMPLETE AT STABLE NON-PROMOTION TERMINAL**

Authorized manuscript terminal: **`P2_NARROWED`**.

V2 campaign terminal: **`P2_V2_ACQUISITION_NOT_PROMOTED`**.

This ledger extends, but never rewrites, `CLAIM_LEDGER_V1.md`. The archived V1 evidence remains authoritative for all manuscript result claims. V2 rows below record which proposed widening claims were tested or gated and whether they earned promotion.

| Claim ID | Candidate claim | Required evidence | Final V2 state |
|---|---|---|---|
| V2-C1 | Strong donor-composed acquisition improves external scientific-literature discovery under matched resources. | Prospectively valid development selection followed by denominator-valid fresh matched confirmation; strongest runnable baseline; uncertainty; absolute misses. | `NOT_PROMOTED` — valid final Dev-3R development candidate regressed on recall (-0.007209 vs corrected lexical baseline), so fresh confirmation precondition failed. |
| V2-C2 | The named ORION authority residual adds value beyond the strongest acquisition-only system. | Direct one-mechanism ablation after acquisition is fixed; matched budgets; stopping-safety guard. | `CANNOT_CHECK` — acquisition never cleared the frozen gate required to enter this claim. |
| V2-C3 | Typed route/task authority reduces premature closure or unresolved-obligation errors under unknown/censored coverage. | Frozen hostile/external authority tasks; strong stopping baselines; direct closure-error denominator. | `CANNOT_CHECK` — V2 did not enter the external stopping/authority stage. |
| V2-C4 | External discovery benefit does not trade away closure safety. | Joint primary discovery metric + frozen premature-closure/unresolved-obligation margin. | `CANNOT_CHECK` — no confirmatory external discovery benefit was earned. |
| V2-C5 | The V2 result transfers beyond the development benchmark. | Separately frozen transfer axis with no tuning on transfer labels/outcomes. | `CANNOT_CHECK` — transfer stage was never entered. |
| V2-C6 | ORION composes strong acquisition methods without granting them unearned global-closure authority. | Architecture/protocol evidence plus C1-C4 empirical support. | `PARTIAL_METHOD_SUPPORT`; empirical widening `NOT_PROMOTED`. |

## Final valid V2 development evidence

The authoritative acquisition-development result is:

`external_results/P2_V2_ACQUISITION_DEV3R_RESULT_2026-08-18.json`

It is development-only and cannot support manuscript promotion. On the frozen 24-task Wide development slice:

- corrected lexical baseline: recall `0.051422`, IoU `0.010756`, precision `0.014583`;
- final diversified candidate: recall `0.044213`, IoU `0.012475`, precision `0.016667`;
- candidate minus baseline: recall `-0.007209`, IoU `+0.001719`, precision `+0.002084`;
- zero-hit tasks: `19/24` for both systems;
- provider calls: `72/72 OK` for each system;
- open obligations: `0` for both;
- task-closure declarations: `0` for both.

The frozen development eligibility rule required recall delta `>= +0.01`, IoU delta `> 0`, and precision delta `>= 0`. Final verdict: **`DEV3R_FINAL_NON_ELIGIBLE`**.

## Fresh evidence deliberately not accessed

The prospective fresh 48-task confirmation was frozen before the final valid development result, with task hash:

`f4af8ac37a2dc49a2aad26368403a3cc5639fedc274db05f28953a3f826d85ed`.

Its execution precondition required `DEV3R_ELIGIBLE_FOR_FRESH_CONFIRMATION`. The actual verdict was non-eligible, therefore the fresh campaign was **not executed and its outcomes were not accessed**. No alternate fresh slice, margin, bootstrap rule or baseline was chosen afterward.

## Superseded V2 development diagnostics

Earlier V2 Wide and Dev-2 development numbers are preserved for audit but may not select a system or support promotion. The candidate harness extracted identifier-shaped strings from the complete Atom body instead of only returned entry identities. The invalidation is archived in:

`external_results/P2_V2_WIDE_V2_HARNESS_INVALIDATION_2026-08-18.json`.

The first corrected Dev-3 attempt is also not the final authority because the shared arXiv parser falsely classified legitimate paper titles beginning with `Error` as API service errors. Dev-3R changed only that response classifier, preserving all acquisition logic and frozen thresholds.

## V1 evidence that remains valid

- frozen 390-task complete-gold controlled mechanism campaign;
- full ORION mean recall 0.979487 versus 0.666667 strongest frozen confirmatory comparator, descriptive only;
- zero premature task closures in the controlled campaign;
- MetaSyn 86-review stage-separated bounded probe;
- AutoResearchBench Deep 0/600 bounded development diagnostic with judge control 9/9;
- all V1 null, blocked and `CANNOT_CHECK` outcomes.

None of those artifacts may be relabelled as a V2 confirmatory positive, and the valid V2 development result may not be used as confirmatory evidence either.

## Promotion rule and terminal

The manuscript may move above `P2_NARROWED` only when `protocol/P2_V2_PROMOTION_STATE.json` names a higher authorized terminal with independently reproducible confirmatory evidence. This V2 campaign did not satisfy that condition. The acquisition stop rule now forbids Dev-4 on the burned development slice and forbids opening the pre-frozen fresh confirmation under this campaign.

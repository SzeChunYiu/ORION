# ORION-19 integration-authority receipt V1

Status: **INTEGRATED ON REVIEW BRANCH; MERGE AUTHORITY STILL EXTERNAL**

Frozen: 2026-08-20

Current integration PR: **#615** — `ORION-19: integrate verified science and bounded TMLR review package`.

Current integration branch: `shadow/p9-peer-review-integration-20260820`.

## Purpose

This receipt does not rewrite or supersede the historical execution receipts. It records that the result-bearing ORION-19 artifacts already verified on their scientific branches are present unchanged in the current review integration. Historical receipts remain provenance for how the experiments were executed; this receipt is the paper-package authority for reading those immutable artifacts on PR #615.

The receipt grants **no authority to claim that #519 or any other historical donor PR merged**. It also grants no scientific authority beyond the frozen result terminals and independent comparisons below.

## A2/A4 integration

Content-addressed donor integration commit: `81e18ddd1227971bb2952ec9026e42d85b3da56f`.

Official result path:

`research/extensions/p9-structured-neural/A2_A4_D0_EXPLICIT_RESULT_V1.json`

Required terminal: `A2_A4_D0_EXPLICIT_INFERENCE_SUFFICIENT`.

Verification state: `BOUNDED_VERIFIED` with all recorded hostile checks true.

## M1 integration

Content-addressed donor integration commit: `0e5cd2531ed35ab89839c3918be10ea72b220b5f`.

Official raw result path:

`research/extensions/p9-structured-neural/execution/M1_EXECUTION_RESULT_V1_5.json`

Official result digest:

`sha256:01e1b62da27b424d453c63b798a5cbb13a915a4546b8ced68fcf84c32d04d97e`

Official corpus manifest digest:

`sha256:01ae54ca4d8cf423b0ac20bf0e085f1ecdf6cec7a1f142cc09b5df0a90d9cc3a`

Required terminal: `M1_GLOBAL_COMPOSITION_RESIDUAL`.

Independent disposition retained from the scientific closure receipt: `BOUNDED_VERIFIED_WITH_ADJUDICATED_NON_MATERIAL_DISCREPANCY`; material discrepancy count `0`. The retained discrepancy is an exact dev tie resolved by the pre-frozen model-selection tie-break and is not a material metric/result discrepancy.

## D1 integration

Content-addressed donor integration commit: `18d3ad2b12ee0cb988642761c028f21fbdc59a6c`.

Historical provenance remains `evidence/D1_OFFICIAL_WORKFLOW_RECEIPT_V1.md`, which correctly records that the original #519 path was pending merge authority at the time that receipt was written. That historical statement is not altered here.

The exact result-bearing D1 artifact from that workflow is now present in PR #615 at:

`research/extensions/p9-structured-neural/execution/D1_EXECUTION_RESULT_V1_2.json`

Official result digest:

`sha256:34003fb8ffcecec6ed01654e40c644ff05b7640be56b398a45efc1e52a30141a`

Official dataset manifest digest:

`sha256:2775298457b7bdee815b207733507cd27d55719df314ef6352bb601bd709c19c`

Required terminal: `D1_TYPED_STRUCTURE_TRANSFER_SUPPORTED`.

The original independent pre-artifact comparison reported exactly:

`MATERIAL_DISCREPANCIES = 0`.

The current PR-head D1 replay workflow is read-only and rechecks the integrated archive identity rather than writing back to the historical donor branch.

## Paper-package authority

For PR #615, the paper evidence builder may read the integrated A2/A4, M1, and D1 official artifacts listed above and may render their already-frozen bounded result values **provided** all of the following fail-closed checks pass on the same review head:

1. exact required terminals;
2. exact M1/D1 result digests;
3. exact M1 corpus and D1 dataset identities where checked by the result/workflow;
4. final official-vs-independent verification with zero material mismatch terminal;
5. result-macro/table regeneration;
6. manuscript claim/citation/evidence audit.

This authority means `INTEGRATED_ARTIFACTS_MAY_BE_RENDERED_ON_PR_615`; it does not mean `MERGED_TO_MAIN`, `PUBLISHED`, or `UNBOUNDED_GENERALIZATION`.

## Claim ceiling

The strongest integrated ORION-19 paper claim remains bounded:

> On the prospectively controlled synthetic/procedural tasks in the ORION-19 package, exact representation collisions distinguish missing information from model failure; simple learners exploit typed relation/history coordinates but leave a global affine-composition residual that exact inference closes; and typed relational method coordinates transfer on a whole held-out procedural domain beyond transcript, untyped, and same-information serialized controls.

No neural-architecture novelty, general LLM scaling law, natural-science understanding result, or universal representation theorem is authorized by this receipt.

Terminal: `P9_VERIFIED_SCIENCE_INTEGRATED_ON_REVIEW_BRANCH`.

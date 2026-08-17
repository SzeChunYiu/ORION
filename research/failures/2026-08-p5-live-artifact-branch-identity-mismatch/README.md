# P5 live-result artifact / branch identity mismatch

**Observed:** 2026-08-17 while reconciling Phase-2 / P5 closure evidence for issues #8, #76, #102, #159 and roadmap #208.

## Failure

Issue #159 contains a report of a result-bearing GLM-5.2 hidden-cause run over 24 cases spanning eight cause families. The report names three result artifacts under temporary host paths (`/tmp/orion-p5-artifacts/...` and `/tmp/run_p5_campaign.py`) and states that committing those artifacts is a subsequent step.

PR #207 was then opened with a P5 live-trial title/body and names candidate-readable P5 evidence paths as committed artifacts. However, the GitHub PR changed-file tree contains only eight Paper-02 claim-ledger/submission files, and `evidence/p5-live-campaign.py` is absent from the PR head. The PR's four commits are P2 work plus a merge from `origin/main`; no P5 artifact commit is present.

Therefore the reported 24/24 execution cannot currently be treated as merged, content-addressed Phase-2/P5 evidence. The numerical report may describe a real execution, but the execution artifact identity and the branch/ref identity advertised as carrying it diverged before integration.

## Failure class

`EXECUTION_IDENTITY_BOUNDARY_MIXUP`

The failure is specifically an evidence-to-Git identity mismatch: ephemeral host artifacts, an issue report, a PR description, a branch ref, and the actual Git tree were treated as if they named the same result-bearing object when they did not.

## Correct response

1. Do not merge #207 or check any empirical Phase-2/P5 gate on the basis of its title/body.
2. Inspect the actual PR changed-file tree and commit history before assigning evidence credit.
3. Treat the issue-comment result as `UNBOUND_EXECUTION_REPORT` until the original bytes can be recovered and hashed, or the campaign is rerun prospectively under a new immutable execution manifest.
4. Keep protected labels/evaluator state outside candidate custody during any recovery or rerun.
5. If original temporary artifacts are recoverable, preserve their exact bytes first, compute content digests, bind them to subject/provider/model/split/evaluator/epoch/resource identities, and independently verify the report from raw records before integration.
6. If original bytes are unavailable, do not reconstruct raw result records from the summary. Preserve the report as historical evidence and rerun under a new protocol/execution epoch.
7. Reconcile or supersede #207 so its PR metadata matches its actual P2 tree; do not force-move another lane's branch.
8. Only after a content-addressed result-bearing artifact is merged on the exact closure subject may #8/#76/#159 empirical boxes be checked.

## Discriminator / reopen condition

The reported campaign becomes admissible for further verification only if one of these conditions is met:

- **Recovery path:** exact original result bytes and driver/config bytes are recovered, hashes are recorded, raw-record-derived metrics reproduce the issue report, and the subject/evaluator/split/provider identities are independently bindable; or
- **Rerun path:** a new immutable pre-outcome execution manifest is frozen and the campaign is rerun, with raw traces/results archived directly into a content-addressed evidence package before any PR metadata claims completion.

Until then, the empirical authority of the 24/24 report remains `CANNOT_CHECK` for Phase-2/P5 closure.

## General lesson candidate

Result identity must be verified through the full chain `execution epoch -> raw bytes -> content digest -> subject/evaluator/split binding -> Git tree -> commit -> ref/PR`. Human-readable issue or PR text is descriptive metadata, not evidence authority. A mismatch at any link must block promotion and trigger reconciliation rather than allowing a plausible result summary to stand in for the missing immutable object.

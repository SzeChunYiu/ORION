# PR 12 hostile review: self-claimed protection and false mechanic closure

**Status:** blocking review findings reproduced; repairs and regression tests added before merge.

## What failed

The first authority-hardening pass still allowed a caller to construct `PatternVerificationReceipt(passed=True, independent=True, ...)`. Assessment checked a candidate hash and episode names but did not resolve the receipt through a trusted verifier or bind episode contents. Replacing all evidence under the same identifiers still produced `CONDITIONALLY_REUSABLE`.

The same review found additional structural gaps:

- episodes lacked parent-run, evaluation-epoch and split identities, so one root attempt could masquerade as repeated evidence;
- dependency references/cycles were not audited;
- generic mechanic envelopes removed step-specific questions even while declaring those coordinates open;
- `CANNOT_CHECK` and residual-only episodes were excluded from matching/pattern formation;
- runtime stored only a root episode, so atomic mechanic failures never entered experience learning.

## Repairs

1. Protected pattern verification now resolves an Ed25519 signature through host-pinned public keys; assessment contains no signing secret and the general caller path cannot invoke promotion authority.
2. Receipts bind the canonical hash of the candidate and complete supporting, replay and fresh-transfer episodes. Episodes retain exact receipt identities, invoked actions, handoff values, metric values/units/uncertainty, provenance, cost/latency and canonical evidence-record hashes; identifier-preserving evidence substitution fails closed.
3. Episodes carry atomic/root run, parent-run, evaluation-epoch and split identities. Candidate construction, receipt minting and assessment each require independent root runs and an exact multi-variation manifest; replay is bound to a supporting case; fresh transfer requires mutually distinct run/task/split/evaluation/variation identities.
4. Recursive audit separately reports unknown child/dependency references and containment/dependency cycles.
5. Universal verification/failure/observability/handoff/state/transition/math envelopes mark their dimensions provisional, preserving step-specific questions.
6. Normalized structural failure signatures include typed residuals and `CANNOT_CHECK` episodes.
7. Every solver trace event carries a transition-consistent `MechanicReceipt`; the runtime records lossless receipt-derived atomic episodes under the root-run parent. Trace/receipt identities are unique per run.
8. Host-installed executable mechanic guards are invoked before their target mechanic and their exact `guard:<pattern_id>` action flows through the real trace and episode path.
9. Operator/provider exceptions become failed atomic receipts and blocked root episodes instead of disappearing before runtime recording.
10. Failure-pattern candidates are structurally fixed at `CANDIDATE`; promotion is a protected assessment result rather than a caller-written field.

## Remaining boundary

Ed25519 removes signing secrets and caller-declared independence from assessment, but host trust-store custody is still a deployment boundary rather than a Python sandbox. Live trials must test protected-assessor isolation, key rotation, evaluator separation, exact build hashes, evidence-lineage construction, persistence failure and process-death recovery. No live Self-ORION promotion authority is granted by this repair.

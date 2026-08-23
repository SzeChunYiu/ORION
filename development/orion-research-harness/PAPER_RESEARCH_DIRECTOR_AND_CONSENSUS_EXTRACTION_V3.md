# ORION shared harness — research director + consensus extraction V3

Date: 2026-08-22
Status: FROZEN_BEFORE_IMPLEMENTATION
Scope: `packages/orion-research-harness`
Authority: engineering/research-control only. This packet grants no scientific, novelty, adoption, promotion, merge, or global-task-stop authority.

## Motivation

The P1–P15 operationalization makes paper mechanics executable and host-callable, but two material gaps remain for a genuinely research-capable harness:

1. the ordinary recursive solve path does not emit a first-class paper-aware directive telling the host which operational research-control surface must run next;
2. raw-paper method extraction has exact-span support and independent evidence verification, but one proposer path can still determine which supported coordinates are noticed.

V3 closes those gaps without changing the scientific authority boundary.

## V3-A — paper-aware research director

### Input boundary

The director consumes only already-materialized recursive solve state:

- solution status;
- material residual identities/descriptions;
- candidate responsibility sets;
- resource/identity-ambiguity conditions.

It does not invent new scientific evidence or inspect protected content.

### Required directives

The director must emit exactly one typed next-action directive.

1. Resource-bound or residual-identity ambiguity -> `CANNOT_CHECK`.
2. Any material residual with zero or multiple candidate responsibilities -> `DIAGNOSE_RESPONSIBILITY`.
3. Singular `EXECUTION` responsibility -> `RESTORE_CAPABILITY` (P15 boundary).
4. Singular `EVIDENCE` responsibility -> `VERIFY_EVIDENCE` (P4/P8 boundary).
5. Singular `EVALUATOR` responsibility -> `CHECK_EVALUATION_AUTHORITY` (P4/P8/P14 boundary).
6. Singular `METHOD` responsibility -> `ASSESS_OCME` (P10). A method residual must never jump directly to method-language expansion.
7. Singular question/representation/search/routing/decomposition/interface/measurement responsibility -> `NAVIGATE_OR_REFRAME` (P1/P2/P7).
8. No material residual + `SOLVED_VERIFIED` -> `ASSESS_SATURATION`. Verified solution is not global task-stop authority.
9. No material residual + non-verified solution -> `VERIFY_OR_REOPEN`.

When multiple singular residuals exist, non-compensatory control precedence is:

`EXECUTION > EVIDENCE > EVALUATOR > METHOD > NAVIGATE_OR_REFRAME`.

### Required output properties

Every directive names:

- directive kind;
- responsible paper IDs;
- triggering residual IDs;
- reason;
- `grants_scientific_authority=false`;
- `grants_novelty_authority=false`;
- `grants_global_task_stop_authority=false`.

The complete recursive solve outcome must expose this directive so a host does not need to infer the next paper mechanic from prose.

## V3-B — two-lane consensus method extraction

### Proposal lanes

`paper-structure-consensus` executes two distinct replayable proposer lanes per source chunk. Lane identity must be in the capability request so broker replay cannot collapse the lanes into one request.

Each lane obeys the V1 exact-span rules:

- every populated claim has an exact verbatim source quote;
- no unsupported coordinate inference;
- sequence claims are atomic;
- dependency values are `[from,to]`;
- no scientific/method-fibre/novelty authority.

### Consensus semantics

- Identical source-supported claims from the two lanes merge into one support identity while retaining both proposer-lane IDs.
- Sequence-valued coordinates use the union of source-supported claims; independent evidence verification remains mandatory.
- Scalar coordinates are fail-closed: if distinct proposer values survive exact-span validation for the same scalar coordinate, the consensus run returns `CANNOT_CHECK_PROPOSER_DISAGREEMENT` before canonical P1/P3 construction.
- Dependency edges that refer to mechanics absent from the merged mechanic set remain invalid exactly as in V1.
- A proposer may omit a coordinate; omission alone is not disagreement and does not become evidence of absence.

### Coverage review

After the two proposer lanes and before final source-support verification, a replayable `INDEPENDENT_REVIEW` coverage check receives the source identity/path/digests and merged claim ledger. It returns:

```json
{
  "passed": true,
  "missed_claims": [],
  "reason": "..."
}
```

Rules:

- `passed=true` requires `missed_claims=[]`.
- Every reported missed claim must use the same exact-span claim schema and is validated against the exact source bytes/text before merge.
- Any valid missed claim reopens extraction: the run returns `CANNOT_CHECK_COVERAGE_GAP` with the validated missed-claim ledger. The caller must rerun after the proposer/review evidence changes; the harness does not silently inject reviewer-proposed scientific structure into a COMPLETE result.
- Invalid/missing coverage-review schema is a host capability failure, never scientific evidence.

### Final verification

Only after proposer agreement and a passing zero-miss coverage review does the existing independent `VERIFY_EVIDENCE` source-support gate run. `COMPLETE` still requires its certificate.

## Host-callable surface

Add:

- `orion-harness-paper paper-structure-consensus ...`
- `orion-harness-paper research-direct --json/--file ...`

The ordinary recursive solve outcome must also include the director result.

## Frozen hostile tests

Director RED tests:

- verified/no-residual -> saturation, never task stop;
- method residual -> OCME, never direct jump;
- evidence/execution/evaluator precedence;
- ambiguous responsibility -> diagnose;
- resource/identity ambiguity -> CANNOT_CHECK;
- recursive solve COMPLETE outcome exposes director result.

Consensus extraction RED tests:

- two proposer requests have distinct lane-bound identities;
- identical claims merge with both lane IDs;
- scalar disagreement -> `CANNOT_CHECK_PROPOSER_DISAGREEMENT` before verifier;
- coverage reviewer with valid missed claim -> `CANNOT_CHECK_COVERAGE_GAP`;
- coverage PASS with no misses proceeds to existing `VERIFY_EVIDENCE` and requires a certificate;
- nonexistent quotes are rejected in either proposer or reviewer lane;
- no output grants scientific/novelty/method-fibre/promotion/global-stop authority.

## Completion terminal

V3 engineering completion requires:

`ORION_HARNESS_RESEARCH_DIRECTOR_CONSENSUS_EXTRACTION_V3_OPERATIONAL`

This terminal means only that the director and consensus extraction control semantics pass the frozen hostile suite. It does not establish arbitrary-paper extraction completeness, research superiority, scientific correctness, or absolute search-space completeness.

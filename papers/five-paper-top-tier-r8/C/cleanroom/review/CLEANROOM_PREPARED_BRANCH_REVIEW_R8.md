# FiberGuard C clean-room prepared-branch review R8

Date: 2026-08-26
Prepared commit: `e0527cba658eceb3af3b84e11bb384d468974e6b`
Prepared tree: `ba5d33cccdda0ef5874a4d267a9746b74d00a5eb`
Prepared parent: `0c451e862a0eeddac7c673813c4dc499f134b088`
Review scope: issue `#1379`, JOB-C-R8-1 preparation only
Disposition: `CLEANROOM_PREPARATION_REVIEW_BLOCKED_NO_EXECUTION_AUTHORITY`

## Blinding and authority boundary

The original FiberGuard implementation and original result artifact were not opened, imported, executed, or compared during this review. This review inspected only the prepared `C/cleanroom` files, exact Git identities, issue metadata without the issue body, and the engineering-custody objects in draft PR `#1382`.

`BLINDING_BREACH_ISSUE_BODY` remains permanent. The issue body exposed frozen verdicts before the prepared output was sealed, so this lane cannot earn a blind independent replay terminal. `CANNOT_CHECK` remains the only admissible independence and comparison disposition. A genuinely blinded external worker is still required.

No scientific result, paper-authority delta, novelty conclusion, or scaling conclusion is produced by this review.

## Executive finding

The prepared code is a credible, structurally different **engineering implementation** of the frozen three-domain protocol. Its declared domains, representations, candidate refinements, dual primary solvers, deterministic fibre selection, and selected-endpoint checks are internally coherent. The fixture receipt and both manifests reproduce exactly.

It is **not executable under the current frozen authority chain** and is not yet a complete immutable execution packet. The prepared branch must not be submitted to LUNARC.

The principal blockers are:

1. permanent blinding breach and `CANNOT_CHECK` independence;
2. no LUNARC submission authority;
3. incompatibility between the legacy v1 packet gate and PR `#1382`'s v2 custody contract;
4. an under-constrained source-manifest gate;
5. a receipt verifier that checks hashes but not the scientific payload terminal vocabulary;
6. missing immutable environment/run/log provenance;
7. no full-panel runtime or memory observation.

## Frozen-spec compliance

### Domains and representations

| Panel | Prepared implementation | Review disposition |
|---|---|---|
| Graphs | All `2^15 = 32,768` labeled simple graphs on six vertices; sorted degree sequence plus triangle count; chromatic target | `CONFORMS_PREPARED_SCOPE` |
| Set cover | All 155,106 covering five-set subfamilies of the 31 nonempty subsets of a five-element labeled universe; set-size and pairwise-intersection multisets; minimum-cover target | `CONFORMS_PREPARED_SCOPE` |
| 2-CNF | All `binom(24,5) = 42,504` five-clause subsets; signed labeled occurrences and labeled unsigned pair counts; exact model-count target | `CONFORMS_PREPARED_SCOPE` |

The candidate-feature names and definitions match `SOURCE_PROTOCOL.json` in all three panels. The endpoint rule is implemented as maximum target diameter, then maximum fibre multiplicity, then canonical representation bytes. Within the selected fibre, the lowest canonical witness at each target endpoint is retained.

### Primary solver diversity

- Graph target: increasing-palette assignment search versus minimum independent-set cover.
- Set-cover target: direct subset enumeration versus universe-mask dynamic programming.
- 2-CNF target: complete truth table versus memoized residual-clause recursion.

These pairs are algorithmically different and compare every instance before fibre aggregation. Any disagreement aborts.

### Third endpoint checker

The graph, set-cover, and 2-CNF endpoint routines independently reconstruct the selected representation and target without calling either named primary target solver. They check both endpoints of the single deterministically selected maximum-diameter fibre, which matches the frozen source protocol.

This is **algorithmic diversity, not independent implementation or custody**: all three endpoint routines live in `fiberguard_cleanroom.py`, share the same process, domain constants, instance objects, authoring lane, and source manifest. They cannot upgrade the lane above `CANNOT_CHECK`, and they do not check refinement features or every instance a third way.

## Identity and LUNARC authority

### Current prepared checkout

The branch is based on the exact R8 scientific subject and adds the clean-room preparation in one descendant commit. Its committed `R8_PACKET_COMMIT.json` is still the historical v1 placeholder. The recorded packet-gate traceback is therefore accurate and dispatch occurs only after that gate.

### Draft PR #1382

Live review observed draft PR `#1382` at head `45957e01c63be6a523ee4cbc9ed2b8a2a71dbcac`, based on the same scientific subject. Its v2 packet and successor binding both state:

- `grants_execution_authority: false`;
- `grants_lunarc_submission: false`;
- `identity_authority: ENGINEERING_CUSTODY_ONLY`.

The prepared executor accepts only the four-field schema `ORION.FivePaperR8.PacketCommit.v1`. It rejects PR `#1382`'s non-self-referential `ORION.FivePaperR8.PacketIdentity.v2` before examining its scientific subject. Therefore merging or checking out PR `#1382` would not unlock this executor even if the PR were approved.

### Separate authority search

Issue `#1379` is open, has no assignee, labels, or authorization comments. The prepared `SUBMISSION_BLOCKER.json` says `lunarc_submission: NOT_SUBMITTED` and requires an additional exact identity transition plus root review. The general execution packet names JOB-C-R8-1 but does not override the branch's failed identity/provenance gates or PR `#1382`'s explicit denial.

**Finding:** no separate, current, runnable LUNARC execution authority was located. This review does not grant it.

## Manifest and receipt audit

### Positive checks

- `SOURCE_MANIFEST.json` exactly equals a fresh allowlisted rebuild.
- `EVIDENCE_MANIFEST.json` verifies all three named evidence files.
- `NON_OUTCOME_VALIDATION.json` is byte-reproducible from fixture mode.
- Its payload hash and source-manifest binding verify.
- `BLINDING_BREACH_ISSUE_BODY`, `CANNOT_CHECK`, `NOT_RUN`, `NOT_PERFORMED`, and `NOT_SUBMITTED` remain visible.

### Blocking gaps

1. **The execution gate does not require the frozen source allowlist.** `verify_manifest` accepts any internally consistent manifest, including a one-file manifest that omits the clean-room implementation, protocol, tests, and SLURM script. `run_replay` accepts an arbitrary manifest path and never compares its path set with `build_manifest.SOURCE_PATHS`.
2. **The legacy packet gate is not an exact-clean-checkout gate.** It accepts a dirty checkout when the named commit is merely an ancestor, and it validates `base_commit` only as 40 lowercase hexadecimal characters. It does not check the base object, tree, branch ref, clean status, or exact HEAD identity.
3. **Receipt semantics are not fail-closed.** `verify_receipt` checks the top-level authority's `CANNOT_CHECK`, payload hash, and manifest hash. A synthetically sealed payload can claim a forbidden independence PASS or scientific-authority gain and still verify because payload terminal fields and exact schema are not validated.
4. **No execution provenance bundle exists.** The prepared result schema and SLURM script do not capture exact commit/tree, dirty status, interpreter version, module list, CPU model, command line, start/end time, wall time, maximum RSS, exit status, or stdout/stderr hashes. The SLURM logs are not sealed into the result.
5. **Evidence-manifest production is not scripted or receipt-bound.** The current evidence manifest verifies, but no committed builder or verifier command binds it to a later exhaustive receipt.

These gaps prevent an immutable execution receipt even if the packet-schema mismatch were repaired later.

## Resource-envelope review

The declared request is 16 CPUs, 32 GB, and two hours. The code creates at most one process per domain, so `--workers 16` currently yields at most three worker processes. Sixteen CPUs are therefore conservative but materially over-allocated.

The finite domains and in-memory fibre tables fit plausibly within 32 GB by static inspection. Two hours also appears conservative for these small exact domains, but no exhaustive run, wall-time sample, or maximum-RSS receipt exists in this lane. Runtime and memory sufficiency therefore remain `CANNOT_CHECK_RESOURCE_ENVELOPE` rather than PASS.

The scripts require a modern Python supporting `zip(..., strict=True)` and current type syntax, but the SLURM script neither loads nor records an interpreter environment. LUNARC environment compatibility is `CANNOT_CHECK_ENVIRONMENT`.

## Test evidence

### Prepared suite

- From repository root: collection fails with three `ModuleNotFoundError` errors because the clean-room directory is not added to the import path.
- From `C/cleanroom`: `34 passed`.

The cwd-sensitive test invocation is an integration/CI packaging defect. It does not refute the 34 local checks.

### Review-only suite

The additive review tests exercise the exact prepared commit/tree, manifests, adverse terminals, v1/v2 incompatibility, dirty-checkout acceptance, incomplete-manifest acceptance, semantic receipt underchecking, third-checker custody, resource declaration, and missing provenance. These tests document current behavior; they do not authorize execution.

## Required transition before any submission

At minimum, a successor owned by the implementation lane must:

1. retain `BLINDING_BREACH_ISSUE_BODY` and `CANNOT_CHECK` permanently;
2. adopt the reviewed v2 subject/publication reader rather than treating the publication identity as an executable commit;
3. add a separate explicit LUNARC authorization object after review;
4. bind the exact clean-room implementation commit/tree and require a clean checkout;
5. require the exact source allowlist and reject substituted/incomplete manifests;
6. validate the exact receipt payload schema and adverse authority fields;
7. capture and seal full environment, resource, command, log, exit, and result provenance;
8. make tests collect from the repository root;
9. obtain root review of the successor bytes before submission.

Until those transitions occur, the only honest execution disposition is:

`BLOCKED_NO_LUNARC_EXECUTION_AUTHORITY__CANNOT_CHECK`

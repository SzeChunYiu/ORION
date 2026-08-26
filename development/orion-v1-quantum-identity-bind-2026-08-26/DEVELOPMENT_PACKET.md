# V1-Q-IDENTITY-BIND-01 development packet

## Frozen authority and identity

- Packet: `ORION.V1.ExecutionPacket.v1 / V1-Q-IDENTITY-BIND-01`
- Packet object: commit `c1f46469f1cdd2735c7c95d48398a7111a62c4fe`, path `research/orion-v1-quantum-audit/V1-Q-IDENTITY-BIND-01/EXECUTION_PACKET_V1.json`
- Frozen source: commit `bf9ee8fa34ffba7531de18e54b58eba4a641601c`, tree `88f8a6c2b24fcec02f2752b78946a7a14652c33c`
- Frozen base main: `ef51b7b9263a72c725dc9d2045627b934b772a92`
- Frozen census artifact: Actions artifact `9598519591`, SHA-256 `115b2ea69dba24bcf1a5959403dc6165ffc4b5b59ad4a5d81fd78ca293f408da`
- Frozen denominator: all 67 lexical candidate issue numbers, including lexical false positives #632 and #1366.

This tranche grants no issue closure, scientific disposition, paper authority, physical-quantum validity, quantum advantage, external novelty, P18 authorization, or ORION V1 freeze. Its only possible positive terminal is a content-bound identity-and-route census.

## Problem

The semantic intake classifies 67 denominator-visible candidates, but issue prose, checkbox state, a merged pull request, a branch path, or a coordination issue cannot establish scientific status. Before atomic scientific adjudication, the programme needs stable bindings among:

1. frozen census issue identities and current successor snapshots;
2. every issue comment and timeline page;
3. explicit linked-PR evidence, not lexical number coincidence;
4. merge identities and ancestry in frozen and current main separately;
5. named repository paths and their exact current-main presence;
6. semantic classes/common cores and non-aggregating next routes.

## Design

`scripts/audit_orion_v1_quantum_identity.py` is standard-library-only and fail-closed.

- It validates the complete 67-row denominator against the semantic intake and the frozen census artifact hash.
- It makes issue-only GitHub API requests. A candidate payload containing `pull_request` is rejected.
- It fetches issue snapshots before and after acquisition. Every comments and timeline endpoint follows `Link: rel=next` until absent, including the first empty page.
- Exact response bytes are stored in deterministic deflated `RAW_RESPONSES.zip`; the raw manifest records request URL, status, selected headers, byte count, SHA-256, and archive entry. Decoded census/current issue bodies and all comment bodies receive separate UTF-8 byte-custody records.
- PR linkage is admitted only from exact repository `/pull/N` URLs, contextual `PR #N`/pull-request phrases, or explicit timeline relations whose source object is a pull request. Plain `#N` mentions and issue cross-references are excluded.
- Each admitted PR binds state, head/base identities, merge commit, fully paginated changed files, and merge ancestry against frozen base main and the current remote-main SHA separately.
- Named repository paths are extracted from the bound issue/comment/PR text. Exact current-main tree membership is independent of linked-branch changed-file evidence; branch-only bytes are never promoted.
- Common cores share only adjudication routes. Member issues retain atomic identities and no common core can mass-close children or transfer source quantum authority.
- `--check` verifies every required output, raw-response/body bytes, denominator, negative-control report, authority ceiling, and result binding without network access.

## Test-first record

The production script did not exist when `tests/unit/orion_v1/test_quantum_identity_audit.py` was first run. The initial RED terminal was:

```text
AssertionError: identity audit script has not been implemented
1 failed
```

The GREEN tests cover pagination, raw content binding, denominator loss/duplication, body-byte substitution, issue/PR separation, contextual PR linkage, timeline linkage, ancestry, branch-only presence, path normalization, lexical-row retention, authority non-transfer, and administrative mass closure.

## Required outputs

The result directory contains all nine packet-required JSON files plus `RAW_RESPONSES.zip`. `RESULT_BINDING_PACKET.json` binds every non-circular result object, including the raw archive. The result terminal remains bounded by the execution packet's authority ceiling.

## Negative controls

All eleven frozen controls must be rejected:

- missing and duplicate issue rows;
- same-length changed issue-body bytes;
- incomplete/truncated page custody;
- pull request substituted for issue;
- uncontextual lexical PR inference;
- merged-but-not-on-main promotion;
- branch-only result promotion;
- scientific disposition from prose/checkboxes;
- loss of #632/#1366;
- source-authority transfer to consumers.

The committed `NEGATIVE_CONTROLS.json` records the typed rejection for each control. It is conformance evidence only.

## Scope and non-goals

Allowed changes are restricted to this development packet, the audit script, its unit test, its dedicated workflow, and the new result directory. No `src/orion/**`, paper, existing result, theorem/claim ledger, LUNARC/Slurm, custody/finalizer, or content-binding baseline is modified. No LUNARC job is required or permitted for this packet.

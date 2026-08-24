# P1 ScienceAgentBench protected artifact staging V1 — handoff

## Terminal

`P1_SAB_LUNARC_ARCHIVE_STAGED_AND_HASH_MANIFESTED__EXTRACTED_TREE_QUARANTINED__ZERO_TASKS_RUN__ZERO_OUTCOMES_OPENED`

## Closed in this increment

- The official public archive was retained only in owner-only LUNARC project
  storage.
- Its exact size and SHA-256 match the identity bound by PR #1102.
- Every encrypted member was mechanically decrypted and byte-count checked.
- A path-bearing per-file hash manifest remains off-repository; this packet
  binds only its byte count and SHA-256 plus aggregate archive counts.
- The extracted tree is quarantined behind a root directory with mode `0000`.
- No entry name or body was printed or semantically inspected.
- No official task, candidate program, evaluator, rubric, gold result or
  outcome was opened or run.

Job `3533828` completed on `cn121` with exit `0:0` in `00:18:32`. Receipt
aggregates: 955 ZIP entries; 845 encrypted files; 110 directories;
4,071,815,117 decrypted file bytes; 132,464 manifest bytes; manifest SHA-256
`003412e023b576333b9b72e4d0875d50378dec44b13fcd2141987dc4cdaecb15`.

## Preserved failure and repair

Job `3533824` failed `22:0` after five exact
`curl: (22) The requested URL returned error: 401` terminals. The public
SharePoint flow required retaining its `FedAuth` cookie across redirects. The
successful transport used an ephemeral owner-only cookie jar through
`--cookie-jar` plus `--cookie` and deleted the jar on exit. The archive then had
to pass the already frozen byte-count and SHA-256 checks before staging.

## Off-repository custody

Do not commit or locally retrieve:

- `benchmark_verified.zip`;
- the extracted tree;
- the path-bearing JSONL manifest;
- entry names or payload bodies;
- task, candidate, gold, evaluator, rubric or outcome material.

Only `LUNARC_ARTIFACT_STAGE_RECEIPT_V1.json` and `REMOTE_SHA256SUMS` were
retrieved. The remote tree and manifest remain subject to the upstream
retention and redistribution terms already frozen in the P1 preflight.

## What remains fail-closed

Archive staging is not benchmark execution and not scientific evidence.
Remaining gates include:

1. build/remove the exact pinned official public base image;
2. bind an admissible immutable generation route with matched prompt, model,
   tokenizer, seed, tool, budget and billed-cost receipts;
3. obtain an owner-controlled credential route for the exact official judge
   `gpt-4o-2024-05-13`;
4. freeze the final runner/protocol/analysis hashes before outcomes;
5. generate all 918 candidate attempts and retain every failure and cost;
6. obtain 102 parseable official evaluator records and pass the frozen paired,
   discipline and cost gates.

Until those gates close, the P1 ScienceAgentBench result is `CANNOT_CHECK`.
Scientific authority delta: `NONE`.

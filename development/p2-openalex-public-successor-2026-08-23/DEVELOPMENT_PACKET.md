# P2 OpenAlex public-data successor development packet

## Scientific problem

Paper 2's external AutoResearchBench Wide campaign exposed a candidate-generation
ceiling: on its frozen 24-task development subset, both the archived lexical
baseline and governed route family missed gold on 19 tasks.  The earlier local
environment also lacked the benchmark bundle and could not reach OpenAlex.
This successor asks a narrower but genuinely empirical question: now that the
public benchmark bytes and the public OpenAlex API are reachable, can three
predeclared, gold-blind views of the same question emit materially more official
gold identifiers at the same 20-candidate cap?

## Ownership and collision boundary

This Codex lane owns only
`development/p2-openalex-public-successor-2026-08-23/`.  It does not edit the P2
manuscript, production modules, shared registries, tests, or another agent's
artifacts.  The decrypted benchmark stays outside the repository under the
projectless `work/open-data-cache/` directory, as upstream asks that decrypted
questions and answers not be reposted.

**Rights repair.** A later adversarial audit found that the two V1 response
trace copies nevertheless retained 24 full `Q0_RAW` strings. Those plaintext
bytes are now quarantined outside the redistributed worktree with mode `0600`;
the in-tree traces retain hash-only provenance. The immutable mapping is
`Q0_RAW_QUARANTINE_RECEIPT_V1.json`. Upstream permission for plaintext
redistribution remains `CANNOT_CHECK`, so plaintext circulation is forbidden.
This archival redaction changes no provider response, candidate, score, gate or
scientific terminal.

## Inputs

- `Lk123/AutoResearchBench` obfuscated bundle at Hugging Face commit
  `dbb4b19d3e1487d14b31a020c2265b6995e07b5e`.
- Obfuscated SHA-256
  `e8d00086dc05bae823d75bf0776a9df5f8bcab59e0d683ea6479ac9e40db631d`.
- Upstream code `CherYou/AutoResearchBench` at
  `a46c9bfb8968786f73f0a6a5b365b5384cd0f96d`.
- Decrypted bundle SHA-256
  `db1839438033a32dd7d76913575d4b76f144d5e442aaac29be4eda32326392c6`.
- Existing frozen 24-task development identities from
  `P2_V2_ACQUISITION_DEV3_FREEZE_2026-08-18.json`.
- OpenAlex public Works API, queried without credentials.

## Gold boundary

`prepare` writes a public file containing only task identity and question and a
separate host-only gold file. `run` accepts only the public file and protocol;
`score` is a separate command that admits the gold after all response and
candidate bytes have been written.  The protocol, queries, candidate cap,
fusion rule, statistics, and gates are frozen before scoring.

## Arms

- `B0_RAW`: OpenAlex relevance order for the raw public question.
- `B1_CURRENT`: relevance order for the existing D1 current-vocabulary query.
- `S1_RRF3`: reciprocal-rank fusion over raw, D1 current-vocabulary, and D2
  lexical-variant result lists.

All arms are views of one shared three-call retrieval batch and return at most
20 arXiv identifiers.  This isolates selection/fusion over a fixed acquired
pool.  It cannot establish an ORION acquisition-policy advantage.

## Decisions

The exact gates are machine-bound in `PROTOCOL_FREEZE.json`.  Failure of a gate
creates a disjoint successor problem; it is never deleted or relabelled.  A pass
is public-provider development evidence only, not confirmatory superiority,
independent custody, or a deployed open-world result.

## Verification allowed in this wave

- provider response and candidate SHA-256 receipts;
- exact JSON parsing;
- deterministic rescoring;
- script byte hash and `git diff --check`.

Per user instruction, pytest and repository CI are out of scope for this
scientific-content wave.

# P2 Wide OpenAIRE scorer-identity bridge — development packet V1

**Date:** 2026-08-18  
**Paper:** P2 — Open-World Scientific Knowledge Discovery  
**Parents:** #99, #279, #157  
**Scope:** evaluation/candidate-generation adapter only; P2 V1 scientific mechanics are not mutated.

## Development question

Can a credential-free scholarly backend produce **scorer-native arXiv identifiers** from the gold-blind AutoResearchBench Wide public questions, so that P2 can execute a matched external ORION-vs-strong-baseline comparison without calling the arXiv API and without proxying title/DOI similarity as official scorer identity?

Atomic fibres:

1. Does current OpenAIRE Graph keyword search return research-product objects containing an explicit structured arXiv PID?
2. Can the adapter admit only explicit `scheme=arxiv` identifiers and refuse regex-looking digit strings in DOI/ISSN/text fields?
3. Can public task selection remain gold-blind and content-addressed against the already frozen 399-task manifest?
4. If the identity bridge is viable, can a later matched comparison give baseline and ORION the same provider-request/candidate budget while treating identity resolution as an explicit cost rather than a free hidden operation?

## Incumbent evidence / negative history

`ISSUE_157_KEYLESS_BACKEND_PROBE_V1.json` reached all three keyless backends on three public tasks but found no valid scorer identity bridge. Its OpenAIRE check searched the raw response with an arXiv-looking regex. The same probe demonstrated why this is unsafe: the regex matched DOI/ISSN digit groups in Crossref JSON and therefore cannot establish arXiv identity.

`WIDE_MATCHED_CAMPAIGN_FREEZE_V1.json` consequently records `BLOCKED_NOT_EXECUTED`: the old matched runner calls arXiv/OpenAlex, while the no-arXiv keyless lane lacked scorer-native identities.

This packet preserves those failures. It does not reinterpret the old probe as a success.

## Knowledge / search-universe saturation

The evaluation question spans three parent domains rather than only IR:

- AutoResearchBench official Wide evaluation semantics;
- scholarly-graph persistent-identifier modelling;
- cross-provider entity/identity resolution.

Primary-source findings frozen for this discriminator:

1. AutoResearchBench's official repository exposes `evaluate/evaluate_wide_search.py` as the Wide retrieval metric path and the benchmark uses arXiv identifiers as the candidate/gold identity object.
2. Current OpenAIRE Graph documentation (11.2/current API docs) exposes research-product persistent identifiers structurally (`pid`/`pids`) rather than requiring text scraping.
3. Current OpenAIRE Graph V4 filter documentation names `ids.arxiv` explicitly as an identity field. This makes arXiv identity a first-class graph property rather than a regex inference.
4. OpenAIRE Graph aggregates arXiv as a source alongside Crossref and other scholarly metadata sources.

Saturation for this **adapter atom** is reached because the discriminator only needs to answer whether a structured scorer identity exists. New retrieval-ranking papers do not change that identity question. Retrieval-mechanism novelty remains governed by P2's existing nearest-work campaign.

## Challenge to the saturation basis

Potential false-flat explanations:

- the old OpenAIRE Search API and current Graph API expose different response shapes;
- a product can be relevant but have no arXiv PID, so `no structured arXiv PID` is not evidence of irrelevance;
- an arXiv-looking substring inside DOI/ISSN/title text can create false identity;
- an identifier can carry a version suffix (`vN`) that must be removed before official set scoring;
- OpenAIRE itself can be unavailable/rate-limited; this must become `CANNOT_CHECK`, not an empty scientific result.

## Frozen implementation hypothesis

Implement a new additive probe that:

1. queries `https://api.openaire.eu/graph/v3/research-products` with public-question-derived keywords only;
2. requests publication results under a bounded result cap;
3. parses JSON structure and accepts an identifier **only** when it occurs in a PID object whose scheme is exactly `arxiv` (case-insensitive); support the documented `pid` and `pids` field spellings;
4. normalizes only an optional `arXiv:` prefix and terminal `vN` version suffix;
5. never scans the raw response body with an arXiv regex;
6. records HTTP/parse status, query, exact task id, admitted IDs, and open obligations;
7. first runs on a frozen small prefix of the already content-addressed 399-task manifest;
8. does not inspect Wide gold and cannot emit a positive paper verdict.

If this probe yields structured arXiv IDs on public Wide tasks, the next separately frozen step may implement a matched comparison. If it yields none, the OpenAIRE-only scorer bridge is rejected without weakening the official scorer.

## Hostile / known-answer tests frozen before network outcome

- explicit `{"scheme":"arxiv","value":"2604.25256v2"}` -> admit `2604.25256`;
- DOI value containing arXiv-looking digits -> reject;
- arbitrary text/original-id containing arXiv-looking digits -> reject;
- malformed PID object -> reject;
- duplicate versioned/unversioned arXiv PID -> one normalized identity;
- transport failure -> typed open obligation, never zero evidence;
- public task input containing hidden/gold fields -> fail closed.

## Reopen triggers

Reopen this development packet if:

- OpenAIRE changes its documented PID response schema;
- the official Wide scorer changes its candidate identity semantics;
- the probe's admitted identifier cannot be independently traced to an explicit structured arXiv PID;
- identity resolution requires gold fields or answer metadata;
- a matched runner hides extra identity-resolution calls from its resource ledger;
- another keyless backend exposes a stronger direct structured arXiv crosswalk.

## Authority boundary

A successful identity probe means only `SCORER_NATIVE_IDENTITY_BRIDGE_OBSERVED`. It is **not** a Wide result, not ORION superiority, and not a reason to narrow P2. The intended scientific terminal remains the broad matched external discovery/stopping claim in #99.
# D R20 — independently maintained authority-integration protocol

Status: `PROTOCOL_FROZEN__EXTERNAL_CASE_AND_ADJUDICATORS_REQUIRED`

## Eligible subject

Choose a maintained integration in which two or more independently validated records, credentials, policy fragments, provenance chains, or evidence origins contribute to one downstream authorization decision. The maintainers must be independent of the Paper-D implementation. A synthetic RFC fixture or a source audit of a known safe merge is a control, not the target subject.

## Pre-outcome freeze

Before labels or incidents are inspected, bind:

- source and deployment revisions;
- record/origin coordinates;
- licence and actor/subject semantics;
- refutation and revocation semantics;
- every authorized bridge between coordinates;
- the typed least-fixed-point evaluator;
- the coordinate-erased comparator;
- the target authorization queries;
- harmless same-origin and explicit-bridge controls;
- first-mixing explanation format;
- adjudicator identities and conflict declarations;
- positive, safe, null, disagreement, timeout and cannot-check terminals.

## Evaluation

For every case, compute typed and coordinate-erased closures. When they disagree, emit the lowest mixed derivation node, its child origins, the erased coordinate, and a minimal selected-origin witness where feasible. The evaluator must distinguish:

- unsafe coordinate erasure;
- an explicitly authorized typed bridge;
- a constituent deny or failed require;
- missing or ambiguous source semantics;
- a safe merge with an individually allowing origin.

## Independent adjudication

At least two domain maintainers independently label whether the mixed proof is authorized by the actual integration contract. Disagreement remains a first-class terminal. Paper-D authors may not convert an ambiguous case into a vulnerability.

## Primary endpoints

- reviewed operational authorization errors prevented by typed evaluation;
- false alarms against maintainer-adjudicated safe cases;
- first-mixing explanation accuracy;
- adjudicator agreement;
- audit time per proposed merge;
- minimum dangerous-origin size on the frozen bounded corpus.

## Allowed terminals

- `D_EXTERNAL_DOMAIN_VALIDATION_PASS`;
- `D_EXTERNAL_SAFE_CONTROL_ONLY`;
- `D_NO_HYBRID_CASES_FOUND`;
- `D_ADJUDICATOR_DISAGREEMENT`;
- `D_TYPED_MODEL_MISMATCH`;
- `CANNOT_CHECK_SOURCE_SEMANTICS`;
- `CANNOT_CHECK_RIGHTS_OR_DISCLOSURE`.

## Authority

A PASS supports only the frozen integration and reviewed cases. It does not establish a vulnerability in Agentgateway, OAuth, JWT, DPoP, MCP, Cedar, or provenance systems generically. Novelty and journal authority require separate current-primary-source review.

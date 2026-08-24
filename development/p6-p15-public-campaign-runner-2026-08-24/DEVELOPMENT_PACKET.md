# P6-P15 public campaign runner development packet

## Scope and authority

This packet freezes an additive, paper-agnostic integrity layer for public-data
campaigns serving P6-P15. It does not execute a paper endpoint, score a paper,
or turn same-owner/public execution into independent adjudication. Missing
licence, source bytes, comparator, official evaluator, chronology, raw output,
replay, or authority-surface agreement must terminate `CANNOT_CHECK`.

## Atomic questions

1. Can every public source be bound to a URL, immutable revision, SHA-256,
   licence/terms URL, citation, retrieval time, task IDs, exclusions, and an
   explicit redistribution decision before execution?
2. Can matched arms, frozen splits, inference units, budgets, seeds, evaluator
   identity, estimand, and gate be represented without paper-specific logic?
3. Can missing or duplicated observations, dropped null/harm/failure rows, and
   evaluator/environment drift, resource overruns, and record/output swaps fail
   closed?
4. Can a fresh-container replay be required to match the original prediction
   and result digests exactly?
5. Can manuscript, active authority, claim ledger, result, and rendered-PDF
   surfaces be required to declare one terminal and one evidence digest?
6. Can the receipt preserve the boundary that online data and same-owner CI do
   not establish protected custody or independent semantic adjudication?

## Incumbent mechanics and nearest reusable donors

- `src/orion/benchmarks/external_evidence.py` already separates PASS, FAIL, and
  CANNOT_CHECK, but is scoped to P1-P5 and assumes independently produced gate
  records rather than auditing a public campaign bundle.
- `development/public-empirical-data-binding-2026-08-23/` binds public source
  identities and explicitly refuses to treat availability as empirical support.
- Existing P6-P15 freezes and receipts independently enforce portions of
  chronology, inference-unit, replay, and authority-surface discipline.
- The smallest justified addition is therefore a generic bundle auditor. It
  composes existing fail-closed principles; it does not replace paper-specific
  evaluators or invent a universal scientific endpoint.

## Bounded saturation assessment

- **Knowledge boundary:** repository-owned source manifests, protocol freezes,
  execution records, evaluator results, replay receipts, and publication
  surfaces.
- **Search boundary:** current P6-P15 artifacts plus the existing public-data
  binding and external-evidence modules.
- **Formulation boundary:** deterministic validation of identities, hashes,
  licence declarations, chronology, complete Cartesian execution coverage,
  matched resource ceilings, adverse-row retention, replay equality, and
  terminal/evidence agreement.
- **Explicit exclusions:** legal interpretation, semantic correctness of gold,
  statistical power, correctness of a paper-specific gate, true organizational
  independence, protected custody, and external proof review.

Within that boundary, the formulation is closed enough to implement because
every accepted field has a deterministic validation rule and every excluded
authority question remains explicit `CANNOT_CHECK`.

The frozen task-to-inference-unit map is part of the protocol identity. The gate
must bind complete `(record, raw output, outcome, inference unit)` rows; its
metrics and interval are included in the signed receipt payload. Replay result,
prediction, environment, and container identities must resolve to that same
execution bundle.

Each publication surface must be read through its canonical path, match its
declared file SHA-256, and contain an uncompressed
`ORION_SURFACE_BINDING_V1|<terminal>|<evidence_sha256>` marker. This makes the
terminal/evidence agreement a property of the verified bytes rather than a
parallel metadata assertion. The replay also binds the canonical full gate
result digest, not only the evaluator-output artifact hash.

Exactly one canonical marker must occur in both the raw bytes and the
reader-visible extracted text; a second/conflicting marker fails closed. Required
runtime, source-revision/citation/task, evaluator, gold, model/tool, custody,
split/unit, estimand/gate, and decision identities reject placeholder sentinels
such as `UNKNOWN`, `CANNOT_CHECK`, `TBD`, and `UNSET`.

Security-relevant flags require exact Boolean values; truthy strings do not
coerce. Budgets, usage, seeds, counts, intervals, and costs reject Booleans as
numbers and reject non-finite numeric values.
Enum fields and observation seeds also require exact runtime types, preventing
string roles and Python's `True == 1` equality from satisfying frozen identities.
Execution-record identities are SHA-256 hashes of canonical structured
`[task, split, arm, seed]` arrays rather than delimiter-concatenated strings;
source, split, inference-unit, execution, and gold registries reject duplicates.

## Saturation-basis challenge

Saturation could be false if a native benchmark requires a licence condition,
split unit, resource dimension, or evaluator identity that the generic schema
cannot represent; if an apparently immutable revision is mutable; or if exact
digest agreement hides semantically inconsistent publication text. Potentially
missing parent domains include software-supply-chain attestation, legal rights
expression, cluster-robust experimental design, and reproducible-build systems.

Prior searches may miss benchmark-specific terms outside the repository,
transitive dataset licences, dynamic evaluator dependencies, or non-file
publication surfaces. Reopen if a P6-P15 adapter needs an unrepresentable field,
if a hostile test can drop an adverse row without detection, if a mutable source
passes as pinned, if replay equality can be spoofed with incomplete coverage, or
if an authority surface can disagree while the bundle passes.

## Frozen implementation hypothesis

A typed immutable bundle plus a deterministic auditor can close the shared
mechanical integrity gaps without changing any scientific terminal. The auditor
will return PASS or FAIL only after all integrity checks pass; otherwise it will
return CANNOT_CHECK. Its independent/protected authority field will remain
CANNOT_CHECK regardless of public availability or same-owner replay.

## Required hostile tests

- missing/ambiguous licence and prohibited redistribution;
- source-hash mismatch and missing frozen task;
- unmatched arm budget and generated-row inference unit;
- duplicate/missing execution record and dropped adverse output;
- evaluator or environment drift;
- post-outcome freeze;
- replay mismatch or non-fresh replay;
- publication-surface terminal/evidence mismatch;
- verified adverse gate remains FAIL, never CANNOT_CHECK or PASS.

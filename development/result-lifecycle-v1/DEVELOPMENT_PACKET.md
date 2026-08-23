# Scientific-result lifecycle V1 — development packet

Date frozen: 2026-08-22
Branch: `codex/p1-r7-wide-successor`
Authority: reporting and validation schema only; no scientific terminal is changed by this work.

## Development question

Can ORION count and present paper results by typed claim lifecycle rather than by grepping negative-looking strings from duplicated artifacts?

## Atomic questions

1. Can every result identify its paper, claim, study, estimand, population, outcome, decision rule, comparator set, visibility contract, and measurement?
2. Can lineage distinguish a true same-study supersession from a new successor, narrowing, adjudication, projection, or metadata amendment?
3. Can the default view return active claim-authority leaves while retaining immutable historical adverse ancestors?
4. Can projections and cross-paper panel copies be deduplicated by record identity and content rather than charged to their enclosing directory?
5. Can invalid digests, ambiguous bare claims, and illegal supersession fail closed?

## Incumbent defects and negative history

- The current publication scoreboard extracts one markdown terminal line and cannot represent multiple scoped claims on one paper.
- Raw text scans count templates, expected negative controls, historical amendments, and duplicate projections as current paper-level failures.
- Three P3/P4/P13 audit files are byte-identical and each contains P1, P4, P4-V3, and P13 panels. Directory-based counting therefore assigns records to the wrong paper.
- P2 narrowed/scoped terminals are not adverse scientific outcomes.
- P11's adverse terminals are genuine and must remain queryable even after a successor.
- P14 adjudication changes the interpretation of an immutable terminal; it does not supersede the result.

## Saturation and challenge

Typed event DAGs, canonical JSON digests, append-only lineage, and materialized active views are sufficient for this reporting problem. Saturation could be false if a new edge silently retires an unlike estimand, a projection is counted as evidence, a directory path overrides record `paper_id`, or an amended metadata file changes result content.

## Frozen implementation hypothesis

If scientific records use a content-verified typed lifecycle DAG, then active publication claims can be counted without deleting historical adverse evidence or inflating counts through projections, cross-paper copies, schemas, manifests, and expected negative controls.

## Hostile tests

- a `supersedes` edge with a different estimand, population, outcome, decision rule, protocol, or comparator set is rejected;
- `successor_of`, `narrows`, and `adjudicates` never retire a parent;
- a projection never becomes an active leaf or diagnostic count;
- a tampered result digest is rejected;
- a historical adverse ancestor remains in the publication view;
- two directory copies of one measurement count once by canonical identity;
- record `paper_id`, never enclosing path, controls paper assignment;
- a bare ambiguous claim id is rejected;
- schemas, manifests, and negative-control expected failures are excluded from default diagnostic counts.

## Reopen triggers

Reopen if a real record cannot express its lineage without an untyped edge, if a valid correction must change the scientific result under `amends_metadata`, or if two records share a canonical measurement identity but disagree on result content.


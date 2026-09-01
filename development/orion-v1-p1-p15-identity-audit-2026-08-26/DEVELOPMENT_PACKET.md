# ORION V1 P1–P15 result-identity audit — development packet

**Date:** 2026-08-26  
**Lane:** `shadow/orion-v1-p1-p15-identity-audit-20260826`  
**Frozen repository subject:** `ef51b7b9263a72c725dc9d2045627b934b772a92`  
**Authority:** identity and byte custody only; no scientific rerun or paper promotion.

## Development question

Do all 25 result SHA fields in `papers/P1_P15_RESULT_BOUND_CLAIM_LEDGER_V1.json`
identify real Git commits whose intended result subtree, result-binding packet,
terminal, and declared artifact bytes remain exactly preserved on the frozen
`main` subject?

## Atomic fibres

1. Reject malformed, duplicate, missing, or non-commit SHA identities.
2. Verify each result commit is an ancestor of the authoritative integration
   merge and the frozen repository subject.
3. Prove the commit actually touches the named result subtree.
4. Compare the result-subtree tree OID at the result commit, authoritative
   integration merge, and frozen subject.
5. Compare the result-binding-packet blob at the result commit and frozen
   subject.
6. Check packet job identity and terminal against the writing ledger.
7. Stream every declared bound blob through Git, checking byte count and
   SHA-256 without loading large raw artifacts into memory.
8. Reject result commits that cross the computation/writing boundary.
9. Report identity closure separately from executable rerun, independent
   reproduction, novelty, rights, reviewer access, journal packaging, and
   publication readiness.

## Expert vetoes

- **Formal methods:** no row passes if job identity, terminal, ancestry, or
  result-tree identity is ambiguous.
- **Systems/reproducibility:** no prose or filesystem path is trusted over Git
  object identity and streamed bytes.
- **Execution/empirical:** this audit must never be called a rerun; external and
  protected jobs remain blocked where their packets say so.
- **Publication authority:** `paper_authority_delta = NONE`; an identity-green
  adverse or `CANNOT_CHECK` result stays adverse or `CANNOT_CHECK`.
- **Quantum transfer:** no quantum structure, physical validity, advantage, or
  cross-domain authority is created by a result hash.

## Incumbent mechanics and negative history

The ledger already requires exactly 40 lowercase hexadecimal characters, but
syntax does not establish object existence, ancestry, intended-result relation,
subtree stability, packet consistency, or artifact-byte identity. Historical
failure modes include stale hashes, title-only identity matching, result-tree
substitution, same-owner replay described as independence, and checker success
promoted into paper authority.

## Saturation challenge

A flat SHA audit could miss:

- a valid commit that does not contain the intended result;
- a later integration commit that changed one result byte;
- a packet whose terminal no longer matches the writing ledger;
- a large raw artifact that was never rehashed;
- a result commit that also edited a manuscript or authority surface;
- a complete identity record whose scientific execution remains invalid,
  censored, unavailable, or externally unverified.

The audit therefore binds commit, tree, packet, every declared blob, and the
non-implication boundary in one derived artifact.

## Frozen implementation hypothesis

A standard-library Python checker using only local Git plumbing can derive the
complete 25-row identity ledger from a full-history checkout. It can stream blob
content through `git cat-file`, making the audit independent of GitHub prose,
working-tree timestamps, and available RAM for large JSONL files.

## Falsifiers

The checker must fail on:

- a missing commit;
- non-ancestor result identity;
- result subtree absent at the named commit;
- subtree OID drift at integration or frozen `main`;
- packet blob drift;
- job or terminal mismatch;
- duplicate or unsafe binding path;
- missing blob, byte-count drift, or SHA-256 drift;
- result commit touching a protected paper/authority surface;
- any attempt to label the audit as a scientific rerun.

## Output and terminal

The workflow emits:

- `RESULT_IDENTITY_LEDGER.json`;
- `SUMMARY.json`;
- `RAW_MANIFEST.json`;
- `RESULT_BINDING_PACKET.json`.

Maximum positive terminal:

```text
P1_P15_25_RESULT_IDENTITIES_AND_BYTES_BOUND_NO_RERUN_AUTHORITY
```

This does not imply P1–P15 finalization, top-tier readiness, independent
reproduction, novelty, peer review, or ORION V1 freeze. It is the prerequisite
identity layer for the later executable and manuscript-claim audit.

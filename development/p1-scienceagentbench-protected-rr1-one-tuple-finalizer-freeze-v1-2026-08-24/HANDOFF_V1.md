# Handoff: protected RR1 one-tuple post-job finalizer freeze V1

## Immutable scope

This packet is prospective and unexecuted against protected/live evidence. It
adds one post-job metadata finalizer for task `1`, arm `RR`, attempt `1`, seed
`101`. It neither invokes nor replaces the Runner V2 918-tuple population
finalizer.

Base after the required fresh rebase:
`eba4a67e8607cdef96a2bb038d685a9a5d548599`.

## Files

- `FINALIZER_CONTRACT_V1.json`: authority, exact argv, allocation, evidence,
  parser, custody, donor, and self-binding freeze.
- `FINALIZER_OUTPUT_SCHEMA_V1.json`: exact success and typed `CANNOT_CHECK`
  field sets.
- `protected_rr1_one_tuple_finalizer_v1.py`: read-only capture plus private
  metadata finalization implementation.
- `validate_protected_rr1_one_tuple_finalizer_v1.py`: invented-metadata hostile
  suite.
- `SYNTHETIC_VALIDATION_RECEIPT_V1.json`: body-free receipt for the local
  `44/44` synthetic result.
- `BODY_FREE_EXPORT_MANIFEST_V1.json`: byte counts and hashes for the
  repository-safe export set.
- `DEVELOPMENT_PACKET.md`: full contract, evidence, and execution guide.
- `SHA256SUMS`: verification list for every exported packet file except the
  checksum file itself.

## Frozen donor bindings

The implementation loads the adapter donor from SHA-verified held bytes, then
asks it to verify its own frozen dependencies. It separately verifies the
direct-route module, contract, one-tuple finalization contract, and donor
`SHA256SUMS`. Donor lanes are never modified or invoked as a 918-tuple
finalizer.

## Required operator sequence

1. Verify this packet with `shasum -a 256 -c SHA256SUMS` from this directory.
2. Run the two predecessor synthetic validators and this hostile validator.
3. Keep all live/private evidence outside the repository on owned mode-`0700`
   storage. Do not put packet bodies, prompts, completions, token arrays,
   evaluator material, credentials, or official outcomes in this export lane.
4. Only after the one tuple has reached a terminal scheduler state, run the
   exact `capture` CLI from `DEVELOPMENT_PACKET.md`. Do not alter argv or use a
   submission command.
5. As evidence custodian, assemble the captured raw scheduler files and exact
   canonical scheduler export with the private direct-route runtime metadata.
   Preserve mode `0700` directories and mode `0400`/`0600` files.
6. Run `finalize` once with a new output root. Exit `0` means only the bounded
   one-tuple metadata-conformance receipt. Exit `1` means a typed fail-closed
   receipt. CLI misuse exits `2` without echoing private data.
7. Independently inspect the receipt hashes and claim boundaries before any
   downstream use. Never promote it to production or scientific authority.

## Exact terminal strings

Successful read-only capture:

```text
P1_SAB_PROTECTED_RR1_POST_JOB_SCHEDULER_CAPTURE_PASS
```

Successful bounded finalization:

```text
P1_SAB_PROTECTED_RR1_ONE_TUPLE_POST_JOB_FINALIZATION_PASS
```

Failed finalization emits only a typed failure code and a SHA-256 detail digest
to stderr; it never emits the underlying detail or a protected body.

## Hostile suite coverage

The `44/44` synthetic suite covers:

- raw contract/schema/normalized-module self-binding;
- exact CLI and scheduler capture argv/order/environment;
- capture rollback and output modes;
- CRLF, malformed rows, steps, duplicates, case aliases, and noncanonical
  JSONL;
- target-row absence/duplication, typed/generic/unknown GPU conflicts,
  unknown intervals, CPU-only rows, and half-open adjacency;
- scheduler configuration, resource, job identity, GPU UUID/index, and
  whole-node-claim drift;
- full 102-task plan validation before tuple selection;
- stage/process/capture/dynamic/bridge/cleanup hash chains and exact typed
  failure-pair handling;
- missing, extra, stale, or tampered source hashes and capture argv;
- symlinks, hardlinks, nonprivate modes, output-parent symlinks, and post-read
  path swaps;
- nested forbidden body/token-ID key aliases;
- explicit trap files that must never be opened; and
- runtime guards against scheduler execution, network, API, or credential
  environment access by the finalize route.

All of that is conformance evidence, not a live scheduler result.

## Frozen nonclaims

- No LUNARC job was submitted in this development lane.
- No protected generation was run or observed here.
- No packet, prompt, completion, token-ID array, evaluator material,
  credential, or official outcome body is exported.
- No whole-node, cluster-global, UUID-global, or 918-tuple non-overlap result is
  claimed.
- `production_admissibility` remains `CANNOT_CHECK`.
- `scientific_authority_delta` remains `NONE`.
- The PR must remain unmerged for immutable-head review.

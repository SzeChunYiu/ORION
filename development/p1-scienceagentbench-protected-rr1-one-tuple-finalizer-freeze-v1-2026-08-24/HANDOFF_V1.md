# Handoff: protected RR1 one-tuple post-job finalizer freeze V1

## Immutable scope

This packet is prospective and unexecuted against protected job evidence. It
adds one bounded read-only terminal watcher/capture and post-job metadata
finalizer for task `1`, arm `RR`, attempt `1`, seed `101`. Privacy-safe parser
shapes were checked against fresh read-only LUNARC Slurm 23.11.3 probes on
2026-08-24; no job was submitted. It neither invokes nor replaces the Runner
V2 918-tuple population finalizer.

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
4. Immediately after a job ID is issued by a separate authorized submission
   path, start the exact `watch-capture` CLI from `DEVELOPMENT_PACKET.md`. The
   watcher accepts no partition or node input, polls only the frozen read-only
   allocation query, derives one node from the unique terminal row, and then
   starts the first post-job `scontrol` within two monotonic seconds and before
   persisting/fsyncing terminal `sacct`. Every command is limited to 20 seconds
   and the five-command sequence to 240 seconds, a 60-second margin below live
   `MinJobAge=300`. Do not alter argv or use a submission command.
5. Keep the resulting capture root separate from the private direct-route
   runtime evidence root. Do not hand-author or copy a scheduler export; the
   finalizer constructs its canonical record and complete source map.
6. Run `finalize` once with both roots and a new output root. Exit `0` means only the bounded
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

Failed watcher/finalizer execution emits only a typed failure code and a
SHA-256 detail digest to stderr; it never emits the underlying detail or a
protected body. A late watcher failure retains safely created mode-`0400` raw
files plus one body-free `SCHEDULER_CAPTURE_CANNOT_CHECK_V1.json` manifest.

## Hostile suite coverage

The `44/44` synthetic suite covers:

- raw contract/schema/normalized-module self-binding;
- exact CLI and repeated scheduler poll/capture argv/order/environment;
- empty/PENDING/RUNNING/terminal watch sequencing, bounded retry exhaustion,
  step/multiple-row rejection, derived-node ambiguity, first-`scontrol` launch
  before terminal persistence, two-second first-command latency, 20-second
  command timeouts/durations, 240-second deadline, UTC/monotonic provenance
  arithmetic/tamper rejection, partial-failure terminal retention, and
  capture/finalizer output modes;
- CRLF, malformed rows, steps, duplicates, case aliases, and noncanonical
  JSONL;
- target-row absence/duplication, typed/generic/unknown GPU conflicts,
  unknown intervals, CPU-only rows, and half-open adjacency;
- byte-faithful Slurm 23.11.3 config header, task-plugin list, `AllowAccounts`,
  24-field/no-trailing-delimiter `sacct`, blank `NTasks`, raw `ReqMem=64G`,
  space-bearing node values, resource, job identity, GPU UUID/index, and
  whole-node-claim drift;
- full 102-task plan validation before tuple selection;
- stage/process/capture/dynamic/bridge/cleanup hash chains, donor capture clock
  and base-record invariants, cross-bound request hashes, exact authorities,
  GPU top-level shape, and exact typed failure-pair handling;
- missing, extra, stale, or tampered source hashes and capture argv;
- symlinks, hardlinks, nonprivate modes, output-parent symlinks, post-read path
  swaps, distinct path/held-directory identities, and post-read
  owner/mode/link-count/identity checks;
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

# Evidence resolution mixed two file occasions

## Observed

At `HEAD` `670afb6bacd1899ee8e4d62ceb5672a10f8f319d`, a hostile
resolver seam rewrote a local artifact after `artifact_digest()` returned but
before the later `read_text()` call. The legacy resolver returned:

```text
status                         RESOLVED
actual_digest_is_original      True
content_is_replacement         True
digest_matches_returned_content False
```

Thus one `EvidenceResolution` claimed the SHA-256 of occasion A while carrying
the text of occasion B. A second probe showed that `b"\xff"` and `b"\xfe"`
have different byte digests but both become the same replacement-text view
`"�"` under `errors="replace"`.

## Failure class

`EVIDENCE_OCCASION_TOCTOU` + `DIGEST_CONTENT_SPLIT` +
`LOSSY_BINARY_PROJECTION` + `PATH_CHECK_USE_GAP`.

## Cause

The working-file path validates and hashes a pathname in one operation, then
opens that pathname again for text. Path containment and `is_file()` are also
checks separated from the later opens. A rename/symlink substitution can change
the opened object, and replacement decoding destroys exact binary identity.

## Correct response

- Keep the legacy resolver diagnostic only.
- Open the host root and each path descriptor-relative with no-follow
  semantics; require one regular-file descriptor.
- Derive bytes, full digest, byte length, and optional strict text view from the
  same retained immutable byte buffer.
- Compare descriptor metadata around the read and preserve instability as
  `CHANGED_DURING_CAPTURE`/later `CANNOT_CHECK`.
- Retain every unresolved request and bind host-owned roles, obligations, root
  configuration, policy manifest, authority revision, and support revision in
  an acyclic snapshot identity.

## General lesson candidate

A digest is not an evidence occasion. Identity metadata and payload must be
derived from one captured object; otherwise an individually correct digest and
an individually real payload can compose into a false record.

## Residuals and reopen coordinates

- descriptor metadata cannot prove that a privileged writer did not change and
  restore a file during one read;
- hard-link policy and platform-specific stronger resolution (`openat2`,
  filesystem snapshots) remain later hardening fibers;
- sequential live-file captures are not a simultaneous multi-file snapshot;
- Task 8 must make frozen bytes durable without creating blob/manifest atomicity
  gaps.

## Hostile repair deltas retained from Task 3

The first protected-capture draft generated additional falsifiers. They remain
part of the negative history even though the draft was repaired:

1. **`ROOT_REGISTRATION_SYMLINK_FOLLOW`.** Calling `Path.resolve()` before the
   protected root open followed a configured root symlink in a separate
   pathname occasion. Later `O_NOFOLLOW` therefore checked an already rewritten
   pathname. The protected root is now opened component by component from `/`
   without lexical resolution; unavailable no-follow primitives fail closed.
2. **`COMPACT_SOURCE_REF_ALIAS`.** Splitting
   `<scheme>:<path>@<declaration>` at a delimiter made path/ref identity
   ambiguous and stripped internal boundary whitespace. Protected V1 now uses
   host-owned typed source registrations; candidate source IDs are opaque.
3. **`GIT_MIXED_COMMIT_OCCASION`.** Resolving one mutable Git branch per path
   can combine files from different commits in one claimed snapshot. Resolution
   is now cached once per `(root, canonical ref)` and reused for every path.
4. **`GIT_OBJECT_PATH_HASH_MISMATCH`.** A scratch Git repository accepted raw
   bytes stored under the wrong loose-object pathname: `git cat-file` returned
   the substituted bytes while `git fsck` diagnosed a hash-path mismatch. The
   capture path now disables replacement objects/lazy fetch, traverses the raw
   frozen commit/tag/tree/blob chain, and independently recomputes every typed
   Git object ID. Git SHA-1 remains only a source coordinate; final bytes receive
   an independent SHA-256 content descriptor.
5. **`SNAPSHOT_CAP_STATUS_ERASURE`.** The first cap implementation retained a
   cumulative over-limit counter, so every record after the first overflowing
   payload was relabelled `TOO_LARGE`, including a later genuinely missing
   artifact. The cap now discards only the payload that would exceed the stored
   byte budget and preserves every later terminal failure status.
6. **`GIT_DESCRIPTOR_PATH_REOPEN`.** Passing only the registered repository
   pathname to Git reopened a mutable path after the host had approved a
   descriptor. A swap/restore probe could therefore make the protected command
   inspect a different repository occasion. Protected Git now validates and
   `fchdir`s the inherited `.git` descriptor in an isolated helper before
   executing an absolute, host-selected Git binary.
7. **`GIT_PIPE_BUDGET_AMPLIFICATION`.** Per-command output limits still allowed
   a sequence of individually bounded Git commands to consume unbounded total
   stdout/stderr. Shared snapshot counters now cap command starts, stdout,
   stderr and elapsed time; usage and exhausted coordinates are part
   of snapshot identity.
8. **`DEADLINE_AS_REPOSITORY_FAILURE`.** When the shared elapsed-time deadline
   expired inside a Git subprocess, the first draft returned `timed_out` but
   omitted the exhausted coordinate. Revision resolution then misclassified
   the event as `NOT_A_REPOSITORY`. Deadline expiry now yields
   `WORK_BUDGET_EXHAUSTED` and an `elapsed_ns` exhaustion receipt. The same
   checks now bracket root and local-file operations. Blocking local syscalls
   are not preempted; a returned overrun is censored rather than silently
   admitted. Empty/unmapped/error paths still record the exhausted coordinate;
   an I/O error returned after the deadline cannot bypass censoring.
9. **`GIT_UNBOUND_ADMIN_INDIRECTION`.** Valid Git mechanisms can move the
   effective object/configuration roots outside the opened `.git` descriptor.
   Scratch repositories using `objects/info/alternates`, `commondir`,
   `[include]`, or `[includeIf]` all resolved successfully under the first
   draft. Protected V1 now refuses them as `UNSUPPORTED_GIT_LAYOUT` until all
   external roots can be safely opened and committed. Bare repositories are
   also classified as valid-but-unsupported, not as nonexistent repositories.
10. **`EXECUTION_IDENTITY_BOUNDARY_MIXUP`.** The helper source was fixed in
    code, but its interpreter path and the Git path were not artifact
    identities. Replacing launcher bytes at the same pathname left the root
    configuration hash unchanged. The configuration now binds paths, bounded
    executable bytes, local descriptor metadata and SHA-256 digests for both
    launchers, plus the inline helper source digest. A residual exec-time
    pathname race and the unbound dynamic-loader/library/OS closure remain.
11. **`VERIFIED_OBJECT_CACHE_BUDGET_DUPLICATION`.** The cache was present but
    lacked an end-to-end discriminator. Two paths sharing one blob now prove
    that only the already size/type/OID-verified object is reused, with one
    object read and one distinct-object/byte charge.
12. **`PROCESS_LIMIT_AS_REPOSITORY_ABSENCE`.** A per-command timeout or output
    limit with a still-live snapshot budget carried `returncode=None`; revision
    resolution rounded that operational limit into `NOT_A_REPOSITORY` or
    `COMMIT_NOT_FOUND`. Process limits now remain `UNREADABLE_ARTIFACT`, while
    shared snapshot exhaustion remains the separate
    `WORK_BUDGET_EXHAUSTED` outcome.
13. **`WORK_RECEIPT_COORDINATE_INJECTION`.** Direct snapshot construction
    initially accepted arbitrary usage/exhaustion coordinate names. That made a
    supposedly typed work receipt an open-ended payload surface. Both coordinate
    domains are now closed enumerations with unique, nonnegative values.
14. **`TAG_DECLARED_EDGE_TYPE_IGNORED`.** The first annotated-tag parser
    validated that a declared target type was `commit` or `tag` but did not
    compare it with the target object's actual type. A hash-valid outer tag
    declaring `commit` while pointing to another tag therefore peeled to
    `RESOLVED`. Every declared tag edge is now checked against the independently
    queried target object type.

## Failure-learning boundary

These observations do not all support the same lesson. A demonstrated object
substitution, identity mismatch, or unsafe accepted indirection is negative
evidence about the implementation. By contrast, `WORK_BUDGET_EXHAUSTED`, a
missing capability, a refused unsupported layout, or an unavailable external
dependency means the target was **not fully examined**. Such episodes must
remain available for retry/replanning and resource-policy learning, but they
must not increment evidence that a scientific mechanic, source, or research
route failed. Repeated censoring is evidence about the budget/instrument only.

Regression discriminators live in
`tests/unit/kernel/test_evidence_snapshot.py`; passing them proves only these
bounded capture properties, not evidence relevance, scientific truth or
transition authority.

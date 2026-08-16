# Flattened projection cannot reverse supersession

## Observed

At exact branch base `970328b907b8a8c658396bdddaba292964da5472`, a
two-round probe applied `r1`, then applied the linear chain `(r1, r2)` to the
already-mutated cells with `r2 supersedes r1`. The resulting mechanic contained
both contributions:

```text
True True
```

The booleans mean that both `only-r1` and `only-r2` remained in
`mathematical_semantics`. A same-round test starting from the untouched seed had
passed because the reducer selected only the tip; it did not exercise a later
round starting from flattened prior state.

## Failure

The old application path unions a tip into current cells. Once the source of a
value has been flattened away, it cannot know whether that value came from the
seed, the superseded record, or another active coordinate. A record-id-to-hash
catalog and active-tip label do not contain enough information to remove only
the superseded contribution.

## Failure class

`LOSSY_STATE_FLATTENING` + `NON_REVERSIBLE_SUPERSESSION` +
`SAME_ROUND_TEST_FALSE_ASSURANCE`.

## Correct response

- Retain the exact immutable seed.
- Retain the complete structurally valid `AnswerRecord` graph and recomputed
  body hashes; only a later authorized commit makes a proposed post-state active.
- Derive active tips from validated record coordinates and supersession edges.
- Recompute materialized cells from seed plus active tips; do not incrementally
  subtract from a provenance-free flattened tuple.
- Test supersession across committed rounds, including values also owned by the
  seed or another active record.

## General lesson candidate

An irreversible projection is not a sufficient state for a reducer that
promises selective replacement. Reversibility requires retained causes or an
equivalent ownership algebra, not only the latest flattened effect.

## Residuals and reopen coordinates

- Task 4 must implement and test pure re-derivation; Task 2 only supplies the
  normal form.
- Accepted-record membership still requires later relying-party authorization.
- Compaction may remove bodies only if an equivalent replayable contribution
  manifest and negative-history addressability survive.

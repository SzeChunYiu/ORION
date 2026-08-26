# Public-reference atlas build, 2026-08-22

The build had never been run with a corpus. Every previous invocation produced
an empty pool, and the report that came back said so in four blockers at once,
which reads as a build that is far from working rather than one that had simply
never been given an input.

## What changed

SciFact's published release was retrieved and passed to the build. The pool went
from **0 candidate cases to 957**, and case selection reached the frozen target
of **32 of 32** for the first time.

| Blocker | Before | After |
|---|---|---|
| authoritative candidate pool produced 0 < target 32 | blocking | **cleared** (957 candidates, 32 selected) |
| atlas must contain both merge-compatible and non-merge authoritative cases | blocking | **cleared** (`COMPATIBLE` and `CONTRADICTORY` both present) |
| only 0 discipline strata available; need at least 3 | blocking | 1 of 3 |
| only 0 case family available; need at least 2 | blocking | 1 of 2 |

Selected-case digest: `db962e4dcc4b3c00690a499bba370fdd257a9589b45fcad029a80369e84b1bc9`.

## Status: still CANNOT_CHECK, and now for one reason instead of four

Two blockers remain and they are the same blocker twice: SciFact is a single
discipline (`scientific_claim_verification`) contributing a single case family
(`polarity_modality_attribution_context`). The coverage gate wants three
disciplines and two families, so it needs the other two pinned corpora --- MUSE
(`cohentsofia/MUSE`) and SciSchema (`scischema/scischema`).

Neither could be retrieved here. The environment's network policy answers `403`
to `codeload.github.com` and to `huggingface.co`; the SciFact release is served
from S3, which is why it alone was reachable. This is an access blocker, not a
scientific one, and it is the whole of what stands between this build and a
`READY_FOR_FREEZE` atlas: the adapters for both corpora exist, are tested, and
are already exercised by the v1.1 build.

## A provenance defect found by running it

The build stamped a pinned upstream revision onto whatever file it was handed.
`"revision": SCIFACT_REVISION` was written unconditionally while `content_hash`
was computed from the input, so an atlas built from an edited, truncated or
wrong-version corpus recorded the pinned revision anyway --- and every case's
`DERIVED_FROM_ALLOWED` authority cited that revision as its evidence. The
provenance was asserted, not checked, which is the failure this programme exists
to refuse, sitting inside the instrument that is supposed to enforce it.

Provenance is now verified against bytes. A file whose digest matches no
declared pin is refused, and the refusal names the digest it saw so a pin can be
added deliberately. What reaches a case record is what has actually been
established: a commit hash is not recoverable from a release tarball, so the
SciFact pins carry `sha256:<digest>` together with the URL those bytes came
from. Promoting one to a commit hash means checking the file out of the upstream
repository at that commit and comparing digests --- which is exactly what the
network policy above currently prevents.

The three original revision constants are kept, renamed to say what they are, and
are no longer reachable from the emit path.

`protocol/PUBLIC_REFERENCE_GOLD_V1.md` still names the three intended upstream
revisions. That is a declaration of what the protocol means to use and is left
as written; the change here is only that a case can no longer claim one of them
without the bytes to back it.

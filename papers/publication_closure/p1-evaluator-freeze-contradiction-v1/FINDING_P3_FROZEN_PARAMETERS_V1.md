# The same failure mode, twice: a digest frozen over repository paths

`tests/unit/study/p3/test_partial_observation_probe.py::TestFreezeBinding::test_runner_digest_matches_the_frozen_twin`
is a second instance of what
`FINDING_V1.md` documents for ORION-01's evaluator, and this one is provable to the
digit rather than argued.

## The numbers

| | value |
|---|---|
| the twin records | `2dc106eee03666ccec7ec7df53a96933814418a296e30be43ad1a81f2e089d21` |
| current `frozen_digest()` | `66973cf106f80729ab95fb697f87183bcc1d7526a9839b123cd59d37f0af8e03` |
| `frozen_digest()` at the **pre-R0** commit `7b97888f3` | **`2dc106eee03666ccec7ec7df53a96933814418a296e30be43ad1a81f2e089d21`** |

The twin's recorded digest is exactly the pre-R0 digest. Nothing is ambiguous here:
the freeze is intact and the thing it froze moved.

## What moved

R0 (`3a1a83178`) changed **13 lines** of
`src/orion/study/p3/partial_observation_probe.py`, every one of the form

```
- "papers/paper-03-global-knowledge-portrait/protocol/"
+ "papers/orion-13-global-knowledge-portrait/protocol/"
```

Those strings live **inside `FROZEN_PARAMETERS`**, in seven entries:
`freeze_document`, the four `amendments[i].document` records, and
`intact_sources.*`. `frozen_digest()` is `sha256_json(FROZEN_PARAMETERS)`, so
renaming a directory changed the digest of the frozen parameters.

The file is byte-for-byte the same length before and after, because `paper-03` and
`orion-13` are both eight characters. The rename was invisible to a size check and
fatal to a digest.

## Why this one has no clean revert

The ORION-01 case at least admitted a revert: that evaluator's changed lines were
self-contained prose, so restoring them restores the freeze at the cost of one file
keeping legacy names.

Here the changed strings are **provenance records naming repository locations**,
and those locations genuinely moved. Reverting them makes `FROZEN_PARAMETERS`
name paths that no longer exist — the digest would match and the provenance would
be false. Keeping them makes the provenance true and the digest wrong. The freeze
cannot be satisfied and be honest at the same time.

## The general lesson, which is the reportable part

**A digest frozen over a structure that embeds repository paths cannot survive a
repository reorganisation, even one that changes nothing scientific.** Two
independent freezes in this repository broke this way in the same commit, for the
same reason, and both are still broken. The parameters that matter — the
coordinate semantics, the absence readings, the amendment chain — are unchanged;
only the addresses of the documents describing them moved.

A freeze that binds *what was decided* survives a rename. A freeze that binds
*where the decision is filed* does not. The two were not separated here.

## Not repaired

Three options, all with costs, and none is a mechanical call:

1. re-pin the twin — destroys what the freeze was for, and is the error reverted in
   #1810;
2. revert the paths — restores the digest and falsifies the provenance;
3. split the frozen structure so paths are recorded outside the digested part —
   correct going forward, but it changes what the freeze means and cannot be done
   retroactively without re-pinning.

`test_p1_p5_successor_readiness[P3]` and `[P4]` report
`LOCAL_PREOUTCOME_CHECK_FAILED` downstream of this and need no separate
diagnosis.

Both failures should be read as **correctly reported freeze violations**, not as
unfixed digests.

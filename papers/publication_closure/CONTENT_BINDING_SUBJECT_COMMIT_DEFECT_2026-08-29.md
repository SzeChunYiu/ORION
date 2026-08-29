# The content-binding subject-commit pin is unverifiable on `main`

**Date:** 2026-08-29 · **Severity:** structural · **Status:** diagnosed, not patched

`check_content_binding_v1.py` makes two independent assertions per candidate paper:
that each bound file's SHA-256 matches `SHA256SUMS`, and — when the manifest records
`subject_commit_status: BOUND` — that those files' bytes equal their content at the
named `subject_commit`. **The first assertion is sound. The second is not being
evaluated on `main`, and where it can be evaluated it currently fails.**

## What CI sees, and what a full clone sees

`p6-p8-candidate-ci` reports `candidate-theory` SUCCESS on `main` at `f17dc68ee` and
at `7c472e3a2`. Running the identical checker against a clone of the same commit
reports `FAIL (P6)`:

```
P6: subject_commit_status claims BOUND but these differ from 541e42630...:
    revalidation/graph-quality-law-v1/{CLAIM_DISPOSITION.md, PROTOCOL.json,
    RESULT_V1.json, THEORY.md, check_graph_quality_law.py}
```

Both are behaving as written. The checker guards the comparison:

```python
if not _commit_exists(repo_root, recorded_commit):
    report.cannot_check.append(f"subject_commit {recorded_commit} not in this object "
                               "database (shallow clone or export); ...")
elif committed.get("subject_commit_status") == "BOUND":
    drifted = commit_disagreement(...)
    if drifted: report.errors.append(...)
```

`cannot_check` does not fail the run. `541e42630` is **not an ancestor of `main`** — it
was #1684's branch base, and the squash-merge that produced `7c472e3a2` orphaned it. A
CI clone cannot resolve it, so the strongest assertion silently downgrades to
"could not check" and the job is green. A clone that happens to hold the commit — one
that has fetched the branches — resolves it and finds five files genuinely drifted.

This is the "could not check reported as checked and fine" failure mode, and it is
load-bearing here: the one real drift in the candidate set is behind it.

## It is not one packet — it is four of six pins

| Paper | Manifest | `subject_commit` | Ancestor of `main`? |
|---|---|---|---|
| ORION-16 | `CONTENT_MANIFEST_V1.json` | `541e42630` | **orphaned** — and drifted |
| ORION-16 | `CONTENT_MANIFEST_V2.json` | `0941a0dee` | **orphaned** |
| ORION-17 | `CONTENT_MANIFEST_V1.json` | `622969a2d` | **orphaned** |
| ORION-17 | `CONTENT_MANIFEST_V2.json` | `3fad64d47` | ancestor |
| ORION-18 | `CONTENT_MANIFEST_V1.json` | `622969a2d` | **orphaned** |
| ORION-18 | `CONTENT_MANIFEST_V2.json` | `d6a1e08f4` | ancestor |

Only ORION-16 V1 shows actual byte drift; the other three orphaned pins still match
their commits when those commits are resolvable. So the immediate damage is one packet,
but the blind spot covers four.

## Why this cannot be fixed by re-pinning

`CONTENT_MANIFEST_V1.json` is **one of its own 81 `bound_files`**. Editing the manifest
to correct `subject_commit` changes the manifest's own bytes, so no commit that already
exists can satisfy the new pin — the only commit whose tree matches is the one the edit
has not yet created. The pin is therefore structurally always one commit stale, and a
squash-merge converts "one commit stale" into "orphaned and unresolvable".

`541e42630` is itself titled *"fix(ci): reconcile content-binding digests after the
manuscript PDF refresh"*, which is the same reconciliation being run again — the loop
has been walked before, and it does not terminate.

Three exits, none of which should be chosen unilaterally:

1. **Exclude the manifest from its own `bound_files`.** Breaks the circularity; weakens
   self-binding, which may be deliberate.
2. **Land a follow-up re-pin commit after each merge.** Keeps the invariant, costs a
   commit per merge, and still breaks under squash.
3. **Make an unresolvable `subject_commit` an error, not `cannot_check`.** Honest, and
   it would have caught this — but it reddens CI on `main` immediately for four pins,
   so it needs the drift fixed first.

The programme's own rule is that "could not check" must never read as "checked and
fine", which argues for (3) once (1) or (2) has cleared the backlog.

## Not claimed

That the digests are wrong. They are not: an independent verification of all 81
`SHA256SUMS` entries against blob content passed 81/81, with a 76/76 control. The
defect is confined to the commit-identity layer above them. Nor is it claimed that
ORION-16 V1's five drifted files are wrong in content — only that they no longer match
the commit the manifest names.

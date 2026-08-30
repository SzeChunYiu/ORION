# ORION-03 round-2 trust-store binding verification V1

**Date:** 2026-08-30 · **Repo commit:** cd4ce5a5a

Discharges the #1701 box "Verify the 1,962 external trust-store merge tasks and
46 hybrid obstructions remain bound."

## Result: every bound artifact verifies

| Check | Result |
|---|---|
| `TASK_MANIFEST_V2.json` task count | **1962** — matches the manuscript's 1,962 |
| `ROUND2_RESULTS_V2.json` hybrid_tasks | **46** — matches the manuscript's 46 |
| `frozen_artifacts` local digests | **5/5 MATCH** |
| `results_artifacts` local digests | **10/10 MATCH** |
| `vendored_files` + `vendored_recipe` upstream digests | **253/253 MATCH** |
| Independent-run byte identity | **3/3 IDENTICAL** |

## Method

**Counts recomputed from data, not read from prose.** Both figures were
recounted directly out of the JSON records rather than taken from
`MANUSCRIPT_V2.md`, so agreement between the two is evidence, not restatement.

**Local digests.** All 15 paths recorded in `SOURCE_BINDING_V2.json` under
`frozen_artifacts` and `results_artifacts` were re-hashed from the working tree
and compared to the recorded value. No mismatches, no missing files.

**Upstream digests — exhaustive, not sampled.** The remaining 253 paths (252
`vendored_files` plus 1 `vendored_recipe`) are OpenSSL sources, pinned in
`source.commit` to `d3c1b1169b3569ff3069e5b399f47b2b28e03d79`. They are not in
this repository, so a local check would only ever return "not found" — which is
`CANNOT_CHECK`, not a pass. Each was therefore fetched from
`raw.githubusercontent.com/openssl/openssl/<commit>/<path>` and hashed. All 253
match. This is the half of the binding that a repository-local checker cannot
see, and it is the half that would silently rot if upstream history were
rewritten.

A preceding 8-file random sample (seed 20260830) also matched; the exhaustive
run supersedes it.

**Independent-run identity.** `ROUND2_RESULTS_V2`, `COST_ROUND2_V2` and
`INDEPENDENT_REPRO_R2` each have a `.run2.json` replica. All three pairs are
byte-identical, so the 46/1962 figures are reproducible across runs and not an
artifact of one execution.

## Scope

Verification of **binding integrity**, not of the scientific claim. It
establishes that the artifacts behind "46 hybrid cases among 1,962 third-party
OpenSSL trust-store merge tasks" are unmodified and still bound to the upstream
commit they name. It does not re-derive the merge obstructions themselves, and
it takes no position on whether the obstruction result is correct.

The selection rule is content-based (`vendored iff >=1
CERTIFICATE/TRUSTED-CERTIFICATE/X509-CRL PEM block and no private-key block`)
and was not re-executed here; that would be a separate check of whether the
252-file corpus is the right corpus, as opposed to whether it is intact.

**Terminal:** `TRUST_STORE_BINDING_INTACT__253_OF_253_UPSTREAM_VERIFIED`

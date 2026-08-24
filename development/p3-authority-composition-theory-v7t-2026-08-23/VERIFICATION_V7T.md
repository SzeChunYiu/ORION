# P3 V7T verification

## Scope

Scientific artifact verification only. No pytest, repository CI, build, Git
mutation, protected outcome access, or manuscript-checkout edit was performed.

## Checks

1. `finite_countermodel_v7t.py` enumerated two admissible worlds, one observed
   local signature, all local gates true, and global identified set `{0,1}`.
2. `validate_v7t.py` passed **32/32** static scientific checks.
3. All unchanged frozen V5/V6 result hashes matched.
4. A peer manuscript edit after the protocol freeze changed the frozen
   `06-results.tex` hash. The mismatch is preserved in
   `PROTOCOL_MANUSCRIPT_SOURCE_REBIND_V7T_A1.json`; the current source was
   rebound before the patch was rebuilt.
5. The rebuilt patch applies cleanly under non-mutating `git apply --check`.
6. The patch has no duplicate theorem labels in the patched fragments, defines
   its new bibliography key, and does not duplicate the V6 results prose that
   is already present in the current manuscript snapshot.
7. Crossref's direct DOI record and reported CC-BY-4.0 licence were parsed. The
   literature claim uses only metadata/abstract authority; HTTP 403 on the
   publisher PDF is preserved.
8. `RESULT_V7T.json` retains 2/3 native smoke, 0/3 scientific comparator
   readiness, no performance scoring, no gold/protected outcome, novelty
   `CANNOT_CHECK`, and `NOT_SUBMISSION_READY`.

## Result

`PASS_32_OF_32__PATCH_READY_FOR_SEPARATE_REVIEW_NOT_APPLIED`

This is same-lane verification. It is not an independent proof or novelty
review.

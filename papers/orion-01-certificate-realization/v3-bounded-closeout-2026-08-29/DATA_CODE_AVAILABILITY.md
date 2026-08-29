# Data and code availability

The bounded V3 package uses no external experimental dataset.

The implementation-independent theorem checker and its tests are included in this directory. They use Python's standard library and import no ORION or PyZX production module.

The compiler-side R6M upper/lower evidence is bound to repository paths named in both manuscripts and in `SUBMISSION_MANIFEST_V3.json`. The capped Round-2/Round-3 execution is bound to PR #1602, source commit `9e9b870b795b6ae0b3726031ced0b9ebef004897`, its aggregate SHA-256, its task custody receipt, and `PR1602_ADOPTION_RECEIPT.json`.

The source branch was substantially stale and diverged when issue #1701 was inspected, so it is not wholesale-merged. The exact Round-2/Round-3 development evidence paths have been transplanted from the immutable source commit; `development/orion-01-pr1602-evidence-transplant-2026-08-29/TRANSPLANT_MANIFEST.json` binds every source blob, byte length, and SHA-256. This does not change the scientific terminal `CANNOT_CHECK_MOVE_COMPLETENESS`.

Generated PDFs are derivable from the Markdown sources using `COMPILE.md`. A release must retain the generated manifest and `SHA256SUMS` and must record visual inspection separately.

No claim of external replication, external proof review, production move completeness, or submission acceptance is made.

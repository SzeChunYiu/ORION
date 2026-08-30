# PR #1817's ORION-18 manifest correction: superseded, with reason

PR #1817 (`fix/orion18-v2-false-bound`) proposed three changes to
`papers/orion-18-epistemic-authority-autonomous-science/CONTENT_MANIFEST_V2.json`:

1. `subject_commit_status: BOUND -> CANNOT_CHECK`, with blocker
   "bound files differ from the recorded commit";
2. removal of three bound files (the `authority-cut-identifiability-v1`
   theory packet);
3. reversion of `check_negative_null_history_v1.py` from `698e326ab` back to
   `38d131ffd`.

**The diagnosis was correct when it was made, and is no longer correct.**

#1817 was cut against subject_commit `d6a1e08f`, where the bound files genuinely
did not match. PR #1786 subsequently re-derived the manifest against
`685ec3141` — repairing the cause rather than downgrading the status.

**Verified on current main:** all **89 of 89** bound files match their recorded
digests at `685ec3141` — zero mismatches, zero absent. The `BOUND` status is
true as recorded, so change (1) would regress a valid binding to
`CANNOT_CHECK`.

Change (2) would remove three files from binding, reducing rather than
increasing what is content-bound. Change (3) would revert the rename-aware
negative-history checker fixed in #1855 to its known-buggy predecessor.

**Disposition:** the manifest changes are superseded. The reachability checker
`check_content_binding_reachability_v1.py` and its `REACHABILITY_V1.json` are
**adopted** — they are independent of the manifest question and add a check main
did not have.

This record exists so the "false BOUND" finding is preserved as history rather
than silently dropped: it was a real defect, it was fixed, and the fix is
verified above.

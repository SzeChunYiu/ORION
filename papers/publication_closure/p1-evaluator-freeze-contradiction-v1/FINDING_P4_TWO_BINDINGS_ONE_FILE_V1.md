# The third instance: a submission package and a frozen protocol claim the same file

`test_p1_p5_successor_readiness[P4]` is the last CI failure on `main` that is not a
missing fix. It is the same R0 failure mode as ORION-01's evaluator
(`FINDING_V1.md`) and ORION-13's frozen parameters
(`FINDING_P3_FROZEN_PARAMETERS_V1.md`), and it is the one that cannot be repaired
by either side yielding.

## The file, and its two claimants

`papers/orion-14-verified-scientific-discovery/evidence/audit/P4_H3_V3_CLAIM_AXIS_ADJUDICATION_2026-08-22.json`

| claimant | declares | what it is |
|---|---|---|
| `protocol/P4_NATURALISTIC_IDENTIFIABILITY_SUCCESSOR_V1.json` → `V3_EXACT_AXIS_ADJUDICATION` | `c0c32de0…` | a **frozen pre-outcome successor protocol** |
| `journal_package/SHA256SUMS` and `journal_package/history/SHA256SUMS_2026-08-24.txt` | `128c22ae…` | the **submission package** |

The file currently hashes `128c22ae…`. `c0c32de0…` is its content at `2bab2148f`
— R0's *git mv* wave, where files moved but content was intact — before
`3a1a83178` renamed identifiers inside it.

So the successor protocol names the record as it was when frozen, and the journal
package names it as R0 left it. **Both are internally consistent. No content of that
file satisfies both.**

Note that ORION-14's paper root has **no `SHA256SUMS` at all**; the only digests
over this file are the two above. The drift the ratchet reports is not a stale
checksum list, it is this disagreement.

## Why neither side yields mechanically

- **Restoring the file** to `c0c32de0…` fixes `successor_readiness[P4]` and breaks
  the journal package's checksums. That is what the package-currency ratchet
  forbids in as many words: *rebuild the package — do not rewrite its digests to
  match the moved files, which would delete the evidence that it moved.* Verified:
  restoring it turned ORION-14 from `stale: 0` to `stale: 1` and added it to the
  drift set.
- **Re-pinning the successor protocol** to `128c22ae…` is re-pinning a frozen
  pre-outcome protocol to whatever the artifact now says, which is the error
  reverted in #1810 and refused twice already in this repair series.
- **Rebuilding the journal package** around the restored record is the action the
  ratchet actually asks for. It is also a submission-package rebuild on a paper
  being prepared for a journal, which is that lane's decision and not a side effect
  of a P3/P4 CI repair.

## What was done instead

Nothing to ORION-14. The two ORION-13 records in the same family were restored,
because their only claimant was the successor protocol and nothing else bound
them; that fixed `successor_readiness[P3]` and both `p3` freeze tests, and tripped
no ratchet. ORION-14's record was explicitly reverted back out of that change
(#1844) once the ratchets fired.

`successor_readiness[P4]` therefore stays red **by decision, not by omission**, and
this document is the decision.

## The pattern, now three for three

R0 renamed identifiers inside artifacts that other records bind by content hash. In
ORION-01 the collision was between a frozen protocol and code constants; the code
yielded and the artifact was restored (#1846). In ORION-13 it was between a frozen
twin and a derived lifecycle; the derived artifact yielded (#1844). Here it is
between a frozen protocol and a submission package, and **a submission package is
not a derived artifact** — rebuilding it is a publication act.

That is the whole lesson of this series: a rename is safe only where nothing binds
the renamed bytes, and R0 could not have known which those were because the
bindings live in three different vocabularies — code constants, derived manifests,
and package checksums.

# ORION-17 density-prospective-v1 — relocation record

**Relocated:** 2026-09-01, on the branch that lands this packet.

**From:** `papers/orion-17-epistemic-navigation-open-worlds/theory/density-prospective-v1/`
**To:** `papers/publication_closure/orion17-density-prospective-v1/`

## Why the packet could not stay inside the paper

ORION-17 is a directly bound paper (`DIRECT_BOUND_PAPERS`), so every file under
`papers/orion-17-epistemic-navigation-open-worlds/` must be covered by a binding
that a checker can verify. `bound_paths` in
`papers/candidates/checkers/check_content_binding_v1.py` enumerates that tree with
`rglob("*")`, so ten additional files made the P7 V1 subject drift and dropped the
paper from `BOUND_CURRENT` to `BOUND_PARTIAL` — *"122 of 132 files are bound and all
match; the other 10 can change without any check noticing."*

The checker offers one additive route: bind the files in `CONTENT_MANIFEST_V2.json`,
which `successor_v2_paths` then excludes from V1's enumeration. **That route was
examined and rejected here**, because P7's V2 manifest carries a load-bearing
`subject_commit` (`2b4cde64…`) and `_subject_identity` resolves every bound file
through `git show {commit}:{path}`. Files that exist at no commit on `main` cannot be
bound to a reachable pin, and this repository squash-merges, so a pin written on a
branch is destroyed at merge — the archive-pin defect that
`tests/unit/programme/test_content_binding_pin_is_reachable.py` now guards against.
Binding in V2 would have passed pull-request CI and turned `main` red.

Relocation needs no binding change at all, and it follows the precedent already set
for `ORION17_SEAL_INTEGRITY_DIAGNOSIS_V1.md`, which was moved to
`papers/publication_closure/` for the same reason.

## What the relocation did not change

The packet's own independent checker resolves its inputs from `__file__`, so it is
position-independent. Re-run from the new location it returns `status: PASS`,
`correct: "5/5"`, all four checks true, and all four negative controls firing —
`an_inverted_rule_would_score_worse`, `size_rule_would_mispredict_at_least_one`,
`both_outcome_classes_occur_in_the_held_out_set`, and
`training_domains_are_separated_by_the_same_threshold`. Every byte of every packet
file is unchanged; only the directory prefix moved.

## Reading the receipts

`CHECKER_EXECUTION_RECEIPT_V1.md` and `RECOVERY_AND_CHRONOLOGY_VERIFICATION_V1.md`
were written before the move and name the old path. They are attestations about a
historical state and have deliberately **not** been edited: rewriting a receipt to
match a later tree is how a receipt stops describing what was actually checked. Read
`theory/density-prospective-v1/` in those two documents as this directory.

Two files inside ORION-17 also name the old path —
`external-cohort-v1/NOTE_V1.md` and `external-cohort-v1/fetch_builder.sh`. Both are
bound in `CONTENT_MANIFEST_V2.json`, so editing either would break the paper's commit
pin for all 123 bound files. They are documentation cross-references rather than
executable dependencies, and they are left exactly as they are.

## Terminals, unchanged by this move

- Scientific terminal, from `RESULT.md`: `READY_TO_SUBMIT_TOP_TIER` (evidence).
- Filing terminal, from `RESULT.md`: `BLOCKED__NO_STANDALONE_MANUSCRIPT`.
- Governance terminal, from `GOVERNANCE_ADJUDICATION_V1.md`:
  `TOP_TIER_SUCCESSOR_NOT_SUPPORTED__BOUNDED_RETAINED`.

The filing blocker is a manuscript-preparation blocker, not a scientific one. The
packet states the distinction plainly: nothing in the evidence is missing or
undetermined, and no experiment is required to clear it. What remains is writing —
converting the working framework document into a venue manuscript under the
`nature-*` skills protocol, with a copyedit and reference-format pass.

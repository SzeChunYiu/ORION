# `test_the_real_protocol_is_execution_frozen` cannot be fixed by re-pinning

One of the CI failures remaining on `main` after #1819 is
`tests/unit/study/p1/test_execution_freeze.py::test_the_real_protocol_is_execution_frozen`,
failing with `unresolved=('evaluator_hash_mismatch',)`.

It looks like one more R0 digest that needs re-pinning. It is not. **Two frozen
constants now require incompatible bytes for the same file, and no content of that
file satisfies both.** This is written down so that the obvious repair — editing
the pinned protocol — is not attempted. That repair was attempted once already, in
#1810, and reverted.

## The two demands

The evaluator is ORION-11's adjudication rubric,
`papers/orion-11-recursive-epistemic-reconstruction/protocol/ADJUDICATION_RUBRIC_V1.md`,
bound by `orion/study/p1/execution_freeze.py::_evaluator_hash` as a whole-file
SHA-256.

| binder | requires the rubric to be | source |
|---|---|---|
| `PROTOCOL_V1.json` → `execution_bindings.evaluator_hash` | `a1d59277…9020` — the **pre-R0** bytes | the frozen protocol |
| `orion/study/p1/adjudication.py` → `FROZEN_RUBRIC_HASH` | `dce9f361…41be` — the **post-R0** body | code constant |
| `orion/study/p1/adjudication.py` → `V1_POLICY.policy_id` | `ORION-11.model-panel-adjudication.v1` | code constant |

`PROTOCOL_V1.json` is itself pinned by `assert_v1_protocol_untouched()` at
`91d5dca84d927ccb5cc5a54fece12502f23c8cba22f8eb8e5a48377539eca0b7`, and it
currently hashes to exactly that. **The protocol is intact and must stay intact.**

## Verified, not inferred

Restoring the rubric to the pre-R0 content (found at commit `2bab2148f`, whose
SHA-256 is exactly the `a1d59277…` the frozen protocol declares) was tried on a
scratch branch:

- `tests/unit/study/p1/test_execution_freeze.py` → **13 passed**, the failure gone;
- `tests/unit/study/p1/test_adjudication.py` → **2 newly failed**:
  `test_rubric_document_hashes_to_the_digest_it_records` and
  `test_policy_is_frozen_inside_the_hashed_rubric_body`.

The scratch branch was deleted. Nothing was committed.

## How it arose

The rubric has exactly three post-freeze versions, and the whole diff from frozen
to current is **five lines, all identifiers**:

- `ORION-P1 Adjudication Rubric` → `ORION-11 Adjudication Rubric`
- `P1.adjudication-rubric.v1` → `ORION-11.adjudication-rubric.v1`
- `P1.H2` → `ORION-11.H2`
- `P1.model-panel-adjudication.v1` → `ORION-11.model-panel-adjudication.v1`
- the rubric's own internal `RUBRIC-CONTENT-SHA256`, re-pinned to match

R0 (`3a1a83178`) renamed identifiers **inside a frozen evaluator**, which broke
that file's internal self-consistency; `0deff0ad4` collapsed a further prefix; and
#1749 (`1657c1f5f`) then re-pinned the internal hash, correctly restoring internal
consistency. Each step was locally reasonable. Together they moved the evaluator's
bytes away from the ones P1 froze, and the whole-file binding cannot tell a
cosmetic rename from a substantive edit.

**The adjudication substance — the criteria, the gold standard — is unchanged.**
Only names moved.

## Why the test failing is correct

`evaluator_hash_mismatch` is true. The rubric is not byte-identical to the one P1
froze. The freeze is doing its job; what it cannot do is distinguish a rename from
a change of standard.

## The three options, none of which should be taken quietly

1. **Re-pin `PROTOCOL_V1.json`.** Forbidden. It is guarded, it is intact, and this
   was tried and reverted in #1810. Re-pinning a freeze to whatever the artifact
   now says is not a repair; it removes the only thing the freeze was for.
2. **Revert the rubric and `adjudication.py`'s two constants together.** Restores
   the freeze and undoes #1749's repair, leaving `P1.`-prefixed identifiers in one
   file. Defensible — a frozen artifact keeping its frozen identifiers is what
   freezing means, and R0's alias registry exists to resolve the old names — but it
   crosses into ORION-11's lane and must be that lane's decision.
3. **Bind the evaluator by substance rather than whole-file bytes.** Would survive
   renames, and would also stop detecting the edits the binding exists to catch.

Option 2 is the most likely correct one. It is not taken here because it edits
another paper's repaired artifact and reverses a merged fix, and because the choice
between "a frozen artifact keeps its old names" and "the repository speaks one
namespace" is an ownership decision rather than a mechanical one.

Until then this failure should be read as **a correctly reported freeze violation**,
not as an unfixed digest.

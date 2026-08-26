# QG34 Adaptive Probe Tree Results — Duplicate-Identity Correction Receipt V1

Status: ADDITIVE CORRECTION RECEIPT (no existing file is modified by this receipt).
Frozen: 2026-08-26 (ORION V1 freeze takeover, issue #1034).

## Defective artifact

`research/extensions/orion-qg/QG34_ADAPTIVE_PROBE_TREE_RESULTS.json`

- sha256 (byte-identical at frozen base `ef51b7b9263a72c725dc9d2045627b934b772a92` and origin/main `926c7529e7b1a4aad18e8a8d7067c2fb293fe771`): `7731425f6395b4d7e9bd4e9b8798ede6530f3375001e9c0d5128c16d7e6ad965`
- git blob (both trees): `13a1a28030afdbed915df128ec7cb92c3c7e2326` (4254 bytes)

## Precise defect

The file parses under permissive `json.loads` but carries THREE duplicate top-level
identity keys with conflicting values (last-key-wins silently selects one authority
state; a strict duplicate-key parser rejects it). The exact conflicting pairs,
verbatim from the file:

- `schema`: `ORIONQG.QG34.CommittedResult.v1` vs `ORION.QG.QG34.CommittedResult.v1`
- `terminal`: `QG34_EXACT_MINIMAX_ADAPTIVE_PROBE_DEPTH_MACHINE_CHECKED` vs `QG34_EXACT_MINIMAX_ADAPTIVE_DEPTH_ESTABLISHED`
- `source_result_digest`: `7c48f505582a36401632489562c7181f4e763e2e1fd1e36549b9a24c794f8a55` vs `d13a0d25ec20a08a28dae59d8f420be3b19b48a1be278ffe3adf1aa99afed75e`

(The `issue` key is also duplicated, with identical value — cosmetic, not a conflict.
Note: the #1034 issue body drops the `PROBE_` token from the first terminal; the
string above is the file's actual content.)

## Origin of the weld (how both identities came to coexist)

1. PR #926 (commit `2589801ac`) introduced the 12-key object
   `{ORION.QG.QG34.CommittedResult.v1, QG34_EXACT_MINIMAX_ADAPTIVE_DEPTH_ESTABLISHED, d13a0d25...}`
   (blob `3d67e219b`, 2671 bytes).
2. PR #940 (commit `af7163662`) union-merged the GitHub-protected dual-harness object
   beside it WITHOUT a separating comma → unparseable JSON (blob `934a063bd`, 4253 bytes).
3. PR #1013 (commit `10884483d`, 2026-08-23T20:45:18Z) performed the parse-only repair
   (inserted the missing comma, kept both object bodies) → blob `13a1a2803`.

The scientific content is NOT in conflict: both identity variants sit on identical
measurement material (worst-case adaptive depth `D_* = 3`; depth histogram
`{0: 7, 1: 30, 2: 39, 3: 16}`; 92 joint summary classes; total orbits 715).

## Canonical identity (single, declared here)

For the **committed dual-harness result layer** the canonical identity is:

- `schema` = `ORIONQG.QG34.CommittedResult.v1`
- `terminal` = `QG34_EXACT_MINIMAX_ADAPTIVE_PROBE_DEPTH_MACHINE_CHECKED`
- `source_result_digest` = `7c48f505582a36401632489562c7181f4e763e2e1fd1e36549b9a24c794f8a55`

Evidence, four independent in-tree points:

1. **Sealed protected-lane object.** The original sealed file (no duplicates, 25 keys,
   1586 bytes) exists on `codex/orion-qg-qg34-adaptive-probe-tree-20260822` (seal
   commits `57d04026b` "seal exact adaptive minimax result" and `4ff87a97a` "commit
   protected dual-harness receipt"), git blob
   `61ad64ed01036b1dd44d7c684c35e43c62534c29`, sha256
   `80f5cb0c11eb21d73704daf9625fe7f54902db6d15854ec2354f3eaf3116d5a1`, carrying exactly
   the canonical identity triple above. (The same blob is the tip content of 7 other
   preserved `codex/*` lane branches.)
2. **Dual-harness run receipt.** `development/orion-qg-regime-geometry/QG34_PROTECTED_RUN_RECEIPT_2026-08-22.json`
   records `schema: ORIONQG.QG34.DualHarness.v1`, `terminal:
   QG34_EXACT_MINIMAX_ADAPTIVE_PROBE_DEPTH_MACHINE_CHECKED`, `both_accept: true`,
   `worst_case_depth: 3`.
3. **Protocol honest-terminal list.** `research/extensions/orion-qg/QG34_ADAPTIVE_PROBE_TREE_PROTOCOL_V1.md`
   ("## Honest terminals") lists exactly the `MACHINE_CHECKED` variant — and no
   `ESTABLISHED` variant — as this lane's production terminal.
4. **Downstream pinned consumers.** `research/extensions/orion-qg/qg36_fair_adaptivity_composition.py`
   (and `qg36_generic_verify.py`) pin `Q34_GIT_BLOB_SHA1 =
   "61ad64ed01036b1dd44d7c684c35e43c62534c29"` AND assert
   `terminal == "QG34_EXACT_MINIMAX_ADAPTIVE_PROBE_DEPTH_MACHINE_CHECKED"` as the QG-36
   parent gate.

Consequence recorded for downstream: against the welded results file as it stands,
BOTH QG-36 parent checks fail (blob pin and terminal assertion) — QG-36 consumed the
sealed protected-lane object, not the welded main copy.

`QG34_EXACT_MINIMAX_ADAPTIVE_DEPTH_ESTABLISHED` is NOT demoted garbage: it remains the
valid identity of the **freeze-registry layer** — `research/extensions/orion-qg/QG34_ADAPTIVE_PROBE_TREE_FREEZE_V1.md`
(lines 48/94) names it as the registry/freeze terminal. It is a different layer's
correct name, not an alias. The defect is the two layers sharing one file, not either
name being wrong.

## Repair direction (for the implementer; this receipt changes no file)

- Reconstruct the committed-result schema with DISTINCT named fields per layer
  (e.g. `committed_result` vs `freeze_registry`) instead of duplicate keys — per the
  #1034 instruction NOT to delete whichever duplicate wins.
- Add duplicate-key rejection on the committed-result loader so ordinary `json.loads`
  cannot silently choose an authority state.
- This receipt itself IS the requested adjudication record: canonical committed-result
  identity = the sealed dual-harness triple above.

## No history rewrite

Nothing in this receipt rewrites, amends, or deletes history. The welded blob
(`934a063bd`), the parse-repaired blob (`13a1a2803`), and the sealed protected-lane
blob (`61ad64ed0`) all remain exactly as committed, on their original refs. All future
work binds identity via this receipt, not via JSON key order.

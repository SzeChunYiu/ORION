# QG34 Adaptive Probe Tree Results — Dual-Identity Repair Receipt V1

Status: REPAIR RECEIPT (executes the repair direction of
`QG34_ADAPTIVE_PROBE_TREE_RESULTS_CORRECTION_RECEIPT_V1.md`; that receipt itself is
untouched). Additive as a receipt; the defective artifact is repaired in the same commit.
Repaired: 2026-08-27 (ORION V1 freeze takeover, issue #1034).

## Defective artifact (before this commit)

`research/extensions/orion-qg/QG34_ADAPTIVE_PROBE_TREE_RESULTS.json`

- git blob: `13a1a28030afdbed915df128ec7cb92c3c7e2326` (4254 bytes)
- sha256: `7731425f6395b4d7e9bd4e9b8798ede6530f3375001e9c0d5128c16d7e6ad965`
- Welded FOUR duplicate top-level identity keys: `issue` (identical value, cosmetic),
  and three with conflicting values — `schema`, `terminal`, `source_result_digest`.

## Repaired artifact (this commit)

Same path.

- git blob: `0fb6e2a0b6ff7d9960ab09942a402a304a890d71` (4289 bytes)
- sha256: `a215426d51fefb5a3948a14991d30939cd251e6bbc40bf88bf64d685741d762c`

Repair mechanics (no verdict content touched):

1. The four duplicate top-level keys are removed from the sorted body.
2. The layer-2 freeze-registry identity is preserved verbatim under a NEW distinct
   named field, at the site of the removed keys:
   `freeze_registry = {issue: SzeChunYiu/ORION#924, schema: ORION.QG.QG34.CommittedResult.v1,
   terminal: QG34_EXACT_MINIMAX_ADAPTIVE_DEPTH_ESTABLISHED,
   source_result_digest: d13a0d25ec20a08a28dae59d8f420be3b19b48a1be278ffe3adf1aa99afed75e}`.
3. Top-level identity is the canonical one adjudicated in the V1 correction receipt.

## Canonical identity (as adjudicated in the V1 correction receipt)

- `schema` = `ORIONQG.QG34.CommittedResult.v1`
- `terminal` = `QG34_EXACT_MINIMAX_ADAPTIVE_PROBE_DEPTH_MACHINE_CHECKED`
- `source_result_digest` = `7c48f505582a36401632489562c7181f4e763e2e1fd1e36549b9a24c794f8a55`
- `issue` = `SzeChunYiu/ORION#924`

`QG34_EXACT_MINIMAX_ADAPTIVE_DEPTH_ESTABLISHED` / `ORION.QG.QG34.CommittedResult.v1` /
`d13a0d25...` are NOT demoted: they are the correct identity of the freeze-registry
layer (`QG34_ADAPTIVE_PROBE_TREE_FREEZE_V1.md` lines 48/94) and now live under
`freeze_registry` instead of colliding at top level.

## Layer-1 verdicts are byte-identical

All 29 non-identity top-level fields — including `class_depths` (92 values),
`depth_histogram`, `orbit_mass_depth_histogram`, `worst_case_depth`, `worst_class_indices`,
`worst_class_sizes`, `first_worst_policy`, `aggregate_dp_stats`, `freeze_requirements`,
`primitives_recomputed_from_main`, `result` (D_star = 3), `witness_tree`, and every
authority flag — are deep-equal to the defective blob's values. No QG-34 verdict,
number, histogram, or authority boolean changed in this repair. The byte delta is
exactly: four duplicate identity lines dropped, six `freeze_registry` lines added.

## Last-key-wins identity flip (ordinary readers)

Under permissive `json.loads` (last-key-wins), the defective file silently presented
the NON-canonical layer-2 identity to every ordinary reader:

- reader saw `terminal` = `QG34_EXACT_MINIMAX_ADAPTIVE_DEPTH_ESTABLISHED` (now only
  under `freeze_registry`),
- reader saw `schema` = `ORION.QG.QG34.CommittedResult.v1` (now only under `freeze_registry`),
- reader saw `source_result_digest` = `d13a0d25...` (now only under `freeze_registry`).

After the repair the same reader sees the canonical committed-result identity
(`...MACHINE_CHECKED` / `ORIONQG.QG34.CommittedResult.v1` / `7c48f505...`), and a
strict duplicate-key parser accepts the file instead of rejecting it.

## Loader hardening (duplicate-key rejection)

`research/extensions/orion-qg/qg36_fair_adaptivity_composition.py` and
`development/orion-qg-regime-geometry/qg36_generic_verify.py` now load the QG-34
committed result through `load_committed_result(p) = json.loads(..., object_pairs_hook=no_dupes)`,
which raises `ValueError("duplicate committed-result keys: <key>")` on any duplicate
key, so ordinary `json.loads` can no longer silently choose an authority state for the
QG-34 parent. Verified: the defective blob is rejected (`duplicate committed-result
keys: issue`); the repaired blob loads with the canonical terminal. QG-35 loads are
unchanged.

## QG-36 consequence and re-run outcomes (2026-08-27, worktree `orion-qg34-fix`)

Per the V1 correction receipt, BOTH QG-36 parent checks previously failed against the
welded file (blob pin `61ad64ed0`/`13a1a2803` mismatch and terminal assertion), i.e.
QG-36 consumed the sealed protected-lane object, not the welded main copy. This repair
re-pins both QG-36 scripts and the QG-36 protocol prose to the repaired blob
`0fb6e2a0b6ff7d9960ab09942a402a304a890d71`, restoring the main-copy binding.

Actual outcomes of re-running both scripts after the repair:

- `python3 research/extensions/orion-qg/qg36_fair_adaptivity_composition.py` (exit 0):
  `ORIONQG_QG36={"D_star":3,"F_star":4,"result_digest":"aaf8329326287b558dea4720d25eb53e22d8ed06ab66d5ed8576e0a55e19bf9a","strict_classes":9,"terminal":"QG36_TARE_POSTSUMMARY_ADAPTIVITY_STRICTLY_REDUCES_WORST_CASE_OBSERVATION_COUNT","violations":0}`
  — all `parent_checks` true (incl. `qg34_blob_frozen` against `0fb6e2a0...` and
  `qg34_exact`).
- `python3 development/orion-qg-regime-geometry/qg36_generic_verify.py` (exit 0):
  `ORIONQG_QG36_GENERIC={"D_star":3,"F_star":4,"decision":"ACCEPT_FAIR_COMPARISON","strict_classes":9,"terminal":"QG36_TARE_POSTSUMMARY_ADAPTIVITY_STRICTLY_REDUCES_WORST_CASE_OBSERVATION_COUNT","violations":0}`
  — `all_checks: true` (all 15 checks true, incl. `qg34`).

These QG-36 outputs are receipt-only artifacts (written under gitignored `artifacts/`);
their authority claims remain bounded by the QG-36 protocol, and this receipt asserts
no new QG-34 verdict — only identity deduplication.

## No history rewrite

The defective blob `13a1a2803`, the pre-parse weld `934a063bd`, the sealed protected-lane
blob `61ad64ed0`, and every frozen census snapshot referencing them remain exactly as
committed on their original refs. This commit only moves main's tip forward.

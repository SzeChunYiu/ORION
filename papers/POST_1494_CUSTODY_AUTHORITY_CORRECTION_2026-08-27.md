# Post-#1494 custody authority correction (2026-08-27)

Repair gate required by issue #1497. This document records the exact
commit/tree/content identity of every record the #1474 (R0 namespace
unification) → #1494 (`0deff0ad4`, "collapse ORION-ORION-NN double prefixes +
rebind paper manifests") wave touched inside frozen custody chains, what was
wrong, and what this repair changed. Until this document and the accompanying
commit landed, #1494 did not serve as exact content-binding closure for the
records named below.

Evidence commands are reproducible from the repository history; every digest
below was recomputed during this repair, not copied from prior prose.

## Class 1 — ORION-12 acquisition freeze `parameters_sha256`

Record: `papers/orion-12-open-world-scientific-discovery/protocol/P2_OPEN_WORLD_ACQUISITION_FREEZE_2026-08-22.json`

Chain of record:

| Commit | `parameters_sha256` | sha256(canonical embedded `parameters`) |
|---|---|---|
| `7b97888f3` (original freeze, #831) | `ad7e4c6a…149f769a` | `ad7e4c6a…149f769a` — self-consistent |
| `3a1a83178` (R0 rename, #1474) | `ad7e4c6a…` (unchanged) | `8a03a917…1eaa418` — **object changed, digest stale** |
| `0deff0ad4` (#1494) | `8a03a917…1eaa418` | `8a03a917…1eaa418` — self-consistent again |

Facts established this repair:

- The authenticated parameter object at `7b97888f3` (call it **A**) vs the
  object at HEAD (**B**) differ in **exactly one leaf of 87**: the
  self-referential `parameters.freeze_document` path
  (`papers/paper-02-…` → `papers/orion-12-…`). No scientific parameter
  (gates, thresholds, seeds, bootstrap, claim scope, world/mechanics module
  bindings) changed.
- Therefore the defect attributed to #1494 ("digest rewritten though review
  records no change to the authenticated parameter object") is precisely:
  the *object* changed at #1474 (one self-referential path leaf) while the
  digest stayed behind; #1494 then recomputed the digest over the renamed
  object. The authenticated scientific content was never altered.
- Disposition: the record at HEAD is self-consistent
  (`sha256(json.dumps(parameters, sort_keys=True, separators=(',',':')))` ==
  `parameters_sha256`) and is left byte-stable by this repair — editing it
  would create a new custody event. This document is the permanent bridge:
  digest of the originally authenticated object A = `ad7e4c6afd66943693ae732b2dde9131aa5bddd13b5632dc97c38223149f769a`,
  recoverable at `7b97888f3:papers/paper-02-open-world-scientific-discovery/protocol/P2_OPEN_WORLD_ACQUISITION_FREEZE_2026-08-22.json`.

## Class 2 — ORION-12 V3 parent-freeze `git_blob_sha` retargeted

Record: `papers/orion-12-open-world-scientific-discovery/protocol/P2_WIDE_OPENAIRE_MATCHED_FREEZE_V3.json` → `parent_v2`

Historical truth (recomputed): at parent head `b96f1e70a65b73556c6bddb8189a5d6099937a48`
the V2 freeze lived at `papers/paper-02-open-world-scientific-discovery/protocol/P2_WIDE_OPENAIRE_MATCHED_FREEZE_V2.json`
with git blob `36c923a416389be831333e8a02f75736278c8b3f`
(`git rev-parse b96f1e70:<path>` → same).

- At `3a1a83178` the record carried the correct pair
  (`head_sha=b96f1e70`, `git_blob_sha=36c923a4…`).
- #1494 (`0deff0ad4`) retargeted `git_blob_sha` → `7b0f0313…` (the
  post-rename blob at the current tree) while leaving `head_sha` fixed — an
  internally false claim: blob `7b0f0313` does not exist at `b96f1e70`.
  Both recorded artifacts of the actual V3 run —
  `evidence/external_results/P2_WIDE_OPENAIRE_MATCHED_RUN_RECEIPT_V3.json:10`
  and `…RESULT_V3.json:120` — kept the historical `36c923a4…`, so #1494 also
  made the freeze disagree with its own run records.
- The motive was mechanical: `load_and_validate_freeze`,
  `run_autoresearchbench_wide_openaire_matched_v3.py`, and
  `analyze_autoresearchbench_wide_openaire_matched_v3.py` each validate
  `git_blob_sha1(current V2 file) == parent_v2.git_blob_sha`, and the R0
  rename had changed the file's bytes (its internal self-references).

Repair applied (this commit):

1. `parent_v2.git_blob_sha` restored to the authenticated `36c923a4…`;
   `path_at_head` records the historical path so the triple
   (head_sha, path_at_head, git_blob_sha) is machine-verifiable;
   `post_rename_git_blob_sha = 7b0f0313…` records the post-rename blob
   explicitly instead of laundering it into the identity.
2. The three validators now accept exactly
   `{git_blob_sha, post_rename_git_blob_sha}` via
   `probe_openaire_v4_doi_filter_transport.parent_v2_blob_is_bound` —
   same-tree execution binding keeps verifying, the historical identity is
   never rewritten again, and no third blob can ever match.
3. Freeze↔run-record agreement restored (`36c923a4…` on all three).

Run-time V3-file identity note: the run receipt pins the V3 freeze's own
run-time blob `25a55bcce0…`; that blob predates both rewrites and remains
recoverable at the run's source commit. It is provenance, not a current-tree
claim.

## Class 3 — ORION-16/17/18 manifest `subject_commit`/`subject_tree` inconsistency

Records: `papers/orion-1{6,7,8}-*/CONTENT_MANIFEST_V1.json` (+ `SHA256SUMS`)

The manifests declared `subject_commit = 0941a0dee…` whose actual tree is
`c3aac00a…`, while the recorded `subject_tree` values differed from it — the
identity pair was false. Root cause: same #1494 rebind wave.

Repair applied (this commit): regenerated via the sanctioned reconciler
`scripts/regen_paper_manifests.py --papers 16,17,18` — each manifest now
carries `subject_commit` = the commit holding the bound bytes,
status `BOUND` (was `CANNOT_CHECK`), `unbound = 0`:

- orion-16: 76 bound files, 76 sums
- orion-17: 73 bound files, 73 sums
- orion-18: 75 bound files, 75 sums

Verified post-repair: `survey_paper_bindings` reports zero drifted papers
against `papers/CONTENT_BINDING_DRIFT_BASELINE_V1.json` (empty baseline).

## Disposition

- #1494's content-binding closure now holds for the records above via this
  correction; no scientific verdict, negative result, or CANNOT_CHECK
  terminal was altered by this repair. The ORION-12 V3/V2 chain keeps its
  retained terminal `P2_WIDE_EXTERNAL_V2_CANNOT_CHECK`.
- Regenerating digests to match unexplained bytes remains prohibited; the
  only sanctioned reconciler for manifest drift is
  `scripts/regen_paper_manifests.py`, and identity fields of *historical*
  pointers (head/blob/path at head) are immutable — post-rename realities are
  recorded additively, never by retargeting.

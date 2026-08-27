# Post-#1494 custody authority correction

Status: `POST_1494_CUSTODY_QUARANTINED`

This note records a reproducibility/custody correction only. It does not alter any theorem, experiment outcome, application result, or protected Task-3 path.

## Trigger

PR #1494 was merged to `main` as `0deff0ad44fc945b3d7d4755d8522105e5ccadc1` while unresolved review findings remained on files that carry freeze/content-binding identity.

## Bound defects

### 1. ORION-12 acquisition-freeze parameter digest

The merged file

`papers/orion-12-open-world-scientific-discovery/protocol/P2_OPEN_WORLD_ACQUISITION_FREEZE_2026-08-22.json`

records

`parameters_sha256 = 8a03a9171e51f82d280ec7566a0239f267ec310e850f9c465111a9ef71eaa418`.

Immediately before #1494, at `9d270935dfbbf0c2881929d93793119ed4726660`, the same freeze recorded

`parameters_sha256 = ad7e4c6afd66943693ae732b2dde9131aa5bddd13b5632dc97c38223149f769a`.

The unresolved review states that the authenticated `parameters` object was not changed when this digest was rewritten. Until the repository's existing digest checker recomputes and validates the binding, #1494 cannot be used as evidence that this historical freeze is byte-authenticated.

### 2. ORION-12 V3 parent-freeze identity

The merged

`papers/orion-12-open-world-scientific-discovery/protocol/P2_WIDE_OPENAIRE_MATCHED_FREEZE_V3.json`

retains historical parent `head_sha = b96f1e70a65b73556c6bddb8189a5d6099937a48` but changes `parent_v2.git_blob_sha` from the pre-#1494 value

`36c923a416389be831333e8a02f75736278c8b3f`

to

`7b0f0313377ac45ab22dec0affaa6d0fd85b4c70`.

The unresolved review identifies this as a false historical binding: the replacement blob is not the parent blob at the still-recorded historical head. The V3 record therefore must not be cited as exact parent-freeze custody until repaired and checked against that head.

### 3. ORION-16/17/18 V2 subject-tree identities

All three merged V2 manifests bind `subject_commit` to

`0941a0dee7f4510059f822f50b92cf6fcfcba567`.

The actual Git tree of that commit is

`c3aac00a60f0121a16488ca5c135ecf6e7a9b1ce`.

The merged manifests instead record:

- ORION-16: `5f78256d573ce70a7856d9e51617f152c06d2ee2`
- ORION-17: `54609427bf44e72826e863f2905f0a0263d6266c`
- ORION-18: `54609427bf44e72826e863f2905f0a0263d6266c`

Thus `subject_commit` and `subject_tree` do not identify the same Git subject. Any status asserting exact subject-commit identity as `BOUND` is non-authoritative until these metadata and their downstream digest chains are regenerated and revalidated.

## Authority consequence

PR #1494 remains useful as transport/editorial CI work, including the namespace cleanup and corpus-pin implementation. However, its merge does **not** establish exact content-binding closure for the affected ORION-12/16/17/18 records while the identities above are inconsistent.

This is a custody/referee correction, not a refutation of the underlying scientific claims. No manuscript or application claim gains or loses theorem authority solely because of this note. Existing adverse/null scientific terminals, including the separate FiberGuard C-NBR2 quarantine, remain unchanged.

## Frozen repair gate

A successor repair may restore authority only if it:

1. changes no scientific parameter, result, theorem statement, or application terminal;
2. validates the ORION-12 `parameters_sha256` using the repository's existing canonical digest procedure over the unchanged frozen parameters;
3. validates `P2_WIDE_OPENAIRE_MATCHED_FREEZE_V3.json` against the exact historical parent head and parent blob it claims;
4. makes each ORION-16/17/18 `subject_tree` equal the actual tree of its declared `subject_commit`, then regenerates every dependent content manifest/SHA256SUMS pointer rather than hand-editing a terminal status;
5. reruns the exact identity/content-binding checkers and preserves any RED/PARTIAL result rather than bypassing it;
6. separately resolves the open MUSE provenance-identity review before treating rebuilt MUSE evidence strings as custody-equivalent to the prior corpus evidence; and
7. does not touch protected Task-3 lanes.

Until that gate is green, use terminal `POST_1494_CUSTODY_QUARANTINED` for the affected binding claims.

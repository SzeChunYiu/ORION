# ORION-11 — archive, licence and external-handoff audit V1

`scientific_authority_delta: NONE`

Records what exists and what is missing for archiving, licensing and external handoff.
**No licence is invented, proposed, or applied here.** Where terms are absent, this
document says so and stops.

Audit date: 2026-08-28. Scope: `papers/orion-11-recursive-epistemic-reconstruction/`
plus the repository-root licence files it depends on.

---

## 1. Licensing — what exists

| Artefact | Path | Terms | Verified |
|---|---|---|---|
| Repository code | `LICENSE` (repo root, 11.1 KB) | Apache License 2.0 | Yes — header read: *"Apache License / Version 2.0, January 2004"* |
| Paper text | `LICENSE-PAPERS-CC-BY-4.0.txt` (repo root, 18.2 KB) | Creative Commons Attribution 4.0 International | Yes — header read: *"Attribution 4.0 International"* |
| Attribution notice | `NOTICE` (repo root, 256 B) | Copyright 2026 Sze Chun Yiu; states the split-by-artifact-type licensing model | Yes |
| Third-party terms | `THIRD_PARTY_NOTICES.md` (repo root, 2.3 KB) | `cryptography` 50.0.0 (`Apache-2.0 OR BSD-3-Clause`), `defusedxml` 0.7.1 (PSFL) | Yes |
| Package-level restrictions | `journal_package/LICENSE.md` | Points at the two root licences; records that `protocol/cases/` is constructed task text (not redistributed third-party papers), that external baselines are protocol-matched reimplementations, and that live provider arms remain subject to provider terms | Yes |

**Discrepancy to resolve — flagged, not fixed.** `README.md` lists as a current
blocker that a clean checkout *"still lacks … (3) repository-level redistribution
terms."* That statement appears **stale**: `LICENSE`, `LICENSE-PAPERS-CC-BY-4.0.txt`,
`NOTICE` and `THIRD_PARTY_NOTICES.md` are all present at the repository root, and
`journal_package/LICENSE.md` cites the first two by name. Either the blocker means
something narrower than the root licences (for example, terms governing
redistribution of the *evidence corpus* specifically, which no file currently
states), or it is out of date. **This audit does not decide which, and does not edit
the blocker.** It requires an owner decision.

Known scope limit, stated by the source itself: `THIRD_PARTY_NOTICES.md` covers only
direct runtime dependencies declared in `pyproject.toml`. It is **not** a transitive
audit and excludes development- and test-only tooling. It says so explicitly. If
redistribution of a built artefact is ever required, a transitive audit against the
resolved lockfile is needed at that moment.

## 2. Archiving — what is missing

Taken from `journal_package/MANIFEST.json` → `missing_artifacts`, all currently
`CANNOT_CHECK`:

| Path | Role | Why missing |
|---|---|---|
| `journal_package/DOI.txt` | `immutable-public-archive-doi` | No immutable public deposit binds the exact current release. |
| `journal_package/current_revision/manuscript.pdf` | `current-revision-content-bound-pdf` | The tracked PDF renders an earlier manuscript; no fresh immutable PDF for the enlarged current source exists in a clean checkout. **Now also stale with respect to the 2026-08-28 retraction edits.** |
| `journal_package/current_revision/RENDER_AND_VISUAL_AUDIT.md` | `current-revision-render-and-page-level-visual-audit` | No build receipt and page-level visual audit bind the current source to a current PDF. |

No `CITATION.cff`, `.zenodo.json` or `codemeta.json` exists anywhere in the
repository. Verified by direct lookup, not inferred from absence of mention. A Zenodo
or comparable deposit would normally need at least one of these; none is present and
none is created here.

## 3. External handoff — what is in external custody

Also from `missing_artifacts`, both `CANNOT_CHECK`:

| Path | Role | State |
|---|---|---|
| `evidence/external-custody/p1-source-native-action-adapter-v2/SHA256SUMS` | `source-native-adapter-47-entry-handoff-manifest` | In external custody, absent from a clean checkout. Only its recorded manifest digest `9f4503f693e155b12fb8c333f4777619cec1d66e387dcfc0e141fffa6933847d` is retained in `MANIFEST.json` → `package_authority.external_handoff_recorded_manifest_sha256`. |
| `evidence/external-custody/p1-source-native-action-adapter-integration-v3/INDEPENDENT_SHA256_VERIFICATION_V1.json` | `independent-source-native-adapter-checksum-receipt` | In external custody, absent from a clean checkout, so its recorded zero-failure statement **cannot be reverified here**. |

The directory `evidence/external-custody/` does not exist in this tree. Its absence is
consistent with the recorded external-custody state and is not itself a defect; the
defect is that neither artefact can be independently checked from a clean checkout.

## 4. Package checksum inventory — now intentionally stale

`journal_package/SHA256SUMS` has 25 entries. Verified on 2026-08-28 after the
retraction edits:

```
OK = 22    FAILED = 3    TOTAL = 25
```

The three failures are exactly the three retraction-edited files that appear in the
inventory:

- `manuscript/main.tex`
- `evidence/CLAIM_LEDGER.md`
- `JOURNAL_READINESS.md`

**Every frozen record in the inventory verified OK**, including
`evidence/CLAIM_LEDGER_V1.md`, `evidence/PEER_REVIEW_READY_BOUNDED_V2.md`,
`protocol/PROTOCOL_V1.json`, `results/P1-T2_baseline_ablation_results.json`,
`results/P1-T2_STATUS_ONTOLOGY_CORRECTION_V1.json`,
`results/P1-T3_failure_taxonomy.json`, `evidence/FINAL_SATURATION_AUDIT.md`,
`journal_package/RENDER_INPUT_CLOSURE.json`,
`journal_package/RENDER_CLOSURE_STATE.json`, `journal_package/manuscript.pdf`, and the
five external `research/revival/p1/confirmatory/v2.2/` result and verification files.

This is an independent confirmation that the retraction touched only current claim
surfaces and no frozen evidence record.

`SHA256SUMS` is **not** regenerated here. `journal_package/COMPILE.md` binds its
refresh to the replacement of `journal_package/manuscript.pdf`, which requires a build
this host must not run. Refresh it as part of that build, not before.

## 5. Follow-ups this audit records but does not perform

1. Owner decision on the `README.md` licence-blocker discrepancy in §1.
2. Fresh PDF build and page-level visual audit of the post-retraction source
   (command in `CANONICAL_SOURCE_DECISION_V1.md` §5; run on `laptop billy` or in CI,
   not on this host).
3. Regenerate `journal_package/RENDER_CLOSURE_STATE.json` from the current tree.
4. Refresh `journal_package/SHA256SUMS` together with the new PDF.
5. Immutable public deposit + DOI, which would also require a citation-metadata file
   (`CITATION.cff` or `.zenodo.json`); none exists today.
6. Clean-checkout access to the two external-custody artefacts, or an explicit
   recorded decision that they remain external and permanently `CANNOT_CHECK`.
7. Transitive dependency licence audit, only if a built artefact is redistributed.

None of these is a scientific claim and none changes the ORION-11 terminal.

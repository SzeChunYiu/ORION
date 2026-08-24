# P4 exact-edge and lineage authority V9

**Identity:** `P4.M6.JOSS.EXACT_EDGE_LINEAGE.AUTHORITY.V9`  
**Frozen scope:** the same seven V8 residual JOSS concepts; zero replacements or proxy units.  
**Result:** **2/7 repaired**, cumulative exact bridge **75/80**; **5/7 remain `CANNOT_CHECK`**.

## Smallest lawful closure

| Index | Repository | V9 verdict | Exact evidence / residual |
|---:|---|---|---|
| 36 | `jaxionproject/jaxion` | `REMAINS_CANNOT_CHECK` | The concept DOI still resolves to a child with no exact `0.0.3` version field, while the archive is a later repository state. A provider correction must bind the frozen DOI and archive root to commit `069ab4f...`. |
| 91 | `nutritionallungimmunity/pai` | `REMAINS_CANNOT_CHECK` | The archive's embedded Git authority authenticates HEAD/main/origin-main `aa021231...`; accepted tag commit `9fa30e9f...` is absent from its object store. Current bytes therefore authenticate a different source state. |
| 133 | `artefactory/woodtapper` | `REMAINS_CANNOT_CHECK` | Zenodo and PyPI sdist hashes agree, but a source rebuild differs in two generated C files and PyPI has no provenance attestation. Exact build-to-commit authority remains missing. |
| 165 | `alek050/databallpy` | **`RESOLVED_SAME_IDENTITY`** | The 106,471,934-byte Zenodo archive and immutable commit `b52a049f...` have exactly **293/293** normalized paths with every byte hash equal. V8 had already bound exact version/tag and MIT rights. |
| 185 | `mit-psfc/disruption-py` | `REMAINS_CANNOT_CHECK` | Tag `v0.14` binds commit `dec5c58a...`, whose project version is `0.14.0`; Zenodo and PyPI sdist hashes agree. But the sdist is a projection plus generated metadata, the local rebuild omitted three tracked ignored CSVs, and no provider attestation binds the exact sdist hash to the commit. |
| 190 | `ugurdar/datadriftr` | **`RESOLVED_SAME_IDENTITY`** | GitHub Atom exposes full commit `6bcb4fb8...`; its codeload ZIP and Zenodo archive have exactly **355/355** normalized paths with identical bytes. Exact-commit and archive MIT licences are byte-equal. The direct archive-to-full-commit identity is stronger than the missing tag edge. |
| 199 | `targene/targene-pipeline` | `REMAINS_CANNOT_CHECK` | Third-party discovery expands prefix `0f8b2db` to `0f8b2dbca06a3bb7031de9058ee9882995e04412`, but current GitHub commit/codeload/raw endpoints and Software Heritage revision lookup all return 404. SWH authenticates only a deposited directory, not the full revision. Discovery evidence is not promoted to provider-native authority. |

Cumulative exact counts are Earth/environment **5**, life/biomedical **6**, scientific software **60**, and physical/engineering **4**. These are exact source-frame edges, not eligible natural pairs.

## External lineage and natural-pair authority

Crossref and Zenodo expose 30 exact publication-author positions across the seven targets:

- Crossref ORCID identified: **27/30**;
- Zenodo ORCID identified: **26/30**;
- exact cross-provider ORCID concordance: **26/30**;
- one additional Crossref-only ORCID; three name-only positions.

This is stable person-identifier progress only. It does **not** adjudicate author-lineage independence: the frozen replication rule applies across the full exact source frame, names cannot prove inequality, and no external normalization adjudication or primary/replication partition is present. Author-lineage adjudications added: **0**.

Natural pairs added: **0**. Exact edges and rights are prerequisites, but no independent material-claim, one-coordinate, target-purity, nuisance, comparator-outcome, evaluator-custody or source-disjoint-replication adjudication was opened. The programme terminal remains `P4_NATURAL_PAIR_SOURCE_TRANSPORT_CANNOT_CHECK`.

## Next discriminator

1. Revisit the five edge residuals only when the named provider-native correction, revision, or build attestation appears.
2. Build the full 75-edge ORCID/name conflict graph, externally adjudicate the unresolved identities, and freeze primary/replication partitions before case outcomes.
3. Then open natural-pair eligibility and external custody. Do not confuse exact-edge repair with source-cell quotas: Earth, life and physical remain structurally short, and scientific-software source-disjoint replication is a separate gate.

No manuscript/shared ledger, Git state, pytest, repository CI, comparator outcome or protected case was touched.

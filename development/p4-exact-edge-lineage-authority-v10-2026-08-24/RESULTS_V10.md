# P4 exact-edge lineage/authority V10 results

## Verdict

One of the five V9 residual exact-source edges closed. The cumulative exact bridge increases from **75/80** to **76/80**; the same 80 frozen units are retained.

| Index | Repository | V10/V10B verdict | Terminal gate |
|---:|---|---|---|
| 36 | `jaxionproject/jaxion` | `REMAINS_CANNOT_CHECK` | `provider_corrected_version_and_archive_to_commit_identity` |
| 91 | `nutritionallungimmunity/pai` | `REMAINS_CANNOT_CHECK` | `corrected_archive_or_provider_statement_superseding_adverse_embedded_git_authority` |
| 133 | `artefactory/woodtapper` | `REMAINS_CANNOT_CHECK` | `provider_native_sdist_to_full_commit_provenance` |
| 185 | `mit-psfc/disruption-py` | `REMAINS_CANNOT_CHECK` | `provider_native_projected_sdist_to_full_commit_provenance` |
| 199 | `targene/targene-pipeline` | `RESOLVED_SAME_CONTENT_IDENTITY` | `closed_exact_source_content_identity` |

## Genuine index-199 repair

The original frozen V10 discriminator failed: neither current GitHub nor Software Heritage authenticates the deleted `v0.13.4` revision `0f8b2dbca06a3bb7031de9058ee9882995e04412`, and the SWH origin snapshot has no `v0.13.4` branch.

A separately named, outcome-informed V10B protocol was then frozen **before** new archive download or comparison. Under it:

- GitHub tag `v0.13.5` and the exact commit API authenticate revision `a85df681d29a5cf3406d529144a7c0645e543e61` with tree `178315b57afafc1f20ab9929b4de893430524c62`.
- The official Software Heritage source-origin snapshot independently binds the same tag, full revision and directory.
- The checksum-bound Zenodo `v0.13.4` ZIP and immutable GitHub revision codeload ZIP each normalize to **165 paths**. The manifests have zero missing, extra or differing entries, including file bytes, entry type and executable bits; both manifest hashes are `32decf39f38d4652e184bef077625ce8e22fa44ec37afb98746ddce178f5364e`.
- The exact LICENSE bytes are MIT.

This is content identity only. It does **not** identify the later revision as the deleted `v0.13.4` commit or establish ancestry.

## Remaining exact-edge discriminators

### Index 36 — `jaxionproject/jaxion`

The exact concept DOI request still returns child record 10.5281/zenodo.21221062, whose metadata has no version and whose sole jaxion.zip file is 85,369,480 bytes with MD5 825cae8912147ba8a5415c6a73d95818. GitHub still binds tag 0.0.3 to full commit 069ab4f56d100d765d46c594ac1b06add7e49f9e. No provider correction binds the frozen archive to version 0.0.3 or that commit.

**Next:** A Zenodo/provider correction must bind the frozen DOI and exact archive bytes to version 0.0.3 and full commit 069ab4f56d100d765d46c594ac1b06add7e49f9e.

### Index 91 — `nutritionallungimmunity/pai`

Zenodo still identifies the checksum-bound record as v1.0.0 and GitHub still binds tag v1.0.0 to 9fa30e9f405de4446c792bd59cb7c5a4bb7ecb59. No corrected archive or provider statement supersedes the immutable V9 archive evidence: embedded HEAD, main and origin/main are aa021231cdafb6d74ce9ab5f55f824a3032058a4, while the accepted tag commit is absent from the embedded object store.

**Next:** A corrected exact v1.0.0 archive or authenticated provider statement must bind the frozen bytes to 9fa30e9f405de4446c792bd59cb7c5a4bb7ecb59 and resolve the adverse embedded Git authority.

### Index 133 — `artefactory/woodtapper`

Zenodo and PyPI still bind woodtapper-0.0.13.tar.gz to SHA-256 b509f6469b9ff8888195751c811d689559f45e24aeb35bb173b9680c99c8dbf3, and GitHub binds tag v0.0.13 to 7ac6d23d504404c4004faad663f6b889427109e6. The exact PyPI Integrity request returns 404 with 'No provenance available for woodtapper-0.0.13.tar.gz'; the exact GitHub artifact-attestation subject also returns 404. V9 local reconstruction differed in two generated C files and cannot substitute for provider provenance.

**Next:** PyPI trusted-publisher/Sigstore provenance or another provider-native exact build attestation must bind SHA-256 b509f646... to commit 7ac6d23d..., including the generated-C toolchain.

### Index 185 — `mit-psfc/disruption-py`

Zenodo and PyPI still bind disruption_py-0.14.0.tar.gz to SHA-256 775f92dbcbd6d1523db241494998e4b0867d51a84236feb7accc86b63b033a19, and GitHub binds source tag v0.14 to dec5c58a3e3970bc6817f33efb615fea11057fce. The exact PyPI Integrity request returns 404 with no provenance and the exact GitHub artifact-attestation subject returns 404. V9 showed common-file equality only: the sdist is a projection and a local rebuild omitted three tracked ignored CSV files.

**Next:** A provider-native build attestation must bind SHA-256 775f92db... to commit dec5c58..., including the tracked-ignored CSV inclusion state.

## Scientific boundary

The exact-edge bridge is a source-frame prerequisite only. V10/V10B adds no natural pair, author-lineage adjudication, source-disjoint replication, external custody, comparator outcome, performance result or superiority authority. The programme therefore remains `P4_NATURAL_PAIR_SOURCE_TRANSPORT_CANNOT_CHECK`.

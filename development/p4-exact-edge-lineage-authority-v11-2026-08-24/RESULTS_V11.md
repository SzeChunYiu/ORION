# P4 exact-edge lineage/authority V11 results

## Verdict

V11 closes **0/4** remaining exact edges. The cumulative bridge stays **76/80**. The negative result is informative: every remaining edge now has a provider-state-change discriminator, so repeating the same requests is not an efficient next action.

| Index | Repository | Verdict | Exact terminal |
|---:|---|---|---|
| 36 | `jaxionproject/jaxion` | `REMAINS_CANNOT_CHECK` | `provider_corrected_exact_version_and_replacement_archive_root_to_accepted_commit` |
| 91 | `nutritionallungimmunity/pai` | `REMAINS_CANNOT_CHECK` | `exact_full_archive_payload_to_immutable_revision_or_provider_native_build_attestation` |
| 133 | `artefactory/woodtapper` | `REMAINS_CANNOT_CHECK` | `pypi_exact_file_signed_artifact_to_full_commit_provenance` |
| 185 | `mit-psfc/disruption-py` | `REMAINS_CANNOT_CHECK` | `pypi_exact_file_signed_projected_sdist_to_full_commit_provenance` |

## Per-edge findings

### Index 36 — `jaxionproject/jaxion`

The exact Zenodo child and both official DataCite concept/child registrations still expose no version. The provider file remains the 85,369,480-byte jaxion.zip with MD5 825cae8912147ba8a5415c6a73d95818. Preserved checksum-bound archive evidence authenticates embedded worktree HEAD 3cd108c376faf9832373adfe3ab4688295aa42fa (tag 0.0.12), not publication version 0.0.3 commit 069ab4f56d100d765d46c594ac1b06add7e49f9e. Metadata absence and content contradiction are both terminal; the large archive was not redundantly downloaded.

**Next discriminator:** A provider replacement/correction must bind an exact 0.0.3 archive checksum whose root is commit 069ab4f56d100d765d46c594ac1b06add7e49f9e; the current checksum-bound archive is an embedded 0.0.12 worktree.

### Index 91 — `nutritionallungimmunity/pai`

The checksum-bound 17,147,954-byte Zenodo archive exactly authenticates embedded Git HEAD aa021231cdafb6d74ce9ab5f55f824a3032058a4 and tree d5620f3acf4e5a163cfdfdefc2432ebd5709008a; git fsck passes, and current GitHub independently authenticates the same full revision and tree. However the separately adjudicated non-.git archive payload has 444 paths versus 338 in immutable codeload: 106 untracked compiled Java .class files are archive-only, and cpp/PAIpp.exe plus run.sh have equal bytes but executable-bit drift. git diff-files is nonzero. Exact manifest equality therefore fails despite MIT rights, and the accepted v1.0.0 tag still points to a different absent-from-archive commit.

**Next discriminator:** A corrected checksum-bound archive must exactly equal an immutable source revision, or provider-native signed build provenance must bind all 106 compiled classes and the two mode changes to full revision aa021231...; subset/source-tree equality is insufficient.

### Index 133 — `artefactory/woodtapper`

PyPI's official PEP 691 exact file object binds woodtapper-0.0.13.tar.gz to SHA-256 b509f6469b9ff8888195751c811d689559f45e24aeb35bb173b9680c99c8dbf3 but exposes provenance: null. This independently agrees with V10's exact Integrity and GitHub artifact-attestation 404s; no provider-native statement binds the sdist to commit 7ac6d23d504404c4004faad663f6b889427109e6.

**Next discriminator:** PyPI must expose exact-file signed provenance binding SHA-256 b509f646... to commit 7ac6d23d..., including the generated-C toolchain.

### Index 185 — `mit-psfc/disruption-py`

PyPI's official PEP 691 exact file object binds disruption_py-0.14.0.tar.gz to SHA-256 775f92dbcbd6d1523db241494998e4b0867d51a84236feb7accc86b63b033a19 but exposes provenance: null. This independently agrees with V10's exact Integrity and GitHub artifact-attestation 404s; no provider-native statement binds the projected sdist to commit dec5c58a3e3970bc6817f33efb615fea11057fce.

**Next discriminator:** PyPI must expose exact-file signed provenance binding SHA-256 775f92db... to commit dec5c58..., including the tracked-ignored CSV inclusion state.

## Scientific boundary

No manuscript or claim-ledger headline changes: no exact edge closed. The bridge remains 76/80, and the programme remains `P4_NATURAL_PAIR_SOURCE_TRANSPORT_CANNOT_CHECK`. Source integrity or exact-file hash evidence alone does not authorize natural pairs, lineage independence, replication, custody, outcomes, performance or superiority.

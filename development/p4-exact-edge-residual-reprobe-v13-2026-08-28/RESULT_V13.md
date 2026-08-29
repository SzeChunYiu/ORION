# P4 exact-edge residual reprobe V13 results

**Lane:** `P4_M6_JOSS_EXACT_EDGE_RESIDUAL_REPROBE_V13` (revival lane for the V11 0/4 and V12 fresh-compile negatives).
**Run date:** 2026-08-28. Public development metadata/build evidence only; no outcome, label, protected case, natural pair, lineage adjudication or comparator authority.

## Verdict

V13 closes **0** of the 4 residual edges; the cumulative exact bridge remains **76/80**. What V13 changes is the *disposition*: three edges (36, 133, 185) move from `CANNOT_CHECK` to **mechanistically UNSOLVABLE at current provider/publisher state**, and edge 91's `FRESH_COMPILE_CANNOT_CHECK` is resolved to an **exact 106/106 fresh-compile reproduction** under the pinned compiler identity, narrowing its residual to signed-build and mode authority alone.

## Edge 36 — jaxionproject/jaxion: concept chain enumerated, single child, unchanged

New estimator (concept-version enumeration; V10/V11 checked only the frozen child and DataCite records):

- Zenodo `records/21221062/versions` (the canonical concept-chain enumeration) returns **total 1**: the frozen child 21221062 itself, `version: None`, concept 21221061. No corrected or replacement child version exists.
- Concept record body is byte-identical to the child body (single-version concept).
- The archive is unchanged: `jaxion.zip`, md5 `825cae8912147ba8a5415c6a73d95818`, 85,369,480 bytes — identical to the V10/V11 frozen values.
- DataCite registrations for both concept and child DOI remain `version: None`.
- The two search-field probes (`conceptrecid:"..."`, `conceptdoi:...`) were rejected by Zenodo with HTTP 400 (query fields unsupported); recorded as failed estimators, superseded by the `/versions` endpoint.

**Disposition:** the archive-root contradiction (checksum-bound 0.0.3-labelled archive whose content root is the embedded 0.0.12 worktree HEAD `3cd108c`, not accepted commit `069ab4f...`) is permanent at current provider state. Only publisher action — a corrected/replacement child version of concept 10.5281/zenodo.21221061 — could close it, and the chain is now enumerated to contain no such child. **UNSOLVABLE at current provider state** (closure condition unchanged).

## Edge 91 — nutritionallungimmunity/PAI: pinned fresh compile is exact 106/106

V12's terminal was environmental: the pinned `eclipse-temurin` 17.0.14+7 OCI image could not execute. V13 obtains the **same pinned compiler identity** — Eclipse Temurin OpenJDK `jdk-17.0.14+7`, `javac 17.0.14` — through its native Adoptium distribution channel (not a substitute compiler):

- Adoptium asset `OpenJDK17U-jdk_x64_linux_hotspot_17.0.14_7.tar.gz`, 191,943,794 bytes, distributor checksum `a3af83983fb94dd7d11b13ba2dba0fb6819dc2caaf87e6937afd22ad4680ae9a` — **verified equal** to the downloaded package.
- Immutable source: codeload tarball of authenticated revision `aa021231cdafb6d74ce9ab5f55f824a3032058a4` (sha256 `d43c827568d1acef62cea08990580a95ea5869f9eef4106fb3da8b941377e5af`), 106 `.java` files.
- V12's frozen compile command executed verbatim (find → `LC_ALL=C sort -z` → `javac -d`), `rc=0`, 106 input files.
- **Projection vs the V12 checksum-bound archive manifest: 106/106 class files byte-exact — 0 hash mismatch, 0 missing, 0 extra.**

`FRESH_COMPILE_CANNOT_CHECK` is thereby resolved: the archive's 106 untracked `java/bin/*.class` files are exactly reproducible from the authenticated revision under the pinned toolchain. Content lineage is now doubly established (tracked-JAR projection in V12, fresh compile in V13).

**Residual (unchanged by any local compile):** (a) provider-native signed build attestation — GitHub attestation endpoints for the archive/files returned 404 in V12 and the deposit has none; (b) the two mode bits — the validly signed tree records `cpp/PAIpp.exe` and `run.sh` as 100644 while the archive records 0755. Mode is not a function of file content: a compile that has just proven byte-exact content identity is structurally incapable of adjudicating mode authority, and the two authentic mode authorities (signed git tree vs checksum-bound archive) contradict. **IMPROVED — conditional:** edge 91 remains open on signed-build and mode authority only, both provider-state gates.

## Edges 133/185 — woodtapper 0.0.13 / disruption-py 0.14.0: publisher never attests

New estimators beyond V10/V11's PEP 691 field, plus a whole-project census:

| Surface | woodtapper (133) | disruption-py (185) |
|---|---|---|
| PEP 691 Simple API `provenance` | `null` | `null` |
| `/_attestations/<project>/<version>/` | 404 | 404 |
| PyPI JSON API per-file `attestations` key | absent | absent |
| PyPI Integrity provenance URL | absent (V10: 404) | absent (V10: 404) |
| GitHub `repos/.../attestations/<digest>` | 404 (V10) | 404 (V10) |
| **Whole-project census** (all files, newest included) | **0/7 with provenance** | **0/14 with provenance** |

The frozen digests are re-verified byte-identical live (`b509f646...`, `775f92db...` — the file objects are the originals). The census shows the publishers mint no attestations for *any* release, including their newest uploads — this is a never-attesting publisher, not an old upload that predated attestation availability.

**Rekor is quarantined.** The probe's digest-shaped Rekor retrieval returned `[]` for both edges, but a positive control (packaging 26.3, provenance present, its own transparency entry at logIndex 2341131906 provably in the log) *also* returns `[]` under both digest shapes (`{"hashes": [...]}` and `{"entryQuerys": [{"hashes": [...]}]}`) while the direct logIndex lookup returns the entry. Digest-shaped retrieval is **structurally blind** to PyPI's dsse-type transparency entries; no Rekor result may be cited for or against these edges. See `REKOR_ESTIMATOR_VALIDATION_V13.json`.

**Disposition (mechanistic):** PyPI mints attestations only inside the upload pipeline; the frozen file objects are immutable (same filename re-upload is rejected; digests unchanged since V11), so no attestation can attach to them without either a platform retroactive-minting program for never-attesting publishers (none exists, and it would still require the publisher's trusted-publishing identity) or a new release — which is a different file identity and does not bind the frozen digest. **UNSOLVABLE at current publisher state** (closure condition unchanged: a signed attestation binding the frozen digest to the accepted commit).

## Closure gates

| Gate | Result |
|---|---|
| Edge 36 concept-chain enumeration finds a corrected child | **FAIL — chain has exactly 1 child, the frozen one** |
| Edge 91 fresh compile under pinned toolchain, exact | **PASS — 106/106 byte-exact** |
| Edge 91 provider-native signed build attestation | **FAIL (provider state)** |
| Edge 91 mode authority for the two 0755 archive paths | **FAIL (contradicts signed tree; structurally outside compile)** |
| Edge 133 signed provenance on any queryable surface | **FAIL — absent on all five; publisher 0/7** |
| Edge 185 signed provenance on any queryable surface | **FAIL — absent on all five; publisher 0/14** |
| Edges closed (of 4) | **0** |
| Cumulative exact bridge | **76/80 (unchanged)** |

## Next causal discriminator

None remains on our side of these edges: every residual gate is a provider/publisher action (corrected Zenodo child; provider-native signed build attestation + mode authority for PAI; publisher-attested re-release for woodtapper/disruption-py — which necessarily changes the file identity). Repeating these probes has no closure value until provider state changes. The estimator-validation artifact additionally prevents any future lane from citing digest-shaped Rekor retrieval as absence evidence.

## Scientific boundary

Development transport/reproducibility evidence only. No natural pair, lineage adjudication, source-disjoint replication, custody transfer, comparator execution, outcome or performance authority is created. The programme terminal `P4_NATURAL_PAIR_SOURCE_TRANSPORT_CANNOT_CHECK` is not modified by this lane.

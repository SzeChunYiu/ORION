# P4 exact-edge build/provenance V12 results

## Verdict

V12 finds a **positive exact packaged-byte result** but closes **0** P4 edges. The cumulative bridge remains **76/80**, and index 91 remains `CANNOT_CHECK`.

## 106 archived Java class extras

The immutable GitHub revision tracks `java/jPAI.jar` at SHA-256 `ff49482838e3a761913df327a48e819d4f9e552bfeab29655a82675c60c47162`. A prospectively frozen, read-only ZIP projection produced exactly **106** `.class` members. After prefixing them with `java/bin/`, the complete multiset equals all 106 Zenodo-archive-only class files: **0 missing, 0 extra, 0 different-byte**. All 106 class files have major version **61** (Java 17).

This is exact packaged-byte availability from the GitHub-authenticated tree, not fresh source compilation and not signed build provenance. The prospectively pinned `eclipse-temurin` 17.0.14+7 linux/arm64 image could not execute: Docker had no daemon/application, and the lawful disposable Colima route ultimately failed with exact terminal `no space left on device`. No substitute compiler and no pytest/CI were used.

## Two executable-mode drifts

GitHub path histories expose one introducing commit for each path. The introducing commit is unsigned; the current content-witness commit `aa021231...` has valid GitHub verification. Both provider trees record `cpp/PAIpp.exe` and `run.sh` as mode **100644**, whereas the checksum-bound archive TAR records both as **0755**. GitHub exact-subject attestation endpoints for the archive and both files return **404**. The one GitHub release has **0 assets** and no predicate binding the archive digest, revision, paths, or modes.

Therefore matching bytes do not establish authority. The archive mode changes are not merely unsigned; they contradict the validly signed revision tree and lack a signed release explanation.

## Closure gates

| Gate | Result |
|---|---|
| Complete tracked-JAR projection equals 106 archive extras | **PASS** |
| Fresh source compilation under the pinned toolchain | **CANNOT_CHECK** |
| Provider-native signed class build provenance | **FAIL** |
| `cpp/PAIpp.exe` archive mode 0755 has signed release authority | **FAIL** |
| `run.sh` archive mode 0755 has signed release authority | **FAIL** |
| Index 91 exact edge closes | **FAIL** |

## Next causal discriminator

Do not repeat the unavailable-runtime probe. Either (1) execute the already frozen linux/arm64 image digest once an OCI runtime and sufficient disposable disk exist, then require the provider signing contract even if bytes match; (2) obtain `AUTHOR_PROVIDER_SIGNING_CONTRACT_V12.json`, binding the exact archive, revision/tree, complete 106-output manifest, build identity, and both deliberate 0755 modes; or (3) provider-replace the checksum-bound archive with one exactly matching immutable revision `aa021231...`, including its signed 100644 modes.

## Scientific boundary

No natural-pair, author-lineage, source-disjoint replication, external custody, comparator outcome, performance, or superiority authority is added. No P4 manuscript or claim-ledger edit is authorized.

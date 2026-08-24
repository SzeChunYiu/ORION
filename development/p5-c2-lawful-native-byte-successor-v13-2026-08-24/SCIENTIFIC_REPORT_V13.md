# P5 C2 lawful scratch-image rights successor V13

## Prospectively frozen question

V13 targeted only `rights.container_and_generated_artifacts`. Before Docker Desktop was started, it froze a `FROM scratch` Linux/arm64 build, a deterministic syscall-only ELF, nine exact rootfs files, a complete per-file rights map, three retained licence/NOTICE texts, the runtime constraints, archive/disposal requirements, and the non-aggregation rule. It did not run pytest, repository CI, MOSS, a model, C4, an evaluator, a scorer, or any protected/outcome data.

## Genuine closure

The exported single layer contained exactly nine regular files and zero symlinks, and every path, byte hash, size and mode matched the frozen rootfs manifest. `IMAGE_SBOM_V13.spdx.json` directly enumerates all nine exported files. `P5_C2_V13_IMAGE_CONTENT_RIGHTS_MAP.json` covers the identical path set. The Apache-2.0 licence, Apache NOTICE and CC0-1.0 text are retained both in the packet and image.

`P5_C2_V13_GENERATED_ARTIFACT_AUTHORITY.json` explicitly authorizes retention, disclosure, publication and redistribution of the newly authored V13 session, transcript, diff, SBOM, image descriptor/archive metadata and evolution-state artifacts, while preserving Apache content under Apache-2.0 rather than relicensing it.

The scratch image built for Linux/arm64, ran with network disabled, a read-only rootfs, all capabilities dropped and no-new-privileges, emitted exactly `ORION V13 container pass\n`, exited zero, and produced an empty `docker diff`. The complete image archive is retained by exact hash and size; the container and daemon image tag were then removed and absence was verified.

## Count and claim boundary

This closes one field for the **distinct V13 successor**: 7/21 becomes **8/21 bound, 13 blocking**. V11 and V12 are not inherited or aggregated. Released MOSS stays 7/21. No performance, H1-H4, superiority, ready-arm, manuscript, or top-tier claim follows.

## Widest defensible positive claim

For this distinct V13 successor, a complete nine-file scratch Linux/arm64 image was built, directly enumerated from its exported layer, matched to a complete SPDX-2.3 SBOM and file-level rights map, accompanied by full Apache/NOTICE/CC0 license bytes and explicit generated-artifact retention/disclosure/publication authority, executed under a read-only no-network no-capability policy with exact output and empty diff, archived, and removed from the Docker daemon.

## Exact terminal

`P5_C2_V13_COMPLETE_SCRATCH_IMAGE_SBOM_LICENSE_AND_GENERATED_ARTIFACT_AUTHORITY_BOUND__DISTINCT_SUCCESSOR_EIGHT_OF_TWENTY_ONE_BOUND__THIRTEEN_BLOCKING__V11_V12_NOT_AGGREGATED__RELEASED_MOSS_UNCHANGED__ZERO_OF_SIX_READY`

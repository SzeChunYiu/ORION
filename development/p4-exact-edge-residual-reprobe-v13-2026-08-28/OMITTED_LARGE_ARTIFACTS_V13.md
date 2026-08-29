# V13 omitted large artifacts

Not retained in the repository (disk-boundary policy, as in prior lanes):

- The Adoptium JDK package `OpenJDK17U-jdk_x64_linux_hotspot_17.0.14_7.tar.gz` (191,943,794 bytes) and its extracted tree. Identity is bound by the verified distributor checksum `a3af83983fb94dd7d11b13ba2dba0fb6819dc2caaf87e6937afd22ad4680ae9a` recorded in `COMPILE_PROJECTION_V13.json`, plus the download byte count.
- The codeload source tarball of revision `aa021231cdafb6d74ce9ab5f55f824a3032058a4` (6,909,445 bytes; sha256 `d43c827568d1acef62cea08990580a95ea5869f9eef4106fb3da8b941377e5af`) and the 106 emitted `.class` files. All 106 class hashes are recorded in `COMPILE_PROJECTION_V13.json` (comparison basis) and in the V12 checksum-bound manifest.
- The compile workdir was deleted after receipt capture (`shutil.rmtree`).

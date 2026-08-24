# P5 C2 V11-V13 manuscript integration audit

This read-only audit verifies three separate successors. It does not aggregate their field closures, modify released MOSS, or change the global 55/126 panel census.

## Exact successor states

- V11: distinct runtime successor, 8/21 bound and 13 blocking.
- V12: distinct source-core successor, 9/21 bound and 12 blocking. V11 is not inherited.
- V13: distinct scratch-image-rights successor, 8/21 bound and 13 blocking. V11 and V12 are not inherited.
- Released MOSS remains 7/21 bound and 14 blocking.
- Zero of six arms is ready; H1-H4, performance and superiority remain `CANNOT_CHECK`.

## V13 four-way path bijection

After documented path normalization, the frozen build-context rootfs, exported-layer inventory, file-level rights map and SPDX 2.3 `fileName` set are identical. Each contains exactly nine regular files and no symlinks:

- `/orion/GENERATED_ARTIFACT_AUTHORITY_V13.json`
- `/orion/IMAGE_CONTENT_RIGHTS_MAP_V13.json`
- `/orion/input/CASE_BODY_V6.json`
- `/orion/input/TASK_SPECIFICATION_V6.md`
- `/orion/input/commons-lang-source.tar.gz`
- `/orion/licenses/APACHE-2.0.txt`
- `/orion/licenses/APACHE-NOTICE.txt`
- `/orion/licenses/CC0-1.0.txt`
- `/orion/probe`

The V13 packet validator passes, all packet checksums verify, and the retained runtime receipt records exact stdout `ORION V13 container pass\n`, exit 0, no network, read-only rootfs, all capabilities dropped, no-new-privileges and an empty container diff. The archived image was removed from the daemon and the ephemeral remote Docker environment was destroyed. No pytest, repository CI, MOSS/model/C4/evaluator/scorer/protected-data execution, performance observation or superiority comparison was performed by this audit.

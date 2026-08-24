#!/usr/bin/env python3
from __future__ import annotations

import datetime as dt
import hashlib
import json
import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
REPO = ROOT.parent.parent
V11 = ROOT.parent / "p4-exact-edge-lineage-authority-v11-2026-08-24"
IDENTITY = V11 / "EDGE_91_EMBEDDED_HEAD_CONTENT_IDENTITY_V11.json"
MANIFESTS = V11 / "EDGE_91_NORMALIZED_MANIFESTS_V11.json"
V11_RESULT = V11 / "RESULT_V11.json"
V11_SUMS = V11 / "SHA256SUMS"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def canonical_sha(value: object) -> str:
    payload = json.dumps(value, sort_keys=True, separators=(",", ":")).encode()
    return hashlib.sha256(payload).hexdigest()


def lookup(manifest: list[dict], path: str) -> dict:
    matches = [item for item in manifest if item["normalized_path"] == path]
    if len(matches) != 1:
        raise AssertionError((path, len(matches)))
    return matches[0]


identity = json.loads(IDENTITY.read_text())
manifests = json.loads(MANIFESTS.read_text())
github_manifest = manifests["github_codeload"]["manifest"]
archive_manifest = manifests["archive_non_git_payload"]["manifest"]

assert sha256(V11_RESULT) == "dee86c33a0347df5da2425ebc606c12020cfffdff6ac21cea6b23b570ad8fef4"
assert sha256(V11_SUMS) == "72cb2fd2a3e0830fe113a69e8db2311416dab67b5cab59a1c732a20ea0048eed"
assert identity["content_witness_revision"] == "aa021231cdafb6d74ce9ab5f55f824a3032058a4"
assert identity["embedded_git"]["tree"] == "d5620f3acf4e5a163cfdfdefc2432ebd5709008a"
assert identity["comparison"]["only_left_count"] == 106

source_rows = [
    item
    for item in github_manifest
    if item["normalized_path"].startswith("java/src/")
    and item["normalized_path"].endswith(".java")
]
source_rows.sort(key=lambda item: item["normalized_path"])
assert len(source_rows) == 106

expected_paths = sorted(identity["comparison"]["only_left"])
assert len(expected_paths) == 106
expected_outputs = [lookup(archive_manifest, path) for path in expected_paths]
assert all(item["entry_type"] == "regular" for item in expected_outputs)

mode_rows = []
for difference in identity["comparison"]["differing"]:
    mode_rows.append(
        {
            "path": difference["normalized_path"],
            "archive": difference["left"],
            "immutable_revision": difference["right"],
            "embedded_git_index_mode": "100644",
            "archive_tar_mode": "0755",
        }
    )
assert [row["path"] for row in mode_rows] == ["cpp/PAIpp.exe", "run.sh"]

python_real = Path(os.path.realpath(sys.executable))
head = subprocess.run(
    ["git", "rev-parse", "HEAD"], cwd=REPO, check=True, capture_output=True, text=True
).stdout.strip()
frozen_at = dt.datetime.now(dt.timezone.utc).isoformat().replace("+00:00", "Z")

protocol = {
    "schema_version": "orion.p4.exact-edge-build-provenance.v12.protocol",
    "identity": "P4.M6.JOSS.EXACT.EDGE.BUILD.PROVENANCE.V12",
    "frozen_at": frozen_at,
    "repository_head_at_freeze": head,
    "outcome_informed": True,
    "new_outcome_access_before_freeze": True,
    "pre_freeze_access_boundary": [
        "Immutable V10/V11 results, manifests, receipts and index-91 adverse state were read.",
        "The checksum-bound Zenodo archive and immutable GitHub codeload were reacquired and hash-checked, then extracted transiently.",
        "java/README.md, java/.classpath, Eclipse Java 1.8 preferences, embedded .git/config, Git tree modes, TAR modes and the tracked jPAI.jar manifest were inspected.",
        "The jPAI.jar manifest reports Created-By 17.0.14 (Debian), and the archive and codeload copies of that tracked JAR have equal SHA-256; class-member equality and any fresh compilation outcome were not accessed before this freeze.",
    ],
    "predecessor": {
        "identity": "P4.M6.JOSS.EXACT.EDGE.LINEAGE.AUTHORITY.V11",
        "result_path": "development/p4-exact-edge-lineage-authority-v11-2026-08-24/RESULT_V11.json",
        "result_sha256": sha256(V11_RESULT),
        "sha256sums_path": "development/p4-exact-edge-lineage-authority-v11-2026-08-24/SHA256SUMS",
        "sha256sums_sha256": sha256(V11_SUMS),
        "index_91_verdict": identity["verdict"],
        "cumulative_exact_bridge": "76/80",
    },
    "frozen_unit": {
        "frozen_index": 91,
        "repository": "NutritionalLungImmunity/PAI",
        "publication_version": "v1.0.0",
        "accepted_tag_commit": "9fa30e9f405de4446c792bd59cb7c5a4bb7ecb59",
        "content_witness_revision": "aa021231cdafb6d74ce9ab5f55f824a3032058a4",
        "content_witness_tree": "d5620f3acf4e5a163cfdfdefc2432ebd5709008a",
        "zenodo_record": 20171460,
        "zenodo_archive_bytes": 17147954,
        "zenodo_archive_sha256": "2a94e0ed7e61e18ea4135aa559d6a06a407adcabd84dbbc52ebface6bba5b407",
        "github_codeload_bytes": 6909445,
        "github_codeload_sha256": "d43c827568d1acef62cea08990580a95ea5869f9eef4106fb3da8b941377e5af",
    },
    "source_freeze": {
        "source_count": len(source_rows),
        "source_manifest_sha256": canonical_sha(source_rows),
        "source_manifest": source_rows,
        "tracked_jar": {
            **lookup(github_manifest, "java/jPAI.jar"),
            "git_blob": "3cfbeb5d147a3c37ab0f4e5b4a4caa8c0c09b882",
        },
        "build_instruction": lookup(github_manifest, "java/README.md"),
        "eclipse_classpath": lookup(github_manifest, "java/.classpath"),
        "eclipse_preferences": lookup(
            github_manifest, "java/.settings/org.eclipse.jdt.core.prefs"
        ),
    },
    "expected_archive_only_outputs": {
        "count": len(expected_outputs),
        "manifest_sha256": canonical_sha(expected_outputs),
        "manifest": expected_outputs,
    },
    "pinned_lawful_tooling": {
        "jar_member_reader": {
            "implementation": "CPython standard-library zipfile; read-only extraction and CRC verification",
            "python_version": sys.version,
            "executable": str(python_real),
            "executable_sha256": sha256(python_real),
            "license_boundary": "Python Software Foundation licensed local runtime; no private or restricted tool used.",
        },
        "compiler_container": {
            "registry": "docker.io/library/eclipse-temurin",
            "tag_observed_before_freeze": "17.0.14_7-jdk",
            "platform": "linux/arm64/v8",
            "manifest_digest": "sha256:38e51c132b7e3bd6c5b131303792ece0a8a6f32ee1039eee2c04a87678760861",
            "required_runtime_check": "javac -version must print javac 17.0.14 and java -version must identify OpenJDK 17.0.14+7 before compilation",
            "license_boundary": "Public Eclipse Temurin OpenJDK image; runtime labels and component/license inventory must be captured in the SBOM.",
        },
    },
    "class_investigation": {
        "jar_projection_gate": "From the immutable-revision tracked java/jPAI.jar, select every non-directory *.class ZIP member. Prefix each member with java/bin/. Pass only if the complete sorted path/type/byte-count/SHA-256 multiset exactly equals all 106 frozen archive-only outputs; any missing, extra, duplicate, CRC failure or byte difference fails.",
        "jar_projection_boundary": "A pass proves exact packaged-byte availability in the GitHub-authenticated tree and a deterministic extraction route. It is not source compilation, a signed attestation, author custody, or release authority.",
        "compiler_command": "Within an empty output directory and immutable source checkout: find java/src -type f -name '*.java' -print0 | LC_ALL=C sort -z | xargs -0 javac -d /out",
        "compiler_gate": "Run once in the pinned linux/arm64 image after its digest and javac version checks pass. Pass only if compilation returns 0 and the complete sorted fresh *.class output multiset, normalized under java/bin/, exactly equals all 106 frozen outputs in path, byte count and SHA-256; no subset credit.",
        "compiler_boundary": "Exact bytes establish narrow reproducibility under one pinned toolchain. They do not establish signed provenance, authority, author custody or acceptance of the publication tag mismatch.",
    },
    "mode_investigation": {
        "frozen_differences": mode_rows,
        "requests": [
            "GitHub official commits?path=... history for cpp/PAIpp.exe and run.sh, followed by exact Git tree mode inspection for every returned full revision.",
            "GitHub official releases and artifact-attestation endpoints for the exact archive/file subjects when available.",
            "Zenodo official record/file metadata already binding the archive checksum; inspect only provider-native signing/provenance fields, never infer mode authority from the TAR header alone.",
        ],
        "authority_gate": "Pass a path only if a provider-native signed build/release statement binds the exact checksum-bound archive (or exact file digest), full revision aa021231..., that path, and executable mode 0755. A historical 100755 commit, matching bytes, current Git mode, TAR header, local chmod, README wording or unsigned metadata alone is insufficient.",
        "joint_gate": "Both paths must pass independently; one does not compensate for the other.",
    },
    "sbom_requirement": "Retain a machine-readable inventory of all 106 sources, expected and observed class outputs, tracked JAR, exact image manifest/config/layers, javac/java versions, licenses, commands, return codes and mode-provenance responses.",
    "closure_rule": "V12 may report exact JAR projection and/or compiler reproducibility separately from authoritative provenance. Index 91 closes only if all 106 outputs exactly reproduce and both mode drifts obtain provider-native signed authority; otherwise REMAINS_CANNOT_CHECK.",
    "scientific_boundary": "No natural-pair, lineage-independence, source-disjoint replication, external custody, comparator outcome, performance or superiority authority follows from reproduction or matching bytes.",
    "forbidden": [
        "modify P4 V10/V11, the P4 manuscript or claim ledger",
        "run pytest or repository CI",
        "accept subset equality or omit an archive-only class",
        "treat reproducibility or matching bytes as signed provenance",
        "repeat a build after the one bounded pinned-toolchain probe without a new prospective protocol",
    ],
    "terminal_if_unavailable": "If the exact pinned image cannot be lawfully acquired or fails the version check, do not substitute another compiler. Preserve the exact blocker and issue the narrowest provider signing contract binding the 106-output manifest and two mode paths to revision aa021231....",
}

protocol_path = ROOT / "PROTOCOL_V12.json"
protocol_path.write_text(json.dumps(protocol, indent=2, sort_keys=True) + "\n")
receipt = {
    "schema_version": "orion.p4.exact-edge-build-provenance.v12.protocol-freeze-receipt",
    "identity": protocol["identity"],
    "frozen_at": frozen_at,
    "outcome_informed": True,
    "new_outcome_access_before_freeze": True,
    "repository_head_at_freeze": head,
    "predecessor_result_sha256": protocol["predecessor"]["result_sha256"],
    "protocol_path": protocol_path.name,
    "protocol_bytes": protocol_path.stat().st_size,
    "protocol_sha256": sha256(protocol_path),
    "source_count": len(source_rows),
    "expected_output_count": len(expected_outputs),
}
(ROOT / "PROTOCOL_FREEZE_RECEIPT_V12.json").write_text(
    json.dumps(receipt, indent=2, sort_keys=True) + "\n"
)
print(json.dumps(receipt, sort_keys=True))

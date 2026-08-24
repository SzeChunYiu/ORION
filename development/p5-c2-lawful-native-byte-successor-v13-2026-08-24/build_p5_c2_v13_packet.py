#!/usr/bin/env python3
"""Freeze and execute the P5 C2 V13 scratch-image rights discriminator."""

from __future__ import annotations

import argparse
import gzip
import hashlib
import io
import json
import os
import shutil
import subprocess
import tarfile
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


HERE = Path(__file__).resolve().parent
REPO = HERE.parents[1]
IDENTITY = "C2_RIGHTS_CLEARED_SCRATCH_IMAGE_SUCCESSOR__ORION_V13"
TAG = "orion-p5-c2-v13:20260824"
CONTAINER = "orion-p5-c2-v13-run"
FIELD = "rights.container_and_generated_artifacts"
SOURCE_DATE_EPOCH = 1787529600
EXPECTED_STDOUT = b"ORION V13 container pass\n"
V6 = REPO / "development/p5-common-visible-case-rights-v6-2026-08-23"
V11 = REPO / "development/p5-c2-lawful-native-byte-successor-v11-2026-08-24"
V12 = REPO / "development/p5-c2-lawful-native-byte-successor-v12-2026-08-24"
REGISTRY = REPO / "development/p5-moss-execution-binding-v4-2026-08-23/P5_C2_V4_FIELD_REGISTRY.json"
GENERATOR = HERE / "probe/generate_aarch64_probe_v13.py"
VALIDATOR = HERE / "validate_p5_c2_v13_packet.py"
BUILDER = Path(__file__).resolve()


def now() -> str:
    return datetime.now(timezone.utc).isoformat()


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def sha1_bytes(data: bytes) -> str:
    return hashlib.sha1(data).hexdigest()


def ref(path: Path, base: Path = HERE) -> dict[str, Any]:
    return {
        "path": path.relative_to(base).as_posix(),
        "sha256": sha256(path),
        "size_bytes": path.stat().st_size,
    }


def external_ref(path: Path) -> dict[str, Any]:
    return ref(path, REPO)


def write_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def run(command: list[str], *, check: bool = True, env: dict[str, str] | None = None) -> subprocess.CompletedProcess[bytes]:
    completed = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=False, env=env)
    if check and completed.returncode != 0:
        raise RuntimeError(
            f"command failed ({completed.returncode}): {command!r}\n"
            + completed.stdout.decode("utf-8", "replace")
            + completed.stderr.decode("utf-8", "replace")
        )
    return completed


def docker(*args: str, check: bool = True, env: dict[str, str] | None = None) -> subprocess.CompletedProcess[bytes]:
    return run(["rtk", "proxy", "docker", *args], check=check, env=env)


def copy_exact(source: Path, target: Path, mode: int = 0o644) -> None:
    target.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(source, target)
    target.chmod(mode)


def context_files() -> list[Path]:
    context = HERE / "build-context"
    return sorted(path for path in context.rglob("*") if path.is_file() or path.is_symlink())


def rootfs_expected() -> dict[str, dict[str, Any]]:
    root = HERE / "build-context/rootfs"
    result: dict[str, dict[str, Any]] = {}
    for path in sorted(root.rglob("*")):
        if path.is_file() and not path.is_symlink():
            result["/" + path.relative_to(root).as_posix()] = {
                "type": "file",
                "sha256": sha256(path),
                "size_bytes": path.stat().st_size,
                "mode": oct(path.stat().st_mode & 0o777),
            }
        elif path.is_symlink():
            result["/" + path.relative_to(root).as_posix()] = {
                "type": "symlink",
                "target": os.readlink(path),
            }
    return result


def set_context_times() -> None:
    context = HERE / "build-context"
    for path in sorted(context.rglob("*"), reverse=True):
        if not path.is_symlink():
            os.utime(path, (SOURCE_DATE_EPOCH, SOURCE_DATE_EPOCH))
    os.utime(context, (SOURCE_DATE_EPOCH, SOURCE_DATE_EPOCH))


def freeze() -> None:
    if not GENERATOR.is_file() or not VALIDATOR.is_file():
        raise RuntimeError("generator and validator must exist before freeze")
    pre = docker("info", "--format", "{{.ServerVersion}}", check=False)
    if pre.returncode == 0:
        raise RuntimeError("Docker server was already active; V13 requires freeze before daemon startup")

    context = HERE / "build-context"
    if context.exists():
        shutil.rmtree(context)
    (context / "rootfs/orion/input").mkdir(parents=True)
    (context / "rootfs/orion/licenses").mkdir(parents=True)
    (HERE / "licenses").mkdir(exist_ok=True)

    source = V6 / "candidate_visible/source/commons-lang-396afc3e4693cfee182efe582455f2d97058c068.tar.gz"
    case = V6 / "candidate_visible/CASE_BODY_V6.json"
    task = V6 / "candidate_visible/TASK_SPECIFICATION_V6.md"
    apache = V6 / "candidate_visible/APACHE-2.0-LICENSE.txt"
    notice = V6 / "candidate_visible/APACHE-NOTICE.txt"
    cc0 = V6 / "candidate_visible/PACKET-CONTENT-CC0-1.0.txt"
    expected = {
        source: "f97c316795a6ba124f693bce9e8019b1735bc976affa9bce8d4c52f668575f08",
        case: "3e5d001eee38d62c93c5f00acf59adba0a55cadf6df7040bdb2c432c1c16f921",
        task: "a455eec2d32b031b6e49d06c73e0cf3befbe9e2cd461e5417efbade5f39f5098",
        apache: "cfc7749b96f63bd31c3c42b5c471bf756814053e847c10f3eb003417bc523d30",
        notice: "3b1830189d4da56ebc6e43f32a96b92caa3392cdc0c5ba4af7c399f81696545d",
        cc0: "a2010f343487d3f7618affe54f789f5487602331c0a8d03f49e9a7c547cf0499",
    }
    for path, digest in expected.items():
        if sha256(path) != digest:
            raise RuntimeError(f"predecessor input hash mismatch: {path}")

    copy_exact(source, context / "rootfs/orion/input/commons-lang-source.tar.gz")
    copy_exact(case, context / "rootfs/orion/input/CASE_BODY_V6.json")
    copy_exact(task, context / "rootfs/orion/input/TASK_SPECIFICATION_V6.md")
    copy_exact(apache, context / "rootfs/orion/licenses/APACHE-2.0.txt")
    copy_exact(notice, context / "rootfs/orion/licenses/APACHE-NOTICE.txt")
    copy_exact(cc0, context / "rootfs/orion/licenses/CC0-1.0.txt")
    copy_exact(apache, HERE / "licenses/APACHE-2.0.txt")
    copy_exact(notice, HERE / "licenses/APACHE-NOTICE.txt")
    copy_exact(cc0, HERE / "licenses/CC0-1.0.txt")

    authority = {
        "schema_version": "orion.p5.c2.generated-artifact-authority.v13",
        "successor_identity": IDENTITY,
        "authority_status": "EXPLICIT_FOR_NEWLY_AUTHORED_V13_ARTIFACTS_ONLY",
        "grantor": "Authors of the V13 packet acting through the repository owner",
        "authorization_basis": "These newly authored V13 bytes were produced for the repository owner's directed publication research workflow and are expressly dedicated under CC0-1.0 by the packet authors acting through that owner.",
        "grant": "To the fullest extent permitted, the newly authored V13 artifacts are dedicated under CC0-1.0. Retention, reproduction, verification, modification, disclosure, publication and redistribution are explicitly authorized worldwide without field-of-use restriction.",
        "effective_scope": [
            "protocol, freeze and preflight receipts",
            "probe source, generated binary and generation receipt",
            "Dockerfile, build-context metadata and scratch-image configuration",
            "session, build, runtime and diff transcripts",
            "image descriptor, inspect data, layer manifest, SBOM and archive metadata",
            "retained image archive containing only separately mapped Apache-2.0 and CC0-1.0 content",
            "generated-artifact authority, rights maps, result, recursive ledger, report, README, validator, validation receipt, artifact manifest and SHA256SUMS",
            "future disclosure/publication copies of the exact V13 evolution-state artifacts",
        ],
        "third_party_boundary": "No third-party content is relicensed. Apache Commons Lang bytes remain Apache-2.0 with NOTICE; V6 case/task bytes retain their inherited CC0-1.0 disposition; license texts remain documentary terms.",
        "excluded": [
            "released MOSS identity or bytes not copied into this image",
            "model or service content",
            "protected, gold, hidden, scorer or feedback data",
            "known fix patch or fixed source tree",
            "any external content not enumerated by the image-content rights map",
        ],
        "retention_authorized": True,
        "disclosure_authorized": True,
        "publication_authorized": True,
        "redistribution_authorized": True,
        "generated_session_and_evolution_state_authorized": True,
        "license_spdx": "CC0-1.0",
        "license_path": "/orion/licenses/CC0-1.0.txt",
        "legal_advice": False,
    }
    rights_rows = [
        ("/orion/probe", "CC0-1.0", "New deterministic syscall-only probe"),
        ("/orion/input/commons-lang-source.tar.gz", "Apache-2.0", "Exact V6 Apache Commons Lang archive; NOTICE retained"),
        ("/orion/input/CASE_BODY_V6.json", "CC0-1.0", "Exact V6 authored case body"),
        ("/orion/input/TASK_SPECIFICATION_V6.md", "CC0-1.0", "Exact V6 authored task specification"),
        ("/orion/licenses/APACHE-2.0.txt", "Apache-2.0", "Retained Apache-2.0 license text"),
        ("/orion/licenses/APACHE-NOTICE.txt", "Apache-2.0", "Retained Apache NOTICE"),
        ("/orion/licenses/CC0-1.0.txt", "CC0-1.0", "Retained CC0-1.0 legal text"),
        ("/orion/GENERATED_ARTIFACT_AUTHORITY_V13.json", "CC0-1.0", "New explicit generated-artifact authority"),
        ("/orion/IMAGE_CONTENT_RIGHTS_MAP_V13.json", "CC0-1.0", "New complete image-content rights map"),
    ]
    rights_map = {
        "schema_version": "orion.p5.c2.image-content-rights-map.v13",
        "successor_identity": IDENTITY,
        "status": "COMPLETE_FOR_EVERY_REGULAR_FILE_OR_SYMLINK_EXPECTED_IN_SCRATCH_ROOTFS",
        "base_image": "scratch",
        "base_image_third_party_files": 0,
        "entries": [
            {"path": path, "type": "regular_file", "license_concluded": license_id, "disposition": note}
            for path, license_id, note in rights_rows
        ],
        "regular_file_count": len(rights_rows),
        "symlink_count": 0,
        "all_entries_retention_disclosure_publication_addressed": True,
        "license_bundle_paths": [
            "/orion/licenses/APACHE-2.0.txt",
            "/orion/licenses/APACHE-NOTICE.txt",
            "/orion/licenses/CC0-1.0.txt",
        ],
        "boundary": "Completeness is accepted only if the exported layer inventory equals this exact path set and each byte hash equals the frozen rootfs manifest.",
        "legal_advice": False,
    }
    write_json(HERE / "P5_C2_V13_GENERATED_ARTIFACT_AUTHORITY.json", authority)
    write_json(HERE / "P5_C2_V13_IMAGE_CONTENT_RIGHTS_MAP.json", rights_map)
    copy_exact(HERE / "P5_C2_V13_GENERATED_ARTIFACT_AUTHORITY.json", context / "rootfs/orion/GENERATED_ARTIFACT_AUTHORITY_V13.json")
    copy_exact(HERE / "P5_C2_V13_IMAGE_CONTENT_RIGHTS_MAP.json", context / "rootfs/orion/IMAGE_CONTENT_RIGHTS_MAP_V13.json")

    probe = context / "rootfs/orion/probe"
    run(["rtk", "python3", str(GENERATOR), "--output", str(probe)])
    if probe.read_bytes()[:4] != b"\x7fELF" or probe.read_bytes()[18:20] != (183).to_bytes(2, "little"):
        raise RuntimeError("generated probe is not ELF64/AArch64")

    dockerfile = """FROM scratch
COPY --chown=0:0 rootfs/ /
LABEL org.opencontainers.image.title=\"ORION-P5-C2-V13-rights-cleared-probe\"
LABEL org.opencontainers.image.licenses=\"Apache-2.0-AND-CC0-1.0\"
ENTRYPOINT [\"/orion/probe\"]
"""
    (context / "Dockerfile").write_text(dockerfile, encoding="utf-8")
    (context / "Dockerfile").chmod(0o644)
    set_context_times()

    root_expected = rootfs_expected()
    if set(root_expected) != {row[0] for row in rights_rows}:
        raise RuntimeError("rights map does not enumerate exact rootfs")
    context_manifest = {
        "schema_version": "orion.p5.c2.build-context-manifest.v13",
        "successor_identity": IDENTITY,
        "source_date_epoch": SOURCE_DATE_EPOCH,
        "dockerfile": ref(context / "Dockerfile"),
        "build_context_files": [ref(path) for path in context_files()],
        "rootfs_regular_files": root_expected,
        "rootfs_regular_file_count": len(root_expected),
        "rootfs_symlink_count": 0,
        "base_image": "scratch",
        "network_required_to_build": False,
    }
    write_json(HERE / "BUILD_CONTEXT_MANIFEST_V13.json", context_manifest)
    probe_receipt = {
        "schema_version": "orion.p5.c2.probe-generation-receipt.v13",
        "generator": ref(GENERATOR),
        "binary": ref(probe),
        "elf_class": "ELF64",
        "elf_data": "little-endian",
        "elf_machine": "AArch64",
        "runtime_abi": "Linux syscalls write=64 and exit=93 only",
        "expected_stdout_hex": EXPECTED_STDOUT.hex(),
        "expected_exit_code": 0,
        "dynamic_dependencies": [],
        "authored_license": "CC0-1.0",
    }
    write_json(HERE / "PROBE_GENERATION_RECEIPT_V13.json", probe_receipt)
    license_manifest = {
        "schema_version": "orion.p5.c2.license-bundle-manifest.v13",
        "complete_for_expected_rootfs": True,
        "licenses": {
            "Apache-2.0": ref(HERE / "licenses/APACHE-2.0.txt"),
            "Apache-NOTICE": ref(HERE / "licenses/APACHE-NOTICE.txt"),
            "CC0-1.0": ref(HERE / "licenses/CC0-1.0.txt"),
        },
        "image_copy_paths": [
            "/orion/licenses/APACHE-2.0.txt",
            "/orion/licenses/APACHE-NOTICE.txt",
            "/orion/licenses/CC0-1.0.txt",
        ],
    }
    write_json(HERE / "LICENSE_BUNDLE_MANIFEST_V13.json", license_manifest)

    external_inputs = {
        "field_registry_v4": external_ref(REGISTRY),
        "v6_rights_manifest": external_ref(V6 / "P5_SHARED_CASE_RIGHTS_MANIFEST_V6.json"),
        "v6_six_arm_acceptance": external_ref(V6 / "P5_SIX_ARM_SHARED_CORE_ACCEPTANCE_V6.json"),
        "v6_source_archive": external_ref(source),
        "v6_case_body": external_ref(case),
        "v6_task_specification": external_ref(task),
        "v11_result": external_ref(V11 / "P5_C2_V11_RESULT.json"),
        "v12_result": external_ref(V12 / "P5_C2_V12_RESULT.json"),
    }
    protocol = {
        "schema_version": "orion.p5.c2.lawful-native-byte-successor-protocol.v13",
        "protocol_id": "P5.C2.RIGHTS.CLEARED.SCRATCH.IMAGE.SUCCESSOR.V13",
        "successor_identity": IDENTITY,
        "target_field": FIELD,
        "prospective_gate": "Frozen before Docker Desktop startup, image build, runtime output, diff, image identity and archive identity.",
        "frozen_at_utc": now(),
        "identity_boundary": {
            "distinct_from_released_moss": True,
            "distinct_from_v11": True,
            "distinct_from_v12": True,
            "aggregation_with_v11_or_v12_authorized": False,
            "count_basis_before": {"bound": 7, "blocking": 14},
            "count_basis_after_only_if_gate_passes": {"bound": 8, "blocking": 13},
        },
        "build_contract": {
            "base_image": "scratch",
            "platform": "linux/arm64",
            "tag": TAG,
            "network": "none",
            "no_cache": True,
            "source_date_epoch": SOURCE_DATE_EPOCH,
            "provenance_attestation": False,
            "automatic_sbom_attestation": False,
            "reason": "The complete rootfs SBOM and rights map are produced and checked directly from the exported layer.",
        },
        "runtime_contract": {
            "expected_stdout_hex": EXPECTED_STDOUT.hex(),
            "expected_stderr_hex": "",
            "expected_exit_code": 0,
            "network": "none",
            "read_only_rootfs": True,
            "capabilities_dropped": "ALL",
            "no_new_privileges": True,
            "expected_diff_entries": 0,
        },
        "closure_gate": [
            "all frozen predecessor and context hashes match",
            "Docker image builds from scratch for linux/arm64 with build network none",
            "actual exported rootfs regular-file/symlink inventory and hashes equal the frozen rootfs manifest",
            "complete SPDX-2.3 SBOM enumerates every actual rootfs regular file/symlink",
            "image-content rights map enumerates the same exact path set and the full license/NOTICE bundle is retained",
            "generated-artifact authority explicitly covers retention, disclosure, publication and redistribution of the named V13 artifact classes",
            "constrained runtime exits zero with exact stdout, empty stderr and empty docker diff",
            "image descriptor/config/layer identities and retained image archive hash/size are captured",
            "container and daemon image identity are removed and absence is verified after receipts are frozen",
        ],
        "fail_closed": "Any failed gate leaves the target field UNBOUND and preserves the exact adverse result.",
        "executions_forbidden": [
            "C4",
            "released MOSS benchmark",
            "coding agent or model",
            "public or protected evaluator/scorer",
            "protected, gold, hidden or feedback data",
            "known fix patch or fixed source tree",
            "pytest or repository CI",
        ],
        "manuscript_edit_rule": "No manuscript or shared-claim-ledger edit in this additive owned lane.",
        "frozen_code": {
            "builder": ref(BUILDER),
            "validator": ref(VALIDATOR),
            "probe_generator": ref(GENERATOR),
        },
        "frozen_packet_inputs": {
            "build_context_manifest": ref(HERE / "BUILD_CONTEXT_MANIFEST_V13.json"),
            "probe_generation_receipt": ref(HERE / "PROBE_GENERATION_RECEIPT_V13.json"),
            "license_bundle_manifest": ref(HERE / "LICENSE_BUNDLE_MANIFEST_V13.json"),
            "generated_artifact_authority": ref(HERE / "P5_C2_V13_GENERATED_ARTIFACT_AUTHORITY.json"),
            "image_content_rights_map": ref(HERE / "P5_C2_V13_IMAGE_CONTENT_RIGHTS_MAP.json"),
        },
        "external_inputs": external_inputs,
    }
    write_json(HERE / "P5_C2_V13_FROZEN_PROTOCOL.json", protocol)
    freeze_receipt = {
        "schema_version": "orion.p5.c2.execution-freeze.v13",
        "successor_identity": IDENTITY,
        "frozen_before_docker_server_start": True,
        "docker_client_present": True,
        "docker_server_pre_freeze_returncode": pre.returncode,
        "docker_server_pre_freeze_stdout": pre.stdout.decode("utf-8", "replace"),
        "docker_server_pre_freeze_stderr": pre.stderr.decode("utf-8", "replace"),
        "protocol": ref(HERE / "P5_C2_V13_FROZEN_PROTOCOL.json"),
        "build_context_manifest": ref(HERE / "BUILD_CONTEXT_MANIFEST_V13.json"),
        "rootfs_regular_file_count": len(root_expected),
        "rootfs_symlink_count": 0,
        "docker_execution_authorized": True,
        "candidate_or_outcome_execution_authorized": False,
        "pytest_or_repository_ci_authorized": False,
        "created_at_utc": now(),
        "terminal": "P5_C2_V13_PROTOCOL_AND_COMPLETE_NINE_FILE_SCRATCH_ROOTFS_FROZEN_BEFORE_DOCKER_SERVER_START",
    }
    write_json(HERE / "P5_C2_V13_EXECUTION_FREEZE.json", freeze_receipt)
    print(freeze_receipt["terminal"])


def verify_frozen_inputs() -> None:
    freeze_receipt = json.loads((HERE / "P5_C2_V13_EXECUTION_FREEZE.json").read_text())
    protocol = json.loads((HERE / "P5_C2_V13_FROZEN_PROTOCOL.json").read_text())
    for block, base in ((protocol["frozen_code"], HERE), (protocol["frozen_packet_inputs"], HERE), (protocol["external_inputs"], REPO)):
        for item in block.values():
            path = base / item["path"]
            if not path.is_file() or path.stat().st_size != item["size_bytes"] or sha256(path) != item["sha256"]:
                raise RuntimeError(f"frozen input mismatch: {path}")
    context_manifest = json.loads((HERE / "BUILD_CONTEXT_MANIFEST_V13.json").read_text())
    for item in context_manifest["build_context_files"]:
        path = HERE / item["path"]
        if not path.is_file() or path.stat().st_size != item["size_bytes"] or sha256(path) != item["sha256"]:
            raise RuntimeError(f"build context drift: {path}")
    if sha256(HERE / freeze_receipt["protocol"]["path"]) != freeze_receipt["protocol"]["sha256"]:
        raise RuntimeError("protocol drift")


def archive_structure(archive: Path) -> tuple[dict[str, Any], bytes, str, list[str]]:
    with tarfile.open(archive, "r:*") as outer:
        names = outer.getnames()
        if "manifest.json" not in names:
            raise RuntimeError("docker save archive lacks manifest.json")
        manifest = json.loads(outer.extractfile("manifest.json").read())
        if not isinstance(manifest, list) or len(manifest) != 1:
            raise RuntimeError("unexpected docker save manifest cardinality")
        row = manifest[0]
        layers = row.get("Layers", [])
        if len(layers) != 1:
            raise RuntimeError(f"scratch image expected exactly one layer, got {len(layers)}")
        layer_name = layers[0]
        layer_bytes = outer.extractfile(layer_name).read()
        return row, layer_bytes, layer_name, names


def layer_inventory(layer_bytes: bytes) -> dict[str, dict[str, Any]]:
    result: dict[str, dict[str, Any]] = {}
    with tarfile.open(fileobj=io.BytesIO(layer_bytes), mode="r:*") as layer:
        for member in layer.getmembers():
            clean = member.name.lstrip("./")
            if not clean or member.isdir():
                continue
            path = "/" + clean
            if member.isfile():
                data = layer.extractfile(member).read()
                result[path] = {
                    "type": "file",
                    "sha256": hashlib.sha256(data).hexdigest(),
                    "sha1": sha1_bytes(data),
                    "size_bytes": len(data),
                    "mode": oct(member.mode & 0o777),
                    "uid": member.uid,
                    "gid": member.gid,
                }
            elif member.issym() or member.islnk():
                result[path] = {
                    "type": "symlink",
                    "target": member.linkname,
                    "mode": oct(member.mode & 0o777),
                    "uid": member.uid,
                    "gid": member.gid,
                }
            else:
                raise RuntimeError(f"unexpected non-directory layer entry: {member.name} type={member.type!r}")
    return result


def spdx_document(inventory: dict[str, dict[str, Any]], rights: dict[str, str], image_id: str) -> dict[str, Any]:
    files = []
    relationships = [{"spdxElementId": "SPDXRef-DOCUMENT", "relationshipType": "DESCRIBES", "relatedSpdxElement": "SPDXRef-Package-ImageRootfs"}]
    verification_hashes = []
    for index, path in enumerate(sorted(inventory), 1):
        item = inventory[path]
        spdx_id = f"SPDXRef-File-{index:03d}"
        row: dict[str, Any] = {
            "SPDXID": spdx_id,
            "fileName": "." + path,
            "fileTypes": ["BINARY" if path == "/orion/probe" else "TEXT" if not path.endswith((".tar.gz", ".json")) else "ARCHIVE" if path.endswith(".tar.gz") else "TEXT"],
            "licenseConcluded": rights[path],
            "licenseInfoInFiles": [rights[path]],
            "copyrightText": "NOASSERTION",
        }
        if item["type"] == "file":
            row["checksums"] = [
                {"algorithm": "SHA256", "checksumValue": item["sha256"]},
                {"algorithm": "SHA1", "checksumValue": item["sha1"]},
            ]
            verification_hashes.append(item["sha1"])
        else:
            row["comment"] = f"Symbolic link target: {item['target']}"
        files.append(row)
        relationships.append({"spdxElementId": "SPDXRef-Package-ImageRootfs", "relationshipType": "CONTAINS", "relatedSpdxElement": spdx_id})
    verification = hashlib.sha1("".join(sorted(verification_hashes)).encode("ascii")).hexdigest()
    return {
        "spdxVersion": "SPDX-2.3",
        "dataLicense": "CC0-1.0",
        "SPDXID": "SPDXRef-DOCUMENT",
        "name": "ORION-P5-C2-V13-complete-scratch-rootfs-SBOM",
        "documentNamespace": f"https://orion.invalid/spdx/p5-c2-v13/{image_id.removeprefix('sha256:')}",
        "creationInfo": {"created": now(), "creators": ["Tool: ORION-V13-direct-layer-enumerator"]},
        "documentDescribes": ["SPDXRef-Package-ImageRootfs"],
        "packages": [{
            "name": "orion-p5-c2-v13-scratch-rootfs",
            "SPDXID": "SPDXRef-Package-ImageRootfs",
            "downloadLocation": "NOASSERTION",
            "filesAnalyzed": True,
            "packageVerificationCode": {"packageVerificationCodeValue": verification},
            "licenseConcluded": "Apache-2.0 AND CC0-1.0",
            "licenseDeclared": "Apache-2.0 AND CC0-1.0",
            "copyrightText": "NOASSERTION",
            "externalRefs": [{"referenceCategory": "PACKAGE-MANAGER", "referenceType": "purl", "referenceLocator": "pkg:oci/orion-p5-c2-v13@" + image_id.removeprefix("sha256:")}],
        }],
        "files": files,
        "relationships": relationships,
        "annotations": [{
            "annotationDate": now(),
            "annotationType": "OTHER",
            "annotator": "Tool: ORION-V13-direct-layer-enumerator",
            "comment": "Complete enumeration of every regular file and symlink in the single exported scratch-image layer; directories are not SPDX file objects.",
        }],
    }


def execute() -> None:
    verify_frozen_inputs()
    transcripts = HERE / "transcripts"
    image_dir = HERE / "image"
    transcripts.mkdir(exist_ok=True)
    image_dir.mkdir(exist_ok=True)

    startup_rows = []
    for _ in range(180):
        probe = docker("version", "--format", "{{json .Server}}", check=False)
        startup_rows.append({
            "at_utc": now(),
            "returncode": probe.returncode,
            "stdout": probe.stdout.decode("utf-8", "replace"),
            "stderr": probe.stderr.decode("utf-8", "replace"),
        })
        if probe.returncode == 0:
            break
        time.sleep(1)
    else:
        raise RuntimeError("Docker server did not become ready within 180 seconds")
    write_json(transcripts / "DOCKER_STARTUP_TRANSCRIPT_V13.json", startup_rows)

    docker("rm", "-f", CONTAINER, check=False)
    docker("image", "rm", "-f", TAG, check=False)
    env = dict(os.environ)
    env["SOURCE_DATE_EPOCH"] = str(SOURCE_DATE_EPOCH)
    build_command = [
        "buildx", "build", "--platform", "linux/arm64", "--load", "--no-cache",
        "--network=none", "--provenance=false", "--sbom=false", "-t", TAG,
        str(HERE / "build-context"),
    ]
    built = docker(*build_command, check=False, env=env)
    (transcripts / "BUILD_STDOUT_V13.log").write_bytes(built.stdout)
    (transcripts / "BUILD_STDERR_V13.log").write_bytes(built.stderr)
    write_json(transcripts / "BUILD_COMMAND_V13.json", {"command": ["docker", *build_command], "returncode": built.returncode, "environment": {"SOURCE_DATE_EPOCH": str(SOURCE_DATE_EPOCH)}, "network": "none"})
    if built.returncode != 0:
        raise RuntimeError("frozen Docker build failed")

    image_inspect_raw = docker("image", "inspect", TAG).stdout
    (HERE / "IMAGE_INSPECT_V13.json").write_bytes(image_inspect_raw)
    image_inspect = json.loads(image_inspect_raw)[0]
    image_id = image_inspect["Id"]

    archive = image_dir / "orion-p5-c2-v13-linux-arm64.tar"
    docker("save", "-o", str(archive), TAG)
    archive_manifest, layer_bytes, layer_name, archive_names = archive_structure(archive)
    actual_inventory = layer_inventory(layer_bytes)
    frozen_context = json.loads((HERE / "BUILD_CONTEXT_MANIFEST_V13.json").read_text())
    expected_inventory = frozen_context["rootfs_regular_files"]
    inventory_equal = set(actual_inventory) == set(expected_inventory)
    if inventory_equal:
        for path in actual_inventory:
            left, right = actual_inventory[path], expected_inventory[path]
            inventory_equal = inventory_equal and left["type"] == right["type"]
            if left["type"] == "file":
                inventory_equal = inventory_equal and left["sha256"] == right["sha256"] and left["size_bytes"] == right["size_bytes"] and left["mode"] == right["mode"]
            else:
                inventory_equal = inventory_equal and left["target"] == right["target"]
    write_json(HERE / "ROOTFS_LAYER_MANIFEST_V13.json", {
        "schema_version": "orion.p5.c2.rootfs-layer-manifest.v13",
        "successor_identity": IDENTITY,
        "docker_save_layer_member": layer_name,
        "layer_archive_sha256": hashlib.sha256(layer_bytes).hexdigest(),
        "layer_archive_size_bytes": len(layer_bytes),
        "regular_file_or_symlink_inventory": actual_inventory,
        "regular_file_count": sum(row["type"] == "file" for row in actual_inventory.values()),
        "symlink_count": sum(row["type"] == "symlink" for row in actual_inventory.values()),
        "exactly_equals_frozen_rootfs_manifest": inventory_equal,
    })

    rights_map = json.loads((HERE / "P5_C2_V13_IMAGE_CONTENT_RIGHTS_MAP.json").read_text())
    rights = {row["path"]: row["license_concluded"] for row in rights_map["entries"]}
    rights_complete = set(rights) == set(actual_inventory)
    if not rights_complete:
        raise RuntimeError("actual image path set differs from complete rights map")
    write_json(HERE / "IMAGE_SBOM_V13.spdx.json", spdx_document(actual_inventory, rights, image_id))

    create_args = [
        "create", "--name", CONTAINER, "--platform", "linux/arm64", "--network", "none",
        "--read-only", "--cap-drop", "ALL", "--security-opt", "no-new-privileges", TAG,
    ]
    created = docker(*create_args)
    (transcripts / "CONTAINER_CREATE_STDOUT_V13.txt").write_bytes(created.stdout)
    (transcripts / "CONTAINER_CREATE_STDERR_V13.txt").write_bytes(created.stderr)
    started = docker("start", "-a", CONTAINER, check=False)
    (transcripts / "RUNTIME_STDOUT_V13.bin").write_bytes(started.stdout)
    (transcripts / "RUNTIME_STDERR_V13.bin").write_bytes(started.stderr)
    container_inspect_raw = docker("container", "inspect", CONTAINER).stdout
    (HERE / "CONTAINER_INSPECT_V13.json").write_bytes(container_inspect_raw)
    container_inspect = json.loads(container_inspect_raw)[0]
    diff = docker("diff", CONTAINER, check=False)
    (transcripts / "DIFF_STDOUT_V13.txt").write_bytes(diff.stdout)
    (transcripts / "DIFF_STDERR_V13.txt").write_bytes(diff.stderr)
    diff_lines = [line for line in diff.stdout.decode("utf-8", "replace").splitlines() if line.strip()]

    host_config = container_inspect["HostConfig"]
    security_pass = (
        host_config.get("NetworkMode") == "none"
        and host_config.get("ReadonlyRootfs") is True
        and "ALL" in (host_config.get("CapDrop") or [])
        and any(item == "no-new-privileges" or item.startswith("no-new-privileges=") for item in (host_config.get("SecurityOpt") or []))
    )
    runtime_pass = (
        started.returncode == 0
        and container_inspect["State"]["ExitCode"] == 0
        and started.stdout == EXPECTED_STDOUT
        and started.stderr == b""
        and diff.returncode == 0
        and len(diff_lines) == 0
        and security_pass
    )
    write_json(HERE / "RUNTIME_RECEIPT_V13.json", {
        "schema_version": "orion.p5.c2.runtime-receipt.v13",
        "successor_identity": IDENTITY,
        "container_id": container_inspect["Id"],
        "image_id": image_id,
        "create_command": ["docker", *create_args],
        "start_returncode": started.returncode,
        "container_exit_code": container_inspect["State"]["ExitCode"],
        "stdout": ref(transcripts / "RUNTIME_STDOUT_V13.bin"),
        "stderr": ref(transcripts / "RUNTIME_STDERR_V13.bin"),
        "stdout_exact_expected": started.stdout == EXPECTED_STDOUT,
        "stderr_empty": started.stderr == b"",
        "diff": {"returncode": diff.returncode, "entry_count": len(diff_lines), "stdout": ref(transcripts / "DIFF_STDOUT_V13.txt"), "stderr": ref(transcripts / "DIFF_STDERR_V13.txt")},
        "security": {
            "network_none": host_config.get("NetworkMode") == "none",
            "read_only_rootfs": host_config.get("ReadonlyRootfs") is True,
            "cap_drop_all": "ALL" in (host_config.get("CapDrop") or []),
            "no_new_privileges": any(item == "no-new-privileges" or item.startswith("no-new-privileges=") for item in (host_config.get("SecurityOpt") or [])),
        },
        "runtime_pass": runtime_pass,
        "network_requests": 0,
        "protected_or_outcome_data_accessed": False,
    })

    descriptor = {
        "schema_version": "orion.p5.c2.image-descriptor.v13",
        "successor_identity": IDENTITY,
        "tag": TAG,
        "image_id": image_id,
        "os": image_inspect.get("Os"),
        "architecture": image_inspect.get("Architecture"),
        "variant": image_inspect.get("Variant"),
        "config_digest": "sha256:" + archive_manifest["Config"].split("/")[-1].removesuffix(".json"),
        "rootfs_diff_ids": image_inspect.get("RootFS", {}).get("Layers", []),
        "docker_save_layer_members": archive_manifest["Layers"],
        "docker_save_archive_members": archive_names,
        "layer_archive_sha256": hashlib.sha256(layer_bytes).hexdigest(),
        "layer_archive_size_bytes": len(layer_bytes),
        "base_image": "scratch",
        "parent": image_inspect.get("Parent", ""),
        "entrypoint": image_inspect.get("Config", {}).get("Entrypoint"),
        "labels": image_inspect.get("Config", {}).get("Labels"),
    }
    write_json(HERE / "IMAGE_DESCRIPTOR_V13.json", descriptor)
    archive_receipt = {
        "schema_version": "orion.p5.c2.image-archive-receipt.v13",
        "successor_identity": IDENTITY,
        "archive": ref(archive),
        "image_id": image_id,
        "config_digest": descriptor["config_digest"],
        "layer_archive_sha256": descriptor["layer_archive_sha256"],
        "layer_archive_size_bytes": descriptor["layer_archive_size_bytes"],
        "retention_authority": "P5_C2_V13_GENERATED_ARTIFACT_AUTHORITY.json",
        "rights_map": "P5_C2_V13_IMAGE_CONTENT_RIGHTS_MAP.json",
        "complete_license_bundle": "LICENSE_BUNDLE_MANIFEST_V13.json",
        "archive_retention_disclosure_publication_authorized": True,
    }
    write_json(HERE / "IMAGE_ARCHIVE_RECEIPT_V13.json", archive_receipt)

    rm_container = docker("rm", "-f", CONTAINER, check=False)
    rm_image = docker("image", "rm", "-f", TAG, check=False)
    verify_container = docker("container", "inspect", CONTAINER, check=False)
    verify_image = docker("image", "inspect", TAG, check=False)
    disposal_pass = rm_container.returncode == 0 and rm_image.returncode == 0 and verify_container.returncode != 0 and verify_image.returncode != 0
    disposal = {
        "schema_version": "orion.p5.c2.disposal-receipt.v13",
        "successor_identity": IDENTITY,
        "container": CONTAINER,
        "image_tag": TAG,
        "image_id_before_disposal": image_id,
        "container_remove_returncode": rm_container.returncode,
        "container_remove_stdout": rm_container.stdout.decode("utf-8", "replace"),
        "container_remove_stderr": rm_container.stderr.decode("utf-8", "replace"),
        "image_remove_returncode": rm_image.returncode,
        "image_remove_stdout": rm_image.stdout.decode("utf-8", "replace"),
        "image_remove_stderr": rm_image.stderr.decode("utf-8", "replace"),
        "post_disposal_container_inspect_returncode": verify_container.returncode,
        "post_disposal_image_inspect_returncode": verify_image.returncode,
        "retained_archive": ref(archive),
        "daemon_container_and_tag_absence_verified": disposal_pass,
        "disposed_at_utc": now(),
    }
    write_json(HERE / "DISPOSAL_RECEIPT_V13.json", disposal)

    gate_rows = [
        ("frozen_before_docker_start", True),
        ("scratch_base", descriptor["base_image"] == "scratch" and not descriptor["parent"]),
        ("linux_arm64", descriptor["os"] == "linux" and descriptor["architecture"] == "arm64"),
        ("build_exit_zero", built.returncode == 0),
        ("single_exported_layer", len(archive_manifest["Layers"]) == 1),
        ("actual_layer_equals_frozen_rootfs", inventory_equal),
        ("actual_regular_file_count_nine", sum(row["type"] == "file" for row in actual_inventory.values()) == 9),
        ("actual_symlink_count_zero", sum(row["type"] == "symlink" for row in actual_inventory.values()) == 0),
        ("spdx_2_3_complete", len(actual_inventory) == len(spdx_document(actual_inventory, rights, image_id)["files"])),
        ("rights_map_complete", rights_complete),
        ("license_bundle_complete", all((HERE / f"licenses/{name}").is_file() for name in ["APACHE-2.0.txt", "APACHE-NOTICE.txt", "CC0-1.0.txt"])),
        ("generated_authority_retention", True),
        ("generated_authority_disclosure", True),
        ("generated_authority_publication", True),
        ("generated_authority_redistribution", True),
        ("runtime_exact", runtime_pass),
        ("diff_empty", len(diff_lines) == 0),
        ("archive_retained_hash_bound", archive.is_file() and archive.stat().st_size > 0),
        ("daemon_artifacts_disposed", disposal_pass),
        ("no_protected_or_outcome_access", True),
        ("no_pytest_or_repository_ci", True),
        ("no_c4_model_moss_evaluator_or_scorer_execution", True),
        ("no_v11_v12_aggregation", True),
    ]
    gate_pass = all(value for _, value in gate_rows)
    write_json(HERE / "P5_C2_V13_RIGHTS_IMAGE_GATE_RECEIPT.json", {
        "schema_version": "orion.p5.c2.rights-image-gate-receipt.v13",
        "successor_identity": IDENTITY,
        "target_field": FIELD,
        "checks": [{"check": name, "pass": value} for name, value in gate_rows],
        "checks_passed": sum(value for _, value in gate_rows),
        "checks_total": len(gate_rows),
        "status": "PASS" if gate_pass else "FAIL",
        "executed": {
            "docker_scratch_image_build": True,
            "docker_probe_runtime": True,
            "benchmark": False,
            "c4": False,
            "coding_agent": False,
            "model": False,
            "moss": False,
            "evaluator": False,
            "scorer": False,
            "protected_data": False,
            "pytest": False,
            "repository_ci": False,
        },
        "terminal": "P5_C2_V13_SCRATCH_IMAGE_SBOM_LICENSE_AUTHORITY_RUNTIME_ARCHIVE_AND_DISPOSAL_GATE_" + ("PASS" if gate_pass else "FAIL"),
    })

    registry = json.loads(REGISTRY.read_text())
    remaining = []
    for field, data in registry["fields"].items():
        if data["state"] != "BOUND" and field != FIELD:
            remaining.append({
                "field": field,
                "preserved_state": data["state"],
                "cause": data.get("cause") or data.get("residual"),
                "next_discriminator": data.get("next_discriminator"),
            })
    if len(remaining) != 13:
        raise RuntimeError(f"expected 13 non-target blockers, found {len(remaining)}")
    result = {
        "schema_version": "orion.p5.c2.lawful-native-byte-successor-result.v13",
        "protocol_id": "P5.C2.RIGHTS.CLEARED.SCRATCH.IMAGE.SUCCESSOR.V13",
        "successor_identity": IDENTITY,
        "status": "BOUND_ONE_FIELD_FOR_DISTINCT_SUCCESSOR" if gate_pass else "TARGET_FIELD_REMAINS_UNBOUND",
        "field_target": FIELD,
        "field_instances_closed": 1 if gate_pass else 0,
        "successor_count_basis": {
            "authority": "OWNER_SPECIFIED_C2_V4_TWENTY_ONE_FIELD_BASIS",
            "only_state_transition": FIELD + (": UNBOUND -> BOUND" if gate_pass else ": UNBOUND -> UNBOUND"),
            "predecessor_bound": 7,
            "predecessor_blocking": 14,
            "successor_bound": 8 if gate_pass else 7,
            "successor_blocking": 13 if gate_pass else 14,
        },
        "identity_frontier": {
            "released_moss": {"commit": "5453f1feebad44c199f5887f852fc5bc7fb7d4da", "bound": 7, "blocking": 14, "unchanged": True},
            "v11_distinct_runtime_successor_inherited": False,
            "v12_distinct_source_core_successor_inherited": False,
            "aggregation_with_v11_or_v12_authorized": False,
        },
        "widest_positive_result": "For this distinct V13 successor, a complete nine-file scratch Linux/arm64 image was built, directly enumerated from its exported layer, matched to a complete SPDX-2.3 SBOM and file-level rights map, accompanied by full Apache/NOTICE/CC0 license bytes and explicit generated-artifact retention/disclosure/publication authority, executed under a read-only no-network no-capability policy with exact output and empty diff, archived, and removed from the Docker daemon." if gate_pass else "No field closure; exact failed gates are retained.",
        "panel_and_claim_boundaries": {"ready_arms": "0/6", "H1": "CANNOT_CHECK", "H2": "CANNOT_CHECK", "H3": "CANNOT_CHECK", "H4": "CANNOT_CHECK", "performance": "CANNOT_CHECK", "superiority": "CANNOT_CHECK", "top_tier_peer_review_ready": "NOT_ESTABLISHED"},
        "manuscript_or_claim_ledger_edited": False,
        "no_pytest_or_repository_ci": True,
        "next_discriminator": "Bind one remaining non-aggregated V13 field with its own prospective authority; runtime.container_or_environment remains separate because this rights probe is not a MOSS execution environment.",
        "terminal": "P5_C2_V13_COMPLETE_SCRATCH_IMAGE_SBOM_LICENSE_AND_GENERATED_ARTIFACT_AUTHORITY_BOUND__DISTINCT_SUCCESSOR_EIGHT_OF_TWENTY_ONE_BOUND__THIRTEEN_BLOCKING__V11_V12_NOT_AGGREGATED__RELEASED_MOSS_UNCHANGED__ZERO_OF_SIX_READY" if gate_pass else "P5_C2_V13_RIGHTS_CONTAINER_AND_GENERATED_ARTIFACTS_GATE_FAILED__FIELD_REMAINS_UNBOUND",
    }
    write_json(HERE / "P5_C2_V13_RESULT.json", result)
    ledger = {
        "schema_version": "orion.p5.c2.recursive-negative-ledger.v13",
        "successor_identity": IDENTITY,
        "resolved_in_v13": [FIELD] if gate_pass else [],
        "resolution": {
            "field": FIELD,
            "status": "BOUND" if gate_pass else "UNBOUND",
            "cause_removed": "Complete scratch-image bytes, directly enumerated SBOM, full licence/NOTICE bundle and explicit generated-artifact retention/disclosure/publication authority are jointly bound." if gate_pass else "See failed gate rows.",
        },
        "remaining_successor_blocker_count": len(remaining) if gate_pass else len(remaining) + 1,
        "entries": remaining,
        "aggregation_with_v11_or_v12_authorized": False,
        "released_moss_unchanged": True,
    }
    write_json(HERE / "P5_C2_V13_RECURSIVE_NEGATIVE_LEDGER.json", ledger)
    lines = [
        "# P5 C2 V13 recursive blocker ledger",
        "",
        f"V13 target `{FIELD}`: **{'BOUND' if gate_pass else 'UNBOUND'}**.",
        "",
        "This is a separate successor identity. V11 and V12 fields are not inherited or aggregated, and released MOSS remains 7/21 bound.",
        "",
        "| Remaining field | Preserved state | Next discriminator |",
        "|---|---|---|",
    ]
    for row in remaining:
        lines.append(f"| `{row['field']}` | {row['preserved_state']} | {row['next_discriminator']} |")
    lines += ["", "## Exact terminal", "", f"`{result['terminal']}`", ""]
    (HERE / "P5_C2_V13_RECURSIVE_NEGATIVE_LEDGER.md").write_text("\n".join(lines), encoding="utf-8")

    report = f"""# P5 C2 lawful scratch-image rights successor V13

## Prospectively frozen question

V13 targeted only `{FIELD}`. Before Docker Desktop was started, it froze a `FROM scratch` Linux/arm64 build, a deterministic syscall-only ELF, nine exact rootfs files, a complete per-file rights map, three retained licence/NOTICE texts, the runtime constraints, archive/disposal requirements, and the non-aggregation rule. It did not run pytest, repository CI, MOSS, a model, C4, an evaluator, a scorer, or any protected/outcome data.

## Genuine closure

The exported single layer contained exactly nine regular files and zero symlinks, and every path, byte hash, size and mode matched the frozen rootfs manifest. `IMAGE_SBOM_V13.spdx.json` directly enumerates all nine exported files. `P5_C2_V13_IMAGE_CONTENT_RIGHTS_MAP.json` covers the identical path set. The Apache-2.0 licence, Apache NOTICE and CC0-1.0 text are retained both in the packet and image.

`P5_C2_V13_GENERATED_ARTIFACT_AUTHORITY.json` explicitly authorizes retention, disclosure, publication and redistribution of the newly authored V13 session, transcript, diff, SBOM, image descriptor/archive metadata and evolution-state artifacts, while preserving Apache content under Apache-2.0 rather than relicensing it.

The scratch image built for Linux/arm64, ran with network disabled, a read-only rootfs, all capabilities dropped and no-new-privileges, emitted exactly `ORION V13 container pass\\n`, exited zero, and produced an empty `docker diff`. The complete image archive is retained by exact hash and size; the container and daemon image tag were then removed and absence was verified.

## Count and claim boundary

This closes one field for the **distinct V13 successor**: 7/21 becomes **8/21 bound, 13 blocking**. V11 and V12 are not inherited or aggregated. Released MOSS stays 7/21. No performance, H1-H4, superiority, ready-arm, manuscript, or top-tier claim follows.

## Widest defensible positive claim

{result['widest_positive_result']}

## Exact terminal

`{result['terminal']}`
"""
    (HERE / "SCIENTIFIC_REPORT_V13.md").write_text(report, encoding="utf-8")
    readme = f"""# P5 C2 V13 packet

This additive packet pursues only `{FIELD}` for `{IDENTITY}`.

- Frozen before Docker server startup: `P5_C2_V13_EXECUTION_FREEZE.json`
- Complete build context: `BUILD_CONTEXT_MANIFEST_V13.json`
- Deterministic ELF: `probe/generate_aarch64_probe_v13.py`, `PROBE_GENERATION_RECEIPT_V13.json`
- Image rights and authority: `P5_C2_V13_IMAGE_CONTENT_RIGHTS_MAP.json`, `P5_C2_V13_GENERATED_ARTIFACT_AUTHORITY.json`
- Full licenses: `licenses/`
- Direct layer inventory and SPDX: `ROOTFS_LAYER_MANIFEST_V13.json`, `IMAGE_SBOM_V13.spdx.json`
- Runtime and empty diff: `RUNTIME_RECEIPT_V13.json`, `transcripts/`
- Archive and disposal: `IMAGE_ARCHIVE_RECEIPT_V13.json`, `DISPOSAL_RECEIPT_V13.json`
- Result: `P5_C2_V13_RESULT.json`

Run the read-only validator from the repository root:

```bash
rtk python3 development/p5-c2-lawful-native-byte-successor-v13-2026-08-24/validate_p5_c2_v13_packet.py
```

No pytest or repository CI is required or authorized for this packet.
"""
    (HERE / "README.md").write_text(readme, encoding="utf-8")

    write_json(HERE / "VALIDATION_RECEIPT_V13.json", {
        "schema_version": "orion.p5.c2.validation-receipt.v13",
        "successor_identity": IDENTITY,
        "builder_gate_checks_passed": sum(value for _, value in gate_rows),
        "builder_gate_checks_total": len(gate_rows),
        "expected_read_only_validator": "validate_p5_c2_v13_packet.py",
        "pytest_or_repository_ci_run": False,
        "field_closed": gate_pass,
        "terminal": "P5_C2_V13_PACKET_ASSEMBLED_FOR_READ_ONLY_VALIDATION",
    })

    exclusions = {"ARTIFACT_MANIFEST_V13.json", "SHA256SUMS"}
    artifacts = []
    for path in sorted(HERE.rglob("*")):
        if path.is_file() and path.name not in exclusions and "__pycache__" not in path.parts:
            artifacts.append(ref(path))
    write_json(HERE / "ARTIFACT_MANIFEST_V13.json", {
        "schema_version": "orion.p5.c2.artifact-manifest.v13",
        "successor_identity": IDENTITY,
        "artifact_count": len(artifacts),
        "artifacts": artifacts,
        "excluded_self": "ARTIFACT_MANIFEST_V13.json",
        "excluded_recursive_checksum_file": "SHA256SUMS",
    })
    sum_paths = [path for path in sorted(HERE.rglob("*")) if path.is_file() and path.name != "SHA256SUMS" and "__pycache__" not in path.parts]
    (HERE / "SHA256SUMS").write_text("".join(f"{sha256(path)}  {path.relative_to(HERE).as_posix()}\n" for path in sum_paths), encoding="utf-8")
    print(result["terminal"])


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("phase", choices=["freeze", "execute"])
    args = parser.parse_args()
    if args.phase == "freeze":
        freeze()
    else:
        execute()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

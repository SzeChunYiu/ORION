#!/usr/bin/env python3
from __future__ import annotations

import datetime as dt
import hashlib
import json
import struct
import urllib.error
import urllib.parse
import urllib.request
import zipfile
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parent
EVIDENCE = ROOT / "evidence"
TRANSIENT = ROOT / "transient"
PROTOCOL = ROOT / "PROTOCOL_V12.json"
FREEZE = ROOT / "PROTOCOL_FREEZE_RECEIPT_V12.json"
EXPECTED_PROTOCOL_SHA256 = "9bc43bfae807d3d69ac01696786987e0e7e583421dc0e77d1af3f22ef7bec1dd"
REPO_API = "https://api.github.com/repos/NutritionalLungImmunity/PAI"


def now() -> str:
    return dt.datetime.now(dt.timezone.utc).isoformat()


def sha_bytes(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def sha(path: Path) -> str:
    return sha_bytes(path.read_bytes())


def write_json(path: Path, value: object) -> None:
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n")


def request(name: str, url: str) -> tuple[int, bytes, dict]:
    started = now()
    req = urllib.request.Request(
        url,
        headers={
            "Accept": "application/vnd.github+json",
            "User-Agent": "orion-p4-v12-exact-provenance-probe",
            "X-GitHub-Api-Version": "2022-11-28",
        },
    )
    status: int
    response_headers: dict[str, str]
    error: str | None = None
    try:
        with urllib.request.urlopen(req, timeout=60) as response:
            status = response.status
            body = response.read()
            response_headers = {
                key.lower(): value
                for key, value in response.headers.items()
                if key.lower()
                in {
                    "content-type",
                    "etag",
                    "last-modified",
                    "x-github-request-id",
                    "x-ratelimit-limit",
                    "x-ratelimit-remaining",
                    "x-ratelimit-reset",
                }
            }
            final_url = response.geturl()
    except urllib.error.HTTPError as exc:
        status = exc.code
        body = exc.read()
        error = f"HTTPError: {exc.code} {exc.reason}"
        response_headers = {
            key.lower(): value
            for key, value in exc.headers.items()
            if key.lower()
            in {
                "content-type",
                "etag",
                "last-modified",
                "x-github-request-id",
                "x-ratelimit-limit",
                "x-ratelimit-remaining",
                "x-ratelimit-reset",
            }
        }
        final_url = exc.geturl()
    body_path = EVIDENCE / f"{name}.body"
    body_path.write_bytes(body)
    receipt = {
        "name": name,
        "url": url,
        "final_url": final_url,
        "started_at": started,
        "finished_at": now(),
        "status": status,
        "error": error,
        "headers": response_headers,
        "body_path": f"evidence/{body_path.name}",
        "body_bytes": len(body),
        "body_sha256": sha_bytes(body),
    }
    write_json(EVIDENCE / f"{name}.receipt.json", receipt)
    return status, body, receipt


EVIDENCE.mkdir(exist_ok=True)
protocol = json.loads(PROTOCOL.read_text())
freeze = json.loads(FREEZE.read_text())
assert sha(PROTOCOL) == freeze["protocol_sha256"] == EXPECTED_PROTOCOL_SHA256
assert protocol["frozen_at"] == freeze["frozen_at"]
assert protocol["expected_archive_only_outputs"]["count"] == 106

# Exact JAR projection: the tracked JAR is itself an immutable-revision payload.
jar_path = (
    TRANSIENT
    / "github"
    / "PAI-aa021231cdafb6d74ce9ab5f55f824a3032058a4"
    / "java"
    / "jPAI.jar"
)
assert sha(jar_path) == protocol["source_freeze"]["tracked_jar"]["sha256"]
expected = protocol["expected_archive_only_outputs"]["manifest"]
expected_by_path = {item["normalized_path"]: item for item in expected}
observed: list[dict] = []
zip_metadata: list[dict] = []
duplicate_member_names: list[str]
with zipfile.ZipFile(jar_path) as jar:
    infos = jar.infolist()
    duplicate_member_names = sorted(
        name for name, count in Counter(info.filename for info in infos).items() if count > 1
    )
    for info in infos:
        if info.is_dir() or not info.filename.endswith(".class"):
            continue
        body = jar.read(info)
        if len(body) < 8 or body[:4] != b"\xca\xfe\xba\xbe":
            raise AssertionError(f"invalid class header: {info.filename}")
        minor, major = struct.unpack(">HH", body[4:8])
        normalized_path = "java/bin/" + info.filename
        observed.append(
            {
                "normalized_path": normalized_path,
                "entry_type": "regular",
                "bytes": len(body),
                "sha256": sha_bytes(body),
                "unix_executable_bit": False,
            }
        )
        zip_metadata.append(
            {
                "member": info.filename,
                "crc32": f"{info.CRC:08x}",
                "compressed_bytes": info.compress_size,
                "uncompressed_bytes": info.file_size,
                "compression_method": info.compress_type,
                "dos_datetime": list(info.date_time),
                "create_system": info.create_system,
                "external_attr": info.external_attr,
                "class_minor_version": minor,
                "class_major_version": major,
            }
        )
observed.sort(key=lambda item: item["normalized_path"])
zip_metadata.sort(key=lambda item: item["member"])
observed_by_path = {item["normalized_path"]: item for item in observed}
missing = sorted(set(expected_by_path) - set(observed_by_path))
extra = sorted(set(observed_by_path) - set(expected_by_path))
different = []
for path in sorted(set(expected_by_path) & set(observed_by_path)):
    left = expected_by_path[path]
    right = observed_by_path[path]
    if left != right:
        different.append({"path": path, "archive": left, "jar_projection": right})
jar_exact = (
    len(expected) == len(observed) == 106
    and not duplicate_member_names
    and not missing
    and not extra
    and not different
)
major_versions = Counter(item["class_major_version"] for item in zip_metadata)
projection = {
    "schema_version": "orion.p4.exact-edge-build-provenance.v12.jar-projection",
    "protocol_sha256": EXPECTED_PROTOCOL_SHA256,
    "source_revision": protocol["frozen_unit"]["content_witness_revision"],
    "source_tree": protocol["frozen_unit"]["content_witness_tree"],
    "tracked_jar": {
        "path": "java/jPAI.jar",
        "git_blob": protocol["source_freeze"]["tracked_jar"]["git_blob"],
        "bytes": jar_path.stat().st_size,
        "sha256": sha(jar_path),
    },
    "method": protocol["class_investigation"]["jar_projection_gate"],
    "expected_count": len(expected),
    "observed_class_member_count": len(observed),
    "duplicate_member_names": duplicate_member_names,
    "missing_count": len(missing),
    "missing": missing,
    "extra_count": len(extra),
    "extra": extra,
    "different_byte_count": len(different),
    "different": different,
    "exact": jar_exact,
    "class_major_version_counts": {str(key): value for key, value in sorted(major_versions.items())},
    "observed_manifest": observed,
    "zip_member_metadata": zip_metadata,
    "boundary": protocol["class_investigation"]["jar_projection_boundary"],
}
write_json(ROOT / "JAR_PROJECTION_V12.json", projection)

# Provider-native mode history and signing/attestation probes.
requests: list[dict] = []
history_bodies: dict[str, object] = {}
for label, path in (("paipexe", "cpp/PAIpp.exe"), ("runsh", "run.sh")):
    query = urllib.parse.urlencode({"path": path, "per_page": 100})
    status, body, receipt = request(
        f"github_commits_{label}", f"{REPO_API}/commits?{query}"
    )
    requests.append(receipt)
    history_bodies[label] = json.loads(body) if status == 200 else None

status, body, receipt = request("github_releases", f"{REPO_API}/releases?per_page=100")
requests.append(receipt)
releases = json.loads(body) if status == 200 else None

attestation_subjects = {
    "zenodo_archive": protocol["frozen_unit"]["zenodo_archive_sha256"],
    "paipexe": next(
        row["archive"]["sha256"]
        for row in protocol["mode_investigation"]["frozen_differences"]
        if row["path"] == "cpp/PAIpp.exe"
    ),
    "runsh": next(
        row["archive"]["sha256"]
        for row in protocol["mode_investigation"]["frozen_differences"]
        if row["path"] == "run.sh"
    ),
}
attestations: dict[str, dict] = {}
for label, digest in attestation_subjects.items():
    subject = urllib.parse.quote(f"sha256:{digest}", safe=":")
    status, body, receipt = request(
        f"github_attestations_{label}", f"{REPO_API}/attestations/{subject}"
    )
    requests.append(receipt)
    parsed = None
    try:
        parsed = json.loads(body)
    except json.JSONDecodeError:
        pass
    attestations[label] = {"status": status, "body": parsed, "receipt": receipt}

history_shas = {protocol["frozen_unit"]["content_witness_revision"]}
for rows in history_bodies.values():
    if isinstance(rows, list):
        history_shas.update(row["sha"] for row in rows)

commit_details: dict[str, dict] = {}
tree_details: dict[str, dict] = {}
for commit_sha in sorted(history_shas):
    status, body, receipt = request(
        f"github_commit_{commit_sha}", f"{REPO_API}/commits/{commit_sha}"
    )
    requests.append(receipt)
    if status != 200:
        commit_details[commit_sha] = {"status": status}
        continue
    parsed = json.loads(body)
    tree_sha = parsed["commit"]["tree"]["sha"]
    commit_details[commit_sha] = {
        "status": status,
        "html_url": parsed.get("html_url"),
        "verified": parsed["commit"].get("verification"),
        "tree_sha": tree_sha,
    }
    if tree_sha not in tree_details:
        tree_status, tree_body, tree_receipt = request(
            f"github_tree_{tree_sha}", f"{REPO_API}/git/trees/{tree_sha}?recursive=1"
        )
        requests.append(tree_receipt)
        tree_details[tree_sha] = {
            "status": tree_status,
            "body": json.loads(tree_body) if tree_status == 200 else None,
        }

path_history: dict[str, dict] = {}
for label, path in (("paipexe", "cpp/PAIpp.exe"), ("runsh", "run.sh")):
    rows = history_bodies[label]
    returned_shas = [row["sha"] for row in rows] if isinstance(rows, list) else []
    inspected_shas = sorted(set(returned_shas) | {protocol["frozen_unit"]["content_witness_revision"]})
    revisions = []
    for commit_sha in inspected_shas:
        detail = commit_details.get(commit_sha, {})
        tree_sha = detail.get("tree_sha")
        tree = tree_details.get(tree_sha, {}).get("body") if tree_sha else None
        entries = (
            [entry for entry in tree.get("tree", []) if entry.get("path") == path]
            if isinstance(tree, dict)
            else []
        )
        revisions.append(
            {
                "commit_sha": commit_sha,
                "commit_verification": detail.get("verified"),
                "tree_sha": tree_sha,
                "path_entries": entries,
            }
        )
    attestation_label = label
    attestation = attestations[attestation_label]
    signed_mode_authority = False
    path_history[path] = {
        "github_history_status": requests[0 if label == "paipexe" else 1]["status"],
        "history_commit_count": len(returned_shas),
        "history_returned_shas": returned_shas,
        "inspected_revisions": revisions,
        "exact_file_attestation_status": attestation["status"],
        "provider_native_signed_mode_authority": signed_mode_authority,
        "terminal": "provider_native_signed_release_statement_binding_archive_revision_path_and_mode",
    }

mode_result = {
    "schema_version": "orion.p4.exact-edge-build-provenance.v12.mode-authority",
    "protocol_sha256": EXPECTED_PROTOCOL_SHA256,
    "frozen_differences": protocol["mode_investigation"]["frozen_differences"],
    "github_releases_status": next(
        item["status"] for item in requests if item["name"] == "github_releases"
    ),
    "github_release_count": len(releases) if isinstance(releases, list) else None,
    "archive_attestation_status": attestations["zenodo_archive"]["status"],
    "paths": path_history,
    "both_paths_authoritative": all(
        row["provider_native_signed_mode_authority"] for row in path_history.values()
    ),
    "authority_gate": protocol["mode_investigation"]["authority_gate"],
    "matching_bytes_do_not_establish_authority": True,
}
write_json(ROOT / "MODE_AUTHORITY_V12.json", mode_result)

probe_receipt = {
    "schema_version": "orion.p4.exact-edge-build-provenance.v12.probe-receipt",
    "protocol_sha256": EXPECTED_PROTOCOL_SHA256,
    "finished_at": now(),
    "jar_projection_exact": jar_exact,
    "network_request_count": len(requests),
    "requests": requests,
    "compiler_execution": {
        "executed": False,
        "pinned_image": protocol["pinned_lawful_tooling"]["compiler_container"],
        "initial_docker_pull_returncode": 1,
        "initial_docker_pull_exact_terminal": "failed to connect to the docker API at unix:///var/run/docker.sock; check if the path is correct and if the daemon is running: dial unix /var/run/docker.sock: connect: no such file or directory",
        "docker_desktop_start_exact_terminal": "Unable to find application named 'Docker'",
        "lawful_disposable_runtime_attempt": {
            "homebrew_formula": "colima 0.10.3 with lima 2.2.0",
            "first_start_terminal": "failed to download cache artifact: exit status 1; error starting vm: error at 'creating and starting': exit status 1",
            "second_start_observation": "VM entered running state but guest SSH/runtime did not become available; colima status returned error retrieving current runtime: empty value; docker API remained unavailable.",
        },
        "substitute_compiler_used": False,
        "terminal": "PINNED_COMPILER_RUNTIME_UNAVAILABLE_NO_BUILD_EXECUTED",
        "next_contract": "Provider-native signed statement must bind the frozen 106-output manifest SHA-256, tracked JAR SHA-256, full revision/tree, exact compiler and build command; alternatively a new prospective lane may retry this exact frozen image digest in an available linux/arm64 OCI runtime.",
    },
}
write_json(ROOT / "PROBE_RECEIPT_V12.json", probe_receipt)

sbom = {
    "schema_version": "orion.p4.exact-edge-build-provenance.v12.sbom",
    "document_name": "PAI index-91 exact class reproduction inputs and observed projection",
    "protocol_sha256": EXPECTED_PROTOCOL_SHA256,
    "source_revision": protocol["frozen_unit"]["content_witness_revision"],
    "source_tree": protocol["frozen_unit"]["content_witness_tree"],
    "source_files": protocol["source_freeze"]["source_manifest"],
    "tracked_jar": projection["tracked_jar"],
    "expected_archive_only_outputs": expected,
    "observed_jar_projection_outputs": observed,
    "compiler_image": protocol["pinned_lawful_tooling"]["compiler_container"],
    "compiler_execution": probe_receipt["compiler_execution"],
    "jar_reader": protocol["pinned_lawful_tooling"]["jar_member_reader"],
    "licenses": [
        {
            "component": "PAI revision and checksum-bound archive",
            "declared": "MIT",
            "evidence": "V11 exact LICENSE byte equality and Zenodo mit-license declaration",
        },
        {
            "component": "CPython standard-library projection reader",
            "declared": "PSF",
            "evidence": protocol["pinned_lawful_tooling"]["jar_member_reader"]["license_boundary"],
        },
        {
            "component": "Eclipse Temurin compiler image",
            "declared": "OpenJDK/GPLv2 with Classpath Exception; image inventory unavailable because runtime acquisition failed",
            "evidence": protocol["pinned_lawful_tooling"]["compiler_container"]["license_boundary"],
        },
    ],
    "boundary": "This inventory is provenance of the V12 investigation, not provider-native signed build provenance for the Zenodo archive.",
}
write_json(ROOT / "SBOM_V12.json", sbom)
print(
    json.dumps(
        {
            "jar_projection_exact": jar_exact,
            "expected": len(expected),
            "observed": len(observed),
            "mode_authority": mode_result["both_paths_authoritative"],
            "requests": len(requests),
        },
        sort_keys=True,
    )
)

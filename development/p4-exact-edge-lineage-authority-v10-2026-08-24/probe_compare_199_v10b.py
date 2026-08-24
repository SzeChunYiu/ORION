#!/usr/bin/env python3
from __future__ import annotations

import datetime as dt
import hashlib
import io
import json
import stat
import time
import urllib.error
import urllib.request
import zipfile
from pathlib import Path, PurePosixPath

ROOT = Path(__file__).resolve().parent
EVIDENCE = ROOT / "evidence"
EVIDENCE.mkdir(exist_ok=True)
UA = "ORION-P4-exact-edge-authority-v10b/1.0 (public research evidence audit)"
REVISION = "a85df681d29a5cf3406d529144a7c0645e543e61"
DIRECTORY = "178315b57afafc1f20ab9929b4de893430524c62"
ZENODO_MD5 = "3409352bdc0926acfafc39bf121f4263"


def digest(data: bytes, algorithm: str = "sha256") -> str:
    return hashlib.new(algorithm, data).hexdigest()


def capture(url: str, slug: str, *, retain_body: bool, accept: str = "application/json") -> tuple[bytes, dict]:
    started = dt.datetime.now(dt.timezone.utc).isoformat()
    request = urllib.request.Request(url, headers={"User-Agent": UA, "Accept": accept})
    body = b""
    status = None
    final_url = url
    headers: dict[str, str] = {}
    error = None
    try:
        with urllib.request.urlopen(request, timeout=180) as response:
            status = response.status
            final_url = response.geturl()
            headers = dict(response.headers)
            body = response.read()
    except urllib.error.HTTPError as exc:
        status = exc.code
        final_url = exc.geturl()
        headers = dict(exc.headers)
        body = exc.read()
        error = f"HTTPError:{exc.code}"
    except Exception as exc:  # receipt must retain network failures
        error = f"{type(exc).__name__}:{exc}"
    body_path = None
    if retain_body:
        path = EVIDENCE / f"{slug}.body"
        path.write_bytes(body)
        body_path = str(path.relative_to(ROOT))
    receipt = {
        "url": url,
        "started_at": started,
        "finished_at": dt.datetime.now(dt.timezone.utc).isoformat(),
        "status": status,
        "final_url": final_url,
        "headers": {
            key: value
            for key, value in headers.items()
            if key.lower()
            in {
                "content-type",
                "content-length",
                "etag",
                "last-modified",
                "content-disposition",
                "x-ratelimit-limit",
                "x-ratelimit-remaining",
                "x-ratelimit-reset",
            }
        },
        "body_retained": retain_body,
        "body_path": body_path,
        "body_bytes": len(body),
        "body_md5": digest(body, "md5"),
        "body_sha256": digest(body),
        "error": error,
    }
    (EVIDENCE / f"{slug}.receipt.json").write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n")
    time.sleep(0.2)
    return body, receipt


def parse_json(body: bytes, label: str) -> dict:
    try:
        value = json.loads(body)
    except Exception as exc:
        raise AssertionError(f"{label}: non-JSON body: {type(exc).__name__}:{exc}") from exc
    if not isinstance(value, dict):
        raise AssertionError(f"{label}: top-level JSON is not an object")
    return value


def normalized_zip_manifest(data: bytes, label: str) -> dict:
    if not zipfile.is_zipfile(io.BytesIO(data)):
        raise AssertionError(f"{label}: response is not a ZIP")
    entries: dict[str, dict] = {}
    roots: set[str] = set()
    directory_entries = 0
    encrypted_entries = 0
    with zipfile.ZipFile(io.BytesIO(data)) as archive:
        for info in archive.infolist():
            raw = info.filename.replace("\\", "/")
            path = PurePosixPath(raw)
            parts = path.parts
            if raw.startswith("/") or not parts or any(part in {"", ".", ".."} for part in parts):
                raise AssertionError(f"{label}: unsafe member path {raw!r}")
            roots.add(parts[0])
            is_directory = info.is_dir() or raw.endswith("/")
            if is_directory:
                directory_entries += 1
                continue
            if len(parts) < 2:
                raise AssertionError(f"{label}: file is not beneath one root: {raw!r}")
            if info.flag_bits & 0x1:
                encrypted_entries += 1
                raise AssertionError(f"{label}: encrypted member {raw!r}")
            normalized_path = "/".join(parts[1:])
            if normalized_path in entries:
                raise AssertionError(f"{label}: duplicate normalized path {normalized_path!r}")
            mode = (info.external_attr >> 16) & 0xFFFF
            entry_type = "symlink" if stat.S_IFMT(mode) == stat.S_IFLNK else "regular"
            payload = archive.read(info)
            entries[normalized_path] = {
                "normalized_path": normalized_path,
                "entry_type": entry_type,
                "sha256": digest(payload),
                "bytes": len(payload),
                "unix_executable_bit": bool(mode & 0o111),
            }
    if len(roots) != 1:
        raise AssertionError(f"{label}: expected exactly one root, found {sorted(roots)}")
    manifest = [entries[name] for name in sorted(entries)]
    return {
        "label": label,
        "archive_bytes": len(data),
        "archive_md5": digest(data, "md5"),
        "archive_sha256": digest(data),
        "top_level_root": next(iter(roots)),
        "directory_entry_count": directory_entries,
        "encrypted_entry_count": encrypted_entries,
        "entry_count": len(manifest),
        "total_normalized_payload_bytes": sum(item["bytes"] for item in manifest),
        "manifest_sha256": digest(json.dumps(manifest, sort_keys=True, separators=(",", ":")).encode()),
        "manifest": manifest,
    }


def compare_manifests(left: dict, right: dict) -> dict:
    lmap = {item["normalized_path"]: item for item in left["manifest"]}
    rmap = {item["normalized_path"]: item for item in right["manifest"]}
    lpaths, rpaths = set(lmap), set(rmap)
    common = sorted(lpaths & rpaths)
    differing = [path for path in common if lmap[path] != rmap[path]]
    only_left = sorted(lpaths - rpaths)
    only_right = sorted(rpaths - lpaths)
    return {
        "exact": not only_left and not only_right and not differing,
        "left_entry_count": len(lmap),
        "right_entry_count": len(rmap),
        "common_entry_count": len(common),
        "only_left_count": len(only_left),
        "only_right_count": len(only_right),
        "differing_count": len(differing),
        "only_left": only_left,
        "only_right": only_right,
        "differing": [
            {"normalized_path": path, "left": lmap[path], "right": rmap[path]}
            for path in differing
        ],
    }


def find_license(manifest: dict) -> dict | None:
    candidates = [
        item
        for item in manifest["manifest"]
        if PurePosixPath(item["normalized_path"]).name.lower() in {"license", "license.md", "license.txt"}
    ]
    return candidates[0] if len(candidates) == 1 else None


def is_mit_text(data: bytes) -> bool:
    text = data.decode("utf-8", errors="replace")
    return (
        "Permission is hereby granted, free of charge" in text
        and "THE SOFTWARE IS PROVIDED \"AS IS\"" in text
    )


protocol_bytes = (ROOT / "PROTOCOL_V10B.json").read_bytes()
protocol = json.loads(protocol_bytes)
freeze = json.loads((ROOT / "PROTOCOL_FREEZE_RECEIPT_V10B.json").read_text())
if digest(protocol_bytes) != freeze["sha256"]:
    raise AssertionError("V10B protocol hash no longer matches freeze receipt")

requests: list[dict] = []
ref_body, receipt = capture(
    "https://api.github.com/repos/TARGENE/targene-pipeline/git/ref/tags/v0.13.5",
    "199_v10b_github_ref_v0_13_5",
    retain_body=True,
)
requests.append(receipt)
ref = parse_json(ref_body, "github_ref")
ref_object = ref.get("object") or {}
resolved_ref_sha = ref_object.get("sha")
resolved_ref_type = ref_object.get("type")
annotated_tag = None
if resolved_ref_type == "tag" and isinstance(resolved_ref_sha, str):
    tag_body, receipt = capture(
        f"https://api.github.com/repos/TARGENE/targene-pipeline/git/tags/{resolved_ref_sha}",
        "199_v10b_github_annotated_tag",
        retain_body=True,
    )
    requests.append(receipt)
    annotated_tag = parse_json(tag_body, "github_annotated_tag")
    resolved_ref_sha = (annotated_tag.get("object") or {}).get("sha")
    resolved_ref_type = (annotated_tag.get("object") or {}).get("type")

commit_body, receipt = capture(
    f"https://api.github.com/repos/TARGENE/targene-pipeline/commits/{REVISION}",
    "199_v10b_github_commit",
    retain_body=True,
)
requests.append(receipt)
commit = parse_json(commit_body, "github_commit")

raw_license, receipt = capture(
    f"https://raw.githubusercontent.com/TARGENE/targene-pipeline/{REVISION}/LICENSE",
    "199_v10b_github_raw_license",
    retain_body=True,
    accept="text/plain,*/*",
)
requests.append(receipt)

zenodo_record_body, receipt = capture(
    "https://zenodo.org/api/records/19202203",
    "199_v10b_zenodo_record",
    retain_body=True,
)
requests.append(receipt)
zenodo_record = parse_json(zenodo_record_body, "zenodo_record")
matching_files = [
    item
    for item in zenodo_record.get("files", [])
    if item.get("key") == "TARGENE/targene-pipeline-v0.13.4.zip"
]
if len(matching_files) != 1:
    raise AssertionError(f"zenodo_record: expected one frozen file, found {len(matching_files)}")
zenodo_file = matching_files[0]
zenodo_url = (zenodo_file.get("links") or {}).get("self")
if not isinstance(zenodo_url, str):
    raise AssertionError("zenodo_record: exact file has no content URL")
zenodo_zip, receipt = capture(
    zenodo_url,
    "199_v10b_zenodo_archive_omitted",
    retain_body=False,
    accept="application/zip,application/octet-stream,*/*",
)
requests.append(receipt)

codeload_zip, receipt = capture(
    f"https://codeload.github.com/TARGENE/targene-pipeline/zip/{REVISION}",
    "199_v10b_github_codeload_omitted",
    retain_body=False,
    accept="application/zip,application/octet-stream,*/*",
)
requests.append(receipt)

zenodo_manifest = normalized_zip_manifest(zenodo_zip, "zenodo_v0.13.4")
codeload_manifest = normalized_zip_manifest(codeload_zip, f"github_revision_{REVISION}")
comparison = compare_manifests(zenodo_manifest, codeload_manifest)

swh_snapshot_bytes = (EVIDENCE / "199_swh_canonical_origin_snapshot.body").read_bytes()
swh_revision_bytes = (EVIDENCE / "199_swh_v0_13_5_revision.body").read_bytes()
swh_snapshot = json.loads(swh_snapshot_bytes)
swh_revision = json.loads(swh_revision_bytes)
swh_branch = (swh_snapshot.get("branches") or {}).get("refs/tags/v0.13.5") or {}

zenodo_related = [
    item.get("identifier", "")
    for item in (zenodo_record.get("metadata") or {}).get("related_identifiers", [])
]
zenodo_license = ((zenodo_record.get("metadata") or {}).get("license") or {}).get("id")
zenodo_record_gate = (
    zenodo_record.get("doi") == "10.5281/zenodo.19202203"
    and (zenodo_record.get("metadata") or {}).get("version") == "v0.13.4"
    and zenodo_license == "mit-license"
    and any("github.com/TARGENE/targene-pipeline/tree/v0.13.4" in value for value in zenodo_related)
    and zenodo_file.get("checksum") == f"md5:{ZENODO_MD5}"
)
zenodo_md5_gate = zenodo_manifest["archive_md5"] == ZENODO_MD5
github_ref_gate = resolved_ref_type == "commit" and resolved_ref_sha == REVISION
github_commit_gate = commit.get("sha") == REVISION and "/TARGENE/targene-pipeline/" in commit.get("html_url", "")
swh_gate = (
    swh_branch.get("target_type") == "revision"
    and swh_branch.get("target") == REVISION
    and swh_revision.get("id") == REVISION
    and swh_revision.get("directory") == DIRECTORY
)
exact_content_gate = comparison["exact"]

zenodo_license_entry = find_license(zenodo_manifest)
codeload_license_entry = find_license(codeload_manifest)
license_path_gate = (
    zenodo_license_entry is not None
    and codeload_license_entry is not None
    and zenodo_license_entry["normalized_path"] == codeload_license_entry["normalized_path"]
)
license_byte_equal = (
    license_path_gate
    and zenodo_license_entry["sha256"] == codeload_license_entry["sha256"] == digest(raw_license)
)
rights_gate = zenodo_license == "mit-license" and is_mit_text(raw_license) and license_byte_equal

gates = {
    "protocol_hash_frozen": digest(protocol_bytes) == freeze["sha256"],
    "github_v0_13_5_ref_to_full_revision": github_ref_gate,
    "github_exact_commit_authenticated": github_commit_gate,
    "swh_origin_ref_revision_directory": swh_gate,
    "zenodo_exact_record_version_repository_file_rights": zenodo_record_gate,
    "zenodo_archive_declared_md5": zenodo_md5_gate,
    "exact_normalized_archive_to_revision_manifest": exact_content_gate,
    "exact_archive_and_revision_mit_rights": rights_gate,
}
all_pass = all(gates.values())

result = {
    "schema_version": "orion.p4.exact-edge-lineage-authority.v10b.edge-199-content-identity",
    "identity": "P4.M6.JOSS.EXACT.EDGE.LINEAGE.AUTHORITY.V10B.INDEX.199",
    "finished_at": dt.datetime.now(dt.timezone.utc).isoformat(),
    "outcome_informed_successor": True,
    "protocol_path": "PROTOCOL_V10B.json",
    "protocol_sha256": digest(protocol_bytes),
    "frozen_index": 199,
    "repository": "targene/targene-pipeline",
    "publication_version": "v0.13.4",
    "comparison_revision_ref": "v0.13.5",
    "comparison_revision": REVISION,
    "comparison_directory_swhid": f"swh:1:dir:{DIRECTORY}",
    "gates": gates,
    "all_closure_gates_pass": all_pass,
    "verdict": "RESOLVED_SAME_CONTENT_IDENTITY" if all_pass else "REMAINS_CANNOT_CHECK",
    "accepted_identity_method": (
        "EXACT_NORMALIZED_ZENODO_ARCHIVE_TO_GITHUB_IMMUTABLE_COMMIT_MANIFEST_EQUALITY"
        if all_pass
        else None
    ),
    "github_ref": {
        "initial_object_type": ref_object.get("type"),
        "initial_object_sha": ref_object.get("sha"),
        "annotated_tag_followed": annotated_tag is not None,
        "resolved_object_type": resolved_ref_type,
        "resolved_object_sha": resolved_ref_sha,
    },
    "github_commit": {
        "sha": commit.get("sha"),
        "html_url": commit.get("html_url"),
        "tree_sha": ((commit.get("commit") or {}).get("tree") or {}).get("sha"),
    },
    "software_heritage": {
        "origin_snapshot_sha1": "4cc32f66bbfae46d9d3ee0bfd210a46619f0e895",
        "snapshot_body_sha256": digest(swh_snapshot_bytes),
        "ref_target": swh_branch.get("target"),
        "ref_target_type": swh_branch.get("target_type"),
        "revision_body_sha256": digest(swh_revision_bytes),
        "revision_id": swh_revision.get("id"),
        "revision_directory": swh_revision.get("directory"),
    },
    "zenodo": {
        "record_id": zenodo_record.get("id"),
        "doi": zenodo_record.get("doi"),
        "version": (zenodo_record.get("metadata") or {}).get("version"),
        "license": zenodo_license,
        "file_key": zenodo_file.get("key"),
        "provider_checksum": zenodo_file.get("checksum"),
        "downloaded_md5": zenodo_manifest["archive_md5"],
        "downloaded_sha256": zenodo_manifest["archive_sha256"],
        "downloaded_bytes": zenodo_manifest["archive_bytes"],
    },
    "github_codeload": {
        "revision": REVISION,
        "downloaded_md5": codeload_manifest["archive_md5"],
        "downloaded_sha256": codeload_manifest["archive_sha256"],
        "downloaded_bytes": codeload_manifest["archive_bytes"],
    },
    "comparison": comparison,
    "licenses": {
        "zenodo_declared": zenodo_license,
        "zenodo_archive_license": zenodo_license_entry,
        "github_codeload_license": codeload_license_entry,
        "github_raw_license_bytes": len(raw_license),
        "github_raw_license_sha256": digest(raw_license),
        "github_raw_license_is_mit": is_mit_text(raw_license),
        "exact_license_byte_equal": license_byte_equal,
    },
    "claim_boundary": [
        "This closes only the checksum-bound archive content identity to an immutable provider-native full revision.",
        "The later v0.13.5 revision is not asserted to be the deleted v0.13.4 commit, its descendant or a restored tag.",
        "The version-label difference is explicit and no unit is added.",
        "No natural-pair, author-lineage, source-disjoint replication, custody, outcome, performance or superiority authority is granted.",
    ],
    "next_discriminator": "Closed for exact source content identity." if all_pass else "Repair the first failed frozen V10B conjunction; no compensatory evidence is allowed.",
}
(ROOT / "EDGE_199_CONTENT_IDENTITY_V10B.json").write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")

manifests = {
    "schema_version": "orion.p4.exact-edge-lineage-authority.v10b.edge-199-manifests",
    "normalization_rule": protocol["normalization_and_comparison"],
    "zenodo": zenodo_manifest,
    "github_codeload": codeload_manifest,
}
(ROOT / "EDGE_199_NORMALIZED_MANIFESTS_V10B.json").write_text(json.dumps(manifests, indent=2, sort_keys=True) + "\n")

probe_receipt = {
    "schema_version": "orion.p4.exact-edge-lineage-authority.v10b.probe-receipt",
    "finished_at": dt.datetime.now(dt.timezone.utc).isoformat(),
    "protocol_sha256": digest(protocol_bytes),
    "request_count": len(requests),
    "requests": requests,
    "large_payloads_retained": False,
    "large_payloads": [
        {
            "identity": "zenodo_v0.13.4_zip",
            "bytes": len(zenodo_zip),
            "md5": digest(zenodo_zip, "md5"),
            "sha256": digest(zenodo_zip),
        },
        {
            "identity": f"github_codeload_revision_{REVISION}",
            "bytes": len(codeload_zip),
            "md5": digest(codeload_zip, "md5"),
            "sha256": digest(codeload_zip),
        },
    ],
}
(ROOT / "PROBE_RECEIPT_V10B.json").write_text(json.dumps(probe_receipt, indent=2, sort_keys=True) + "\n")

print(
    json.dumps(
        {
            "all_closure_gates_pass": all_pass,
            "gates": gates,
            "zenodo_entries": zenodo_manifest["entry_count"],
            "github_entries": codeload_manifest["entry_count"],
            "comparison": {
                "exact": comparison["exact"],
                "only_left": comparison["only_left_count"],
                "only_right": comparison["only_right_count"],
                "differing": comparison["differing_count"],
            },
        },
        sort_keys=True,
    )
)

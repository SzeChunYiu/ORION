#!/usr/bin/env python3
from __future__ import annotations

import datetime as dt
import hashlib
import io
import json
import os
import stat
import subprocess
import tarfile
import tempfile
import time
import urllib.error
import urllib.request
from pathlib import Path, PurePosixPath

ROOT = Path(__file__).resolve().parent
EVIDENCE = ROOT / "evidence"
EVIDENCE.mkdir(exist_ok=True)
UA = "ORION-P4-exact-edge-authority-v11/1.0 (public research evidence audit)"
HEAD91 = "aa021231cdafb6d74ce9ab5f55f824a3032058a4"
ARCHIVE91_SHA256 = "2a94e0ed7e61e18ea4135aa559d6a06a407adcabd84dbbc52ebface6bba5b407"


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
        with urllib.request.urlopen(request, timeout=240) as response:
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
    except Exception as exc:
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
                "x-pypi-last-serial",
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
    time.sleep(0.15)
    return body, receipt


def json_object(body: bytes, label: str) -> dict:
    try:
        value = json.loads(body)
    except Exception as exc:
        raise AssertionError(f"{label}: non-JSON response {type(exc).__name__}:{exc}") from exc
    if not isinstance(value, dict):
        raise AssertionError(f"{label}: top-level JSON is not an object")
    return value


def tar_manifest(data: bytes, label: str, *, separate_git_envelope: bool) -> dict:
    roots: set[str] = set()
    entries: dict[str, dict] = {}
    git_members: list[dict] = []
    directories = 0
    rejected_types: list[dict] = []
    try:
        archive = tarfile.open(fileobj=io.BytesIO(data), mode="r:gz")
    except Exception as exc:
        raise AssertionError(f"{label}: not a gzip-compressed TAR: {type(exc).__name__}:{exc}") from exc
    with archive:
        for member in archive.getmembers():
            raw = member.name.replace("\\", "/").rstrip("/")
            path = PurePosixPath(raw)
            parts = path.parts
            if raw.startswith("/") or not parts or any(part in {"", ".", ".."} for part in parts):
                raise AssertionError(f"{label}: unsafe path {member.name!r}")
            roots.add(parts[0])
            if member.isdir():
                directories += 1
                continue
            if len(parts) < 2:
                raise AssertionError(f"{label}: non-directory member is not beneath one root: {member.name!r}")
            normalized = "/".join(parts[1:])
            if separate_git_envelope and (normalized == ".git" or normalized.startswith(".git/")):
                git_members.append(
                    {
                        "normalized_path": normalized,
                        "entry_type": "symlink" if member.issym() else "regular" if member.isfile() else "other",
                        "bytes": member.size,
                        "mode": member.mode,
                    }
                )
                continue
            if normalized in entries:
                raise AssertionError(f"{label}: duplicate normalized path {normalized!r}")
            if member.isfile():
                handle = archive.extractfile(member)
                if handle is None:
                    raise AssertionError(f"{label}: cannot read regular file {member.name!r}")
                payload = handle.read()
                entry_type = "regular"
            elif member.issym():
                payload = member.linkname.encode("utf-8")
                entry_type = "symlink"
            else:
                rejected_types.append({"normalized_path": normalized, "tar_type": repr(member.type)})
                continue
            entries[normalized] = {
                "normalized_path": normalized,
                "entry_type": entry_type,
                "sha256": digest(payload),
                "bytes": len(payload),
                "unix_executable_bit": bool(member.mode & 0o111),
            }
    if len(roots) != 1:
        raise AssertionError(f"{label}: expected exactly one top-level root, found {sorted(roots)}")
    if rejected_types:
        raise AssertionError(f"{label}: unsupported TAR member types: {rejected_types[:5]}")
    manifest = [entries[name] for name in sorted(entries)]
    return {
        "label": label,
        "archive_bytes": len(data),
        "archive_md5": digest(data, "md5"),
        "archive_sha256": digest(data),
        "top_level_root": next(iter(roots)),
        "directory_entry_count": directories,
        "git_envelope_separated": separate_git_envelope,
        "git_envelope_member_count": len(git_members),
        "git_envelope_members_sha256": digest(json.dumps(git_members, sort_keys=True, separators=(",", ":")).encode()),
        "entry_count": len(manifest),
        "total_payload_bytes": sum(item["bytes"] for item in manifest),
        "manifest_sha256": digest(json.dumps(manifest, sort_keys=True, separators=(",", ":")).encode()),
        "manifest": manifest,
    }


def compare(left: dict, right: dict) -> dict:
    lm = {item["normalized_path"]: item for item in left["manifest"]}
    rm = {item["normalized_path"]: item for item in right["manifest"]}
    common = sorted(set(lm) & set(rm))
    only_left = sorted(set(lm) - set(rm))
    only_right = sorted(set(rm) - set(lm))
    differing = [name for name in common if lm[name] != rm[name]]
    return {
        "exact": not only_left and not only_right and not differing,
        "left_count": len(lm),
        "right_count": len(rm),
        "common_count": len(common),
        "only_left_count": len(only_left),
        "only_right_count": len(only_right),
        "differing_count": len(differing),
        "only_left": only_left,
        "only_right": only_right,
        "differing": [
            {"normalized_path": name, "left": lm[name], "right": rm[name]}
            for name in differing
        ],
    }


def run_git(repo: Path, *args: str, check: bool = False) -> dict:
    env = {**os.environ, "HOME": str(repo.parent), "GIT_CONFIG_NOSYSTEM": "1", "GIT_OPTIONAL_LOCKS": "0", "LC_ALL": "C"}
    proc = subprocess.run(
        ["git", "-C", str(repo), *args],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        env=env,
        text=True,
        timeout=180,
        check=False,
    )
    receipt = {
        "args": list(args),
        "returncode": proc.returncode,
        "stdout": proc.stdout,
        "stderr": proc.stderr,
    }
    if check and proc.returncode != 0:
        raise AssertionError(f"git {' '.join(args)} failed: {receipt}")
    return receipt


def embedded_git_receipt(data: bytes) -> dict:
    with tempfile.TemporaryDirectory(prefix="orion-p4-v11-91-") as tmp:
        base = Path(tmp)
        with tarfile.open(fileobj=io.BytesIO(data), mode="r:gz") as archive:
            members = archive.getmembers()
            for member in members:
                path = PurePosixPath(member.name.replace("\\", "/"))
                if member.name.startswith("/") or any(part in {"", ".", ".."} for part in path.parts):
                    raise AssertionError(f"unsafe extraction path {member.name!r}")
                if member.islnk() or member.isdev() or member.isfifo():
                    raise AssertionError(f"unsupported extraction member {member.name!r}")
            archive.extractall(base, filter="data")
        roots = [path for path in base.iterdir() if path.is_dir()]
        if len(roots) != 1:
            raise AssertionError(f"expected one extracted root, found {roots}")
        repo = roots[0]
        commands = {
            "head": run_git(repo, "rev-parse", "HEAD", check=True),
            "tree": run_git(repo, "rev-parse", "HEAD^{tree}", check=True),
            "origin": run_git(repo, "config", "--get", "remote.origin.url", check=True),
            "fsck": run_git(repo, "fsck", "--full", "--no-reflogs"),
            "status": run_git(repo, "status", "--porcelain=v1", "--untracked-files=all", check=True),
            "diff_files": run_git(repo, "diff-files", "--quiet"),
            "diff_index": run_git(repo, "diff-index", "--cached", "--quiet", "HEAD"),
        }
        return {
            "commands": commands,
            "head": commands["head"]["stdout"].strip(),
            "tree": commands["tree"]["stdout"].strip(),
            "origin": commands["origin"]["stdout"].strip(),
            "fsck_returncode": commands["fsck"]["returncode"],
            "fsck_stderr_sha256": digest(commands["fsck"]["stderr"].encode()),
            "status_porcelain": commands["status"]["stdout"].splitlines(),
            "diff_files_clean": commands["diff_files"]["returncode"] == 0,
            "diff_index_clean": commands["diff_index"]["returncode"] == 0,
        }


def find_license(manifest: dict) -> dict | None:
    candidates = [
        item
        for item in manifest["manifest"]
        if PurePosixPath(item["normalized_path"]).name.lower() in {"license", "license.md", "license.txt"}
    ]
    return candidates[0] if len(candidates) == 1 else None


def is_mit(data: bytes) -> bool:
    text = data.decode("utf-8", errors="replace")
    return "Permission is hereby granted, free of charge" in text and "THE SOFTWARE IS PROVIDED \"AS IS\"" in text


protocol_bytes = (ROOT / "PROTOCOL_V11.json").read_bytes()
freeze = json.loads((ROOT / "PROTOCOL_FREEZE_RECEIPT_V11.json").read_text())
if digest(protocol_bytes) != freeze["protocol_sha256"]:
    raise AssertionError("V11 protocol hash mismatch")
requests: list[dict] = []

# Index 36: smallest provider-correction gate; do not redownload the known adverse 85 MB archive.
z36_body, receipt = capture("https://zenodo.org/api/records/21221062", "36_zenodo_child", retain_body=True)
requests.append(receipt)
d36c_body, receipt = capture("https://api.datacite.org/dois/10.5281%2Fzenodo.21221061", "36_datacite_concept", retain_body=True)
requests.append(receipt)
d36v_body, receipt = capture("https://api.datacite.org/dois/10.5281%2Fzenodo.21221062", "36_datacite_child", retain_body=True)
requests.append(receipt)
z36 = json_object(z36_body, "index36_zenodo")
d36c = json_object(d36c_body, "index36_datacite_concept")
d36v = json_object(d36v_body, "index36_datacite_child")
d36_version = ((d36v.get("data") or {}).get("attributes") or {}).get("version")
z36_version = (z36.get("metadata") or {}).get("version")
index36 = {
    "schema_version": "orion.p4.exact-edge-lineage-authority.v11.index-36-provider-correction",
    "frozen_index": 36,
    "zenodo": {
        "id": z36.get("id"),
        "doi": z36.get("doi"),
        "conceptdoi": (z36.get("metadata") or {}).get("conceptdoi"),
        "version": z36_version,
        "file": [
            {"key": item.get("key"), "size": item.get("size"), "checksum": item.get("checksum")}
            for item in z36.get("files", [])
        ],
    },
    "datacite": {
        "concept_doi": ((d36c.get("data") or {}).get("attributes") or {}).get("doi"),
        "concept_version": ((d36c.get("data") or {}).get("attributes") or {}).get("version"),
        "child_doi": ((d36v.get("data") or {}).get("attributes") or {}).get("doi"),
        "child_version": d36_version,
    },
    "preserved_archive": {
        "sha256": "e8d9defc64c7da5b64859ade992230c99ff4c20cb2e748c1f5827f6fcf72480c",
        "embedded_head": "3cd108c376faf9832373adfe3ab4688295aa42fa",
        "embedded_head_tag": "0.0.12",
        "accepted_commit": "069ab4f56d100d765d46c594ac1b06add7e49f9e",
    },
    "gates": {
        "provider_exact_version_0_0_3": z36_version == "0.0.3" and d36_version == "0.0.3",
        "archive_root_to_accepted_commit": False,
    },
    "verdict": "REMAINS_CANNOT_CHECK",
    "terminal": "VERSION_METADATA_AND_PRESERVED_EMBEDDED_HEAD_BOTH_CONTRADICT_PUBLICATION_VERSION_COMMIT",
    "next_discriminator": "A provider replacement/correction must bind an exact 0.0.3 archive checksum whose root is the accepted commit; the current archive is an embedded 0.0.12 worktree.",
}
(ROOT / "EDGE_36_PROVIDER_CORRECTION_V11.json").write_text(json.dumps(index36, indent=2, sort_keys=True) + "\n")

# Index 91: exact embedded-HEAD content witness.
z91_body, receipt = capture("https://zenodo.org/api/records/20171460", "91_zenodo_record", retain_body=True)
requests.append(receipt)
z91 = json_object(z91_body, "index91_zenodo")
files91 = z91.get("files", [])
if len(files91) != 1:
    raise AssertionError(f"index91: expected one exact archive, found {len(files91)}")
archive91_url = (files91[0].get("links") or {}).get("self")
if not isinstance(archive91_url, str):
    raise AssertionError("index91: exact archive has no content URL")
archive91, receipt = capture(archive91_url, "91_zenodo_archive_omitted", retain_body=False, accept="application/gzip,application/octet-stream,*/*")
requests.append(receipt)
commit91_body, receipt = capture(
    f"https://api.github.com/repos/NutritionalLungImmunity/PAI/commits/{HEAD91}",
    "91_github_embedded_head_commit",
    retain_body=True,
)
requests.append(receipt)
commit91 = json_object(commit91_body, "index91_github_commit")
license91, receipt = capture(
    f"https://raw.githubusercontent.com/NutritionalLungImmunity/PAI/{HEAD91}/LICENSE",
    "91_github_embedded_head_license",
    retain_body=True,
    accept="text/plain,*/*",
)
requests.append(receipt)
codeload91, receipt = capture(
    f"https://codeload.github.com/NutritionalLungImmunity/PAI/tar.gz/{HEAD91}",
    "91_github_embedded_head_codeload_omitted",
    retain_body=False,
    accept="application/gzip,application/octet-stream,*/*",
)
requests.append(receipt)

archive_manifest = tar_manifest(archive91, "zenodo_v1.0.0_embedded_git_archive", separate_git_envelope=True)
codeload_manifest = tar_manifest(codeload91, f"github_revision_{HEAD91}", separate_git_envelope=False)
comparison = compare(archive_manifest, codeload_manifest)
git_receipt = embedded_git_receipt(archive91)
commit_tree = ((commit91.get("commit") or {}).get("tree") or {}).get("sha")
z91_license = ((z91.get("metadata") or {}).get("license") or {}).get("id")
archive_license = find_license(archive_manifest)
codeload_license = find_license(codeload_manifest)
license_equal = (
    archive_license is not None
    and codeload_license is not None
    and archive_license["normalized_path"] == codeload_license["normalized_path"]
    and archive_license["sha256"] == codeload_license["sha256"] == digest(license91)
)
gates91 = {
    "zenodo_exact_record_version_file_rights": (
        z91.get("doi") == "10.5281/zenodo.20171460"
        and (z91.get("metadata") or {}).get("version") == "v1.0.0"
        and z91_license == "mit-license"
        and files91[0].get("checksum") == "md5:506a29c006cbf81161acf21bca60e021"
    ),
    "zenodo_archive_checksum": digest(archive91, "md5") == "506a29c006cbf81161acf21bca60e021" and digest(archive91) == ARCHIVE91_SHA256,
    "embedded_git_valid_clean_head": (
        git_receipt["head"] == HEAD91
        and git_receipt["fsck_returncode"] == 0
        and git_receipt["status_porcelain"] == []
        and git_receipt["diff_files_clean"]
        and git_receipt["diff_index_clean"]
        and "github.com/NutritionalLungImmunity/PAI" in git_receipt["origin"]
    ),
    "github_full_revision_authenticated": commit91.get("sha") == HEAD91 and commit_tree is not None,
    "embedded_git_tree_equals_github_tree": git_receipt["tree"] == commit_tree,
    "exact_non_git_archive_to_codeload_manifest": comparison["exact"],
    "archive_and_revision_mit_rights": z91_license == "mit-license" and is_mit(license91) and license_equal,
}
pass91 = all(gates91.values())
edge91 = {
    "schema_version": "orion.p4.exact-edge-lineage-authority.v11.index-91-embedded-head-content-identity",
    "frozen_index": 91,
    "repository": "nutritionallungimmunity/pai",
    "publication_version": "v1.0.0",
    "accepted_tag_commit": "9fa30e9f405de4446c792bd59cb7c5a4bb7ecb59",
    "content_witness_revision": HEAD91,
    "gates": gates91,
    "all_closure_gates_pass": pass91,
    "verdict": "RESOLVED_SAME_CONTENT_IDENTITY" if pass91 else "REMAINS_CANNOT_CHECK",
    "accepted_identity_method": "EXACT_CLEAN_EMBEDDED_GIT_HEAD_TREE_AND_NON_GIT_WORKTREE_TO_GITHUB_IMMUTABLE_REVISION_EQUALITY" if pass91 else None,
    "zenodo_archive": {
        "bytes": len(archive91),
        "md5": digest(archive91, "md5"),
        "sha256": digest(archive91),
        "provider_checksum": files91[0].get("checksum"),
    },
    "github_codeload": {"bytes": len(codeload91), "md5": digest(codeload91, "md5"), "sha256": digest(codeload91)},
    "github_commit": {"sha": commit91.get("sha"), "tree_sha": commit_tree, "html_url": commit91.get("html_url")},
    "embedded_git": git_receipt,
    "comparison": comparison,
    "licenses": {
        "zenodo_declared": z91_license,
        "archive_license": archive_license,
        "codeload_license": codeload_license,
        "raw_license_bytes": len(license91),
        "raw_license_sha256": digest(license91),
        "raw_license_is_mit": is_mit(license91),
        "exact_license_byte_equal": license_equal,
    },
    "tag_mismatch_boundary": "The exact content witness is embedded HEAD aa021231cdafb6d74ce9ab5f55f824a3032058a4, not accepted tag commit 9fa30e9f405de4446c792bd59cb7c5a4bb7ecb59. No equality, ancestry or restoration relation between those commits is asserted.",
    "next_discriminator": "Closed for exact source content identity." if pass91 else "Repair the first failed frozen V11 index-91 conjunction; no subset or compensatory rule is allowed.",
}
(ROOT / "EDGE_91_EMBEDDED_HEAD_CONTENT_IDENTITY_V11.json").write_text(json.dumps(edge91, indent=2, sort_keys=True) + "\n")
(ROOT / "EDGE_91_NORMALIZED_MANIFESTS_V11.json").write_text(
    json.dumps(
        {
            "schema_version": "orion.p4.exact-edge-lineage-authority.v11.index-91-manifests",
            "normalization_rule": json.loads(protocol_bytes)["index_91_archive_normalization"],
            "archive_non_git_payload": archive_manifest,
            "github_codeload": codeload_manifest,
        },
        indent=2,
        sort_keys=True,
    )
    + "\n"
)

# Indices 133/185: alternate official PyPI file-object provenance channel.
pypi_rows = []
for index, project, filename, expected_sha, expected_commit in [
    (133, "woodtapper", "woodtapper-0.0.13.tar.gz", "b509f6469b9ff8888195751c811d689559f45e24aeb35bb173b9680c99c8dbf3", "7ac6d23d504404c4004faad663f6b889427109e6"),
    (185, "disruption-py", "disruption_py-0.14.0.tar.gz", "775f92dbcbd6d1523db241494998e4b0867d51a84236feb7accc86b63b033a19", "dec5c58a3e3970bc6817f33efb615fea11057fce"),
]:
    body, receipt = capture(
        f"https://pypi.org/simple/{project}/",
        f"{index}_pypi_simple_json",
        retain_body=True,
        accept="application/vnd.pypi.simple.v1+json",
    )
    requests.append(receipt)
    simple = json_object(body, f"index{index}_pypi_simple")
    matches = [item for item in simple.get("files", []) if item.get("filename") == filename]
    if len(matches) != 1:
        raise AssertionError(f"index {index}: expected one exact Simple file object, found {len(matches)}")
    file_object = matches[0]
    provenance_value = file_object.get("provenance")
    provenance_url = None
    if isinstance(provenance_value, str):
        provenance_url = provenance_value
    elif isinstance(provenance_value, dict):
        for key in ("url", "href"):
            if isinstance(provenance_value.get(key), str):
                provenance_url = provenance_value[key]
                break
    provenance_receipt = None
    provenance_parsed = None
    if provenance_url:
        provenance_body, provenance_receipt = capture(
            provenance_url,
            f"{index}_pypi_exact_file_provenance",
            retain_body=True,
            accept="application/json",
        )
        requests.append(provenance_receipt)
        try:
            provenance_parsed = json.loads(provenance_body)
        except Exception:
            provenance_parsed = None
    hash_gate = (file_object.get("hashes") or {}).get("sha256") == expected_sha
    # No statement is promoted by string search; a future non-null object requires a dedicated frozen parser successor.
    direct_binding_gate = False
    pypi_rows.append(
        {
            "frozen_index": index,
            "project": project,
            "filename": filename,
            "expected_sha256": expected_sha,
            "simple_api_sha256": (file_object.get("hashes") or {}).get("sha256"),
            "exact_file_object": file_object,
            "exact_file_hash_gate": hash_gate,
            "provenance_field_present": provenance_value is not None,
            "provenance_value": provenance_value,
            "provenance_url": provenance_url,
            "provenance_receipt": provenance_receipt,
            "provenance_top_level_type": type(provenance_parsed).__name__ if provenance_parsed is not None else None,
            "accepted_commit": expected_commit,
            "provider_native_signed_artifact_to_commit_binding": direct_binding_gate,
            "verdict": "REMAINS_CANNOT_CHECK",
            "terminal": "PYPI_EXACT_FILE_OBJECT_HAS_NO_PARSED_SIGNED_ARTIFACT_TO_FULL_COMMIT_BINDING",
            "next_discriminator": "An exact-file PyPI provenance statement must bind the frozen SHA-256 to the accepted full commit; if a provenance field appears, freeze a statement parser before adjudication.",
        }
    )
(ROOT / "PYPI_SIMPLE_PROVENANCE_V11.json").write_text(
    json.dumps(
        {
            "schema_version": "orion.p4.exact-edge-lineage-authority.v11.pypi-simple-provenance",
            "rows": pypi_rows,
        },
        indent=2,
        sort_keys=True,
    )
    + "\n"
)

probe_receipt = {
    "schema_version": "orion.p4.exact-edge-lineage-authority.v11.probe-receipt",
    "finished_at": dt.datetime.now(dt.timezone.utc).isoformat(),
    "protocol_sha256": digest(protocol_bytes),
    "request_count": len(requests),
    "requests": requests,
    "large_payloads_retained": False,
    "large_payloads": [
        {"identity": "index_91_zenodo_archive", "bytes": len(archive91), "md5": digest(archive91, "md5"), "sha256": digest(archive91)},
        {"identity": f"index_91_github_codeload_{HEAD91}", "bytes": len(codeload91), "md5": digest(codeload91, "md5"), "sha256": digest(codeload91)},
    ],
}
(ROOT / "PROBE_RECEIPT_V11.json").write_text(json.dumps(probe_receipt, indent=2, sort_keys=True) + "\n")

print(
    json.dumps(
        {
            "requests": len(requests),
            "index36": index36["verdict"],
            "index91": edge91["verdict"],
            "index91_gates": gates91,
            "index91_comparison": {
                "exact": comparison["exact"],
                "left": comparison["left_count"],
                "right": comparison["right_count"],
                "only_left": comparison["only_left_count"],
                "only_right": comparison["only_right_count"],
                "differing": comparison["differing_count"],
            },
            "pypi": [{"index": row["frozen_index"], "provenance": row["provenance_field_present"], "verdict": row["verdict"]} for row in pypi_rows],
        },
        sort_keys=True,
    )
)

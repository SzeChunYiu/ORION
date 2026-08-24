#!/usr/bin/env python3
"""Materialize only the outcome-free DGM source subset at the frozen commit."""

from __future__ import annotations

import gzip
import hashlib
import io
import json
import tarfile
import time
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path


HERE = Path(__file__).resolve().parent
EVIDENCE = HERE / "evidence"
REPOSITORY = "jennyzzt/dgm"
COMMIT = "a565fd2d1dca504ef5104a7cc0f3bdc4ab9b4fd2"
EXPECTED_TREE = "dc58ea5c481124afdb97468c1bed4e0debb425c4"
EXCLUDED = ("initial/", "initial_polyglot/", "swe_bench/ref_agent_results/")
EXPECTED_EXCLUDED_FILES = 1595
EXPECTED_EXCLUDED_BYTES = 49_707_333
EXPECTED_INCLUDED_FILES = 55
EXPECTED_INCLUDED_BYTES = 3_488_164
OUTPUT = HERE / f"DGM_FILTERED_SOURCE_{COMMIT}.tar.gz"
RECEIPT = HERE / "P5_C3_FILTERED_DGM_SOURCE_RECEIPT_V8.json"


def now() -> str:
    return datetime.now(timezone.utc).isoformat()


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def git_blob_sha1(data: bytes) -> str:
    return hashlib.sha1(f"blob {len(data)}\0".encode() + data).hexdigest()


def fetch(url: str, accept: str) -> tuple[bytes | None, dict]:
    started = now()
    clock = time.monotonic()
    body = b""
    status = None
    final_url = url
    error = None
    headers = {}
    req = urllib.request.Request(
        url,
        headers={"Accept": accept, "User-Agent": "orion-p5-c3-v8-exact-seed/1.0"},
    )
    try:
        with urllib.request.urlopen(req, timeout=120) as response:
            body = response.read()
            status = response.status
            final_url = response.geturl()
            headers = dict(response.headers.items())
    except urllib.error.HTTPError as exc:
        body = exc.read()
        status = exc.code
        final_url = exc.geturl()
        error = f"HTTPError:{exc.code}"
    except Exception as exc:
        error = f"{type(exc).__name__}:{exc}"
    receipt = {
        "url": url,
        "final_url": final_url,
        "http_status": status,
        "error": error,
        "body_bytes": len(body),
        "body_sha256": sha256(body) if body else None,
        "content_type": headers.get("Content-Type"),
        "started_at": started,
        "finished_at": now(),
        "runtime_seconds": round(time.monotonic() - clock, 6),
    }
    return (body if status == 200 and error is None else None), receipt


def deterministic_tar_gz(members: list[tuple[str, bytes, int, str | None]]) -> bytes:
    out = io.BytesIO()
    with gzip.GzipFile(fileobj=out, mode="wb", mtime=0, filename="") as gz:
        with tarfile.open(fileobj=gz, mode="w", format=tarfile.PAX_FORMAT) as tar:
            for path, data, mode, linkname in sorted(members):
                info = tarfile.TarInfo(path)
                info.uid = 0
                info.gid = 0
                info.uname = ""
                info.gname = ""
                info.mtime = 0
                info.mode = mode
                if linkname is None:
                    info.size = len(data)
                    info.type = tarfile.REGTYPE
                    tar.addfile(info, io.BytesIO(data))
                else:
                    info.size = 0
                    info.type = tarfile.SYMTYPE
                    info.linkname = linkname
                    tar.addfile(info)
    return out.getvalue()


def main() -> None:
    EVIDENCE.mkdir(exist_ok=True)
    started_at = now()
    clock = time.monotonic()
    api = f"https://api.github.com/repos/{REPOSITORY}"
    commit_body, commit_req = fetch(f"{api}/git/commits/{COMMIT}", "application/vnd.github+json")
    if commit_body is None:
        raise RuntimeError("exact commit metadata unavailable")
    commit_meta = json.loads(commit_body)
    if commit_meta.get("sha") != COMMIT or (commit_meta.get("tree") or {}).get("sha") != EXPECTED_TREE:
        raise RuntimeError("commit/tree identity mismatch")

    tree_body, tree_req = fetch(
        f"{api}/git/trees/{EXPECTED_TREE}?recursive=1", "application/vnd.github+json"
    )
    if tree_body is None:
        raise RuntimeError("exact tree metadata unavailable")
    tree_meta = json.loads(tree_body)
    if tree_meta.get("sha") != EXPECTED_TREE or tree_meta.get("truncated") is not False:
        raise RuntimeError("tree response incomplete")
    blobs = {item["path"]: item for item in tree_meta["tree"] if item.get("type") == "blob"}
    included_tree = {p: x for p, x in blobs.items() if not p.startswith(EXCLUDED)}
    excluded_tree = {p: x for p, x in blobs.items() if p.startswith(EXCLUDED)}
    if (len(included_tree), sum(x["size"] for x in included_tree.values())) != (
        EXPECTED_INCLUDED_FILES,
        EXPECTED_INCLUDED_BYTES,
    ):
        raise RuntimeError("included metadata census mismatch")
    if (len(excluded_tree), sum(x["size"] for x in excluded_tree.values())) != (
        EXPECTED_EXCLUDED_FILES,
        EXPECTED_EXCLUDED_BYTES,
    ):
        raise RuntimeError("excluded metadata census mismatch")

    license_body, license_req = fetch(
        f"{api}/contents/LICENSE?ref={COMMIT}", "application/vnd.github.raw+json"
    )
    if license_body is None or sha256(license_body) != "84b7504ce8dda1f37f592cdf67ad21371864583720d79ea289b0b0c75bfcdb17":
        raise RuntimeError("exact DGM license mismatch")
    (EVIDENCE / "DGM_LICENSE_APACHE_2_0.txt").write_bytes(license_body)

    archive_url = f"https://codeload.github.com/{REPOSITORY}/tar.gz/{COMMIT}"
    archive_body, archive_req = fetch(archive_url, "application/octet-stream")
    if archive_body is None:
        raise RuntimeError("exact source archive unavailable")

    selected: list[tuple[str, bytes, int, str | None]] = []
    manifest = []
    archive_member_paths = set()
    excluded_archive_members = 0
    excluded_archive_bytes = 0
    with tarfile.open(fileobj=io.BytesIO(archive_body), mode="r:gz") as src:
        roots = {m.name.split("/", 1)[0] for m in src.getmembers() if "/" in m.name}
        if len(roots) != 1:
            raise RuntimeError("unexpected codeload archive root")
        root = next(iter(roots)) + "/"
        for member in src.getmembers():
            if not member.name.startswith(root):
                continue
            path = member.name[len(root) :]
            if not path or member.isdir():
                continue
            if path.startswith(EXCLUDED):
                if path in excluded_tree:
                    excluded_archive_members += 1
                    excluded_archive_bytes += excluded_tree[path]["size"]
                continue
            expected = included_tree.get(path)
            if expected is None:
                continue
            if member.isfile():
                stream = src.extractfile(member)
                if stream is None:
                    raise RuntimeError(f"cannot read included member {path}")
                data = stream.read()
                linkname = None
            elif member.issym():
                data = member.linkname.encode()
                linkname = member.linkname
            else:
                raise RuntimeError(f"unsupported included archive member type: {path}")
            if len(data) != expected["size"] or git_blob_sha1(data) != expected["sha"]:
                raise RuntimeError(f"included blob mismatch: {path}")
            mode = int(expected["mode"], 8) & 0o777
            selected.append((f"dgm/{path}", data, mode, linkname))
            archive_member_paths.add(path)
            manifest.append(
                {
                    "path": f"dgm/{path}",
                    "size_bytes": len(data),
                    "sha256": sha256(data),
                    "git_blob_sha1": expected["sha"],
                    "git_mode": expected["mode"],
                }
            )
    if archive_member_paths != set(included_tree):
        raise RuntimeError("codeload archive is missing included tree blobs")
    if (excluded_archive_members, excluded_archive_bytes) != (
        EXPECTED_EXCLUDED_FILES,
        EXPECTED_EXCLUDED_BYTES,
    ):
        raise RuntimeError("codeload excluded-member census mismatch")

    filtered = deterministic_tar_gz(selected)
    OUTPUT.write_bytes(filtered)
    canonical_manifest_sha256 = sha256(
        b"".join(
            f"{x['path']}\0{x['size_bytes']}\0{x['sha256']}\0{x['git_blob_sha1']}\n".encode()
            for x in sorted(manifest, key=lambda row: row["path"])
        )
    )
    finished_at = now()
    receipt = {
        "schema_version": "orion.p5.c3.filtered-dgm-source-receipt.v8",
        "authority": "GITHUB_EXACT_COMMIT_TREE_AND_BYTE_VERIFIED_FILTERED_SOURCE_ONLY",
        "source": {
            "repository": f"https://github.com/{REPOSITORY}",
            "commit_sha": COMMIT,
            "tree_sha": EXPECTED_TREE,
            "commit_request": commit_req,
            "tree_request": tree_req,
            "license_request": license_req,
            "codeload_request": archive_req,
        },
        "filter": {
            "excluded_prefixes": list(EXCLUDED),
            "excluded_files": excluded_archive_members,
            "excluded_blob_bytes": excluded_archive_bytes,
            "excluded_payload_contents_opened": False,
            "included_files": len(selected),
            "included_blob_bytes": sum(item["size_bytes"] for item in manifest),
            "every_included_blob_matches_exact_git_tree": True,
        },
        "rights": {
            "source_spdx": "Apache-2.0",
            "license_path": "evidence/DGM_LICENSE_APACHE_2_0.txt",
            "license_sha256": sha256(license_body),
        },
        "output": {
            "path": OUTPUT.name,
            "size_bytes": len(filtered),
            "sha256": sha256(filtered),
            "canonical_member_manifest_sha256": canonical_manifest_sha256,
            "members": manifest,
        },
        "started_at": started_at,
        "finished_at": finished_at,
        "runtime_seconds": round(time.monotonic() - clock, 6),
        "executions": {"dgm": 0, "model": 0, "benchmark": 0, "scorer": 0, "outcomes": 0},
    }
    RECEIPT.write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n")
    print(
        "P5_C3_V8_FILTERED_DGM_SOURCE_MATERIALIZED__"
        f"INCLUDED={len(selected)}__EXCLUDED={excluded_archive_members}__"
        f"SHA256={sha256(filtered)}__RUNTIME_SECONDS={time.monotonic() - clock:.6f}"
    )


if __name__ == "__main__":
    main()

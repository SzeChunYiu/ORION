#!/usr/bin/env python3
"""Build a deterministic Git-object binding for the ORION V1 component graph.

The builder reads only a frozen Git tree. Working-tree bytes, generated files,
and author declarations cannot alter the result. It binds every configured
component path to exact Git blob OIDs, SHA-256 byte digests, sizes, and modes.

This job deliberately does not infer a typed conceptual interface from path
co-location or imports. Dependency edges are emitted as explicit open proof
obligations until a separate interface-witness ledger discharges them.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import platform
import subprocess
import sys
import time
from dataclasses import dataclass
from pathlib import Path, PurePosixPath
from typing import Any, Iterable, Mapping, Sequence

SCHEMA = "ORION.V1.ComponentContentBinding.v1"
PACKET_SCHEMA = "ORION.V1.ComponentContentBindingPacket.v1"
DEFAULT_GRAPH = Path("research/orion-v1-freeze/V1_COMPONENT_GRAPH_V1.json")
PACKET_FILES = (
    "FREEZE.json",
    "RAW_MANIFEST.json",
    "PRIMARY_RESULT.json",
    "DONOR_RESULT.json",
    "NEGATIVE_CONTROLS.json",
    "RESOURCE_LEDGER.json",
    "TRANSFER_RESULT.json",
)


class BindingError(RuntimeError):
    """Raised when the frozen source or graph cannot be bound safely."""


@dataclass(frozen=True)
class TreeBlob:
    path: str
    mode: str
    oid: str
    size: int
    sha256: str

    def as_json(self) -> dict[str, Any]:
        return {
            "path": self.path,
            "mode": self.mode,
            "blob_oid": self.oid,
            "bytes": self.size,
            "sha256": self.sha256,
        }


def _run_git(root: Path, *args: str, text: bool = True) -> str | bytes:
    command = ["git", "-C", str(root), *args]
    completed = subprocess.run(
        command,
        check=False,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=text,
    )
    if completed.returncode != 0:
        stderr = completed.stderr if text else completed.stderr.decode("utf-8", "replace")
        raise BindingError(f"git command failed ({completed.returncode}): {' '.join(command)}\n{stderr}")
    return completed.stdout


def _safe_repo_path(value: Any, label: str) -> str:
    if not isinstance(value, str) or not value:
        raise BindingError(f"{label}: nonempty path required")
    if "\\" in value:
        raise BindingError(f"{label}: backslashes are forbidden")
    path = PurePosixPath(value)
    if path.is_absolute() or ".." in path.parts or value.startswith("./"):
        raise BindingError(f"{label}: unsafe repository path {value!r}")
    normalized = path.as_posix()
    if value.endswith("/") and not normalized.endswith("/"):
        normalized += "/"
    return normalized


def _load_graph(path: Path) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise BindingError(f"component graph missing: {path}") from exc
    except json.JSONDecodeError as exc:
        raise BindingError(f"invalid component graph JSON: {exc}") from exc
    if not isinstance(value, dict):
        raise BindingError("component graph must be a JSON object")
    if value.get("schema") != "ORION.V1.ComponentGraph.v1":
        raise BindingError("unexpected component graph schema")
    nodes = value.get("nodes")
    if not isinstance(nodes, list) or not nodes:
        raise BindingError("component graph must contain a nonempty nodes array")
    ids: list[str] = []
    for index, node in enumerate(nodes):
        if not isinstance(node, dict):
            raise BindingError(f"node {index}: object required")
        ident = node.get("id")
        if not isinstance(ident, str) or not ident:
            raise BindingError(f"node {index}: id required")
        ids.append(ident)
        paths = node.get("paths")
        if not isinstance(paths, list):
            raise BindingError(f"component {ident}: paths must be an array")
        node["paths"] = [_safe_repo_path(item, f"component {ident}") for item in paths]
        deps = node.get("depends_on")
        if not isinstance(deps, list) or not all(isinstance(item, str) for item in deps):
            raise BindingError(f"component {ident}: depends_on must be a string array")
        if len(deps) != len(set(deps)) or ident in deps:
            raise BindingError(f"component {ident}: duplicate or self dependency")
    if len(ids) != len(set(ids)):
        raise BindingError("duplicate component id")
    known = set(ids)
    for node in nodes:
        unknown = set(node["depends_on"]) - known
        if unknown:
            raise BindingError(f"component {node['id']}: unknown dependencies {sorted(unknown)}")
    return value


def _parse_tree(root: Path, ref: str) -> list[tuple[str, str, str]]:
    raw = _run_git(root, "ls-tree", "-r", "-z", "--full-tree", ref, text=False)
    assert isinstance(raw, bytes)
    rows: list[tuple[str, str, str]] = []
    for record in raw.split(b"\0"):
        if not record:
            continue
        try:
            metadata, path_bytes = record.split(b"\t", 1)
            mode, kind, oid = metadata.decode("ascii").split(" ", 2)
            path = path_bytes.decode("utf-8")
        except (ValueError, UnicodeDecodeError) as exc:
            raise BindingError("malformed git ls-tree record") from exc
        if kind == "blob":
            rows.append((path, mode, oid))
        elif kind == "commit":
            # A submodule is a distinct Git object, not a blob we can bind as bytes.
            rows.append((path, mode, f"SUBMODULE:{oid}"))
        else:
            raise BindingError(f"unexpected recursive tree object type {kind!r} for {path}")
    rows.sort(key=lambda row: row[0])
    return rows


def _read_blobs(root: Path, oids: Iterable[str]) -> dict[str, tuple[int, str]]:
    unique = sorted({oid for oid in oids if not oid.startswith("SUBMODULE:")})
    process = subprocess.Popen(
        ["git", "-C", str(root), "cat-file", "--batch"],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    assert process.stdin is not None and process.stdout is not None and process.stderr is not None
    result: dict[str, tuple[int, str]] = {}
    try:
        for oid in unique:
            process.stdin.write((oid + "\n").encode("ascii"))
            process.stdin.flush()
            header = process.stdout.readline()
            if not header:
                raise BindingError(f"git cat-file ended before {oid}")
            parts = header.decode("ascii", "replace").rstrip("\n").split(" ")
            if len(parts) == 2 and parts[1] == "missing":
                raise BindingError(f"Git object missing: {oid}")
            if len(parts) != 3 or parts[0] != oid or parts[1] != "blob":
                raise BindingError(f"unexpected git cat-file header for {oid}: {header!r}")
            size = int(parts[2])
            content = process.stdout.read(size)
            newline = process.stdout.read(1)
            if len(content) != size or newline != b"\n":
                raise BindingError(f"truncated Git blob response for {oid}")
            result[oid] = (size, hashlib.sha256(content).hexdigest())
        process.stdin.close()
        return_code = process.wait(timeout=30)
        if return_code != 0:
            raise BindingError(process.stderr.read().decode("utf-8", "replace"))
    finally:
        if process.poll() is None:
            process.kill()
    return result


def _matches(configured: str, tree_path: str) -> bool:
    if configured.endswith("/"):
        return tree_path.startswith(configured)
    return tree_path == configured or tree_path.startswith(configured + "/")


def _canonical_digest(value: Any) -> str:
    encoded = json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def _write_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(value, indent=2, sort_keys=True, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )


def build_binding(
    *, root: Path, graph_path: Path, output_dir: Path, ref: str = "HEAD"
) -> dict[str, Any]:
    started = time.monotonic()
    root = root.resolve()
    graph_file = graph_path if graph_path.is_absolute() else root / graph_path
    output = output_dir if output_dir.is_absolute() else root / output_dir
    graph = _load_graph(graph_file)

    source_commit = str(_run_git(root, "rev-parse", f"{ref}^{{commit}}")).strip()
    source_tree = str(_run_git(root, "rev-parse", f"{ref}^{{tree}}")).strip()
    commit_time = str(_run_git(root, "show", "-s", "--format=%cI", source_commit)).strip()
    graph_relative = graph_file.relative_to(root).as_posix()
    graph_oid = str(_run_git(root, "rev-parse", f"{ref}:{graph_relative}")).strip()

    tree_rows = _parse_tree(root, ref)
    blob_metadata = _read_blobs(root, (oid for _, _, oid in tree_rows))
    all_tree: dict[str, TreeBlob] = {}
    submodules: list[dict[str, str]] = []
    for path, mode, oid in tree_rows:
        if oid.startswith("SUBMODULE:"):
            submodules.append({"path": path, "mode": mode, "commit_oid": oid.split(":", 1)[1]})
            continue
        size, sha256 = blob_metadata[oid]
        all_tree[path] = TreeBlob(path=path, mode=mode, oid=oid, size=size, sha256=sha256)

    node_results: list[dict[str, Any]] = []
    globally_bound: dict[str, TreeBlob] = {}
    missing_configured_paths: list[dict[str, str]] = []
    for node in graph["nodes"]:
        ident = node["id"]
        configured_paths: list[str] = node["paths"]
        matched_paths: set[str] = set()
        missing: list[str] = []
        per_configured_path: list[dict[str, Any]] = []
        for configured in configured_paths:
            matches = sorted(path for path in all_tree if _matches(configured, path))
            if not matches:
                missing.append(configured)
                missing_configured_paths.append({"component_id": ident, "path": configured})
            matched_paths.update(matches)
            per_configured_path.append(
                {
                    "configured_path": configured,
                    "matched_file_count": len(matches),
                    "matched_files_digest": _canonical_digest(matches),
                }
            )
        files = [all_tree[path] for path in sorted(matched_paths)]
        for item in files:
            globally_bound[item.path] = item
        file_rows = [item.as_json() for item in files]
        if not configured_paths:
            status = "DECLARED_NO_IMPLEMENTATION_PATHS"
        elif missing:
            status = "INCOMPLETE_MISSING_CONFIGURED_PATH"
        elif not files:
            status = "INCOMPLETE_EMPTY_BINDING"
        else:
            status = "PATHS_AND_BYTES_BOUND"
        node_results.append(
            {
                "component_id": ident,
                "layer": node.get("layer"),
                "declared_status": node.get("status"),
                "declared_authority": node.get("authority"),
                "configured_paths": configured_paths,
                "configured_path_results": per_configured_path,
                "missing_configured_paths": missing,
                "file_count": len(files),
                "bytes": sum(item.size for item in files),
                "binding_digest": _canonical_digest(file_rows),
                "status": status,
                "files": file_rows,
            }
        )

    node_ids = {row["component_id"] for row in node_results}
    node_by_id = {row["component_id"]: row for row in node_results}
    dependency_edges: list[dict[str, Any]] = []
    for node in graph["nodes"]:
        for parent in node["depends_on"]:
            child_bound = node_by_id[node["id"]]["file_count"] > 0
            parent_bound = node_by_id[parent]["file_count"] > 0
            dependency_edges.append(
                {
                    "from_component": node["id"],
                    "to_dependency": parent,
                    "path_evidence_present": child_bound and parent_bound,
                    "typed_interface_status": "OPEN_REQUIRES_EXPLICIT_INTERFACE_WITNESS",
                    "authority_delta": "NONE",
                }
            )
    dependency_edges.sort(key=lambda row: (row["from_component"], row["to_dependency"]))

    global_rows = [globally_bound[path].as_json() for path in sorted(globally_bound)]
    content_complete = not missing_configured_paths and all(
        row["status"] in {"PATHS_AND_BYTES_BOUND", "DECLARED_NO_IMPLEMENTATION_PATHS"}
        for row in node_results
    )
    interfaces_complete = not dependency_edges
    terminal = (
        "V1_COMPONENT_GRAPH_CONTENT_AND_INTERFACES_BOUND"
        if content_complete and interfaces_complete
        else "V1_COMPONENT_GRAPH_PATHS_AND_BYTES_BOUND__INTERFACE_PROOF_OPEN"
        if content_complete
        else "V1_COMPONENT_GRAPH_CONTENT_BINDING_INCOMPLETE"
    )
    source = {
        "repository_root_name": root.name,
        "source_ref": ref,
        "source_commit": source_commit,
        "source_tree": source_tree,
        "source_commit_time": commit_time,
        "component_graph_path": graph_relative,
        "component_graph_blob_oid": graph_oid,
        "component_graph_sha256": hashlib.sha256(
            _run_git(root, "cat-file", "blob", graph_oid, text=False)
        ).hexdigest(),
    }
    primary = {
        "schema": SCHEMA,
        "source": source,
        "terminal": terminal,
        "content_complete": content_complete,
        "typed_interfaces_complete": interfaces_complete,
        "component_count": len(node_results),
        "dependency_edge_count": len(dependency_edges),
        "globally_bound_file_count": len(global_rows),
        "globally_bound_bytes": sum(row["bytes"] for row in global_rows),
        "global_binding_digest": _canonical_digest(global_rows),
        "missing_configured_paths": missing_configured_paths,
        "components": node_results,
        "dependency_edges": dependency_edges,
        "authority_ceiling": "GIT_OBJECT_AND_PATH_BINDING_ONLY_NO_THEOREM_INTERFACE_OR_SCIENTIFIC_AUTHORITY",
        "paper_authority_delta": "NONE",
    }
    raw_manifest = {
        "schema": "ORION.V1.ComponentRawManifest.v1",
        "source": source,
        "tree_blob_count": len(all_tree),
        "tree_submodule_count": len(submodules),
        "bound_file_count": len(global_rows),
        "bound_files": global_rows,
        "submodules": submodules,
        "manifest_digest": _canonical_digest(global_rows),
    }
    freeze = {
        "schema": "ORION.V1.ComponentBindingFreeze.v1",
        "source": source,
        "component_ids": sorted(node_ids),
        "component_count": len(node_ids),
        "configured_path_count": sum(len(node["paths"]) for node in graph["nodes"]),
        "working_tree_bytes_used": False,
        "paper_authority_delta": "NONE",
    }
    donor = {
        "schema": "ORION.V1.ComponentBindingDonor.v1",
        "authoritative_donor": "GIT_TREE_AND_BLOB_OBJECT_DATABASE",
        "why": "Git object identity, not the mutable checkout, defines the bound source bytes.",
        "donor_equivalence": "EXACT_FOR_PATH_AND_BYTE_IDENTITY",
        "not_established": ["typed interfaces", "theorem validity", "scientific validity", "external novelty"],
    }
    negative_controls = {
        "schema": "ORION.V1.ComponentBindingNegativeControls.v1",
        "registered_controls": [
            "unsafe absolute or parent-traversal path is rejected",
            "duplicate component identity is rejected",
            "unknown dependency identity is rejected",
            "configured path with no frozen-tree match remains incomplete",
            "working-tree mutation cannot change a HEAD binding",
            "overlapping component paths do not double-count the global manifest",
            "two runs on one source tree are byte-identical",
        ],
        "hostile_test_path": "tests/unit/orion_v1/test_component_binding_builder.py",
    }
    resource = {
        "schema": "ORION.V1.ComponentBindingResourceLedger.v1",
        "python": sys.version,
        "platform": platform.platform(),
        "git_version": str(_run_git(root, "--version")).strip(),
        "elapsed_seconds": round(time.monotonic() - started, 6),
        "unique_bound_blobs": len({row["blob_oid"] for row in global_rows}),
        "bound_bytes": sum(row["bytes"] for row in global_rows),
    }
    transfer = {
        "schema": "ORION.V1.ComponentBindingTransfer.v1",
        "component_graph_status_change": "PATH_AND_BYTE_EVIDENCE_ADDED",
        "typed_interface_status_change": "NONE",
        "scientific_authority_delta": "NONE",
        "publication_authority_delta": "NONE",
        "external_validation": "CANNOT_CHECK",
    }

    output.mkdir(parents=True, exist_ok=True)
    values = {
        "FREEZE.json": freeze,
        "RAW_MANIFEST.json": raw_manifest,
        "PRIMARY_RESULT.json": primary,
        "DONOR_RESULT.json": donor,
        "NEGATIVE_CONTROLS.json": negative_controls,
        "RESOURCE_LEDGER.json": resource,
        "TRANSFER_RESULT.json": transfer,
    }
    for name in PACKET_FILES:
        _write_json(output / name, values[name])
    file_bindings: list[dict[str, Any]] = []
    for name in PACKET_FILES:
        data = (output / name).read_bytes()
        file_bindings.append(
            {"path": name, "bytes": len(data), "sha256": hashlib.sha256(data).hexdigest()}
        )
    binding_packet = {
        "schema": PACKET_SCHEMA,
        "source": source,
        "terminal": terminal,
        "files": file_bindings,
        "packet_digest": _canonical_digest(file_bindings),
        "content_complete": content_complete,
        "typed_interfaces_complete": interfaces_complete,
        "paper_authority_delta": "NONE",
        "authority_ceiling": primary["authority_ceiling"],
    }
    _write_json(output / "RESULT_BINDING_PACKET.json", binding_packet)
    return binding_packet


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path.cwd())
    parser.add_argument("--graph", type=Path, default=DEFAULT_GRAPH)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--ref", default="HEAD")
    args = parser.parse_args(argv)
    try:
        packet = build_binding(
            root=args.root,
            graph_path=args.graph,
            output_dir=args.output_dir,
            ref=args.ref,
        )
    except BindingError as exc:
        print(f"ORION_V1_COMPONENT_BINDING_INVALID: {exc}", file=sys.stderr)
        return 1
    print(json.dumps(packet, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

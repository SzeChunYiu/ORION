#!/usr/bin/env python3
"""Content-bind every V1 component to the frozen Git tree (V1-COMPONENT-BIND-01).

Walks the frozen tree rather than the mutable working directory, and binds each
declared component path to an exact Git object id: a tree OID for a directory,
a blob OID plus SHA-256 for a file. Absent, ambiguous and duplicate ownership
are recorded separately rather than collapsed into a pass.

Every dependency edge must be backed by at least one concrete reference from
the dependent component's own files into the dependency's declared paths or
module names. Unbacked edges are marked open, never assumed.

Repairs nothing. Emits no scientific authority.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
from collections import defaultdict
from pathlib import Path
from typing import Any

GRAPH = Path("research/orion-v1-freeze/V1_COMPONENT_GRAPH_V1.json")
CODE_SUFFIXES = {".py", ".md", ".json", ".toml", ".yml", ".yaml", ".tex"}


def git(*args: str) -> str:
    return subprocess.run(["git", *args], capture_output=True, text=True, check=True).stdout


def tree_files(base: str) -> list[str]:
    return git("ls-tree", "-r", "--name-only", base).splitlines()


def object_id(base: str, path: str) -> str | None:
    r = subprocess.run(["git", "rev-parse", f"{base}:{path}"], capture_output=True, text=True)
    return r.stdout.strip() if r.returncode == 0 else None


def blob_sha256(base: str, path: str) -> str:
    raw = subprocess.run(["git", "show", f"{base}:{path}"], capture_output=True, check=True).stdout
    return hashlib.sha256(raw).hexdigest()


def module_tokens(paths: list[str]) -> set[str]:
    """Import-visible tokens a dependent would have to name to use this component."""
    out: set[str] = set()
    for p in paths:
        parts = [x for x in p.strip("/").split("/") if x]
        if not parts:
            continue
        leaf = parts[-1]
        out.add(leaf[:-3] if leaf.endswith(".py") else leaf)
        if "src" in parts and "orion" in parts:
            i = parts.index("orion")
            tail = parts[i + 1 :]
            if tail:
                out.add(tail[0].removesuffix(".py"))
    # A directory may be named orion-epistemic-state-v1 while the import is
    # orion.epistemic_state_v1. Matching one spelling only produces false
    # "unbacked" verdicts, so both separator forms are accepted.
    variants: set[str] = set()
    for t in out:
        variants.add(t)
        variants.add(t.replace("-", "_"))
        variants.add(t.replace("_", "-"))
        if t.startswith("orion-") or t.startswith("orion_"):
            variants.add(t[6:])
            variants.add(t[6:].replace("-", "_"))
    return {t for t in variants if len(t) > 3}


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--base", required=True)
    ap.add_argument("--out", type=Path, required=True)
    args = ap.parse_args()
    base = args.base

    graph = json.loads(GRAPH.read_text(encoding="utf-8"))
    files = tree_files(base)
    owners: dict[str, list[str]] = defaultdict(list)
    bound: dict[str, Any] = {}

    for node in graph["nodes"]:
        rows, absent = [], []
        for p in node["paths"]:
            oid = object_id(base, p.rstrip("/"))
            if oid is None:
                absent.append(p)
                continue
            if p.endswith("/"):
                members = [f for f in files if f.startswith(p)]
                for f in members:
                    owners[f].append(node["id"])
                rows.append({"path": p, "kind": "tree", "oid": oid, "files": len(members)})
            else:
                owners[p].append(node["id"])
                rows.append({"path": p, "kind": "blob", "oid": oid, "sha256": blob_sha256(base, p)})
        bound[node["id"]] = {"bindings": rows, "absent_paths": absent}

    duplicates = {f: sorted(set(o)) for f, o in owners.items() if len(set(o)) > 1}

    # Dependency edges: require a concrete reference, do not assume one.
    edges = []
    by_id = {n["id"]: n for n in graph["nodes"]}
    for node in graph["nodes"]:
        own = [f for f in files if any(f.startswith(p) or f == p.rstrip("/") for p in node["paths"])]
        own_code = [f for f in own if Path(f).suffix in CODE_SUFFIXES][:4000]
        for dep in node["depends_on"]:
            target = by_id.get(dep)
            if target is None:
                edges.append({"from": node["id"], "to": dep, "backed": False, "reason": "UNKNOWN_TARGET"})
                continue
            tokens = module_tokens(target["paths"]) | {p.rstrip("/") for p in target["paths"]}
            witness = None
            for f in own_code:
                try:
                    text = subprocess.run(["git", "show", f"{base}:{f}"], capture_output=True, check=True).stdout.decode("utf-8", "ignore")
                except subprocess.CalledProcessError:
                    continue
                hit = next((t for t in tokens if t and t in text), None)
                if hit:
                    witness = {"file": f, "token": hit}
                    break
            edges.append({
                "from": node["id"], "to": dep,
                "backed": witness is not None,
                "witness": witness,
                "reason": None if witness else ("NO_OWN_FILES" if not own_code else "NO_TYPED_INTERFACE_WITNESS"),
            })

    absent_nodes = sorted(k for k, v in bound.items() if v["absent_paths"])
    unimplemented = sorted(k for k, v in bound.items() if not v["bindings"])
    payload = {
        "schema": "ORION.V1.ComponentBinding.v1",
        "base_main": base,
        "components": bound,
        "duplicate_ownership": duplicates,
        "dependency_edges": edges,
        "summary": {
            "components": len(bound),
            "components_with_absent_paths": len(absent_nodes),
            "components_with_no_binding": len(unimplemented),
            "duplicate_owned_files": len(duplicates),
            "edges": len(edges),
            "edges_unbacked": sum(1 for e in edges if not e["backed"]),
        },
        "components_with_absent_paths": absent_nodes,
        "components_with_no_binding": unimplemented,
        "authority_delta": "NONE",
    }
    args.out.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(payload["summary"], indent=2, sort_keys=True))
    print("absent:", absent_nodes)
    print("no binding:", unimplemented)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

from __future__ import annotations

import importlib.util
import json
import subprocess
import sys
from pathlib import Path
from types import ModuleType
from typing import Any

import pytest

REPO_ROOT = Path(__file__).resolve().parents[3]
SCRIPT = REPO_ROOT / "scripts/build_orion_v1_component_binding.py"


def _load() -> ModuleType:
    spec = importlib.util.spec_from_file_location("orion_v1_component_binding", SCRIPT)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


BIND = _load()


def _git(root: Path, *args: str) -> str:
    completed = subprocess.run(
        ["git", "-C", str(root), *args],
        check=True,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    return completed.stdout.strip()


def _graph(*, missing: bool = False, traversal: bool = False, duplicate: bool = False) -> dict[str, Any]:
    path_a = "../outside" if traversal else ("missing.txt" if missing else "a.txt")
    nodes = [
        {
            "id": "A",
            "layer": "formalism",
            "paths": [path_a],
            "depends_on": [],
            "status": "TEST",
            "authority": "NONE",
        },
        {
            "id": "B",
            "layer": "implementation",
            "paths": ["src/"],
            "depends_on": ["A"],
            "status": "TEST",
            "authority": "NONE",
        },
        {
            "id": "C",
            "layer": "external_successor",
            "paths": [],
            "depends_on": ["B"],
            "status": "TEST",
            "authority": "NONE",
        },
    ]
    if duplicate:
        nodes.append(dict(nodes[0]))
    return {
        "schema": "ORION.V1.ComponentGraph.v1",
        "base_main": "0" * 40,
        "coverage": {"complete": False},
        "nodes": nodes,
    }


def _repo(tmp_path: Path, graph: dict[str, Any] | None = None) -> Path:
    root = tmp_path / "repo"
    root.mkdir()
    _git(root, "init")
    _git(root, "config", "user.email", "orion-test@example.invalid")
    _git(root, "config", "user.name", "ORION test")
    (root / "a.txt").write_text("alpha\n", encoding="utf-8")
    (root / "src").mkdir()
    (root / "src/one.py").write_text("VALUE = 1\n", encoding="utf-8")
    (root / "src/two.py").write_text("VALUE = 2\n", encoding="utf-8")
    graph_path = root / "research/orion-v1-freeze/V1_COMPONENT_GRAPH_V1.json"
    graph_path.parent.mkdir(parents=True)
    graph_path.write_text(
        json.dumps(_graph() if graph is None else graph, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    _git(root, "add", ".")
    _git(root, "commit", "-m", "fixture")
    return root


def _read(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def test_binds_frozen_git_objects_not_working_tree(tmp_path: Path) -> None:
    root = _repo(tmp_path)
    committed = (root / "a.txt").read_bytes()
    (root / "a.txt").write_text("uncommitted drift\n", encoding="utf-8")
    output = root / "out"

    packet = BIND.build_binding(
        root=root,
        graph_path=Path("research/orion-v1-freeze/V1_COMPONENT_GRAPH_V1.json"),
        output_dir=output,
    )

    primary = _read(output / "PRIMARY_RESULT.json")
    row = next(item for item in primary["components"] if item["component_id"] == "A")
    assert row["files"][0]["sha256"] == BIND.hashlib.sha256(committed).hexdigest()
    assert row["files"][0]["sha256"] != BIND.hashlib.sha256(b"uncommitted drift\n").hexdigest()
    assert packet["terminal"] == "V1_COMPONENT_GRAPH_PATHS_AND_BYTES_BOUND__INTERFACE_PROOF_OPEN"
    assert packet["content_complete"] is True
    assert packet["typed_interfaces_complete"] is False


def test_overlapping_paths_do_not_double_count_global_manifest(tmp_path: Path) -> None:
    graph = _graph()
    graph["nodes"][0]["paths"] = ["src/one.py"]
    graph["nodes"][1]["paths"] = ["src/"]
    root = _repo(tmp_path, graph)
    output = root / "out"
    BIND.build_binding(root=root, graph_path=Path("research/orion-v1-freeze/V1_COMPONENT_GRAPH_V1.json"), output_dir=output)
    raw = _read(output / "RAW_MANIFEST.json")
    assert raw["bound_file_count"] == 2
    assert [row["path"] for row in raw["bound_files"]] == ["src/one.py", "src/two.py"]


def test_two_runs_are_byte_identical(tmp_path: Path) -> None:
    root = _repo(tmp_path)
    first = root / "out-a"
    second = root / "out-b"
    BIND.build_binding(root=root, graph_path=Path("research/orion-v1-freeze/V1_COMPONENT_GRAPH_V1.json"), output_dir=first)
    BIND.build_binding(root=root, graph_path=Path("research/orion-v1-freeze/V1_COMPONENT_GRAPH_V1.json"), output_dir=second)
    first_files = sorted(path.name for path in first.iterdir())
    second_files = sorted(path.name for path in second.iterdir())
    assert first_files == second_files
    for name in first_files:
        assert (first / name).read_bytes() == (second / name).read_bytes(), name


def test_missing_configured_path_fails_closed(tmp_path: Path) -> None:
    root = _repo(tmp_path, _graph(missing=True))
    output = root / "out"
    packet = BIND.build_binding(root=root, graph_path=Path("research/orion-v1-freeze/V1_COMPONENT_GRAPH_V1.json"), output_dir=output)
    primary = _read(output / "PRIMARY_RESULT.json")
    assert packet["terminal"] == "V1_COMPONENT_GRAPH_CONTENT_BINDING_INCOMPLETE"
    assert packet["content_complete"] is False
    assert primary["missing_configured_paths"] == [{"component_id": "A", "path": "missing.txt"}]


@pytest.mark.parametrize(
    ("graph", "message"),
    [
        (_graph(traversal=True), "unsafe repository path"),
        (_graph(duplicate=True), "duplicate component id"),
    ],
)
def test_malformed_graph_is_rejected(tmp_path: Path, graph: dict[str, Any], message: str) -> None:
    root = _repo(tmp_path, graph)
    with pytest.raises(BIND.BindingError, match=message):
        BIND.build_binding(
            root=root,
            graph_path=Path("research/orion-v1-freeze/V1_COMPONENT_GRAPH_V1.json"),
            output_dir=root / "out",
        )

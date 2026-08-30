#!/usr/bin/env python3
"""Prospectively frozen ORION-01 Round-2 study: pinned PyZX atomic
checker-guarded move registry.

Round 1 (r11-pyzx-full-reduce) bound the twelve ``full_reduce`` automatic
macros and failed: the batch matchers mutate the graph during matching, so a
detached macro invocation is not a sound freely-reorderable move.  Round 2
binds the same production system at the granularity the source itself exposes
for manual targeting: one move is ONE application of an official site-guarded
rewrite primitive (``Rewrite*.apply`` at one site, or one whole-graph official
call) evaluated on the current graph at application time.  Guards are the pure
``check_*`` predicates of the pinned source.

The three frozen arms per word are the unmodified production ``full_reduce``
(native), exhaustive breadth-first search over the atomic registry
(certificate), and a seeded random-restart resource-greedy search (generic
control).  Nothing in this module treats the registry as all of PyZX or all of
the ZX calculus.  See ORION01_ROUND2_ATOMIC_PROTOCOL.md before using any
result.
"""

from __future__ import annotations

import argparse
import ast
from collections import Counter, deque
from dataclasses import dataclass
import hashlib
import importlib.metadata
import itertools
import json
import os
from pathlib import Path
import subprocess
import time
from typing import Any, Callable, Iterable, Mapping, Sequence

import numpy as np
import pyzx
from pyzx import Circuit
from pyzx.graph.base import BaseGraph
from pyzx.graph.jsonparser import json_to_graph
from pyzx.utils import VertexType


HERE = Path(__file__).resolve().parent
REPO_ROOT = HERE.parents[3]
REGISTRY_PATH = HERE / "ORION01_ROUND2_ATOMIC_SOURCE_REGISTRY.json"
PROTOCOL_PATH = HERE / "ORION01_ROUND2_ATOMIC_PROTOCOL.md"
RESULTS_PATH = HERE / "ORION01_ROUND2_ATOMIC_RESULTS.json"
SUBSET_RESULTS_PATH = HERE / "ORION01_ROUND2_ATOMIC_RESULTS_SUBSET.json"
PILOT_PATH = HERE / "ORION01_ROUND2_ATOMIC_PILOT_LOG.json"
REQUIREMENTS_PATH = HERE / "requirements-lock.txt"

EXPECTED_COMMIT = "dade7d46f193635bbdaefd8fcde837f9449fddc5"
EXPECTED_VERSION = "0.10.5"

FAIL_TERMINAL = "CANNOT_CHECK_MOVE_COMPLETENESS"
POSITIVE_TERMINAL = "AB_R2_ATOMIC_CHECKER_REGISTRY_REALIZED_GAP"
NULL_TERMINAL = "AB_R2_ATOMIC_CHECKER_REGISTRY_NO_STRICT_GAP"
GENERIC_TERMINAL = "AB_R2_GAP_MATCHED_BY_GENERIC_SEARCH"
CROSS_TERMINAL = "AB_R2_CROSS_MOVE_COLLAPSES_GAP"

PRIMARY_MAX_LENGTH = 3
PROBE_LENGTH = 6
PROBE_WORD_COUNT = 16
GENERIC_RESTARTS = 4
GENERIC_EPSILON = 0.25
GENERIC_SEED_MULTIPLIER = 1000003
GENERIC_SEED_OFFSET = 7

# Mutating BaseGraph / scalar method names.  Any call to one of these inside a
# function body marks that function as a mutator for the structural audits.
MUTATING_METHODS = frozenset(
    {
        "add_vertex",
        "add_vertices",
        "add_edge",
        "add_edges",
        "add_edge_table",
        "remove_vertex",
        "remove_vertices",
        "remove_edge",
        "remove_edges",
        "remove_isolated_vertices",
        "remove_tadholes",
        "set_phase",
        "add_to_phase",
        "set_type",
        "set_qubit",
        "set_row",
        "update_phase_index",
        "fuse_phases",
        "phase_negate",
        "add_power",
        "add_phase",
        "add_node",
        "add_bound",
        "multiply_int",
        "set_ground",
        "set_vdata",
    }
)

# Official graph-level primitives (not Rewrite objects).
GRAPH_OFFICIALS = ("to_gh", "remove_isolated_vertices")


class StudyFailure(RuntimeError):
    """Fail-closed scientific prerequisite failure."""


def canonical_json(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True)


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def sha256_text(value: str) -> str:
    return sha256_bytes(value.encode("utf-8"))


def load_registry(path: Path = REGISTRY_PATH) -> dict[str, Any]:
    row = json.loads(path.read_text(encoding="utf-8"))
    if row["schema"] != "ORION.ORION01.Round2.PyZXAtomicCheckerSourceRegistry.v1":
        raise StudyFailure("unexpected source-registry schema")
    return row


def pyzx_source_root() -> Path:
    return Path(pyzx.__file__).resolve().parent.parent


def _direct_url_record() -> dict[str, Any]:
    dist = importlib.metadata.distribution("pyzx")
    direct = dist.read_text("direct_url.json")
    if direct is None:
        raise StudyFailure("installed PyZX has no direct_url.json commit binding")
    return json.loads(direct)


def verify_installed_source(registry: Mapping[str, Any]) -> dict[str, Any]:
    source = registry["source"]
    if pyzx.__version__ != source["version"] or pyzx.__version__ != EXPECTED_VERSION:
        raise StudyFailure(f"PyZX version mismatch: {pyzx.__version__}")

    direct = _direct_url_record()
    vcs = direct.get("vcs_info", {})
    if direct.get("url") != "https://github.com/zxcalc/pyzx.git":
        raise StudyFailure(f"unexpected PyZX direct URL: {direct.get('url')}")
    if vcs.get("commit_id") != EXPECTED_COMMIT:
        raise StudyFailure(f"unexpected PyZX commit: {vcs.get('commit_id')}")
    if vcs.get("requested_revision") != EXPECTED_COMMIT:
        raise StudyFailure("PyZX requested revision is not the frozen full commit")

    root = pyzx_source_root()
    checked: list[dict[str, str]] = []
    for item in source["source_files"]:
        path = root / item["path"]
        if not path.is_file():
            raise StudyFailure(f"missing pinned source file: {item['path']}")
        actual = sha256_bytes(path.read_bytes())
        if actual != item["sha256"]:
            raise StudyFailure(f"source digest mismatch: {item['path']}")
        checked.append({"path": item["path"], "sha256": actual})

    return {
        "direct_url": direct["url"],
        "commit": vcs["commit_id"],
        "requested_revision": vcs["requested_revision"],
        "version": pyzx.__version__,
        "source_files_checked": len(checked),
        "source_file_manifest_sha256": sha256_text(canonical_json(checked)),
    }


# ---------------------------------------------------------------------------
# Static AST audits (structural, never outcome-based)
# ---------------------------------------------------------------------------


def _function_nodes(tree: ast.AST) -> dict[str, ast.FunctionDef | ast.AsyncFunctionDef]:
    return {
        node.name: node
        for node in tree.body  # type: ignore[attr-defined]
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))
    }


def _called_symbols(node: ast.AST) -> set[str]:
    calls: set[str] = set()
    for child in ast.walk(node):
        if not isinstance(child, ast.Call):
            continue
        fn = child.func
        if isinstance(fn, ast.Name):
            calls.add(fn.id)
        elif isinstance(fn, ast.Attribute):
            calls.add(fn.attr)
    return calls


def _method_calls(node: ast.AST) -> set[str]:
    methods: set[str] = set()
    for child in ast.walk(node):
        if isinstance(child, ast.Call) and isinstance(child.func, ast.Attribute):
            methods.add(child.func.attr)
    return methods


def _parse_module(relative: str) -> ast.AST:
    path = pyzx_source_root() / relative
    if not path.is_file():
        raise StudyFailure(f"missing pinned module for AST audit: {relative}")
    return ast.parse(path.read_text(encoding="utf-8"), filename=str(path))


class SourceModel:
    """Name-resolved static model of the pinned modules used by the audits."""

    AUDIT_MODULES = (
        "pyzx/simplify.py",
        "pyzx/rewrite_rules/fuse_rule.py",
        "pyzx/rewrite_rules/self_loops_rule.py",
        "pyzx/rewrite_rules/remove_id_rule.py",
        "pyzx/rewrite_rules/pivot_rule.py",
        "pyzx/rewrite_rules/lcomp_rule.py",
        "pyzx/rewrite_rules/merge_phase_gadget_rule.py",
        "pyzx/rewrite_rules/copy_rule.py",
        "pyzx/rewrite_rules/supplementarity_rule.py",
        "pyzx/rewrite_rules/bialgebra_rule.py",
        "pyzx/rewrite_rules/hopf_rule.py",
    )

    def __init__(self) -> None:
        self.functions: dict[str, ast.FunctionDef | ast.AsyncFunctionDef] = {}
        self.function_module: dict[str, str] = {}
        # rewrite-object name -> component function names it dispatches to
        self.objects: dict[str, set[str]] = {}
        self.object_rmv_isolated: dict[str, bool] = {}
        for relative in self.AUDIT_MODULES:
            tree = _parse_module(relative)
            for name, node in _function_nodes(tree).items():
                if name in self.functions:
                    raise StudyFailure(f"ambiguous function name across pinned modules: {name}")
                self.functions[name] = node
                self.function_module[name] = relative
            for node in tree.body:  # type: ignore[attr-defined]
                targets: list[ast.Name] = []
                value: ast.expr | None = None
                if isinstance(node, ast.Assign):
                    targets = [t for t in node.targets if isinstance(t, ast.Name)]
                    value = node.value
                elif isinstance(node, ast.AnnAssign):
                    if isinstance(node.target, ast.Name):
                        targets = [node.target]
                    value = node.value
                if value is None or not isinstance(value, ast.Call):
                    continue
                if not isinstance(value.func, ast.Name) or not value.func.id.startswith("Rewrite"):
                    continue
                if len(targets) != 1:
                    continue
                obj_name = targets[0].id
                components: set[str] = set()
                rmv_isolated = False
                for arg in value.args:
                    if isinstance(arg, ast.Name):
                        components.add(arg.id)
                for keyword in value.keywords:
                    if keyword.arg == "simp_override" and isinstance(keyword.value, ast.Name):
                        components.add(keyword.value.id)
                    if keyword.arg == "rmv_isolated" and isinstance(keyword.value, ast.Constant):
                        rmv_isolated = bool(keyword.value.value)
                if obj_name in self.objects:
                    raise StudyFailure(f"duplicate rewrite object definition: {obj_name}")
                self.objects[obj_name] = components
                self.object_rmv_isolated[obj_name] = rmv_isolated

    def _components(self, name: str) -> set[str]:
        """Resolve a called name to the pinned symbols it dispatches to."""
        if name in self.functions:
            return {name}
        if name in self.objects:
            out = set(self.objects[name])
            if self.object_rmv_isolated.get(name):
                out.add("remove_isolated_vertices")
            return out
        return set()

    def call_closure(self, roots: Sequence[str]) -> set[str]:
        """Transitive closure over pinned functions and rewrite objects."""
        seen: set[str] = set()
        todo = list(roots)
        while todo:
            name = todo.pop()
            if name in seen:
                continue
            seen.add(name)
            if name in self.functions:
                todo.extend(sorted(_called_symbols(self.functions[name])))
            elif name in self.objects:
                todo.extend(sorted(self._components(name)))
        return seen

    def mutator_method_surface(self, names: Iterable[str]) -> set[str]:
        surface: set[str] = set()
        for name in names:
            if name == "remove_isolated_vertices":
                surface.add("remove_isolated_vertices")
                continue
            if name in self.functions:
                surface |= _method_calls(self.functions[name]) & MUTATING_METHODS
        return surface

    def is_mutating_function(self, name: str) -> bool:
        if name == "remove_isolated_vertices":
            return True
        if name not in self.functions:
            return False
        return bool(_method_calls(self.functions[name]) & MUTATING_METHODS)


def derive_source_audits(registry: Mapping[str, Any]) -> dict[str, Any]:
    model = SourceModel()

    schemas = registry["registered_schemas"]
    official_by_schema = {row["id"]: row["official_object"] for row in schemas}
    # The registry stores dotted official objects; map them onto the source
    # symbol names used by the static model.
    official_symbol = {
        "PYZX.R2.01": "fuse_simp",
        "PYZX.R2.02": "remove_self_loop_simp",
        "PYZX.R2.03": "to_gh",
        "PYZX.R2.04": "id_simp",
        "PYZX.R2.05": "pivot_simp",
        "PYZX.R2.06": "lcomp_simp",
        "PYZX.R2.07": "pivot_boundary_simp",
        "PYZX.R2.08": "pivot_gadget_simp",
        "PYZX.R2.09": "gadget_simp",
        "PYZX.R2.10": "copy_simp",
        "PYZX.R2.11": "supplementarity_simp",
        "PYZX.R2.12": "remove_isolated_vertices",
    }
    if set(official_symbol) != set(official_by_schema):
        raise StudyFailure("registry schema ids differ from the frozen audit mapping")

    closure_fr = model.call_closure(["full_reduce"])

    # Audit 1: primitive-closure equality.
    derived_primitives = {
        name for name in closure_fr if name in model.objects or name in GRAPH_OFFICIALS
    }
    registered = set(official_symbol.values())
    if derived_primitives != registered:
        raise StudyFailure(
            "primitive closure equality failed: "
            f"derived={sorted(derived_primitives)} registered={sorted(registered)}"
        )
    omissions: list[dict[str, Any]] = []
    for schema_id, symbol in official_symbol.items():
        mutated = registered - {symbol}
        rejected = mutated != derived_primitives
        if not rejected:
            raise StudyFailure(f"hostile schema omission accepted: {schema_id}")
        omissions.append({"omitted_schema": schema_id, "omitted_symbol": symbol, "rejected": rejected})

    # Audit 2: mutator-method surface inclusion (production covered by routes).
    route_closures: dict[str, set[str]] = {}
    for schema_id, row in zip(official_symbol, schemas):
        symbol = official_symbol[schema_id]
        if symbol in model.objects:
            components = set(model.objects[symbol])
            # The manual-target apply route: guard + applier (+ isolated cleanup).
            if model.object_rmv_isolated.get(symbol):
                components.add("remove_isolated_vertices")
        elif symbol == "to_gh":
            components = {"to_gh"}
        else:
            components = {"remove_isolated_vertices"}
        route_closures[schema_id] = model.call_closure(sorted(components))

    fr_surface = model.mutator_method_surface(closure_fr)
    route_surface: set[str] = set()
    for closure in route_closures.values():
        route_surface |= model.mutator_method_surface(closure)
    uncovered = sorted(fr_surface - route_surface)
    if uncovered:
        raise StudyFailure(f"mutator method surface not covered by atomic routes: {uncovered}")

    # Audit 3: guard purity.
    impure: list[str] = []
    for guard in registry["guard_purity_symbols"]:
        guard_closure = model.call_closure([guard])
        surface = model.mutator_method_surface(guard_closure)
        if surface:
            impure.append(guard)
    if impure:
        raise StudyFailure(f"registered guards are not pure: {impure}")

    # Audit 4: runtime binding of audited source to executed objects.
    binding: dict[str, Any] = {}
    import pyzx.rewrite_rules.fuse_rule as fuse_rule
    import pyzx.rewrite_rules.self_loops_rule as self_loops_rule
    import pyzx.rewrite_rules.remove_id_rule as remove_id_rule
    import pyzx.rewrite_rules.pivot_rule as pivot_rule
    import pyzx.rewrite_rules.lcomp_rule as lcomp_rule
    import pyzx.rewrite_rules.copy_rule as copy_rule
    import pyzx.rewrite_rules.merge_phase_gadget_rule as merge_rule
    import pyzx.rewrite_rules.supplementarity_rule as supp_rule

    def _require(condition: bool, message: str) -> None:
        if not condition:
            raise StudyFailure(f"runtime binding failed: {message}")

    simplify = pyzx.simplify
    _require(simplify.fuse_simp.is_match is fuse_rule.check_fuse, "fuse_simp.is_match")
    _require(simplify.fuse_simp.applier is fuse_rule.unsafe_fuse, "fuse_simp.applier")
    _require(bool(simplify.fuse_simp.rmv_isolated), "fuse_simp.rmv_isolated")
    _require(simplify.remove_self_loop_simp.is_match is self_loops_rule.check_self_loop, "remove_self_loop_simp.is_match")
    _require(simplify.remove_self_loop_simp.applier is self_loops_rule.unsafe_remove_self_loop, "remove_self_loop_simp.applier")
    _require(simplify.id_simp.is_match is remove_id_rule.check_remove_id, "id_simp.is_match")
    _require(simplify.id_simp.applier is remove_id_rule.unsafe_remove_id, "id_simp.applier")
    _require(simplify.pivot_simp.is_match is pivot_rule.check_pivot, "pivot_simp.is_match")
    _require(simplify.pivot_simp.applier is pivot_rule.unsafe_pivot, "pivot_simp.applier")
    _require(simplify.lcomp_simp.is_match is lcomp_rule.check_lcomp, "lcomp_simp.is_match")
    _require(simplify.lcomp_simp.applier is lcomp_rule.unsafe_lcomp, "lcomp_simp.applier")
    _require(simplify.pivot_boundary_simp.is_match is pivot_rule.check_pivot_boundary, "pivot_boundary_simp.is_match")
    _require(simplify.pivot_boundary_simp.applier is pivot_rule.unsafe_pivot_boundary, "pivot_boundary_simp.applier")
    _require(simplify.pivot_boundary_simp.simp_override is pivot_rule.pivot_boundary_for_simp, "pivot_boundary_simp.simp_override")
    _require(simplify.pivot_boundary_simp.is_ordered, "pivot_boundary_simp.is_ordered")
    _require(simplify.pivot_gadget_simp.is_match is pivot_rule.check_pivot_gadget, "pivot_gadget_simp.is_match")
    _require(simplify.pivot_gadget_simp.applier is pivot_rule.unsafe_pivot_gadget, "pivot_gadget_simp.applier")
    _require(simplify.pivot_gadget_simp.simp_override is pivot_rule.pivot_gadget_for_simp, "pivot_gadget_simp.simp_override")
    _require(simplify.pivot_gadget_simp.is_ordered, "pivot_gadget_simp.is_ordered")
    _require(simplify.gadget_simp.applier is merge_rule.merge_phase_gadgets_for_apply, "gadget_simp.applier")
    _require(simplify.copy_simp.is_match is copy_rule.check_copy, "copy_simp.is_match")
    _require(simplify.copy_simp.applier is copy_rule.unsafe_copy, "copy_simp.applier")
    _require(simplify.supplementarity_simp.applier is supp_rule.safe_apply_supplementarity, "supplementarity_simp.applier")
    _require(callable(simplify.to_gh), "to_gh callable")
    binding["checked_relations"] = 25
    binding["apply_routes_distinct_from_batch_simp"] = [
        "pivot_boundary_simp",
        "pivot_gadget_simp",
    ]
    binding["mutating_batch_matchers_reachable_from_full_reduce"] = sorted(
        name
        for name in closure_fr
        if model.is_mutating_function(name) and name.startswith("match_")
    )

    mutators_in_fr = sorted(name for name in closure_fr if model.is_mutating_function(name) or name == "remove_isolated_vertices")
    return {
        "observed_full_reduce_closure_size": len(closure_fr),
        "derived_official_primitives": sorted(derived_primitives),
        "registered_official_symbols": sorted(registered),
        "primitive_closure_exact": True,
        "hostile_single_omissions": omissions,
        "hostile_omissions_rejected": sum(int(x["rejected"]) for x in omissions),
        "full_reduce_mutator_method_surface": sorted(fr_surface),
        "atomic_route_union_mutator_method_surface": sorted(route_surface),
        "mutator_method_surface_uncovered": uncovered,
        "mutator_method_surface_covered": not uncovered,
        "mutating_functions_in_full_reduce_closure": mutators_in_fr,
        "guard_purity_symbols_checked": list(registry["guard_purity_symbols"]),
        "guard_purity_all_pure": not impure,
        "runtime_binding": binding,
    }


# ---------------------------------------------------------------------------
# Frozen task domain
# ---------------------------------------------------------------------------

GATE_ALPHABET = ("H0", "H1", "S0", "S1", "T0", "T1", "CX01", "CX10")


def primary_words() -> list[tuple[str, ...]]:
    words: list[tuple[str, ...]] = []
    for length in range(PRIMARY_MAX_LENGTH + 1):
        words.extend(itertools.product(GATE_ALPHABET, repeat=length))
    return words


def probe_words() -> list[tuple[str, ...]]:
    return list(itertools.islice(itertools.product(GATE_ALPHABET, repeat=PROBE_LENGTH), PROBE_WORD_COUNT))


def circuit_from_word(word: Sequence[str]) -> Circuit:
    circuit = Circuit(2)
    for token in word:
        if token[0] in {"H", "S", "T"}:
            name = {"H": "HAD", "S": "S", "T": "T"}[token[0]]
            circuit.add_gate(name, int(token[1]))
        elif token == "CX01":
            circuit.add_gate("CNOT", 0, 1)
        elif token == "CX10":
            circuit.add_gate("CNOT", 1, 0)
        else:  # pragma: no cover - frozen alphabet makes this unreachable
            raise StudyFailure(f"unknown frozen gate token: {token}")
    return circuit


def source_graph_state(graph: BaseGraph[Any, Any]) -> str:
    """Lossless deterministic JSON while preserving operational vertex ids."""

    return canonical_json(graph.to_dict(include_scalar=True))


def canonical_state(graph: BaseGraph[Any, Any]) -> str:
    """Canonical compacted state: pyzx ``copy()`` renumbers vertices to
    consecutive ids (documented pyzx behaviour), then the lossless
    deterministic JSON is taken.

    Vertex-removing official routes leave id gaps in place, and two histories
    reaching the same abstract graph can carry different id labellings; routing
    every *produced* state through pyzx's own compaction removes that id
    history from state identity without touching the frozen serialization
    (``to_dict(include_scalar=True)``) or any official route.
    """

    return source_graph_state(graph.copy())


def graph_from_state(state: str) -> BaseGraph[Any, Any]:
    return json_to_graph(json.loads(state))


def start_state_from_word(word: Sequence[str]) -> str:
    graph = circuit_from_word(word).to_graph()
    if any(graph.type(v) == VertexType.H_BOX for v in graph.vertices()):
        raise StudyFailure(f"frozen circuit generated forbidden H-box: {word}")
    return canonical_state(graph)


def resource(graph: BaseGraph[Any, Any]) -> tuple[int, int, int]:
    non_boundary = sum(graph.type(v) != VertexType.BOUNDARY for v in graph.vertices())
    return (pyzx.simplify.tcount(graph), non_boundary, graph.num_edges())


def structural_measure(graph: BaseGraph[Any, Any]) -> tuple[int, int, int]:
    x_vertices = sum(graph.type(v) == VertexType.X for v in graph.vertices())
    return (graph.num_vertices(), x_vertices, graph.num_edges())


def dense_matrix(state: str) -> np.ndarray[Any, np.dtype[np.complexfloating[Any, Any]]]:
    graph = graph_from_state(state)
    return np.asarray(graph.to_matrix(preserve_scalar=True), dtype=np.complex128)


def matrices_equal(left: np.ndarray[Any, Any], right: np.ndarray[Any, Any]) -> bool:
    return left.shape == right.shape and bool(
        np.allclose(left, right, rtol=1e-9, atol=1e-9, equal_nan=False)
    )


# ---------------------------------------------------------------------------
# Atomic move machinery: one move = one official site-guarded application
# ---------------------------------------------------------------------------

Site = tuple[int, ...]  # () = whole graph, (v,) = vertex site, (a, b) = ordered pair


class GuardUnsound(StudyFailure):
    """A legal atomic move changed the dense map: terminal AB_R2_ATOMIC_GUARD_UNSOUND."""


class CapExceeded(StudyFailure):
    """Fail-closed per-input state cap reached inside the primary domain."""


def _is_non_clifford(graph: BaseGraph[Any, Any], vertex: int) -> bool:
    phase = graph.phase(vertex)
    denominator = getattr(phase, "denominator", 1)
    return phase != 0 and denominator > 2


def _enum_all_vertices(graph: BaseGraph[Any, Any]) -> list[Site]:
    return sorted((v,) for v in graph.vertices())


def _enum_ordered_edge_pairs(graph: BaseGraph[Any, Any]) -> list[Site]:
    pairs: list[Site] = []
    for v in graph.vertices():
        for w in graph.neighbors(v):
            if v != w:
                pairs.append((v, w))
    return sorted(set(pairs))


def _enum_gadget_leaf_pairs(graph: BaseGraph[Any, Any]) -> list[Site]:
    leaves = sorted(
        v for v in graph.vertices() if _is_non_clifford(graph, v) and len(list(graph.neighbors(v))) == 1
    )
    return [(a, b) for a in leaves for b in leaves if a != b]


def _enum_nonclifford_pairs(graph: BaseGraph[Any, Any]) -> list[Site]:
    nodes = sorted(v for v in graph.vertices() if _is_non_clifford(graph, v))
    return [(a, b) for a in nodes for b in nodes if a != b]


def _enum_whole_graph(graph: BaseGraph[Any, Any]) -> list[Site]:
    return [()]


def _apply_to_gh(graph: BaseGraph[Any, Any], site: Site) -> bool:
    # Graph-level official call: it always runs; legality is state difference.
    pyzx.simplify.to_gh(graph)
    return True


def _apply_remove_isolated(graph: BaseGraph[Any, Any], site: Site) -> bool:
    graph.remove_isolated_vertices()
    return True


def _apply_gadget_merge(graph: BaseGraph[Any, Any], site: Site) -> bool:
    return bool(pyzx.simplify.gadget_simp.apply(graph, list(site)))


def _apply_supplementarity(graph: BaseGraph[Any, Any], site: Site) -> bool:
    return bool(pyzx.simplify.supplementarity_simp.apply(graph, list(site)))


def _pair_route(obj: Any) -> Callable[[BaseGraph[Any, Any], Site], bool]:
    def route(graph: BaseGraph[Any, Any], site: Site) -> bool:
        return bool(obj.apply(graph, site[0], site[1]))

    return route


def _vertex_route(obj: Any) -> Callable[[BaseGraph[Any, Any], Site], bool]:
    def route(graph: BaseGraph[Any, Any], site: Site) -> bool:
        return bool(obj.apply(graph, site[0]))

    return route


def atomic_move_table() -> dict[str, dict[str, Any]]:
    """Frozen schema id -> site enumerator and official applicator."""

    simplify = pyzx.simplify
    table: dict[str, dict[str, Any]] = {
        "PYZX.R2.01": {"enumerator": _enum_ordered_edge_pairs, "applicator": _pair_route(simplify.fuse_simp)},
        "PYZX.R2.02": {"enumerator": _enum_all_vertices, "applicator": _vertex_route(simplify.remove_self_loop_simp)},
        "PYZX.R2.03": {"enumerator": _enum_whole_graph, "applicator": _apply_to_gh},
        "PYZX.R2.04": {"enumerator": _enum_all_vertices, "applicator": _vertex_route(simplify.id_simp)},
        "PYZX.R2.05": {"enumerator": _enum_ordered_edge_pairs, "applicator": _pair_route(simplify.pivot_simp)},
        "PYZX.R2.06": {"enumerator": _enum_all_vertices, "applicator": _vertex_route(simplify.lcomp_simp)},
        "PYZX.R2.07": {"enumerator": _enum_ordered_edge_pairs, "applicator": _pair_route(simplify.pivot_boundary_simp)},
        "PYZX.R2.08": {"enumerator": _enum_ordered_edge_pairs, "applicator": _pair_route(simplify.pivot_gadget_simp)},
        "PYZX.R2.09": {"enumerator": _enum_gadget_leaf_pairs, "applicator": _apply_gadget_merge},
        "PYZX.R2.10": {"enumerator": _enum_all_vertices, "applicator": _vertex_route(simplify.copy_simp)},
        "PYZX.R2.11": {"enumerator": _enum_nonclifford_pairs, "applicator": _apply_supplementarity},
        "PYZX.R2.12": {"enumerator": _enum_whole_graph, "applicator": _apply_remove_isolated},
    }
    return table


def hostile_extension_map() -> dict[str, Callable[[BaseGraph[Any, Any]], Any]]:
    simplify = pyzx.simplify
    return {
        "bialg_simp": simplify.bialg_simp,
        "hopf_simp": simplify.hopf_simp,
        "gadget_phasepoly_simp": simplify.gadget_phasepoly_simp,
    }


def attempt_atomic_move(
    base: BaseGraph[Any, Any], move: Mapping[str, Any], site: Site
) -> str | None:
    """Apply the official route at one site on a private copy of ``base``.

    Site ids are enumerated on ``base``; the copy is asserted to preserve them
    (``copy()`` preserves operational ids; ``to_dict``/``json_to_graph``
    round-trip ids verbatim, including gaps left by vertex-removing official
    routes, so ids agree across serialization).
    Returns the successor state, or None when the move is not legal (official
    route declined or the canonical state is unchanged).  ``None``-moves may
    still have mutated the private copy (the gadget-merge matcher absorbs axel
    phases while matching); that is exactly why every attempt runs on a copy.
    """

    graph = base.copy()
    if list(graph.vertices()) != list(base.vertices()):
        raise StudyFailure("graph copy does not preserve operational vertex ids")
    try:
        applied = move["applicator"](graph, site)
    except Exception as exc:  # official route raised: fail closed
        raise StudyFailure(
            f"official route raised for site {site}: {type(exc).__name__}: {exc}"
        ) from exc
    if not applied:
        return None
    successor = canonical_state(graph)
    return successor if successor != source_graph_state_cached(base) else None


_BASE_STATE_ATTR = "_orion_state_json"


def source_graph_state_cached(base: BaseGraph[Any, Any]) -> str:
    cached = getattr(base, _BASE_STATE_ATTR, None)
    if cached is None:
        cached = source_graph_state(base)
        try:
            setattr(base, _BASE_STATE_ATTR, cached)
        except Exception:
            return cached
    return cached


# ---------------------------------------------------------------------------
# Certificate arm: exhaustive BFS over the atomic registry
# ---------------------------------------------------------------------------


class AtomicExplorer:
    """Per-word exhaustive explorer over the registered atomic moves.

    Every expansion runs each official route on a private graph copy (several
    official matchers mutate the graph while matching); a move counts only when
    the official route accepts AND the lossless canonical state differs.
    """

    def __init__(
        self,
        start: str,
        moves: Mapping[str, Mapping[str, Any]],
        cap: int,
        check_semantics: bool,
    ) -> None:
        self.start = start
        self.moves = dict(moves)
        self.cap = cap
        self.check_semantics = check_semantics
        self.schema_order = sorted(self.moves)
        self.expansions: dict[str, dict[str, dict[Site, str]]] = {}
        self.parents: dict[str, tuple[str, str, Site] | None] = {start: None}
        self.transitions = 0
        self.attempts = 0
        self.semantic_edges_checked = 0
        self._checked_edges: set[tuple[str, str]] = set()
        self._matrices: dict[str, np.ndarray[Any, Any]] = {}
        self._resources: dict[str, tuple[int, int, int]] = {}
        self._closed = False

    # -- caches ---------------------------------------------------------

    def matrix(self, state: str) -> np.ndarray[Any, Any]:
        cached = self._matrices.get(state)
        if cached is None:
            cached = dense_matrix(state)
            self._matrices[state] = cached
        return cached

    def resource_of(self, state: str) -> tuple[int, int, int]:
        cached = self._resources.get(state)
        if cached is None:
            cached = resource(graph_from_state(state))
            self._resources[state] = cached
        return cached

    # -- expansion ------------------------------------------------------

    def expand(self, state: str) -> dict[str, dict[Site, str]]:
        cached = self.expansions.get(state)
        if cached is not None:
            return cached
        base = graph_from_state(state)
        if list(base.vertices()) != list(range(base.num_vertices())):
            raise StudyFailure("canonical state does not decode to consecutive vertex ids")
        expansion: dict[str, dict[Site, str]] = {}
        for schema_id in self.schema_order:
            move = self.moves[schema_id]
            legal: dict[Site, str] = {}
            for site in move["enumerator"](base):
                self.attempts += 1
                successor = attempt_atomic_move(base, move, site)
                if successor is None:
                    continue
                legal[site] = successor
                self.transitions += 1
                edge = (state, successor)
                if edge not in self._checked_edges:
                    self._checked_edges.add(edge)
                    if self.check_semantics and not matrices_equal(
                        self.matrix(state), self.matrix(successor)
                    ):
                        raise GuardUnsound(
                            "legal atomic move changed the dense map: "
                            f"schema={schema_id} site={site} state_sha={sha256_text(state)[:16]} "
                            f"successor_sha={sha256_text(successor)[:16]}"
                        )
                    self.semantic_edges_checked += 1
            if legal:
                expansion[schema_id] = dict(sorted(legal.items()))
        self.expansions[state] = expansion
        return expansion

    # -- closure --------------------------------------------------------

    def closure(self) -> None:
        if self._closed:
            return
        queue: deque[str] = deque([self.start])
        while queue:
            state = queue.popleft()
            expansion = self.expand(state)
            for schema_id in self.schema_order:
                for site in sorted(expansion.get(schema_id, {})):
                    successor = expansion[schema_id][site]
                    if successor not in self.parents:
                        if len(self.parents) >= self.cap:
                            raise CapExceeded(
                                f"state cap {self.cap} exceeded with pending states"
                            )
                        self.parents[successor] = (state, schema_id, site)
                        queue.append(successor)
        self._closed = True

    # -- certificate extraction ----------------------------------------

    def optimum(self) -> tuple[str, tuple[int, int, int]]:
        best_state: str | None = None
        best_key: tuple[tuple[int, int, int], str] | None = None
        for state in self.parents:
            key = (self.resource_of(state), state)
            if best_key is None or key < best_key:
                best_key = key
                best_state = state
        assert best_state is not None and best_key is not None
        return best_state, best_key[0]

    def witness_path(self, optimum_state: str) -> list[tuple[str, Site]]:
        path: list[tuple[str, Site]] = []
        state: str | None = optimum_state
        while state is not None and state != self.start:
            parent = self.parents[state]
            if parent is None:
                raise StudyFailure("witness reconstruction reached an orphan state")
            prev, schema_id, site = parent
            path.append((schema_id, site))
            state = prev
        path.reverse()
        return path


def replay_witness(
    start: str, witness: Sequence[tuple[str, Site]], moves: Mapping[str, Mapping[str, Any]]
) -> tuple[bool, str]:
    state = start
    for schema_id, site in witness:
        base = graph_from_state(state)
        successor = attempt_atomic_move(base, moves[schema_id], site)
        if successor is None:
            return False, state
        state = successor
    return True, state


# ---------------------------------------------------------------------------
# Native and generic arms
# ---------------------------------------------------------------------------


def native_full_reduce(start: str) -> tuple[str, tuple[int, int, int]]:
    graph = graph_from_state(start)
    pyzx.simplify.full_reduce(graph)
    return canonical_state(graph), resource(graph)


def generic_search(
    explorer: AtomicExplorer, word_index: int, witness_length: int
) -> tuple[str, tuple[int, int, int]]:
    """Seeded random-restart resource-greedy control with no registry knowledge."""

    rng = np.random.Generator(
        np.random.PCG64(GENERIC_SEED_MULTIPLIER * word_index + GENERIC_SEED_OFFSET)
    )
    budget = max(100, 100 * witness_length)
    start_key = explorer.resource_of(explorer.start)
    best_state, best_key = explorer.start, start_key
    for _restart in range(GENERIC_RESTARTS):
        current = explorer.start
        applied = 0
        while applied < budget:
            expansion = explorer.expand(current)
            legal: list[tuple[str, Site, str]] = []
            for schema_id in explorer.schema_order:
                for site in sorted(expansion.get(schema_id, {})):
                    legal.append((schema_id, site, expansion[schema_id][site]))
            if not legal:
                break
            if float(rng.random()) < GENERIC_EPSILON:
                index = int(rng.integers(len(legal)))
            else:
                keys = [explorer.resource_of(succ) for _, _, succ in legal]
                minimum = min(keys)
                candidates = [i for i, key in enumerate(keys) if key == minimum]
                index = candidates[int(rng.integers(len(candidates)))]
            _schema_id, _site, current = legal[index]
            applied += 1
            current_key = explorer.resource_of(current)
            if (current_key, current) < (best_key, best_state):
                best_state, best_key = current, current_key
    return best_state, best_key


def hostile_extension_outcomes(
    production_state: str, optimum_resource: tuple[int, int, int]
) -> dict[str, Any]:
    """Predeclared hostile extensions applied to the native output state."""

    rows: list[dict[str, Any]] = []
    any_collapse = False
    for name in sorted(hostile_extension_map()):
        operation = hostile_extension_map()[name]
        graph = graph_from_state(production_state)
        raised: str | None = None
        try:
            operation(graph)
            pyzx.simplify.full_reduce(graph)
            outcome_resource = resource(graph)
        except Exception as exc:  # hostile op failure is recorded, not fatal
            raised = f"{type(exc).__name__}: {exc}"
            outcome_resource = None
        collapse = (
            raised is None
            and outcome_resource is not None
            and outcome_resource <= optimum_resource
        )
        if collapse:
            any_collapse = True
        rows.append(
            {
                "extension": name,
                "raised": raised,
                "resource_after": list(outcome_resource) if outcome_resource else None,
                "collapses_gap": bool(collapse),
            }
        )
    return {"rows": rows, "any_collapse": bool(any_collapse)}


# ---------------------------------------------------------------------------
# Critical interactions: bounded canonical-site two-step census
# ---------------------------------------------------------------------------


def critical_interaction_census(explorer: AtomicExplorer) -> dict[str, Any]:
    """Ordered schema-pair census over the whole per-word closure.

    Two-step diamonds use the canonical site of each schema (first legal site
    in the frozen schema order and sorted site order).  This is a bounded
    representative-move census, not a critical-pair theorem and not evidence
    of confluence.
    """

    keys = [
        "co_enabled",
        "a_disables_b",
        "a_enables_b",
        "diamonds",
        "commuting",
        "noncommuting",
        "divergent_resource",
    ]
    totals: dict[tuple[str, str], Counter[str]] = {
        (a, b): Counter({key: 0 for key in keys})
        for a in explorer.schema_order
        for b in explorer.schema_order
    }

    def canonical_successor(state: str, schema_id: str) -> str | None:
        expansion = explorer.expand(state)
        legal = expansion.get(schema_id)
        if not legal:
            return None
        first_site = sorted(legal)[0]
        return legal[first_site]

    for state in explorer.parents:
        expansion = explorer.expand(state)
        enabled = {sid: bool(expansion.get(sid)) for sid in explorer.schema_order}
        for a in explorer.schema_order:
            if not enabled[a]:
                continue
            succ_a = canonical_successor(state, a)
            for b in explorer.schema_order:
                row = totals[(a, b)]
                if enabled[a] and enabled[b]:
                    row["co_enabled"] += 1
                expansion_a = explorer.expand(succ_a)
                b_after_a = bool(expansion_a.get(b))
                if enabled[b] and not b_after_a:
                    row["a_disables_b"] += 1
                if not enabled[b] and b_after_a:
                    row["a_enables_b"] += 1
                if enabled[a] and enabled[b]:
                    row["diamonds"] += 1
                    s_ab = canonical_successor(succ_a, b) or succ_a
                    succ_b = canonical_successor(state, b)
                    s_ba = canonical_successor(succ_b, a) or succ_b
                    if s_ab == s_ba:
                        row["commuting"] += 1
                    else:
                        row["noncommuting"] += 1
                        if explorer.resource_of(s_ab) != explorer.resource_of(s_ba):
                            row["divergent_resource"] += 1
    pairs = [
        {"first": a, "second": b, **{key: int(counter[key]) for key in keys}}
        for (a, b), counter in sorted(totals.items())
    ]
    return {
        "census_kind": "CANONICAL_SITE_REPRESENTATIVE_TWO_STEP__NOT_A_CONFLUENCE_CLAIM",
        "schema_order": list(explorer.schema_order),
        "pairs": pairs,
        "pair_count": len(pairs),
    }


def merge_interaction_census(censuses: Sequence[Mapping[str, Any]]) -> dict[str, Any]:
    base = censuses[0]
    keys = [
        "co_enabled",
        "a_disables_b",
        "a_enables_b",
        "diamonds",
        "commuting",
        "noncommuting",
        "divergent_resource",
    ]
    totals: dict[tuple[str, str], Counter[str]] = {}
    for census in censuses:
        for row in census["pairs"]:
            key = (row["first"], row["second"])
            counter = totals.setdefault(key, Counter({k: 0 for k in keys}))
            for name in keys:
                counter[name] += row[name]
    return {
        "census_kind": base["census_kind"],
        "schema_order": base["schema_order"],
        "pair_count": len(totals),
        "pairs": [
            {"first": a, "second": b, **{key: int(counter[key]) for key in keys}}
            for (a, b), counter in sorted(totals.items())
        ],
    }


# ---------------------------------------------------------------------------
# Per-word analysis
# ---------------------------------------------------------------------------


@dataclass
class WordTask:
    word: tuple[str, ...]
    word_index: int
    mode: str  # "pilot" | "execute"
    domain: str  # "primary" | "probe"
    cap: int


def analyze_word(task: WordTask) -> dict[str, Any]:
    started = time.monotonic()
    start = start_state_from_word(task.word)
    moves = atomic_move_table()
    check_semantics = task.mode == "execute"
    explorer = AtomicExplorer(start, moves, task.cap, check_semantics)
    record: dict[str, Any] = {
        "word": list(task.word),
        "word_index": task.word_index,
        "domain": task.domain,
        "start_sha256": sha256_text(start),
        "reachable_states": len(explorer.parents),
        "reachable_transitions": explorer.transitions,
        "move_attempts": explorer.attempts,
        "semantic_edges_checked": explorer.semantic_edges_checked,
        "cap_hit": False,
    }
    try:
        explorer.closure()  # raises GuardUnsound / StudyFailure upward
    except CapExceeded:
        record.update(
            {
                "cap_hit": True,
                "reachable_states": None,
                "reachable_transitions": None,
                "move_attempts": explorer.attempts,
                "semantic_edges_checked": None,
            }
        )
        if task.mode == "pilot":
            record["wall_seconds"] = round(time.monotonic() - started, 3)
        return record

    # refresh the counters: the record header holds pre-closure snapshots
    record.update(
        {
            "reachable_states": len(explorer.parents),
            "reachable_transitions": explorer.transitions,
            "move_attempts": explorer.attempts,
            "semantic_edges_checked": explorer.semantic_edges_checked,
        }
    )

    if task.mode == "pilot":
        record["wall_seconds"] = round(time.monotonic() - started, 3)
        return record

    # native arm
    native_state, native_resource = native_full_reduce(start)
    if not matrices_equal(explorer.matrix(start), explorer.matrix(native_state)):
        raise StudyFailure(f"native full_reduce changed semantics: word={task.word}")

    # certificate arm
    optimum_state, optimum_resource = explorer.optimum()
    witness = explorer.witness_path(optimum_state)
    replay_ok, replay_final = replay_witness(start, witness, moves)
    if not replay_ok or replay_final != optimum_state:
        raise StudyFailure(f"witness replay failed: word={task.word}")
    if not matrices_equal(explorer.matrix(start), explorer.matrix(optimum_state)):
        raise StudyFailure(f"certificate optimum changed semantics: word={task.word}")

    # generic control
    generic_state, generic_resource = generic_search(explorer, task.word_index, len(witness))
    if not matrices_equal(explorer.matrix(start), explorer.matrix(generic_state)):
        raise StudyFailure(f"generic search changed semantics: word={task.word}")

    production_reachable = native_state in explorer.parents
    production_matched = production_reachable
    if not production_matched:
        for state in explorer.parents:
            if explorer.resource_of(state) == native_resource and matrices_equal(
                explorer.matrix(state), explorer.matrix(native_state)
            ):
                production_matched = True
                break

    census = critical_interaction_census(explorer) if task.domain == "primary" else None

    record.update(
        {
            "native_resource": list(native_resource),
            "optimum_resource": list(optimum_resource),
            "generic_resource": list(generic_resource),
            "strict_gap": bool(native_resource > optimum_resource),
            "generic_match": bool(generic_resource == optimum_resource),
            "witness": [
                {"schema": schema_id, "site": list(site)} for schema_id, site in witness
            ],
            "witness_length": len(witness),
            "witness_replay_ok": True,
            "native_state_sha256": sha256_text(native_state),
            "optimum_state_sha256": sha256_text(optimum_state),
            "native_state_reachable": bool(production_reachable),
            "native_state_represented": bool(production_matched),
            "interaction_census": census,
        }
    )
    return record


def analyze_word_task(payload: tuple[str, list[str], int, str, int]) -> dict[str, Any]:
    """Multiprocessing entry point: (mode marker, word, index, domain, cap)."""

    mode, word, word_index, domain, cap = payload
    task = WordTask(word=tuple(word), word_index=word_index, mode=mode, domain=domain, cap=cap)
    try:
        return analyze_word(task)
    except GuardUnsound as failure:
        raise GuardUnsound(f"word={task.word}: {failure}") from failure


# ---------------------------------------------------------------------------
# Freeze binding (frozen inputs must be committed, clean, same intro commit)
# ---------------------------------------------------------------------------


FROZEN_INPUTS = (REGISTRY_PATH, PROTOCOL_PATH, REQUIREMENTS_PATH, Path(__file__))


def _git(args: Sequence[str]) -> str:
    result = subprocess.run(
        ["git", "-C", str(REPO_ROOT), *args], check=False, capture_output=True, text=True
    )
    if result.returncode != 0:
        raise StudyFailure(f"git failed: {' '.join(args)}: {result.stderr.strip()}")
    return result.stdout.strip()


def freeze_binding() -> dict[str, Any]:
    relative = [str(path.relative_to(REPO_ROOT)) for path in FROZEN_INPUTS]
    status = _git(["status", "--porcelain", "--", *relative])
    if status:
        raise StudyFailure(f"frozen inputs have uncommitted changes: {status}")
    intro_commits: set[str] = set()
    for path in relative:
        commits = _git(["log", "--format=%H", "--diff-filter=A", "--", path]).splitlines()
        if not commits:
            raise StudyFailure(f"frozen input was never committed: {path}")
        intro_commits.add(commits[0])
    if len(intro_commits) != 1:
        raise StudyFailure(
            f"frozen inputs introduced in different commits: {sorted(intro_commits)}"
        )
    return {
        "frozen_inputs": relative,
        "introduced_in_one_commit": True,
        "introduction_commit": sorted(intro_commits)[0],
        "head_commit": _git(["rev-parse", "HEAD"]),
        "worktree_clean_for_frozen_inputs": True,
    }


# ---------------------------------------------------------------------------
# Receipt assembly, gates, terminals
# ---------------------------------------------------------------------------


def terminal_from_records(records: Sequence[Mapping[str, Any]]) -> dict[str, Any]:
    primary = [row for row in records if row["domain"] == "primary"]
    gaps = [row for row in primary if row.get("strict_gap")]
    outcome: dict[str, Any] = {
        "primary_words": len(primary),
        "gap_words": len(gaps),
        "hostile_collapse_words": None,
        "surviving_gap_words": None,
        "generic_miss_words": None,
    }
    if not gaps:
        outcome["terminal"] = NULL_TERMINAL
        return outcome
    survivors = [row for row in gaps if not row.get("hostile_collapse")]
    outcome["hostile_collapse_words"] = len(gaps) - len(survivors)
    outcome["surviving_gap_words"] = len(survivors)
    if not survivors:
        outcome["terminal"] = CROSS_TERMINAL
        return outcome
    misses = [row for row in survivors if not row.get("generic_match")]
    outcome["generic_miss_words"] = len(misses)
    outcome["terminal"] = GENERIC_TERMINAL if not misses else POSITIVE_TERMINAL
    return outcome


def hostile_collapse_records(records: Sequence[Mapping[str, Any]]) -> list[dict[str, Any]]:
    """Apply predeclared hostile extensions on each distinct gap witness word."""

    rows: list[dict[str, Any]] = []
    for row in records:
        if row["domain"] != "primary" or not row.get("strict_gap") or row.get("cap_hit"):
            continue
        start = start_state_from_word(row["word"])
        native_state, _native_resource = native_full_reduce(start)
        optimum = tuple(row["optimum_resource"])
        outcome = hostile_extension_outcomes(native_state, optimum)
        rows.append(
            {
                "word": row["word"],
                "word_index": row["word_index"],
                "optimum_resource": row["optimum_resource"],
                "native_resource": row["native_resource"],
                "extensions": outcome["rows"],
                "any_collapse": outcome["any_collapse"],
            }
        )
    return rows


def build_gates(
    registry: Mapping[str, Any],
    audits: Mapping[str, Any],
    records: Sequence[Mapping[str, Any]],
    source_verification: Mapping[str, Any],
    freeze: Mapping[str, Any],
) -> list[dict[str, Any]]:
    primary = [row for row in records if row["domain"] == "primary"]
    probes = [row for row in records if row["domain"] == "probe"]
    censuses = [row["interaction_census"] for row in primary if row["interaction_census"]]
    return [
        {"gate": "source_digests_and_direct_url", "passed": source_verification["commit"] == EXPECTED_COMMIT},
        {"gate": "ast_primitive_closure_equality", "passed": bool(audits["primitive_closure_exact"])},
        {"gate": "ast_single_schema_omissions_rejected", "passed": audits["hostile_omissions_rejected"] == len(registry["registered_schemas"])},
        {"gate": "ast_mutator_surface_covered", "passed": bool(audits["mutator_method_surface_covered"])},
        {"gate": "guard_purity_all_pure", "passed": bool(audits["guard_purity_all_pure"])},
        {"gate": "primary_domain_exhaustive_585", "passed": len(primary) == registry["input_domain"]["primary_word_count"]},
        {"gate": "probe_domain_complete_16", "passed": len(probes) == registry["input_domain"]["boundary_probe_length6_word_count"]},
        {"gate": "no_primary_cap_hit", "passed": not any(row.get("cap_hit") for row in primary)},
        {"gate": "primary_semantics_all_transitions_checked", "passed": all(row["semantic_edges_checked"] is not None for row in primary)},
        {"gate": "native_state_represented_everywhere", "passed": all(row.get("native_state_represented") for row in primary)},
        {"gate": "witness_replay_everywhere", "passed": all(row.get("witness_replay_ok") for row in primary)},
        {"gate": "interaction_matrix_complete", "passed": bool(censuses) and all(c["pair_count"] == len(registry["registered_schemas"]) ** 2 for c in censuses)},
    ] + [{"gate": "freeze_binding_clean", "passed": bool(freeze["introduced_in_one_commit"])}]


def success_receipt(
    mode: str,
    registry: Mapping[str, Any],
    source_verification: Mapping[str, Any],
    audits: Mapping[str, Any],
    freeze: Mapping[str, Any],
    records: Sequence[Mapping[str, Any]],
) -> dict[str, Any]:
    hostile = hostile_collapse_records(records)
    collapse_by_index = {row["word_index"]: row["any_collapse"] for row in hostile}
    enriched: list[dict[str, Any]] = []
    for row in records:
        item = {k: v for k, v in row.items() if k != "interaction_census"}
        if row.get("strict_gap") and row["word_index"] in collapse_by_index:
            item["hostile_collapse"] = collapse_by_index[row["word_index"]]
        enriched.append(item)
    outcome = terminal_from_records(enriched)
    primary = [row for row in records if row["domain"] == "primary"]
    merged_census = merge_interaction_census(
        [row["interaction_census"] for row in primary if row["interaction_census"]]
    )
    gaps = [row for row in primary if row.get("strict_gap")]
    gates = build_gates(registry, audits, records, source_verification, freeze)
    receipt: dict[str, Any] = {
        "schema": "ORION.ORION01.Round2.PyZXAtomicCheckerRegistryResults.v1",
        "paper_id": "ORION-01",
        "round": 2,
        "mode": mode,
        "date": "2026-08-27",
        "source_verification": dict(source_verification),
        "freeze_binding": dict(freeze),
        "audits": dict(audits),
        "domain_counts": {
            "primary": len(primary),
            "probe": len(records) - len(primary),
            "probe_cap_hits": sum(1 for row in records if row["domain"] == "probe" and row.get("cap_hit")),
        },
        "arm_counts": {
            "strict_gap_words": len(gaps),
            "gap_witness_words": [row["word_index"] for row in gaps],
        },
        "hostile_extensions": hostile,
        "critical_interactions": merged_census,
        "gates": gates,
        "gates_all_passed": all(gate["passed"] for gate in gates),
        "outcome": outcome,
        "rows": sorted(enriched, key=lambda row: row["word_index"]),
    }
    if not receipt["gates_all_passed"]:
        failed = [gate["gate"] for gate in gates if not gate["passed"]]
        raise StudyFailure(f"realization gates failed before terminal: {failed}")
    return receipt


def failed_receipt(
    mode: str,
    registry: Mapping[str, Any],
    source_verification: Mapping[str, Any],
    audits: Mapping[str, Any],
    freeze: Mapping[str, Any],
    failure: BaseException,
    records: Sequence[Mapping[str, Any]],
) -> dict[str, Any]:
    terminal = AB_R2_GUARD_UNSOUND_TERMINAL if isinstance(failure, GuardUnsound) else FAIL_TERMINAL
    return {
        "schema": "ORION.ORION01.Round2.PyZXAtomicCheckerRegistryResults.v1",
        "paper_id": "ORION-01",
        "round": 2,
        "mode": mode,
        "date": "2026-08-27",
        "source_verification": dict(source_verification),
        "freeze_binding": dict(freeze),
        "audits": dict(audits),
        "outcome": {
            "terminal": terminal,
            "failure_kind": type(failure).__name__,
            "failure_message": str(failure),
            "records_completed_before_failure": len(records),
        },
        "rows": sorted((dict(row) for row in records), key=lambda row: row["word_index"]),
    }


AB_R2_GUARD_UNSOUND_TERMINAL = "AB_R2_ATOMIC_GUARD_UNSOUND"


# ---------------------------------------------------------------------------
# Drivers
# ---------------------------------------------------------------------------


def frozen_cap(registry: Mapping[str, Any]) -> int:
    return int(registry["max_states_per_input_fail_closed"])


def word_payloads(mode: str, registry: Mapping[str, Any]) -> list[tuple[str, list[str], int, str, int]]:
    cap = frozen_cap(registry)
    payloads: list[tuple[str, list[str], int, str, int]] = []
    for index, word in enumerate(primary_words()):
        if mode == "pilot" and len(word) > 2:
            continue
        payloads.append((mode, list(word), index, "primary", cap))
    if mode == "execute":
        primary_count = len(primary_words())
        for offset, word in enumerate(probe_words()):
            payloads.append((mode, list(word), primary_count + offset, "probe", cap))
    return payloads


def run_pool(
    mode: str, registry: Mapping[str, Any], workers: int
) -> list[dict[str, Any]]:
    payloads = word_payloads(mode, registry)
    if workers <= 1:
        records = [analyze_word_task(payload) for payload in payloads]
    else:
        import multiprocessing

        with multiprocessing.Pool(processes=workers) as pool:
            records = pool.map(analyze_word_task, payloads, chunksize=1)
    if len(records) != len(payloads):
        raise StudyFailure(f"worker record count mismatch: {len(records)} != {len(payloads)}")
    return records


def run_pilot(registry: Mapping[str, Any], workers: int) -> dict[str, Any]:
    source_verification = verify_installed_source(registry)
    started = time.monotonic()
    records = run_pool("pilot", registry, workers)
    walls = [row["wall_seconds"] for row in records]
    states = [row["reachable_states"] for row in records]
    log = {
        "schema": "ORION.ORION01.Round2.PyZXAtomicCheckerRegistryPilotLog.v1",
        "paper_id": "ORION-01",
        "round": 2,
        "date": "2026-08-27",
        "purpose": "INFRASTRUCTURE_CALIBRATION_ONLY__NO_ARM_COMPARISON_COMPUTED_OR_INSPECTED",
        "source_verification": {
            "commit": source_verification["commit"],
            "version": source_verification["version"],
        },
        "workers": workers,
        "word_count": len(records),
        "cap": frozen_cap(registry),
        "totals": {
            "wall_seconds_total": round(time.monotonic() - started, 3),
            "max_word_wall_seconds": max(walls),
            "max_reachable_states": max(states),
            "sum_reachable_states": sum(states),
            "cap_hits": sum(1 for row in records if row.get("cap_hit")),
        },
        "rows": sorted(records, key=lambda row: row["word_index"]),
    }
    return log


def run_execute(
    mode_label: str,
    registry: Mapping[str, Any],
    workers: int,
    progress: list[dict[str, Any]] | None = None,
) -> dict[str, Any]:
    source_verification = verify_installed_source(registry)
    audits = derive_source_audits(registry)
    freeze = freeze_binding()
    records = run_pool("execute", registry, workers)
    if progress is not None:
        progress.extend(records)
    primary_caps = [
        row for row in records if row["domain"] == "primary" and row.get("cap_hit")
    ]
    if primary_caps:
        raise StudyFailure(
            "primary-domain fail-closed state cap hit on "
            f"{len(primary_caps)} words (first word_index={primary_caps[0]['word_index']})"
        )
    return success_receipt(mode_label, registry, source_verification, audits, freeze, records)


def subset_receipt(receipt: Mapping[str, Any]) -> dict[str, Any]:
    gap_indexes = set(receipt["arm_counts"]["gap_witness_words"])
    rows = [
        dict(row)
        for row in receipt["rows"]
        if len(row["word"]) <= 2 or row["word_index"] in gap_indexes
    ]
    subset = {key: value for key, value in receipt.items() if key != "rows"}
    subset["schema"] = "ORION.ORION01.Round2.PyZXAtomicCheckerRegistryResultsSubset.v1"
    subset["subset_rule"] = "PRIMARY_WORDS_LENGTH_LE_2_PLUS_ALL_GAP_WITNESS_WORDS"
    subset["subset_row_count"] = len(rows)
    subset["rows"] = rows
    return subset


def write_receipt(path: Path, payload: Mapping[str, Any]) -> None:
    text = canonical_json(payload) + "\n"
    if not text.strip():
        raise StudyFailure(f"refusing to write empty receipt: {path}")
    path.write_text(text, encoding="utf-8")


def build_execution_receipt(
    registry: Mapping[str, Any], workers: int
) -> tuple[dict[str, Any], bool]:
    """Run the frozen study once; return (receipt, succeeded)."""

    records: list[dict[str, Any]] = []
    try:
        receipt = run_execute("execute", registry, workers, progress=records)
        return receipt, True
    except StudyFailure as failure:
        source_verification = verify_installed_source(registry)
        audits: dict[str, Any]
        freeze: dict[str, Any]
        try:
            audits = derive_source_audits(registry)
        except StudyFailure as audit_failure:
            audits = {"audit_failure": str(audit_failure)}
        try:
            freeze = freeze_binding()
        except StudyFailure as freeze_failure:
            freeze = {"freeze_failure": str(freeze_failure)}
        return (
            failed_receipt(
                "execute", registry, source_verification, audits, freeze, failure, records
            ),
            False,
        )


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="ORION-01 Round-2 atomic checker registry study")
    parser.add_argument("mode", choices=("pilot", "execute", "check"))
    parser.add_argument("--workers", type=int, default=min(os.cpu_count() or 1, 16))
    args = parser.parse_args(argv)

    registry = load_registry()
    if args.mode == "pilot":
        log = run_pilot(registry, args.workers)
        write_receipt(PILOT_PATH, log)
        print(json.dumps({"pilot": log["totals"], "workers": args.workers}, sort_keys=True))
        return 0

    receipt, succeeded = build_execution_receipt(registry, args.workers)

    if args.mode == "execute":
        write_receipt(RESULTS_PATH, receipt)
        if succeeded:
            write_receipt(SUBSET_RESULTS_PATH, subset_receipt(receipt))
        print(json.dumps({"outcome": receipt["outcome"], "receipt": RESULTS_PATH.name}, sort_keys=True))
        return 0

    # check mode: byte-compare a fresh full re-execution against committed files
    fresh = canonical_json(receipt) + "\n"
    fresh_subset = canonical_json(subset_receipt(receipt)) + "\n" if succeeded else None
    committed = RESULTS_PATH.read_text(encoding="utf-8")
    committed_subset = SUBSET_RESULTS_PATH.read_text(encoding="utf-8")
    identical = fresh == committed and fresh_subset is not None and fresh_subset == committed_subset
    print(json.dumps({"byte_identical_rerun": bool(identical), "checked": 2}, sort_keys=True))
    return 0 if identical else 3


if __name__ == "__main__":
    raise SystemExit(main())

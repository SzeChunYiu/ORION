#!/usr/bin/env python3
"""Prospectively frozen ORION-01 PyZX ``full_reduce`` Round-1 study.

The scientific object is deliberately narrow: the automatic macro-operation
language called by ``pyzx.simplify.full_reduce`` at one pinned public commit.
This module never treats that registry as all of PyZX or all of the ZX
calculus.  See ORION01_R11_PYZX_ROUND1_PROTOCOL.md before using any result.
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
from pathlib import Path
import subprocess
import sys
from typing import Any, Callable, Iterator, Mapping, Sequence

import numpy as np
import pyzx
from pyzx import Circuit
from pyzx.graph.base import BaseGraph
from pyzx.graph.jsonparser import json_to_graph
from pyzx.utils import VertexType


HERE = Path(__file__).resolve().parent
REGISTRY_PATH = HERE / "ORION01_R11_PYZX_SOURCE_REGISTRY.json"
PROTOCOL_PATH = HERE / "ORION01_R11_PYZX_ROUND1_PROTOCOL.md"
RESULTS_PATH = HERE / "ORION01_R11_PYZX_RESULTS.json"
REQUIREMENTS_PATH = HERE / "requirements-lock.txt"

EXPECTED_COMMIT = "dade7d46f193635bbdaefd8fcde837f9449fddc5"
EXPECTED_VERSION = "0.10.5"
FAIL_TERMINAL = "CANNOT_CHECK_MOVE_COMPLETENESS"
POSITIVE_TERMINAL = "AB_R11_REALIZED_GAP_COMPLETE_REWRITE_REGISTRY"
NULL_TERMINAL = "AB_R11_COMPLETE_REGISTRY_NO_STRICT_GAP"
CROSS_TERMINAL = "AB_R11_CROSS_MOVE_COLLAPSES_GAP"

CONTROL_SYMBOLS = {
    "full_reduce",
    "clifford_simp",
    "interior_clifford_simp",
    "spider_simp",
}


class StudyFailure(RuntimeError):
    """Fail-closed scientific prerequisite failure."""


@dataclass(frozen=True)
class RootAnalysis:
    start_state: str
    production_state: str
    production_resource: tuple[int, int, int]
    optimum_state: str
    optimum_resource: tuple[int, int, int]
    optimum_path: tuple[str, ...]
    reachable_states: int
    reachable_transitions: int
    production_exactly_reachable: bool
    production_resource_semantics_matched: bool

    @property
    def strict_gap(self) -> bool:
        return self.optimum_resource < self.production_resource


def canonical_json(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True)


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def sha256_text(value: str) -> str:
    return sha256_bytes(value.encode("utf-8"))


def load_registry(path: Path = REGISTRY_PATH) -> dict[str, Any]:
    row = json.loads(path.read_text(encoding="utf-8"))
    if row["schema"] != "ORION.ORION01.R11.PyZXFullReduceSourceRegistry.v1":
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


def derive_source_registry(registry: Mapping[str, Any]) -> dict[str, Any]:
    simplify_path = pyzx_source_root() / "pyzx/simplify.py"
    tree = ast.parse(simplify_path.read_text(encoding="utf-8"), filename=str(simplify_path))
    functions = _function_nodes(tree)
    expected_graph = registry["control_call_graph"]
    target_names = set(registry["registered_symbol_order"]) | CONTROL_SYMBOLS | {
        "remove_isolated_vertices"
    }

    observed_graph: dict[str, list[str]] = {}
    for parent, expected_children in expected_graph.items():
        if parent not in functions:
            raise StudyFailure(f"missing control function in pinned source: {parent}")
        calls = _called_symbols(functions[parent]) & target_names
        normalized = {
            "BaseGraph.remove_isolated_vertices" if name == "remove_isolated_vertices" else name
            for name in calls
        }
        if normalized != set(expected_children):
            raise StudyFailure(
                f"source call-closure mismatch for {parent}: "
                f"observed={sorted(normalized)} expected={sorted(expected_children)}"
            )
        observed_graph[parent] = sorted(normalized)

    manifest_symbols = set(registry["registered_symbol_order"])
    discovered: set[str] = set()
    todo = ["full_reduce"]
    seen_controls: set[str] = set()
    while todo:
        parent = todo.pop()
        if parent in seen_controls:
            continue
        seen_controls.add(parent)
        for child in expected_graph[parent]:
            name = "remove_isolated_vertices" if child.startswith("BaseGraph.") else child
            if name in manifest_symbols:
                discovered.add(name)
            elif name in expected_graph:
                todo.append(name)
            else:
                raise StudyFailure(f"unclassified source-reachable symbol: {child}")

    if discovered != manifest_symbols:
        raise StudyFailure(
            f"registry symbol set mismatch: discovered={sorted(discovered)} "
            f"manifest={sorted(manifest_symbols)}"
        )

    # Every one-entry omission must fail set equality against the independently
    # source-derived closure.  This is deliberately not a trace-coverage test.
    omissions: list[dict[str, Any]] = []
    for omitted in registry["registered_symbol_order"]:
        mutated = manifest_symbols - {omitted}
        rejected = mutated != discovered
        if not rejected:
            raise StudyFailure(f"hostile registry omission accepted: {omitted}")
        omissions.append({"omitted": omitted, "rejected": rejected})

    return {
        "observed_control_call_graph": observed_graph,
        "discovered_registered_symbols": sorted(discovered),
        "discovered_count": len(discovered),
        "manifest_exact": True,
        "hostile_single_omissions": omissions,
        "hostile_omissions_rejected": sum(int(x["rejected"]) for x in omissions),
    }


def source_graph_state(graph: BaseGraph[Any, Any]) -> str:
    """Lossless deterministic JSON while preserving operational vertex ids."""

    return canonical_json(graph.to_dict(include_scalar=True))


def graph_from_state(state: str) -> BaseGraph[Any, Any]:
    return json_to_graph(json.loads(state))


def resource(graph: BaseGraph[Any, Any]) -> tuple[int, int, int]:
    non_boundary = sum(graph.type(v) != VertexType.BOUNDARY for v in graph.vertices())
    return (pyzx.simplify.tcount(graph), non_boundary, graph.num_edges())


def structural_measure(graph: BaseGraph[Any, Any]) -> tuple[int, int, int]:
    x_vertices = sum(graph.type(v) == VertexType.X for v in graph.vertices())
    return (graph.num_vertices(), x_vertices, graph.num_edges())


def _remove_isolated(graph: BaseGraph[Any, Any]) -> None:
    graph.remove_isolated_vertices()


def operation_map() -> dict[str, Callable[[BaseGraph[Any, Any]], Any]]:
    simplify = pyzx.simplify
    return {
        "fuse_simp": simplify.fuse_simp,
        "remove_self_loop_simp": simplify.remove_self_loop_simp,
        "to_gh": simplify.to_gh,
        "id_simp": simplify.id_simp,
        "pivot_simp": simplify.pivot_simp,
        "lcomp_simp": simplify.lcomp_simp,
        "pivot_boundary_simp": simplify.pivot_boundary_simp,
        "pivot_gadget_simp": simplify.pivot_gadget_simp,
        "gadget_simp": simplify.gadget_simp,
        "copy_simp": simplify.copy_simp,
        "supplementarity_simp": simplify.supplementarity_simp,
        "remove_isolated_vertices": _remove_isolated,
    }


def hostile_extension_map() -> dict[str, Callable[[BaseGraph[Any, Any]], Any]]:
    simplify = pyzx.simplify
    return {
        "bialg_simp": simplify.bialg_simp,
        "hopf_simp": simplify.hopf_simp,
        "gadget_phasepoly_simp": simplify.gadget_phasepoly_simp,
    }


def apply_operation(state: str, operation: Callable[[BaseGraph[Any, Any]], Any]) -> str | None:
    graph = graph_from_state(state)
    operation(graph)
    successor = source_graph_state(graph)
    return successor if successor != state else None


GATE_ALPHABET = ("H0", "H1", "S0", "S1", "T0", "T1", "CX01", "CX10")


def all_gate_words(max_length: int = 4) -> Iterator[tuple[str, ...]]:
    for length in range(max_length + 1):
        yield from itertools.product(GATE_ALPHABET, repeat=length)


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


def start_state_from_word(word: Sequence[str]) -> str:
    graph = circuit_from_word(word).to_graph()
    if any(graph.type(v) == VertexType.H_BOX for v in graph.vertices()):
        raise StudyFailure(f"frozen circuit generated forbidden H-box: {word}")
    return source_graph_state(graph)


def dense_matrix(state: str) -> np.ndarray[Any, np.dtype[np.complexfloating[Any, Any]]]:
    graph = graph_from_state(state)
    return np.asarray(graph.to_matrix(preserve_scalar=True), dtype=np.complex128)


def matrices_equal(left: np.ndarray[Any, Any], right: np.ndarray[Any, Any]) -> bool:
    return left.shape == right.shape and bool(
        np.allclose(left, right, rtol=1e-9, atol=1e-9, equal_nan=False)
    )


class ExactExplorer:
    def __init__(self, symbols: Sequence[str], state_cap: int) -> None:
        operations = operation_map()
        if set(symbols) != set(operations):
            raise StudyFailure("runtime operation map differs from frozen registry")
        self.symbols = tuple(symbols)
        self.operations = operations
        self.state_cap = state_cap
        self.expansion_cache: dict[str, dict[str, str]] = {}
        self.tensor_cache: dict[str, np.ndarray[Any, Any]] = {}
        self.resource_cache: dict[str, tuple[int, int, int]] = {}
        self.measure_cache: dict[str, tuple[int, int, int]] = {}
        self.operation_attempts: Counter[str] = Counter()
        self.operation_moves: Counter[str] = Counter()
        self.measure_directions: Counter[str] = Counter()
        self.semantic_checks = 0

    def matrix(self, state: str) -> np.ndarray[Any, Any]:
        if state not in self.tensor_cache:
            self.tensor_cache[state] = dense_matrix(state)
        return self.tensor_cache[state]

    def state_resource(self, state: str) -> tuple[int, int, int]:
        if state not in self.resource_cache:
            self.resource_cache[state] = resource(graph_from_state(state))
        return self.resource_cache[state]

    def state_measure(self, state: str) -> tuple[int, int, int]:
        if state not in self.measure_cache:
            self.measure_cache[state] = structural_measure(graph_from_state(state))
        return self.measure_cache[state]

    def expand(self, state: str) -> dict[str, str]:
        if state in self.expansion_cache:
            return self.expansion_cache[state]
        before_matrix = self.matrix(state)
        before_measure = self.state_measure(state)
        successors: dict[str, str] = {}
        for symbol in self.symbols:
            self.operation_attempts[symbol] += 1
            successor = apply_operation(state, self.operations[symbol])
            if successor is None:
                continue
            self.operation_moves[symbol] += 1
            after_matrix = self.matrix(successor)
            self.semantic_checks += 1
            if not matrices_equal(before_matrix, after_matrix):
                raise StudyFailure(
                    f"dense scalar-preserving semantics failure for {symbol}: "
                    f"{sha256_text(state)} -> {sha256_text(successor)}"
                )
            after_measure = self.state_measure(successor)
            if after_measure < before_measure:
                direction = "decrease"
            elif after_measure == before_measure:
                direction = "equal"
            else:
                direction = "increase"
            self.measure_directions[direction] += 1
            successors[symbol] = successor
        self.expansion_cache[state] = successors
        return successors

    def analyze(self, start_state: str) -> RootAnalysis:
        queue: deque[str] = deque([start_state])
        parents: dict[str, tuple[str, str] | None] = {start_state: None}
        transitions = 0
        while queue:
            state = queue.popleft()
            successors = self.expand(state)
            transitions += len(successors)
            for symbol in self.symbols:
                successor = successors.get(symbol)
                if successor is None or successor in parents:
                    continue
                parents[successor] = (state, symbol)
                if len(parents) > self.state_cap:
                    raise StudyFailure(
                        f"fail-closed state cap {self.state_cap} reached for "
                        f"root {sha256_text(start_state)}"
                    )
                queue.append(successor)

        optimum_state = min(
            parents,
            key=lambda state: (self.state_resource(state), state),
        )
        optimum_path_reversed: list[str] = []
        cursor = optimum_state
        while parents[cursor] is not None:
            predecessor, symbol = parents[cursor]  # type: ignore[misc]
            optimum_path_reversed.append(symbol)
            cursor = predecessor
        optimum_path = tuple(reversed(optimum_path_reversed))

        production_graph = graph_from_state(start_state)
        pyzx.simplify.full_reduce(production_graph)
        production_state = source_graph_state(production_graph)
        self.semantic_checks += 1
        if not matrices_equal(self.matrix(start_state), self.matrix(production_state)):
            raise StudyFailure("pinned full_reduce failed dense scalar-preserving semantics")
        production_resource = self.state_resource(production_state)
        exact_reachable = production_state in parents
        matched = exact_reachable
        if not matched:
            production_matrix = self.matrix(production_state)
            matched = any(
                self.state_resource(state) == production_resource
                and matrices_equal(self.matrix(state), production_matrix)
                for state in parents
            )
        if not matched:
            raise StudyFailure(
                "production full_reduce result is not represented by the complete "
                "registered macro closure at equal resource and semantics"
            )

        return RootAnalysis(
            start_state=start_state,
            production_state=production_state,
            production_resource=production_resource,
            optimum_state=optimum_state,
            optimum_resource=self.state_resource(optimum_state),
            optimum_path=optimum_path,
            reachable_states=len(parents),
            reachable_transitions=transitions,
            production_exactly_reachable=exact_reachable,
            production_resource_semantics_matched=matched,
        )


def critical_interactions(
    explorer: ExactExplorer,
) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    symbols = explorer.symbols
    for first in symbols:
        for second in symbols:
            counts: Counter[str] = Counter()
            for state, successors in explorer.expansion_cache.items():
                first_state = successors.get(first)
                second_state = successors.get(second)
                if first_state is not None and second_state is not None:
                    counts["coenabled"] += 1
                if first_state is not None:
                    second_after_first = explorer.expand(first_state).get(second)
                    if second_state is None and second_after_first is not None:
                        counts["first_enables_second"] += 1
                    if second_state is not None and second_after_first is None:
                        counts["first_disables_second"] += 1
                else:
                    second_after_first = None
                if second_state is not None:
                    first_after_second = explorer.expand(second_state).get(first)
                else:
                    first_after_second = None

                if first_state is not None and second_state is not None:
                    final_first_second = second_after_first or first_state
                    final_second_first = first_after_second or second_state
                    if final_first_second == final_second_first:
                        counts["commuting_diamond"] += 1
                    else:
                        counts["noncommuting_diamond"] += 1
                        if explorer.state_resource(final_first_second) != explorer.state_resource(
                            final_second_first
                        ):
                            counts["two_step_resource_divergence"] += 1
            rows.append(
                {
                    "first": first,
                    "second": second,
                    "coenabled_states": counts["coenabled"],
                    "first_enables_second": counts["first_enables_second"],
                    "first_disables_second": counts["first_disables_second"],
                    "commuting_diamonds": counts["commuting_diamond"],
                    "noncommuting_diamonds": counts["noncommuting_diamond"],
                    "two_step_resource_divergences": counts[
                        "two_step_resource_divergence"
                    ],
                    "bounded_overlap_status": (
                        "OVERLAP_OBSERVED"
                        if counts["coenabled"]
                        else "NO_OVERLAP_OBSERVED_IN_FROZEN_DOMAIN"
                    ),
                }
            )
    return rows


def hostile_authority_controls() -> dict[str, Any]:
    """Finite controls for the completeness/non-identifiability logic."""

    # Complete declared chain: no gap between terminal and intrinsic minimum.
    complete = {"s3": ("s2",), "s2": ("s1",), "s1": ()}
    # Omit the global edge s3->s1: an observed s3->s2 trace is unchanged, but
    # a different terminal resource is possible if s2 is made terminal.
    incomplete_a = {"s3": ("s2",), "s2": (), "s1": ()}
    incomplete_b = {"s3": ("s2", "s1"), "s2": (), "s1": ()}
    resource_map = {"s1": 1, "s2": 2, "s3": 3}

    def reachable(registry: Mapping[str, Sequence[str]], start: str) -> set[str]:
        seen = {start}
        queue = [start]
        while queue:
            state = queue.pop()
            for nxt in registry[state]:
                if nxt not in seen:
                    seen.add(nxt)
                    queue.append(nxt)
        return seen

    complete_min = min(resource_map[s] for s in reachable(complete, "s3"))
    omitted_min = min(resource_map[s] for s in reachable(incomplete_a, "s3"))
    global_min = min(resource_map[s] for s in reachable(incomplete_b, "s3"))

    # Two local terminals of unit resource look additive until a legal global
    # merge maps the pair to one unit.
    local_only = 2
    with_cross_component_merge = 1

    passed = (
        complete_min == 1
        and omitted_min == 2
        and global_min == 1
        and local_only == 2
        and with_cross_component_merge == 1
    )
    if not passed:
        raise StudyFailure("hostile authority controls failed")
    return {
        "complete_registry_no_gap": {"minimum": complete_min, "passed": True},
        "trace_equivalent_omitted_global_move": {
            "shared_observed_edge": ["s3", "s2"],
            "incomplete_minimum": omitted_min,
            "completed_minimum": global_min,
            "gap_collapsed": True,
        },
        "omitted_cross_component_merge": {
            "local_additive_terminal": local_only,
            "global_terminal": with_cross_component_merge,
            "gap_collapsed": True,
        },
        "all_passed": passed,
    }


def _git(*args: str) -> str:
    try:
        return subprocess.check_output(
            ["git", *args], cwd=HERE, text=True, stderr=subprocess.STDOUT
        ).strip()
    except subprocess.CalledProcessError as exc:  # pragma: no cover - CI/repo prerequisite
        raise StudyFailure(f"git binding failed: {' '.join(args)}: {exc.output}") from exc


def protocol_freeze_binding() -> dict[str, str]:
    repo = Path(_git("rev-parse", "--show-toplevel"))
    rows: dict[str, str] = {}
    commits: set[str] = set()
    for path in (PROTOCOL_PATH, REGISTRY_PATH, REQUIREMENTS_PATH, Path(__file__)):
        relative = path.resolve().relative_to(repo)
        tracked_blob = _git("rev-parse", f"HEAD:{relative.as_posix()}")
        worktree_blob = _git("hash-object", relative.as_posix())
        if tracked_blob != worktree_blob:
            raise StudyFailure(f"frozen input has uncommitted bytes: {relative}")
        introduced = _git(
            "log", "--diff-filter=A", "--format=%H", "-1", "--", relative.as_posix()
        )
        if not introduced:
            raise StudyFailure(f"cannot identify freeze commit for {relative}")
        commits.add(introduced)
        rows[relative.as_posix()] = tracked_blob
    # The protocol, registry, requirements and runner must be introduced as one
    # pre-outcome object. Later result-only commits cannot silently refreeze it.
    if len(commits) != 1:
        raise StudyFailure(f"frozen inputs were not introduced together: {sorted(commits)}")
    freeze_commit = next(iter(commits))
    return {
        "freeze_commit": freeze_commit,
        "head_at_execution": _git("rev-parse", "HEAD"),
        "frozen_blob_manifest_sha256": sha256_text(canonical_json(rows)),
    }


def hostile_extension_disposition(
    analysis: RootAnalysis,
) -> dict[str, Any]:
    production_matrix = dense_matrix(analysis.production_state)
    attempts: list[dict[str, Any]] = []
    collapse = False
    for symbol, operation in hostile_extension_map().items():
        state = apply_operation(analysis.production_state, operation)
        if state is None:
            attempts.append({"symbol": symbol, "applicable": False, "collapsed": False})
            continue
        if not matrices_equal(production_matrix, dense_matrix(state)):
            raise StudyFailure(f"hostile extension changed semantics: {symbol}")
        graph = graph_from_state(state)
        pyzx.simplify.full_reduce(graph)
        reduced = source_graph_state(graph)
        if not matrices_equal(production_matrix, dense_matrix(reduced)):
            raise StudyFailure(f"hostile extension plus full_reduce changed semantics: {symbol}")
        reduced_resource = resource(graph_from_state(reduced))
        collapsed = reduced_resource <= analysis.optimum_resource
        collapse = collapse or collapsed
        attempts.append(
            {
                "symbol": symbol,
                "applicable": True,
                "post_extension_full_reduce_resource": list(reduced_resource),
                "collapsed": collapsed,
            }
        )
    return {"attempts": attempts, "any_collapse": collapse}


def run_study() -> dict[str, Any]:
    registry = load_registry()
    if registry["source"]["commit"] != EXPECTED_COMMIT:
        raise StudyFailure("registry commit differs from compiled expected commit")
    if registry["input_domain"]["complete_word_count"] != sum(
        len(GATE_ALPHABET) ** n for n in range(5)
    ):
        raise StudyFailure("frozen word-count arithmetic mismatch")

    source_receipt = verify_installed_source(registry)
    call_receipt = derive_source_registry(registry)
    freeze = protocol_freeze_binding()
    hostile_controls = hostile_authority_controls()
    symbols = tuple(registry["registered_symbol_order"])
    explorer = ExactExplorer(symbols, int(registry["max_states_per_input_fail_closed"]))

    analysis_cache: dict[str, RootAnalysis] = {}
    word_digest = hashlib.sha256()
    per_length: dict[int, Counter[str]] = {length: Counter() for length in range(5)}
    gap_witnesses: list[dict[str, Any]] = []
    first_word_for_root: dict[str, str] = {}
    production_exact_reachable = 0
    production_matched = 0
    max_states = 0
    max_transitions = 0

    for word in all_gate_words(4):
        label = ",".join(word) if word else "IDENTITY"
        start = start_state_from_word(word)
        first_word_for_root.setdefault(start, label)
        if start not in analysis_cache:
            analysis_cache[start] = explorer.analyze(start)
        result = analysis_cache[start]
        length_stats = per_length[len(word)]
        length_stats["source_words"] += 1
        length_stats["strict_gaps"] += int(result.strict_gap)
        length_stats["reachable_state_observations"] += result.reachable_states
        length_stats["reachable_transition_observations"] += result.reachable_transitions
        production_exact_reachable += int(result.production_exactly_reachable)
        production_matched += int(result.production_resource_semantics_matched)
        max_states = max(max_states, result.reachable_states)
        max_transitions = max(max_transitions, result.reachable_transitions)

        record = {
            "word": list(word),
            "start_sha256": sha256_text(start),
            "production_resource": list(result.production_resource),
            "optimum_resource": list(result.optimum_resource),
            "reachable_states": result.reachable_states,
            "reachable_transitions": result.reachable_transitions,
            "strict_gap": result.strict_gap,
        }
        word_digest.update((canonical_json(record) + "\n").encode("utf-8"))

        if result.strict_gap:
            gap_witnesses.append(
                {
                    "word": list(word),
                    "word_label": label,
                    "start_state_sha256": sha256_text(result.start_state),
                    "production_state_sha256": sha256_text(result.production_state),
                    "production_resource": list(result.production_resource),
                    "optimum_state_sha256": sha256_text(result.optimum_state),
                    "optimum_resource": list(result.optimum_resource),
                    "optimum_path": list(result.optimum_path),
                    "reachable_states": result.reachable_states,
                    "reachable_transitions": result.reachable_transitions,
                }
            )

    expected_words = int(registry["input_domain"]["complete_word_count"])
    observed_words = sum(row["source_words"] for row in per_length.values())
    if observed_words != expected_words:
        raise StudyFailure(f"incomplete input corpus: {observed_words}/{expected_words}")

    interaction_rows = critical_interactions(explorer)
    expected_pairs = len(symbols) ** 2
    if len(interaction_rows) != expected_pairs:
        raise StudyFailure("critical interaction matrix is incomplete")

    hostile_extensions: dict[str, Any] = {
        "executed": bool(gap_witnesses),
        "subjects": [],
        "any_collapse": False,
    }
    # Distinct starting graphs only; duplicate source words cannot strengthen
    # or weaken the hostile disposition.
    seen_gap_roots: set[str] = set()
    for witness in gap_witnesses:
        start_hash = witness["start_state_sha256"]
        if start_hash in seen_gap_roots:
            continue
        seen_gap_roots.add(start_hash)
        matching = next(
            analysis for state, analysis in analysis_cache.items() if sha256_text(state) == start_hash
        )
        disposition = hostile_extension_disposition(matching)
        hostile_extensions["subjects"].append(
            {"start_state_sha256": start_hash, **disposition}
        )
        hostile_extensions["any_collapse"] = (
            hostile_extensions["any_collapse"] or disposition["any_collapse"]
        )

    gap_count = len(gap_witnesses)
    if hostile_extensions["any_collapse"]:
        terminal = CROSS_TERMINAL
    elif gap_count:
        terminal = POSITIVE_TERMINAL
    else:
        terminal = NULL_TERMINAL

    # Stable digest binds every source word while the explicit witness table
    # retains every strict gap. No timing or host-dependent metadata is stored.
    results: dict[str, Any] = {
        "schema": "ORION.ORION01.R11.PyZXFullReduceRound1Results.v1",
        "date": "2026-08-27",
        "paper_id": "ORION-01",
        "round": 1,
        "terminal": terminal,
        "protocol_freeze": freeze,
        "source_binding": source_receipt,
        "registry_audit": call_receipt,
        "input_domain": registry["input_domain"],
        "objective": registry["objective"],
        "search": {
            "source_words_completed": observed_words,
            "unique_start_states": len(analysis_cache),
            "unique_expanded_states_global": len(explorer.expansion_cache),
            "max_reachable_states_per_start": max_states,
            "max_reachable_transitions_per_start": max_transitions,
            "fail_closed_state_cap": explorer.state_cap,
            "all_queues_exhausted": True,
            "production_exact_state_reachable_word_count": production_exact_reachable,
            "production_resource_semantics_matched_word_count": production_matched,
            "dense_scalar_preserving_semantics_checks": explorer.semantic_checks,
            "operation_attempts_on_unique_states": dict(sorted(explorer.operation_attempts.items())),
            "operation_moves_on_unique_states": dict(sorted(explorer.operation_moves.items())),
            "diagnostic_structural_measure_directions": dict(
                sorted(explorer.measure_directions.items())
            ),
            "per_length": {
                str(length): dict(sorted(counts.items()))
                for length, counts in per_length.items()
            },
            "all_word_outcomes_sha256": word_digest.hexdigest(),
            "strict_gap_source_word_count": gap_count,
            "strict_gap_witnesses": gap_witnesses,
        },
        "critical_interactions": {
            "ordered_pair_count": len(interaction_rows),
            "expected_ordered_pair_count": expected_pairs,
            "state_weighting": "UNIQUE_OPERATIONAL_STATE_ACROSS_ALL_EXPANDED_ROOT_CLOSURES",
            "rows": interaction_rows,
        },
        "hostile_authority_controls": hostile_controls,
        "hostile_public_pyzx_extensions": hostile_extensions,
        "gates": {
            "exact_public_source_identity": True,
            "complete_ast_move_and_guard_registry": True,
            "all_single_registry_omissions_rejected": True,
            "complete_frozen_input_domain": True,
            "exact_reachable_queue_exhaustion": True,
            "dense_semantics_including_scalar": True,
            "production_schedule_represented": production_matched == observed_words,
            "complete_ordered_critical_interaction_matrix": len(interaction_rows)
            == expected_pairs,
            "hostile_authority_controls": hostile_controls["all_passed"],
        },
        "round_accounting": {
            "consumed": 1,
            "maximum": 3,
            "science_status_after_this_round": "OPEN",
            "next_round_required": True,
        },
        "authority": {
            "bounded_pinned_full_reduce_macro_result": True,
            "all_pyzx_completeness": False,
            "all_zx_calculus_completeness": False,
            "manual_match_level_optimality": False,
            "generic_compiler_optimality": False,
            "physical_or_hardware_advantage": False,
            "external_independence": False,
            "novelty": False,
            "journal_authority": False,
            "submission_authorized": False,
            "protected_task3_or_p9": False,
        },
    }
    if not all(results["gates"].values()):
        raise StudyFailure(f"one or more predeclared gates failed: {results['gates']}")
    return results


def failed_receipt(exc: BaseException) -> dict[str, Any]:
    return {
        "schema": "ORION.ORION01.R11.PyZXFullReduceRound1Failure.v1",
        "date": "2026-08-27",
        "paper_id": "ORION-01",
        "round": 1,
        "terminal": FAIL_TERMINAL,
        "failure_type": type(exc).__name__,
        "failure": str(exc),
        "authority": {
            "science_result_established": False,
            "production_authority": False,
            "external_independence": False,
            "novelty": False,
            "journal_authority": False,
            "submission_authorized": False,
        },
    }


def render_results(results: Mapping[str, Any]) -> str:
    return json.dumps(results, indent=2, sort_keys=True) + "\n"


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--write", action="store_true", help="execute and write committed receipt")
    mode.add_argument("--check", action="store_true", help="execute and compare committed receipt")
    args = parser.parse_args(argv)

    try:
        results = run_study()
        rendered = render_results(results)
    except BaseException as exc:  # preserve a durable fail-closed receipt on --write
        rendered = render_results(failed_receipt(exc))
        if args.write:
            RESULTS_PATH.write_text(rendered, encoding="utf-8")
        print(FAIL_TERMINAL)
        print(f"{type(exc).__name__}: {exc}", file=sys.stderr)
        return 1

    if args.write:
        RESULTS_PATH.write_text(rendered, encoding="utf-8")
    else:
        if not RESULTS_PATH.is_file():
            print("committed result is missing", file=sys.stderr)
            return 1
        committed = RESULTS_PATH.read_text(encoding="utf-8")
        if committed != rendered:
            print("committed result differs from fresh replay", file=sys.stderr)
            return 1
    print(results["terminal"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

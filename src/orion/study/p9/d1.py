"""P9 D1 exact algorithmic/procedural method-transfer benchmark.

D1 lifts the already frozen P1/P3 authored method structures into a deterministic
train/dev/test benchmark with a whole-domain holdout.  Surface labels are
reminted independently of semantic gold.  All labels are evaluator-side and are
bounded structural comparison states only.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from hashlib import sha256
from typing import Mapping, Sequence

from orion.transfer.v2.canonical import content_digest
from orion.transfer.v2.p1_method_realization import MethodRealization, build_method_realization


class D1Domain(str, Enum):
    NUMERICAL = "numerical_methods"
    GRAPH = "graph_algorithms"
    WORKFLOW = "transactional_workflows"
    CACHE = "cache_admission"


class D1Split(str, Enum):
    TRAIN = "TRAIN"
    DEV = "DEV"
    TEST = "TEST"


class D1Label(str, Enum):
    ALIGNED = "ALIGNED"
    OBSTRUCTION = "OBSTRUCTION"
    UNRESOLVED = "UNRESOLVED"


class D1View(str, Enum):
    TRANSCRIPT = "TRANSCRIPT"
    UNTYPED = "UNTYPED"
    TYPED = "TYPED"
    TYPED_SERIALIZED = "TYPED_SERIALIZED"


COMPARISON_COORDINATES = (
    "preconditions",
    "invariants",
    "effects",
    "progress_measure",
    "terminal_condition",
    "reconstruction_map",
    "failure_modes",
    "dependencies",
)

SINGLE_MUTATIONS = COMPARISON_COORDINATES
DOUBLE_MUTATIONS = (
    ("preconditions", "invariants"),
    ("effects", "reconstruction_map"),
    ("dependencies", "failure_modes"),
)


def _d(value: str) -> str:
    return content_digest({"p9-d1": value})


def _opaque(prefix: str, material: str, *, length: int = 16) -> str:
    digest = sha256(material.encode("utf-8")).hexdigest()
    return prefix + digest[:length]


def _base_method(name: str) -> MethodRealization:
    common = dict(
        source_digest=_d(name),
        source_version="p1p3-authored-fixture-v1",
        authority_boundary="REPRESENTATION_ONLY",
    )
    if name == "bisection":
        return build_method_realization(
            method_id=name,
            target_role="bounded_monotone_localization",
            preconditions=("ordered_domain", "bracketed_target", "monotone_response"),
            assumptions=("deterministic_response",),
            resources=("oracle",),
            representation_in="ordered_interval",
            representation_out="shrinking_interval",
            mechanics=("measure_midpoint", "discard_inconsistent_half"),
            dependencies=(("measure_midpoint", "discard_inconsistent_half"),),
            invariants=("target_remains_bracketed",),
            progress_measure="interval_width_decreases",
            effects=("shrink_candidate_interval",),
            terminal_condition="interval_width_below_tolerance",
            reconstruction_map="return_interval_representative",
            failure_modes=("non_monotone_response", "target_not_bracketed"),
            lineage=("donor:bisection",),
            **common,
        )
    if name == "threshold_calibration":
        return build_method_realization(
            method_id=name,
            target_role="bounded_monotone_localization",
            preconditions=("ordered_domain", "bracketed_target", "monotone_response"),
            assumptions=("deterministic_response",),
            resources=("oracle",),
            representation_in="ordered_interval",
            representation_out="shrinking_interval",
            mechanics=("sample_candidate", "discard_inconsistent_region"),
            dependencies=(("sample_candidate", "discard_inconsistent_region"),),
            invariants=("target_remains_bracketed",),
            progress_measure="interval_width_decreases",
            effects=("shrink_candidate_interval",),
            terminal_condition="interval_width_below_tolerance",
            reconstruction_map="return_interval_representative",
            failure_modes=("non_monotone_response", "target_not_bracketed"),
            lineage=("donor:threshold",),
            **common,
        )
    if name == "nonmonotone_midpoint":
        return build_method_realization(
            method_id=name,
            target_role="bounded_localization",
            preconditions=("ordered_domain", "bracketed_target"),
            assumptions=("deterministic_response",),
            resources=("oracle",),
            representation_in="ordered_interval",
            representation_out="shrinking_interval",
            mechanics=("measure_midpoint", "discard_half"),
            dependencies=(("measure_midpoint", "discard_half"),),
            invariants=("finite_values",),
            progress_measure="interval_width_decreases",
            effects=("shrink_candidate_interval",),
            terminal_condition="interval_width_below_tolerance",
            reconstruction_map="return_interval_representative",
            failure_modes=("discarded_true_target",),
            lineage=("donor:nonmonotone",),
            **common,
        )
    if name in {"queue_bfs", "layer_frontier_bfs"}:
        mechanics = (
            ("dequeue", "enqueue_unseen")
            if name == "queue_bfs"
            else ("expand_frontier", "form_next_frontier")
        )
        return build_method_realization(
            method_id=name,
            target_role="unweighted_shortest_path_layers",
            preconditions=("unweighted_graph",),
            assumptions=("finite_graph",),
            resources=("adjacency_access",),
            representation_in="source_graph",
            representation_out="distance_layers",
            mechanics=mechanics,
            dependencies=((mechanics[0], mechanics[1]),),
            invariants=("first_visit_has_minimum_hop_distance",),
            progress_measure="visited_set_grows",
            effects=("discover_next_distance_layer",),
            terminal_condition="target_found_or_frontier_empty",
            reconstruction_map="parent_links_to_path",
            failure_modes=("target_unreachable",),
            lineage=(f"donor:{name}",),
            **common,
        )
    if name == "stack_dfs":
        return build_method_realization(
            method_id=name,
            target_role="graph_reachability",
            preconditions=("finite_graph",),
            assumptions=(),
            resources=("adjacency_access",),
            representation_in="source_graph",
            representation_out="depth_first_tree",
            mechanics=("pop_stack", "push_unseen"),
            dependencies=(("pop_stack", "push_unseen"),),
            invariants=("visited_nodes_are_reachable",),
            progress_measure="visited_set_grows",
            effects=("discover_reachable_node",),
            terminal_condition="target_found_or_stack_empty",
            reconstruction_map="parent_links_to_some_path",
            failure_modes=("target_unreachable",),
            lineage=("donor:dfs",),
            **common,
        )
    if name in {"transaction_rollback", "deployment_rollback"}:
        mechanics = (
            ("identify_changed_units", "restore_prior_snapshot")
            if name == "transaction_rollback"
            else ("identify_changed_components", "restore_prior_release")
        )
        return build_method_realization(
            method_id=name,
            target_role="bounded_state_recovery",
            preconditions=("prior_good_state_available", "changed_footprint_known"),
            assumptions=("restore_operation_idempotent",),
            resources=("snapshot_store",),
            representation_in="failed_state_plus_change_set",
            representation_out="restored_state",
            mechanics=mechanics,
            dependencies=((mechanics[0], mechanics[1]),),
            invariants=("unchanged_state_preserved",),
            progress_measure="unrecovered_footprint_decreases",
            effects=("restore_changed_footprint",),
            terminal_condition="all_changed_units_restored",
            reconstruction_map="identity_on_unaffected_state",
            failure_modes=("snapshot_missing", "footprint_unknown"),
            lineage=(f"donor:{name}",),
            **common,
        )
    if name == "opaque_recovery":
        return build_method_realization(
            method_id=name,
            target_role="bounded_state_recovery",
            preconditions=("prior_good_state_available", "changed_footprint_known"),
            assumptions=("restore_operation_idempotent",),
            resources=("recovery_tool",),
            representation_in="failed_state_plus_change_set",
            representation_out="restored_state",
            mechanics=("invoke_recovery",),
            dependencies=(),
            invariants=("unchanged_state_preserved",),
            progress_measure=None,
            effects=("restore_changed_footprint",),
            terminal_condition="all_changed_units_restored",
            reconstruction_map=None,
            failure_modes=("unknown_failure",),
            lineage=("donor:opaque",),
            unknown_coordinates=("progress_measure", "reconstruction_map"),
            **common,
        )
    if name == "lru_eviction":
        return build_method_realization(
            method_id=name,
            target_role="bounded_residency_reclamation",
            preconditions=(
                "bounded_residency_budget",
                "recency_stamp_observable",
                "reuse_locality_present",
            ),
            assumptions=("stable_residency_budget",),
            resources=("recency_index",),
            representation_in="occupied_residency_set",
            representation_out="reclaimed_residency_set",
            mechanics=("consult_recency_stamp", "release_least_recent_entry"),
            dependencies=(("consult_recency_stamp", "release_least_recent_entry"),),
            invariants=("residency_never_exceeds_budget",),
            progress_measure="stale_residency_fraction_decreases",
            effects=("release_stale_residency",),
            terminal_condition="residency_within_budget",
            reconstruction_map="return_surviving_residency_set",
            failure_modes=("uniform_reuse_profile", "recency_stamp_unavailable"),
            lineage=("donor:recency_reclamation",),
            **common,
        )
    if name == "clock_sweep_eviction":
        return build_method_realization(
            method_id=name,
            target_role="bounded_residency_reclamation",
            preconditions=(
                "bounded_residency_budget",
                "recency_stamp_observable",
                "reuse_locality_present",
            ),
            assumptions=("stable_residency_budget",),
            resources=("recency_index",),
            representation_in="occupied_residency_set",
            representation_out="reclaimed_residency_set",
            mechanics=("advance_sweep_hand", "release_unmarked_entry"),
            dependencies=(("advance_sweep_hand", "release_unmarked_entry"),),
            invariants=("residency_never_exceeds_budget",),
            progress_measure="stale_residency_fraction_decreases",
            effects=("release_stale_residency",),
            terminal_condition="residency_within_budget",
            reconstruction_map="return_surviving_residency_set",
            failure_modes=("uniform_reuse_profile", "recency_stamp_unavailable"),
            lineage=("donor:sweep_reclamation",),
            **common,
        )
    if name == "uniform_random_release":
        return build_method_realization(
            method_id=name,
            target_role="unbounded_residency_release",
            preconditions=("bounded_residency_budget",),
            assumptions=("stable_residency_budget",),
            resources=("uniform_sampler",),
            representation_in="occupied_residency_set",
            representation_out="reclaimed_residency_set",
            mechanics=("draw_uniform_entry", "release_drawn_entry"),
            dependencies=(("draw_uniform_entry", "release_drawn_entry"),),
            invariants=("residency_count_is_finite",),
            progress_measure="residency_count_decreases",
            effects=("release_arbitrary_residency",),
            terminal_condition="residency_within_budget",
            reconstruction_map="return_remaining_residency_set",
            failure_modes=("hot_entry_released",),
            lineage=("donor:uniform_release",),
            **common,
        )
    raise KeyError(name)


DOMAIN_ANALOGUES: Mapping[D1Domain, tuple[str, str]] = {
    D1Domain.NUMERICAL: ("bisection", "threshold_calibration"),
    D1Domain.GRAPH: ("queue_bfs", "layer_frontier_bfs"),
    D1Domain.WORKFLOW: ("transaction_rollback", "deployment_rollback"),
    D1Domain.CACHE: ("lru_eviction", "clock_sweep_eviction"),
}

DOMAIN_FALSE_CONTROLS: Mapping[D1Domain, tuple[str, str | None]] = {
    D1Domain.NUMERICAL: ("bisection", "nonmonotone_midpoint"),
    D1Domain.GRAPH: ("queue_bfs", "stack_dfs"),
    D1Domain.WORKFLOW: ("transaction_rollback", None),
    D1Domain.CACHE: ("lru_eviction", "uniform_random_release"),
}


def _dependency_signature(method: MethodRealization) -> tuple[tuple[int, int], ...]:
    """Canonical dependency topology over local action-role indices.

    Action names are surface realization details for D1.  The deterministic local
    order is the method's canonical mechanics order as already stored by P1.
    """

    index = {name: position for position, name in enumerate(method.mechanics)}
    return tuple(sorted((index[left], index[right]) for left, right in method.dependencies))


def _coordinate_value(method: MethodRealization, coordinate: str) -> object:
    if coordinate == "dependencies":
        return _dependency_signature(method)
    return getattr(method, coordinate)


def _unknown_for_coordinate(method: MethodRealization, coordinate: str) -> bool:
    return coordinate in set(method.unknown_coordinates)


def classify_methods(left: MethodRealization, right: MethodRealization) -> D1Label:
    """Exact D1 gold without surface names/domain identifiers."""

    left.verify()
    right.verify()
    for coordinate in COMPARISON_COORDINATES:
        if _unknown_for_coordinate(left, coordinate) or _unknown_for_coordinate(right, coordinate):
            return D1Label.UNRESOLVED
    for coordinate in COMPARISON_COORDINATES:
        if _coordinate_value(left, coordinate) != _coordinate_value(right, coordinate):
            return D1Label.OBSTRUCTION
    return D1Label.ALIGNED


def _rebuild(method: MethodRealization, *, method_id: str, **changes: object) -> MethodRealization:
    values: dict[str, object] = {
        "method_id": method_id,
        "source_digest": _d(method_id),
        "source_version": "p9-d1-generated-v1",
        "target_role": method.target_role,
        "preconditions": method.preconditions,
        "assumptions": method.assumptions,
        "resources": method.resources,
        "representation_in": method.representation_in,
        "representation_out": method.representation_out,
        "mechanics": method.mechanics,
        "dependencies": method.dependencies,
        "invariants": method.invariants,
        "progress_measure": method.progress_measure,
        "effects": method.effects,
        "terminal_condition": method.terminal_condition,
        "reconstruction_map": method.reconstruction_map,
        "failure_modes": method.failure_modes,
        "lineage": method.lineage,
        "authority_boundary": method.authority_boundary,
        "unknown_coordinates": method.unknown_coordinates,
    }
    values.update(changes)
    return build_method_realization(**values)  # type: ignore[arg-type]


def _mutated_value(method: MethodRealization, coordinate: str, salt: str) -> object:
    token = "x_" + sha256(f"{salt}|{coordinate}".encode("utf-8")).hexdigest()[:12]
    if coordinate in {"preconditions", "invariants", "effects", "failure_modes"}:
        original = tuple(getattr(method, coordinate))
        return tuple(sorted((*original, token)))
    if coordinate == "progress_measure":
        return token
    if coordinate == "terminal_condition":
        return token
    if coordinate == "reconstruction_map":
        return token
    if coordinate == "dependencies":
        mechanics = tuple(method.mechanics)
        if len(mechanics) >= 2:
            return ((mechanics[1], mechanics[0]),)
        return ()
    raise ValueError(f"unsupported D1 mutation coordinate: {coordinate}")


def mutate_method(
    method: MethodRealization,
    *,
    coordinates: Sequence[str],
    seed: str,
) -> MethodRealization:
    changes: dict[str, object] = {}
    for coordinate in coordinates:
        if coordinate not in COMPARISON_COORDINATES:
            raise ValueError(f"unsupported D1 coordinate: {coordinate}")
        changes[coordinate] = _mutated_value(method, coordinate, seed)
    method_id = _opaque("m", f"{seed}|mutated|{','.join(sorted(coordinates))}")
    return _rebuild(method, method_id=method_id, **changes)


def unresolved_method(method: MethodRealization, *, seed: str) -> MethodRealization:
    unknown = tuple(sorted(set((*method.unknown_coordinates, "reconstruction_map"))))
    return _rebuild(
        method,
        method_id=_opaque("m", f"{seed}|unresolved"),
        reconstruction_map=None,
        unknown_coordinates=unknown,
    )


@dataclass(frozen=True)
class D1Instance:
    instance_id: str
    domain: D1Domain
    split: D1Split
    left: MethodRealization
    right: MethodRealization
    label: D1Label
    mutation_coordinates: tuple[str, ...]
    surface_left: tuple[str, ...]
    surface_right: tuple[str, ...]
    surface_role_left: str
    surface_role_right: str

    def verify(self) -> None:
        self.left.verify()
        self.right.verify()
        if not self.instance_id:
            raise ValueError("D1 instance id required")
        if self.label is not classify_methods(self.left, self.right):
            raise ValueError("D1 gold does not match exact semantic classifier")
        if not self.surface_left or not self.surface_right:
            raise ValueError("D1 transcript surfaces required")
        if any(not value for value in (*self.surface_left, *self.surface_right)):
            raise ValueError("empty D1 surface token")

    def model_payload(self, view: D1View) -> dict[str, object]:
        self.verify()
        if view is D1View.TRANSCRIPT:
            return {
                "schema": "P9.D1Transcript.v1",
                "left_role": self.surface_role_left,
                "right_role": self.surface_role_right,
                "left_actions": list(self.surface_left),
                "right_actions": list(self.surface_right),
                "left_action_count": len(self.surface_left),
                "right_action_count": len(self.surface_right),
            }
        if view is D1View.UNTYPED:
            return {
                "schema": "P9.D1Untyped.v1",
                "left": _untyped_payload(self.left),
                "right": _untyped_payload(self.right),
            }
        typed = {
            "schema": "P9.D1Typed.v1",
            "left": _typed_payload(self.left),
            "right": _typed_payload(self.right),
        }
        if view is D1View.TYPED:
            return typed
        if view is D1View.TYPED_SERIALIZED:
            # Same semantic information, serialized canonically as a deterministic
            # sequence.  It is not natural language and adds no extra coordinate.
            return {
                "schema": "P9.D1TypedSerialized.v1",
                "sequence": _serialize_typed(typed),
            }
        raise ValueError(f"unsupported D1 view: {view}")

    def manifest_entry(self) -> dict[str, object]:
        return {
            "instance_id": self.instance_id,
            "domain": self.domain.value,
            "split": self.split.value,
            "left_digest": self.left.digest,
            "right_digest": self.right.digest,
            "label": self.label.value,
            "mutation_coordinates": list(self.mutation_coordinates),
        }


def _coordinate_shape(method: MethodRealization, coordinate: str) -> object:
    value = _coordinate_value(method, coordinate)
    if isinstance(value, tuple):
        return {"present": True, "kind": "sequence", "length": len(value)}
    return {"present": value is not None, "kind": "scalar"}


def _untyped_payload(method: MethodRealization) -> dict[str, object]:
    return {
        "coordinates": {
            coordinate: {
                **_coordinate_shape(method, coordinate),
                "unknown": _unknown_for_coordinate(method, coordinate),
            }
            for coordinate in COMPARISON_COORDINATES
        },
        "dependency_topology": [list(edge) for edge in _dependency_signature(method)],
    }


def _typed_payload(method: MethodRealization) -> dict[str, object]:
    return {
        "preconditions": list(method.preconditions),
        "invariants": list(method.invariants),
        "effects": list(method.effects),
        "progress_measure": method.progress_measure,
        "terminal_condition": method.terminal_condition,
        "reconstruction_map": method.reconstruction_map,
        "failure_modes": list(method.failure_modes),
        "dependencies": [list(edge) for edge in _dependency_signature(method)],
        "unknown_coordinates": [
            coordinate for coordinate in COMPARISON_COORDINATES if _unknown_for_coordinate(method, coordinate)
        ],
    }


def _serialize_typed(value: object, *, path: str = "root") -> list[str]:
    tokens: list[str] = []
    if isinstance(value, Mapping):
        for key in sorted(value):
            tokens.extend(_serialize_typed(value[key], path=f"{path}.{key}"))
    elif isinstance(value, (list, tuple)):
        tokens.append(f"{path}:LEN={len(value)}")
        for child in value:
            tokens.extend(_serialize_typed(child, path=f"{path}[]"))
    elif value is None:
        tokens.append(f"{path}=<NONE>")
    else:
        tokens.append(f"{path}={value}")
    return tokens


class SurfaceRemintScope(str, Enum):
    """How widely one reminted surface token is shared.

    ``D1_PROTOCOL_V1.json`` declares ``surface_remint`` with
    ``mechanic_action_names: true`` and ``surface_role_names: true``. It does not
    say at what *scope* a reminted name is reused, and the two readings are not
    equivalent:

    ``PER_INSTANCE`` seeds every token on the instance that emitted it, so no
    token occurs twice anywhere in the corpus. This is what the frozen run used
    and what every committed D1 result was produced under; it is the default and
    nothing here changes it.

    ``PER_SPLIT`` seeds a token on the mechanic it stands for and the split it
    appears in, so the same action carries the same opaque name throughout a
    split and a different one in every other split. That is still a remint --- no
    authored name reaches the model, and nothing transfers across the holdout ---
    but the vocabulary is shared inside a split rather than minted per row.

    The reading matters because ``TRANSCRIPT_BAG``'s protected denominator is one
    under ``PER_INSTANCE``, and :func:`orion.study.p9.transfer_margins.d1_view_collapse_report`
    reports "no corpus could have contained these keys" as the cause. This enum
    exists so that sentence can be *checked* rather than believed: the report
    rebuilds the corpus under ``PER_SPLIT`` and measures whether the denominator
    moves. It carries no scientific authority and promotes no D1 result.
    """

    PER_INSTANCE = "PER_INSTANCE"
    PER_SPLIT = "PER_SPLIT"


def _surface_tokens(seed: str, side: str, count: int) -> tuple[str, ...]:
    return tuple(_opaque("s", f"{seed}|surface|{side}|{index}") for index in range(count))


def _split_scoped_surface_tokens(
    split: D1Split, side: str, mechanics: Sequence[str]
) -> tuple[str, ...]:
    return tuple(_opaque("s", f"alphabet|{split.value}|{side}|{name}") for name in mechanics)


def _instance(
    *,
    domain: D1Domain,
    split: D1Split,
    seed: str,
    variant: str,
    mutation_coordinates: Sequence[str] = (),
    unresolved: bool = False,
    surface_remint_scope: SurfaceRemintScope = SurfaceRemintScope.PER_INSTANCE,
) -> D1Instance:
    left_name, right_name = DOMAIN_ANALOGUES[domain]
    left = _base_method(left_name)
    right = _base_method(right_name)
    if unresolved:
        right = unresolved_method(right, seed=f"{seed}|{variant}")
    elif mutation_coordinates:
        right = mutate_method(right, coordinates=mutation_coordinates, seed=f"{seed}|{variant}")
    label = classify_methods(left, right)
    instance = D1Instance(
        instance_id=_opaque("i", f"{seed}|{domain.value}|{split.value}|{variant}"),
        domain=domain,
        split=split,
        left=left,
        right=right,
        label=label,
        mutation_coordinates=tuple(sorted(mutation_coordinates)),
        surface_left=(
            _surface_tokens(f"{seed}|{variant}", "left", len(left.mechanics))
            if surface_remint_scope is SurfaceRemintScope.PER_INSTANCE
            else _split_scoped_surface_tokens(split, "left", left.mechanics)
        ),
        surface_right=(
            _surface_tokens(f"{seed}|{variant}", "right", len(right.mechanics))
            if surface_remint_scope is SurfaceRemintScope.PER_INSTANCE
            else _split_scoped_surface_tokens(split, "right", right.mechanics)
        ),
        surface_role_left=(
            _opaque("s", f"{seed}|{variant}|left-role")
            if surface_remint_scope is SurfaceRemintScope.PER_INSTANCE
            else _opaque("s", f"role|{split.value}|left|{left.target_role}")
        ),
        surface_role_right=(
            _opaque("s", f"{seed}|{variant}|right-role")
            if surface_remint_scope is SurfaceRemintScope.PER_INSTANCE
            else _opaque("s", f"role|{split.value}|right|{right.target_role}")
        ),
    )
    instance.verify()
    return instance


@dataclass(frozen=True)
class D1Dataset:
    seed: str
    train: tuple[D1Instance, ...]
    dev: tuple[D1Instance, ...]
    test: tuple[D1Instance, ...]
    manifest_digest: str

    def verify(self) -> None:
        if not self.seed:
            raise ValueError("D1 dataset seed required")
        for split, instances in (
            (D1Split.TRAIN, self.train),
            (D1Split.DEV, self.dev),
            (D1Split.TEST, self.test),
        ):
            for instance in instances:
                instance.verify()
                if instance.split is not split:
                    raise ValueError("D1 split identity mismatch")
        ids = [instance.instance_id for instance in (*self.train, *self.dev, *self.test)]
        if len(ids) != len(set(ids)):
            raise ValueError("D1 instance identity collision across splits")
        if content_digest(self.manifest()) != self.manifest_digest:
            raise ValueError("D1 manifest digest mismatch")

    def manifest(self) -> dict[str, object]:
        return {
            "schema": "P9.D1Dataset.v1",
            "seed_digest": content_digest(self.seed),
            "train": [instance.manifest_entry() for instance in self.train],
            "dev": [instance.manifest_entry() for instance in self.dev],
            "test": [instance.manifest_entry() for instance in self.test],
            "authority": "EVALUATOR_ONLY_NO_SCIENTIFIC_AUTHORITY",
        }


def _split_instances(
    *,
    seed: str,
    split: D1Split,
    domains: Sequence[D1Domain],
    instances_per_base_pair: int,
    include_double: bool,
    surface_remint_scope: SurfaceRemintScope = SurfaceRemintScope.PER_INSTANCE,
) -> tuple[D1Instance, ...]:
    rows: list[D1Instance] = []
    for domain in domains:
        for index in range(instances_per_base_pair):
            local = f"{seed}|{split.value}|{domain.value}|{index}"
            rows.append(_instance(
                    domain=domain,
                    split=split,
                    seed=local,
                    variant="aligned",
                    surface_remint_scope=surface_remint_scope,
                ))
            coordinate = SINGLE_MUTATIONS[index % len(SINGLE_MUTATIONS)]
            rows.append(
                _instance(
                    domain=domain,
                    split=split,
                    seed=local,
                    variant=f"single-{coordinate}",
                    mutation_coordinates=(coordinate,),
                    surface_remint_scope=surface_remint_scope,
                )
            )
            rows.append(
                _instance(
                    domain=domain,
                    split=split,
                    seed=local,
                    variant="unresolved",
                    unresolved=True,
                    surface_remint_scope=surface_remint_scope,
                )
            )
            if include_double:
                double = DOUBLE_MUTATIONS[index % len(DOUBLE_MUTATIONS)]
                rows.append(
                    _instance(
                        domain=domain,
                        split=split,
                        seed=local,
                        variant=f"double-{double[0]}-{double[1]}",
                        mutation_coordinates=double,
                        surface_remint_scope=surface_remint_scope,
                    )
                )
    return tuple(rows)


def generate_d1_dataset(
    *,
    seed: str = "p9-d1-method-transfer-v1",
    train_instances_per_base_pair: int = 48,
    dev_instances_per_base_pair: int = 16,
    test_instances_per_base_pair: int = 32,
    surface_remint_scope: SurfaceRemintScope = SurfaceRemintScope.PER_INSTANCE,
) -> D1Dataset:
    train = _split_instances(
        seed=seed,
        split=D1Split.TRAIN,
        domains=(D1Domain.NUMERICAL, D1Domain.GRAPH),
        instances_per_base_pair=train_instances_per_base_pair,
        include_double=False,
        surface_remint_scope=surface_remint_scope,
    )
    dev = _split_instances(
        seed=seed,
        split=D1Split.DEV,
        domains=(D1Domain.NUMERICAL, D1Domain.GRAPH),
        instances_per_base_pair=dev_instances_per_base_pair,
        include_double=False,
        surface_remint_scope=surface_remint_scope,
    )
    test = _split_instances(
        seed=seed,
        split=D1Split.TEST,
        domains=(D1Domain.WORKFLOW,),
        instances_per_base_pair=test_instances_per_base_pair,
        include_double=True,
        surface_remint_scope=surface_remint_scope,
    )
    provisional = {
        "schema": "P9.D1Dataset.v1",
        "seed_digest": content_digest(seed),
        "train": [instance.manifest_entry() for instance in train],
        "dev": [instance.manifest_entry() for instance in dev],
        "test": [instance.manifest_entry() for instance in test],
        "authority": "EVALUATOR_ONLY_NO_SCIENTIFIC_AUTHORITY",
    }
    dataset = D1Dataset(seed, train, dev, test, content_digest(provisional))
    dataset.verify()
    return dataset


__all__ = [
    "COMPARISON_COORDINATES",
    "D1Dataset",
    "SurfaceRemintScope",
    "D1Domain",
    "D1Instance",
    "D1Label",
    "D1Split",
    "D1View",
    "DOUBLE_MUTATIONS",
    "SINGLE_MUTATIONS",
    "classify_methods",
    "generate_d1_dataset",
    "mutate_method",
    "unresolved_method",
]

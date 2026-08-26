from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum

from .group import GroupSpec, InputError, Vector


class FactorizationStatus(StrEnum):
    POSITIVE = "POSITIVE"
    NEGATIVE = "NEGATIVE"
    CANNOT_CHECK_RESOURCE_BOUND = "CANNOT_CHECK_RESOURCE_BOUND"


@dataclass(frozen=True, slots=True)
class FactorizationCertificate:
    bins: tuple[tuple[int, ...], ...]


@dataclass(frozen=True, slots=True)
class FactorizationResult:
    status: FactorizationStatus
    certificate: FactorizationCertificate | None
    sequence_length: int
    k: int
    layers_completed: int
    states_explored: int
    frontier_peak: int
    exhaustive: bool


BinPayload = tuple[bool, Vector, tuple[int, ...]]
StateKey = tuple[tuple[bool, Vector], ...]
StatePayload = tuple[BinPayload, ...]


def _validate_k(k: object) -> int:
    if isinstance(k, bool) or not isinstance(k, int) or k < 1:
        raise InputError("k must be a positive integer")
    return k


def _sort_payload(bins: list[BinPayload]) -> StatePayload:
    return tuple(sorted(bins, key=lambda item: (item[0], item[1], item[2])))


def _key(payload: StatePayload) -> StateKey:
    return tuple((used, vector_sum) for used, vector_sum, _indices in payload)


def find_disjoint_zero_sums(
    spec: GroupSpec,
    sequence: object,
    k: object,
    *,
    max_states: int | None = None,
) -> FactorizationResult:
    bin_count = _validate_k(k)
    vectors = spec.validate_sequence(sequence)
    if max_states is not None and (
        isinstance(max_states, bool) or not isinstance(max_states, int) or max_states < 1
    ):
        raise InputError("max_states must be a positive integer")

    initial_payload: StatePayload = tuple((False, spec.zero, ()) for _ in range(bin_count))
    frontier: dict[StateKey, StatePayload] = {_key(initial_payload): initial_payload}
    states_explored = 0
    frontier_peak = 1
    target: StateKey = tuple((True, spec.zero) for _ in range(bin_count))

    for index, vector in enumerate(vectors):
        next_frontier: dict[StateKey, StatePayload] = dict(frontier)  # item unused
        for payload in frontier.values():
            seen_bin_summaries: set[tuple[bool, Vector]] = set()
            for bin_index, (used, vector_sum, indices) in enumerate(payload):
                summary = (used, vector_sum)
                if summary in seen_bin_summaries:
                    continue
                seen_bin_summaries.add(summary)
                states_explored += 1
                updated = list(payload)
                updated[bin_index] = (True, spec.add(vector_sum, vector), (*indices, index))
                canonical_payload = _sort_payload(updated)
                state_key = _key(canonical_payload)
                if state_key not in next_frontier:
                    if max_states is not None and len(next_frontier) >= max_states:
                        return FactorizationResult(
                            status=FactorizationStatus.CANNOT_CHECK_RESOURCE_BOUND,
                            certificate=None,
                            sequence_length=len(vectors),
                            k=bin_count,
                            layers_completed=index,
                            states_explored=states_explored,
                            frontier_peak=max(frontier_peak, len(next_frontier)),
                            exhaustive=False,
                        )
                    next_frontier[state_key] = canonical_payload
        frontier = next_frontier
        frontier_peak = max(frontier_peak, len(frontier))
        if target in frontier:
            certificate = FactorizationCertificate(
                bins=tuple(indices for _used, _sum, indices in frontier[target])
            )
            assert_valid_certificate(spec, vectors, bin_count, certificate)
            return FactorizationResult(
                status=FactorizationStatus.POSITIVE,
                certificate=certificate,
                sequence_length=len(vectors),
                k=bin_count,
                layers_completed=index + 1,
                states_explored=states_explored,
                frontier_peak=frontier_peak,
                exhaustive=True,
            )

    return FactorizationResult(
        status=FactorizationStatus.NEGATIVE,
        certificate=None,
        sequence_length=len(vectors),
        k=bin_count,
        layers_completed=len(vectors),
        states_explored=states_explored,
        frontier_peak=frontier_peak,
        exhaustive=True,
    )


def certificate_errors(
    spec: GroupSpec, sequence: object, k: object, certificate: object
) -> tuple[str, ...]:
    errors: list[str] = []
    try:
        vectors = spec.validate_sequence(sequence)
        bin_count = _validate_k(k)
    except (InputError, TypeError) as exc:
        return (f"invalid checker input: {exc}",)
    if not isinstance(certificate, FactorizationCertificate):
        return ("certificate has the wrong type",)
    if not isinstance(certificate.bins, tuple) or len(certificate.bins) != bin_count:
        return (f"certificate must contain exactly {bin_count} bins",)
    used_indices: set[int] = set()
    for bin_number, indices in enumerate(certificate.bins):
        if not isinstance(indices, tuple):
            errors.append(f"bin {bin_number} indices must be a tuple")
            continue
        if not indices:
            errors.append(f"bin {bin_number} is empty")
            continue
        local: set[int] = set()
        valid_indices: list[int] = []
        for index in indices:
            if isinstance(index, bool) or not isinstance(index, int):
                errors.append(f"bin {bin_number} has a non-integer index")
                continue
            if not 0 <= index < len(vectors):
                errors.append(f"bin {bin_number} index {index} is out of range")
                continue
            if index in local:
                errors.append(f"bin {bin_number} repeats index {index}")
                continue
            if index in used_indices:
                errors.append(f"index {index} appears in multiple bins")
                continue
            local.add(index)
            used_indices.add(index)
            valid_indices.append(index)
        if (
            len(valid_indices) == len(indices)
            and spec.sum_vectors(vectors[i] for i in valid_indices) != spec.zero
        ):
            errors.append(f"bin {bin_number} does not sum to zero")
    return tuple(errors)


def verify_factorization_certificate(
    spec: GroupSpec, sequence: object, k: object, certificate: object
) -> bool:
    return not certificate_errors(spec, sequence, k, certificate)


def assert_valid_certificate(
    spec: GroupSpec, sequence: object, k: object, certificate: object
) -> None:
    errors = certificate_errors(spec, sequence, k, certificate)
    if errors:
        raise ValueError("; ".join(errors))

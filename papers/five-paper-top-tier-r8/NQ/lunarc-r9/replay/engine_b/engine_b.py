"""Clean-room Engine B: a SAT encoding derived from primitive C_5^3 addition.

The implementation deliberately does not use the repository's existing NQ
algorithms. Public programme material exposed expected counts, so this lane is
structurally independent but not blinded and cannot itself establish external
independent-replay authority.
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from itertools import product
from typing import Any, Iterable, Mapping, Sequence


SUBJECT_COMMIT = "0c451e862a0eeddac7c673813c4dc499f134b088"
ZERO = 0
GROUP_ELEMENTS = tuple(range(125))


class CertificateMismatch(RuntimeError):
    """Raised when a witness/proof certificate does not verify."""


def _require_element(element: int) -> int:
    if type(element) is not int:
        raise TypeError("group element must be an integer")
    if not 0 <= element < 125:
        raise ValueError("group element must lie in the canonical range 0..124")
    return element


def encode_element(coordinates: Sequence[int]) -> int:
    value = tuple(coordinates)
    if len(value) != 3 or any(
        type(coordinate) is not int or not 0 <= coordinate < 5 for coordinate in value
    ):
        raise ValueError("group element coordinates must be three residues in 0..4")
    return value[0] + 5 * value[1] + 25 * value[2]


def decode_element(element: int) -> tuple[int, int, int]:
    value = _require_element(element)
    return value % 5, (value // 5) % 5, value // 25


def add(left: int, right: int) -> int:
    """Primitive componentwise addition in the fixed base-five encoding."""

    lx, ly, lz = decode_element(left)
    rx, ry, rz = decode_element(right)
    return encode_element(((lx + rx) % 5, (ly + ry) % 5, (lz + rz) % 5))


def negate(element: int) -> int:
    x, y, z = decode_element(element)
    return encode_element(((-x) % 5, (-y) % 5, (-z) % 5))


def sum_elements(elements: Iterable[int]) -> int:
    total = ZERO
    for element in elements:
        total = add(total, element)
    return total


def _canonical(value: Any) -> Any:
    if isinstance(value, tuple):
        return [_canonical(item) for item in value]
    if isinstance(value, list):
        return [_canonical(item) for item in value]
    if isinstance(value, dict):
        return {str(key): _canonical(item) for key, item in sorted(value.items())}
    if value is None or type(value) in {str, int, bool}:
        return value
    raise TypeError(f"value is not canonical JSON: {type(value).__name__}")


def canonical_json_bytes(value: Any) -> bytes:
    return json.dumps(
        _canonical(value),
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=True,
        allow_nan=False,
    ).encode("ascii")


@dataclass(frozen=True)
class CNF:
    variable_count: int
    clauses: tuple[tuple[int, ...], ...]

    def __post_init__(self) -> None:
        if type(self.variable_count) is not int or self.variable_count < 0:
            raise ValueError("CNF variable count must be nonnegative")
        for clause in self.clauses:
            if type(clause) is not tuple or not clause:
                raise ValueError("CNF clauses must be nonempty exact tuples")
            if any(
                type(literal) is not int or literal == 0 or abs(literal) > self.variable_count
                for literal in clause
            ):
                raise ValueError("CNF clause contains an invalid literal")


class _Builder:
    def __init__(self) -> None:
        self.variable_count = 0
        self.clauses: list[tuple[int, ...]] = []

    def variable(self) -> int:
        self.variable_count += 1
        return self.variable_count

    def clause(self, *literals: int) -> None:
        self.clauses.append(tuple(literals))

    def exactly_one(self, variables: Sequence[int]) -> None:
        self.clause(*variables)
        for left_index in range(len(variables)):
            for right_index in range(left_index + 1, len(variables)):
                self.clause(-variables[left_index], -variables[right_index])

    def build(self) -> CNF:
        return CNF(self.variable_count, tuple(self.clauses))


@dataclass(frozen=True)
class FactorizationEncoding:
    sequence: tuple[int, ...]
    required_bins: int
    cnf: CNF
    x_variables: tuple[tuple[int, ...], ...]
    state_variables: tuple[tuple[tuple[tuple[int, ...], ...], ...], ...]
    cnf_sha256: str

    def model_for_labels(self, labels: Sequence[int]) -> dict[int, bool]:
        label_tuple = tuple(labels)
        if len(label_tuple) != len(self.sequence):
            raise ValueError("label assignment length does not match sequence")
        if any(
            type(label) is not int or not -1 <= label < self.required_bins for label in label_tuple
        ):
            raise ValueError("labels must be -1 or a declared bin index")
        model = {variable: False for variable in range(1, self.cnf.variable_count + 1)}
        for index, label in enumerate(label_tuple):
            for bin_index, variable in enumerate(self.x_variables[index]):
                model[variable] = label == bin_index
        coordinates = tuple(decode_element(element) for element in self.sequence)
        for bin_index in range(self.required_bins):
            for coordinate in range(3):
                state = 0
                model[self.state_variables[bin_index][coordinate][0][state]] = True
                for index, label in enumerate(label_tuple):
                    if label == bin_index:
                        state = (state + coordinates[index][coordinate]) % 5
                    model[self.state_variables[bin_index][coordinate][index + 1][state]] = True
        return model

    def extract_witness(self, model: Mapping[int, bool]) -> tuple[tuple[int, ...], ...]:
        return tuple(
            tuple(
                index
                for index, row in enumerate(self.x_variables)
                if bool(model.get(row[bin_index], False))
            )
            for bin_index in range(self.required_bins)
        )


def _require_sequence(sequence: Sequence[int]) -> tuple[int, ...]:
    value = tuple(sequence)
    if not value:
        raise ValueError("factorization sequence must be nonempty")
    if len(value) > 31:
        raise ValueError("factorization sequence exceeds the frozen length-31 scope")
    return tuple(_require_element(element) for element in value)


def build_factorization_cnf(sequence: Sequence[int], required_bins: int) -> FactorizationEncoding:
    value = _require_sequence(sequence)
    if type(required_bins) is not int or not 1 <= required_bins <= 4:
        raise ValueError("required_bins must be an integer from one through four")

    builder = _Builder()
    x_variables = tuple(tuple(builder.variable() for _ in range(required_bins)) for _ in value)
    for row in x_variables:
        for left, right in product(range(required_bins), repeat=2):
            if left < right:
                builder.clause(-row[left], -row[right])
    for bin_index in range(required_bins):
        builder.clause(*(row[bin_index] for row in x_variables))

    state_variables = tuple(
        tuple(
            tuple(tuple(builder.variable() for _ in range(5)) for _ in range(len(value) + 1))
            for _ in range(3)
        )
        for _ in range(required_bins)
    )
    coordinates = tuple(decode_element(element) for element in value)
    for bin_index in range(required_bins):
        for coordinate in range(3):
            states = state_variables[bin_index][coordinate]
            for prefix in states:
                builder.exactly_one(prefix)
            builder.clause(states[0][0])
            for nonzero in range(1, 5):
                builder.clause(-states[0][nonzero])
            for index, row in enumerate(x_variables):
                selected = row[bin_index]
                delta = coordinates[index][coordinate]
                for prior in range(5):
                    builder.clause(-states[index][prior], selected, states[index + 1][prior])
                    builder.clause(
                        -states[index][prior],
                        -selected,
                        states[index + 1][(prior + delta) % 5],
                    )
            builder.clause(states[len(value)][0])

    cnf = builder.build()
    digest_payload = {
        "schema": "ORION.NQ.EngineB.FactorizationCNF.v1",
        "subject_commit": SUBJECT_COMMIT,
        "sequence": list(value),
        "required_bins": required_bins,
        "variable_count": cnf.variable_count,
        "clauses": [list(clause) for clause in cnf.clauses],
    }
    return FactorizationEncoding(
        value,
        required_bins,
        cnf,
        x_variables,
        state_variables,
        hashlib.sha256(canonical_json_bytes(digest_payload)).hexdigest(),
    )


def evaluate_cnf(cnf: CNF, model: Mapping[int, bool]) -> bool:
    return all(
        any(bool(model.get(abs(literal), False)) == (literal > 0) for literal in clause)
        for clause in cnf.clauses
    )


def _propagate(clauses: tuple[tuple[int, ...], ...], assignment: dict[int, bool]) -> bool:
    changed = True
    while changed:
        changed = False
        for clause in clauses:
            if any(
                variable in assignment and assignment[variable] == (literal > 0)
                for literal in clause
                for variable in (abs(literal),)
            ):
                continue
            unassigned = [literal for literal in clause if abs(literal) not in assignment]
            if not unassigned:
                return False
            if len(unassigned) == 1:
                literal = unassigned[0]
                variable = abs(literal)
                value = literal > 0
                if variable in assignment and assignment[variable] != value:
                    return False
                if variable not in assignment:
                    assignment[variable] = value
                    changed = True
    return True


def solve_cnf_dpll(cnf: CNF, assumptions: Sequence[int] = ()) -> dict[int, bool] | None:
    initial: dict[int, bool] = {}
    for literal in assumptions:
        if type(literal) is not int or literal == 0:
            raise ValueError("DPLL assumption contains an invalid literal")
        variable = abs(literal)
        value = literal > 0
        if not 1 <= variable <= cnf.variable_count:
            raise ValueError("DPLL assumption contains an invalid literal")
        if variable in initial and initial[variable] != value:
            return None
        initial[variable] = value

    def search(assignment: dict[int, bool]) -> dict[int, bool] | None:
        working = assignment.copy()
        if not _propagate(cnf.clauses, working):
            return None
        unresolved = []
        for clause in cnf.clauses:
            if any(
                abs(literal) in working and working[abs(literal)] == (literal > 0)
                for literal in clause
            ):
                continue
            unresolved.append(clause)
        if not unresolved:
            return working
        clause = min(
            unresolved,
            key=lambda item: sum(abs(literal) not in working for literal in item),
        )
        variable = next(abs(literal) for literal in clause if abs(literal) not in working)
        for value in (True, False):
            branch = working.copy()
            branch[variable] = value
            result = search(branch)
            if result is not None:
                return result
        return None

    return search(initial)


def verify_witness(
    sequence: Sequence[int], *, required_bins: int, bins: Sequence[Sequence[int]]
) -> None:
    value = _require_sequence(sequence)
    bin_tuple = tuple(tuple(selected) for selected in bins)
    if len(bin_tuple) != required_bins or any(not selected for selected in bin_tuple):
        raise CertificateMismatch("witness must contain every declared nonempty bin")
    flattened = [index for selected in bin_tuple for index in selected]
    if any(type(index) is not int or not 0 <= index < len(value) for index in flattened):
        raise CertificateMismatch("witness contains an out-of-range sequence index")
    if len(flattened) != len(set(flattened)):
        raise CertificateMismatch("witness bins are not pairwise disjoint")
    for selected in bin_tuple:
        if tuple(sorted(selected)) != selected or len(set(selected)) != len(selected):
            raise CertificateMismatch("witness bin indices are not canonical and unique")
        if sum_elements(value[index] for index in selected) != ZERO:
            raise CertificateMismatch("witness bin is not zero-sum")


def has_k_disjoint_zero_sums_bruteforce(sequence: Sequence[int], required_bins: int) -> bool:
    value = tuple(_require_element(element) for element in sequence)
    if type(required_bins) is not int or not 1 <= required_bins <= 4:
        raise ValueError("required_bins must be an integer from one through four")
    if not value:
        return False
    if len(value) > 12:
        raise ValueError("slow reference enumerator is limited to twelve elements")
    for labels in product(range(-1, required_bins), repeat=len(value)):
        bins = tuple(
            tuple(index for index, label in enumerate(labels) if label == bin_index)
            for bin_index in range(required_bins)
        )
        if all(bins) and all(
            sum_elements(value[index] for index in selected) == ZERO for selected in bins
        ):
            return True
    return False


def _sequence_sha256(sequence: Sequence[int]) -> str:
    return hashlib.sha256(canonical_json_bytes(list(sequence))).hexdigest()


def _certificate_digest(certificate: Mapping[str, Any]) -> str:
    payload = {key: value for key, value in certificate.items() if key != "certificate_sha256"}
    return hashlib.sha256(canonical_json_bytes(payload)).hexdigest()


def build_sat_certificate(
    *,
    record_id: str,
    encoded: FactorizationEncoding,
    model: Mapping[int, bool],
    solver_identity: str,
) -> dict[str, Any]:
    witness = encoded.extract_witness(model)
    verify_witness(encoded.sequence, required_bins=encoded.required_bins, bins=witness)
    certificate: dict[str, Any] = {
        "schema": "ORION.NQ.EngineB.SATCertificate.v1",
        "subject_commit": SUBJECT_COMMIT,
        "record_id": record_id,
        "status": "SAT_K_DISJOINT_ZERO_SUMS",
        "solver_identity": solver_identity,
        "sequence_sha256": _sequence_sha256(encoded.sequence),
        "required_bins": encoded.required_bins,
        "cnf_sha256": encoded.cnf_sha256,
        "witness_bins": [list(selected) for selected in witness],
    }
    certificate["certificate_sha256"] = _certificate_digest(certificate)
    return certificate


def verify_certificate(
    sequence: Sequence[int], *, required_bins: int, certificate: Mapping[str, Any]
) -> None:
    value = _require_sequence(sequence)
    if certificate.get("schema") != "ORION.NQ.EngineB.SATCertificate.v1":
        raise CertificateMismatch("certificate schema mismatch")
    if certificate.get("subject_commit") != SUBJECT_COMMIT:
        raise CertificateMismatch("certificate subject mismatch")
    if certificate.get("status") != "SAT_K_DISJOINT_ZERO_SUMS":
        raise CertificateMismatch("certificate status is not a SAT witness")
    if certificate.get("required_bins") != required_bins:
        raise CertificateMismatch("certificate bin count mismatch")
    if certificate.get("sequence_sha256") != _sequence_sha256(value):
        raise CertificateMismatch("certificate sequence binding mismatch")
    encoded = build_factorization_cnf(value, required_bins)
    if certificate.get("cnf_sha256") != encoded.cnf_sha256:
        raise CertificateMismatch("certificate CNF binding mismatch")
    if certificate.get("certificate_sha256") != _certificate_digest(certificate):
        raise CertificateMismatch("certificate content digest mismatch")
    try:
        verify_witness(
            value,
            required_bins=required_bins,
            bins=certificate["witness_bins"],
        )
    except (KeyError, TypeError, ValueError) as error:
        raise CertificateMismatch("certificate witness is malformed") from error

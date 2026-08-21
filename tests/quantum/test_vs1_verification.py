import math
import random

from orion.quantum.verification import reconstruct_s1a_case


def valid_n3_case0() -> dict:
    search_size = 8
    iterations = 2
    probability = math.sin((2 * iterations + 1) * math.asin(1 / math.sqrt(search_size))) ** 2
    seed = 73503000
    order = list(range(search_size))
    random.Random(seed).shuffle(order)
    return {
        "schema": "ORION.QN.GroverCaseExecution.v1",
        "case_id": "S1A-n3-case0-marked0",
        "n_qubits": 3,
        "search_size": search_size,
        "case_index": 0,
        "marked_index": 0,
        "iterations": iterations,
        "analytic_marked_probability": probability,
        "simulated_marked_probability": probability,
        "normalization_error": 0.0,
        "measured_candidates": [0],
        "returned_candidate": 0,
        "attempts": 1,
        "oracle_calls": iterations,
        "verification_predicate_calls": 1,
        "measurement_shots": 1,
        "classical_ordered_calls": 1,
        "classical_random_calls": order.index(0) + 1,
        "classical_random_seed": seed,
        "backend_identity": {
            "qiskit_version": "2.5.1",
            "qiskit_aer_version": "0.17.2",
            "backend_family": "qiskit-aer",
            "backend_name": "AerSimulator",
            "method": "statevector",
            "noise_model": "none",
            "evidence_mode": "LOCAL_SIMULATION",
        },
        "circuit_qubits": 3,
        "logical_depth": 1,
        "transpiled_depth": 1,
        "logical_ops": {},
        "transpiled_ops": {},
    }


def test_p4_reconstruction_accepts_a_fully_bound_case() -> None:
    reconstruction = reconstruct_s1a_case(valid_n3_case0())

    assert reconstruction["valid_record"] is True
    assert reconstruction["candidate_verified"] is True
    assert reconstruction["errors"] == []


def test_p4_reconstruction_rejects_underreported_oracle_calls() -> None:
    record = valid_n3_case0()
    record["oracle_calls"] = 1

    reconstruction = reconstruct_s1a_case(record)

    assert reconstruction["valid_record"] is False
    assert any("oracle-call accounting" in item for item in reconstruction["errors"])


def test_p4_reconstruction_rejects_hidden_answer_substitution() -> None:
    record = valid_n3_case0()
    record["measured_candidates"] = [3]
    record["returned_candidate"] = 0

    reconstruction = reconstruct_s1a_case(record)

    assert reconstruction["valid_record"] is False
    assert any("final measured candidate" in item for item in reconstruction["errors"])


def test_p4_reconstruction_rejects_backend_version_drift() -> None:
    record = valid_n3_case0()
    record["backend_identity"]["qiskit_version"] = "2.5.2"

    reconstruction = reconstruct_s1a_case(record)

    assert reconstruction["valid_record"] is False
    assert any("backend identity/version" in item for item in reconstruction["errors"])


def test_p4_reconstruction_rejects_tampered_probability() -> None:
    record = valid_n3_case0()
    record["analytic_marked_probability"] = 1.0

    reconstruction = reconstruct_s1a_case(record)

    assert reconstruction["valid_record"] is False
    assert any("analytic probability" in item for item in reconstruction["errors"])

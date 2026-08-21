from tests.quantum.test_vs1_verification import valid_n3_case0

from orion.quantum.verification import reconstruct_s1a_case


def test_negative_qubit_count_fails_closed_instead_of_raising() -> None:
    record = valid_n3_case0()
    record["n_qubits"] = -1

    reconstruction = reconstruct_s1a_case(record)

    assert reconstruction["valid_record"] is False
    assert reconstruction["candidate_verified"] is False
    assert any("n_qubits outside" in item for item in reconstruction["errors"])


def test_impossible_search_size_fails_closed_instead_of_raising() -> None:
    record = valid_n3_case0()
    record["search_size"] = 0

    reconstruction = reconstruct_s1a_case(record)

    assert reconstruction["valid_record"] is False
    assert reconstruction["candidate_verified"] is False
    assert any("search_size" in item for item in reconstruction["errors"])


def test_out_of_range_marked_identity_fails_closed_instead_of_raising() -> None:
    record = valid_n3_case0()
    record["marked_index"] = 99
    record["case_id"] = "S1A-n3-case0-marked99"

    reconstruction = reconstruct_s1a_case(record)

    assert reconstruction["valid_record"] is False
    assert reconstruction["candidate_verified"] is False
    assert any("marked_index" in item for item in reconstruction["errors"])


def test_out_of_range_case_index_fails_closed_instead_of_raising() -> None:
    record = valid_n3_case0()
    record["case_index"] = 99
    record["case_id"] = "S1A-n3-case99-marked0"

    reconstruction = reconstruct_s1a_case(record)

    assert reconstruction["valid_record"] is False
    assert reconstruction["candidate_verified"] is False
    assert any("case_index" in item for item in reconstruction["errors"])

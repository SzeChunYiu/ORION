from __future__ import annotations

import importlib.util
import itertools
import json
import subprocess
import sys
from collections import Counter
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
PACKET = ROOT / "research/orion-rg/promotion/orion04-global-certified-search-v1"
GENERATOR_PATH = PACKET / "generate_opb.py"
WITNESS_CHECKER = PACKET / "independent_checker/check_witness.py"
PROTOCOL = PACKET / "PROTOCOL.json"


def _load_generator() -> Any:
    spec = importlib.util.spec_from_file_location("orion04_global_opb", GENERATOR_PATH)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def _coords(code: int, prime: int, rank: int) -> tuple[int, ...]:
    values = []
    for _ in range(rank):
        values.append(code % prime)
        code //= prime
    return tuple(values)


def _zero_sum(multiset: tuple[int, ...], prime: int, rank: int) -> bool:
    totals = [0] * rank
    for code in multiset:
        point = _coords(code, prime, rank)
        for axis, value in enumerate(point):
            totals[axis] = (totals[axis] + value) % prime
    return totals == [0] * rank


def _independent_short_counts(prime: int, rank: int, max_length: int, cap: int) -> dict[str, int]:
    points = range(1, prime**rank)
    result: dict[str, int] = {}
    for length in range(2, max_length + 1):
        result[str(length)] = sum(
            1
            for multiset in itertools.combinations_with_replacement(points, length)
            if _zero_sum(multiset, prime, rank)
            and max(Counter(multiset).values()) <= cap
        )
    return result


def test_small_instance_is_deterministic_and_complete(tmp_path: Path) -> None:
    module = _load_generator()
    params = module.Parameters(
        prime=3,
        rank=2,
        length=7,
        support_lower_bound=3,
        max_short_length=3,
        positive_multiplicities=(1, 2),
    )
    module.validate_parameters(params)
    first = tmp_path / "first.opb"
    second = tmp_path / "second.opb"
    manifest_first = module.materialize_instance(first, params)
    manifest_second = module.materialize_instance(second, params)

    assert first.read_bytes() == second.read_bytes()
    assert manifest_first["opb_sha256"] == manifest_second["opb_sha256"]
    assert manifest_first["variable_count"] > 0
    assert manifest_first["constraint_count"] > 0
    header = first.read_text().splitlines()[0]
    assert header == (
        f"* #variable= {manifest_first['variable_count']} "
        f"#constraint= {manifest_first['constraint_count']}"
    )
    expected = _independent_short_counts(prime=3, rank=2, max_length=3, cap=2)
    assert manifest_first["details"]["short_zero_constraints_by_length"] == expected


def test_registered_protocol_starts_fail_closed() -> None:
    raw = json.loads(PROTOCOL.read_text())
    assert raw["protocol_id"] == "ORION04.D4.GLOBAL_CERTIFIED_SEARCH.v1"
    assert raw["authority"]["support_at_least_14_parent_authority"] is True
    assert raw["authority"]["support_at_least_23_authority"] is False
    assert raw["authority"]["c0_31_authority"] is False
    assert raw["authority"]["exact_d4_authority"] is False
    assert raw["authority"]["external_proof_checked"] is False


def test_witness_checker_rejects_total_sum_and_short_zero_failures(tmp_path: Path) -> None:
    witness = {
        "schema": "ORION.ORION04.ExtremalWitness.v1",
        "prime": 5,
        "rank": 3,
        "length": 31,
        "multiplicities": [
            {"point": [1, 0, 0], "multiplicity": 4},
            {"point": [4, 0, 0], "multiplicity": 4},
            {"point": [0, 1, 0], "multiplicity": 4},
            {"point": [0, 4, 0], "multiplicity": 4},
            {"point": [0, 0, 1], "multiplicity": 4},
            {"point": [0, 0, 4], "multiplicity": 4},
            {"point": [1, 1, 1], "multiplicity": 2},
            {"point": [2, 1, 1], "multiplicity": 2},
            {"point": [3, 1, 1], "multiplicity": 2},
            {"point": [4, 1, 1], "multiplicity": 1},
        ],
    }
    input_path = tmp_path / "bad-witness.json"
    output_path = tmp_path / "report.json"
    input_path.write_text(json.dumps(witness))
    completed = subprocess.run(
        [
            sys.executable,
            str(WITNESS_CHECKER),
            "--input",
            str(input_path),
            "--output",
            str(output_path),
        ],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    assert completed.returncode == 1
    report = json.loads(output_path.read_text())
    assert report["terminal"] == "ORION04_GLOBAL_CERTIFIED_SEARCH_CANNOT_CHECK"
    assert report["checks"]["no_zero_sum_of_length_1_to_5"] is False
    assert report["exact_d4_31_authority"] is False

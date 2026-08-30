from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PACKET = ROOT / "research/orion-rg/promotion/orion04-global-certified-search-v1"
DECODER = PACKET / "independent_checker/decode_kissat_model.py"
CHECKER = PACKET / "independent_checker/check_witness.py"


def x_variable(code: int, multiplicity_index: int) -> int:
    # Seven variables are allocated per nonzero point: m1,m2,m4,t1,t2,t3,t4.
    return 1 + (code - 1) * 7 + multiplicity_index


def test_decoder_reconstructs_registered_multiplicity_variables(tmp_path: Path) -> None:
    # A deliberately invalid mathematical sequence is enough to test model decoding.
    selected = [
        x_variable(1, 2),
        x_variable(4, 2),
        x_variable(5, 2),
        x_variable(20, 2),
        x_variable(25, 2),
        x_variable(100, 2),
        x_variable(31, 1),
        x_variable(32, 1),
        x_variable(33, 1),
        x_variable(34, 0),
    ]
    solver_output = tmp_path / "kissat.out"
    solver_output.write_text(
        "s SATISFIABLE\n" + "v " + " ".join(str(value) for value in selected) + " 0\n"
    )
    witness = tmp_path / "witness.json"
    completed = subprocess.run(
        [
            sys.executable,
            str(DECODER),
            "--solver-output",
            str(solver_output),
            "--output",
            str(witness),
        ],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    assert completed.returncode == 0, completed.stderr + completed.stdout
    raw = json.loads(witness.read_text())
    assert raw["schema"] == "ORION.ORION04.ExtremalWitness.v1"
    assert sum(row["multiplicity"] for row in raw["multiplicities"]) == 31

    report = tmp_path / "report.json"
    checked = subprocess.run(
        [
            sys.executable,
            str(CHECKER),
            "--input",
            str(witness),
            "--output",
            str(report),
        ],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    assert checked.returncode == 1
    assert json.loads(report.read_text())["exact_d4_31_authority"] is False

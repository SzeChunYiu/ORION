from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
PACKET = ROOT / "research/orion-rg/promotion/orion04-global-certified-search-v1"


def load(path: Path, name: str) -> Any:
    spec = importlib.util.spec_from_file_location(name, path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def test_cnf_and_opb_have_identical_short_zero_coverage(tmp_path: Path) -> None:
    opb = load(PACKET / "generate_opb.py", "orion04_opb_crosscheck")
    cnf = load(PACKET / "generate_cnf.py", "orion04_cnf_crosscheck")

    params = opb.Parameters(
        prime=3,
        rank=2,
        length=7,
        support_lower_bound=3,
        max_short_length=3,
        positive_multiplicities=(1, 2),
    )
    opb_path = tmp_path / "control.opb"
    opb_manifest = opb.materialize_instance(opb_path, params)

    cnf_path = tmp_path / "control.cnf"
    cnf_manifest_path = tmp_path / "control-cnf.json"
    cnf_manifest = cnf.materialize(
        output=cnf_path,
        manifest_path=cnf_manifest_path,
        prime=3,
        rank=2,
        length=7,
        support_lower_bound=3,
        max_short_length=3,
        multiplicities=(1, 2),
    )

    assert cnf_manifest["short_zero_clauses_by_length"] == opb_manifest["details"][
        "short_zero_constraints_by_length"
    ]
    assert cnf_manifest[
        "short_zero_multisets_impossible_from_multiplicity_cap"
    ] == opb_manifest["details"][
        "short_zero_multisets_impossible_from_multiplicity_cap"
    ]
    header = cnf_path.read_text().splitlines()[0]
    assert header == (
        f"p cnf {cnf_manifest['variable_count']} {cnf_manifest['clause_count']}"
    )
    assert cnf_manifest["solver_outcome_accessed"] is False
    assert cnf_manifest["c0_31_authority"] is False
    assert cnf_manifest["exact_d4_authority"] is False

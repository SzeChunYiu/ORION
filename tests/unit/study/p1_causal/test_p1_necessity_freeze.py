from __future__ import annotations

import ast
import importlib.util
import inspect
import json
from pathlib import Path

from orion.study.p1_causal.necessity_policies import ABLATION_ARMS, RUNNABLE_ARMS
import orion.study.p1_causal.necessity_scoring as scoring_module

ROOT = Path(__file__).resolve().parents[4]
P1 = ROOT / "research" / "revival" / "p1"
BASE = P1 / "protocol" / "P1.epistemic-mutation-necessity.v2.2.json"
AMENDMENT = P1 / "protocol" / "P1.epistemic-mutation-necessity.v2.2.1.json"
FREEZER = P1 / "freeze_mutation_necessity_worlds.py"

_spec = importlib.util.spec_from_file_location("p1_nc_freezer", FREEZER)
assert _spec is not None and _spec.loader is not None
freezer = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(freezer)


def test_protocol_chain_is_frozen_before_confirmatory_world_access() -> None:
    base = json.loads(BASE.read_text())
    amendment = json.loads(AMENDMENT.read_text())
    effective, identity = freezer.load_effective_protocol(AMENDMENT)

    assert base["protocol_version"] == "P1.epistemic-mutation-necessity.v2.2.0"
    assert base["outcome_accessed"] is False
    assert amendment["base_protocol_version"] == base["protocol_version"]
    assert amendment["confirmatory_outcome_accessed"] is False
    assert effective["protocol_version"] == "P1.epistemic-mutation-necessity.v2.2.1"
    assert effective["fresh_world_plan"]["confirmatory_seed"] == 202608172211
    assert effective["fresh_world_plan"]["confirmatory_seed"] != 30303
    assert effective["fresh_world_plan"]["total_n"] == 2880
    assert effective["intervention_budget"]["units_per_task"] == 4
    assert identity["kind"] == "base_plus_amendments"
    assert [node["protocol_version"] for node in identity["nodes"]] == [
        "P1.epistemic-mutation-necessity.v2.2.0",
        "P1.epistemic-mutation-necessity.v2.2.1",
    ]


def test_protocol_arm_and_ablation_registries_match_code() -> None:
    effective, _ = freezer.load_effective_protocol(AMENDMENT)
    frozen_runnable = tuple(
        item["id"] for item in effective["matched_arms"] if item["id"] != "oracle_minimal_valid_ceiling"
    )
    assert frozen_runnable == tuple(item.__name__ for item in RUNNABLE_ARMS)
    assert set(effective["direct_ablations"]) == {item.__name__ for item in ABLATION_ARMS}
    assert "oracle_minimal_valid_ceiling" not in {item.__name__ for item in RUNNABLE_ARMS}


def test_independent_scorer_imports_neither_policies_nor_orion_licensing() -> None:
    tree = ast.parse(inspect.getsource(scoring_module))
    imports = []
    for node in ast.walk(tree):
        if isinstance(node, ast.ImportFrom):
            imports.append(node.module or "")
        elif isinstance(node, ast.Import):
            imports.extend(alias.name for alias in node.names)
    assert not any(name.endswith("necessity_policies") for name in imports)
    assert not any(name.endswith("licensing") for name in imports)


def test_strengthening_does_not_change_confirmatory_seed_or_sample_sizes() -> None:
    base = json.loads(BASE.read_text())
    effective, _ = freezer.load_effective_protocol(AMENDMENT)
    for field in ("confirmatory_seed", "hidden_shift_n", "negative_control_n", "total_n"):
        assert effective["fresh_world_plan"][field] == base["fresh_world_plan"][field]

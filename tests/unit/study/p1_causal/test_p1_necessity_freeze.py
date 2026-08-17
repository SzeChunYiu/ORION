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
AMENDMENT_1 = P1 / "protocol" / "P1.epistemic-mutation-necessity.v2.2.1.json"
AMENDMENT_2 = P1 / "protocol" / "P1.epistemic-mutation-necessity.v2.2.2.json"
FREEZER = P1 / "freeze_mutation_necessity_worlds.py"

_spec = importlib.util.spec_from_file_location("p1_nc_freezer", FREEZER)
assert _spec is not None and _spec.loader is not None
freezer = importlib.util.module_from_spec(_spec)
_freeze_spec = _spec.loader
_freeze_spec.exec_module(freezer)


def test_protocol_chain_is_frozen_before_confirmatory_world_access() -> None:
    base = json.loads(BASE.read_text())
    amendment_1 = json.loads(AMENDMENT_1.read_text())
    amendment_2 = json.loads(AMENDMENT_2.read_text())
    effective, identity = freezer.load_effective_protocol(AMENDMENT_2)

    assert base["protocol_version"] == "P1.epistemic-mutation-necessity.v2.2.0"
    assert base["outcome_accessed"] is False
    assert amendment_1["base_protocol_version"] == base["protocol_version"]
    assert amendment_1["confirmatory_outcome_accessed"] is False
    assert amendment_2["base_protocol_version"] == amendment_1["protocol_version"]
    assert amendment_2["confirmatory_outcome_accessed"] is False
    assert amendment_2["base_protocol_git_blob_sha"] == freezer._git_blob_sha(
        AMENDMENT_1.read_bytes()
    )
    assert effective["protocol_version"] == "P1.epistemic-mutation-necessity.v2.2.2"
    assert effective["fresh_world_plan"]["confirmatory_seed"] == 202608172211
    assert effective["fresh_world_plan"]["replication_seed"] == 202608172212
    assert effective["fresh_world_plan"]["confirmatory_seed"] != 30303
    assert effective["fresh_world_plan"]["hidden_shift_n"] == 480
    assert effective["fresh_world_plan"]["negative_control_n"] == 2402
    assert effective["fresh_world_plan"]["total_n"] == 2882
    assert effective["intervention_budget"]["units_per_task"] == 4
    assert identity["kind"] == "base_plus_amendments"
    assert [node["protocol_version"] for node in identity["nodes"]] == [
        "P1.epistemic-mutation-necessity.v2.2.0",
        "P1.epistemic-mutation-necessity.v2.2.1",
        "P1.epistemic-mutation-necessity.v2.2.2",
    ]


def test_protocol_arm_and_ablation_registries_match_code() -> None:
    effective, _ = freezer.load_effective_protocol(AMENDMENT_2)
    frozen_runnable = tuple(
        item["id"]
        for item in effective["matched_arms"]
        if item["id"] != "oracle_minimal_valid_ceiling"
    )
    assert frozen_runnable == tuple(item.__name__ for item in RUNNABLE_ARMS)
    assert set(effective["direct_ablations"]) == {
        item.__name__ for item in ABLATION_ARMS
    }
    assert "oracle_minimal_valid_ceiling" not in {
        item.__name__ for item in RUNNABLE_ARMS
    }


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


def test_v222_strengthens_precision_without_relaxing_mechanism_or_seed() -> None:
    effective_1, _ = freezer.load_effective_protocol(AMENDMENT_1)
    effective_2, _ = freezer.load_effective_protocol(AMENDMENT_2)

    assert effective_2["fresh_world_plan"]["confirmatory_seed"] == effective_1[
        "fresh_world_plan"
    ]["confirmatory_seed"]
    assert effective_2["fresh_world_plan"]["hidden_shift_n"] == effective_1[
        "fresh_world_plan"
    ]["hidden_shift_n"]
    assert effective_2["fresh_world_plan"]["negative_control_n"] == 2402
    assert effective_1["fresh_world_plan"]["negative_control_n"] == 2400
    assert effective_2["fresh_world_plan"]["total_n"] == 2882
    assert effective_2["primary_hypotheses"] == effective_1["primary_hypotheses"]
    assert effective_2["support_rule"] == effective_1["support_rule"]
    assert effective_2["matched_arms"] == effective_1["matched_arms"]
    assert effective_2["direct_ablations"] == effective_1["direct_ablations"]

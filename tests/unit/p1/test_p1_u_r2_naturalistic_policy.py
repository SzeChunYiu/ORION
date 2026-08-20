from __future__ import annotations

import importlib.util
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
POLICY_PATH = ROOT / "research" / "claim_expansion" / "p1" / "gpt_r2" / "policy.py"
PROTOCOL_PATH = POLICY_PATH.parent / "PROTOCOL_V1.json"


def load_policy():
    spec = importlib.util.spec_from_file_location("p1_u_r2_policy", POLICY_PATH)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def case(dossier: str, target: str | None = None, *, unresolved: bool = False, no_high: bool = False):
    protocol = json.loads(PROTOCOL_PATH.read_text())
    probes = {}
    for probe, cls in protocol["probes"].items():
        if unresolved:
            probes[probe] = "INCONCLUSIVE"
        elif no_high:
            probes[probe] = "REFUTE"
        else:
            probes[probe] = "SUPPORT" if cls == target else "REFUTE"
    return {"dossier": dossier, "probes": probes}


def test_observation_distributions_are_normalized():
    p = load_policy()
    prior = p.surface_prior("generic scientific failure")
    for probe in p.PROBES:
        dist = p.observation_distribution(prior, probe)
        assert set(dist) == {"SUPPORT", "REFUTE", "INCONCLUSIVE"}
        assert abs(sum(dist.values()) - 1.0) < 1e-12


def test_orion_r2_reaches_every_registered_responsibility_before_holdout():
    p = load_policy()
    cases = [
        ("SEARCH_OR_EVIDENCE", case("The analysis reports missing evidence and insufficient data coverage; additional data may resolve the result.", "SEARCH_OR_EVIDENCE")),
        ("REPRESENTATION_OR_INTERFACE", case("The same objective behaves differently after serialization; a representation encoding interface mapping is suspected.", "REPRESENTATION_OR_INTERFACE")),
        ("IMPLEMENTATION_OR_ENVIRONMENT", case("A software pipeline configuration dependency and environment version bug makes the result fail.", "IMPLEMENTATION_OR_ENVIRONMENT")),
        ("MEASUREMENT_OR_EVALUATOR", case("The benchmark metric changes after calibration of the instrument and evaluator scoring procedure.", "MEASUREMENT_OR_EVALUATOR")),
        ("OBJECTIVE_OR_MODEL_CLASS", case("Persistent residual error indicates a misspecified hypothesis and inadequate model class for the mechanism.", "OBJECTIVE_OR_MODEL_CLASS")),
        ("PROBLEM_BOUNDARY", case("An omitted process outside scope changes the system boundary and the relevant population context.", "PROBLEM_BOUNDARY")),
        ("NO_HIGH_LEVEL_REFORMULATION", case("The adequate model is reproduced and stable; a control shows no change is needed and the same objective remains sufficient.", no_high=True)),
        ("UNRESOLVED", case("Conflicting evidence leaves several plausible explanations with no decisive diagnostic available.", unresolved=True)),
    ]
    for expected, episode in cases:
        result = p.orion_r2_policy(episode)
        assert result["choice"] == expected, (expected, result)
        assert result["cost"] <= 2


def test_no_policy_receives_gold_label_field():
    p = load_policy()
    episode = case("A software pipeline dependency produces an environment-specific failure.", "IMPLEMENTATION_OR_ENVIRONMENT")
    episode["gold"] = "PROBLEM_BOUNDARY"
    with_gold = p.run_all(episode)
    episode.pop("gold")
    without_gold = p.run_all(episode)
    assert with_gold == without_gold

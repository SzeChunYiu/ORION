from __future__ import annotations

import json
import math
from pathlib import Path
from typing import Iterable, Mapping, Sequence

ROOT = Path(__file__).resolve().parent
PROTOCOL = json.loads((ROOT / "PROTOCOL_V1.json").read_text())

CLASSES: tuple[str, ...] = tuple(PROTOCOL["classes"])
PROBE_TO_CLASS: dict[str, str] = dict(PROTOCOL["probes"])
PROBES: tuple[str, ...] = tuple(PROBE_TO_CLASS)
BUDGET = int(PROTOCOL["budget"])
THRESHOLD = float(PROTOCOL["posterior_terminal_threshold"])
LOW_GATE = float(PROTOCOL["orion_lower_level_mass_gate"])
BOUNDARY_GATE = float(PROTOCOL["orion_boundary_lower_plus_objective_mass_gate"])
LOW_PROBE_PRIORITY = float(PROTOCOL["orion_lower_level_probe_priority_mass"])
NO_HIGH_MAX_HIGH_MASS = float(PROTOCOL["orion_no_high_level_max_high_mass"])
NO_HIGH_MIN_REFUTATIONS = int(PROTOCOL["orion_no_high_min_refutations"])

LOW_LEVEL = {
    "SEARCH_OR_EVIDENCE",
    "REPRESENTATION_OR_INTERFACE",
    "IMPLEMENTATION_OR_ENVIRONMENT",
    "MEASUREMENT_OR_EVALUATOR",
}
HIGH_LEVEL = {"OBJECTIVE_OR_MODEL_CLASS", "PROBLEM_BOUNDARY"}


def _normalize(m: Mapping[str, float]) -> dict[str, float]:
    clean = {str(k): max(0.0, float(v)) for k, v in m.items()}
    total = sum(clean.values())
    if total <= 0:
        if not clean:
            raise ValueError("cannot normalize an empty mapping")
        return {k: 1.0 / len(clean) for k in clean}
    return {k: v / total for k, v in clean.items()}


def _class_norm(m: Mapping[str, float]) -> dict[str, float]:
    return _normalize({c: float(m.get(c, 0.0)) for c in CLASSES})


def surface_prior(dossier: str) -> dict[str, float]:
    cfg = PROTOCOL["surface_prior"]
    text = " ".join(dossier.lower().split())
    base = float(cfg["base_mass"])
    weight = float(cfg["keyword_weight"])
    cap = int(cfg["max_keyword_hits_per_class"])
    masses: dict[str, float] = {}
    for cls in CLASSES:
        hits = sum(1 for kw in cfg["keywords"][cls] if kw.lower() in text)
        masses[cls] = base + weight * min(hits, cap)
    return _class_norm(masses)


def likelihood(true_class: str, probe: str, observation: str) -> float:
    target = PROBE_TO_CLASS[probe]
    if true_class == "NO_HIGH_LEVEL_REFORMULATION":
        key = "no_high_level_target_probe"
    elif true_class == target:
        key = "target_probe"
    else:
        key = "nontarget_probe"
    return float(PROTOCOL["likelihoods"][key][observation])


def update(posterior: Mapping[str, float], probe: str, observation: str) -> dict[str, float]:
    return _class_norm({c: posterior[c] * likelihood(c, probe, observation) for c in CLASSES})


def observation_distribution(posterior: Mapping[str, float], probe: str) -> dict[str, float]:
    out = {o: 0.0 for o in PROTOCOL["probe_observations"]}
    for c, p in posterior.items():
        for obs in out:
            out[obs] += p * likelihood(c, probe, obs)
    return _normalize(out)


def entropy(posterior: Mapping[str, float]) -> float:
    return -sum(p * math.log(p, 2) for p in posterior.values() if p > 0)


def expected_entropy_after_probe(posterior: Mapping[str, float], probe: str) -> float:
    dist = observation_distribution(posterior, probe)
    return sum(prob * entropy(update(posterior, probe, obs)) for obs, prob in dist.items())


def _choice_utility(choice: str, true_class: str) -> float:
    if choice == "UNRESOLVED":
        return 0.0
    if choice == true_class:
        return 1.0
    if choice in HIGH_LEVEL and true_class not in HIGH_LEVEL:
        return -2.0
    return -1.0


def best_flat_terminal(posterior: Mapping[str, float], allowed: Iterable[str] | None = None) -> tuple[str, float]:
    choices = list(allowed) if allowed is not None else list(CLASSES)
    choices.append("UNRESOLVED")
    best_choice = "UNRESOLVED"
    best_value = -1e9
    for choice in choices:
        value = sum(p * _choice_utility(choice, c) for c, p in posterior.items())
        if value > best_value + 1e-12 or (abs(value - best_value) <= 1e-12 and choice < best_choice):
            best_choice, best_value = choice, value
    return best_choice, best_value


def _expected_plan_value(
    posterior: Mapping[str, float],
    unprobed: Sequence[str],
    depth: int,
    allowed_terminal: Iterable[str] | None = None,
) -> float:
    _, terminal_value = best_flat_terminal(posterior, allowed_terminal)
    if depth <= 0 or not unprobed:
        return terminal_value
    best = terminal_value
    for probe in unprobed:
        dist = observation_distribution(posterior, probe)
        next_unprobed = tuple(p for p in unprobed if p != probe)
        value = -0.05 + sum(
            prob * _expected_plan_value(update(posterior, probe, obs), next_unprobed, depth - 1, allowed_terminal)
            for obs, prob in dist.items()
        )
        best = max(best, value)
    return best


def _best_plan_probe(
    posterior: Mapping[str, float],
    unprobed: Sequence[str],
    depth: int,
    allowed_terminal: Iterable[str] | None = None,
) -> str | None:
    _, terminal_value = best_flat_terminal(posterior, allowed_terminal)
    best_probe: str | None = None
    best_value = terminal_value
    for probe in unprobed:
        dist = observation_distribution(posterior, probe)
        next_unprobed = tuple(p for p in unprobed if p != probe)
        value = -0.05 + sum(
            prob * _expected_plan_value(update(posterior, probe, obs), next_unprobed, depth - 1, allowed_terminal)
            for obs, prob in dist.items()
        )
        if value > best_value + 1e-12 or (
            abs(value - best_value) <= 1e-12 and best_probe is not None and probe < best_probe
        ):
            best_probe, best_value = probe, value
    return best_probe


def donor_complete_policy(case: Mapping[str, object], horizon: int = 2) -> dict[str, object]:
    posterior = surface_prior(str(case["dossier"]))
    trace: list[dict[str, object]] = []
    unprobed = list(PROBES)
    for _ in range(min(BUDGET, horizon)):
        probe = _best_plan_probe(posterior, unprobed, horizon - len(trace))
        if probe is None:
            break
        obs = str(case["probes"][probe])
        posterior = update(posterior, probe, obs)
        trace.append({"probe": probe, "observation": obs})
        unprobed.remove(probe)
    choice, _ = best_flat_terminal(posterior)
    top = max(posterior.values())
    if choice != "UNRESOLVED" and top < THRESHOLD:
        choice = "UNRESOLVED"
    return {"choice": choice, "cost": len(trace), "trace": trace, "posterior": posterior}


def no_reformulation_policy(case: Mapping[str, object]) -> dict[str, object]:
    posterior = surface_prior(str(case["dossier"]))
    allowed = sorted(LOW_LEVEL | {"NO_HIGH_LEVEL_REFORMULATION"})
    trace: list[dict[str, object]] = []
    unprobed = list(PROBES)
    for _ in range(BUDGET):
        probe = _best_plan_probe(posterior, unprobed, BUDGET - len(trace), allowed)
        if probe is None:
            break
        obs = str(case["probes"][probe])
        posterior = update(posterior, probe, obs)
        trace.append({"probe": probe, "observation": obs})
        unprobed.remove(probe)
    choice, _ = best_flat_terminal(posterior, allowed)
    if choice != "UNRESOLVED" and max(posterior.get(c, 0.0) for c in allowed) < THRESHOLD:
        choice = "UNRESOLVED"
    return {"choice": choice, "cost": len(trace), "trace": trace, "posterior": posterior}


def always_escalate_policy(case: Mapping[str, object]) -> dict[str, object]:
    posterior = surface_prior(str(case["dossier"]))
    choice = max(("OBJECTIVE_OR_MODEL_CLASS", "PROBLEM_BOUNDARY"), key=lambda c: (posterior[c], c))
    return {"choice": choice, "cost": 0, "trace": [], "posterior": posterior}


def _orion_terminal(posterior: Mapping[str, float], trace: Sequence[Mapping[str, object]]) -> str | None:
    refutations = sum(1 for t in trace if t["observation"] == "REFUTE")
    supports = sum(1 for t in trace if t["observation"] == "SUPPORT")
    high_mass = sum(posterior[c] for c in HIGH_LEVEL)
    if refutations >= NO_HIGH_MIN_REFUTATIONS and supports == 0 and high_mass <= NO_HIGH_MAX_HIGH_MASS:
        return "NO_HIGH_LEVEL_REFORMULATION"

    top_class, top_prob = max(posterior.items(), key=lambda kv: (kv[1], kv[0]))
    if top_prob < THRESHOLD:
        return None
    if top_class == "OBJECTIVE_OR_MODEL_CLASS":
        lower_mass = sum(posterior[c] for c in LOW_LEVEL)
        direct = any(t["probe"] == "P_OBJECTIVE_PREDICTIVE_CHECK" and t["observation"] == "SUPPORT" for t in trace)
        if lower_mass > LOW_GATE or not direct:
            return None
    if top_class == "PROBLEM_BOUNDARY":
        lower_plus_obj = sum(posterior[c] for c in LOW_LEVEL | {"OBJECTIVE_OR_MODEL_CLASS"})
        direct = any(t["probe"] == "P_BOUNDARY_COUNTERFACTUAL" and t["observation"] == "SUPPORT" for t in trace)
        if lower_plus_obj > BOUNDARY_GATE or not direct:
            return None
    return top_class


def _orion_probe(posterior: Mapping[str, float], unprobed: Sequence[str]) -> str | None:
    if not unprobed:
        return None
    lower_mass = sum(posterior[c] for c in LOW_LEVEL)
    if lower_mass > LOW_PROBE_PRIORITY:
        candidates = [p for p in unprobed if PROBE_TO_CLASS[p] in LOW_LEVEL]
        if candidates:
            return max(candidates, key=lambda p: (posterior[PROBE_TO_CLASS[p]], -PROBES.index(p)))
    h0 = entropy(posterior)
    ranked = []
    for probe in unprobed:
        gain = h0 - expected_entropy_after_probe(posterior, probe)
        ranked.append((gain, posterior[PROBE_TO_CLASS[probe]], -PROBES.index(probe), probe))
    return max(ranked)[-1]


def orion_r2_policy(case: Mapping[str, object]) -> dict[str, object]:
    posterior = surface_prior(str(case["dossier"]))
    trace: list[dict[str, object]] = []
    unprobed = list(PROBES)
    for _ in range(BUDGET):
        choice = _orion_terminal(posterior, trace)
        if choice is not None:
            return {"choice": choice, "cost": len(trace), "trace": trace, "posterior": posterior}
        probe = _orion_probe(posterior, unprobed)
        if probe is None:
            break
        obs = str(case["probes"][probe])
        posterior = update(posterior, probe, obs)
        trace.append({"probe": probe, "observation": obs})
        unprobed.remove(probe)
    choice = _orion_terminal(posterior, trace)
    if choice is None:
        choice = "UNRESOLVED"
    return {"choice": choice, "cost": len(trace), "trace": trace, "posterior": posterior}


def run_all(case: Mapping[str, object]) -> dict[str, dict[str, object]]:
    return {
        "B0_NO_REFORMULATION": no_reformulation_policy(case),
        "B1_ALWAYS_ESCALATE": always_escalate_policy(case),
        "B2_IMMEDIATE_VOI": donor_complete_policy(case, horizon=1),
        "B3_HORIZON2_DONOR_COMPLETE": donor_complete_policy(case, horizon=2),
        "ORION_R2": orion_r2_policy(case),
    }

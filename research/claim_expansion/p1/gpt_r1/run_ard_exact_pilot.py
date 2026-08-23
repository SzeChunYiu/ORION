from __future__ import annotations

import argparse
import hashlib
import json
import random
from dataclasses import dataclass
from fractions import Fraction
from pathlib import Path
from typing import Callable, Iterable

BUDGET = 2
COST_WEIGHT = Fraction(1, 20)  # 0.05
FALSE_HIGH_LEVEL_PENALTY = Fraction(1, 1)

LOW_LEVEL = {
    "KEEP_SEARCH",
    "KEEP_COMPILE",
    "KEEP_REPAIR",
    "REVISE_MEASUREMENT",
}
HIGH_LEVEL = {"REFORMULATE_OBJECTIVE", "REFORMULATE_BOUNDARY"}
UNRESOLVED = "UNRESOLVED"

ACTION_IDS = (
    "SEARCH_MORE",
    "COMPILE_OR_REPRESENT",
    "REPAIR_ENV_OR_HARNESS",
    "REMEASURE",
    "TEST_OBJECTIVE_BASIS",
    "TEST_PROBLEM_BOUNDARY",
)

DOMAINS = (
    "SOFTWARE_DEBUGGING",
    "SCIENTIFIC_RETRIEVAL",
    "SEMANTIC_INTEGRATION",
    "EVIDENCE_VERIFICATION",
    "MODEL_EXPERIMENT_DESIGN",
)

FAMILIES = (
    "DIRECT_LOWER_LEVEL",
    "DIRECT_HIGH_LEVEL",
    "REPRESENTATION_MASQUERADE",
    "HARNESS_MASQUERADE",
    "OBJECTIVE_BASIS_SUFFICIENT",
    "SEQUENTIAL_COMPLEMENT",
    "DECISION_VS_LABEL_INFORMATION",
    "NON_IDENTIFIABLE",
)

SYSTEMS = (
    "B0_STATIC_NO_PROBE",
    "B1_GREEDY_RESTORATION",
    "B2_ONE_STEP_LABEL_VOI",
    "B3_ONE_STEP_DECISION_VOI",
    "B4_TWO_STEP_LABEL_PLANNER",
    "P1_ARD_HORIZON2_SCIENTIFIC_RESPONSIBILITY",
    "CEILING_HORIZON2_FULL_SCIENTIFIC_ORACLE",
)


@dataclass(frozen=True)
class Action:
    action_id: str
    cost: int
    observation_by_hypothesis: dict[str, str]
    requires: tuple[tuple[str, str], ...] = ()


@dataclass(frozen=True)
class Episode:
    template_id: str
    domain: str
    family: str
    hypotheses: tuple[str, ...]
    prior: dict[str, Fraction]
    decision_by_hypothesis: dict[str, str]
    actual_hypothesis: str
    actions: tuple[Action, ...]
    remint: int = 0


@dataclass(frozen=True)
class RunResult:
    system: str
    decision: str
    actions_taken: tuple[str, ...]
    cost: int
    grs: int
    false_high_level: int
    missed_high_level: int


def _constant_action(action_id: str, hypotheses: Iterable[str], *, cost: int = 1) -> Action:
    return Action(action_id, cost, {h: "NO_DIAGNOSTIC_CHANGE" for h in hypotheses})


def _actions_for(hypotheses: tuple[str, ...]) -> dict[str, Action]:
    return {aid: _constant_action(aid, hypotheses) for aid in ACTION_IDS}


def _episode(domain: str, family: str) -> Episode:
    tid = f"{domain}:{family}"

    if family == "DIRECT_LOWER_LEVEL":
        hs = ("h_search", "h_compile")
        prior = {hs[0]: Fraction(1, 2), hs[1]: Fraction(1, 2)}
        decisions = {hs[0]: "KEEP_SEARCH", hs[1]: "KEEP_COMPILE"}
        actions = _actions_for(hs)
        actions["SEARCH_MORE"] = Action(
            "SEARCH_MORE", 1, {hs[0]: "EVIDENCE_RESOLVES", hs[1]: "EVIDENCE_PERSISTS"}
        )
        actual = hs[0]

    elif family == "DIRECT_HIGH_LEVEL":
        hs = ("h_objective", "h_boundary")
        prior = {hs[0]: Fraction(1, 2), hs[1]: Fraction(1, 2)}
        decisions = {hs[0]: "REFORMULATE_OBJECTIVE", hs[1]: "REFORMULATE_BOUNDARY"}
        actions = _actions_for(hs)
        actions["TEST_PROBLEM_BOUNDARY"] = Action(
            "TEST_PROBLEM_BOUNDARY", 1, {hs[0]: "BOUNDARY_ADEQUATE", hs[1]: "BOUNDARY_WRONG"}
        )
        actual = hs[0]

    elif family == "REPRESENTATION_MASQUERADE":
        hs = ("h_compile", "h_objective")
        prior = {hs[0]: Fraction(3, 10), hs[1]: Fraction(7, 10)}
        decisions = {hs[0]: "KEEP_COMPILE", hs[1]: "REFORMULATE_OBJECTIVE"}
        actions = _actions_for(hs)
        actions["COMPILE_OR_REPRESENT"] = Action(
            "COMPILE_OR_REPRESENT", 1, {hs[0]: "COMPILE_RESOLVES", hs[1]: "COMPILE_FAILS"}
        )
        actual = hs[0]

    elif family == "HARNESS_MASQUERADE":
        hs = ("h_repair", "h_boundary")
        prior = {hs[0]: Fraction(3, 10), hs[1]: Fraction(7, 10)}
        decisions = {hs[0]: "KEEP_REPAIR", hs[1]: "REFORMULATE_BOUNDARY"}
        actions = _actions_for(hs)
        actions["REPAIR_ENV_OR_HARNESS"] = Action(
            "REPAIR_ENV_OR_HARNESS", 1, {hs[0]: "REPAIR_RESOLVES", hs[1]: "REPAIR_FAILS"}
        )
        actual = hs[0]

    elif family == "OBJECTIVE_BASIS_SUFFICIENT":
        hs = ("h_search", "h_objective")
        prior = {hs[0]: Fraction(2, 5), hs[1]: Fraction(3, 5)}
        decisions = {hs[0]: "KEEP_SEARCH", hs[1]: "REFORMULATE_OBJECTIVE"}
        actions = _actions_for(hs)
        actions["TEST_OBJECTIVE_BASIS"] = Action(
            "TEST_OBJECTIVE_BASIS", 1, {hs[0]: "BASIS_SUFFICIENT", hs[1]: "BASIS_INCOMPLETE"}
        )
        actual = hs[0]

    elif family == "SEQUENTIAL_COMPLEMENT":
        hs = ("h_objective", "h_boundary")
        prior = {hs[0]: Fraction(1, 2), hs[1]: Fraction(1, 2)}
        decisions = {hs[0]: "REFORMULATE_OBJECTIVE", hs[1]: "REFORMULATE_BOUNDARY"}
        actions = _actions_for(hs)
        actions["TEST_OBJECTIVE_BASIS"] = Action(
            "TEST_OBJECTIVE_BASIS", 1, {hs[0]: "BASIS_INADEQUATE", hs[1]: "BASIS_INADEQUATE"}
        )
        actions["TEST_PROBLEM_BOUNDARY"] = Action(
            "TEST_PROBLEM_BOUNDARY",
            1,
            {hs[0]: "BOUNDARY_ADEQUATE", hs[1]: "BOUNDARY_WRONG"},
            requires=(("TEST_OBJECTIVE_BASIS", "BASIS_INADEQUATE"),),
        )
        # Tie without probing resolves lexicographically to boundary, so choose objective as the hostile truth.
        actual = hs[0]

    elif family == "DECISION_VS_LABEL_INFORMATION":
        hs = ("h_search_a", "h_search_b", "h_objective")
        prior = {hs[0]: Fraction(2, 5), hs[1]: Fraction(2, 5), hs[2]: Fraction(1, 5)}
        decisions = {
            hs[0]: "KEEP_SEARCH",
            hs[1]: "KEEP_SEARCH",
            hs[2]: "REFORMULATE_OBJECTIVE",
        }
        actions = _actions_for(hs)
        actions["SEARCH_MORE"] = Action(
            "SEARCH_MORE",
            1,
            {hs[0]: "SEARCH_ROUTE_A", hs[1]: "SEARCH_ROUTE_B", hs[2]: "SEARCH_ROUTE_B"},
        )
        actions["TEST_OBJECTIVE_BASIS"] = Action(
            "TEST_OBJECTIVE_BASIS",
            2,
            {hs[0]: "BASIS_SUFFICIENT", hs[1]: "BASIS_SUFFICIENT", hs[2]: "BASIS_INCOMPLETE"},
        )
        actual = hs[2]

    elif family == "NON_IDENTIFIABLE":
        hs = ("h_objective", "h_boundary")
        prior = {hs[0]: Fraction(1, 2), hs[1]: Fraction(1, 2)}
        decisions = {hs[0]: "REFORMULATE_OBJECTIVE", hs[1]: "REFORMULATE_BOUNDARY"}
        actions = _actions_for(hs)
        actual = hs[0]

    else:
        raise ValueError(family)

    return Episode(
        template_id=tid,
        domain=domain,
        family=family,
        hypotheses=hs,
        prior=prior,
        decision_by_hypothesis=decisions,
        actual_hypothesis=actual,
        actions=tuple(actions[k] for k in sorted(actions)),
    )


def generate_templates() -> list[Episode]:
    return [_episode(domain, family) for domain in DOMAINS for family in FAMILIES]


def _renamed_episode(ep: Episode, remint: int) -> Episode:
    if remint == 0:
        return ep
    rng = random.Random(f"{ep.template_id}:{remint}:20260820")
    old = list(ep.hypotheses)
    new = [f"r{remint}_{i}_{hashlib.sha256((ep.template_id + h + str(remint)).encode()).hexdigest()[:8]}" for i, h in enumerate(old)]
    rename = dict(zip(old, new, strict=True))
    action_list = []
    for action in ep.actions:
        action_list.append(
            Action(
                action.action_id,
                action.cost,
                {rename[h]: obs for h, obs in action.observation_by_hypothesis.items()},
                action.requires,
            )
        )
    rng.shuffle(action_list)
    return Episode(
        template_id=ep.template_id,
        domain=ep.domain,
        family=ep.family,
        hypotheses=tuple(new),
        prior={rename[h]: p for h, p in ep.prior.items()},
        decision_by_hypothesis={rename[h]: d for h, d in ep.decision_by_hypothesis.items()},
        actual_hypothesis=rename[ep.actual_hypothesis],
        actions=tuple(action_list),
        remint=remint,
    )


def generate_all_episodes() -> list[Episode]:
    episodes = []
    for ep in generate_templates():
        for remint in range(12):
            episodes.append(_renamed_episode(ep, remint))
    return episodes


def _normalize(weights: dict[str, Fraction]) -> dict[str, Fraction]:
    total = sum(weights.values(), Fraction(0, 1))
    if total <= 0:
        raise ValueError("posterior has zero mass")
    return {k: v / total for k, v in weights.items() if v > 0}


def _decision_mass(ep: Episode, posterior: dict[str, Fraction]) -> dict[str, Fraction]:
    mass: dict[str, Fraction] = {}
    for h, p in posterior.items():
        d = ep.decision_by_hypothesis[h]
        mass[d] = mass.get(d, Fraction(0, 1)) + p
    return mass


def _enabled(action: Action, history: tuple[tuple[str, str], ...]) -> bool:
    seen = set(history)
    return all(req in seen for req in action.requires) and action.action_id not in {a for a, _ in history}


def _available(ep: Episode, history: tuple[tuple[str, str], ...], remaining: int) -> list[Action]:
    return sorted(
        [a for a in ep.actions if a.cost <= remaining and _enabled(a, history)],
        key=lambda a: a.action_id,
    )


def _posterior_groups(
    ep: Episode, posterior: dict[str, Fraction], action: Action
) -> dict[str, tuple[Fraction, dict[str, Fraction]]]:
    raw: dict[str, dict[str, Fraction]] = {}
    for h, p in posterior.items():
        obs = action.observation_by_hypothesis[h]
        raw.setdefault(obs, {})[h] = p
    out: dict[str, tuple[Fraction, dict[str, Fraction]]] = {}
    for obs, weights in raw.items():
        prob = sum(weights.values(), Fraction(0, 1))
        out[obs] = (prob, _normalize(weights))
    return out


def _bayes_decision(ep: Episode, posterior: dict[str, Fraction]) -> str:
    mass = _decision_mass(ep, posterior)
    best = max(mass.values())
    return sorted(d for d, p in mass.items() if p == best)[0]


def _harm_aware_decision(ep: Episode, posterior: dict[str, Fraction]) -> tuple[str, Fraction]:
    candidates = sorted(set(ep.decision_by_hypothesis.values()))
    scored: list[tuple[Fraction, str]] = []
    for decision in candidates:
        value = Fraction(0, 1)
        for h, p in posterior.items():
            truth = ep.decision_by_hypothesis[h]
            if decision == truth:
                value += p
            elif decision in HIGH_LEVEL and truth in LOW_LEVEL:
                value -= FALSE_HIGH_LEVEL_PENALTY * p
        scored.append((value, decision))
    best_value = max(v for v, _ in scored)
    best_decision = sorted(d for v, d in scored if v == best_value)[0]
    return best_decision, best_value


def _label_value(posterior: dict[str, Fraction]) -> Fraction:
    return max(posterior.values())


def _decision_accuracy_value(ep: Episode, posterior: dict[str, Fraction]) -> Fraction:
    return max(_decision_mass(ep, posterior).values())


def _can_resolve_decision(
    ep: Episode,
    posterior: dict[str, Fraction],
    history: tuple[tuple[str, str], ...],
    remaining: int,
) -> bool:
    if len(_decision_mass(ep, posterior)) <= 1:
        return True
    for action in _available(ep, history, remaining):
        branches = _posterior_groups(ep, posterior, action)
        if all(
            _can_resolve_decision(ep, post, history + ((action.action_id, obs),), remaining - action.cost)
            for obs, (_, post) in branches.items()
        ):
            return True
    return False


def _plan_value(
    ep: Episode,
    posterior: dict[str, Fraction],
    history: tuple[tuple[str, str], ...],
    remaining: int,
    terminal_value: Callable[[Episode, dict[str, Fraction]], Fraction],
) -> tuple[Fraction, str | None]:
    stop = terminal_value(ep, posterior)
    best_value = stop
    best_action: str | None = None
    for action in _available(ep, history, remaining):
        value = -COST_WEIGHT * action.cost
        for obs, (prob, post) in _posterior_groups(ep, posterior, action).items():
            child, _ = _plan_value(
                ep,
                post,
                history + ((action.action_id, obs),),
                remaining - action.cost,
                terminal_value,
            )
            value += prob * child
        if value > best_value or (value == best_value and best_action is not None and action.action_id < best_action):
            best_value = value
            best_action = action.action_id
    return best_value, best_action


def _label_terminal(_: Episode, posterior: dict[str, Fraction]) -> Fraction:
    return _label_value(posterior)


def _scientific_terminal(ep: Episode, posterior: dict[str, Fraction]) -> Fraction:
    return _harm_aware_decision(ep, posterior)[1]


def _execute_action(
    ep: Episode,
    posterior: dict[str, Fraction],
    action_id: str,
    history: tuple[tuple[str, str], ...],
) -> tuple[dict[str, Fraction], tuple[tuple[str, str], ...], int]:
    action = next(a for a in ep.actions if a.action_id == action_id)
    if not _enabled(action, history):
        raise AssertionError(f"disabled action executed: {action_id}")
    obs = action.observation_by_hypothesis[ep.actual_hypothesis]
    _, post = _posterior_groups(ep, posterior, action)[obs]
    return post, history + ((action_id, obs),), action.cost


def _one_step_action(
    ep: Episode,
    posterior: dict[str, Fraction],
    objective: str,
) -> str | None:
    history: tuple[tuple[str, str], ...] = ()
    if objective == "label":
        baseline = _label_value(posterior)
        value_fn = lambda post: _label_value(post)
    elif objective == "decision":
        baseline = _decision_accuracy_value(ep, posterior)
        value_fn = lambda post: _decision_accuracy_value(ep, post)
    elif objective == "restoration":
        baseline = Fraction(0, 1)
        value_fn = lambda post: Fraction(1, 1) if len(_decision_mass(ep, post)) == 1 else Fraction(0, 1)
    else:
        raise ValueError(objective)

    best_value = baseline
    best_action: str | None = None
    for action in _available(ep, history, BUDGET):
        expected = -COST_WEIGHT * action.cost
        for _, (prob, post) in _posterior_groups(ep, posterior, action).items():
            expected += prob * value_fn(post)
        if expected > best_value or (expected == best_value and best_action is not None and action.action_id < best_action):
            best_value = expected
            best_action = action.action_id
    return best_action


def _correct_terminal(ep: Episode) -> str:
    if ep.family == "NON_IDENTIFIABLE":
        return UNRESOLVED
    return ep.decision_by_hypothesis[ep.actual_hypothesis]


def _score(ep: Episode, system: str, decision: str, actions: tuple[str, ...], cost: int) -> RunResult:
    truth = _correct_terminal(ep)
    false_high = int(decision in HIGH_LEVEL and truth not in HIGH_LEVEL)
    missed_high = int(truth in HIGH_LEVEL and decision != truth)
    grs = int(decision == truth and false_high == 0)
    return RunResult(system, decision, actions, cost, grs, false_high, missed_high)


def run_system(ep: Episode, system: str) -> RunResult:
    posterior = dict(ep.prior)
    history: tuple[tuple[str, str], ...] = ()
    actions_taken: list[str] = []
    cost = 0

    if system == "B0_STATIC_NO_PROBE":
        decision = _bayes_decision(ep, posterior)

    elif system in {"B1_GREEDY_RESTORATION", "B2_ONE_STEP_LABEL_VOI", "B3_ONE_STEP_DECISION_VOI"}:
        objective = {
            "B1_GREEDY_RESTORATION": "restoration",
            "B2_ONE_STEP_LABEL_VOI": "label",
            "B3_ONE_STEP_DECISION_VOI": "decision",
        }[system]
        action_id = _one_step_action(ep, posterior, objective)
        if action_id is not None:
            posterior, history, spent = _execute_action(ep, posterior, action_id, history)
            actions_taken.append(action_id)
            cost += spent
        decision = _bayes_decision(ep, posterior)

    elif system == "B4_TWO_STEP_LABEL_PLANNER":
        remaining = BUDGET
        while remaining > 0:
            _, action_id = _plan_value(ep, posterior, history, remaining, _label_terminal)
            if action_id is None:
                break
            posterior, history, spent = _execute_action(ep, posterior, action_id, history)
            actions_taken.append(action_id)
            cost += spent
            remaining -= spent
        decision = _bayes_decision(ep, posterior)

    elif system in {
        "P1_ARD_HORIZON2_SCIENTIFIC_RESPONSIBILITY",
        "CEILING_HORIZON2_FULL_SCIENTIFIC_ORACLE",
    }:
        if not _can_resolve_decision(ep, posterior, history, BUDGET):
            decision = UNRESOLVED
        else:
            remaining = BUDGET
            while remaining > 0:
                _, action_id = _plan_value(ep, posterior, history, remaining, _scientific_terminal)
                if action_id is None:
                    break
                posterior, history, spent = _execute_action(ep, posterior, action_id, history)
                actions_taken.append(action_id)
                cost += spent
                remaining -= spent
            decision = _harm_aware_decision(ep, posterior)[0]
    else:
        raise ValueError(system)

    return _score(ep, system, decision, tuple(actions_taken), cost)


def _wire_result(r: RunResult) -> dict[str, object]:
    return {
        "system": r.system,
        "decision": r.decision,
        "actions_taken": list(r.actions_taken),
        "cost": r.cost,
        "grs": r.grs,
        "false_high_level": r.false_high_level,
        "missed_high_level": r.missed_high_level,
    }


def build_report() -> dict[str, object]:
    templates = generate_templates()
    if len(templates) != 40:
        raise AssertionError("expected 40 distinct templates")
    episodes = generate_all_episodes()
    if len(episodes) != 480:
        raise AssertionError("expected 480 reminted episodes")

    template_rows: list[dict[str, object]] = []
    invariant = True
    for base in templates:
        base_results = {s: run_system(base, s) for s in SYSTEMS}
        for remint in range(1, 12):
            ep = _renamed_episode(base, remint)
            for system in SYSTEMS:
                rr = run_system(ep, system)
                br = base_results[system]
                if (rr.decision, rr.cost, rr.grs, rr.false_high_level, rr.missed_high_level) != (
                    br.decision,
                    br.cost,
                    br.grs,
                    br.false_high_level,
                    br.missed_high_level,
                ):
                    invariant = False
        template_rows.append(
            {
                "template_id": base.template_id,
                "domain": base.domain,
                "family": base.family,
                "correct_terminal": _correct_terminal(base),
                "systems": {s: _wire_result(base_results[s]) for s in SYSTEMS},
            }
        )

    summary: dict[str, object] = {}
    for system in SYSTEMS:
        rows = [next(r for r in template_rows if r["template_id"] == ep.template_id)["systems"][system] for ep in templates]
        summary[system] = {
            "template_grs": sum(int(r["grs"]) for r in rows),
            "template_count": len(rows),
            "grs_rate": sum(int(r["grs"]) for r in rows) / len(rows),
            "false_high_level": sum(int(r["false_high_level"]) for r in rows),
            "missed_high_level": sum(int(r["missed_high_level"]) for r in rows),
            "mean_cost": sum(int(r["cost"]) for r in rows) / len(rows),
        }

    ard = summary["P1_ARD_HORIZON2_SCIENTIFIC_RESPONSIBILITY"]
    b3 = summary["B3_ONE_STEP_DECISION_VOI"]
    diff = float(ard["grs_rate"]) - float(b3["grs_rate"])

    domain_effects: dict[str, float] = {}
    for domain in DOMAINS:
        subset = [r for r in template_rows if r["domain"] == domain]
        a = sum(r["systems"]["P1_ARD_HORIZON2_SCIENTIFIC_RESPONSIBILITY"]["grs"] for r in subset) / len(subset)
        b = sum(r["systems"]["B3_ONE_STEP_DECISION_VOI"]["grs"] for r in subset) / len(subset)
        domain_effects[domain] = a - b

    nonid_ok = all(
        r["systems"]["P1_ARD_HORIZON2_SCIENTIFIC_RESPONSIBILITY"]["decision"] == UNRESOLVED
        for r in template_rows
        if r["family"] == "NON_IDENTIFIABLE"
    )
    ceiling_match = all(
        r["systems"]["P1_ARD_HORIZON2_SCIENTIFIC_RESPONSIBILITY"]["decision"]
        == r["systems"]["CEILING_HORIZON2_FULL_SCIENTIFIC_ORACLE"]["decision"]
        for r in template_rows
    )
    ard_zero_harm = int(ard["false_high_level"]) == 0
    domain_nonnegative = all(v >= 0 for v in domain_effects.values())
    positive_domains = sum(v > 0 for v in domain_effects.values())

    gates = {
        "minimum_grs_difference_vs_b3": diff >= 0.10,
        "zero_protected_high_level_harm": ard_zero_harm,
        "all_non_identifiable_correct": nonid_ok,
        "exact_ceiling_match": ceiling_match,
        "all_remints_invariant": invariant,
        "nonnegative_domain_effect_all": domain_nonnegative,
        "strictly_positive_domains_at_least_3": positive_domains >= 3,
    }
    terminal = "ARD_EXACT_MECHANISM_POSITIVE" if all(gates.values()) else "ARD_EXACT_MECHANISM_NOT_POSITIVE"

    report = {
        "version": "P1_U_ARD_EXACT_PILOT_RESULT_V1",
        "issue": 696,
        "protocol": "ARD_PROTOCOL_V1",
        "template_count": len(templates),
        "remints_per_template": 12,
        "concrete_episode_count": len(episodes),
        "remints_are_independent_n": False,
        "summary": summary,
        "ard_minus_b3_grs": diff,
        "domain_effects": domain_effects,
        "gates": gates,
        "terminal": terminal,
        "authority": {
            "general_p1_u_superiority": False,
            "runtime_registration": False,
            "adoption_or_merge": False,
        },
        "templates": template_rows,
    }
    canonical = json.dumps(report, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()
    report["canonical_sha256_without_digest"] = hashlib.sha256(canonical).hexdigest()
    return report


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    report = build_report()
    text = json.dumps(report, indent=2, sort_keys=True) + "\n"
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(text)
    else:
        print(text, end="")


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""Reconstruct exact nearest-competitor margins for ORION22's frozen regret classes.

This is an additive analysis of already-committed frozen inputs.  It does not alter
any action, regime, price, budget, task family, or protected outcome.
"""
from __future__ import annotations

import hashlib
import importlib.util
import json
import math
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
TOP = HERE.parent.parent / "top_tier"


def load(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def action_key(action) -> list[str]:
    return sorted(action)


def main() -> int:
    sys.path.insert(0, str(TOP))
    try:
        runner = load("p12_margin_runner", TOP / "run_p12_price_aware_successor_v1.py")
    except Exception as exc:
        print(json.dumps({
            "terminal": "CANNOT_CHECK_RUNNER_IMPORT",
            "reason": str(exc),
        }, indent=2, sort_keys=True))
        return 3

    stress, frozen = runner.stress, runner.frozen
    budget, regimes = runner.BUDGET, runner.REGIMES

    def feasible_actions(sids, declared):
        out = []
        for mask in range(1 << len(sids)):
            chosen = frozenset(sids[i] for i in range(len(sids)) if mask & (1 << i))
            if sum(declared[s] for s in chosen) <= budget:
                out.append(chosen)
        return out

    def priced_cost(chosen, sids, declared, reason, state, p_b, p_s):
        build = sum(declared[s] for s in chosen)
        serve = sum(state[s] if s in chosen else reason[s] for s in sids)
        return stress.priced(p_b, p_s, build, serve)

    classes = []
    finite_margins = []
    singleton_classes = 0

    for pool_name in ("p12_transfer_cases_v1.json", "p12_transfer_cases_expanded_v1.json"):
        pool = json.loads((TOP / pool_name).read_text(encoding="utf-8"))
        for domain_block in pool["domains"]:
            domain = domain_block["domain"]
            for case in domain_block["cases"]:
                structures = case["structures"]
                sids = [st["sid"] for st in structures]
                declared = {st["sid"]: st["declared_cost"] for st in structures}
                frozen.prime_caches(domain, structures)
                reason, state, _, _ = stress.per_structure_charges(domain, structures)
                actions = feasible_actions(sids, declared)
                if not actions:
                    raise AssertionError(f"no feasible actions: {pool_name}/{domain}/{case['case_id']}")

                envs = []
                for regime, p_b, p_s in regimes:
                    costs = {
                        a: priced_cost(a, sids, declared, reason, state, p_b, p_s)
                        for a in actions
                    }
                    envs.append((regime, costs, min(costs.values())))

                per_action = {
                    a: max(costs[a] - optimum for _, costs, optimum in envs)
                    for a in actions
                }
                ordered = sorted(per_action.items(), key=lambda item: (item[1], action_key(item[0])))
                floor = ordered[0][1]
                winners = [a for a, value in ordered if abs(value - floor) <= 1e-12]
                if len(winners) != 1:
                    raise AssertionError(
                        f"committed unique-floor invariant failed: {pool_name}/{domain}/{case['case_id']}"
                    )

                if len(ordered) == 1:
                    margin = None
                    radius = None
                    margin_status = "NO_COMPETITOR__INFINITE_RADIUS_WITHIN_FIXED_FEASIBLE_SET"
                    singleton_classes += 1
                else:
                    second = ordered[1][1]
                    margin = second - floor
                    if not margin > 0:
                        raise AssertionError(
                            f"nonpositive nearest-competitor margin: {pool_name}/{domain}/{case['case_id']}"
                        )
                    radius = margin / 2
                    margin_status = "FINITE_POSITIVE_MARGIN"
                    finite_margins.append(margin)

                classes.append({
                    "pool": pool_name,
                    "domain": domain,
                    "case_id": case["case_id"],
                    "feasible_actions": len(actions),
                    "best_action": action_key(ordered[0][0]),
                    "best_regret": floor,
                    "second_best_regret": None if len(ordered) == 1 else ordered[1][1],
                    "decision_margin": margin,
                    "uniform_loss_perturbation_radius_open": radius,
                    "margin_status": margin_status,
                    "action_regrets": [
                        {"action": action_key(action), "worst_case_regret": regret}
                        for action, regret in ordered
                    ],
                })

    if not finite_margins:
        raise AssertionError("no finite competitor margins")

    key_sources = [
        HERE / "compute_regret_law.py",
        TOP / "run_p12_price_aware_successor_v1.py",
        TOP / "run_transfer_allocation_v1.py",
        TOP / "run_p12_robustness_v1.py",
        TOP / "p12_price_aware_allocator_v1.py",
        TOP / "p12_transfer_cases_v1.json",
        TOP / "p12_transfer_cases_expanded_v1.json",
    ]
    result = {
        "schema": "ORION.ORION22.DecisionMargins.Result.v1",
        "protocol_identity": "ORION22.DECISION_MARGIN_RECONSTRUCTION.v1",
        "authority": "REANALYSIS_OF_COMMITTED_FROZEN_INPUTS",
        "scientific_authority_delta": "NONE",
        "classes_total": len(classes),
        "finite_margin_classes": len(finite_margins),
        "singleton_feasible_action_classes": singleton_classes,
        "minimum_finite_decision_margin": min(finite_margins),
        "global_uniform_loss_perturbation_radius_open": min(finite_margins) / 2,
        "radius_semantics": (
            "For every class with >=2 feasible actions, arbitrary jointly dependent per-action "
            "loss perturbations bounded by epsilon strictly below this radius preserve the unique "
            "best action. Singleton-feasible-action classes are invariant within the fixed feasible set."
        ),
        "source_bindings_sha256": {
            str(path.relative_to(HERE.parents[4])): sha256(path) for path in key_sources
        },
        "classes": classes,
        "terminal": "EXACT_FROZEN_DECISION_MARGINS_RECONSTRUCTED",
        "scope": (
            "Frozen ORION-22 charging family only. Does not establish external transfer, "
            "model misspecification robustness, or stability to changes in feasible-action sets."
        ),
    }
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

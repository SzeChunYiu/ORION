"""Exact MAX-R3B hostile witness for joint quantum obligation binding.

The construction formalizes a simple but load-bearing boundary.  Local verifier
success for semantics/access/error/resources is not sufficient if those receipts
are not bound to the same transformed object and assumptions.  Balanced hostile
pairs have identical local validation vectors and opposite admissibility outcomes;
therefore every deterministic controller restricted to that local vector has
accuracy at most 1/2.  A joint bound-obligation view separates all pairs.

This is an exact synthetic architecture result, not P10 method invention and not
a real quantum-algorithm claim.
"""

from __future__ import annotations

from collections import Counter, defaultdict
from hashlib import sha256
import json

DOMAINS = ("SYNTHESIS", "ALGO_INTERFACE", "QEC_CODESIGN", "FORMAL_REASONING")
FAMILIES = (
    "SEMANTIC_BINDING",
    "ACCESS_BINDING",
    "ERROR_NORM_BINDING",
    "RESOURCE_BINDING",
    "STALE_FAILURE_SCOPE",
    "AMBIGUOUS_TRANSPORT",
)
REMINTS_PER_DOMAIN = 100


def digest(payload: object) -> str:
    raw = json.dumps(payload, sort_keys=True, separators=(",", ":"))
    return sha256(raw.encode("utf-8")).hexdigest()


def pair(domain: str, remint: int, family: str) -> list[dict[str, object]]:
    surface = digest({"domain": domain, "remint": remint, "family": family})[:16]

    valid_local = {
        "semantic_check": True,
        "access_check": True,
        "error_check": True,
        "resource_check": True,
        "previous_failure": False,
        "transport_ambiguous": False,
    }
    bound = {
        "semantic_bound_current": True,
        "access_bound_current": True,
        "error_norm_bound_current": True,
        "resource_bound_current": True,
        "failure_scope_stale": False,
        "ambiguity_unresolved": False,
    }

    left_local = dict(valid_local)
    right_local = dict(valid_local)
    left_bound = dict(bound)
    right_bound = dict(bound)

    if family == "SEMANTIC_BINDING":
        left_gold, right_gold = "ADMIT", "BLOCK"
        right_bound["semantic_bound_current"] = False
    elif family == "ACCESS_BINDING":
        left_gold, right_gold = "ADMIT", "BLOCK"
        right_bound["access_bound_current"] = False
    elif family == "ERROR_NORM_BINDING":
        left_gold, right_gold = "ADMIT", "BLOCK"
        right_bound["error_norm_bound_current"] = False
    elif family == "RESOURCE_BINDING":
        left_gold, right_gold = "ADMIT", "BLOCK"
        right_bound["resource_bound_current"] = False
    elif family == "STALE_FAILURE_SCOPE":
        left_local["previous_failure"] = True
        right_local["previous_failure"] = True
        left_gold, right_gold = "REOPEN", "BLOCK"
        left_bound["failure_scope_stale"] = True
    elif family == "AMBIGUOUS_TRANSPORT":
        left_local["transport_ambiguous"] = True
        right_local["transport_ambiguous"] = True
        left_gold, right_gold = "ADMIT", "CANNOT_CHECK"
        right_bound["ambiguity_unresolved"] = True
    else:  # pragma: no cover - frozen family guard
        raise ValueError(f"unsupported family: {family}")

    return [
        {"surface": surface, "local": left_local, "bound": left_bound, "gold": left_gold},
        {"surface": surface, "local": right_local, "bound": right_bound, "gold": right_gold},
    ]


def view_key(sample: dict[str, object], *, bound: bool) -> str:
    payload: dict[str, object] = {
        "surface": sample["surface"],
        "local": sample["local"],
    }
    if bound:
        payload["bound"] = sample["bound"]
    return digest(payload)


def ceiling(samples: list[dict[str, object]], *, bound: bool) -> dict[str, object]:
    buckets: dict[str, list[str]] = defaultdict(list)
    for sample in samples:
        buckets[view_key(sample, bound=bound)].append(str(sample["gold"]))
    correct = sum(max(Counter(labels).values()) for labels in buckets.values())
    return {
        "accuracy": correct / len(samples),
        "distinct_views": len(buckets),
        "ambiguous_view_buckets": sum(len(set(labels)) > 1 for labels in buckets.values()),
    }


def joint_rule(sample: dict[str, object]) -> str:
    local = sample["local"]
    bound = sample["bound"]
    if local["transport_ambiguous"] and bound["ambiguity_unresolved"]:
        return "CANNOT_CHECK"
    if local["previous_failure"]:
        return "REOPEN" if bound["failure_scope_stale"] else "BLOCK"
    if not all(
        (
            bound["semantic_bound_current"],
            bound["access_bound_current"],
            bound["error_norm_bound_current"],
            bound["resource_bound_current"],
        )
    ):
        return "BLOCK"
    return "ADMIT"


def main() -> None:
    samples: list[dict[str, object]] = []
    for domain in DOMAINS:
        for remint in range(REMINTS_PER_DOMAIN):
            for family in FAMILIES:
                hostile_pair = pair(domain, remint, family)
                if hostile_pair[0]["local"] != hostile_pair[1]["local"]:
                    raise AssertionError(f"local-view mismatch in {family}")
                samples.extend(hostile_pair)

    local = ceiling(samples, bound=False)
    joint = ceiling(samples, bound=True)
    joint_accuracy = sum(joint_rule(sample) == sample["gold"] for sample in samples) / len(samples)

    result = {
        "schema": "ORIONQ.MAXR3BJointObligationBindingResult.v1",
        "domains": list(DOMAINS),
        "families": list(FAMILIES),
        "remints_per_domain": REMINTS_PER_DOMAIN,
        "sample_count": len(samples),
        "local_donor_composition_ceiling": local,
        "joint_bound_obligation_ceiling": joint,
        "orion_joint_rule_accuracy": joint_accuracy,
        "theorem_boundary": (
            "For any balanced hostile pair with identical local verifier view and "
            "opposite gold decisions, every deterministic controller measurable with "
            "respect to the local view has pair accuracy at most 1/2."
        ),
        "terminal": "MAX_R3_EXTERNAL_DONOR_COMPOSITION_BINDING_BOUNDARY__EXACT_SYNTHETIC",
        "p10_incremental_value": False,
        "p7_p4_absorbed_into_incumbent": True,
        "novelty_authorized": False,
    }
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()

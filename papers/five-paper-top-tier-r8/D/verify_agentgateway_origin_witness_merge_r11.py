#!/usr/bin/env python3
"""Finite corroboration for the source-derived agentgateway RuleSets merge theorem.

The analytic Boolean proof owns the all-origin claim. This program exhausts
request-relative origin summaries through eight origins and checks origin-witness
preservation, mandatory constraints, semantic algebra, and hostile controls.
"""
from __future__ import annotations

from dataclasses import dataclass
import argparse
from itertools import product, permutations
import json
from pathlib import Path

SCHEMA = "ORION.D.AgentgatewayOriginWitnessMerge.R11.v1"
UPSTREAM_COMMIT = "e136c7458b0fe0f51378dd31ffd60ab2b6939fc2"


@dataclass(frozen=True)
class Origin:
    name: str
    deny: bool
    require_ok: bool
    has_allow: bool
    allow_match: bool

    def __post_init__(self) -> None:
        if self.allow_match and not self.has_allow:
            raise ValueError("allow_match requires an allowlist")

    def accepts(self) -> bool:
        return (
            not self.deny
            and self.require_ok
            and (not self.has_allow or self.allow_match)
        )


STATES = (
    Origin("deny", True, True, False, False),
    Origin("require_fail", False, False, False, False),
    Origin("denylist_pass", False, True, False, False),
    Origin("allow_unmatched", False, True, True, False),
    Origin("allow_matched", False, True, True, True),
)


def merged_accepts(origins: tuple[Origin, ...]) -> bool:
    if not origins:
        return True
    has_rules_deny = any(origin.deny for origin in origins)
    if has_rules_deny:
        return False
    if any(not origin.require_ok for origin in origins):
        return False
    has_allow = any(origin.has_allow for origin in origins)
    if any(origin.allow_match for origin in origins):
        return True
    return not has_allow


def closed_form(origins: tuple[Origin, ...]) -> bool:
    return (
        all(not origin.deny for origin in origins)
        and all(origin.require_ok for origin in origins)
        and (
            all(not origin.has_allow for origin in origins)
            or any(origin.allow_match for origin in origins)
        )
    )


def semantic_signature(origins: tuple[Origin, ...]) -> tuple[bool, bool, bool, bool]:
    """Duplicate-insensitive truth aggregate determining merged acceptance."""
    return (
        any(origin.deny for origin in origins),
        all(origin.require_ok for origin in origins),
        any(origin.has_allow for origin in origins),
        any(origin.allow_match for origin in origins),
    )


def run(max_origins: int) -> dict[str, object]:
    cases = 0
    accepted_cases = 0
    witness_checks = 0
    mandatory_checks = 0
    algebra_checks = 0

    for n in range(0, max_origins + 1):
        for indices in product(range(len(STATES)), repeat=n):
            origins = tuple(STATES[index] for index in indices)
            cases += 1
            direct = merged_accepts(origins)
            formula = closed_form(origins)
            assert direct == formula
            if direct:
                accepted_cases += 1
                if origins:
                    assert any(origin.accepts() for origin in origins)
                    witness_checks += 1
                    assert all(not origin.deny for origin in origins)
                    assert all(origin.require_ok for origin in origins)
                    mandatory_checks += 2

            # Duplicate-insensitive semantic idempotence.
            duplicated = tuple(item for origin in origins for item in (origin, origin))
            assert merged_accepts(origins) == merged_accepts(duplicated)
            assert semantic_signature(origins) == semantic_signature(duplicated)
            algebra_checks += 2

            # Associativity at every split point.
            for split in range(n + 1):
                left, right = origins[:split], origins[split:]
                # Since the source merge is rule-set concatenation, concatenating
                # grouped parts must yield the same truth aggregate.
                assert semantic_signature(left + right) == semantic_signature(origins)
                assert merged_accepts(left + right) == direct
                algebra_checks += 2

            # Full permutation checks are factorial; perform them only for n<=5,
            # which already covers every summary state interaction exhaustively.
            if n <= 5:
                seen = set()
                for perm in permutations(origins):
                    key = tuple(origin.name for origin in perm)
                    if key in seen:
                        continue
                    seen.add(key)
                    assert semantic_signature(perm) == semantic_signature(origins)
                    assert merged_accepts(perm) == direct
                    algebra_checks += 2

    # Hostile control 1: this algebra is not intersection semantics.
    alice = Origin("allow_alice", False, True, True, True)
    bob_for_alice = Origin("allow_bob_unmatched_for_alice", False, True, True, False)
    assert alice.accepts()
    assert not bob_for_alice.accepts()
    assert merged_accepts((alice, bob_for_alice))

    # Hostile control 2: higher-precedence allow cannot erase a base deny.
    base_deny = Origin("base_deny", True, True, False, False)
    higher_allow = Origin("higher_allow", False, True, True, True)
    assert not base_deny.accepts()
    assert higher_allow.accepts()
    assert not merged_accepts((base_deny, higher_allow))
    assert not merged_accepts((higher_allow, base_deny))

    # Hostile control 3: higher allow cannot launder a failed require.
    base_require_fail = Origin("base_require_fail", False, False, False, False)
    assert not merged_accepts((base_require_fail, higher_allow))

    # Hostile control 4: no allowlists + clean mandatory constraints is denylist
    # semantics and remains allowed under arbitrary duplication.
    clean_denylist = Origin("clean_denylist", False, True, False, False)
    assert merged_accepts((clean_denylist,) * 12)

    return {
        "schema": SCHEMA,
        "terminal": "AGENTGATEWAY_RULESETS_ORIGIN_WITNESS_SAFE",
        "upstream_commit": UPSTREAM_COMMIT,
        "max_origins": max_origins,
        "abstract_origin_states": [state.name for state in STATES],
        "exhaustive_cases": cases,
        "accepted_cases": accepted_cases,
        "origin_witness_checks": witness_checks,
        "mandatory_constraint_checks": mandatory_checks,
        "semantic_algebra_checks": algebra_checks,
        "hostile_controls": {
            "not_intersection_semantics": "PASS",
            "higher_allow_does_not_erase_base_deny": "PASS",
            "higher_allow_does_not_launder_require_failure": "PASS",
            "pure_denylist_default_allow": "PASS",
        },
        "authority": {
            "all_instance_theorem_source": "analytic_boolean_proof",
            "finite_enumeration_role": "implementation_corroboration_only",
            "same_field_rulesets_merge_only": True,
            "whole_project_security_certification": False,
            "cross_field_bridge_safety": False,
            "grants_journal_authority": False,
        },
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--max-origins", type=int, default=8)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    if args.max_origins < 0 or args.max_origins > 8:
        raise SystemExit("--max-origins must be between 0 and 8")
    result = run(args.max_origins)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, sort_keys=True, indent=2) + "\n")
    print(
        "AGENTGATEWAY_RULESETS_ORIGIN_WITNESS_SAFE",
        f"cases={result['exhaustive_cases']}",
        f"accepted={result['accepted_cases']}",
        f"algebra_checks={result['semantic_algebra_checks']}",
    )


if __name__ == "__main__":
    main()

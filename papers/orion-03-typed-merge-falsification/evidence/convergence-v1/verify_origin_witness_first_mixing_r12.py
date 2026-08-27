#!/usr/bin/env python3
"""Finite corroboration for Paper D R12 origin-witness propagation.

The implementation uses a direct topological witness-set recurrence and checks
it against independently computed per-origin Horn closures.  It also extracts
a first-mixing frontier for every hybrid atom and retains hostile alternative-
proof and single-slot controls.
"""
from __future__ import annotations

import argparse
import hashlib
import itertools
import json
from pathlib import Path
import random
from typing import Any, Iterable

SCHEMA = "ORION.TypedAuthority.FirstMixing.R12.v1"
TERMINAL = "TYPED_AUTHORITY_FIRST_MIXING_R12_PASS"
SOURCE_BASE = "f6b21c94b9cd372700d7a13ccc229e27637acef9"
SEED = 20260826

Rule = tuple[int, tuple[int, ...]]


def canonical_json(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def validate_program(atom_count: int, rules: tuple[Rule, ...]) -> None:
    for head, body in rules:
        if not 0 <= head < atom_count:
            raise ValueError(("invalid head", head))
        if not body:
            raise ValueError("empty-body rules are outside the R12 subject")
        if len(set(body)) != len(body):
            raise ValueError(("duplicate body atom", head, body))
        if any(not 0 <= atom < head for atom in body):
            raise ValueError(("program is not topologically acyclic", head, body))


def closure(atom_count: int, rules: tuple[Rule, ...], seeds: Iterable[int]) -> frozenset[int]:
    reached = set(seeds)
    for atom in range(atom_count):
        if atom in reached:
            continue
        if any(head == atom and all(body_atom in reached for body_atom in body) for head, body in rules):
            reached.add(atom)
    return frozenset(reached)


def independent_witnesses(
    atom_count: int,
    rules: tuple[Rule, ...],
    seed_by_origin: tuple[frozenset[int], ...],
) -> tuple[frozenset[int], ...]:
    closures = [closure(atom_count, rules, seeds) for seeds in seed_by_origin]
    return tuple(
        frozenset(origin for origin, reached in enumerate(closures) if atom in reached)
        for atom in range(atom_count)
    )


def witness_recurrence(
    atom_count: int,
    rules: tuple[Rule, ...],
    seed_by_origin: tuple[frozenset[int], ...],
) -> tuple[frozenset[int], ...]:
    seed_origins = [set() for _ in range(atom_count)]
    for origin, seeds in enumerate(seed_by_origin):
        for atom in seeds:
            seed_origins[atom].add(origin)
    witness: list[set[int]] = [set(origins) for origins in seed_origins]
    by_head: dict[int, list[tuple[int, ...]]] = {}
    for head, body in rules:
        by_head.setdefault(head, []).append(body)
    for atom in range(atom_count):
        for body in by_head.get(atom, []):
            contribution = set(witness[body[0]])
            for premise in body[1:]:
                contribution.intersection_update(witness[premise])
            witness[atom].update(contribution)
    return tuple(frozenset(origins) for origins in witness)


def pooled_recurrence(
    atom_count: int,
    rules: tuple[Rule, ...],
    seed_by_origin: tuple[frozenset[int], ...],
) -> tuple[bool, ...]:
    pooled_seed = set().union(*seed_by_origin) if seed_by_origin else set()
    reached = [False] * atom_count
    by_head: dict[int, list[tuple[int, ...]]] = {}
    for head, body in rules:
        by_head.setdefault(head, []).append(body)
    for atom in range(atom_count):
        reached[atom] = atom in pooled_seed or any(
            all(reached[premise] for premise in body)
            for body in by_head.get(atom, [])
        )
    return tuple(reached)


def pooled_parent_rules(
    atom_count: int,
    rules: tuple[Rule, ...],
    seed_by_origin: tuple[frozenset[int], ...],
    pooled: tuple[bool, ...],
) -> dict[int, Rule]:
    pooled_seed = set().union(*seed_by_origin) if seed_by_origin else set()
    parent: dict[int, Rule] = {}
    for atom in range(atom_count):
        if atom in pooled_seed:
            continue
        choices = sorted(
            (rule for rule in rules if rule[0] == atom and all(pooled[p] for p in rule[1])),
            key=lambda rule: (len(rule[1]), rule[1]),
        )
        if pooled[atom]:
            if not choices:
                raise AssertionError(("pooled atom lacks proof rule", atom))
            parent[atom] = choices[0]
    return parent


def first_mixing_certificate(
    target: int,
    witnesses: tuple[frozenset[int], ...],
    pooled: tuple[bool, ...],
    parent: dict[int, Rule],
) -> dict[str, Any]:
    if not pooled[target] or witnesses[target]:
        raise ValueError("target is not hybrid")
    path = [target]
    current = target
    while True:
        head, body = parent[current]
        hybrid_children = [premise for premise in body if pooled[premise] and not witnesses[premise]]
        if hybrid_children:
            current = min(hybrid_children)
            path.append(current)
            continue
        if not all(pooled[premise] and witnesses[premise] for premise in body):
            raise AssertionError(("frontier premises are not independently supported", head, body))
        intersection = set(witnesses[body[0]])
        for premise in body[1:]:
            intersection.intersection_update(witnesses[premise])
        if intersection:
            raise AssertionError(("frontier has a common origin", head, body, intersection))
        return {
            "target": target,
            "frontier_head": head,
            "frontier_body": list(body),
            "premise_witnesses": [sorted(witnesses[premise]) for premise in body],
            "common_origin_intersection": [],
            "hybrid_path_target_to_frontier": path,
        }


def audit(
    atom_count: int,
    rules: tuple[Rule, ...],
    seed_by_origin: tuple[frozenset[int], ...],
) -> dict[str, Any]:
    validate_program(atom_count, rules)
    direct = independent_witnesses(atom_count, rules, seed_by_origin)
    recurrent = witness_recurrence(atom_count, rules, seed_by_origin)
    if direct != recurrent:
        raise AssertionError(("witness recurrence disagreement", direct, recurrent))
    pooled = pooled_recurrence(atom_count, rules, seed_by_origin)
    pooled_direct = closure(
        atom_count,
        rules,
        set().union(*seed_by_origin) if seed_by_origin else set(),
    )
    if pooled != tuple(atom in pooled_direct for atom in range(atom_count)):
        raise AssertionError("pooled recurrence disagreement")
    parent = pooled_parent_rules(atom_count, rules, seed_by_origin, pooled)
    hybrid = tuple(atom for atom in range(atom_count) if pooled[atom] and not direct[atom])
    certificates = [first_mixing_certificate(atom, direct, pooled, parent) for atom in hybrid]
    return {
        "witnesses": [sorted(origins) for origins in direct],
        "pooled": list(pooled),
        "hybrid_atoms": list(hybrid),
        "certificates": certificates,
    }


def exhaustive_panel() -> dict[str, int]:
    atom_count = 3
    origin_count = 3
    possible_rules: tuple[Rule, ...] = (
        (1, (0,)),
        (2, (0,)),
        (2, (1,)),
        (2, (0, 1)),
    )
    systems = hybrid_atoms = certificates = 0
    for rule_mask in range(1 << len(possible_rules)):
        rules = tuple(
            possible_rules[index]
            for index in range(len(possible_rules))
            if (rule_mask >> index) & 1
        )
        for seed_mask in range(1 << (atom_count * origin_count)):
            seeds = tuple(
                frozenset(
                    atom
                    for atom in range(atom_count)
                    if (seed_mask >> (origin * atom_count + atom)) & 1
                )
                for origin in range(origin_count)
            )
            result = audit(atom_count, rules, seeds)
            systems += 1
            hybrid_atoms += len(result["hybrid_atoms"])
            certificates += len(result["certificates"])
    return {
        "systems": systems,
        "hybrid_atoms": hybrid_atoms,
        "first_mixing_certificates": certificates,
    }


def random_panel() -> dict[str, int]:
    rng = random.Random(SEED)
    system_count = 2000
    hybrid_atoms = certificates = 0
    unary_safe_systems = unary_safe_hybrid_atoms = 0
    for _ in range(system_count):
        atom_count = rng.randint(3, 9)
        origin_count = rng.randint(1, 6)
        rules: set[Rule] = set()
        for head in range(1, atom_count):
            for _ in range(rng.randint(0, 3)):
                size = rng.randint(1, min(3, head))
                body = tuple(sorted(rng.sample(range(head), size)))
                rules.add((head, body))
        seeds = tuple(
            frozenset(atom for atom in range(atom_count) if rng.random() < 0.28)
            for _ in range(origin_count)
        )
        result = audit(atom_count, tuple(sorted(rules)), seeds)
        hybrid_atoms += len(result["hybrid_atoms"])
        certificates += len(result["certificates"])

        unary_rules = tuple(rule for rule in sorted(rules) if len(rule[1]) == 1)
        unary = audit(atom_count, unary_rules, seeds)
        unary_safe_systems += 1
        unary_safe_hybrid_atoms += len(unary["hybrid_atoms"])
        if unary["hybrid_atoms"]:
            raise AssertionError(("unary origin-preserving program produced hybrid", unary))
    return {
        "systems": system_count,
        "hybrid_atoms": hybrid_atoms,
        "first_mixing_certificates": certificates,
        "unary_safe_systems": unary_safe_systems,
        "unary_safe_hybrid_atoms": unary_safe_hybrid_atoms,
    }


def hostile_controls() -> dict[str, Any]:
    # 0=subject, 1=admin scope, 2=authorization.
    rules: tuple[Rule, ...] = ((2, (0, 1)),)
    erased = audit(3, rules, (frozenset({0}), frozenset({1})))
    if erased["hybrid_atoms"] != [2]:
        raise AssertionError(erased)
    certificate = erased["certificates"][0]
    if certificate["premise_witnesses"] != [[0], [1]]:
        raise AssertionError(certificate)

    alternative = audit(
        3,
        rules,
        (frozenset({0}), frozenset({1}), frozenset({0, 1})),
    )
    if alternative["hybrid_atoms"]:
        raise AssertionError(alternative)
    if alternative["witnesses"][2] != [2]:
        raise AssertionError(alternative)

    slot_a = audit(3, rules, (frozenset({0}),))
    slot_b = audit(3, rules, (frozenset({1}),))
    if slot_a["pooled"][2] or slot_b["pooled"][2]:
        raise AssertionError((slot_a, slot_b))

    # A declared bridge-license origin carries the complete premise tuple.
    licensed = audit(3, rules, (frozenset({0, 1}),))
    if licensed["hybrid_atoms"] or licensed["witnesses"][2] != [0]:
        raise AssertionError(licensed)
    return {
        "cross_token_erasure": erased,
        "alternative_complete_origin": alternative,
        "single_slot_a_authorizes": slot_a["pooled"][2],
        "single_slot_b_authorizes": slot_b["pooled"][2],
        "explicit_bridge_license": licensed,
    }


def build_result(script: Path) -> dict[str, Any]:
    exhaustive = exhaustive_panel()
    random_result = random_panel()
    hostile = hostile_controls()
    return {
        "schema": SCHEMA,
        "terminal": TERMINAL,
        "source_base": SOURCE_BASE,
        "verifier_sha256": sha256_file(script),
        "exhaustive_panel": exhaustive,
        "random_panel": random_result,
        "hostile_controls": hostile,
        "controls": {
            "recurrence_matches_independent_origin_closures": True,
            "pooled_recurrence_matches_direct_union_closure": True,
            "every_hybrid_has_first_mixing_certificate": True,
            "unary_origin_preserving_programs_have_no_hybrids": True,
            "cross_token_coordinate_erasure_detected": True,
            "alternative_complete_origin_prevents_false_alarm": True,
            "single_typed_claim_slot_does_not_splice": True,
            "explicit_bridge_license_is_not_mislabeled_splicing": True,
        },
        "authority": {
            "analytic_theorems": "PROVED_IN_ADDENDUM",
            "finite_verification": "IMPLEMENTATION_CORROBORATION_ONLY",
            "agentgateway_whole_system_security": False,
            "deployed_vulnerability": False,
            "external_independence": "CANNOT_CHECK",
            "novelty": "CANNOT_CHECK",
            "grants_journal_authority": False,
        },
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    result = build_result(Path(__file__))
    payload = canonical_json(result) + "\n"
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(payload, encoding="utf-8")
    digest = hashlib.sha256(payload.encode()).hexdigest()
    print(
        TERMINAL,
        f"systems={result['exhaustive_panel']['systems'] + result['random_panel']['systems']}",
        f"hybrids={result['exhaustive_panel']['hybrid_atoms'] + result['random_panel']['hybrid_atoms']}",
        f"sha256={digest}",
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

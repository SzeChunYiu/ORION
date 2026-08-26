#!/usr/bin/env python3
"""Typed evidence-license merge checker and exhaustive finite attack audit.

The general theorem checked by the implementation is:
For any set of license coordinates, the closure of the merged seeds/rules equals
union of coordinate closures iff that union is closed under every merged rule.
"""
from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable, Sequence

SCHEMA = "ORION.TypedAuthorityMergeR8.Results.v1"


def canonical_json(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def sha256(value: Any) -> str:
    return hashlib.sha256(canonical_json(value).encode("utf-8")).hexdigest()


@dataclass(frozen=True)
class Rule:
    body: int
    head: int

    def to_json(self, names: Sequence[str]) -> dict[str, Any]:
        return {
            "body": [names[i] for i in range(len(names)) if (self.body >> i) & 1],
            "head": names[self.head.bit_length() - 1],
        }


def closure(seeds: int, rules: Sequence[Rule]) -> int:
    reached = seeds
    while True:
        nxt = reached
        for rule in rules:
            if (rule.body & reached) == rule.body:
                nxt |= rule.head
        if nxt == reached:
            return reached
        reached = nxt


def is_closed(reached: int, rules: Sequence[Rule]) -> bool:
    return all((rule.body & reached) != rule.body or (rule.head & reached) for rule in rules)


def coordinate_union_closure(coordinates: Sequence[tuple[int, Sequence[Rule]]]) -> int:
    result = 0
    for seeds, rules in coordinates:
        result |= closure(seeds, rules)
    return result


def merged_closure(coordinates: Sequence[tuple[int, Sequence[Rule]]]) -> int:
    seeds = 0
    merged_rules: list[Rule] = []
    seen: set[Rule] = set()
    for coordinate_seeds, coordinate_rules in coordinates:
        seeds |= coordinate_seeds
        for rule in coordinate_rules:
            if rule not in seen:
                merged_rules.append(rule)
                seen.add(rule)
    return closure(seeds, merged_rules)


def merge_report(names: Sequence[str], coordinates: Sequence[tuple[int, Sequence[Rule]]]) -> dict[str, Any]:
    union = coordinate_union_closure(coordinates)
    merged_rules = tuple(dict.fromkeys(rule for _, rules in coordinates for rule in rules))
    merged = closure(0 if not coordinates else _or_all(seeds for seeds, _ in coordinates), merged_rules)
    safe = union == merged
    criterion = is_closed(union, merged_rules)
    assert safe == criterion
    return {
        "coordinate_closures": [
            [names[i] for i in range(len(names)) if (closure(seeds, rules) >> i) & 1]
            for seeds, rules in coordinates
        ],
        "coordinatewise_union": [names[i] for i in range(len(names)) if (union >> i) & 1],
        "merged_closure": [names[i] for i in range(len(names)) if (merged >> i) & 1],
        "spliced_claims": [names[i] for i in range(len(names)) if ((merged & ~union) >> i) & 1],
        "safe_merge": safe,
        "closed_union_criterion": criterion,
    }


def _or_all(values: Iterable[int]) -> int:
    result = 0
    for value in values:
        result |= value
    return result


def bit(names: Sequence[str], name: str) -> int:
    return 1 << names.index(name)


def attack_suite() -> list[dict[str, Any]]:
    names = ("a", "b", "c", "target")
    cases: list[tuple[str, Sequence[tuple[int, Sequence[Rule]]], bool]] = []

    # A coordinate owns a seed, another owns a rule that can consume it.
    cases.append(
        (
            "SEED_RULE_SPLICE",
            (
                (bit(names, "a"), ()),
                (0, (Rule(bit(names, "a"), bit(names, "target")),)),
            ),
            False,
        )
    )

    # Two coordinates separately supply the two premises of a conjunctive rule.
    cases.append(
        (
            "CONJUNCTIVE_PREMISE_SPLICE",
            (
                (bit(names, "a"), (Rule(bit(names, "a") | bit(names, "b"), bit(names, "target")),)),
                (bit(names, "b"), ()),
            ),
            False,
        )
    )

    # A seed and alternating rule fragments form a recursive bridge only after merge.
    cases.append(
        (
            "RECURSIVE_BRIDGE_SPLICE",
            (
                (
                    bit(names, "a"),
                    (
                        Rule(bit(names, "c"), bit(names, "b")),
                        Rule(bit(names, "b"), bit(names, "target")),
                    ),
                ),
                (0, (Rule(bit(names, "a"), bit(names, "c")),)),
            ),
            False,
        )
    )

    # Dominance: weaker coordinate is syntactically contained in stronger coordinate.
    cases.append(
        (
            "DOMINANCE_SAFE_CONTROL",
            (
                (bit(names, "a"), (Rule(bit(names, "a"), bit(names, "b")),)),
                (
                    bit(names, "a") | bit(names, "c"),
                    (
                        Rule(bit(names, "a"), bit(names, "b")),
                        Rule(bit(names, "b") | bit(names, "c"), bit(names, "target")),
                    ),
                ),
            ),
            True,
        )
    )

    # Disconnected claim/rule supports are safe.
    cases.append(
        (
            "DISCONNECTED_SAFE_CONTROL",
            (
                (bit(names, "a"), (Rule(bit(names, "a"), bit(names, "b")),)),
                (bit(names, "c"), (Rule(bit(names, "c"), bit(names, "target")),)),
            ),
            True,
        )
    )

    output = []
    for case_id, coordinates, expected_safe in cases:
        report = merge_report(names, coordinates)
        assert report["safe_merge"] is expected_safe
        output.append({"case_id": case_id, "expected_safe": expected_safe, **report})
    return output


def exhaustive_three_claim_audit() -> dict[str, Any]:
    claim_count = 3
    all_claims = (1 << claim_count) - 1
    rules: list[Rule] = []
    for source in range(claim_count):
        for target in range(claim_count):
            if source != target:
                rules.append(Rule(1 << source, 1 << target))
    for head in range(claim_count):
        body = all_claims & ~(1 << head)
        rules.append(Rule(body, 1 << head))
    assert len(rules) == 9

    rule_subset_count = 1 << len(rules)
    signature_count = (1 << claim_count) * rule_subset_count

    subset_rules: list[tuple[Rule, ...]] = []
    for mask in range(rule_subset_count):
        subset_rules.append(tuple(rule for i, rule in enumerate(rules) if (mask >> i) & 1))

    closures = [0] * signature_count
    for seeds in range(1 << claim_count):
        for rule_mask in range(rule_subset_count):
            index = seeds * rule_subset_count + rule_mask
            closures[index] = closure(seeds, subset_rules[rule_mask])

    unsafe = 0
    safe = 0
    theorem_mismatches = 0
    maximum_splice = 0
    for seeds_a in range(1 << claim_count):
        base_a = seeds_a * rule_subset_count
        for rules_a in range(rule_subset_count):
            closure_a = closures[base_a + rules_a]
            for seeds_b in range(1 << claim_count):
                merged_seeds = seeds_a | seeds_b
                base_b = seeds_b * rule_subset_count
                merged_base = merged_seeds * rule_subset_count
                for rules_b in range(rule_subset_count):
                    closure_b = closures[base_b + rules_b]
                    union = closure_a | closure_b
                    merged_rules_mask = rules_a | rules_b
                    merged = closures[merged_base + merged_rules_mask]
                    criterion = is_closed(union, subset_rules[merged_rules_mask])
                    equality = merged == union
                    if criterion != equality:
                        theorem_mismatches += 1
                    if equality:
                        safe += 1
                    else:
                        unsafe += 1
                        maximum_splice = max(maximum_splice, (merged & ~union).bit_count())

    pair_count = signature_count * signature_count
    assert safe + unsafe == pair_count
    assert theorem_mismatches == 0
    return {
        "claim_count": claim_count,
        "rule_pool": {
            "unary_rules": 6,
            "binary_conjunctive_rules": 3,
            "total_rules": len(rules),
        },
        "coordinate_signature_count": signature_count,
        "ordered_coordinate_pair_count": pair_count,
        "safe_pair_count": safe,
        "unsafe_pair_count": unsafe,
        "maximum_new_claims_from_splicing": maximum_splice,
        "safe_merge_iff_closed_union_mismatches": theorem_mismatches,
        "status": "FINITE_EXACT",
    }


def main() -> None:
    result = {
        "schema": SCHEMA,
        "authority": {
            "general_theorem_authority": "DISPLAYED_PROOF_REQUIRED",
            "finite_attack_audit": True,
            "real_policy_validation": False,
            "grants_scientific_authority": False,
        },
        "attack_suite": attack_suite(),
        "exhaustive_audit": exhaustive_three_claim_audit(),
    }
    result["content_sha256"] = sha256(result)
    output = Path(__file__).with_name("TYPED_AUTHORITY_MERGE_R8_RESULTS.json")
    output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()

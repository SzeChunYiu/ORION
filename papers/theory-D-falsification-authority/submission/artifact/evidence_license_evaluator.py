#!/usr/bin/env python3
"""Deterministic evaluator for finite typed evidence-license rule graphs."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any, Dict, Iterable, List, Mapping, MutableMapping, Set, Tuple


class ValidationError(ValueError):
    """Raised when a rule-graph document violates the public schema contract."""


def _unique_strings(values: Any, field: str, *, allow_empty: bool = False) -> List[str]:
    if not isinstance(values, list) or not all(isinstance(item, str) and item for item in values):
        raise ValidationError(f"{field} must be a list of nonempty strings")
    if not allow_empty and not values:
        raise ValidationError(f"{field} must not be empty")
    if len(values) != len(set(values)):
        raise ValidationError(f"{field} must not contain duplicates")
    return list(values)


def validate_document(document: Mapping[str, Any]) -> Dict[str, Any]:
    """Validate and normalize one evidence-license system."""

    if not isinstance(document, Mapping):
        raise ValidationError("document must be an object")

    allowed_top = {"version", "licenses", "claims", "rules", "refutations"}
    extra_top = set(document) - allowed_top
    if extra_top:
        raise ValidationError(f"unknown top-level fields: {sorted(extra_top)}")
    missing_top = allowed_top - set(document)
    if missing_top:
        raise ValidationError(f"missing required top-level fields: {sorted(missing_top)}")
    if document.get("version") != "1.0":
        raise ValidationError("version must be '1.0'")

    licenses = _unique_strings(document.get("licenses"), "licenses")
    license_set = set(licenses)

    raw_claims = document.get("claims")
    if not isinstance(raw_claims, list) or not raw_claims:
        raise ValidationError("claims must be a nonempty list")

    claims: Dict[str, List[str]] = {}
    for index, claim in enumerate(raw_claims):
        if not isinstance(claim, Mapping) or set(claim) != {"id", "seeds"}:
            raise ValidationError(f"claims[{index}] must contain exactly id and seeds")
        claim_id = claim.get("id")
        if not isinstance(claim_id, str) or not claim_id:
            raise ValidationError(f"claims[{index}].id must be a nonempty string")
        if claim_id in claims:
            raise ValidationError(f"duplicate claim id: {claim_id}")
        seeds = _unique_strings(claim.get("seeds"), f"claims[{index}].seeds", allow_empty=True)
        unknown = set(seeds) - license_set
        if unknown:
            raise ValidationError(f"claim {claim_id} uses unknown licenses: {sorted(unknown)}")
        claims[claim_id] = sorted(seeds)

    claim_set = set(claims)
    raw_rules = document.get("rules")
    if not isinstance(raw_rules, list):
        raise ValidationError("rules must be a list")

    rules: List[Dict[str, Any]] = []
    rule_ids: Set[str] = set()
    for index, rule in enumerate(raw_rules):
        if not isinstance(rule, Mapping) or set(rule) != {"id", "body", "head", "cap"}:
            raise ValidationError(f"rules[{index}] must contain exactly id, body, head, and cap")
        rule_id = rule.get("id")
        if not isinstance(rule_id, str) or not rule_id:
            raise ValidationError(f"rules[{index}].id must be a nonempty string")
        if rule_id in rule_ids:
            raise ValidationError(f"duplicate rule id: {rule_id}")
        rule_ids.add(rule_id)

        body = _unique_strings(rule.get("body"), f"rules[{index}].body")
        head = rule.get("head")
        if not isinstance(head, str) or head not in claim_set:
            raise ValidationError(f"rule {rule_id} has unknown head: {head!r}")
        unknown_claims = set(body) - claim_set
        if unknown_claims:
            raise ValidationError(f"rule {rule_id} uses unknown claims: {sorted(unknown_claims)}")
        cap = _unique_strings(rule.get("cap"), f"rules[{index}].cap", allow_empty=True)
        unknown_licenses = set(cap) - license_set
        if unknown_licenses:
            raise ValidationError(
                f"rule {rule_id} uses unknown licenses: {sorted(unknown_licenses)}"
            )
        rules.append({"id": rule_id, "body": sorted(body), "head": head, "cap": sorted(cap)})

    refutations = _unique_strings(document.get("refutations"), "refutations", allow_empty=True)
    unknown_refutations = set(refutations) - claim_set
    if unknown_refutations:
        raise ValidationError(f"unknown refuted claims: {sorted(unknown_refutations)}")

    return {
        "version": "1.0",
        "licenses": sorted(licenses),
        "claims": [{"id": key, "seeds": claims[key]} for key in sorted(claims)],
        "rules": sorted(rules, key=lambda item: item["id"]),
        "refutations": sorted(refutations),
    }


def _labels_from_document(document: Mapping[str, Any]) -> Dict[str, Set[str]]:
    return {claim["id"]: set() for claim in document["claims"]}


def least_fixed_point(
    document: Mapping[str, Any], refutations: Iterable[str]
) -> Tuple[Dict[str, Set[str]], int]:
    """Evaluate the synchronous least fixed point for a validated document."""

    refuted = set(refutations)
    seeds = {claim["id"]: set(claim["seeds"]) for claim in document["claims"]}
    labels = _labels_from_document(document)
    max_rounds = len(document["claims"]) * len(document["licenses"]) + 1

    for round_index in range(1, max_rounds + 1):
        next_labels: Dict[str, Set[str]] = {}
        for claim_id in labels:
            if claim_id in refuted:
                next_labels[claim_id] = set()
                continue
            value = set(seeds[claim_id])
            for rule in document["rules"]:
                if rule["head"] != claim_id:
                    continue
                transfer = set(rule["cap"])
                for premise in rule["body"]:
                    transfer.intersection_update(labels[premise])
                value.update(transfer)
            next_labels[claim_id] = value

        if next_labels == labels:
            return labels, round_index
        labels = next_labels

    raise RuntimeError("least-fixed-point iteration exceeded the finite lattice bound")


def _canonical_labels(labels: Mapping[str, Set[str]]) -> Dict[str, List[str]]:
    return {claim: sorted(labels[claim]) for claim in sorted(labels)}


def evaluate_document(document: Mapping[str, Any]) -> Dict[str, Any]:
    """Validate, evaluate, and return a canonical semantic result."""

    normalized = validate_document(document)
    baseline, baseline_iterations = least_fixed_point(normalized, [])
    final, final_iterations = least_fixed_point(normalized, normalized["refutations"])
    retracted = [
        {"claim": claim, "license": license_name}
        for claim in sorted(baseline)
        for license_name in sorted(baseline[claim] - final[claim])
    ]
    return {
        "version": normalized["version"],
        "baseline_labels": _canonical_labels(baseline),
        "final_labels": _canonical_labels(final),
        "refutations": normalized["refutations"],
        "retracted": retracted,
        "iterations": {
            "baseline": baseline_iterations,
            "final": final_iterations,
        },
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input", type=Path, help="JSON evidence-license system")
    parser.add_argument("--output", type=Path, help="optional output JSON path")
    args = parser.parse_args()

    with args.input.open("r", encoding="utf-8") as handle:
        document = json.load(handle)
    output = json.dumps(evaluate_document(document), indent=2, sort_keys=True) + "\n"
    if args.output:
        args.output.write_text(output, encoding="utf-8")
    else:
        print(output, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

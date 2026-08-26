#!/usr/bin/env python3
"""Deterministic typed-vs-untyped OAuth evidence-merge benchmark for Paper D R9."""
from __future__ import annotations

import hashlib
import json
from collections import defaultdict
from pathlib import Path
from typing import Any, Iterable

SCHEMA = "ORION.TypedAuthority.OAuthTokenSplicingR9.Results.v1"
CORE = frozenset({"typ_at_jwt", "signature_valid", "issuer_trusted", "not_expired"})
ENTITLEMENT = frozenset({"aud_rs1", "subject_alice", "scope_admin"})
DPOP = frozenset(
    {
        "dpop_token_bound",
        "dpop_proof_signature_valid",
        "dpop_key_matches",
        "dpop_ath_matches",
        "dpop_method_matches",
        "dpop_uri_matches",
    }
)
BEARER_RULES = (
    ("JWT_CORE_VALID", CORE, "jwt_core_valid"),
    ("RS1_ADMIN_ALICE_ENTITLEMENT", ENTITLEMENT, "rs1_admin_alice_entitlement"),
    (
        "BEARER_AUTHORIZE_RS1_ADMIN_ALICE",
        frozenset({"jwt_core_valid", "rs1_admin_alice_entitlement"}),
        "authorize_rs1_admin_alice",
    ),
)
DPOP_RULES = BEARER_RULES + (
    ("DPOP_CONTEXT_VALID", DPOP, "dpop_context_valid"),
    (
        "DPOP_AUTHORIZE_RS1_ADMIN_ALICE",
        frozenset({"jwt_core_valid", "rs1_admin_alice_entitlement", "dpop_context_valid"}),
        "authorize_rs1_admin_alice_dpop",
    ),
)


def canonical_json(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def digest(value: Any) -> str:
    return hashlib.sha256(canonical_json(value).encode("utf-8")).hexdigest()


def required(mode: str) -> frozenset[str]:
    return CORE | ENTITLEMENT | (DPOP if mode == "dpop" else frozenset())


def rules_and_target(mode: str):
    if mode == "dpop":
        return DPOP_RULES, "authorize_rs1_admin_alice_dpop"
    assert mode == "bearer"
    return BEARER_RULES, "authorize_rs1_admin_alice"


def closure(seed: Iterable[str], rules) -> tuple[set[str], list[str]]:
    reached = set(seed)
    trace: list[str] = []
    changed = True
    while changed:
        changed = False
        for rule_id, body, head in rules:
            if head not in reached and body.issubset(reached):
                reached.add(head)
                trace.append(rule_id)
                changed = True
    return reached, trace


def surviving_by_coordinate(case: dict[str, Any]) -> dict[str, set[str]]:
    refuted = {(row["coordinate"], row["fact"]) for row in case.get("refutations", [])}
    facts: dict[str, set[str]] = defaultdict(set)
    for record in case["records"]:
        coordinate = record["coordinate"]
        facts[coordinate].update(
            fact for fact in record["facts"] if (coordinate, fact) not in refuted
        )
    return dict(facts)


def fact_sources(case: dict[str, Any]) -> dict[str, list[dict[str, str]]]:
    refuted = {(row["coordinate"], row["fact"]) for row in case.get("refutations", [])}
    sources: dict[str, list[dict[str, str]]] = defaultdict(list)
    for record in case["records"]:
        for fact in record["facts"]:
            if (record["coordinate"], fact) not in refuted:
                sources[fact].append(
                    {"record_id": record["record_id"], "coordinate": record["coordinate"]}
                )
    return dict(sources)


def direct_authorized(facts: set[str], mode: str) -> bool:
    return required(mode).issubset(facts)


def evaluate(case: dict[str, Any]) -> dict[str, Any]:
    mode = case["mode"]
    rules, target = rules_and_target(mode)
    by_coordinate = surviving_by_coordinate(case)
    typed_authorized: list[str] = []
    typed_traces: dict[str, list[str]] = {}
    for coordinate, facts in sorted(by_coordinate.items()):
        reached, trace = closure(facts, rules)
        assert (target in reached) == direct_authorized(facts, mode)
        typed_traces[coordinate] = trace
        if target in reached:
            typed_authorized.append(coordinate)

    projected = set().union(*by_coordinate.values()) if by_coordinate else set()
    untyped_reached, untyped_trace = closure(projected, rules)
    assert (target in untyped_reached) == direct_authorized(projected, mode)
    expected = bool(case["expected_authorized"])
    sources = fact_sources(case)
    return {
        "case_id": case["case_id"],
        "mode": mode,
        "expected_authorized": expected,
        "expected_reason": case["expected_reason"],
        "typed_authorized": bool(typed_authorized),
        "typed_authorized_coordinates": typed_authorized,
        "typed_rule_trace_by_coordinate": typed_traces,
        "typed_missing_requirements_by_coordinate": {
            coordinate: sorted(required(mode) - facts)
            for coordinate, facts in sorted(by_coordinate.items())
            if not direct_authorized(facts, mode)
        },
        "untyped_authorized": target in untyped_reached,
        "untyped_false_positive": target in untyped_reached and not expected,
        "untyped_rule_trace": untyped_trace,
        "untyped_required_fact_source_coordinates": {
            fact: sorted({row["coordinate"] for row in sources.get(fact, [])})
            for fact in sorted(required(mode))
        },
        "independent_formula_agreement": True,
    }


def main() -> None:
    root = Path(__file__).parent
    corpus_path = root / "OAUTH_TOKEN_SPLICE_CORPUS_R9.json"
    source_path = root / "OAUTH_POLICY_SOURCE_REGISTRY_R9.json"
    corpus = json.loads(corpus_path.read_text(encoding="utf-8"))
    source_registry = json.loads(source_path.read_text(encoding="utf-8"))
    assert corpus["schema"] == "ORION.TypedAuthority.OAuthTokenSpliceCorpusR9.v1"
    assert source_registry["schema"] == "ORION.TypedAuthority.OAuthPolicySourceRegistryR9.v1"
    source_ids = sorted(row["source_id"] for row in source_registry["sources"])
    assert source_ids == ["RFC8707", "RFC9068", "RFC9449", "RFC9700"]

    rows = [evaluate(case) for case in corpus["cases"]]
    for case, row in zip(corpus["cases"], rows, strict=True):
        assert row["typed_authorized"] == bool(case["expected_authorized"])

    false_positive_ids = [row["case_id"] for row in rows if row["untyped_false_positive"]]
    summary = {
        "case_count": len(rows),
        "typed_expected_agreement": sum(
            row["typed_authorized"] == row["expected_authorized"] for row in rows
        ),
        "untyped_expected_agreement": sum(
            row["untyped_authorized"] == row["expected_authorized"] for row in rows
        ),
        "typed_false_positive_count": sum(
            row["typed_authorized"] and not row["expected_authorized"] for row in rows
        ),
        "typed_false_negative_count": sum(
            not row["typed_authorized"] and row["expected_authorized"] for row in rows
        ),
        "untyped_false_positive_count": len(false_positive_ids),
        "untyped_false_positive_case_ids": false_positive_ids,
        "independent_formula_agreement_count": sum(
            row["independent_formula_agreement"] for row in rows
        ),
    }
    result: dict[str, Any] = {
        "schema": SCHEMA,
        "domain": "RFC_8707_9068_9449_9700_OAUTH_TOKEN_EVIDENCE_MERGE",
        "model": {
            "query": "authorize Alice for the RS1 admin action",
            "typed": "positive Horn closure evaluated independently per content-bound token/request coordinate",
            "untyped_baseline": "project coordinates away, union surviving facts, then run the same Horn rules",
        },
        "inputs": {
            "corpus_sha256": hashlib.sha256(corpus_path.read_bytes()).hexdigest(),
            "source_registry_sha256": hashlib.sha256(source_path.read_bytes()).hexdigest(),
            "registered_source_ids": source_ids,
        },
        "cases": rows,
        "summary": summary,
        "controls": {
            "clean_bearer_authorized": next(
                row for row in rows if row["case_id"] == "CLEAN_BEARER_ADMIN"
            )["typed_authorized"],
            "same_token_fragmentation_authorized": next(
                row for row in rows if row["case_id"] == "SAME_TOKEN_FRAGMENTATION_ALLOWED"
            )["typed_authorized"],
            "read_only_denied": not next(
                row for row in rows if row["case_id"] == "READ_ONLY_TOKEN"
            )["typed_authorized"],
            "clean_dpop_authorized": next(
                row for row in rows if row["case_id"] == "CLEAN_DPOP_ADMIN"
            )["typed_authorized"],
            "all_registered_splices_blocked": all(
                not row["typed_authorized"]
                for row in rows
                if "SPLICE" in row["case_id"] or "LAUNDERING" in row["case_id"]
            ),
        },
        "authority": {
            "official_rfc_grounded_protocol_fixture": True,
            "real_implementation_vulnerability_measurement": False,
            "independent_oauth_domain_review": False,
            "independent_encoding_replay": False,
            "general_prevalence": False,
            "legal_or_compliance_determination": False,
            "grants_journal_authority": False,
        },
        "terminal": "D_RFC_GROUNDED_TOKEN_SPLICE_CORPUS__TYPED_BLOCKS_ALL_REGISTERED_UNTYPED_FALSE_POSITIVES",
    }
    result["content_sha256"] = digest(result)
    output = root / "OAUTH_TOKEN_SPLICE_R9_RESULTS.json"
    output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()

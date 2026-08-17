"""P3.coordinate-obstruction.v2 protocol freeze: families, schema, fixtures.

V2 gold is ``CANNOT_CHECK`` until pinned expert/public annotations or
deterministic standards are bound. LLM/proxy labels cannot become gold.
The V1 confirmatory result is immutable and is not pooled into V2.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Mapping, Sequence

from orion.study.p3_confirmatory_receipt import PAPER03, REPO_ROOT
from orion.study.p3_public_reference import canonical_json, sha256_json

PROTOCOL_ID = "P3.coordinate-obstruction.v2"
SCHEMA_VERSION = "orion.p3.coordinate-obstruction-protocol.v2"
CASE_SCHEMA_VERSION = "orion.p3.coordinate-obstruction-case.v2"
GOLD_STATUS = "CANNOT_CHECK"

PROTOCOL_PATH = PAPER03 / "protocol" / "P3_COORDINATE_OBSTRUCTION_V2.json"
CASE_SCHEMA_PATH = PAPER03 / "protocol" / "P3_COORDINATE_OBSTRUCTION_CASE_SCHEMA_V2.json"
FIXTURE_PATH = (
    PAPER03 / "gold" / "adjudicated" / "coordinate-obstruction-v2" / "FAMILY_FIXTURES_V2.jsonl"
)
GOLD_STATUS_PATH = (
    PAPER03 / "gold" / "adjudicated" / "coordinate-obstruction-v2" / "GOLD_STATUS.json"
)

FAMILIES: tuple[str, ...] = (
    "REFERENT_IDENTITY",
    "CONSTRUCT_IDENTITY",
    "MEASUREMENT_OPERATIONALIZATION",
    "TEMPORAL_STATE_CONTEXT",
    "MODALITY_POLARITY_ATTRIBUTION",
    "REPRESENTATION_TRANSFORM",
    "PLURALISM_OBSTRUCTION",
    "UNRESOLVED",
)

INTEGRATION_TERMINALS = ("GLUE", "OBSTRUCTION", "UNRESOLVED")
FORBIDDEN_GOLD = ("LLM_PROPOSAL", "HEURISTIC_PROXY", "SIMULATED", "SELF_LABEL")
ALLOWED_GOLD = (
    "UPSTREAM_EXPERT",
    "UPSTREAM_HUMAN",
    "DETERMINISTIC_STANDARD",
    "DERIVED_FROM_ALLOWED",
)

# Minimal pair/triple *designs* per family. These are schema fixtures, not gold.
# V1 confirmatory pointers are exemplars of related structure, not V2 labels.
FAMILY_DESIGNS: tuple[dict[str, object], ...] = (
    {
        "family": "REFERENT_IDENTITY",
        "pair_kind": "same_label_different_entity",
        "varied_coordinate": "referent",
        "held_constant": [
            "construct",
            "measurement",
            "temporal",
            "modality",
            "polarity",
            "attribution",
            "representation",
        ],
        "v1_confirmatory_exemplars": [],
        "cannot_check_reason": (
            "no pinned expert annotation of same-label/different-entity on the V2 protocol"
        ),
    },
    {
        "family": "REFERENT_IDENTITY",
        "pair_kind": "different_label_same_entity",
        "varied_coordinate": "surface_form",
        "held_constant": ["referent", "construct", "measurement", "temporal"],
        "v1_confirmatory_exemplars": ["muse-240507114635088FIIGCD-R2-0"],
        "cannot_check_reason": (
            "V1 confirmatory MUSE coreference is MeaningRelation=COMPATIBLE, not independently "
            "adjudicated V2 GLUE/OBSTRUCTION gold"
        ),
    },
    {
        "family": "REFERENT_IDENTITY",
        "pair_kind": "identity_ambiguity",
        "varied_coordinate": "referent",
        "held_constant": ["construct", "measurement"],
        "v1_confirmatory_exemplars": [],
        "cannot_check_reason": "identity-ambiguity cases require frozen independent annotation",
    },
    {
        "family": "CONSTRUCT_IDENTITY",
        "pair_kind": "same_measurement_label_different_construct",
        "varied_coordinate": "construct",
        "held_constant": ["referent", "measurement_label", "temporal"],
        "v1_confirmatory_exemplars": [],
        "cannot_check_reason": (
            "confirmatory ablations did not identify construct necessity; no targeted expert gold"
        ),
    },
    {
        "family": "CONSTRUCT_IDENTITY",
        "pair_kind": "same_construct_different_discipline_naming",
        "varied_coordinate": "surface_form",
        "held_constant": ["construct", "referent"],
        "v1_confirmatory_exemplars": [],
        "cannot_check_reason": "cross-discipline construct naming needs specialist gold",
    },
    {
        "family": "MEASUREMENT_OPERATIONALIZATION",
        "pair_kind": "same_construct_incompatible_operationalization",
        "varied_coordinate": "measurement",
        "held_constant": ["referent", "construct"],
        "v1_confirmatory_exemplars": [],
        "cannot_check_reason": "no pinned incompatible-operationalization expert gold for V2",
    },
    {
        "family": "MEASUREMENT_OPERATIONALIZATION",
        "pair_kind": "valid_versus_invalid_unit_scale_transform",
        "varied_coordinate": "measurement",
        "held_constant": ["referent", "construct"],
        "v1_confirmatory_exemplars": [],
        "cannot_check_reason": (
            "SI/UCUM deterministic standards are not yet content-hashed into this freeze"
        ),
    },
    {
        "family": "MEASUREMENT_OPERATIONALIZATION",
        "pair_kind": "proxy_versus_direct",
        "varied_coordinate": "measurement",
        "held_constant": ["referent", "construct"],
        "v1_confirmatory_exemplars": [],
        "cannot_check_reason": "proxy-versus-direct operationalization needs specialist gold",
    },
    {
        "family": "TEMPORAL_STATE_CONTEXT",
        "pair_kind": "same_entity_across_intervention_state_phase_epoch",
        "varied_coordinate": "temporal",
        "held_constant": ["referent", "construct", "measurement"],
        "v1_confirmatory_exemplars": [],
        "cannot_check_reason": "no pinned temporal-state expert gold bound for V2",
    },
    {
        "family": "MODALITY_POLARITY_ATTRIBUTION",
        "pair_kind": "observed_versus_hypothesized",
        "varied_coordinate": "modality",
        "held_constant": ["referent", "construct", "measurement"],
        "v1_confirmatory_exemplars": [],
        "cannot_check_reason": "observed-vs-hypothesized pairs are not independently adjudicated for V2",
    },
    {
        "family": "MODALITY_POLARITY_ATTRIBUTION",
        "pair_kind": "support_versus_contradiction",
        "varied_coordinate": "polarity",
        "held_constant": ["referent", "construct"],
        "v1_confirmatory_exemplars": ["scifact-32-12428497-0"],
        "cannot_check_reason": (
            "V1 SciFact SUPPORT/CONTRADICT is MeaningRelation gold, not V2 obstruction-certificate gold"
        ),
    },
    {
        "family": "MODALITY_POLARITY_ATTRIBUTION",
        "pair_kind": "author_versus_cited_claim",
        "varied_coordinate": "attribution",
        "held_constant": ["referent", "construct", "polarity"],
        "v1_confirmatory_exemplars": [],
        "cannot_check_reason": "author-versus-cited attribution needs discourse-level expert gold",
    },
    {
        "family": "MODALITY_POLARITY_ATTRIBUTION",
        "pair_kind": "negation_scope",
        "varied_coordinate": "polarity",
        "held_constant": ["referent", "construct"],
        "v1_confirmatory_exemplars": [],
        "cannot_check_reason": "negation/scope cases need specialist gold",
    },
    {
        "family": "REPRESENTATION_TRANSFORM",
        "pair_kind": "invertible_valid_map",
        "varied_coordinate": "representation",
        "held_constant": ["referent", "construct", "measurement"],
        "v1_confirmatory_exemplars": ["scischema-a93fcc4e06fe62c8"],
        "cannot_check_reason": (
            "V1 SciSchema cases are COMPATIBLE schema-identity maps, not V2 transform gold"
        ),
    },
    {
        "family": "REPRESENTATION_TRANSFORM",
        "pair_kind": "lossy_but_bounded",
        "varied_coordinate": "representation",
        "held_constant": ["referent", "construct"],
        "v1_confirmatory_exemplars": [],
        "cannot_check_reason": "lossy-but-bounded transforms need preservation-condition expert gold",
    },
    {
        "family": "REPRESENTATION_TRANSFORM",
        "pair_kind": "invalid_lexical_similarity_map",
        "varied_coordinate": "representation",
        "held_constant": ["referent"],
        "v1_confirmatory_exemplars": [],
        "cannot_check_reason": "invalid lexical-similarity maps are not yet expert-bound for V2",
    },
    {
        "family": "PLURALISM_OBSTRUCTION",
        "pair_kind": "coherent_incompatible_views_must_coexist",
        "varied_coordinate": "pluralism",
        "held_constant": ["referent"],
        "v1_confirmatory_exemplars": [],
        "cannot_check_reason": "scientific pluralism cases require frozen independent annotation",
    },
    {
        "family": "UNRESOLVED",
        "pair_kind": "evidence_genuinely_insufficient",
        "varied_coordinate": "evidence",
        "held_constant": [],
        "v1_confirmatory_exemplars": [],
        "cannot_check_reason": "UNRESOLVED V2 gold cannot be manufactured; evidence is not yet bound",
    },
)


class ProtocolFreezeError(ValueError):
    """V2 protocol or fixture is not admissible."""


def fixtures() -> list[dict[str, object]]:
    records: list[dict[str, object]] = []
    for index, design in enumerate(FAMILY_DESIGNS, start=1):
        family = str(design["family"])
        pair_kind = str(design["pair_kind"])
        records.append(
            {
                "schema_version": CASE_SCHEMA_VERSION,
                "fixture_id": f"P3.CO.V2.{family}.{index:02d}.{pair_kind}",
                "family": family,
                "pair_kind": pair_kind,
                "arity": "triple" if family == "PLURALISM_OBSTRUCTION" else "pair",
                "varied_coordinate": design["varied_coordinate"],
                "held_constant": list(design["held_constant"]),  # type: ignore[arg-type]
                "expected_integration": None,
                "gold_status": GOLD_STATUS,
                "gold_authority": None,
                "cannot_check_reason": design["cannot_check_reason"],
                "v1_confirmatory_exemplars": list(design["v1_confirmatory_exemplars"]),  # type: ignore[arg-type]
                "llm_gold_forbidden": True,
            }
        )
    return records


def validate_fixture(record: Mapping[str, object]) -> dict[str, object]:
    required = {
        "schema_version",
        "fixture_id",
        "family",
        "pair_kind",
        "gold_status",
        "expected_integration",
        "llm_gold_forbidden",
    }
    missing = sorted(required - set(record))
    if missing:
        raise ProtocolFreezeError(f"fixture missing keys: {', '.join(missing)}")
    if record["schema_version"] != CASE_SCHEMA_VERSION:
        raise ProtocolFreezeError("unsupported fixture schema_version")
    if record["family"] not in FAMILIES:
        raise ProtocolFreezeError(f"unknown family: {record['family']}")
    if record["gold_status"] != GOLD_STATUS:
        raise ProtocolFreezeError("V2 gold_status must remain CANNOT_CHECK until expert gold is bound")
    if record["expected_integration"] is not None:
        raise ProtocolFreezeError("V2 fixtures must not carry expected_integration without expert gold")
    authority = record.get("gold_authority")
    if authority is not None:
        kind = ""
        if isinstance(authority, dict):
            kind = str(authority.get("kind", ""))
        if kind in FORBIDDEN_GOLD:
            raise ProtocolFreezeError(f"forbidden gold authority: {kind}")
        raise ProtocolFreezeError("V2 gold_authority must be null while gold_status is CANNOT_CHECK")
    if record.get("llm_gold_forbidden") is not True:
        raise ProtocolFreezeError("llm_gold_forbidden must be true")
    return dict(record)


def protocol_document() -> dict[str, object]:
    return {
        "schema_version": SCHEMA_VERSION,
        "paper_id": "P3",
        "protocol_id": PROTOCOL_ID,
        "protocol_status": "DESIGN_FROZEN",
        "outcome_accessed": False,
        "gold_status": GOLD_STATUS,
        "v1_confirmatory_immutable": True,
        "v1_protocol_mutated": False,
        "novelty_nonclaims": [
            "generic schema induction",
            "ontology fusion",
            "provenance knowledge graphs as such",
            "structured scientific knowledge construction as such",
            "standalone scientific obstruction without provenance-bound certificates",
        ],
        "novelty_target": (
            "provenance-bound scientific obstruction / non-merge certificates that explain "
            "why two source-local representations must not be globally identified"
        ),
        "primary_hypothesis": {
            "id": "P3.CO.V2.H1",
            "text": (
                "On a coordinate-targeted atlas with pinned expert or deterministic gold, "
                "obstruction certificates reduce false merge/false contradiction relative to "
                "flat canonicalization and exact conservative abstention while preserving valid "
                "integrations. Hypothesis is unbound until V2 gold exists."
            ),
            "status": GOLD_STATUS,
        },
        "required_families": list(FAMILIES),
        "integration_terminals": list(INTEGRATION_TERMINALS),
        "gold_authority": {
            "allowed": list(ALLOWED_GOLD),
            "forbidden": list(FORBIDDEN_GOLD),
            "rule": "LLM/proxy labels cannot become gold. Missing authority is CANNOT_CHECK.",
        },
        "literature_saturation": {
            "status": "SEED_ONLY_NOT_CLOSED",
            "rule": (
                "Stop after two consecutive primary-source + related-work rounds yield no "
                "mechanism-changing coordinate, mapping, obstruction, provenance, or baseline change."
            ),
            "seed_dispositions": [
                {
                    "work": "MUSE arXiv:2608.10974",
                    "disposition": "ADAPT",
                    "role": "upstream expert coreference source; not a mapping calculus",
                },
                {
                    "work": "SCOPE/SCION arXiv:2607.21610",
                    "disposition": "DEFER",
                    "role": "stronger conservative schema-fusion baseline; not implemented; not novelty",
                },
                {
                    "work": "SciSchema.org arXiv:2607.27955",
                    "disposition": "ADAPT",
                    "role": "deterministic schema-identity source; not ontology-fusion novelty",
                },
                {
                    "work": "Executable Schema Contracts arXiv:2606.05415",
                    "disposition": "DEFER",
                    "role": "provenance-aware integration baseline stub; not novelty",
                },
                {
                    "work": "Provenance-Enhanced Statements arXiv:2606.15246",
                    "disposition": "DEFER",
                    "role": "attributed-statement baseline stub; not novelty",
                },
                {
                    "work": "generic ontology alignment / schema matching",
                    "disposition": "REJECT",
                    "role": "explicitly out of novelty scope",
                },
            ],
        },
        "baselines": {
            "secondary_on_frozen_v1": [
                "exact_coordinate_conservative",
                "flat_predicate_canonicalization",
            ],
            "v2_unbound_until_faithful": [
                "scion_like_conservative_schema_fusion",
                "executable_schema_contracts_like",
                "provenance_world_attributed_statements",
                "strongest_ontology_schema_alignment_from_saturation",
            ],
            "rule": "post-outcome baselines remain secondary and cannot rewrite confirmatory PASS",
        },
        "ablations_planned": [
            "remove_each_coordinate",
            "remove_obstruction_force_best_map",
            "remove_provenance_preservation",
            "pairwise_only_without_cycle_roundtrip",
            "no_source_recoverability",
        ],
        "execution_bindings": {
            "subject_revision": "UNBOUND",
            "v2_gold_hash": "UNBOUND",
            "evaluator_hash": "UNBOUND",
            "evaluation_epoch": "UNBOUND",
        },
        "terminal_rule": (
            "Green tests or a pretty atlas alone never close issue #280. "
            "BROADER_THEORY_SUPPORTED requires targeted coordinate necessity plus certificate "
            "value under strong baselines. Otherwise NARROW_THEORY_CONFIRMED, "
            "POSITIVE_INVALIDATED, or CANNOT_CHECK."
        ),
    }


def gold_status_document(records: Sequence[Mapping[str, object]]) -> dict[str, object]:
    by_family = {family: 0 for family in FAMILIES}
    for record in records:
        by_family[str(record["family"])] += 1
    return {
        "schema_version": "orion.p3.coordinate-obstruction-gold-status.v2",
        "protocol_id": PROTOCOL_ID,
        "gold_status": GOLD_STATUS,
        "fixture_count": len(records),
        "families_with_schema_fixture": sorted(
            family for family, count in by_family.items() if count
        ),
        "families_missing_schema_fixture": sorted(
            family for family, count in by_family.items() if not count
        ),
        "expert_gold_bound": False,
        "llm_gold_used": False,
        "reason": (
            "V2 gold requires pinned expert/public annotations or content-hashed deterministic "
            "standards. Schema fixtures and V1 confirmatory pointers are not V2 gold."
        ),
    }


def emit_freeze() -> dict[str, str]:
    records = [validate_fixture(item) for item in fixtures()]
    missing = [family for family in FAMILIES if family not in {item["family"] for item in records}]
    if missing:
        raise ProtocolFreezeError(f"missing family fixtures: {', '.join(missing)}")
    PROTOCOL_PATH.parent.mkdir(parents=True, exist_ok=True)
    FIXTURE_PATH.parent.mkdir(parents=True, exist_ok=True)
    protocol = protocol_document()
    PROTOCOL_PATH.write_text(json.dumps(protocol, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    CASE_SCHEMA_PATH.write_text(
        json.dumps(case_schema(), indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    FIXTURE_PATH.write_bytes(b"\n".join(canonical_json(item) for item in records) + b"\n")
    GOLD_STATUS_PATH.write_text(
        json.dumps(gold_status_document(records), indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    return {
        "protocol_sha256": sha256_json(protocol),
        "fixtures_sha256": sha256_json(records),
        "gold_status_sha256": sha256_json(gold_status_document(records)),
        "gold_status": GOLD_STATUS,
    }


def case_schema() -> dict[str, object]:
    return {
        "$schema": "https://json-schema.org/draft/2020-12/schema",
        "$id": CASE_SCHEMA_VERSION,
        "title": "ORION-P3 coordinate-obstruction V2 case fixture",
        "type": "object",
        "required": [
            "schema_version",
            "fixture_id",
            "family",
            "pair_kind",
            "gold_status",
            "expected_integration",
            "llm_gold_forbidden",
        ],
        "properties": {
            "schema_version": {"const": CASE_SCHEMA_VERSION},
            "fixture_id": {"type": "string"},
            "family": {"enum": list(FAMILIES)},
            "pair_kind": {"type": "string"},
            "arity": {"enum": ["pair", "triple"]},
            "varied_coordinate": {"type": "string"},
            "held_constant": {"type": "array", "items": {"type": "string"}},
            "expected_integration": {"type": ["string", "null"], "enum": [*INTEGRATION_TERMINALS, None]},
            "gold_status": {"const": GOLD_STATUS},
            "gold_authority": {"type": ["object", "null"]},
            "cannot_check_reason": {"type": "string"},
            "v1_confirmatory_exemplars": {"type": "array", "items": {"type": "string"}},
            "llm_gold_forbidden": {"const": True},
        },
        "additionalProperties": True,
    }


def load_frozen_protocol() -> dict[str, object]:
    if not PROTOCOL_PATH.is_file():
        raise ProtocolFreezeError("CANNOT_CHECK: V2 protocol file missing")
    return json.loads(PROTOCOL_PATH.read_text(encoding="utf-8"))


def load_frozen_fixtures() -> list[dict[str, object]]:
    if not FIXTURE_PATH.is_file():
        raise ProtocolFreezeError("CANNOT_CHECK: V2 fixture file missing")
    records = [
        validate_fixture(json.loads(line))
        for line in FIXTURE_PATH.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]
    present = {str(item["family"]) for item in records}
    missing = [family for family in FAMILIES if family not in present]
    if missing:
        raise ProtocolFreezeError(f"CANNOT_CHECK: missing family fixtures: {', '.join(missing)}")
    return records


def protocol_relative(path: Path) -> str:
    return str(path.relative_to(REPO_ROOT))


def main() -> int:
    hashes = emit_freeze()
    print(json.dumps(hashes, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

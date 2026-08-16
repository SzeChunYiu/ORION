from __future__ import annotations

import json
from dataclasses import asdict

from orion.core.contributions import (
    AssimilationOutcome,
    KnowledgeContribution,
    MappingRelation,
    ReferentBinding,
    ReferentResolution,
    RepresentationMapping,
)
from orion.core.problem import Problem
from orion.core.residuals import Residual, Responsibility
from orion.core.search import RetrievedItem, SearchQuery, SearchRouteKind
from orion.core.state import OrionState
from orion.providers.llm.base import LLMProvider, LLMRequest
from orion.providers.reasoner.base import Diagnosis, ReframeProposal

_SYSTEM = """You are a semantic reasoning component inside ORION.
You may propose interpretations, queries, diagnoses and prose, but you do not create scientific authority.
Return only JSON matching the requested schema. Preserve uncertainty and do not invent source evidence.
For search planning, do not remain inside the current vocabulary: deliberately use independent route families such as function-only, parent-discipline, adversarial-omission and freshness searches when they remain uncovered."""


def _schema(payload: dict[str, object]) -> str:
    return json.dumps(payload, sort_keys=True, separators=(",", ":"))


_SEARCH_SCHEMA = _schema(
    {
        "type": "object",
        "required": ["queries"],
        "properties": {
            "queries": {
                "type": "array",
                "minItems": 1,
                "items": {
                    "type": "object",
                    "required": [
                        "query_id",
                        "text",
                        "route_id",
                        "route_kind",
                        "domain_hint",
                    ],
                    "properties": {
                        "query_id": {"type": "string", "minLength": 1},
                        "text": {"type": "string", "minLength": 1},
                        "route_id": {"type": "string", "minLength": 1},
                        "route_kind": {
                            "type": "string",
                            "enum": [item.value for item in SearchRouteKind],
                        },
                        "domain_hint": {"type": ["string", "null"]},
                    },
                    "additionalProperties": False,
                },
            }
        },
        "additionalProperties": False,
    }
)

_INTERPRET_SCHEMA = _schema(
    {
        "type": "object",
        "required": [
            "contribution_id",
            "text",
            "assimilation",
            "discovered_domain_ids",
            "representation_ids",
            "contradicts_claim_ids",
            "related_claim_ids",
            "context_ids",
            "referent_bindings",
            "representation_mappings",
            "assumption_ids",
        ],
        "properties": {
            "contribution_id": {"type": "string", "minLength": 1},
            "text": {"type": "string", "minLength": 1},
            "assimilation": {
                "type": "string",
                "enum": [item.value for item in AssimilationOutcome],
            },
            "discovered_domain_ids": {
                "type": "array",
                "items": {"type": "string", "minLength": 1},
            },
            "representation_ids": {
                "type": "array",
                "items": {"type": "string", "minLength": 1},
            },
            "contradicts_claim_ids": {
                "type": "array",
                "items": {"type": "string", "minLength": 1},
            },
            "related_claim_ids": {
                "type": "array",
                "items": {"type": "string", "minLength": 1},
            },
            "context_ids": {
                "type": "array",
                "items": {"type": "string", "minLength": 1},
            },
            "referent_bindings": {
                "type": "array",
                "items": {
                    "type": "object",
                    "required": ["mention", "resolution", "referent_id", "context_id"],
                    "properties": {
                        "mention": {"type": "string", "minLength": 1},
                        "resolution": {
                            "type": "string",
                            "enum": [item.value for item in ReferentResolution],
                        },
                        "referent_id": {"type": "string"},
                        "context_id": {"type": "string"},
                    },
                    "additionalProperties": False,
                },
            },
            "representation_mappings": {
                "type": "array",
                "items": {
                    "type": "object",
                    "required": [
                        "mapping_id",
                        "source_representation_id",
                        "target_representation_id",
                        "relation",
                        "evidence_ids",
                        "recoverable",
                    ],
                    "properties": {
                        "mapping_id": {"type": "string", "minLength": 1},
                        "source_representation_id": {"type": "string", "minLength": 1},
                        "target_representation_id": {"type": "string", "minLength": 1},
                        "relation": {
                            "type": "string",
                            "enum": [item.value for item in MappingRelation],
                        },
                        "evidence_ids": {
                            "type": "array",
                            "items": {"type": "string", "minLength": 1},
                        },
                        "recoverable": {"type": "boolean"},
                    },
                    "additionalProperties": False,
                },
            },
            "assumption_ids": {
                "type": "array",
                "items": {"type": "string", "minLength": 1},
            },
        },
        "additionalProperties": False,
    }
)

_RECONSTRUCT_SCHEMA = _schema(
    {
        "type": "object",
        "required": ["summary"],
        "properties": {"summary": {"type": "string"}},
        "additionalProperties": False,
    }
)

_DIAGNOSE_SCHEMA = _schema(
    {
        "type": "object",
        "required": ["responsibilities", "rationale"],
        "properties": {
            "responsibilities": {
                "type": "array",
                "minItems": 1,
                "items": {
                    "type": "string",
                    "enum": [item.value for item in Responsibility],
                },
            },
            "rationale": {"type": "string"},
        },
        "additionalProperties": False,
    }
)

_REFRAME_SCHEMA = _schema(
    {
        "type": "object",
        "required": ["add_domain_ids", "add_representation_ids", "note"],
        "properties": {
            "add_domain_ids": {
                "type": "array",
                "items": {"type": "string", "minLength": 1},
            },
            "add_representation_ids": {
                "type": "array",
                "items": {"type": "string", "minLength": 1},
            },
            "note": {"type": "string"},
        },
        "additionalProperties": False,
    }
)

_ANSWER_SCHEMA = _schema(
    {
        "type": "object",
        "required": ["answer"],
        "properties": {"answer": {"type": "string"}},
        "additionalProperties": False,
    }
)


def _required_string(item: dict, field: str, *, context: str) -> str:
    value = item.get(field)
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{context}.{field} must be a non-empty string")
    return value


def _string_list(value: object, *, field: str) -> tuple[str, ...]:
    if not isinstance(value, list) or any(
        not isinstance(item, str) or not item.strip() for item in value
    ):
        raise ValueError(f"{field} must be an array of non-empty strings")
    return tuple(value)


class LLMResearchReasoner:
    """Maps the ORION reasoner contract onto any LLMProvider."""

    def __init__(self, provider: LLMProvider) -> None:
        self._provider = provider

    def _call(self, task: str, payload: dict, schema: str) -> dict:
        response = self._provider.complete(
            LLMRequest(
                task=task,
                system=_SYSTEM,
                user=json.dumps(payload, sort_keys=True),
                response_schema=schema,
            )
        )
        try:
            data = json.loads(response.content)
        except json.JSONDecodeError as exc:
            raise ValueError(f"LLM returned invalid JSON for {task}") from exc
        if not isinstance(data, dict):
            raise TypeError(f"LLM response for {task} must be a JSON object")
        return data

    def plan_search(self, problem: Problem, state: OrionState) -> tuple[SearchQuery, ...]:
        data = self._call(
            "plan_search",
            {
                "problem": asdict(problem),
                "active_domains": state.search_universe.active_domain_ids,
                "candidate_domains": state.search_universe.candidate_domain_ids,
                "searched_domains": state.search_universe.searched_domain_ids,
                "covered_route_kinds": state.search_universe.route_kind_ids,
                "representations": state.search_universe.representation_ids,
            },
            _SEARCH_SCHEMA,
        )
        queries = data.get("queries")
        if not isinstance(queries, list) or not queries:
            raise ValueError("plan_search.queries must be a non-empty list")
        parsed: list[SearchQuery] = []
        for index, item in enumerate(queries):
            if not isinstance(item, dict):
                raise ValueError(f"plan_search.queries[{index}] must be an object")
            route_kind_value = _required_string(
                item, "route_kind", context=f"plan_search.queries[{index}]"
            )
            try:
                route_kind = SearchRouteKind(route_kind_value)
            except ValueError as error:
                raise ValueError(
                    f"plan_search.queries[{index}].route_kind is invalid: {route_kind_value}"
                ) from error
            domain_hint = item.get("domain_hint")
            if domain_hint is not None and (
                not isinstance(domain_hint, str) or not domain_hint.strip()
            ):
                raise ValueError(
                    f"plan_search.queries[{index}].domain_hint must be null or a non-empty string"
                )
            parsed.append(
                SearchQuery(
                    query_id=_required_string(
                        item, "query_id", context=f"plan_search.queries[{index}]"
                    ),
                    text=_required_string(
                        item, "text", context=f"plan_search.queries[{index}]"
                    ),
                    route_id=_required_string(
                        item, "route_id", context=f"plan_search.queries[{index}]"
                    ),
                    route_kind=route_kind,
                    domain_hint=domain_hint,
                )
            )
        return tuple(parsed)

    def interpret(
        self, item: RetrievedItem, problem: Problem, state: OrionState
    ) -> KnowledgeContribution:
        data = self._call(
            "interpret",
            {
                "problem": asdict(problem),
                "retrieved_item": asdict(item),
                "known_claims": [claim.text for claim in state.knowledge.claims],
                "active_domains": state.search_universe.active_domain_ids,
                "known_source_projections": state.knowledge.source_projection_ids,
                "known_representation_mappings": state.knowledge.representation_mapping_ids,
            },
            _INTERPRET_SCHEMA,
        )
        referent_raw = data.get("referent_bindings")
        if not isinstance(referent_raw, list):
            raise ValueError("interpret.referent_bindings must be a list")
        referent_bindings = tuple(
            ReferentBinding(
                mention=_required_string(
                    binding, "mention", context=f"interpret.referent_bindings[{index}]"
                ),
                resolution=ReferentResolution(
                    _required_string(
                        binding,
                        "resolution",
                        context=f"interpret.referent_bindings[{index}]",
                    )
                ),
                referent_id=str(binding.get("referent_id", "")),
                context_id=str(binding.get("context_id", "")),
            )
            for index, binding in enumerate(referent_raw)
            if isinstance(binding, dict)
        )
        if len(referent_bindings) != len(referent_raw):
            raise ValueError("interpret.referent_bindings must contain objects")
        mappings_raw = data.get("representation_mappings")
        if not isinstance(mappings_raw, list):
            raise ValueError("interpret.representation_mappings must be a list")
        representation_mappings = tuple(
            RepresentationMapping(
                mapping_id=_required_string(
                    mapping,
                    "mapping_id",
                    context=f"interpret.representation_mappings[{index}]",
                ),
                source_representation_id=_required_string(
                    mapping,
                    "source_representation_id",
                    context=f"interpret.representation_mappings[{index}]",
                ),
                target_representation_id=_required_string(
                    mapping,
                    "target_representation_id",
                    context=f"interpret.representation_mappings[{index}]",
                ),
                relation=MappingRelation(
                    _required_string(
                        mapping,
                        "relation",
                        context=f"interpret.representation_mappings[{index}]",
                    )
                ),
                evidence_ids=_string_list(
                    mapping.get("evidence_ids"),
                    field=f"interpret.representation_mappings[{index}].evidence_ids",
                ),
                recoverable=bool(mapping.get("recoverable")),
            )
            for index, mapping in enumerate(mappings_raw)
            if isinstance(mapping, dict)
        )
        if len(representation_mappings) != len(mappings_raw):
            raise ValueError("interpret.representation_mappings must contain objects")
        return KnowledgeContribution(
            contribution_id=_required_string(
                data, "contribution_id", context="interpret"
            ),
            text=_required_string(data, "text", context="interpret"),
            assimilation=AssimilationOutcome(
                _required_string(data, "assimilation", context="interpret")
            ),
            evidence_ids=(item.item_id,),
            discovered_domain_ids=_string_list(
                data.get("discovered_domain_ids"), field="interpret.discovered_domain_ids"
            ),
            representation_ids=_string_list(
                data.get("representation_ids"), field="interpret.representation_ids"
            ),
            contradicts_claim_ids=_string_list(
                data.get("contradicts_claim_ids"), field="interpret.contradicts_claim_ids"
            ),
            related_claim_ids=_string_list(
                data.get("related_claim_ids"), field="interpret.related_claim_ids"
            ),
            context_ids=_string_list(
                data.get("context_ids"), field="interpret.context_ids"
            ),
            referent_bindings=referent_bindings,
            representation_mappings=representation_mappings,
            assumption_ids=_string_list(
                data.get("assumption_ids"), field="interpret.assumption_ids"
            ),
        )

    def reconstruct(self, problem: Problem, state: OrionState) -> str:
        data = self._call(
            "reconstruct",
            {
                "problem": asdict(problem),
                "claims": [
                    {
                        "claim_id": claim.claim_id,
                        "text": claim.text,
                        "authority": claim.authority.value,
                    }
                    for claim in state.knowledge.claims
                ],
                "source_projection_ids": state.knowledge.source_projection_ids,
                "representation_mapping_ids": state.knowledge.representation_mapping_ids,
                "unresolved_residual_ids": state.knowledge.residual_ids,
            },
            _RECONSTRUCT_SCHEMA,
        )
        summary = data.get("summary")
        if not isinstance(summary, str):
            raise ValueError("reconstruct.summary must be a string")
        return summary

    def diagnose(
        self, residual: Residual, problem: Problem, state: OrionState
    ) -> Diagnosis:
        data = self._call(
            "diagnose",
            {
                "problem": asdict(problem),
                "residual": {
                    "id": residual.residual_id,
                    "kind": residual.kind.value,
                    "description": residual.description,
                    "metadata": residual.metadata_dict(),
                },
            },
            _DIAGNOSE_SCHEMA,
        )
        raw = _string_list(
            data.get("responsibilities"), field="diagnose.responsibilities"
        )
        if not raw:
            raise ValueError("diagnose.responsibilities cannot be empty")
        responsibilities = tuple(Responsibility(value) for value in raw)
        rationale = data.get("rationale")
        if not isinstance(rationale, str):
            raise ValueError("diagnose.rationale must be a string")
        return Diagnosis(responsibilities=responsibilities, rationale=rationale)

    def propose_reframe(
        self,
        residual: Residual,
        diagnosis: Diagnosis,
        problem: Problem,
        state: OrionState,
    ) -> ReframeProposal:
        data = self._call(
            "propose_reframe",
            {
                "problem": asdict(problem),
                "residual": residual.description,
                "responsibilities": [r.value for r in diagnosis.responsibilities],
                "active_domains": state.search_universe.active_domain_ids,
                "candidate_domains": state.search_universe.candidate_domain_ids,
            },
            _REFRAME_SCHEMA,
        )
        note = data.get("note")
        if not isinstance(note, str):
            raise ValueError("propose_reframe.note must be a string")
        return ReframeProposal(
            add_domain_ids=_string_list(
                data.get("add_domain_ids"), field="propose_reframe.add_domain_ids"
            ),
            add_representation_ids=_string_list(
                data.get("add_representation_ids"),
                field="propose_reframe.add_representation_ids",
            ),
            note=note,
        )

    def compose_answer(self, problem: Problem, state: OrionState) -> str:
        verified = [
            {
                "claim_id": claim.claim_id,
                "text": claim.text,
                "evidence_ids": claim.evidence_ids,
            }
            for claim in state.knowledge.claims
            if claim.authority.value == "VERIFIED"
        ]
        data = self._call(
            "compose_answer",
            {"problem": asdict(problem), "verified_claims": verified},
            _ANSWER_SCHEMA,
        )
        answer = data.get("answer")
        if not isinstance(answer, str):
            raise ValueError("compose_answer.answer must be a string")
        return answer

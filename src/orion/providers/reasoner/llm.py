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
            '{"queries":[{"query_id":"...","text":"...","route_id":"...","route_kind":"PARENT_DISCIPLINE","domain_hint":null}]}',
        )
        queries = data.get("queries", [])
        if not isinstance(queries, list):
            raise TypeError("plan_search.queries must be a list")
        return tuple(
            SearchQuery(
                query_id=str(item["query_id"]),
                text=str(item["text"]),
                route_id=str(item["route_id"]),
                route_kind=SearchRouteKind(str(item["route_kind"])),
                domain_hint=(str(item["domain_hint"]) if item.get("domain_hint") else None),
            )
            for item in queries
        )

    def interpret(self, item: RetrievedItem, problem: Problem, state: OrionState) -> KnowledgeContribution:
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
            (
                '{"contribution_id":"...","text":"...",'
                '"assimilation":"COMPLEMENTARY_FACET","discovered_domain_ids":[],'
                '"representation_ids":[],"contradicts_claim_ids":[],"related_claim_ids":[],'
                '"context_ids":[],"referent_bindings":[{"mention":"...",'
                '"resolution":"RESOLVED","referent_id":"...","context_id":"..."}],'
                '"representation_mappings":[{"mapping_id":"...",'
                '"source_representation_id":"...","target_representation_id":"orion:...",'
                '"relation":"EQUIVALENT","evidence_ids":["..."],"recoverable":true}],'
                '"assumption_ids":[]}'
            ),
        )
        referent_bindings = tuple(
            ReferentBinding(
                mention=str(binding["mention"]),
                resolution=ReferentResolution(str(binding["resolution"])),
                referent_id=str(binding.get("referent_id", "")),
                context_id=str(binding.get("context_id", "")),
            )
            for binding in data.get("referent_bindings", [])
        )
        representation_mappings = tuple(
            RepresentationMapping(
                mapping_id=str(mapping["mapping_id"]),
                source_representation_id=str(mapping["source_representation_id"]),
                target_representation_id=str(mapping["target_representation_id"]),
                relation=MappingRelation(str(mapping["relation"])),
                evidence_ids=tuple(str(value) for value in mapping.get("evidence_ids", [])),
                recoverable=bool(mapping.get("recoverable", True)),
            )
            for mapping in data.get("representation_mappings", [])
        )
        return KnowledgeContribution(
            contribution_id=str(data["contribution_id"]),
            text=str(data["text"]),
            assimilation=AssimilationOutcome(str(data["assimilation"])),
            evidence_ids=(item.item_id,),
            discovered_domain_ids=tuple(str(x) for x in data.get("discovered_domain_ids", [])),
            representation_ids=tuple(str(x) for x in data.get("representation_ids", [])),
            contradicts_claim_ids=tuple(str(x) for x in data.get("contradicts_claim_ids", [])),
            related_claim_ids=tuple(str(x) for x in data.get("related_claim_ids", [])),
            context_ids=tuple(str(x) for x in data.get("context_ids", [])),
            referent_bindings=referent_bindings,
            representation_mappings=representation_mappings,
            assumption_ids=tuple(str(x) for x in data.get("assumption_ids", [])),
        )

    def reconstruct(self, problem: Problem, state: OrionState) -> str:
        data = self._call(
            "reconstruct",
            {
                "problem": asdict(problem),
                "claims": [
                    {"claim_id": claim.claim_id, "text": claim.text, "authority": claim.authority.value}
                    for claim in state.knowledge.claims
                ],
                "source_projection_ids": state.knowledge.source_projection_ids,
                "representation_mapping_ids": state.knowledge.representation_mapping_ids,
                "unresolved_residual_ids": state.knowledge.residual_ids,
            },
            '{"summary":"..."}',
        )
        return str(data.get("summary", ""))

    def diagnose(self, residual: Residual, problem: Problem, state: OrionState) -> Diagnosis:
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
            '{"responsibilities":["SEARCH"],"rationale":"..."}',
        )
        responsibilities = tuple(Responsibility(str(value)) for value in data.get("responsibilities", []))
        return Diagnosis(responsibilities=responsibilities, rationale=str(data.get("rationale", "")))

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
            '{"add_domain_ids":[],"add_representation_ids":[],"note":"..."}',
        )
        return ReframeProposal(
            add_domain_ids=tuple(str(x) for x in data.get("add_domain_ids", [])),
            add_representation_ids=tuple(str(x) for x in data.get("add_representation_ids", [])),
            note=str(data.get("note", "")),
        )

    def compose_answer(self, problem: Problem, state: OrionState) -> str:
        verified = [
            {"claim_id": claim.claim_id, "text": claim.text, "evidence_ids": claim.evidence_ids}
            for claim in state.knowledge.claims
            if claim.authority.value == "VERIFIED"
        ]
        data = self._call(
            "compose_answer",
            {"problem": asdict(problem), "verified_claims": verified},
            '{"answer":"..."}',
        )
        return str(data.get("answer", ""))
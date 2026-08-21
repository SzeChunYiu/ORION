from __future__ import annotations

import json
from collections.abc import Mapping
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
from orion.core.problem_tree import (
    DiscriminatorKind,
    DiscriminatorSpec,
    RecursiveProblemStopReason,
    ResidualAtom,
    ResidualDecomposition,
)
from orion.core.residuals import Residual, Responsibility
from orion.core.search import RetrievedItem, SearchQuery, SearchRouteKind
from orion.core.state import OrionState
from orion.providers.llm.base import LLMProvider, LLMRequest
from orion.providers.reasoner.base import Diagnosis, ReframeProposal

_SYSTEM = """You are a semantic reasoning component inside ORION.
You may propose interpretations, queries, diagnoses, decompositions and prose, but you do not create scientific authority.
Return only JSON matching the requested schema. Preserve uncertainty and do not invent source evidence.
For search planning, do not remain inside the current vocabulary: deliberately use independent route families such as function-only, parent-discipline, adversarial-omission and freshness searches when they remain uncovered.
For residual decomposition, treat a material residual as a child research problem. Split broad residuals recursively until every child is decision-separating and has exactly one concrete discriminator. Prefer cheap obstruction, dominance, exact-computation or donor-subsumption tests before expensive experiments when those tests can settle the same child. Do not merely rename the parent residual. Preserve interaction-only possibilities and return an explicit stop reason when no valid finer decomposition is identifiable. Decomposition is proposal-only and never grants scientific, novelty, adoption, promotion, merge or global-stop authority."""


def _nonempty_string(value: object, *, name: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise TypeError(f"{name} must be a non-empty string")
    return value


def _string_array(value: object, *, name: str) -> tuple[str, ...]:
    if not isinstance(value, list):
        raise TypeError(f"{name} must be an array")
    result = tuple(_nonempty_string(item, name=f"{name} entry") for item in value)
    return result


def _string_metadata(value: object, *, name: str) -> tuple[tuple[str, str], ...]:
    if value is None:
        return ()
    if not isinstance(value, Mapping):
        raise TypeError(f"{name} must be an object")
    rows: list[tuple[str, str]] = []
    for key, item in value.items():
        rows.append(
            (
                _nonempty_string(key, name=f"{name} key"),
                _nonempty_string(item, name=f"{name}.{key}"),
            )
        )
    return tuple(sorted(rows))


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
                    "candidate_responsibilities": [
                        value.value for value in residual.candidate_responsibilities
                    ],
                    "metadata": residual.metadata_dict(),
                },
            },
            '{"responsibilities":["SEARCH"],"rationale":"..."}',
        )
        responsibilities = tuple(Responsibility(str(value)) for value in data.get("responsibilities", []))
        return Diagnosis(responsibilities=responsibilities, rationale=str(data.get("rationale", "")))

    def decompose_residual(
        self,
        residual: Residual,
        problem: Problem,
        state: OrionState,
    ) -> ResidualDecomposition:
        data = self._call(
            "decompose_residual",
            {
                "problem": asdict(problem),
                "residual": {
                    "id": residual.residual_id,
                    "kind": residual.kind.value,
                    "description": residual.description,
                    "candidate_responsibilities": [
                        value.value for value in residual.candidate_responsibilities
                    ],
                    "metadata": residual.metadata_dict(),
                },
                "known_evidence_ids": list(state.knowledge.evidence_ids),
                "known_negative_history_ids": list(state.knowledge.negative_history_ids),
                "active_domains": list(state.search_universe.active_domain_ids),
                "representations": list(state.search_universe.representation_ids),
                "instruction": (
                    "Return a decision-separating recursive decomposition. Each atom must be "
                    "strictly narrower than the parent residual and must have exactly one concrete "
                    "discriminator. Prefer a lower-cost dominance/formal/exact/donor obstruction "
                    "when it can settle the same atom. If no valid finer split is identifiable, "
                    "return no atoms and an explicit stop_reason. Never claim authority."
                ),
            },
            (
                '{"atoms":[{"atom_id":"...","question":"...",'
                '"responsibility":"METHOD","scope":"...","initial_domain_ids":[],'
                '"metadata":{},"discriminator":{"discriminator_id":"...",'
                '"kind":"DOMINANCE_PROOF","question":"...",'
                '"success_criterion":"...","expected_cost_units":1.0,'
                '"metadata":{}}}],"stop_reason":null,"rationale":"..."}'
            ),
        )
        raw_atoms = data.get("atoms", [])
        if not isinstance(raw_atoms, list):
            raise TypeError("decompose_residual.atoms must be an array")
        atoms: list[ResidualAtom] = []
        for index, raw in enumerate(raw_atoms):
            if not isinstance(raw, Mapping):
                raise TypeError("decompose_residual atom must be an object")
            raw_discriminator = raw.get("discriminator")
            if not isinstance(raw_discriminator, Mapping):
                raise TypeError("decompose_residual atom.discriminator must be an object")
            raw_cost = raw_discriminator.get("expected_cost_units")
            if isinstance(raw_cost, bool) or not isinstance(raw_cost, (int, float)):
                raise TypeError(
                    "decompose_residual discriminator.expected_cost_units must be numeric"
                )
            raw_domains = raw.get("initial_domain_ids", [])
            domains = _string_array(
                raw_domains, name=f"decompose_residual.atoms[{index}].initial_domain_ids"
            )
            scope = raw.get("scope", "")
            if not isinstance(scope, str):
                raise TypeError("decompose_residual atom.scope must be a string")
            atoms.append(
                ResidualAtom(
                    atom_id=_nonempty_string(
                        raw.get("atom_id"),
                        name=f"decompose_residual.atoms[{index}].atom_id",
                    ),
                    question=_nonempty_string(
                        raw.get("question"),
                        name=f"decompose_residual.atoms[{index}].question",
                    ),
                    responsibility=Responsibility(
                        _nonempty_string(
                            raw.get("responsibility"),
                            name=f"decompose_residual.atoms[{index}].responsibility",
                        )
                    ),
                    scope=scope,
                    initial_domain_ids=domains,
                    metadata=_string_metadata(
                        raw.get("metadata", {}),
                        name=f"decompose_residual.atoms[{index}].metadata",
                    ),
                    discriminator=DiscriminatorSpec(
                        discriminator_id=_nonempty_string(
                            raw_discriminator.get("discriminator_id"),
                            name=(
                                f"decompose_residual.atoms[{index}]"
                                ".discriminator.discriminator_id"
                            ),
                        ),
                        kind=DiscriminatorKind(
                            _nonempty_string(
                                raw_discriminator.get("kind"),
                                name=(
                                    f"decompose_residual.atoms[{index}]"
                                    ".discriminator.kind"
                                ),
                            )
                        ),
                        question=_nonempty_string(
                            raw_discriminator.get("question"),
                            name=(
                                f"decompose_residual.atoms[{index}]"
                                ".discriminator.question"
                            ),
                        ),
                        success_criterion=_nonempty_string(
                            raw_discriminator.get("success_criterion"),
                            name=(
                                f"decompose_residual.atoms[{index}]"
                                ".discriminator.success_criterion"
                            ),
                        ),
                        expected_cost_units=float(raw_cost),
                        metadata=_string_metadata(
                            raw_discriminator.get("metadata", {}),
                            name=(
                                f"decompose_residual.atoms[{index}]"
                                ".discriminator.metadata"
                            ),
                        ),
                    ),
                )
            )
        raw_stop = data.get("stop_reason")
        if raw_stop is not None and not isinstance(raw_stop, str):
            raise TypeError("decompose_residual.stop_reason must be a string or null")
        stop_reason = (
            None if raw_stop is None else RecursiveProblemStopReason(raw_stop)
        )
        rationale = data.get("rationale", "")
        if not isinstance(rationale, str):
            raise TypeError("decompose_residual.rationale must be a string")
        decomposition = ResidualDecomposition(
            parent_residual_id=residual.residual_id,
            atoms=tuple(atoms),
            stop_reason=stop_reason,
            rationale=rationale,
        )
        decomposition.verify(residual)
        return decomposition

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

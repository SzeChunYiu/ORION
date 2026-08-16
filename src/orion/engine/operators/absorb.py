from __future__ import annotations

from dataclasses import replace

from orion.core.claims import ClaimAuthority, ClaimRecord
from orion.core.evidence import EvidenceRecord
from orion.core.problem import Problem
from orion.core.state import OrionState
from orion.engine.contracts import OperatorResult
from orion.engine.cycle import CycleOperator, Transition
from orion.engine.operators.search import SearchBatch
from orion.knowledge.assimilation import (
    assimilation_effect,
    build_source_projection,
    representation_ids_for,
    residuals_for_contribution,
)
from orion.providers.reasoner.base import ResearchReasoner
from orion.providers.verification.base import VerificationProvider


class AbsorbOperator:
    operator_id = "ABSORB.v1"

    def __init__(self, reasoner: ResearchReasoner, verification: VerificationProvider) -> None:
        self._reasoner = reasoner
        self._verification = verification

    def run(
        self,
        problem: Problem,
        state: OrionState,
        batch: SearchBatch,
    ) -> OperatorResult[tuple[str, ...]]:
        claims = list(state.knowledge.claims)
        evidence = list(state.knowledge.evidence)
        residuals = list(state.knowledge.residuals)
        projections = list(state.knowledge.source_projections)
        mappings = list(state.knowledge.representation_mappings)

        known_evidence = {item.evidence_id for item in evidence}
        known_claims = {claim.claim_id for claim in claims}
        known_residuals = {residual.residual_id for residual in residuals}
        known_projections = {projection.projection_id for projection in projections}
        known_mappings = {mapping.mapping_id for mapping in mappings}

        certificate_ids: list[str] = []
        contribution_ids: list[str] = []
        discovered_domains: list[str] = []
        representations: list[str] = []
        evidence_added = False
        claim_added = False
        residual_added = False
        projection_added = False
        mapping_added = False

        for item in batch.items:
            contribution = self._reasoner.interpret(item, problem, state)
            contribution_ids.append(contribution.contribution_id)
            effect = assimilation_effect(contribution.assimilation)
            projection = build_source_projection(contribution, item, problem)

            if item.item_id not in known_evidence:
                evidence.append(
                    EvidenceRecord(
                        evidence_id=item.item_id,
                        content=item.content,
                        source_uri=item.source_uri,
                        domain_ids=item.domain_ids,
                    )
                )
                known_evidence.add(item.item_id)
                evidence_added = True

            if projection.projection_id not in known_projections:
                projections.append(projection)
                known_projections.add(projection.projection_id)
                projection_added = True

            for mapping in contribution.representation_mappings:
                if mapping.mapping_id in known_mappings:
                    continue
                mappings.append(mapping)
                known_mappings.add(mapping.mapping_id)
                mapping_added = True

            for residual in residuals_for_contribution(contribution):
                if residual.residual_id in known_residuals:
                    continue
                residuals.append(residual)
                known_residuals.add(residual.residual_id)
                residual_added = True

            if effect.widen_search_universe:
                discovered_domains.extend(contribution.discovered_domain_ids)
                representations.extend(representation_ids_for(contribution))

            if not effect.integrate_claim:
                continue

            verification = self._verification.verify(contribution, item)
            authority = (
                ClaimAuthority.VERIFIED
                if verification.passed
                else ClaimAuthority.SOURCE_PROJECTION
            )
            if contribution.contribution_id not in known_claims:
                claims.append(
                    ClaimRecord(
                        claim_id=contribution.contribution_id,
                        text=contribution.text,
                        evidence_ids=contribution.evidence_ids,
                        authority=authority,
                        certificate_ids=verification.certificate_ids,
                        contradicts_claim_ids=contribution.contradicts_claim_ids,
                    )
                )
                known_claims.add(contribution.contribution_id)
                claim_added = True
                if verification.passed:
                    certificate_ids.extend(verification.certificate_ids)

        universe = state.search_universe.add_candidates(tuple(discovered_domains))
        universe = universe.add_representations(tuple(representations))
        knowledge = replace(
            state.knowledge,
            claims=tuple(claims),
            evidence=tuple(evidence),
            residuals=tuple(residuals),
            source_projections=tuple(projections),
            representation_mappings=tuple(mappings),
        )
        next_state = replace(state, knowledge=knowledge, search_universe=universe)

        transition = Transition(
            operator=CycleOperator.ABSORB,
            input_epoch=state.epoch,
            output_epoch=state.epoch,
            evidence_ids=tuple(item.item_id for item in batch.items),
            authority_increase=bool(certificate_ids),
            scientific_authority_certificate_ids=tuple(certificate_ids),
            changed_coordinates=tuple(
                coordinate
                for coordinate, changed in (
                    ("K.EVIDENCE", evidence_added),
                    ("K.SOURCE_PROJECTIONS", projection_added),
                    ("K.CLAIMS", claim_added),
                    ("K.RESIDUALS", residual_added),
                    ("K.REPRESENTATION_MAPPINGS", mapping_added),
                    ("W.CANDIDATE_DOMAINS", bool(discovered_domains)),
                    ("W.REPRESENTATIONS", bool(representations)),
                )
                if changed
            ),
        )
        return OperatorResult(next_state, tuple(contribution_ids), transition)

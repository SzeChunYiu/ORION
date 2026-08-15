from __future__ import annotations

from dataclasses import replace

from orion.core.claims import ClaimAuthority, ClaimRecord
from orion.core.evidence import EvidenceRecord
from orion.core.problem import Problem
from orion.core.state import OrionState
from orion.engine.contracts import OperatorResult
from orion.engine.cycle import CycleOperator, Transition
from orion.engine.operators.search import SearchBatch
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
        known_evidence = {item.evidence_id for item in evidence}
        known_claims = {claim.claim_id for claim in claims}
        certificate_ids: list[str] = []
        contribution_ids: list[str] = []
        discovered_domains: list[str] = []
        representations: list[str] = []

        for item in batch.items:
            contribution = self._reasoner.interpret(item, problem, state)
            contribution_ids.append(contribution.contribution_id)
            discovered_domains.extend(contribution.discovered_domain_ids)
            representations.extend(contribution.representation_ids)

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

            verification = self._verification.verify(contribution, item)
            authority = ClaimAuthority.VERIFIED if verification.passed else ClaimAuthority.SOURCE_PROJECTION
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
            certificate_ids.extend(verification.certificate_ids)

        universe = state.search_universe.add_candidates(tuple(discovered_domains))
        universe = universe.add_representations(tuple(representations))
        knowledge = replace(state.knowledge, claims=tuple(claims), evidence=tuple(evidence))
        next_state = replace(state, knowledge=knowledge, search_universe=universe)

        transition = Transition(
            operator=CycleOperator.ABSORB,
            input_epoch=state.epoch,
            output_epoch=state.epoch,
            evidence_ids=tuple(item.item_id for item in batch.items),
            authority_increase=bool(certificate_ids),
            scientific_authority_certificate_ids=tuple(certificate_ids),
            changed_coordinates=tuple(
                coord
                for coord, changed in (
                    ("K.CLAIMS", bool(batch.items)),
                    ("W.CANDIDATE_DOMAINS", bool(discovered_domains)),
                    ("W.REPRESENTATIONS", bool(representations)),
                )
                if changed
            ),
        )
        return OperatorResult(next_state, tuple(contribution_ids), transition)

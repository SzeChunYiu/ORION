from __future__ import annotations

from dataclasses import dataclass

from orion.core.contributions import KnowledgeContribution
from orion.core.search import RetrievedItem
from orion.providers.verification.base import VerificationResult


@dataclass(frozen=True)
class InMemoryVerificationProvider:
    accepted_item_ids: frozenset[str]

    def verify(self, contribution: KnowledgeContribution, item: RetrievedItem) -> VerificationResult:
        if item.item_id in self.accepted_item_ids:
            return VerificationResult(
                passed=True,
                certificate_ids=(f"verify:{item.item_id}:{contribution.contribution_id}",),
                reason="known-world protected verifier",
            )
        return VerificationResult(passed=False, reason="item not accepted by protected verifier")

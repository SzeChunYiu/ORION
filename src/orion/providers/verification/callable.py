from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass

from orion.core.contributions import KnowledgeContribution
from orion.core.search import RetrievedItem
from orion.providers.verification.base import VerificationResult


@dataclass(frozen=True)
class CallableVerificationProvider:
    verify_fn: Callable[[KnowledgeContribution, RetrievedItem], VerificationResult]

    def verify(self, contribution: KnowledgeContribution, item: RetrievedItem) -> VerificationResult:
        result = self.verify_fn(contribution, item)
        if not isinstance(result, VerificationResult):
            raise TypeError("verification callable must return VerificationResult")
        return result

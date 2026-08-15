from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol

from orion.core.contributions import KnowledgeContribution
from orion.core.search import RetrievedItem


@dataclass(frozen=True)
class VerificationResult:
    passed: bool
    certificate_ids: tuple[str, ...] = ()
    reason: str = ""

    def __post_init__(self) -> None:
        if self.passed and not self.certificate_ids:
            raise ValueError("passed verification requires certificate_ids")


class VerificationProvider(Protocol):
    def verify(self, contribution: KnowledgeContribution, item: RetrievedItem) -> VerificationResult:
        ...

from __future__ import annotations

from dataclasses import dataclass
from typing import Mapping, Sequence

from ..types import ProblemSignature, TransferStatus
from .canonical import content_digest
from .models import TransferReceipt, build_transfer_receipt, problem_signature_payload
from .registry import TransferRegistry

PORTFOLIO_VERSION = "ORION_TRANSFER_PORTFOLIO_V2"


def _evidence_bundle_payload(evidence_by_cell: Mapping[str, Mapping[str, object]]) -> dict[str, object]:
    out: dict[str, object] = {}
    for cell_id in sorted(evidence_by_cell):
        raw = evidence_by_cell[cell_id]
        allowed = {"assumptions", "falsifiers", "provenance"}
        if set(raw) - allowed:
            raise ValueError(f"unexpected evidence envelope fields for {cell_id}")
        assumptions = raw.get("assumptions", {})
        falsifiers = raw.get("falsifiers", {})
        provenance = raw.get("provenance", [])
        if not isinstance(assumptions, Mapping) or not isinstance(falsifiers, Mapping):
            raise ValueError("assumptions/falsifiers evidence must be objects")
        if not isinstance(provenance, Sequence) or isinstance(provenance, (str, bytes)):
            raise ValueError("provenance must be a sequence of strings")
        out[cell_id] = {
            "assumptions": dict(assumptions),
            "falsifiers": dict(falsifiers),
            "provenance": list(provenance),
        }
    return out


@dataclass(frozen=True)
class PortfolioReceipt:
    target_id: str
    target_digest: str
    catalog_digest: str
    evidence_bundle_digest: str
    min_independent_domains: int
    decisions: tuple[TransferReceipt, ...]
    selected_cell_ids: tuple[str, ...]
    confirmed_mechanisms: tuple[str, ...]
    receipt_digest: str
    portfolio_version: str = PORTFOLIO_VERSION

    def unsigned_payload(self) -> dict[str, object]:
        return {
            "portfolio_version": self.portfolio_version,
            "target_id": self.target_id,
            "target_digest": self.target_digest,
            "catalog_digest": self.catalog_digest,
            "evidence_bundle_digest": self.evidence_bundle_digest,
            "min_independent_domains": self.min_independent_domains,
            "decisions": [decision.to_payload() for decision in self.decisions],
            "selected_cell_ids": list(self.selected_cell_ids),
            "confirmed_mechanisms": list(self.confirmed_mechanisms),
        }

    def to_payload(self) -> dict[str, object]:
        payload = self.unsigned_payload()
        payload["receipt_digest"] = self.receipt_digest
        return payload

    def verify(self) -> None:
        if self.portfolio_version != PORTFOLIO_VERSION:
            raise ValueError("unsupported portfolio receipt version")
        for decision in self.decisions:
            decision.verify()
        expected = content_digest(self.unsigned_payload())
        if expected != self.receipt_digest:
            raise ValueError("portfolio receipt digest mismatch")


def build_portfolio(
    target: ProblemSignature,
    registry: TransferRegistry,
    evidence_by_cell: Mapping[str, Mapping[str, object]],
    *,
    min_independent_domains: int = 1,
) -> PortfolioReceipt:
    if min_independent_domains < 1:
        raise ValueError("min_independent_domains must be >= 1")
    known_ids = {cell.cell_id for cell in registry.cells}
    unknown_ids = set(evidence_by_cell) - known_ids
    if unknown_ids:
        raise ValueError(f"evidence references unknown cells: {sorted(unknown_ids)}")
    bundle = _evidence_bundle_payload(evidence_by_cell)

    ranked = sorted(
        registry.cells,
        key=lambda cell: (-target.far_domain_score(cell.source_signature), cell.cell_id),
    )
    decisions: list[TransferReceipt] = []
    for cell in ranked:
        evidence = bundle.get(cell.cell_id, {"assumptions": {}, "falsifiers": {}, "provenance": []})
        receipt = build_transfer_receipt(
            target,
            cell,
            assumption_truth=evidence["assumptions"],  # type: ignore[arg-type]
            falsifier_results=evidence["falsifiers"],  # type: ignore[arg-type]
            provenance=evidence["provenance"],  # type: ignore[arg-type]
        )
        decisions.append(receipt)

    admissible = [decision for decision in decisions if decision.status is TransferStatus.ADMISSIBLE]
    confirmed_mechanisms: list[str] = []
    if min_independent_domains == 1:
        selected = [decision.cell_id for decision in admissible]
        confirmed_mechanisms = sorted({decision.mechanism for decision in admissible})
    else:
        by_mechanism: dict[str, set[str]] = {}
        for decision in admissible:
            by_mechanism.setdefault(decision.mechanism, set()).add(decision.source_domain)
        confirmed_mechanisms = sorted(
            mechanism
            for mechanism, domains in by_mechanism.items()
            if len(domains) >= min_independent_domains
        )
        allowed = set(confirmed_mechanisms)
        selected = [decision.cell_id for decision in admissible if decision.mechanism in allowed]

    unsigned = {
        "portfolio_version": PORTFOLIO_VERSION,
        "target_id": target.problem_id,
        "target_digest": content_digest(problem_signature_payload(target)),
        "catalog_digest": registry.digest,
        "evidence_bundle_digest": content_digest(bundle),
        "min_independent_domains": min_independent_domains,
        "decisions": [decision.to_payload() for decision in decisions],
        "selected_cell_ids": selected,
        "confirmed_mechanisms": confirmed_mechanisms,
    }
    return PortfolioReceipt(
        target_id=target.problem_id,
        target_digest=unsigned["target_digest"],  # type: ignore[arg-type]
        catalog_digest=registry.digest,
        evidence_bundle_digest=unsigned["evidence_bundle_digest"],  # type: ignore[arg-type]
        min_independent_domains=min_independent_domains,
        decisions=tuple(decisions),
        selected_cell_ids=tuple(selected),
        confirmed_mechanisms=tuple(confirmed_mechanisms),
        receipt_digest=content_digest(unsigned),
    )


def verify_portfolio_replay(
    receipt: PortfolioReceipt,
    target: ProblemSignature,
    registry: TransferRegistry,
    evidence_by_cell: Mapping[str, Mapping[str, object]],
) -> None:
    receipt.verify()
    rebuilt = build_portfolio(
        target,
        registry,
        evidence_by_cell,
        min_independent_domains=receipt.min_independent_domains,
    )
    if rebuilt.to_payload() != receipt.to_payload():
        raise ValueError("portfolio replay mismatch")

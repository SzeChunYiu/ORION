"""Content-addressed, fail-closed productionization of ORION transfer mechanics.

Everything in this package is local engineering infrastructure or a V2/future-study
hook. It does not mutate or authorize any frozen P1-P5 V1 publication protocol.
"""

from .canonical import canonical_json, content_digest, verify_digest
from .manifest import validate_paper_v2_manifest
from .models import TransferReceipt, build_transfer_receipt
from .portfolio import PortfolioReceipt, build_portfolio, verify_portfolio_replay
from .registry import TransferRegistry

__all__ = [
    "PortfolioReceipt",
    "TransferReceipt",
    "TransferRegistry",
    "build_portfolio",
    "build_transfer_receipt",
    "canonical_json",
    "content_digest",
    "validate_paper_v2_manifest",
    "verify_digest",
    "verify_portfolio_replay",
]

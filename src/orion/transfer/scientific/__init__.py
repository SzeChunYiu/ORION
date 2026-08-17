"""Scientific mechanic-contract transfer (#286).

Local engineering for a frozen transfer object, fail-closed selector and
toy hostile/ablation fixtures. Not scientific cross-domain evidence.
"""

from .objects import (
    FORBIDDEN_OUTCOME_FIELDS,
    SCHEMA_VERSION,
    ScientificTransferObject,
    schema_digest,
    transfer_object_from_payload,
)
from .selector import SelectorKind, TransferDecision, select_transfer, surface_similarity

__all__ = [
    "FORBIDDEN_OUTCOME_FIELDS",
    "SCHEMA_VERSION",
    "ScientificTransferObject",
    "SelectorKind",
    "TransferDecision",
    "schema_digest",
    "select_transfer",
    "surface_similarity",
    "transfer_object_from_payload",
]

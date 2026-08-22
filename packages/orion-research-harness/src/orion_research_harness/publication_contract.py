"""Publication-facing contract for ORION-Q Paper Q3.

This module is intentionally narrow.  It does not grant scientific authority and it
is not a security certification.  It exposes the exact harness surfaces that the
Q3 systems manuscript is allowed to describe so framework/paper drift becomes a
machine failure instead of a prose discrepancy.

Benchmark semantics such as whether AGREE/DISAGREE are admissible outcomes live in
the frozen benchmark protocol, not in this harness implementation contract.
"""

from __future__ import annotations

import inspect
from typing import Any

from .campaign_protocol import (
    CAMPAIGN_DECISION_SCHEMA,
    CAMPAIGN_STATE_SCHEMA,
    CAMPAIGN_TRANSITION_SCHEMA,
)
from .protocol import REQUEST_SCHEMA, RESULT_SCHEMA, request_id_for
from .recursive_runner import run_problem_recursive
from .workspace import ResearchWorkspace

Q3_HARNESS_PUBLICATION_CONTRACT_ID = "ORION.Q3.HarnessPublicationContract.v1"

Q3_HARNESS_REQUIRED_PROPERTIES = (
    "deterministic_content_derived_request_identity",
    "request_result_digest_binding",
    "create_only_success_receipts",
    "failed_receipt_archival_with_history",
    "successful_invalid_content_archival_with_reason",
    "invalid_reasoner_content_maps_to_host_capability_failed",
    "campaign_state_decision_transition_schemas",
    "campaign_authority_non_escalation",
    "protected_reference_custody_checks",
)


def q3_publication_contract() -> dict[str, Any]:
    """Return the publication-facing contract after validating code bindings.

    The values here describe implemented mechanics, not empirical reliability of
    the scientific benchmark.  The benchmark's one-item outcome and its admissible
    AGREE/PARTIAL/DISAGREE vocabulary remain frozen evidence/protocol properties in
    the paper package rather than properties of this module.
    """

    validate_q3_publication_contract()
    sample_id = request_id_for("publication-contract", "TEST", {"x": 1})
    return {
        "schema": Q3_HARNESS_PUBLICATION_CONTRACT_ID,
        "request_schema": REQUEST_SCHEMA,
        "result_schema": RESULT_SCHEMA,
        "campaign_schemas": (
            CAMPAIGN_STATE_SCHEMA,
            CAMPAIGN_DECISION_SCHEMA,
            CAMPAIGN_TRANSITION_SCHEMA,
        ),
        "required_properties": Q3_HARNESS_REQUIRED_PROPERTIES,
        "sample_request_id_prefix_valid": sample_id.startswith("hostreq:"),
        "grants_scientific_authority": False,
        "grants_novelty_authority": False,
        "grants_security_certification": False,
    }


def validate_q3_publication_contract() -> None:
    """Fail if code no longer implements a surface Q3 describes.

    Some checks deliberately inspect source because the publication statement is
    about a control-path behavior rather than only the existence of a symbol.  A
    future refactor is free to change the implementation, but then this validator
    and the paper must be updated together.
    """

    if not hasattr(ResearchWorkspace, "archive_failed_result"):
        raise RuntimeError("Q3 contract drift: archive_failed_result missing")
    if not hasattr(ResearchWorkspace, "archive_invalid_result"):
        raise RuntimeError("Q3 contract drift: archive_invalid_result missing")

    invalid_source = inspect.getsource(ResearchWorkspace.archive_invalid_result)
    if ".invalid-" not in invalid_source or ".reason.txt" not in invalid_source:
        raise RuntimeError(
            "Q3 contract drift: invalid-content archival no longer preserves the declared audit shape"
        )

    recursive_source = inspect.getsource(run_problem_recursive)
    if "except (ValueError, TypeError, KeyError)" not in recursive_source:
        raise RuntimeError(
            "Q3 contract drift: invalid reasoner content is no longer caught at the declared boundary"
        )
    if '"status": "HOST_CAPABILITY_FAILED"' not in recursive_source:
        raise RuntimeError(
            "Q3 contract drift: invalid reasoner content no longer maps to HOST_CAPABILITY_FAILED"
        )

    first = request_id_for("s", "C", {"a": 1})
    second = request_id_for("s", "C", {"a": 1})
    different = request_id_for("s", "C", {"a": 2})
    if first != second or first == different or not first.startswith("hostreq:"):
        raise RuntimeError("Q3 contract drift: deterministic request identity changed")


__all__ = [
    "Q3_HARNESS_PUBLICATION_CONTRACT_ID",
    "Q3_HARNESS_REQUIRED_PROPERTIES",
    "q3_publication_contract",
    "validate_q3_publication_contract",
]

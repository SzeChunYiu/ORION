"""Publication-facing contract for ORION-Q Paper Q3.

This module is intentionally narrow. It does not grant scientific authority and it
is not a security certification. It exposes the exact harness surfaces that the
Q3 systems manuscript is allowed to describe so framework/paper drift becomes a
machine failure instead of a prose discrepancy.

Benchmark semantics such as whether AGREE/DISAGREE are admissible outcomes live in
the frozen benchmark protocol, not in this harness implementation contract.
"""

from __future__ import annotations

import inspect
from typing import Any

from . import campaign_protocol as _campaign_protocol
from . import campaign_runner as _campaign_runner
from . import workspace as _workspace
from .campaign_protocol import (
    CAMPAIGN_DECISION_SCHEMA,
    CAMPAIGN_STATE_SCHEMA,
    CAMPAIGN_TRANSITION_SCHEMA,
    CampaignDecision,
    CampaignState,
    CampaignTransition,
)
from .protocol import (
    REQUEST_SCHEMA,
    RESULT_SCHEMA,
    CapabilityRequest,
    CapabilityResult,
    request_id_for,
)
from .recursive_runner import run_problem_recursive
from .workspace import ResearchWorkspace

Q3_HARNESS_PUBLICATION_CONTRACT_ID = "ORION.Q3.HarnessPublicationContract.v1"

Q3_HARNESS_REQUIRED_PROPERTIES = (
    "deterministic_content_derived_request_identity",
    "request_result_digest_binding",
    "create_only_receipt_persistence",
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
    the scientific benchmark. The benchmark's one-item outcome and its admissible
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


def _require_source_tokens(obj: Any, *, label: str, tokens: tuple[str, ...]) -> None:
    source = inspect.getsource(obj)
    missing = [token for token in tokens if token not in source]
    if missing:
        raise RuntimeError(f"Q3 contract drift: {label} missing source bindings {missing!r}")


def validate_q3_publication_contract() -> None:
    """Fail if code no longer implements a surface Q3 describes.

    Source-level assertions intentionally bind behavior that would otherwise be
    easy to change while leaving the same public symbol name. A future refactor is
    free to alter the implementation, but then this contract and the paper must be
    updated together.
    """

    # Deterministic, content-derived request identity.
    first = request_id_for("s", "C", {"a": 1})
    second = request_id_for("s", "C", {"a": 1})
    different = request_id_for("s", "C", {"a": 2})
    if first != second or first == different or not first.startswith("hostreq:"):
        raise RuntimeError("Q3 contract drift: deterministic request identity changed")

    # Request/result self-validation and exact request/digest cross-binding.
    _require_source_tokens(
        CapabilityRequest.validate,
        label="CapabilityRequest.validate",
        tokens=("request_id_for", "request_digest", "content_digest", "id mismatch"),
    )
    _require_source_tokens(
        CapabilityResult.validate,
        label="CapabilityResult.validate",
        tokens=(
            "result_digest",
            "content_digest",
            "request id mismatch",
            "request digest mismatch",
        ),
    )

    # Immutable/create-only publication of persisted receipt objects.
    _require_source_tokens(
        _workspace._write_json_create,
        label="workspace._write_json_create",
        tokens=("open(\"x\"", "os.fsync", "os.link", "FileExistsError"),
    )

    if not hasattr(ResearchWorkspace, "archive_failed_result"):
        raise RuntimeError("Q3 contract drift: archive_failed_result missing")
    if not hasattr(ResearchWorkspace, "archive_invalid_result"):
        raise RuntimeError("Q3 contract drift: archive_invalid_result missing")
    _require_source_tokens(
        ResearchWorkspace.archive_failed_result,
        label="archive_failed_result",
        tokens=("if result.success", ".failed-", "os.link", "os.unlink"),
    )
    _require_source_tokens(
        ResearchWorkspace.archive_invalid_result,
        label="archive_invalid_result",
        tokens=(".invalid-", ".reason.txt", "os.link", "os.unlink", "non-empty reason"),
    )

    # Invalid successful model content is an orchestration failure, not evidence.
    recursive_source = inspect.getsource(run_problem_recursive)
    if "except (ValueError, TypeError, KeyError)" not in recursive_source:
        raise RuntimeError(
            "Q3 contract drift: invalid reasoner content is no longer caught at the declared boundary"
        )
    if '"status": "HOST_CAPABILITY_FAILED"' not in recursive_source:
        raise RuntimeError(
            "Q3 contract drift: invalid reasoner content no longer maps to HOST_CAPABILITY_FAILED"
        )

    # Campaign records keep the paper's exact schemas. CampaignState is the
    # persisted/read record and rejects any true authority field on from_dict;
    # decision/transition are serialized from typed in-memory objects and their
    # unsigned payloads always inject the all-false authority surface.
    if not _campaign_protocol._AUTHORITY_FIELDS:
        raise RuntimeError("Q3 contract drift: campaign authority field set is empty")
    for schema in (
        CAMPAIGN_STATE_SCHEMA,
        CAMPAIGN_DECISION_SCHEMA,
        CAMPAIGN_TRANSITION_SCHEMA,
    ):
        if not isinstance(schema, str) or not schema:
            raise RuntimeError("Q3 contract drift: empty campaign schema")
    _require_source_tokens(
        CampaignState.from_dict,
        label="CampaignState.from_dict",
        tokens=("_require_authority_false",),
    )
    _require_source_tokens(
        CampaignState.unsigned,
        label="CampaignState.unsigned",
        tokens=("_authority_false",),
    )
    _require_source_tokens(
        CampaignDecision.unsigned,
        label="CampaignDecision.unsigned",
        tokens=("_authority_false",),
    )
    _require_source_tokens(
        CampaignTransition.unsigned,
        label="CampaignTransition.unsigned",
        tokens=("_authority_false",),
    )

    # Protected reference custody is a declared-surface scan, not general taint
    # tracking. Bind exactly the path/blob/payload/script checks the paper states.
    _require_source_tokens(
        _campaign_runner._protect_unreleased_refs,
        label="campaign protected-reference custody",
        tokens=(
            "declared_read_paths",
            "script.read_text",
            "if ref.path and ref.path in material",
            "if ref.blob and ref.blob in material",
            "if ref.released",
        ),
    )


__all__ = [
    "Q3_HARNESS_PUBLICATION_CONTRACT_ID",
    "Q3_HARNESS_REQUIRED_PROPERTIES",
    "q3_publication_contract",
    "validate_q3_publication_contract",
]

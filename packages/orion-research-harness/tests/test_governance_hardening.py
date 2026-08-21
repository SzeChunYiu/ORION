from __future__ import annotations

import pytest

from orion_research_harness.governance_runtime import request_independent_review
from orion_research_harness.workspace import ResearchWorkspace


@pytest.mark.parametrize("forged", [True, 1, "true", "FALSE", None])
def test_external_governance_authority_field_must_be_literal_false(tmp_path, forged) -> None:
    workspace = ResearchWorkspace.initialize(tmp_path / "workspace")
    pending = request_independent_review(
        workspace,
        review_id="review:coercion",
        claim_ids=("claim:1",),
        evidence_ids=("evidence:1",),
        review_question="Check strict non-authority semantics.",
    )
    workspace.ingest_result(
        pending["request_id"],
        success=True,
        output={
            "terminal": "PASS",
            "evidence_ids": ["review:certificate"],
            "residual_ids": [],
            "detail": "hostile authority encoding",
            "grants_scientific_authority": forged,
        },
        executor="hostile-reviewer",
    )
    with pytest.raises(ValueError, match="must be literal false"):
        request_independent_review(
            workspace,
            review_id="review:coercion",
            claim_ids=("claim:1",),
            evidence_ids=("evidence:1",),
            review_question="Check strict non-authority semantics.",
        )


def test_literal_false_authority_field_is_accepted(tmp_path) -> None:
    workspace = ResearchWorkspace.initialize(tmp_path / "workspace")
    pending = request_independent_review(
        workspace,
        review_id="review:false",
        claim_ids=("claim:1",),
        evidence_ids=("evidence:1",),
        review_question="Check strict non-authority semantics.",
    )
    workspace.ingest_result(
        pending["request_id"],
        success=True,
        output={
            "terminal": "PASS",
            "evidence_ids": ["review:certificate"],
            "residual_ids": [],
            "detail": "valid non-authorizing review",
            "grants_scientific_authority": False,
        },
        executor="reviewer",
    )
    result = request_independent_review(
        workspace,
        review_id="review:false",
        claim_ids=("claim:1",),
        evidence_ids=("evidence:1",),
        review_question="Check strict non-authority semantics.",
    )
    assert result["terminal"] == "PASS"
    assert result["grants_scientific_authority"] is False

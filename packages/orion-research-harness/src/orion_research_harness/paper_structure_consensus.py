from __future__ import annotations

import json
from pathlib import Path
from typing import Mapping, Sequence
from uuid import uuid4

from orion.providers.llm.base import LLMRequest

from . import paper_structure as _ps
from .broker import (
    BrokerLLMProvider,
    CapabilityBroker,
    HostCapabilityFailed,
    HostCapabilityRequired,
)
from .protocol import content_digest
from .workspace import ResearchWorkspace


_EXTRACTION_MODE = "TWO_LANE_CONSENSUS_V3"
_LANES = ("lane_a", "lane_b")


def _claim_from_raw(
    *,
    document: _ps.SourceDocument,
    chunk: _ps.SourceChunk,
    raw: Mapping[str, object],
) -> _ps.SupportedClaim:
    coordinate = raw.get("coordinate")
    if not isinstance(coordinate, str) or coordinate not in _ps._ALLOWED_COORDINATES:
        raise ValueError(f"unsupported paper structure coordinate: {coordinate!r}")
    quote = raw.get("quote")
    if not isinstance(quote, str) or not quote:
        raise TypeError("paper structure claim.quote must be non-empty")
    value = _ps._parse_claim_value(coordinate, raw.get("value"))
    start, end = _ps._locate_quote(chunk, quote)
    span_digest = _ps._sha256_text(document.text[start:end])
    base = {
        "coordinate": coordinate,
        "value": value,
        "quote": quote,
        "start": start,
        "end": end,
        "span_digest": span_digest,
        "source_digest": document.source_digest,
    }
    return _ps.SupportedClaim(
        claim_id="support:" + content_digest(base),
        coordinate=coordinate,
        value=value,
        quote=quote,
        start=start,
        end=end,
        span_digest=span_digest,
    )


def _extract_lane_chunk_claims(
    workspace: ResearchWorkspace,
    *,
    document: _ps.SourceDocument,
    method_id: str,
    chunk: _ps.SourceChunk,
    lane_id: str,
) -> tuple[_ps.SupportedClaim, ...]:
    if lane_id not in _LANES:
        raise ValueError(f"unknown proposer lane: {lane_id}")
    task = f"paper_method_structure_extract_v2_{lane_id}"
    llm = BrokerLLMProvider(CapabilityBroker(workspace))
    response = llm.complete(
        LLMRequest(
            task=task,
            system=(
                f"You are ORION paper method-structure proposer {lane_id}. "
                "Extract only source-local scientific method structure explicitly supported by the supplied chunk. "
                "Every claim requires an exact verbatim quote. Do not infer missing coordinates by analogy or common knowledge. "
                "For sequence-valued coordinates emit one atomic claim per value; dependencies are [from_mechanic,to_mechanic]. "
                "This proposer lane grants no scientific, novelty, method-fibre, adoption, promotion, or task-stop authority."
            ),
            user=json.dumps(
                {
                    "proposal_lane": lane_id,
                    "source_id": document.source_id,
                    "source_digest": document.source_digest,
                    "text_digest": document.text_digest,
                    "method_id": method_id,
                    "chunk_id": chunk.chunk_id,
                    "chunk_start": chunk.start,
                    "chunk_text": chunk.text,
                    "allowed_coordinates": sorted(_ps._ALLOWED_COORDINATES),
                },
                sort_keys=True,
            ),
            response_schema=(
                '{"claims":[{"coordinate":"mechanics","value":"...","quote":"exact verbatim source text"},'
                '{"coordinate":"dependencies","value":["mechanic_a","mechanic_b"],"quote":"exact verbatim source text"}]}'
            ),
        )
    )
    try:
        payload = json.loads(response.content)
    except json.JSONDecodeError as exc:
        raise ValueError(f"{lane_id} paper structure proposer returned invalid JSON") from exc
    if not isinstance(payload, Mapping) or not isinstance(payload.get("claims", []), list):
        raise TypeError(f"{lane_id} proposer must return an object containing claims")
    claims: dict[str, _ps.SupportedClaim] = {}
    for raw in payload.get("claims", []):
        if not isinstance(raw, Mapping):
            raise TypeError("paper structure claim must be an object")
        claim = _claim_from_raw(document=document, chunk=chunk, raw=raw)
        claims[claim.claim_id] = claim
    return tuple(claims[key] for key in sorted(claims))


def _merge_lane_claims(
    lane_claims: Mapping[str, Sequence[_ps.SupportedClaim]],
) -> tuple[
    tuple[_ps.SupportedClaim, ...],
    dict[str, tuple[str, ...]],
    tuple[str, ...],
]:
    merged: dict[str, _ps.SupportedClaim] = {}
    lanes_by_claim: dict[str, set[str]] = {}
    scalar_values: dict[str, set[str]] = {key: set() for key in _ps._SCALAR_COORDINATES}
    for lane_id, claims in lane_claims.items():
        for claim in claims:
            merged[claim.claim_id] = claim
            lanes_by_claim.setdefault(claim.claim_id, set()).add(lane_id)
            if claim.coordinate in scalar_values and isinstance(claim.value, str):
                scalar_values[claim.coordinate].add(claim.value)
    conflicts = tuple(
        sorted(coordinate for coordinate, values in scalar_values.items() if len(values) > 1)
    )
    return (
        tuple(merged[key] for key in sorted(merged)),
        {key: tuple(sorted(values)) for key, values in lanes_by_claim.items()},
        conflicts,
    )


def _enriched_claim_dict(
    claim: _ps.SupportedClaim,
    lanes_by_claim: Mapping[str, tuple[str, ...]],
) -> dict[str, object]:
    return {
        **claim.as_dict(),
        "proposer_lane_ids": list(lanes_by_claim.get(claim.claim_id, ())),
    }


def _coverage_review(
    workspace: ResearchWorkspace,
    *,
    document: _ps.SourceDocument,
    method_id: str,
    claims: Sequence[_ps.SupportedClaim],
    lanes_by_claim: Mapping[str, tuple[str, ...]],
) -> dict[str, object]:
    broker = CapabilityBroker(workspace)
    request, result = broker.require_result(
        "INDEPENDENT_REVIEW",
        {
            "review_kind": "PAPER_METHOD_STRUCTURE_COVERAGE_V3",
            "source": {
                "source_id": document.source_id,
                "source_path": document.source_path,
                "source_digest": document.source_digest,
                "text_digest": document.text_digest,
            },
            "method_id": method_id,
            "merged_support_claims": [
                _enriched_claim_dict(item, lanes_by_claim) for item in claims
            ],
            "allowed_coordinates": sorted(_ps._ALLOWED_COORDINATES),
            "instruction": (
                "Independently review source coverage, not scientific truth. Return {passed, missed_claims, reason}. "
                "Every missed claim must use the same {coordinate,value,quote} schema and quote exact source text. "
                "passed=true requires missed_claims=[]; do not infer unsupported coordinates."
            ),
        },
    )
    try:
        output = result.output
        if not isinstance(output, Mapping):
            raise TypeError("INDEPENDENT_REVIEW output must be an object")
        passed = output.get("passed")
        if not isinstance(passed, bool):
            raise TypeError("INDEPENDENT_REVIEW.passed must be boolean")
        raw_missed = output.get("missed_claims", [])
        if not isinstance(raw_missed, list):
            raise TypeError("INDEPENDENT_REVIEW.missed_claims must be an array")
        reason = output.get("reason", "")
        if not isinstance(reason, str):
            raise TypeError("INDEPENDENT_REVIEW.reason must be a string")
        whole = _ps.SourceChunk("coverage:whole-source", 0, len(document.text), document.text)
        missed: list[_ps.SupportedClaim] = []
        for raw in raw_missed:
            if not isinstance(raw, Mapping):
                raise TypeError("coverage missed claim must be an object")
            missed.append(_claim_from_raw(document=document, chunk=whole, raw=raw))
        if passed and missed:
            raise ValueError("passing coverage review cannot report missed claims")
        return {
            "passed": passed,
            "missed_claims": [item.as_dict() for item in missed],
            "reason": reason,
            "executor": result.executor,
            "request_id": request.request_id,
        }
    except Exception as exc:
        raise broker.invalid_result(request, result, exc) from exc


def _authority_false() -> dict[str, bool]:
    return {
        "grants_scientific_authority": False,
        "grants_novelty_authority": False,
        "grants_method_fibre_authority": False,
        "grants_promotion_authority": False,
        "grants_global_task_stop_authority": False,
    }


def run_paper_structure_consensus(
    workspace: ResearchWorkspace,
    *,
    source_path: str,
    method_id: str,
    source_id: str,
    source_version: str,
    chunk_size: int = 12000,
    chunk_overlap: int = 800,
) -> dict[str, object]:
    if not isinstance(method_id, str) or not method_id.strip():
        raise ValueError("method_id is required")
    try:
        document = _ps.load_source_document(
            workspace,
            source_path=source_path,
            source_id=source_id,
            source_version=source_version,
        )
        chunks = _ps._chunks(document.text, chunk_size=chunk_size, overlap=chunk_overlap)
        lane_claims: dict[str, list[_ps.SupportedClaim]] = {lane: [] for lane in _LANES}
        for lane in _LANES:
            for chunk in chunks:
                lane_claims[lane].extend(
                    _extract_lane_chunk_claims(
                        workspace,
                        document=document,
                        method_id=method_id,
                        chunk=chunk,
                        lane_id=lane,
                    )
                )
        merged, lanes_by_claim, conflicts = _merge_lane_claims(lane_claims)
        if conflicts:
            return {
                "schema": "ORION.HarnessPaperStructureConsensusOutcome.v3",
                "status": "CANNOT_CHECK_PROPOSER_DISAGREEMENT",
                "method_id": method_id,
                "extraction_mode": _EXTRACTION_MODE,
                "conflicting_coordinates": list(conflicts),
                "support_claims": [
                    _enriched_claim_dict(item, lanes_by_claim) for item in merged
                ],
                **_authority_false(),
            }
        if not merged:
            raise ValueError("no source-supported method structure claims were extracted")

        coverage = _coverage_review(
            workspace,
            document=document,
            method_id=method_id,
            claims=merged,
            lanes_by_claim=lanes_by_claim,
        )
        if coverage["passed"] is not True or coverage["missed_claims"]:
            run_id = "paper-consensus-coverage:" + uuid4().hex
            record = {
                "schema": "ORION.HarnessPaperStructureConsensusRun.v3",
                "run_id": run_id,
                "status": "CANNOT_CHECK_COVERAGE_GAP",
                "method_id": method_id,
                "extraction_mode": _EXTRACTION_MODE,
                "source": {
                    "source_id": document.source_id,
                    "source_version": document.source_version,
                    "source_path": document.source_path,
                    "source_digest": document.source_digest,
                    "text_digest": document.text_digest,
                },
                "support_claims": [
                    _enriched_claim_dict(item, lanes_by_claim) for item in merged
                ],
                "coverage_review": coverage,
                **_authority_false(),
            }
            workspace.save_run(run_id, record)
            return record

        realization, projection, unknown = _ps._canonical_objects(
            document,
            method_id=method_id,
            claims=merged,
        )
        verification = _ps._verify_extraction(
            workspace,
            document=document,
            realization=realization,
            projection=projection,
            claims=merged,
        )
    except HostCapabilityRequired as pending:
        return {
            "schema": "ORION.HarnessPaperStructureConsensusOutcome.v3",
            "status": "PENDING_CAPABILITY",
            "method_id": method_id,
            "extraction_mode": _EXTRACTION_MODE,
            "request": pending.request.as_dict(),
            **_authority_false(),
        }
    except HostCapabilityFailed as failed:
        return {
            "schema": "ORION.HarnessPaperStructureConsensusOutcome.v3",
            "status": "HOST_CAPABILITY_FAILED",
            "method_id": method_id,
            "extraction_mode": _EXTRACTION_MODE,
            "request": failed.request.as_dict(),
            "result": failed.result.as_dict(),
            "error": failed.detail,
            **_authority_false(),
        }
    except (ValueError, TypeError, KeyError) as exc:
        return {
            "schema": "ORION.HarnessPaperStructureConsensusOutcome.v3",
            "status": "HOST_CAPABILITY_FAILED",
            "method_id": method_id,
            "extraction_mode": _EXTRACTION_MODE,
            "error": f"consensus paper structure content invalid: {exc}",
            **_authority_false(),
        }

    status = "COMPLETE" if verification["passed"] else "CANNOT_CHECK_SOURCE_SUPPORT"
    run_id = "paper-structure-consensus:" + uuid4().hex
    record = {
        "schema": "ORION.HarnessPaperStructureConsensusRun.v3",
        "run_id": run_id,
        "status": status,
        "method_id": method_id,
        "extraction_mode": _EXTRACTION_MODE,
        "source": {
            "source_id": document.source_id,
            "source_version": document.source_version,
            "source_path": document.source_path,
            "source_digest": document.source_digest,
            "text_digest": document.text_digest,
        },
        "method_realization": _ps._realization_payload(realization),
        "method_structure_projection": _ps._projection_payload(projection),
        "support_claims": [
            _enriched_claim_dict(item, lanes_by_claim) for item in merged
        ],
        "unknown_coordinates": list(unknown),
        "coverage_review": coverage,
        "verification": verification,
        **_authority_false(),
    }
    workspace.save_run(run_id, record)
    return record


# Install as an additive attribute on the existing paper_structure module so
# `from orion_research_harness.paper_structure import run_paper_structure_consensus`
# works without changing the already-green V1 source file.
_ps.run_paper_structure_consensus = run_paper_structure_consensus


__all__ = [
    "run_paper_structure_consensus",
    "_merge_lane_claims",
]

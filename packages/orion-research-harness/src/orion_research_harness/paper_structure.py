from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Mapping, Sequence
from uuid import uuid4

from orion.providers.llm.base import LLMRequest
from orion.transfer.v2.p1_method_realization import (
    COORDINATES,
    build_method_realization,
    completeness_errors,
)
from orion.transfer.v2.p3_method_projection import build_projection

from .broker import (
    BrokerLLMProvider,
    CapabilityBroker,
    HostCapabilityFailed,
    HostCapabilityRequired,
)
from .protocol import content_digest
from .workspace import ResearchWorkspace

_EXTRA_COORDINATES = {
    "initial_obstruction",
    "representation_changes",
    "auxiliary_objects",
    "author_rationale",
}
_ALLOWED_COORDINATES = set(COORDINATES) | _EXTRA_COORDINATES
_SEQUENCE_COORDINATES = {
    "preconditions",
    "assumptions",
    "resources",
    "mechanics",
    "invariants",
    "effects",
    "failure_modes",
    "lineage",
    "initial_obstruction",
    "representation_changes",
    "auxiliary_objects",
    "author_rationale",
}
_SCALAR_COORDINATES = {
    "target_role",
    "representation_in",
    "representation_out",
    "progress_measure",
    "terminal_condition",
    "reconstruction_map",
}


@dataclass(frozen=True)
class SourceDocument:
    source_id: str
    source_version: str
    source_path: str
    source_digest: str
    text: str
    text_digest: str


@dataclass(frozen=True)
class SourceChunk:
    chunk_id: str
    start: int
    end: int
    text: str


@dataclass(frozen=True)
class SupportedClaim:
    claim_id: str
    coordinate: str
    value: object
    quote: str
    start: int
    end: int
    span_digest: str

    def as_dict(self) -> dict[str, object]:
        return {
            "claim_id": self.claim_id,
            "coordinate": self.coordinate,
            "value": self.value,
            "quote": self.quote,
            "start": self.start,
            "end": self.end,
            "span_digest": self.span_digest,
        }


def _sha256_bytes(raw: bytes) -> str:
    return "sha256:" + hashlib.sha256(raw).hexdigest()


def _sha256_text(text: str) -> str:
    return _sha256_bytes(text.encode("utf-8"))


def _project_path(workspace: ResearchWorkspace, source_path: str) -> Path:
    if not isinstance(source_path, str) or not source_path.strip():
        raise ValueError("source_path is required")
    candidate = (workspace.project_root / source_path).expanduser().resolve()
    try:
        candidate.relative_to(workspace.project_root)
    except ValueError as exc:
        raise PermissionError("paper source is outside project root") from exc
    if not candidate.is_file():
        raise FileNotFoundError(candidate)
    return candidate


def _document_text_from_pdf(
    workspace: ResearchWorkspace,
    *,
    path: Path,
    raw: bytes,
    source_digest: str,
) -> str:
    broker = CapabilityBroker(workspace)
    request, result = broker.require_result(
        "DOCUMENT_TEXT_EXTRACT",
        {
            "project_relative_path": str(path.relative_to(workspace.project_root)),
            "source_digest": source_digest,
            "byte_length": len(raw),
            "instruction": (
                "Extract searchable text from this exact PDF without semantic summarization. "
                "Return {text, source_digest}. source_digest must equal the request digest. "
                "Do not invent or normalize scientific content beyond text extraction."
            ),
        },
    )
    try:
        output = result.output
        if not isinstance(output, Mapping):
            raise TypeError("DOCUMENT_TEXT_EXTRACT output must be an object")
        returned_digest = output.get("source_digest")
        if returned_digest != source_digest:
            raise ValueError("DOCUMENT_TEXT_EXTRACT source digest mismatch")
        text = output.get("text")
        if not isinstance(text, str) or not text.strip():
            raise TypeError("DOCUMENT_TEXT_EXTRACT.text must be non-empty")
        return text
    except Exception as exc:
        raise broker.invalid_result(request, result, exc) from exc


def load_source_document(
    workspace: ResearchWorkspace,
    *,
    source_path: str,
    source_id: str,
    source_version: str,
) -> SourceDocument:
    if not source_id.strip() or not source_version.strip():
        raise ValueError("source_id and source_version are required")
    path = _project_path(workspace, source_path)
    raw = path.read_bytes()
    source_digest = _sha256_bytes(raw)
    if path.suffix.casefold() == ".pdf":
        text = _document_text_from_pdf(
            workspace, path=path, raw=raw, source_digest=source_digest
        )
    else:
        try:
            text = raw.decode("utf-8")
        except UnicodeDecodeError as exc:
            raise ValueError(
                "non-PDF paper sources must be UTF-8 text; use a host document-text extractor otherwise"
            ) from exc
        if not text.strip():
            raise ValueError("paper source text is empty")
    return SourceDocument(
        source_id=source_id,
        source_version=source_version,
        source_path=str(path.relative_to(workspace.project_root)),
        source_digest=source_digest,
        text=text,
        text_digest=_sha256_text(text),
    )


def _chunks(text: str, *, chunk_size: int, overlap: int) -> tuple[SourceChunk, ...]:
    if chunk_size < 1000:
        raise ValueError("chunk_size must be at least 1000")
    if overlap < 0 or overlap >= chunk_size:
        raise ValueError("chunk overlap must satisfy 0 <= overlap < chunk_size")
    if len(text) <= chunk_size:
        return (SourceChunk("chunk:0000", 0, len(text), text),)
    rows: list[SourceChunk] = []
    start = 0
    index = 0
    while start < len(text):
        target_end = min(len(text), start + chunk_size)
        end = target_end
        if target_end < len(text):
            newline = text.rfind("\n", start + chunk_size // 2, target_end)
            if newline > start:
                end = newline + 1
        rows.append(SourceChunk(f"chunk:{index:04d}", start, end, text[start:end]))
        if end >= len(text):
            break
        start = max(start + 1, end - overlap)
        index += 1
    return tuple(rows)


def _parse_claim_value(coordinate: str, raw: object) -> object:
    if coordinate == "dependencies":
        if not isinstance(raw, (list, tuple)) or len(raw) != 2:
            raise TypeError("dependencies claim value must be a two-item array")
        left, right = raw
        if not isinstance(left, str) or not left.strip() or not isinstance(right, str) or not right.strip():
            raise TypeError("dependency endpoints must be non-empty strings")
        return [left.strip(), right.strip()]
    if not isinstance(raw, str) or not raw.strip():
        raise TypeError(f"{coordinate} claim value must be a non-empty string")
    return raw.strip()


def _locate_quote(chunk: SourceChunk, quote: str) -> tuple[int, int]:
    local = chunk.text.find(quote)
    if local < 0:
        raise ValueError(
            f"extraction quote does not occur verbatim in source chunk {chunk.chunk_id}: {quote!r}"
        )
    start = chunk.start + local
    return start, start + len(quote)


def _extract_chunk_claims(
    workspace: ResearchWorkspace,
    *,
    document: SourceDocument,
    method_id: str,
    chunk: SourceChunk,
) -> tuple[SupportedClaim, ...]:
    llm = BrokerLLMProvider(CapabilityBroker(workspace))
    response = llm.complete(
        LLMRequest(
            task="paper_method_structure_extract_v1",
            system=(
                "You extract source-local scientific method structure for ORION. "
                "Return only claims explicitly supported by the supplied source chunk. "
                "Every claim must include an exact verbatim quote from the chunk. "
                "Do not infer missing coordinates by analogy. Do not grant method-fibre, scientific, novelty, or adoption authority. "
                "For sequence-valued coordinates emit one claim per atomic value. For dependencies, value is [from_mechanic,to_mechanic]."
            ),
            user=json.dumps(
                {
                    "source_id": document.source_id,
                    "source_digest": document.source_digest,
                    "text_digest": document.text_digest,
                    "method_id": method_id,
                    "chunk_id": chunk.chunk_id,
                    "chunk_start": chunk.start,
                    "chunk_text": chunk.text,
                    "allowed_coordinates": sorted(_ALLOWED_COORDINATES),
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
        raise ValueError("paper structure extractor returned invalid JSON") from exc
    if not isinstance(payload, Mapping) or not isinstance(payload.get("claims", []), list):
        raise TypeError("paper structure extractor must return an object containing claims")
    claims: list[SupportedClaim] = []
    for raw in payload.get("claims", []):
        if not isinstance(raw, Mapping):
            raise TypeError("paper structure claim must be an object")
        coordinate = raw.get("coordinate")
        if not isinstance(coordinate, str) or coordinate not in _ALLOWED_COORDINATES:
            raise ValueError(f"unsupported paper structure coordinate: {coordinate!r}")
        quote = raw.get("quote")
        if not isinstance(quote, str) or not quote:
            raise TypeError("paper structure claim.quote must be non-empty")
        value = _parse_claim_value(coordinate, raw.get("value"))
        start, end = _locate_quote(chunk, quote)
        span_digest = _sha256_text(document.text[start:end])
        base = {
            "coordinate": coordinate,
            "value": value,
            "quote": quote,
            "start": start,
            "end": end,
            "span_digest": span_digest,
            "source_digest": document.source_digest,
        }
        claims.append(
            SupportedClaim(
                claim_id="support:" + content_digest(base),
                coordinate=coordinate,
                value=value,
                quote=quote,
                start=start,
                end=end,
                span_digest=span_digest,
            )
        )
    unique: dict[str, SupportedClaim] = {}
    for claim in claims:
        unique[claim.claim_id] = claim
    return tuple(unique[key] for key in sorted(unique))


def _claims_by_coordinate(
    claims: Sequence[SupportedClaim],
) -> dict[str, tuple[SupportedClaim, ...]]:
    rows: dict[str, list[SupportedClaim]] = {}
    for claim in claims:
        rows.setdefault(claim.coordinate, []).append(claim)
    return {
        key: tuple(sorted(value, key=lambda item: (item.start, item.end, item.claim_id)))
        for key, value in rows.items()
    }


def _sequence_values(rows: Mapping[str, tuple[SupportedClaim, ...]], coordinate: str) -> tuple[str, ...]:
    values = {
        str(item.value)
        for item in rows.get(coordinate, ())
        if isinstance(item.value, str) and str(item.value).strip()
    }
    return tuple(sorted(values))


def _scalar_value(
    rows: Mapping[str, tuple[SupportedClaim, ...]], coordinate: str
) -> tuple[str | None, bool]:
    values = {
        str(item.value)
        for item in rows.get(coordinate, ())
        if isinstance(item.value, str) and str(item.value).strip()
    }
    if len(values) == 1:
        return next(iter(values)), False
    if len(values) > 1:
        return None, True
    return None, False


def _canonical_objects(
    document: SourceDocument,
    *,
    method_id: str,
    claims: Sequence[SupportedClaim],
) -> tuple[object, object, tuple[str, ...]]:
    rows = _claims_by_coordinate(claims)
    scalar_values: dict[str, str | None] = {}
    conflicts: set[str] = set()
    for coordinate in _SCALAR_COORDINATES:
        value, conflict = _scalar_value(rows, coordinate)
        scalar_values[coordinate] = value
        if conflict:
            conflicts.add(coordinate)

    dependencies = {
        (str(item.value[0]), str(item.value[1]))
        for item in rows.get("dependencies", ())
        if isinstance(item.value, list) and len(item.value) == 2
    }
    mechanics = _sequence_values(rows, "mechanics")
    valid_dependencies = tuple(
        sorted(edge for edge in dependencies if edge[0] in mechanics and edge[1] in mechanics)
    )
    if dependencies and len(valid_dependencies) != len(dependencies):
        conflicts.add("dependencies")

    framework_known = {"authority_boundary", "lineage"}
    populated = {
        coordinate
        for coordinate in COORDINATES
        if (
            (coordinate in _SCALAR_COORDINATES and scalar_values.get(coordinate) is not None)
            or (coordinate in _SEQUENCE_COORDINATES and _sequence_values(rows, coordinate))
            or (coordinate == "dependencies" and valid_dependencies)
        )
    } | framework_known
    unknown = tuple(sorted((set(COORDINATES) - populated) | conflicts))

    explicit_lineage = _sequence_values(rows, "lineage")
    lineage = tuple(sorted(set(explicit_lineage) | {f"source:{document.source_id}:{document.source_digest}"}))
    realization = build_method_realization(
        method_id=method_id,
        source_digest=document.source_digest,
        source_version=document.source_version,
        target_role=scalar_values["target_role"],
        preconditions=_sequence_values(rows, "preconditions"),
        assumptions=_sequence_values(rows, "assumptions"),
        resources=_sequence_values(rows, "resources"),
        representation_in=scalar_values["representation_in"],
        representation_out=scalar_values["representation_out"],
        mechanics=mechanics,
        dependencies=valid_dependencies,
        invariants=_sequence_values(rows, "invariants"),
        progress_measure=scalar_values["progress_measure"],
        effects=_sequence_values(rows, "effects"),
        terminal_condition=scalar_values["terminal_condition"],
        reconstruction_map=scalar_values["reconstruction_map"],
        failure_modes=_sequence_values(rows, "failure_modes"),
        lineage=lineage,
        authority_boundary="REPRESENTATION_ONLY",
        unknown_coordinates=unknown,
    )
    span_digests = tuple(sorted({item.span_digest for item in claims}))
    if not span_digests:
        raise ValueError("no source-supported method structure claims were extracted")
    projection = build_projection(
        realization,
        projection_id=f"projection:{method_id}:{content_digest({'source': document.source_digest, 'method': method_id})[:16]}",
        source_id=document.source_id,
        source_span_digests=span_digests,
        initial_obstruction=_sequence_values(rows, "initial_obstruction"),
        representation_changes=_sequence_values(rows, "representation_changes"),
        auxiliary_objects=_sequence_values(rows, "auxiliary_objects"),
        author_rationale=_sequence_values(rows, "author_rationale"),
        unknown_coordinates=unknown,
    )
    return realization, projection, unknown


def _verify_extraction(
    workspace: ResearchWorkspace,
    *,
    document: SourceDocument,
    realization: object,
    projection: object,
    claims: Sequence[SupportedClaim],
) -> dict[str, object]:
    broker = CapabilityBroker(workspace)
    request, result = broker.require_result(
        "VERIFY_EVIDENCE",
        {
            "verification_kind": "PAPER_METHOD_STRUCTURE_SOURCE_SUPPORT_V1",
            "source": {
                "source_id": document.source_id,
                "source_path": document.source_path,
                "source_digest": document.source_digest,
                "text_digest": document.text_digest,
            },
            "method_realization": realization.unsigned(),
            "method_realization_digest": realization.digest,
            "method_structure_projection": projection.unsigned(),
            "method_structure_projection_digest": projection.digest,
            "support_claims": [item.as_dict() for item in claims],
            "instruction": (
                "Independently verify that every populated scientific method coordinate is supported by the cited exact source spans. "
                "Fail closed for semantic overreach, missing support, or invented rationale. "
                "Return {passed, certificate_ids, reason}; PASS requires at least one certificate id."
            ),
        },
    )
    try:
        output = result.output
        if not isinstance(output, Mapping):
            raise TypeError("VERIFY_EVIDENCE output must be an object")
        passed = output.get("passed")
        if not isinstance(passed, bool):
            raise TypeError("VERIFY_EVIDENCE.passed must be a boolean")
        raw_ids = output.get("certificate_ids", ())
        if isinstance(raw_ids, (str, bytes)) or not isinstance(raw_ids, (list, tuple)):
            raise TypeError("VERIFY_EVIDENCE.certificate_ids must be an array")
        certificate_ids = tuple(str(item) for item in raw_ids if isinstance(item, str) and item.strip())
        if len(certificate_ids) != len(raw_ids):
            raise TypeError("VERIFY_EVIDENCE certificate ids must be non-empty strings")
        if passed and not certificate_ids:
            raise ValueError("passing structure verification requires a certificate id")
        reason = output.get("reason", "")
        if not isinstance(reason, str):
            raise TypeError("VERIFY_EVIDENCE.reason must be a string")
        return {
            "passed": passed,
            "certificate_ids": list(certificate_ids),
            "reason": reason,
            "executor": result.executor,
            "request_id": request.request_id,
        }
    except Exception as exc:
        raise broker.invalid_result(request, result, exc) from exc


def _realization_payload(realization: object) -> dict[str, object]:
    return {
        "payload": realization.unsigned(),
        "digest": realization.digest,
        "state": realization.state.value,
        "completeness_errors": list(completeness_errors(realization)),
    }


def _projection_payload(projection: object) -> dict[str, object]:
    return {
        "payload": projection.unsigned(),
        "digest": projection.digest,
        "state": projection.state.value,
    }


def run_paper_structure(
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
        document = load_source_document(
            workspace,
            source_path=source_path,
            source_id=source_id,
            source_version=source_version,
        )
        claims: list[SupportedClaim] = []
        for chunk in _chunks(document.text, chunk_size=chunk_size, overlap=chunk_overlap):
            claims.extend(
                _extract_chunk_claims(
                    workspace,
                    document=document,
                    method_id=method_id,
                    chunk=chunk,
                )
            )
        unique = {item.claim_id: item for item in claims}
        ordered_claims = tuple(unique[key] for key in sorted(unique))
        realization, projection, unknown = _canonical_objects(
            document, method_id=method_id, claims=ordered_claims
        )
        verification = _verify_extraction(
            workspace,
            document=document,
            realization=realization,
            projection=projection,
            claims=ordered_claims,
        )
    except HostCapabilityRequired as pending:
        return {
            "schema": "ORION.HarnessPaperStructureOutcome.v1",
            "status": "PENDING_CAPABILITY",
            "method_id": method_id,
            "request": pending.request.as_dict(),
            "grants_scientific_authority": False,
            "grants_novelty_authority": False,
            "grants_method_fibre_authority": False,
        }
    except HostCapabilityFailed as failed:
        return {
            "schema": "ORION.HarnessPaperStructureOutcome.v1",
            "status": "HOST_CAPABILITY_FAILED",
            "method_id": method_id,
            "request": failed.request.as_dict(),
            "result": failed.result.as_dict(),
            "error": failed.detail,
            "grants_scientific_authority": False,
            "grants_novelty_authority": False,
            "grants_method_fibre_authority": False,
        }
    except (ValueError, TypeError, KeyError) as exc:
        return {
            "schema": "ORION.HarnessPaperStructureOutcome.v1",
            "status": "HOST_CAPABILITY_FAILED",
            "method_id": method_id,
            "error": f"paper structure content invalid: {exc}",
            "grants_scientific_authority": False,
            "grants_novelty_authority": False,
            "grants_method_fibre_authority": False,
        }

    status = "COMPLETE" if verification["passed"] else "CANNOT_CHECK_SOURCE_SUPPORT"
    run_id = "paper-structure:" + uuid4().hex
    record = {
        "schema": "ORION.HarnessPaperStructureRun.v1",
        "run_id": run_id,
        "status": status,
        "source": {
            "source_id": document.source_id,
            "source_version": document.source_version,
            "source_path": document.source_path,
            "source_digest": document.source_digest,
            "text_digest": document.text_digest,
        },
        "method_realization": _realization_payload(realization),
        "method_structure_projection": _projection_payload(projection),
        "support_claims": [item.as_dict() for item in ordered_claims],
        "unknown_coordinates": list(unknown),
        "verification": verification,
        "grants_scientific_authority": False,
        "grants_novelty_authority": False,
        "grants_method_fibre_authority": False,
        "grants_promotion_authority": False,
    }
    workspace.save_run(run_id, record)
    return record


__all__ = [
    "SourceDocument",
    "SupportedClaim",
    "load_source_document",
    "run_paper_structure",
]

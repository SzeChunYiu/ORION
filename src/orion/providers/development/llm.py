from __future__ import annotations

import hashlib
import json

from orion.providers.llm.base import LLMProvider, LLMRequest

from .artifacts import DevelopmentArtifactStore
from .base import DevelopmentChangeProposal, DevelopmentChangeRequest


_RESPONSE_SCHEMA = """{
  "type": "object",
  "required": ["touched_paths", "patch", "rationale", "expected_effects", "test_plan", "falsifier"],
  "properties": {
    "touched_paths": {"type": "array", "items": {"type": "string"}, "minItems": 1},
    "patch": {"type": "string", "minLength": 1},
    "rationale": {"type": "string", "minLength": 1},
    "expected_effects": {"type": "array", "items": {"type": "string"}, "minItems": 1},
    "test_plan": {"type": "array", "items": {"type": "string"}, "minItems": 1},
    "falsifier": {"type": "string", "minLength": 1}
  },
  "additionalProperties": false
}"""


def _string_tuple(value: object, *, field: str) -> tuple[str, ...]:
    if not isinstance(value, list) or not value:
        raise ValueError(f"LLM development response {field} must be a non-empty list")
    result = tuple(item for item in value if isinstance(item, str) and item.strip())
    if len(result) != len(value):
        raise ValueError(f"LLM development response {field} must contain non-empty strings")
    return result


class LLMDevelopmentChangeProvider:
    """Use an LLM as a coding proposal worker, never as development authority."""

    def __init__(self, llm: LLMProvider, artifact_store: DevelopmentArtifactStore) -> None:
        self._llm = llm
        self._artifact_store = artifact_store

    def propose(self, request: DevelopmentChangeRequest) -> DevelopmentChangeProposal:
        protected_paths = "\n".join(f"- {item}" for item in request.protected_path_prefixes)
        constraints = "\n".join(f"- {item}" for item in request.protected_constraints)
        tests = "\n".join(f"- {item}" for item in request.required_tests)
        causal_context = ""
        if request.observed_failure_bound:
            causal_context = (
                "Frozen observed-failure binding (do not reinterpret after candidate outcome):\n"
                f"- development issue: {request.development_issue_id}\n"
                f"- observed failure artifact: {request.observed_failure_artifact_hash}\n"
                f"- competing causes: {request.candidate_cause_ids}\n"
                f"- supported cause: {request.supported_cause_id}\n"
                f"- discriminator artifact: {request.discriminator_artifact_hash}\n"
                f"- discriminator evidence: {request.discriminator_evidence_ids}\n"
                f"- retained negative/harmful alternatives: {request.negative_alternative_ids}\n"
            )
        response = self._llm.complete(
            LLMRequest(
                task="orion-development-change-proposal",
                system=(
                    "You are a proposal-only coding worker inside ORION. Return strict JSON matching the supplied schema. "
                    "Do not claim that tests passed, do not weaken evaluators/authority boundaries, and do not claim merge or promotion authority. "
                    "Produce the smallest repository-relative unified diff that addresses the diagnosed problem."
                ),
                user=(
                    f"Request: {request.request_id}\n"
                    f"Mechanic: {request.mechanic_id}\n"
                    f"Base revision: {request.base_revision}\n"
                    f"Problem: {request.problem_statement}\n"
                    f"Evidence ids: {request.evidence_ids}\n"
                    f"Failure episode ids: {request.failure_episode_ids}\n"
                    f"{causal_context}"
                    f"Protected constraints:\n{constraints}\n"
                    f"Protected paths (proposal will be rejected if touched):\n{protected_paths}\n"
                    f"Required tests/assurance obligations:\n{tests}\n"
                    f"Falsifier: {request.falsifier}\n"
                ),
                response_schema=_RESPONSE_SCHEMA,
            )
        )
        try:
            payload = json.loads(response.content)
        except json.JSONDecodeError as exc:
            raise ValueError("LLM development provider returned invalid JSON") from exc
        if not isinstance(payload, dict):
            raise ValueError("LLM development provider response must be a JSON object")
        touched_paths = _string_tuple(payload.get("touched_paths"), field="touched_paths")
        expected_effects = _string_tuple(payload.get("expected_effects"), field="expected_effects")
        supplied_tests = _string_tuple(payload.get("test_plan"), field="test_plan")
        patch = payload.get("patch")
        rationale = payload.get("rationale")
        falsifier = payload.get("falsifier")
        if not isinstance(patch, str) or not patch.strip():
            raise ValueError("LLM development response patch must be non-empty")
        if not isinstance(rationale, str) or not rationale.strip():
            raise ValueError("LLM development response rationale must be non-empty")
        if not isinstance(falsifier, str) or not falsifier.strip():
            raise ValueError("LLM development response falsifier must be non-empty")
        artifact = self._artifact_store.put(
            patch.encode("utf-8"),
            media_type="text/x-diff; charset=utf-8",
        )
        proposal_seed = f"{request.request_id}|{request.base_revision}|{artifact.content_hash}"
        proposal_id = "proposal:" + hashlib.sha256(proposal_seed.encode("utf-8")).hexdigest()
        provenance = tuple(
            item
            for item in (
                f"llm:model:{response.model_id}" if response.model_id else None,
                f"llm:response:{response.response_id}" if response.response_id else None,
                f"development-request:{request.request_id}",
                (
                    f"observed-failure:{request.observed_failure_artifact_hash}"
                    if request.observed_failure_bound
                    else None
                ),
                (
                    f"discriminator:{request.discriminator_artifact_hash}"
                    if request.observed_failure_bound
                    else None
                ),
                artifact.artifact_id,
            )
            if item is not None
        )
        return DevelopmentChangeProposal(
            proposal_id=proposal_id,
            request_id=request.request_id,
            base_revision=request.base_revision,
            patch_artifact_id=artifact.artifact_id,
            patch_artifact_hash=artifact.content_hash,
            touched_paths=touched_paths,
            rationale=rationale,
            expected_effects=expected_effects,
            test_plan=tuple(dict.fromkeys((*request.required_tests, *supplied_tests))),
            falsifier=falsifier,
            provenance_ids=provenance,
            proposal_only=True,
        )


__all__ = ["LLMDevelopmentChangeProvider"]

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from pathlib import Path

from orion.core.search import RetrievedItem, SearchQuery, SearchRouteKind
from orion.providers.llm.base import LLMProvider, LLMRequest, LLMResponse
from orion.providers.retrieval.base import RetrievalProvider

from .live_trial import BaselineTaskResult, FrozenTrialTask


BASELINE_ARTIFACT_SCHEMA = "SimpleLLMRetrievalBaselineArtifact.v1"
BASELINE_BUNDLE_SCHEMA = "SimpleLLMRetrievalBaselineBundle.v1"


def _sha256(payload: object) -> str:
    return hashlib.sha256(
        json.dumps(payload, sort_keys=True, separators=(",", ":")).encode()
    ).hexdigest()


@dataclass(frozen=True)
class SimpleBaselineArtifact:
    task_id: str
    evaluation_epoch_id: str
    query: SearchQuery
    retrieved_items: tuple[RetrievedItem, ...]
    response_content: str = ""
    model_id: str | None = None
    response_id: str | None = None
    solved: bool = False
    used_evidence_ids: tuple[str, ...] = ()
    residual_ids: tuple[str, ...] = ()
    retrieval_error: str = ""
    llm_error: str = ""
    parse_error: str = ""

    @property
    def payload(self) -> dict[str, object]:
        return {
            "schema": BASELINE_ARTIFACT_SCHEMA,
            "task_id": self.task_id,
            "evaluation_epoch_id": self.evaluation_epoch_id,
            "query": {
                "query_id": self.query.query_id,
                "text": self.query.text,
                "route_id": self.query.route_id,
                "route_kind": self.query.route_kind.value,
                "domain_hint": self.query.domain_hint,
            },
            "retrieved_items": [
                {
                    "item_id": item.item_id,
                    "content": item.content,
                    "source_uri": item.source_uri,
                    "domain_ids": list(item.domain_ids),
                }
                for item in self.retrieved_items
            ],
            "response_content": self.response_content,
            "model_id": self.model_id,
            "response_id": self.response_id,
            "solved": self.solved,
            "used_evidence_ids": list(self.used_evidence_ids),
            "residual_ids": list(self.residual_ids),
            "retrieval_error": self.retrieval_error,
            "llm_error": self.llm_error,
            "parse_error": self.parse_error,
        }

    @property
    def artifact_hash(self) -> str:
        return _sha256(self.payload)


class SimpleLLMRetrievalBaseline:
    """One-search/one-completion baseline for the frozen Shadow trial.

    This deliberately omits ORION mechanics, iterative routing, structured
    absorption, failure learning and self-development. It performs one query
    using the task's current vocabulary, retrieves a bounded set of documents,
    and asks one LLM call to answer using only returned item IDs.
    """

    def __init__(
        self,
        *,
        llm: LLMProvider,
        retrieval: RetrievalProvider,
        max_results: int = 12,
        retrieval_call_cost_units: float = 1.0,
        llm_call_cost_units: float = 1.0,
    ) -> None:
        if max_results < 1:
            raise ValueError("baseline max_results must be positive")
        if retrieval_call_cost_units < 0 or llm_call_cost_units < 0:
            raise ValueError("baseline call costs cannot be negative")
        self._llm = llm
        self._retrieval = retrieval
        self._max_results = max_results
        self._retrieval_cost = retrieval_call_cost_units
        self._llm_cost = llm_call_cost_units
        self._artifacts: dict[str, SimpleBaselineArtifact] = {}

    @property
    def artifacts(self) -> tuple[SimpleBaselineArtifact, ...]:
        return tuple(self._artifacts[key] for key in sorted(self._artifacts))

    def artifact(self, task_id: str) -> SimpleBaselineArtifact | None:
        return self._artifacts.get(task_id)

    @staticmethod
    def _query(task: FrozenTrialTask) -> SearchQuery:
        digest = hashlib.sha256(
            f"{task.task_id}\n{task.problem.question}".encode()
        ).hexdigest()[:20]
        return SearchQuery(
            query_id=f"baseline-query:{digest}",
            text=task.problem.question,
            route_id="simple-baseline:single-current-vocabulary-search",
            route_kind=SearchRouteKind.CURRENT_VOCABULARY,
            domain_hint=(
                task.problem.initial_domain_ids[0]
                if task.problem.initial_domain_ids
                else None
            ),
        )

    @staticmethod
    def _request(task: FrozenTrialTask, items: tuple[RetrievedItem, ...]) -> LLMRequest:
        documents = "\n\n".join(
            f"ITEM_ID: {item.item_id}\nSOURCE: {item.source_uri}\nCONTENT:\n{item.content}"
            for item in items
        )
        return LLMRequest(
            task="simple_llm_retrieval_baseline",
            system=(
                "You are the frozen simple LLM+retrieval baseline. Use only the supplied documents. "
                "Do not invent evidence IDs. Return JSON only."
            ),
            user=(
                f"QUESTION:\n{task.problem.question}\n\n"
                f"SUCCESS CRITERIA:\n{list(task.problem.success_criteria)}\n\n"
                f"DOCUMENTS:\n{documents}\n\n"
                "Return an object with: solved (boolean), answer (string), "
                "used_item_ids (array of exact ITEM_ID strings), residual_ids (array of strings)."
            ),
            response_schema=(
                '{"type":"object","required":["solved","answer","used_item_ids","residual_ids"],'
                '"properties":{"solved":{"type":"boolean"},"answer":{"type":"string"},'
                '"used_item_ids":{"type":"array","items":{"type":"string"}},'
                '"residual_ids":{"type":"array","items":{"type":"string"}}}}'
            ),
        )

    def _store(self, artifact: SimpleBaselineArtifact, resource_units: float) -> BaselineTaskResult:
        self._artifacts[artifact.task_id] = artifact
        return BaselineTaskResult(
            task_id=artifact.task_id,
            solved=artifact.solved,
            evidence_ids=artifact.used_evidence_ids,
            residual_ids=artifact.residual_ids,
            resource_units=resource_units,
            artifact_hash=artifact.artifact_hash,
        )

    def run(
        self, task: FrozenTrialTask, *, evaluation_epoch_id: str
    ) -> BaselineTaskResult:
        query = self._query(task)
        try:
            items = tuple(self._retrieval.search(query, limit=self._max_results))
        except Exception as error:  # noqa: BLE001 - preserve provider failure as trial data
            artifact = SimpleBaselineArtifact(
                task.task_id,
                evaluation_epoch_id,
                query,
                (),
                residual_ids=("baseline_retrieval_error",),
                retrieval_error=f"{type(error).__name__}: {error}",
            )
            return self._store(artifact, self._retrieval_cost)

        if not items:
            artifact = SimpleBaselineArtifact(
                task.task_id,
                evaluation_epoch_id,
                query,
                (),
                residual_ids=("baseline_no_retrieval_results",),
            )
            return self._store(artifact, self._retrieval_cost)

        try:
            response: LLMResponse = self._llm.complete(self._request(task, items))
        except Exception as error:  # noqa: BLE001 - preserve provider failure as trial data
            artifact = SimpleBaselineArtifact(
                task.task_id,
                evaluation_epoch_id,
                query,
                items,
                residual_ids=("baseline_llm_error",),
                llm_error=f"{type(error).__name__}: {error}",
            )
            return self._store(artifact, self._retrieval_cost + self._llm_cost)

        parse_error = ""
        raw: dict[str, object] = {}
        try:
            decoded = json.loads(response.content)
            if not isinstance(decoded, dict):
                raise ValueError("baseline response must be a JSON object")
            raw = decoded
        except (json.JSONDecodeError, ValueError) as error:
            parse_error = f"{type(error).__name__}: {error}"

        available = {item.item_id for item in items}
        requested_ids = tuple(
            str(item) for item in raw.get("used_item_ids", ())
        ) if isinstance(raw.get("used_item_ids", ()), list) else ()
        unknown = tuple(item for item in requested_ids if item not in available)
        used = tuple(dict.fromkeys(item for item in requested_ids if item in available))
        supplied_residuals = tuple(
            str(item) for item in raw.get("residual_ids", ())
        ) if isinstance(raw.get("residual_ids", ()), list) else ()
        residuals = list(supplied_residuals)
        if parse_error:
            residuals.append("baseline_output_unparseable")
        if unknown:
            residuals.append("baseline_unknown_evidence_id")
        solved_requested = raw.get("solved") is True
        if solved_requested and not used:
            residuals.append("baseline_solved_without_retrieved_evidence")
        solved = solved_requested and bool(used) and not parse_error and not unknown

        artifact = SimpleBaselineArtifact(
            task.task_id,
            evaluation_epoch_id,
            query,
            items,
            response_content=response.content,
            model_id=response.model_id,
            response_id=response.response_id,
            solved=solved,
            used_evidence_ids=used,
            residual_ids=tuple(dict.fromkeys(residuals)),
            parse_error=parse_error,
        )
        return self._store(artifact, self._retrieval_cost + self._llm_cost)


def baseline_bundle_to_dict(
    baseline: SimpleLLMRetrievalBaseline,
) -> dict[str, object]:
    artifacts = baseline.artifacts
    payload = {
        "schema": BASELINE_BUNDLE_SCHEMA,
        "artifacts": [
            {**artifact.payload, "artifact_hash": artifact.artifact_hash}
            for artifact in artifacts
        ],
    }
    payload["bundle_hash"] = _sha256(payload)
    return payload


def write_baseline_bundle(
    baseline: SimpleLLMRetrievalBaseline, path: Path | str
) -> None:
    Path(path).write_text(
        json.dumps(baseline_bundle_to_dict(baseline), indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )


__all__ = [
    "BASELINE_ARTIFACT_SCHEMA",
    "BASELINE_BUNDLE_SCHEMA",
    "SimpleBaselineArtifact",
    "SimpleLLMRetrievalBaseline",
    "baseline_bundle_to_dict",
    "write_baseline_bundle",
]

"""Evidence retention for live-provider campaigns.

A live campaign runs against indices that change under us. The run itself is
therefore not reproducible; only the *record* of it can be. This module keeps
that record: every request as issued, every response body as returned, and a
manifest of the freeze identities that make the run interpretable later.

Two things are load-bearing. Responses are retained verbatim and addressed by
sha256, so a later reader can check what the provider actually said rather than
what we concluded from it. And request URLs are redacted before they touch
disk, because OpenAlex carries its credential in the query string and an
evidence archive is exactly the wrong place to learn that.
"""

from __future__ import annotations

import hashlib
import json
from collections.abc import Callable, Mapping, Sequence
from dataclasses import dataclass, field
from pathlib import Path
from urllib.parse import parse_qsl, urlencode, urlsplit, urlunsplit

REDACTED = "REDACTED"
SECRET_PARAMS = frozenset(
    {"api_key", "apikey", "key", "token", "access_token", "secret", "password"}
)
MANIFEST_SCHEMA = "orion.publication-run-manifest.v1"
HASH_FIELD = "manifest_content_sha256"


def redact_url(url: str) -> str:
    """Strip credential-bearing query parameters from a URL.

    OpenAlex takes its API key as ``?api_key=``. Persisting the raw URL would
    write a live credential into the retained evidence, where it would then be
    copied by every archive and reproduction package built from it.
    """

    parts = urlsplit(url)
    if not parts.query:
        return url
    pairs = [
        (name, REDACTED if name.lower() in SECRET_PARAMS else value)
        for name, value in parse_qsl(parts.query, keep_blank_values=True)
    ]
    return urlunsplit(
        (parts.scheme, parts.netloc, parts.path, urlencode(pairs), parts.fragment)
    )


def sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def sha256_file(path: Path) -> str:
    """Digest a file's bytes, never a reformatted copy of its contents."""

    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


@dataclass(frozen=True)
class RequestRecord:
    """One request/response pair as it happened."""

    sequence: int
    url: str
    requested_at_utc: str
    route_id: str
    derivation: str
    http_status: int | None
    response_sha256: str
    response_bytes: int
    elapsed_seconds: float
    response_headers: Mapping[str, str] = field(default_factory=dict)
    transport_error: str = ""

    def as_dict(self) -> dict:
        return {
            "sequence": self.sequence,
            "url": self.url,
            "requested_at_utc": self.requested_at_utc,
            "route_id": self.route_id,
            "derivation": self.derivation,
            "http_status": self.http_status,
            "response_sha256": self.response_sha256,
            "response_bytes": self.response_bytes,
            "elapsed_seconds": self.elapsed_seconds,
            "response_headers": dict(self.response_headers),
            "transport_error": self.transport_error,
        }


@dataclass
class CampaignTrace:
    """Append-only record of everything a campaign asked and was told.

    Wraps an injected transport rather than replacing it, so the provider
    clients keep their own typed error handling and the trace observes the
    exact bytes those clients parsed.
    """

    artifact_root: Path
    clock: Callable[[], float]
    timestamp: Callable[[], str]
    _records: list[RequestRecord] = field(default_factory=list, init=False)
    _route_id: str = field(default="", init=False)
    _derivation: str = field(default="", init=False)

    def __post_init__(self) -> None:
        self.artifact_root = Path(self.artifact_root)
        (self.artifact_root / "responses").mkdir(parents=True, exist_ok=True)

    @property
    def records(self) -> tuple[RequestRecord, ...]:
        return tuple(self._records)

    def bind_route(self, route_id: str, derivation: str) -> None:
        """Attribute subsequent requests to a route, so evidence is traceable."""

        self._route_id = route_id
        self._derivation = derivation

    def mark(self) -> int:
        return len(self._records)

    def since(self, mark: int) -> tuple[RequestRecord, ...]:
        return tuple(self._records[mark:])

    def wrap(self, transport: Callable[[str], object]) -> Callable[[str], object]:
        """Return a transport that records every exchange before returning it."""

        def recording(url: str) -> object:
            started = self.clock()
            requested_at = self.timestamp()
            try:
                response = transport(url)
            except Exception as error:  # noqa: BLE001 - transport failures are evidence
                self._append(
                    url=url,
                    requested_at=requested_at,
                    status=None,
                    body="",
                    headers={},
                    elapsed=self.clock() - started,
                    transport_error=f"{type(error).__name__}: {error}",
                )
                raise
            body = str(getattr(response, "body", "") or "")
            self._append(
                url=url,
                requested_at=requested_at,
                status=getattr(response, "status", None),
                body=body,
                headers=dict(getattr(response, "headers", None) or {}),
                elapsed=self.clock() - started,
            )
            return response

        return recording

    def _append(
        self,
        *,
        url: str,
        requested_at: str,
        status: int | None,
        body: str,
        headers: Mapping[str, str],
        elapsed: float,
        transport_error: str = "",
    ) -> None:
        digest = sha256_text(body)
        if body:
            (self.artifact_root / "responses" / f"{digest}.raw").write_text(
                body, encoding="utf-8"
            )
        record = RequestRecord(
            sequence=len(self._records),
            url=redact_url(url),
            requested_at_utc=requested_at,
            route_id=self._route_id,
            derivation=self._derivation,
            http_status=status,
            response_sha256=digest,
            response_bytes=len(body.encode("utf-8")),
            elapsed_seconds=round(max(0.0, elapsed), 6),
            response_headers=dict(headers),
            transport_error=transport_error,
        )
        self._records.append(record)
        with (self.artifact_root / "requests.jsonl").open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(record.as_dict(), sort_keys=True) + "\n")

    def write_manifest(self, manifest: Mapping[str, object]) -> Path:
        path = self.artifact_root / "campaign_manifest.json"
        path.write_text(canonical_json(manifest) + "\n", encoding="utf-8")
        return path


def canonical_json(payload: Mapping[str, object]) -> str:
    """One byte-stable serialization, so a manifest hash means something."""

    return json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=True)


def manifest_content_hash(manifest: Mapping[str, object]) -> str:
    """Hash a manifest over everything except the hash field itself."""

    payload = {key: value for key, value in manifest.items() if key != HASH_FIELD}
    return sha256_text(canonical_json(payload))


@dataclass(frozen=True)
class RouteDefinition:
    """The freeze identity of one route, as it will be reported."""

    route_id: str
    route_kind: str
    backend: str
    query_derivation: str
    provider: str
    endpoint: str
    budget_units: float
    cost_budget_usd: float | None = None

    def as_dict(self) -> dict:
        return {
            "route_id": self.route_id,
            "route_kind": self.route_kind,
            "backend": self.backend,
            "query_derivation": self.query_derivation,
            "provider": self.provider,
            "endpoint": self.endpoint,
            "budget_units": self.budget_units,
            "cost_budget_usd": self.cost_budget_usd,
        }


@dataclass(frozen=True)
class ContaminationNote:
    """Whether the questions could have leaked into the indices being searched.

    A live search route can retrieve the answer to a public benchmark item
    simply because the benchmark is on the web. That is a real threat to a
    headline claim and it is not detectable after the fact, so it is declared
    per campaign, before the run, in the manifest.
    """

    questions_are_public_benchmark_items: bool
    rationale: str
    mitigations: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        if not self.rationale.strip():
            raise ValueError("a contamination note must state its reasoning")

    def as_dict(self) -> dict:
        return {
            "questions_are_public_benchmark_items": self.questions_are_public_benchmark_items,
            "search_time_contamination_risk": (
                "PRESENT" if self.questions_are_public_benchmark_items else "REMOVED_FOR_THIS_CAMPAIGN"
            ),
            "rationale": self.rationale,
            "mitigations": list(self.mitigations),
        }


def build_campaign_manifest(
    *,
    campaign_id: str,
    protocol_id: str,
    protocol_path: Path,
    subject_revision: str,
    artifact_root: str,
    questions: Sequence[Mapping[str, object]],
    routes: Sequence[RouteDefinition],
    provider_endpoints: Mapping[str, str],
    provider_api_versions: Mapping[str, str],
    client_user_agent: str,
    rate_policy: Mapping[str, object],
    resource_limits: Mapping[str, object],
    seeds: Sequence[int],
    environment: Mapping[str, object],
    access_policy_hash: str,
    evaluator_hash: str,
    evaluation_epoch: str,
    started_at_utc: str,
    ended_at_utc: str,
    contamination: ContaminationNote,
    notes: str = "",
) -> dict:
    """Assemble the freeze identities of one live campaign.

    Shaped to ``RUN_MANIFEST_SCHEMA_V1`` so a live campaign lands in the same
    archive as every other run, with the live-specific freeze identities —
    endpoints, API versions, client identity, rate policy, route definitions,
    budgets and window — carried alongside rather than instead.
    """

    if len(subject_revision) != 40 or not all(
        char in "0123456789abcdef" for char in subject_revision
    ):
        raise ValueError(
            "subject_revision must be a full 40-character git sha; a short sha "
            "does not bind a revision unambiguously"
        )
    if not questions:
        raise ValueError("a campaign manifest must freeze at least one question")
    if not routes:
        raise ValueError("a campaign manifest must freeze at least one route")
    if not seeds:
        raise ValueError("a campaign manifest must record at least one seed")

    manifest: dict = {
        "schema_version": MANIFEST_SCHEMA,
        "paper_id": "P2",
        "protocol_id": protocol_id,
        "protocol_digest": sha256_file(protocol_path),
        "subject_revision": subject_revision,
        "data_artifacts": [
            {
                "name": f"live:{route.backend}",
                "revision_or_hash": provider_api_versions.get(route.backend, "UNVERSIONED_LIVE_INDEX"),
                "access": "PUBLIC",
                "license": None,
                "retrieval_timestamp": started_at_utc,
            }
            for route in _unique_backends(routes)
        ],
        "model_provider_revisions": dict(provider_api_versions),
        "baseline_config_hashes": {"live_campaign": "NOT_APPLICABLE_OUTCOME_BLIND"},
        "evaluator_hash": evaluator_hash,
        "split_hashes": {"live_campaign": "NO_SPLIT_LIVE_OPEN_WORLD"},
        "evaluation_epoch": evaluation_epoch,
        "seeds": list(seeds),
        "resource_limits": dict(resource_limits),
        "environment": dict(environment),
        "access_policy_hash": access_policy_hash,
        "artifact_root": artifact_root,
        "created_before_outcome_access": True,
        "notes": notes,
        "live_campaign": {
            "campaign_id": campaign_id,
            "provider_endpoints": dict(provider_endpoints),
            "provider_api_versions": dict(provider_api_versions),
            "client_user_agent": client_user_agent,
            "rate_policy": dict(rate_policy),
            "frozen_questions": [dict(item) for item in questions],
            "route_definitions": [item.as_dict() for item in routes],
            "started_at_utc": started_at_utc,
            "ended_at_utc": ended_at_utc,
            "contamination": contamination.as_dict(),
            "denominator": "INCOMPLETE_OPEN_WORLD",
            "recall_reportable": False,
        },
    }
    manifest[HASH_FIELD] = manifest_content_hash(manifest)
    return manifest


def _unique_backends(routes: Sequence[RouteDefinition]) -> tuple[RouteDefinition, ...]:
    seen: set[str] = set()
    unique: list[RouteDefinition] = []
    for route in routes:
        if route.backend in seen:
            continue
        seen.add(route.backend)
        unique.append(route)
    return tuple(unique)


__all__ = [
    "CampaignTrace",
    "ContaminationNote",
    "HASH_FIELD",
    "REDACTED",
    "RequestRecord",
    "RouteDefinition",
    "build_campaign_manifest",
    "canonical_json",
    "manifest_content_hash",
    "redact_url",
    "sha256_file",
    "sha256_text",
]

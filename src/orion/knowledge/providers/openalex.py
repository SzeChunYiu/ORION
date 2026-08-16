from __future__ import annotations

import json
from collections.abc import Callable
from dataclasses import dataclass
from enum import Enum
from urllib.parse import urlencode

from ..identity import CanonicalId, canonical_source_id
from .arxiv import TransportResponse

BASE_URL = "https://api.openalex.org"
MAX_PER_PAGE = 100
BASIC_PAGING_CEILING = 10_000


class OpenAlexStatus(str, Enum):
    OK = "OK"
    KEY_REQUIRED = "KEY_REQUIRED"
    RATE_LIMITED = "RATE_LIMITED"
    REFUSED_BASIC_PAGING_CEILING = "REFUSED_BASIC_PAGING_CEILING"
    TRANSPORT_ERROR = "TRANSPORT_ERROR"
    MALFORMED_RESPONSE = "MALFORMED_RESPONSE"
    SERVICE_ERROR = "SERVICE_ERROR"


@dataclass(frozen=True)
class OpenAlexRecord:
    identity: CanonicalId
    title: str
    abstract: str
    publication_year: int | None = None
    aliases: tuple[str, ...] = ()
    referenced_works: tuple[str, ...] = ()

    @property
    def source_id(self) -> str:
        return str(self.identity)


@dataclass(frozen=True)
class OpenAlexPage:
    status: OpenAlexStatus
    records: tuple[OpenAlexRecord, ...] = ()
    next_cursor: str = ""
    total: int | None = None
    cost_usd: float | None = None
    retry_after_seconds: float | None = None
    note: str = ""

    @property
    def ok(self) -> bool:
        return self.status is OpenAlexStatus.OK


def reconstruct_abstract(inverted_index: dict[str, list[int]] | None) -> str:
    """Rebuild plain text from OpenAlex's inverted index.

    OpenAlex ships abstracts as {token: [positions]} rather than prose. Anything
    that treats a missing or unreconstructed abstract as an empty one will read
    a present abstract as absent, which for a coverage-driven system is a false
    negative dressed as a fact.
    """

    if not inverted_index:
        return ""
    positioned: list[tuple[int, str]] = [
        (position, token)
        for token, positions in inverted_index.items()
        for position in positions
    ]
    if not positioned:
        return ""
    positioned.sort()
    return " ".join(token for _, token in positioned)


def build_works_url(
    *,
    search: str = "",
    filters: str = "",
    per_page: int = 25,
    page: int | None = None,
    cursor: str = "",
    api_key: str = "",
) -> str:
    if per_page < 1 or per_page > MAX_PER_PAGE:
        raise ValueError(f"per_page must be between 1 and {MAX_PER_PAGE}")
    if page is not None and cursor:
        raise ValueError("use page or cursor, never both")
    params: list[tuple[str, str]] = []
    if search:
        params.append(("search", search))
    if filters:
        params.append(("filter", filters))
    params.append(("per-page", str(per_page)))
    if cursor:
        params.append(("cursor", cursor))
    elif page is not None:
        params.append(("page", str(page)))
    if api_key:
        params.append(("api_key", api_key))
    return f"{BASE_URL}/works?{urlencode(params)}"


def basic_paging_exceeded(page: int, per_page: int) -> bool:
    """Whether this request crosses OpenAlex's hard basic-paging wall."""

    return page * per_page > BASIC_PAGING_CEILING


def _record_from_work(work: dict) -> OpenAlexRecord | None:
    raw_id = work.get("id") or ""
    identity = canonical_source_id(str(raw_id)) if raw_id else None
    if identity is None or not identity.is_resolvable:
        return None
    ids = work.get("ids") or {}
    aliases: list[str] = []
    for key in ("doi", "pmid", "mag"):
        value = ids.get(key)
        if not value:
            continue
        resolved = canonical_source_id(str(value))
        if resolved.is_resolvable and str(resolved) != str(identity):
            aliases.append(str(resolved))
    return OpenAlexRecord(
        identity=identity,
        title=str(work.get("display_name") or ""),
        abstract=reconstruct_abstract(work.get("abstract_inverted_index")),
        publication_year=work.get("publication_year"),
        aliases=tuple(dict.fromkeys(aliases)),
        referenced_works=tuple(str(item) for item in work.get("referenced_works") or ()),
    )


def parse_works(body: str) -> tuple[OpenAlexStatus, tuple[OpenAlexRecord, ...], dict]:
    try:
        payload = json.loads(body)
    except json.JSONDecodeError as error:
        return OpenAlexStatus.MALFORMED_RESPONSE, (), {"note": str(error)}
    if not isinstance(payload, dict):
        return OpenAlexStatus.MALFORMED_RESPONSE, (), {"note": "response is not an object"}
    if "error" in payload:
        return OpenAlexStatus.SERVICE_ERROR, (), {"note": str(payload.get("message") or payload["error"])}
    results = payload.get("results")
    if not isinstance(results, list):
        return OpenAlexStatus.MALFORMED_RESPONSE, (), {"note": "no results array"}
    records = tuple(
        item for item in (_record_from_work(work) for work in results if isinstance(work, dict))
        if item is not None
    )
    return OpenAlexStatus.OK, records, payload.get("meta") or {}


@dataclass
class OpenAlexClient:
    """Fetch OpenAlex works, refusing rather than burning a shared budget."""

    transport: Callable[[str], TransportResponse]
    api_key: str = ""
    gate: object | None = None

    def fetch_works(
        self,
        *,
        search: str = "",
        filters: str = "",
        per_page: int = 25,
        page: int | None = None,
        cursor: str = "",
    ) -> OpenAlexPage:
        if not self.api_key:
            return OpenAlexPage(
                OpenAlexStatus.KEY_REQUIRED,
                note=(
                    "OpenAlex has required an API key since February 2026 and now "
                    "ignores the mailto parameter. Keyless requests draw on a "
                    "$0.1 budget shared across the whole IP and were observed to "
                    "429 after about three list calls, so attempting one would "
                    "spend a budget every other caller on this address depends on."
                ),
            )
        if page is not None and basic_paging_exceeded(page, per_page):
            return OpenAlexPage(
                OpenAlexStatus.REFUSED_BASIC_PAGING_CEILING,
                note=(
                    f"page*per_page exceeds {BASIC_PAGING_CEILING}; OpenAlex basic "
                    "paging stops there. Switch to cursor paging (cursor=*)."
                ),
            )
        url = build_works_url(
            search=search,
            filters=filters,
            per_page=per_page,
            page=page,
            cursor=cursor,
            api_key=self.api_key,
        )
        try:
            response = self.transport(url)
        except Exception as error:  # noqa: BLE001 - transport failures are data
            return OpenAlexPage(
                OpenAlexStatus.TRANSPORT_ERROR, note=f"{type(error).__name__}: {error}"
            )
        if self.gate is not None:
            self.gate.record_request("openalex")  # type: ignore[attr-defined]

        if response.status == 429:
            retry = _retry_after(response.headers)
            if self.gate is not None and retry is not None:
                self.gate.record_retry_after("openalex", retry)  # type: ignore[attr-defined]
            return OpenAlexPage(
                OpenAlexStatus.RATE_LIMITED,
                retry_after_seconds=retry,
                note="daily budget exhausted or per-second limit exceeded",
            )
        if response.status >= 500:
            return OpenAlexPage(OpenAlexStatus.SERVICE_ERROR, note=f"HTTP {response.status}")
        if response.status != 200:
            return OpenAlexPage(OpenAlexStatus.TRANSPORT_ERROR, note=f"HTTP {response.status}")

        status, records, meta = parse_works(response.body)
        if status is not OpenAlexStatus.OK:
            return OpenAlexPage(status, note=str(meta.get("note", "")))
        return OpenAlexPage(
            OpenAlexStatus.OK,
            records=records,
            next_cursor=str(meta.get("next_cursor") or ""),
            total=meta.get("count"),
            cost_usd=meta.get("cost_usd"),
        )


def _retry_after(headers: dict[str, str] | None) -> float | None:
    if not headers:
        return None
    for key, value in headers.items():
        if key.lower() in {"retry-after", "retryafter"}:
            try:
                return float(value)
            except ValueError:
                return None
    return None

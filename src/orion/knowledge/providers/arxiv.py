from __future__ import annotations

import xml.etree.ElementTree as ElementTree

import defusedxml.ElementTree as SafeElementTree
from collections.abc import Callable
from dataclasses import dataclass
from enum import Enum
from urllib.parse import urlencode

from ..identity import CanonicalId, canonical_source_id

BASE_URL = "https://export.arxiv.org/api/query"
_ATOM = "{http://www.w3.org/2005/Atom}"
_ARXIV_NS = "{http://arxiv.org/schemas/atom}"

# arXiv documents a 2000-result slice and a 30000 ceiling, but deep paging fails
# earlier and differently than documented: `start` in the low tens of thousands
# returns HTTP 500 with an Atom body whose single entry is an internal-error
# notice, not the documented 400. Refuse past a conservative bound rather than
# walking into a wall of 500s, and tell the caller to switch access method.
SAFE_START_LIMIT = 2000
MAX_RESULTS_PER_REQUEST = 2000


class FetchStatus(str, Enum):
    """Typed outcome of one retrieval attempt."""

    OK = "OK"
    RATE_LIMITED = "RATE_LIMITED"
    REFUSED_UNSAFE_PAGING = "REFUSED_UNSAFE_PAGING"
    TRANSPORT_ERROR = "TRANSPORT_ERROR"
    MALFORMED_RESPONSE = "MALFORMED_RESPONSE"
    SERVICE_ERROR = "SERVICE_ERROR"


@dataclass(frozen=True)
class ArxivRecord:
    """One work as arXiv describes it."""

    identity: CanonicalId
    versioned_id: str
    title: str
    summary: str
    published: str = ""
    updated: str = ""
    authors: tuple[str, ...] = ()
    doi: str = ""
    primary_category: str = ""

    @property
    def source_id(self) -> str:
        return str(self.identity)

    @property
    def aliases(self) -> tuple[str, ...]:
        """A DOI arXiv reports for this work is a genuine alias.

        This is the one case where an identifier found alongside a document does
        identify it: arXiv states the DOI in a field describing the entry, not
        in prose the entry happens to contain.
        """

        if not self.doi:
            return ()
        resolved = canonical_source_id(self.doi)
        return (str(resolved),) if resolved.is_resolvable else ()


@dataclass(frozen=True)
class FetchResult:
    """What one attempt produced, including why it produced nothing."""

    status: FetchStatus
    records: tuple[ArxivRecord, ...] = ()
    retry_after_seconds: float | None = None
    note: str = ""

    @property
    def ok(self) -> bool:
        return self.status is FetchStatus.OK


@dataclass(frozen=True)
class TransportResponse:
    """The minimal shape an injected transport must return."""

    status: int
    body: str
    headers: dict[str, str] | None = None


def build_query_url(
    *,
    search_query: str = "",
    id_list: tuple[str, ...] = (),
    start: int = 0,
    max_results: int = 25,
) -> str:
    if not search_query and not id_list:
        raise ValueError("an arXiv query needs a search expression or an id list")
    if start < 0 or max_results < 1:
        raise ValueError("start must be non-negative and max_results positive")
    if max_results > MAX_RESULTS_PER_REQUEST:
        raise ValueError(
            f"max_results above {MAX_RESULTS_PER_REQUEST} is outside the documented slice"
        )
    params: list[tuple[str, str]] = []
    if search_query:
        params.append(("search_query", search_query))
    if id_list:
        params.append(("id_list", ",".join(id_list)))
    params.extend([("start", str(start)), ("max_results", str(max_results))])
    return f"{BASE_URL}?{urlencode(params)}"


def _text(node: ElementTree.Element | None) -> str:
    return " ".join(node.text.split()) if node is not None and node.text else ""


def _versioned_arxiv_id(raw_id: str) -> str:
    """Preserve the complete versioned arXiv identifier from an Atom entry.

    Modern identifiers have no slash after ``/abs/`` and were safe to obtain via
    ``rsplit('/', 1)``. Legacy identifiers include their archive/category prefix,
    for example ``hep-th/9901001v2``. Taking only the final path component loses
    ``hep-th/`` and makes a retrieved legacy paper impossible to match against a
    correct scorer-side identifier. Keep the full ``/abs/`` tail whenever the
    canonical Atom form supplies it; retain the historical fallback for unusual
    but otherwise resolvable feeds.
    """

    marker = "/abs/"
    if marker in raw_id:
        return raw_id.split(marker, 1)[1].strip().strip("/")
    return raw_id.rsplit("/", 1)[-1]


def parse_atom(body: str) -> tuple[FetchStatus, tuple[ArxivRecord, ...], str]:
    """Parse an arXiv Atom feed, distinguishing empty from broken.

    arXiv reports server faults *inside* a 200-shaped Atom document, as a single
    entry whose title is an error notice. Parsing that as a record would turn a
    service failure into a silently empty result set, which downstream reads as
    "nothing matched" — a false negative that looks like evidence of absence.
    """

    try:
        # Untrusted remote input: parse with entity expansion disabled.
        root = SafeElementTree.fromstring(body)
    except (ElementTree.ParseError, ValueError) as error:
        return FetchStatus.MALFORMED_RESPONSE, (), f"unparseable feed: {error}"

    records: list[ArxivRecord] = []
    for entry in root.findall(f"{_ATOM}entry"):
        raw_id = _text(entry.find(f"{_ATOM}id"))
        title = _text(entry.find(f"{_ATOM}title"))
        summary = _text(entry.find(f"{_ATOM}summary"))
        if not raw_id:
            continue
        if "arxiv.org/api/errors" in raw_id or title.lower().startswith("error"):
            return FetchStatus.SERVICE_ERROR, (), summary or title
        identity = canonical_source_id(raw_id)
        if not identity.is_resolvable:
            continue
        category = entry.find(f"{_ARXIV_NS}primary_category")
        records.append(
            ArxivRecord(
                identity=identity,
                versioned_id=_versioned_arxiv_id(raw_id),
                title=title,
                summary=summary,
                published=_text(entry.find(f"{_ATOM}published")),
                updated=_text(entry.find(f"{_ATOM}updated")),
                authors=tuple(
                    _text(item.find(f"{_ATOM}name"))
                    for item in entry.findall(f"{_ATOM}author")
                ),
                doi=_text(entry.find(f"{_ARXIV_NS}doi")),
                primary_category=(category.get("term", "") if category is not None else ""),
            )
        )
    return FetchStatus.OK, tuple(records), ""


@dataclass
class ArxivClient:
    """Fetch from arXiv under an injected transport and rate gate."""

    transport: Callable[[str], TransportResponse]
    gate: object | None = None

    def fetch(
        self,
        *,
        search_query: str = "",
        id_list: tuple[str, ...] = (),
        start: int = 0,
        max_results: int = 25,
    ) -> FetchResult:
        if start > SAFE_START_LIMIT:
            return FetchResult(
                FetchStatus.REFUSED_UNSAFE_PAGING,
                note=(
                    f"start={start} exceeds the safe bound {SAFE_START_LIMIT}; arXiv "
                    "fails past this with HTTP 500 rather than the documented 400. "
                    "Use OAI-PMH or the S3 bulk mirror for deep traversal."
                ),
            )
        url = build_query_url(
            search_query=search_query,
            id_list=id_list,
            start=start,
            max_results=max_results,
        )
        try:
            response = self.transport(url)
        except Exception as error:  # noqa: BLE001 - transport failures are data
            return FetchResult(
                FetchStatus.TRANSPORT_ERROR, note=f"{type(error).__name__}: {error}"
            )
        if self.gate is not None:
            self.gate.record_request("arxiv")  # type: ignore[attr-defined]

        if response.status == 429:
            retry = _retry_after(response.headers)
            if self.gate is not None and retry is not None:
                self.gate.record_retry_after("arxiv", retry)  # type: ignore[attr-defined]
            return FetchResult(
                FetchStatus.RATE_LIMITED,
                retry_after_seconds=retry,
                note=(
                    "arXiv refused the request. Observed 2026-08-16 on an isolated "
                    "request that honoured the published one-per-three-seconds "
                    "spacing, so the published budget is a floor, not a guarantee."
                ),
            )
        if response.status >= 500:
            return FetchResult(
                FetchStatus.SERVICE_ERROR, note=f"HTTP {response.status}"
            )
        if response.status != 200:
            return FetchResult(
                FetchStatus.TRANSPORT_ERROR, note=f"HTTP {response.status}"
            )

        status, records, note = parse_atom(response.body)
        return FetchResult(status, records, note=note)


def _retry_after(headers: dict[str, str] | None) -> float | None:
    if not headers:
        return None
    for key, value in headers.items():
        if key.lower() == "retry-after":
            try:
                return float(value)
            except ValueError:
                return None
    return None

from __future__ import annotations

import re
from dataclasses import dataclass
from enum import Enum

_DOI_PREFIXES = ("https://doi.org/", "http://doi.org/", "doi:", "DOI:")
_ARXIV_PREFIXES = (
    "https://arxiv.org/abs/",
    "http://arxiv.org/abs/",
    "https://arxiv.org/pdf/",
    "arxiv:",
    "arXiv:",
)
_OPENALEX_PREFIXES = ("https://openalex.org/", "openalex:")
_ARXIV_VERSION = re.compile(r"^(?P<base>.+?)v(?P<version>\d+)$")
_DOI_SHAPE = re.compile(r"^10\.\d{4,9}/\S+$")
_ARXIV_NEW = re.compile(r"^\d{4}\.\d{4,5}(v\d+)?$")
_ARXIV_OLD = re.compile(r"^[a-z-]+(\.[A-Z]{2})?/\d{7}(v\d+)?$")
_OPENALEX_SHAPE = re.compile(r"^[WwAaSsIiCc]\d+$")


class IdentityScheme(str, Enum):
    DOI = "doi"
    ARXIV = "arxiv"
    OPENALEX = "openalex"
    LOCAL = "local"
    URL = "url"
    UNKNOWN = "unknown"


@dataclass(frozen=True)
class CanonicalId:
    """One normalized work identifier, with its version stripped off."""

    scheme: IdentityScheme
    value: str
    version: str = ""

    def __str__(self) -> str:
        return f"{self.scheme.value}:{self.value}"

    @property
    def is_resolvable(self) -> bool:
        return self.scheme is not IdentityScheme.UNKNOWN


def canonical_source_id(raw: str) -> CanonicalId:
    """Normalize a raw identifier so the same work maps to one key.

    Deduplication happens here or not at all. Two rules carry most of the
    weight: a DOI is case-insensitive and often arrives wrapped in a resolver
    URL, and an arXiv version suffix denotes a *rendition* of a work rather
    than a different work — `2301.00001v1` and `v2` are one paper, so the
    version is stripped into its own field instead of forking the identity.
    """

    text = raw.strip()
    if not text:
        raise ValueError("a source identifier is required")

    for prefix in _DOI_PREFIXES:
        if text.lower().startswith(prefix.lower()):
            text = text[len(prefix) :]
            break
    else:
        for prefix in _ARXIV_PREFIXES:
            if text.lower().startswith(prefix.lower()):
                return _arxiv(text[len(prefix) :].removesuffix(".pdf"))
        for prefix in _OPENALEX_PREFIXES:
            if text.lower().startswith(prefix.lower()):
                return CanonicalId(IdentityScheme.OPENALEX, text[len(prefix) :].upper())
        if text.lower().startswith("local:"):
            return CanonicalId(IdentityScheme.LOCAL, text[len("local:") :])

    lowered = text.lower()
    if _DOI_SHAPE.match(lowered):
        return CanonicalId(IdentityScheme.DOI, lowered)
    if _ARXIV_NEW.match(text) or _ARXIV_OLD.match(text):
        return _arxiv(text)
    if _OPENALEX_SHAPE.match(text):
        return CanonicalId(IdentityScheme.OPENALEX, text.upper())
    if lowered.startswith(("http://", "https://")):
        return CanonicalId(IdentityScheme.URL, text)
    return CanonicalId(IdentityScheme.UNKNOWN, text)


def _arxiv(value: str) -> CanonicalId:
    """Parse an arXiv identifier, refusing anything that is not shaped like one.

    A declared scheme is a claim, not a credential. Accepting `arXiv:2305` just
    because it was labelled arXiv would put an identifier into the graph that
    can never resolve, and a source key that cannot be fetched is worse than an
    unknown one — it looks covered.
    """

    match = _ARXIV_VERSION.match(value)
    base, version = (
        (match.group("base"), match.group("version")) if match else (value, "")
    )
    if _ARXIV_NEW.match(base) or _ARXIV_OLD.match(base):
        return CanonicalId(IdentityScheme.ARXIV, base, version)
    return CanonicalId(IdentityScheme.UNKNOWN, value)


@dataclass(frozen=True)
class SourceIdentity:
    """A work, independent of where any particular copy of it came from."""

    source_id: str
    aliases: tuple[str, ...] = ()
    title: str = ""

    def __post_init__(self) -> None:
        if not self.source_id.strip():
            raise ValueError("source identity requires a canonical id")

    @property
    def keys(self) -> frozenset[str]:
        return frozenset((self.source_id, *self.aliases))


def merge_identities(
    identities: tuple[SourceIdentity, ...],
) -> tuple[SourceIdentity, ...]:
    """Collapse identities that share any alias into one work.

    A paper reached by DOI, by arXiv id and by an OpenAlex id is one paper. If
    those stay separate, every coverage and saturation count is inflated by the
    number of routes that happened to find it — which would make heterogeneous
    search look like knowledge growth.
    """

    groups: list[tuple[set[str], list[SourceIdentity]]] = []
    for identity in identities:
        keys = set(identity.keys)
        overlapping = [item for item in groups if item[0] & keys]
        if not overlapping:
            groups.append((keys, [identity]))
            continue
        merged_keys: set[str] = keys
        merged_members: list[SourceIdentity] = [identity]
        for item in overlapping:
            merged_keys |= item[0]
            merged_members.extend(item[1])
            groups.remove(item)
        groups.append((merged_keys, merged_members))

    resolved: list[SourceIdentity] = []
    for keys, members in groups:
        primary = sorted(members, key=lambda item: item.source_id)[0]
        title = next((item.title for item in members if item.title.strip()), "")
        resolved.append(
            SourceIdentity(
                source_id=primary.source_id,
                aliases=tuple(sorted(keys - {primary.source_id})),
                title=title,
            )
        )
    return tuple(sorted(resolved, key=lambda item: item.source_id))


@dataclass(frozen=True)
class ReadReceipt:
    """Evidence that a specific rendition was actually extracted from."""

    source_id: str
    content_digest: str
    schema_version: str
    frame_id: str
    contribution_ids: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        if not self.content_digest.strip() or not self.schema_version.strip():
            raise ValueError("a read receipt requires a content digest and schema")


class ReadDecision(str, Enum):
    """Whether this source still has to be read, and why."""

    UNSEEN = "UNSEEN"
    ALREADY_READ = "ALREADY_READ"
    CONTENT_CHANGED = "CONTENT_CHANGED"
    NEW_SCHEMA = "NEW_SCHEMA"
    NEW_FRAME = "NEW_FRAME"


def decide_read(
    source_id: str,
    content_digest: str,
    schema_version: str,
    frame_id: str,
    receipts: tuple[ReadReceipt, ...],
) -> ReadDecision:
    """Decide whether this source needs reading, given everything read before.

    `ALREADY_READ` requires an exact match on all four coordinates. That is
    deliberately strict: "we have seen this paper" is not the same claim as
    "we have extracted what this paper says about *this* question, under the
    *current* schema, from *this* version of the text". Collapsing those is how
    a system convinces itself it has covered material it only skimmed for a
    different purpose — and coverage is the one thing saturation rests on.
    """

    for_source = tuple(item for item in receipts if item.source_id == source_id)
    if not for_source:
        return ReadDecision.UNSEEN
    # Evaluate the whole receipt set, not the first hit: a source read under
    # several frames or schema versions has several receipts, and stopping at
    # whichever came first would report a re-read that is not needed, or worse,
    # skip one that is.
    same_content = tuple(
        item for item in for_source if item.content_digest == content_digest
    )
    if not same_content:
        return ReadDecision.CONTENT_CHANGED
    same_schema = tuple(
        item for item in same_content if item.schema_version == schema_version
    )
    if not same_schema:
        return ReadDecision.NEW_SCHEMA
    if any(item.frame_id == frame_id for item in same_schema):
        return ReadDecision.ALREADY_READ
    return ReadDecision.NEW_FRAME

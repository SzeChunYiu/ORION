from __future__ import annotations

import hashlib
import re
from collections.abc import Iterator
from dataclasses import dataclass
from pathlib import Path

from .identity import IdentityScheme, SourceIdentity, canonical_source_id, merge_identities

DEFAULT_SUFFIXES = (".tex", ".md", ".txt", ".bib", ".rst")
_SKIP_DIRECTORIES = frozenset(
    {".git", ".venv", "venv", "node_modules", "__pycache__", ".worktrees", ".mypy_cache",
     ".pytest_cache", ".ruff_cache", "site-packages", ".tox", "dist", "build"}
)
_MAX_BYTES = 4 * 1024 * 1024

_DOI = re.compile(r"10\.\d{4,9}/[-._;()/:a-zA-Z0-9]+")
_ARXIV = re.compile(
    r"(?:arXiv:|arxiv\.org/(?:abs|pdf)/)([a-zA-Z-]+(?:\.[A-Z]{2})?/\d{7}|\d{4}\.\d{4,5})(v\d+)?",
    re.IGNORECASE,
)
_TITLE = re.compile(r"\\title\{([^}]{4,200})\}|^#\s+(.{4,200})$", re.MULTILINE)


@dataclass(frozen=True)
class IndexedFile:
    """One file on disk, reduced to the work it is a copy of."""

    path: Path
    content_digest: str
    identity: SourceIdentity
    references: tuple[str, ...] = ()


def iter_corpus_files(
    root: Path, suffixes: tuple[str, ...] = DEFAULT_SUFFIXES
) -> Iterator[Path]:
    """Walk a corpus root, skipping directories that hold copies, not sources.

    Virtualenvs, caches and worktrees contain duplicates of material already
    indexed elsewhere. Including them would inflate every count with copies of
    the same content, which is the failure the content-addressed identity below
    exists to prevent — better not to manufacture the problem in the first place.
    """

    wanted = {item.lower() for item in suffixes}
    for path in sorted(root.rglob("*")):
        if any(part in _SKIP_DIRECTORIES for part in path.parts):
            continue
        if path.is_file() and path.suffix.lower() in wanted:
            yield path


def read_text_head(path: Path, limit: int = _MAX_BYTES) -> str:
    try:
        return path.read_bytes()[:limit].decode("utf-8", errors="replace")
    except OSError:
        return ""


def extract_references(text: str) -> tuple[str, ...]:
    """Pull the DOIs and arXiv ids a document *cites* out of its text.

    These are outbound citation edges, never aliases of the document itself.
    The distinction is load-bearing: identifiers in a document's text overwhelm-
    ingly belong to other works, so treating them as aliases would fuse a
    bibliography with all six works it cites — and, transitively through alias
    merging, fuse any two documents that happen to cite a common paper. Real
    corpus data produced exactly that on the first run.

    Self-identity cannot be established from arbitrary text, so a local file
    claims none: its identity is its content digest, and these are edges.
    """

    found: list[str] = []
    for match in _DOI.finditer(text):
        found.append(match.group(0).rstrip(".,;:)"))
    for match in _ARXIV.finditer(text):
        found.append(f"arXiv:{match.group(1)}")
    canonical: list[str] = []
    for raw in found:
        identity = canonical_source_id(raw)
        if identity.scheme in {IdentityScheme.DOI, IdentityScheme.ARXIV}:
            canonical.append(str(identity))
    return tuple(dict.fromkeys(canonical))


def _title(text: str) -> str:
    match = _TITLE.search(text)
    if not match:
        return ""
    return " ".join((match.group(1) or match.group(2) or "").split())


def index_file(path: Path) -> IndexedFile | None:
    """Index one file, keyed by its content rather than its location.

    A local file's canonical id is `local:<content digest>`. Two copies of one
    paper in two directories are therefore one work, and a file that moves keeps
    its identity. Keying on the path would make every copy and every move look
    like a new discovery.
    """

    try:
        payload = path.read_bytes()[:_MAX_BYTES]
    except OSError:
        return None
    if not payload.strip():
        return None
    digest = hashlib.sha256(payload).hexdigest()
    text = payload.decode("utf-8", errors="replace")
    return IndexedFile(
        path=path,
        content_digest=digest,
        identity=SourceIdentity(
            source_id=f"local:{digest[:16]}",
            title=_title(text),
        ),
        references=extract_references(text),
    )


def index_local_corpus(
    root: Path, suffixes: tuple[str, ...] = DEFAULT_SUFFIXES
) -> tuple[tuple[IndexedFile, ...], tuple[SourceIdentity, ...]]:
    """Index a corpus root, returning per-file records and the merged works."""

    files = tuple(
        item for item in (index_file(path) for path in iter_corpus_files(root, suffixes))
        if item is not None
    )
    return files, merge_identities(tuple(item.identity for item in files))

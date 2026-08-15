from __future__ import annotations

from pathlib import Path

from orion.knowledge.identity import merge_identities
from orion.knowledge.local import (
    extract_references,
    index_file,
    index_local_corpus,
    iter_corpus_files,
)

_CITING = r"""\title{A Study of Things}
We build on \cite{a} (arXiv:2301.00001) and on doi:10.1038/s41586-021-03819-3.
"""


def test_the_same_paper_in_two_places_is_one_work(tmp_path: Path) -> None:
    """Identity is content, not location: copies and moves are not discoveries."""

    body = "\\title{One Paper}\nidentical body text\n"
    (tmp_path / "a").mkdir()
    (tmp_path / "b").mkdir()
    (tmp_path / "a" / "paper.tex").write_text(body, encoding="utf-8")
    (tmp_path / "b" / "copy.tex").write_text(body, encoding="utf-8")

    files, works = index_local_corpus(tmp_path)
    assert len(files) == 2
    assert len(works) == 1
    assert files[0].identity.source_id == files[1].identity.source_id


def test_identifiers_in_a_document_are_citations_not_aliases(tmp_path: Path) -> None:
    """The defect real corpus data exposed on the first run.

    Treating identifiers found in text as aliases fused a bibliography with all
    six works it cited. Self-identity cannot be established from arbitrary text.
    """

    path = tmp_path / "citing.tex"
    path.write_text(_CITING, encoding="utf-8")
    indexed = index_file(path)

    assert indexed is not None
    assert indexed.identity.aliases == ()
    assert set(indexed.references) == {
        "arxiv:2301.00001",
        "doi:10.1038/s41586-021-03819-3",
    }


def test_two_documents_citing_the_same_paper_do_not_merge(tmp_path: Path) -> None:
    """The catastrophic case: alias merging is transitive, so this would have
    collapsed any two documents sharing a single reference into one work."""

    (tmp_path / "one.tex").write_text(
        "\\title{One}\nsee arXiv:2301.00001 for background\n", encoding="utf-8"
    )
    (tmp_path / "two.tex").write_text(
        "\\title{Two}\nalso see arXiv:2301.00001, unrelated work\n", encoding="utf-8"
    )
    files, works = index_local_corpus(tmp_path)

    assert len(works) == 2
    assert all(item.references == ("arxiv:2301.00001",) for item in files)
    # And the merge function agrees when handed those identities directly.
    assert len(merge_identities(tuple(item.identity for item in files))) == 2


def test_copies_inside_caches_and_worktrees_are_not_indexed(tmp_path: Path) -> None:
    """Those directories hold copies of material indexed elsewhere; counting
    them would manufacture the duplication the design exists to avoid."""

    (tmp_path / "real.tex").write_text("\\title{Real}\nbody\n", encoding="utf-8")
    for skipped in (".git", ".venv", "node_modules", ".worktrees", "__pycache__"):
        directory = tmp_path / skipped
        directory.mkdir()
        (directory / "copy.tex").write_text("\\title{Copy}\nbody\n", encoding="utf-8")

    assert [item.name for item in iter_corpus_files(tmp_path)] == ["real.tex"]


def test_an_empty_or_unreadable_file_yields_nothing(tmp_path: Path) -> None:
    (tmp_path / "blank.tex").write_text("   \n\n", encoding="utf-8")
    assert index_file(tmp_path / "blank.tex") is None
    assert index_file(tmp_path / "absent.tex") is None


def test_malformed_identifiers_in_text_are_not_promoted(tmp_path: Path) -> None:
    """A declared scheme is a claim, not a credential — same rule as identity."""

    assert extract_references("see arXiv:2305 and 10.1/x for details") == ()


def test_the_repository_papers_tree_indexes_cleanly() -> None:
    """Real-data smoke test: the corpus this system was validated against."""

    root = Path(__file__).resolve().parents[3] / "papers"
    files, works = index_local_corpus(root)
    assert files, "the papers tree is non-empty"
    assert len(works) == len({item.content_digest for item in files})
    assert all(item.aliases == () for item in works)

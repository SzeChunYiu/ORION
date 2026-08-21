"""Publication-source invariants for transitioned ORION P11-P14 papers."""

from pathlib import Path

from orion.programme.superiority_terminals import FUTURE_PAPER_DIRECTORIES

REPO_ROOT = Path(__file__).resolve().parents[3]
PAPER_IDS = ("P11", "P12", "P13", "P14")


def test_transitioned_papers_have_paired_markdown_and_latex_chapters() -> None:
    for paper_id in PAPER_IDS:
        root = REPO_ROOT / FUTURE_PAPER_DIRECTORIES[paper_id]
        readme = (root / "README.md").read_text(encoding="utf-8")
        if "NO_PROTECTED_RESULT" in readme:
            continue

        paper = root / "paper"
        main = paper / "main.tex"
        chapters = paper / "chapters"
        assert main.is_file(), f"{paper_id} lacks paper/main.tex"
        assert (paper / "Makefile").is_file(), f"{paper_id} lacks paper/Makefile"
        assert (paper / "references.bib").is_file(), f"{paper_id} lacks paper/references.bib"
        assert chapters.is_dir(), f"{paper_id} lacks paper/chapters"

        md_stems = {path.stem for path in chapters.glob("*.md")}
        tex_stems = {path.stem for path in chapters.glob("*.tex")}
        assert md_stems, f"{paper_id} has no chapter text sources"
        assert md_stems == tex_stems, (
            f"{paper_id} chapter pairing mismatch: md={sorted(md_stems)}, tex={sorted(tex_stems)}"
        )

        main_text = main.read_text(encoding="utf-8")
        assert "\\usepackage[pipeTables]{markdown}" in main_text
        for stem in sorted(md_stems):
            assert f"\\input{{chapters/{stem}.tex}}" in main_text, (
                f"{paper_id} main.tex does not include paired chapter {stem}"
            )
            wrapper = (chapters / f"{stem}.tex").read_text(encoding="utf-8")
            assert f"\\markdownInput{{chapters/{stem}.md}}" in wrapper, (
                f"{paper_id} {stem}.tex does not import its canonical Markdown text"
            )

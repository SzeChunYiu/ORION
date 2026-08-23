from pathlib import Path
import sys


HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

from audit_portfolio import audit  # noqa: E402
from run_dual_portfolio_audit import compare, run  # noqa: E402


def test_missing_manuscript_fails_closed(tmp_path: Path) -> None:
    paper = tmp_path / "papers" / "paper-01-example"
    paper.mkdir(parents=True)

    report = audit(tmp_path)

    assert report["portfolio_pass"] is False
    assert report["papers"][0]["structural_status"] == "INCOMPLETE"
    assert report["papers"][14]["structural_status"] == "MISSING"


def test_branding_missing_citation_and_input_are_reported(tmp_path: Path) -> None:
    manuscript = tmp_path / "papers" / "paper-01-example" / "manuscript"
    sections = manuscript / "sections"
    sections.mkdir(parents=True)
    (manuscript / "main.tex").write_text(
        "\\input{sections/chapter}\\n\\input{sections/missing}\\n",
        encoding="utf-8",
    )
    (sections / "chapter.tex").write_text(
        "ORION lives in this repository \\cite{missing-key}.\n",
        encoding="utf-8",
    )

    paper = audit(tmp_path)["papers"][0]

    assert paper["structural_status"] == "BLOCKED"
    assert paper["missing_citation_keys"] == ["missing-key"]
    assert paper["missing_inputs"][0]["input"] == "sections/missing"
    assert len(paper["branding_hits"]) == 1
    assert len(paper["codebase_hits"]) == 1


def test_dual_audit_is_answer_free_and_agrees_on_fixture(tmp_path: Path) -> None:
    manuscript = tmp_path / "papers" / "paper-01-example" / "manuscript"
    sections = manuscript / "sections"
    sections.mkdir(parents=True)
    (manuscript / "main.tex").write_text("\\input{sections/chapter}\n", encoding="utf-8")
    (sections / "chapter.tex").write_text("A bounded claim.\n", encoding="utf-8")

    result = run(tmp_path)

    assert result["terminal"] == "P1_P15_DUAL_SOURCE_AUDIT_AGREEMENT"
    assert result["lane_a"]["llm_calls"] == 0
    assert result["lane_b"]["llm_calls"] == 0
    assert result["lane_a"]["facts"]["P1"] == result["lane_b"]["facts"]["P1"]


def test_chapters_directory_is_a_canonical_tex_surface(tmp_path: Path) -> None:
    manuscript = tmp_path / "papers" / "paper-15-example" / "manuscript"
    chapters = manuscript / "chapters"
    chapters.mkdir(parents=True)
    (manuscript / "main.tex").write_text(
        "\\input{chapters/scope}\n", encoding="utf-8"
    )
    (chapters / "scope.tex").write_text("A bounded framework claim.\n", encoding="utf-8")

    paper = audit(tmp_path)["papers"][14]
    result = run(tmp_path)

    assert paper["structural_status"] == "STRUCTURAL_REVIEW"
    assert paper["chapter_tex_count"] == 1
    assert result["lane_a"]["facts"]["P15"] == result["lane_b"]["facts"]["P15"]
    assert result["lane_a"]["facts"]["P15"]["chapter_tex_count"] == 1


def test_dual_audit_disagreement_fails_closed() -> None:
    disagreements = compare(
        {"P1": {"main_tex": True}},
        {"P1": {"main_tex": False}},
    )

    assert disagreements == [
        {
            "paper_id": "P1",
            "lane_a": {"main_tex": True},
            "lane_b": {"main_tex": False},
        }
    ]

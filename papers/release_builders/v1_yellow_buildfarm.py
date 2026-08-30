#!/usr/bin/env python3
"""Build claim-preserving V1 yellow-paper release sources on the public ORION runner.

The source trees used here are Git-object identical to their ORION-paper V1
counterparts, except where this adapter deliberately applies a release-only
metadata/format repair documented in the canonical paper repository.
"""
from __future__ import annotations

import argparse
import re
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
AUTHOR = "SzeChunYiu"
AFFILIATION = "Stockholm University, Stockholm, Sweden"
EMAIL = "sze-chun.yiu@fysik.su.se"
FUNDING = "The author received no specific funding for this work."
COI = "The author declares no competing interests."
AI = (
    "During the preparation of this work, the author used OpenAI ChatGPT and "
    "related language-model tooling to support literature triage, code and "
    "manuscript auditing, organization, and language refinement. The author "
    "reviewed and edited all AI-assisted output, independently checked the "
    "scientific claims and cited sources against the underlying evidence, and "
    "takes full responsibility for the content of the article."
)
AUTHOR_CONTRIB = (
    "SzeChunYiu conceived and directed the study, curated the evidence, verified "
    "the analyses and claims, and wrote and revised the manuscript. OpenAI "
    "ChatGPT and related language-model tooling were used for literature triage, "
    "code and manuscript auditing, organization, language refinement, and portions "
    "of code/text production under author review. The author checked the resulting "
    "claims, calculations, citations, and final manuscript and takes full "
    "responsibility for the work."
)
JAR_ABSTRACT = (
    "Scientific falsification must retract claims by both derivation and evidence type. "
    "Boolean dependency graphs can preserve or remove reachability, but they cannot "
    "prevent a surviving derivation from inheriting authority it never earned. We "
    "introduce a finite typed authority calculus for positive conjunctive scientific "
    "rule systems. Claims carry subsets of a finite license universe; seeds declare "
    "licenses, rules transmit only licenses shared by all premises and permitted by an "
    "explicit cap, and directly refuted claims are assigned the empty label. The "
    "resulting monotone operator has a least fixed point on the finite powerset lattice.\n\n"
    "We prove finite convergence, rule-order independence, a typed proof-tree "
    "characterization, monotonicity under added refutations, and minimal typed "
    "retraction within the declared license algebra. The rule caps internalize "
    "nonpromotion: post-outcome repair cannot manufacture prospective authority, and "
    "bounded computation cannot manufacture theorem authority. Three cases instantiate "
    "the calculus for forecast falsification, query-specific information falsification, "
    "and bounded-computation nonpromotion. A reusable domain-agnostic evaluator "
    "independently reproduces the committed verdicts. An external X.509 trust-store "
    "study further shows that the target merge obstruction is non-vacuous, with 46 "
    "hybrid cases among 1,962 third-party OpenSSL-derived merge tasks. Its zero unsafe "
    "merges and zero needless rejections are analytic consequences of authorizing "
    "exactly the parent-authorized set, not detector-performance estimates. The "
    "contribution is therefore a scientific evidence-license specialization of donor "
    "fixed-point and provenance machinery, together with cap-preserving nonpromotion, "
    "executable evaluation, and external instantiation."
)
FOLDERS = {
    "03": "orion-03-typed-merge-falsification",
    "05": "orion-05-tare-expressivity",
    "12": "orion-12-open-world-scientific-discovery",
    "13": "orion-13-global-knowledge-portrait",
    "19": "orion-19-structured-epistemic-learning",
    "24": "orion-24-orion-rse",
}


def named_author_tex() -> str:
    return rf"\author{{{AUTHOR}\\{AFFILIATION}\\\texttt{{{EMAIL}}}}}"


def disclosure_tex(*, quantum: bool = False) -> str:
    if quantum:
        return (
            "\n\\section*{Author contributions and AI assistance}\n" + AUTHOR_CONTRIB
            + "\n\n\\section*{Funding}\n" + FUNDING
            + "\n\n\\section*{Competing interests}\n" + COI + "\n"
        )
    return (
        "\n\\section*{Statements and Declarations}\n"
        "\\noindent\\textbf{Funding.} " + FUNDING + "\n\n"
        "\\noindent\\textbf{Competing interests.} " + COI + "\n\n"
        "\\noindent\\textbf{Author contributions.} " + AUTHOR_CONTRIB + "\n\n"
        "\\noindent\\textbf{AI assistance disclosure.} " + AI + "\n"
    )


def insert_before_bibliography(tex: str, block: str) -> str:
    for marker in ("\\bibliographystyle", "\\bibliography", "\\end{document}"):
        i = tex.find(marker)
        if i >= 0:
            return tex[:i] + block + "\n" + tex[i:]
    raise ValueError("bibliography/end marker not found")


def copy_manuscript(folder: str, out: Path) -> Path:
    src = ROOT / "papers" / folder / "manuscript"
    dst = out / "source"
    if dst.exists():
        shutil.rmtree(dst)
    shutil.copytree(src, dst)
    for pattern in ("*.pdf", "*.aux", "*.log", "*.out", "*.bbl", "*.blg", "*.fls", "*.fdb_latexmk"):
        for p in dst.glob(pattern):
            p.unlink()
    return dst


def build03(out: Path) -> None:
    text = (ROOT / "papers" / FOLDERS["03"] / "MANUSCRIPT_V2.md").read_text(encoding="utf-8")
    title_line, body = text.split("\n", 1)
    title = title_line.lstrip("# ").strip()
    body, n = re.subn(
        r"## Abstract\n\n.*?\n\n## 1\. Introduction",
        "## Abstract\n\n" + JAR_ABSTRACT + "\n\n## 1. Introduction",
        body,
        count=1,
        flags=re.S,
    )
    if n != 1:
        raise ValueError("ORION-03 abstract replacement anchor missing")
    header = (
        "---\n"
        f"title: \"{title}\"\n"
        f"author: \"{AUTHOR}\"\n"
        "date: \"August 2026\"\ngeometry: margin=1in\nfontsize: 11pt\n---\n\n"
        f"**Affiliation:** {AFFILIATION}  \n**Contact:** {EMAIL}  \n\n"
        "**Keywords:** automated reasoning; scientific authority; provenance; truth maintenance; evidence licensing; falsification.\n\n"
    )
    declarations = (
        "\n## Statements and Declarations\n\n"
        f"**Funding.** {FUNDING}\n\n**Competing interests.** {COI}\n\n"
        f"**Author contributions.** {AUTHOR_CONTRIB}\n\n**AI assistance disclosure.** {AI}\n\n"
        "## Data and code availability\n\n"
        "The executable evaluator, frozen claim/evidence ledgers, external X.509 "
        "instantiation records, and reproduction instructions accompanying this paper "
        "are included in the ORION-03 paper package. Protected credentials or secrets "
        "are not required for the bounded results reported here.\n"
    )
    dst = out / "source"
    dst.mkdir(parents=True, exist_ok=True)
    (dst / "main.md").write_text(header + body + declarations, encoding="utf-8")


def build05(out: Path) -> None:
    dst = copy_manuscript(FOLDERS["05"], out)
    p = dst / "main.tex"
    tex = p.read_text(encoding="utf-8")
    old = r"\author{Working framework draft}"
    if old not in tex:
        raise ValueError("ORION-05 author anchor missing")
    tex = tex.replace(old, named_author_tex(), 1)
    p.write_text(insert_before_bibliography(tex, disclosure_tex(quantum=True)), encoding="utf-8")


def build12(out: Path) -> None:
    dst = copy_manuscript(FOLDERS["12"], out)
    tex = (dst / "ipm_submission.tex").read_text(encoding="utf-8")
    old = r"\author[1]{Anonymous authors}"
    if old not in tex:
        raise ValueError("ORION-12 anonymous author anchor missing")
    tex = tex.replace(old, r"\author[1]{SzeChunYiu}", 1)
    tex = tex.replace(r"\shortauthors{Anonymous authors}", r"\shortauthors{SzeChunYiu}", 1)
    tex = tex.replace("pdfauthor={Anonymous authors}", "pdfauthor={SzeChunYiu}")
    anchor = r"\author[1]{SzeChunYiu}"
    meta = (
        "\n\\affiliation[1]{organization={Stockholm University},city={Stockholm},country={Sweden}}"
        f"\n\\ead{{{EMAIL}}}\n\\nonumnote{{Contact: {EMAIL}}}\n"
    )
    tex = tex.replace(anchor, anchor + meta, 1)
    (dst / "main.tex").write_text(insert_before_bibliography(tex, disclosure_tex()), encoding="utf-8")


def build13(out: Path) -> None:
    dst = copy_manuscript(FOLDERS["13"], out)
    p = dst / "main.tex"
    tex = p.read_text(encoding="utf-8")
    old = r"\author{Working framework draft}"
    if old not in tex:
        raise ValueError("ORION-13 author anchor missing")
    tex = tex.replace(old, named_author_tex(), 1)
    p.write_text(insert_before_bibliography(tex, disclosure_tex()), encoding="utf-8")


def build19(out: Path) -> None:
    dst = copy_manuscript(FOLDERS["19"], out)
    p = dst / "main.tex"
    tex = p.read_text(encoding="utf-8")
    if r"\usepackage{tmlr}" not in tex or r"\author{Anonymous Authors}" not in tex:
        raise ValueError("ORION-19 preprint anchors missing")
    tex = tex.replace(r"\usepackage{tmlr}", r"\usepackage[preprint]{tmlr}", 1)
    tex = tex.replace(r"\author{Anonymous Authors}", named_author_tex(), 1)
    p.write_text(insert_before_bibliography(tex, disclosure_tex()), encoding="utf-8")


def build24(out: Path) -> None:
    dst = copy_manuscript(FOLDERS["24"], out)
    p = dst / "main.tex"
    tex = p.read_text(encoding="utf-8")
    old = r"\author{ORION-P14}"
    if old not in tex:
        raise ValueError("ORION-24 author anchor missing")
    tex = tex.replace(old, named_author_tex(), 1)
    p.write_text(insert_before_bibliography(tex, disclosure_tex()), encoding="utf-8")


BUILDERS = {"03": build03, "05": build05, "12": build12, "13": build13, "19": build19, "24": build24}


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--paper", choices=sorted(BUILDERS), required=True)
    ap.add_argument("--out", type=Path, required=True)
    args = ap.parse_args()
    args.out.mkdir(parents=True, exist_ok=True)
    BUILDERS[args.paper](args.out)
    print(f"ORION_{args.paper}_BUILD_SOURCE=PASS")

if __name__ == "__main__":
    main()

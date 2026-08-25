#!/usr/bin/env python3
"""Finalize abstract and PDF metadata in generated submission TeX."""

from __future__ import annotations

import sys
from pathlib import Path


def main() -> int:
    if len(sys.argv) != 2:
        raise SystemExit("usage: postprocess_submission_tex_v5.py PATH")

    path = Path(sys.argv[1])
    text = path.read_text(encoding="utf-8")
    heading = "\\hypertarget{abstract}{%\n\\section{Abstract}\\label{abstract}}\n\n"
    if text.count(heading) != 1:
        raise SystemExit(f"expected one Pandoc Abstract heading in {path}")
    if text.count("\\textbf{Keywords:}") != 1:
        raise SystemExit(f"expected one Keywords marker in {path}")

    text = text.replace(heading, "\\begin{abstract}\n", 1)
    text = text.replace(
        "\\textbf{Keywords:}",
        "\\end{abstract}\n\n\\noindent\\textbf{Keywords:}",
        1,
    )

    stem = path.stem
    metadata = {
        "Zero-Sum_Deletion_Normal_Forms_for_Multi-Tag_Quantum_Compilation": (
            "Exact normal forms for a finite Multi-Tag quantum-compilation grammar",
            "quantum compilation, block encoding, zero-sum sequences, sparse optimization",
        ),
        "Zero-Sum_Deletion_Certificates_versus_Intrinsic_Support_in_Quantum_Compilation": (
            "Certificate complexity and intrinsic support in quantum compilation",
            "quantum compilation, certificate complexity, support normalization, zero-sum deletion",
        ),
        "Low-Order_Decision_Certificates_and_Value-Estimation_Limits_in_Structured_Quantum_Compilation": (
            "Information limits for a structured Pauli partition compiler",
            "quantum compilation, low-order certificates, information lower bounds, Mobius inversion",
        ),
        "Typed_Evidence_Licenses_for_Finite_Positive_Rule_Graphs": (
            "Typed least-fixed-point semantics for finite positive scientific rule graphs",
            "automated reasoning, scientific evidence, provenance, belief revision",
        ),
        "Conditional_Width-One_Bounds_for_Generalized_Davenport_Constants_of_C5_Cubed": (
            "Conditional structural bounds for generalized Davenport constants of C5 cubed",
            "generalized Davenport constants, zero-sum sequences, elementary abelian groups",
        ),
    }
    if stem not in metadata:
        raise SystemExit(f"unknown submission stem for metadata: {stem}")
    subject, keywords = metadata[stem]
    author_marker = "  pdfauthor={Sze Chun Yiu},\n"
    if text.count(author_marker) != 1:
        raise SystemExit(f"expected one PDF author marker in {path}")
    text = text.replace(
        author_marker,
        author_marker
        + f"  pdfsubject={{{subject}}},\n"
        + f"  pdfkeywords={{{keywords}}},\n",
        1,
    )
    if stem.startswith("Conditional_Width-One"):
        start = "  pdftitle={"
        title_start = text.index(start)
        title_end = text.index("},\n", title_start) + 2
        text = (
            text[:title_start]
            + "  pdftitle={Conditional Width-One Bounds for Generalized Davenport Constants of C5 Cubed},\n"
            + text[title_end + 1 :]
        )
    if stem.startswith("Zero-Sum_Deletion_"):
        section_marker = "\\hypertarget{references}{%\n\\section{References}\\label{references}}"
        if text.count(section_marker) != 1:
            raise SystemExit(f"expected one References marker in {path}")
        extra_lines = 12 if "Certificates_versus" in stem else 8
        text = text.replace(
            section_marker,
            f"\\enlargethispage{{{extra_lines}\\baselineskip}}\n" + section_marker,
            1,
        )
    path.write_text(text, encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

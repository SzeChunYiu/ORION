#!/usr/bin/env python3
"""Generate the current ORION-16 AIJ/arXiv manuscript from the audited base.

The historical AIJ_MANUSCRIPT.tex remains an auditable source. This builder makes
only publication-state updates already supported by committed evidence:
- author/affiliation metadata supplied by the author;
- the V3 scientific-certificate theorem update;
- the current abstract describing the V3 bounded result;
- resolved funding and competing-interest statements.
"""

from __future__ import annotations

import pathlib
import re
import sys

HERE = pathlib.Path(__file__).resolve().parent
BASE = HERE / "AIJ_MANUSCRIPT.tex"
UPDATE = HERE / "V3_SCIENCE_UPDATE.tex"
OUT = HERE / "AIJ_MANUSCRIPT_CURRENT.tex"

AUTHOR_OLD = r"\author{Sze Chun Yiu\\Department of Physics, Stockholm University, Stockholm, Sweden\\\texttt{sze-chun.yiu@fysik.su.se}}"
AUTHOR_NEW = r"\author{SzeChunYiu\\Stockholm University, Stockholm, Sweden\\\texttt{sze-chun.yiu@fysik.su.se}}"

ABSTRACT = r"""\begin{abstract}
Scientific agents change more than propositional belief. Mature theory already supplies truth and dependency maintenance, incremental computation, typed effects, continuing authorization, provenance, workflow reproducibility, and execution-attestation certificates. We ask a narrower question: when such systems operate on scientifically certified state, can donor-native computational or operational validity remain unchanged while scientific admissibility changes because a load-bearing evidence, source-authority, claim-scope, or verification-epoch obligation has changed? The base contract proves root-inclusive repair safety, distinguishes support soundness from minimax minimality, separates preservation from revalidation, requires faithful footprints for history-aware commutation, and conserves hard obligations and non-escalating authority. A prospectively frozen certificate-semantics successor generalizes the typed-erasure separation over three bounded donor embeddings: dependency maintenance, effectful computation, and continuing authorization plus execution provenance. A forgetful map preserves each donor's native validity, yet whenever it erases a non-inert scientific certificate coordinate it need not reflect scientific admissibility. When all scientific obligations are discharged, the enrichment reduces exactly to donor-native validity; an ideal donor product carrying the same scientific coordinates and predicate is extensionally equivalent. A frozen finite model evaluates 1,536 states and records zero donor-preservation violations, 96 typed-erasure separation witnesses spanning all four scientific coordinates, 96 conservative-reduction cases with zero violations, zero ideal-product mismatches, 96 certificate-revocation countermodels, and 24 donor-valid no-alarm cases; a second implementation independently reproduces all headline counts. The contribution is a bounded scientific-admissibility enrichment and conservative-extension/separation theorem family, not generic certification, provenance, authorization, or deployed-agent superiority.
\end{abstract}"""

FINAL_DECLARATIONS = r"""\section*{Data and code availability}
The formal checkers, frozen countermodels, claim ledgers, and reproduction instructions supporting the bounded theorem claims are maintained in the public ORION repository. The V3 finite-model checker and its independent audit are included in the bound research record. Public repository availability is reported as reproducibility infrastructure, not as independent scientific verification. No human-subject or animal data are used in this theoretical study.

\section*{Funding}
The author received no specific funding for this work.

\section*{Competing interests}
The author declares no competing interests.

\begin{thebibliography}{99}"""


def fail(msg: str) -> int:
    print(f"ORION16_CURRENT_AIJ=FAIL\n- {msg}")
    return 1


def main() -> int:
    text = BASE.read_text(encoding="utf-8")
    update = UPDATE.read_text(encoding="utf-8").strip()

    if AUTHOR_OLD not in text:
        return fail("expected historical author line not found")
    text = text.replace(AUTHOR_OLD, AUTHOR_NEW, 1)

    abstract_pattern = re.compile(r"\\begin\{abstract\}.*?\\end\{abstract\}", re.S)
    if len(abstract_pattern.findall(text)) != 1:
        return fail("expected exactly one abstract block")
    text = abstract_pattern.sub(lambda _: ABSTRACT, text, count=1)

    marker = r"\section{Discussion and implications for AI systems}"
    if marker not in text:
        return fail("discussion insertion marker missing")
    if "Scientific-certificate semantics as a conservative enrichment" in text:
        return fail("V3 update already present in historical base")
    text = text.replace(marker, update + "\n\n" + marker, 1)

    declarations_pattern = re.compile(
        r"\\section\*\{Data, code, and competing-interest statements\}.*?\\begin\{thebibliography\}\{99\}",
        re.S,
    )
    if len(declarations_pattern.findall(text)) != 1:
        return fail("expected historical data/COI section not found")
    text = declarations_pattern.sub(lambda _: FINAL_DECLARATIONS, text, count=1)

    required = (
        "SzeChunYiu",
        "Stockholm University, Stockholm, Sweden",
        "sze-chun.yiu@fysik.su.se",
        "1,536 states",
        "96 typed-erasure separation witnesses",
        "zero ideal-product mismatches",
        "The author received no specific funding for this work.",
        "The author declares no competing interests.",
        "Declaration of generative AI",
    )
    for token in required:
        if token not in text:
            return fail(f"required release token missing: {token}")

    forbidden = (
        "supplied through the journal submission interface after author confirmation",
        "AUTHOR INPUT REQUIRED",
        "CORRESPONDING AUTHOR INPUT REQUIRED",
    )
    for token in forbidden:
        if token in text:
            return fail(f"release placeholder remains: {token}")

    OUT.write_text(text, encoding="utf-8")
    print("ORION16_CURRENT_AIJ=PASS")
    print(f"OUTPUT={OUT}")
    return 0


if __name__ == "__main__":
    sys.exit(main())

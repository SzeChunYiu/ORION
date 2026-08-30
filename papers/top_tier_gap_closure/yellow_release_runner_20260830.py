#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import pathlib
import re
import shutil
import subprocess
import sys

ROOT = pathlib.Path(__file__).resolve().parents[2]
BUILD = ROOT / "build" / "orion-paper-yellow"
AUTHOR = "SzeChunYiu"
AFFIL = "Stockholm University, Stockholm, Sweden"
EMAIL = "sze-chun.yiu@fysik.su.se"
FUNDING = "The author received no specific funding for this work."
COI = "The author declares no competing interests."
PUBLIC_COMMIT = "2dccbc5b3aee3c1f189ba63971f0873cf4ec3204"

AI_GENERIC = (
    "During the preparation of this work, the author used OpenAI ChatGPT and related "
    "language-model tooling to support literature triage, code and manuscript auditing, "
    "organization, and language refinement. The author reviewed and edited all AI-assisted "
    "output, independently checked the scientific claims and cited sources against the "
    "underlying evidence, and takes full responsibility for the content of the article."
)


def fail(msg: str) -> None:
    raise SystemExit("YELLOW_RELEASE=FAIL\n- " + msg)


def read(p: pathlib.Path) -> str:
    if not p.exists():
        fail(f"missing input: {p}")
    return p.read_text(encoding="utf-8", errors="replace")


def reset(out: pathlib.Path) -> None:
    if out.exists():
        shutil.rmtree(out)
    out.mkdir(parents=True, exist_ok=True)


def strip_internal_markdown(s: str) -> str:
    lines = s.splitlines()
    if lines and lines[0].startswith("# "):
        lines = lines[1:]
    internal_prefixes = (
        "**Paper ", "Scientific cut:", "Workflow cut:", "**Evidence freeze:",
        "**Submission status:", "**Recursively refined", "**Stretch target:",
        "**Fallback:", "**Stable ID:**", "**Paper issue:**", "**Programme:**",
    )
    while lines and (not lines[0].strip() or any(lines[0].startswith(x) for x in internal_prefixes)):
        lines = lines[1:]
    if lines and lines[0].strip() == "---":
        lines = lines[1:]
    s = "\n".join(lines).lstrip()
    s = re.split(r"\n## Publication decision record\n", s, maxsplit=1)[0].rstrip()
    return s


def named_markdown(source: pathlib.Path, out: pathlib.Path, title: str, extra_tail: str = "") -> None:
    body = strip_internal_markdown(read(source))
    meta = f'''---
title: "{title}"
author: "{AUTHOR}"
date: ""
geometry: margin=1in
colorlinks: false
---

**Affiliation:** {AFFIL}  
**Contact:** {EMAIL}

'''
    tail = f'''\n\n## Statements and declarations\n\n**Funding.** {FUNDING}\n\n**Competing interests.** {COI}\n\n**AI assistance disclosure.** {AI_GENERIC}\n'''
    out.write_text(meta + body + extra_tail + tail + "\n", encoding="utf-8")


def audit_text(s: str, required=(), forbidden=()) -> None:
    for t in required:
        if t.lower() not in s.lower():
            fail(f"required token missing: {t}")
    for t in forbidden:
        if t.lower() in s.lower():
            fail(f"forbidden token present: {t}")
    for pat in (r"\bTBD\b", r"TO BE INSERTED", r"PENDING_OFFICIAL_RECEIPT"):
        if re.search(pat, s, re.I):
            fail(f"release placeholder present: {pat}")


def write_receipt(out: pathlib.Path, paper: str, status: str, details: dict) -> None:
    receipt = {
        "schema": "ORIONPaper.PublicRunnerReleaseReceipt.v1",
        "paper": paper,
        "status": status,
        "source_repository": "SzeChunYiu/ORION",
        "source_commit": PUBLIC_COMMIT,
        "canonical_repository": "SzeChunYiu/ORION-paper",
        "scientific_authority_delta": "NONE",
        **details,
    }
    (out / "verification_receipt.json").write_text(json.dumps(receipt, indent=2) + "\n", encoding="utf-8")


def build03() -> None:
    out = BUILD / "ORION-03"; reset(out)
    source = ROOT / "papers/orion-03-typed-merge-falsification/MANUSCRIPT_V2.md"
    availability = (
        "\n\n## Data and code availability\n\n"
        "The evaluator, regression tests, external X.509 instantiation, evidence bindings, and "
        f"reproduction records supporting this bounded paper are available in the immutable public ORION source snapshot at commit `{PUBLIC_COMMIT}` under `papers/orion-03-typed-merge-falsification/`.\n"
    )
    named_markdown(source, out / "manuscript.md", "Typed Falsification-Aware Scientific Authority as a Least Fixed Point", availability)
    s = read(out / "manuscript.md")
    audit_text(s, (AUTHOR, AFFIL, EMAIL, "Data and code availability", "Journal of Automated Reasoning"), ("Publication decision record",))
    write_receipt(out, "ORION-03", "SOURCE_READY_FOR_JAR_AND_ARXIV_RENDER", {
        "source_path": str(source.relative_to(ROOT)),
        "source_blob_sha": "b3eb3a718bd0ed46969324c6a5a4b6d448fc2bc4",
        "primary_venue": "Journal of Automated Reasoning",
        "fallback": "ACM Transactions on Computational Logic",
        "arxiv_category": "cs.LO",
        "arxiv_license": "arXiv.org perpetual, non-exclusive license 1.0",
    })


def build05() -> None:
    out = BUILD / "ORION-05"; reset(out)
    source = ROOT / "papers/orion-05-tare-expressivity/MANUSCRIPT_V3_REFINED.md"
    s0 = read(source)
    if r"\kappa_{\mathrm{R6M}}=2" not in s0 or "one pinned comm-$s2$ lemma short" in s0:
        fail("ORION-05 authoritative refined theorem source not closed")
    body = strip_internal_markdown(s0)
    body = body.replace(
        "`REPRODUCE.md` gives the intended clean-checkout reproduction route. Before archival publication, the cited code/results should be tagged or deposited in a DOI-minting repository and the permanent identifier inserted here.",
        f"`REPRODUCE.md` gives the clean-checkout reproduction route. The submission release is bound to the immutable public ORION source snapshot at commit `{PUBLIC_COMMIT}`; the cited proof, checker, protocol, and result paths above are resolved relative to that snapshot."
    )
    meta = f'''---\ntitle: "A Sharp Support-Two Normal Form for Shared-Tag TARE Quantum Compilation"\nauthor: "{AUTHOR}"\ndate: ""\ngeometry: margin=1in\ncolorlinks: false\n---\n\n**Affiliation:** {AFFIL}  \n**Contact:** {EMAIL}\n\n'''
    tail = f'''\n\n## Statements and declarations\n\n**Funding.** {FUNDING}\n\n**Competing interests.** {COI}\n\n**AI assistance disclosure.** {AI_GENERIC}\n'''
    (out / "manuscript.md").write_text(meta + body + tail + "\n", encoding="utf-8")
    s = read(out / "manuscript.md")
    audit_text(s, (AUTHOR, AFFIL, EMAIL, "kappa", "Code and data availability", PUBLIC_COMMIT), ("one pinned comm-$s2$ lemma short", "Working framework draft", "permanent identifier inserted here"))
    write_receipt(out, "ORION-05", "SOURCE_READY_FOR_PRX_QUANTUM_AND_ARXIV_RENDER", {
        "source_path": str(source.relative_to(ROOT)),
        "source_blob_sha": "c896763b09c0566c06e815b05d27f9a5c629abfc",
        "primary_venue": "PRX Quantum",
        "fallback": "npj Quantum Information; Quantum",
        "arxiv_category": "quant-ph",
        "arxiv_license": "CC BY 4.0",
        "exact_head_replay": "papers/orion-05-tare-expressivity/independent_human_proof_sanity.py",
        "literature_closure": "papers/orion-05-tare-expressivity/LITERATURE_CLOSURE_2026-08-30.md",
    })


def patch12(text: str) -> str:
    if r"\newcommand{\idt}" not in text:
        text = text.replace(r"\urlstyle{same}", r'''\urlstyle{same}
% Release-only identifier line-breaking helper.
\newcommand{\idt}[1]{\path{#1}}''')
    if r"\label{sec:public-screening-transport}" not in text:
        text = text.replace(r'''\input{sections/results}

\section{Related work}''', r'''\input{sections/results}
\label{sec:public-screening-transport}

\section{Related work}''')
    text = text.replace(r'''Table~\ref{tab:p2-external-boundaries} keeps these results visible
without averaging incompatible authority levels.''', r'''These bounded, adverse, and provider-invalid findings remain reported
separately rather than averaged across incompatible authority levels.''')
    return text


def build12() -> None:
    out = BUILD / "ORION-12"; reset(out)
    src = ROOT / "papers/orion-12-open-world-scientific-discovery/manuscript"
    anon = out / "anonymous_source"; shutil.copytree(src, anon)
    tex = patch12(read(anon / "ipm_submission.tex"))
    (anon / "ipm_submission.tex").write_text(tex, encoding="utf-8")
    if "tab:p2-external-boundaries" in tex or r"\label{sec:public-screening-transport}" not in tex:
        fail("ORION-12 release-only reference repair failed")
    named = out / "arxiv_source"; shutil.copytree(anon, named)
    n = read(named / "ipm_submission.tex")
    n = n.replace("pdfauthor={Anonymous authors}", "pdfauthor={SzeChunYiu}")
    old = r"\author[1]{Anonymous authors}"
    new = r'''\author[1]{SzeChunYiu}
\affiliation[1]{organization={Stockholm University},city={Stockholm},country={Sweden}}
\nonumnote{Contact: sze-chun.yiu@fysik.su.se.}'''
    if old not in n: fail("ORION-12 anonymous author anchor missing")
    n = n.replace(old, new).replace(r"\shortauthors{Anonymous authors}", r"\shortauthors{SzeChunYiu}")
    old_ai = r'''\section*{Declaration of generative AI and AI-assisted technologies}

During preparation of this work, the authors used OpenAI ChatGPT to support
literature searching, source checking, reproducibility review, manuscript
editing, and submission-package preparation. The tool was not treated as an
author and did not replace scientific judgment. Result-bearing statements and
citations were checked against the archived evidence and primary-source
records. The authors remain responsible for the article's content.
'''
    new_ai = r'''\section*{Declaration of generative AI and AI-assisted technologies in the manuscript preparation process}
During the preparation of this work, the author used OpenAI ChatGPT and related language-model tooling to support literature triage, source checking, reproducibility review, code and manuscript auditing, organization, and language refinement. The author reviewed and edited all AI-assisted output, independently checked the scientific claims and cited sources against the underlying evidence, and takes full responsibility for the content of the article.

\section*{Funding}
The author received no specific funding for this work.

\section*{Competing interests}
The author declares no competing interests.
'''
    if old_ai not in n: fail("ORION-12 AI declaration anchor missing")
    n = n.replace(old_ai, new_ai).replace("Anonymous authors", "SzeChunYiu")
    (named / "arxiv.tex").write_text(n, encoding="utf-8")
    combined = n + read(named / "novelty_refresh_2026.bib")
    audit_text(combined, (AUTHOR, "Stockholm University", EMAIL, "voorhees2020treccovid", FUNDING, COI), ("tab:p2-external-boundaries",))
    write_receipt(out, "ORION-12", "SOURCES_READY_FOR_IPM_ANONYMOUS_AND_ARXIV_RENDER", {
        "source_path": "papers/orion-12-open-world-scientific-discovery/manuscript/ipm_submission.tex",
        "source_blob_sha": "5bf7cc7cefa830c54f805a610821fa4cd2b72c37",
        "release_adapter_scientific_authority_delta": "NONE",
        "primary_venue": "Information Processing & Management",
        "arxiv_category": "cs.IR",
        "arxiv_license": "arXiv.org perpetual, non-exclusive license 1.0",
    })


def build13() -> None:
    out = BUILD / "ORION-13"; reset(out)
    src = ROOT / "papers/orion-13-global-knowledge-portrait/manuscript"
    stage = out / "scoped_source"; shutil.copytree(src, stage)
    tex = read(stage / "main.tex")
    tex = tex.replace(r"\title{Scientific Identity Authority for Recoverable Cross-Domain Knowledge Integration}" + "\n", "")
    old = r"\author{Working framework draft}"
    if old not in tex: fail("ORION-13 author anchor missing")
    tex = tex.replace(old, r"\author{SzeChunYiu\\Stockholm University, Stockholm, Sweden\\\texttt{sze-chun.yiu@fysik.su.se}}")
    for block in (
        r'''\section{Epistemic portrait envelope theory}
\label{sec:envelope}
\input{sections/36-partial-identification-theory}

''',
        r'''% These four fragments own their own \section/\label declarations.
\input{sections/56-p3x-successor}
\input{sections/57-successor-correspondence-interface}

''',
    ):
        if block not in tex: fail("ORION-13 successor-removal anchor missing")
        tex = tex.replace(block, "")
    anchor = r"\bibliographystyle{plain}"
    declarations = rf'''\section*{{Statements and declarations}}
\textbf{{Funding.}} {FUNDING}

\textbf{{Competing interests.}} {COI}

\textbf{{AI assistance disclosure.}} {AI_GENERIC}

'''
    tex = tex.replace(anchor, declarations + anchor)
    (stage / "main.tex").write_text(tex, encoding="utf-8")
    stable = "https://github.com/SzeChunYiu/ORION/tree/fdd913d6042e2dba605bec3281c42c85a7aee22b/papers/orion-13-global-knowledge-portrait"
    availability = rf'''\section{{Data and code availability}}
\label{{sec:availability}}
The public, immutable scientific source snapshot for this scoped paper is
\url{{{stable}}}. It binds the public-reference protocols, frozen datasets,
evaluator implementations, confirmatory result receipts, independent verification records, and checksum manifests.
Where third-party source text cannot be redistributed, the archive retains source identity, version, locator, and content commitments instead. The archive does not contain the unexecuted expert annotations and does not authorize raw-text extraction superiority or downstream answer-quality claims.
'''
    (stage / "sections/60-availability.tex").write_text(availability, encoding="utf-8")
    audit_text(tex + availability, (AUTHOR, AFFIL, EMAIL, stable, FUNDING, COI), ("Working framework draft", "36-partial-identification-theory", "56-p3x-successor", "57-successor-correspondence-interface"))
    write_receipt(out, "ORION-13", "SCOPED_SOURCE_READY_FOR_SWJ_AND_ARXIV_RENDER", {
        "source_entry_blob_sha": "eed53fb760b116a5505927b380d4464b973b00d8",
        "scoped_terminal": "PEER_REVIEW_READY_SCOPED_C5_C9",
        "primary_venue": "Semantic Web Journal",
        "fallback": "Journal of Web Semantics",
        "arxiv_category": "cs.AI",
        "stable_resource": stable,
        "excluded_successor_sections": ["36-partial-identification-theory", "56-p3x-successor", "57-successor-correspondence-interface"],
    })


def build19() -> None:
    out = BUILD / "ORION-19"; reset(out)
    src = ROOT / "papers/orion-19-structured-epistemic-learning/manuscript"
    anon = out / "anonymous_source"; shutil.copytree(src, anon)
    a = read(anon / "main.tex")
    disclosure = r"\footnotetext{AI assistance disclosure: General-purpose language-model tools, including OpenAI ChatGPT, were used for literature triage, code and manuscript auditing, organization, and language refinement. All scientific claims, citations, analyses, and final text were reviewed against the underlying evidence by the human author, who retains full responsibility. The language-model tools are not authors and are not treated as scientific authority.}"
    if disclosure not in a:
        a = a.replace(r"\maketitle", r"\maketitle" + "\n" + disclosure, 1)
    (anon / "main.tex").write_text(a, encoding="utf-8")
    named = out / "arxiv_source"; shutil.copytree(anon, named)
    n = read(named / "main.tex")
    n = n.replace(r"\usepackage{tmlr}", r"\usepackage[preprint]{tmlr}", 1)
    n = n.replace(r"\author{Anonymous Authors}", r"\author{SzeChunYiu\\Stockholm University, Stockholm, Sweden\\\texttt{sze-chun.yiu@fysik.su.se}}", 1)
    anchor = r"\bibliographystyle{plainnat}"
    decl = rf'''\section*{{Funding}}
{FUNDING}
\section*{{Competing interests}}
{COI}
'''
    n = n.replace(anchor, decl + anchor)
    (named / "main.tex").write_text(n, encoding="utf-8")
    audit_text(a, ("Anonymous Authors", "AI assistance disclosure"), (AUTHOR, EMAIL, AFFIL, "github.com/SzeChunYiu"))
    audit_text(n, (AUTHOR, AFFIL, EMAIL, FUNDING, COI), ("\\author{Anonymous Authors}",))
    write_receipt(out, "ORION-19", "SOURCES_READY_FOR_TMLR_ANONYMOUS_AND_ARXIV_RENDER", {
        "public_source_entry_blob_sha": "abb1ad0a9055a63713ae3f025317633d3a7a4b8b",
        "canonical_review_entry_blob_sha": "4482380f2fd0dac0b70b502573fdb0b55999e57d",
        "canonical_delta": "anonymous AI disclosure footnote only; scientific claims unchanged",
        "primary_venue": "Transactions on Machine Learning Research",
        "arxiv_category": "cs.AI",
        "exact_head_replay": "papers/orion-19-structured-epistemic-learning/reproduce_final.py",
    })


def resolve24() -> None:
    out = BUILD / "ORION-24"; reset(out)
    manuscript = ROOT / "papers/orion-24-orion-rse/MANUSCRIPT.md"
    binding = ROOT / "papers/orion-23-responsibility-carrying-state/P13_P14_CONSOLIDATION_SCOPE_BINDING_V1.json"
    m = read(manuscript); b = json.loads(read(binding))
    if b.get("disposition") != "CONSOLIDATE_LIFECYCLE_CONTRACT_SAFETY" or b.get("p14_separate_75_paper") is not False:
        fail("ORION-24 current consolidation authority not found")
    normalized = " ".join(m.lower().split())
    for t in ("not a separate paper at the 75+ bar", "external campaign", "cannot_check"):
        if t not in normalized:
            fail(f"ORION-24 canonical manuscript missing consolidation boundary: {t}")
    write_receipt(out, "ORION-24", "RESOLVED_BY_CONSOLIDATION_NOT_STANDALONE_SUBMISSION", {
        "source_blob_sha": "d2856f3be0be5b5711e8c1e48ef6f8a67ad8fb93",
        "disposition": b["disposition"],
        "p14_separate_75_paper": False,
        "consolidated_with": "ORION-23",
        "current_scientific_terminal_retained": "P14C_SPECIFICATION_SEPARATED_GOVERNANCE_CONFORMANCE_SUPPORTED",
        "standalone_release_action": "DO_NOT_SUBMIT_AS_SEPARATE_75_PLUS_PAPER",
        "successor_gate": b["external_campaign_state"],
    })


def main() -> int:
    ap = argparse.ArgumentParser(); ap.add_argument("paper", choices=["03", "05", "12", "13", "19", "24"]); ns = ap.parse_args()
    {"03": build03, "05": build05, "12": build12, "13": build13, "19": build19, "24": resolve24}[ns.paper]()
    print(f"YELLOW_RELEASE=PASS paper={ns.paper}")
    return 0

if __name__ == "__main__":
    sys.exit(main())

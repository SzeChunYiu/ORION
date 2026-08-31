#!/usr/bin/env python3
"""Build the six authority-matched publication packages.

The script is intentionally additive: historical manuscripts and evidence stay
in place, while each paper receives one unambiguous filing directory.  Package
manifests bind payload bytes, never the future Git commit that will contain
them.
"""

from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import tempfile
import zipfile
import platform


ROOT = Path(__file__).resolve().parents[3]
DATE = "2026-08-31"
EPOCH = (1980, 1, 1, 0, 0, 0)
AUTHOR = "Sze Chun Yiu"
EMAIL = "sze-chun.yiu@fysik.su.se"
AFFILIATION = "Independent Researcher"


SPECS = {
    "ORION-13": {
        "slug": "orion-13-global-knowledge-portrait",
        "title": "Coordinate-Governed Mapping of Source-Local Scientific Projections",
        "venue": "Semantic Web Journal",
        "article_type": "Full research paper",
        "identity": "identified_transparent_review",
        "authority": "SCOPED_PUBLICATION_TRACK_V1.md",
        "terminal": "P3_C5_C9_REPLICATED_MAPPING__P3_C10_C11_EXACT_IDENTITY_AUTHORITY",
        "source_kind": "orion13",
        "requirements": "https://www.semantic-web-journal.net/authors",
        "human": [
            "Author must complete the journal-specific paragraph-level AI-provenance review and approve the exact disclosure.",
            "Confirm affiliation/address and ORCID disposition in the portal.",
            "Bind an immutable public review-resource URL before upload.",
            "Confirm funding, conflicts, originality and no parallel review.",
        ],
    },
    "ORION-14": {
        "slug": "orion-14-verified-scientific-discovery",
        "title": "Non-Escalating Scientific Authority under Content-Bound Evidence and Protected Evaluation",
        "venue": "Transactions on Machine Learning Research",
        "article_type": "Research article",
        "identity": "double_blind",
        "authority": "PUBLICATION_FREEZE_ADDENDUM_V1.md",
        "terminal": "P4_PROTECTED_AUTHORITY_V2_BOUNDED__H3_NOT_SUPPORTED",
        "source_kind": "orion14",
        "requirements": "https://jmlr.org/tmlr/author-guide.html",
        "human": [
            "Confirm exact author set, OpenReview profiles, affiliations, conflicts and funding in the portal.",
            "Replace the placeholder OpenReview identifier only after the portal creates it.",
            "Approve CC BY 4.0 licensing and originality/no-parallel-review declarations.",
        ],
    },
    "ORION-19": {
        "slug": "orion-19-structured-epistemic-learning",
        "title": "Diagnosing Learning-System Failures Before Escalating Compute",
        "venue": "Transactions on Machine Learning Research",
        "article_type": "Research article",
        "identity": "double_blind",
        "authority": "PUBLICATION_FREEZE_ADDENDUM_V1.md",
        "terminal": "P9_BOUNDED_CAUSAL_DIAGNOSTIC_PEER_REVIEW_READY",
        "source_kind": "orion19",
        "requirements": "https://jmlr.org/tmlr/author-guide.html",
        "human": [
            "Confirm exact author set, OpenReview profiles, affiliations, conflicts and funding in the portal.",
            "Replace the placeholder OpenReview identifier only after the portal creates it.",
            "Approve CC BY 4.0 licensing and originality/no-parallel-review declarations.",
        ],
    },
    "ORION-21": {
        "slug": "orion-21-state-as-computation",
        "title": "State as Computation: Moving Structural Search between Representation Construction and Downstream Reasoning",
        "venue": "Transactions on Machine Learning Research",
        "article_type": "Research article",
        "identity": "double_blind",
        "authority": "P11_ACTIVE_CLAIM_AUTHORITY_V2.json",
        "terminal": "P11_WIDTH_CONDITIONED_AUTHORITY_SUPPORTED",
        "source_kind": "orion21",
        "requirements": "https://jmlr.org/tmlr/author-guide.html",
        "human": [
            "Confirm exact author set, OpenReview profiles, affiliations, conflicts and funding in the portal.",
            "Replace the placeholder OpenReview identifier only after the portal creates it.",
            "Approve CC BY 4.0 licensing and originality/no-parallel-review declarations.",
        ],
    },
    "ORION-23": {
        "slug": "orion-23-responsibility-carrying-state",
        "title": "Responsibility-Carrying State: Auditable Sufficiency, Reopen Contracts, and Safe State Reuse",
        "venue": "Autonomous Agents and Multi-Agent Systems",
        "article_type": "Regular paper",
        "identity": "identified",
        "authority": "P13_ACTIVE_CLAIM_AUTHORITY_V3.json",
        "terminal": "P13_CONTROLLED_COMPOSED_SAFETY_EFFICACY_AUTHORITY_SUPPORTED",
        "source_kind": "orion23",
        "requirements": "https://link.springer.com/journal/10458/submission-guidelines",
        "human": [
            "Confirm city/country, postal address and ORCID disposition for the title page and portal.",
            "Approve author contribution, funding, competing-interest, originality and AI-use declarations.",
            "Confirm that the repository URL or archive PID entered at filing resolves for anonymous readers.",
        ],
    },
    "ORION-24": {
        "slug": "orion-24-orion-rse",
        "title": "Fail-Closed Evaluation Contracts for Autonomous Research Software Engineering",
        "venue": "Autonomous Agents and Multi-Agent Systems",
        "article_type": "Viewpoint",
        "identity": "identified",
        "authority": "WAVE3_PUBLICATION_DISPOSITION_V1.json",
        "terminal": "ORION24_EXTERNAL_ACQUISITION_BLOCKED__EXECUTABLE_HANDOFF_COMPLETE",
        "source_kind": "orion24",
        "requirements": "https://link.springer.com/journal/10458/submission-guidelines",
        "human": [
            "Confirm the JAAMAS Viewpoint routing with the handling editor before upload.",
            "Confirm city/country, postal address and ORCID disposition for the title page and portal.",
            "Approve author contribution, funding, competing-interest, originality and AI-use declarations.",
        ],
    },
}


def run(*args: str, cwd: Path | None = None) -> str:
    env = os.environ.copy()
    env["SOURCE_DATE_EPOCH"] = "315532800"
    result = subprocess.run(args, cwd=cwd or ROOT, env=env, check=False, text=True,
                            encoding="utf-8", errors="replace",
                            stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    if result.returncode:
        raise RuntimeError(f"command failed ({result.returncode}) in {cwd or ROOT}: {' '.join(args)}\n{result.stdout[-12000:]}")
    return result.stdout


def sha(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def deterministic_zip(source: Path, target: Path) -> None:
    target.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(target, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=9) as zf:
        for path in sorted(p for p in source.rglob("*") if p.is_file()):
            rel = path.relative_to(source).as_posix()
            info = zipfile.ZipInfo(rel, EPOCH)
            info.compress_type = zipfile.ZIP_DEFLATED
            info.external_attr = 0o100644 << 16
            zf.writestr(info, path.read_bytes())


def copytree(src: Path, dst: Path, ignore_generated: bool = True) -> None:
    ignored = {"main.pdf", "main.log", "main.aux", "main.fls", "main.fdb_latexmk",
               "main.out", "main.bbl", "main.blg", "main.markdown.lua", "main.markdown.out"}
    for path in sorted(src.rglob("*")):
        if not path.is_file() or (ignore_generated and path.name in ignored):
            continue
        out = dst / path.relative_to(src)
        out.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(path, out)


def git_file(rev: str, path: str) -> bytes:
    return subprocess.check_output(["git", "show", f"{rev}:{path}"], cwd=ROOT)


def source_orion13(dst: Path) -> Path:
    archive = ROOT / "papers/orion-13-global-knowledge-portrait/journal_package/wave1_current/source.zip"
    with zipfile.ZipFile(archive) as zf:
        zf.extractall(dst)
    manuscript = dst / "manuscript"
    main = manuscript / "main.tex"
    text = main.read_text()
    text = text.replace("\\input{sections/06-results}", "\\input{sections/55-exact-contract-result}\n\\input{sections/06-results}")
    main.write_text(text)
    abstract = manuscript / "sections/00-abstract.tex"
    atext = abstract.read_text().replace(
        "The evidence concerns structured mapping decisions only;",
        "In a separate frozen 400-contract battery, the rule scored 400/400 versus 250/400 for a donor-complete product and 50/400 for a compensatory product; an information-equivalent typed product tied at 400/400. The evidence concerns structured mapping decisions only;",
    ).replace(
        "The paired\ndifference was $-0.1875$ with a 95\\% bootstrap interval of",
        "The paired\ndifference was $-0.1875$ with a fixed-panel bootstrap diagnostic of",
    )
    abstract.write_text(atext)
    for section in (manuscript / "sections").glob("*.tex"):
        section_text = section.read_text()
        section_text = section_text.replace(
            "95\\% bootstrap interval",
            "fixed-panel bootstrap diagnostic interval",
        ).replace(
            "95\\% paired interval",
            "fixed-panel paired diagnostic interval",
        )
        section.write_text(section_text)
    write(manuscript / "sections/55-exact-contract-result.tex", r"""\section{Exact-contract identity-authority result}
\label{sec:exact-contract}
A separately frozen finite battery asks whether the decision relation is merely
the product of its donor coordinates. Across 400 exact contracts, the complete
relation is correct on 400, a donor-complete product on 250, and a compensatory
product on 50. An information-equivalent typed product is also correct on all
400. The tie is load-bearing: the experiment supports the registered decision
scope and an exact coordinate-level implementation, not universal necessity of
the chosen syntax or representation. The public-reference ablations are zero in
their registered cells, and all six false-merge discordances occur in one case
family. Intervals and tests are therefore fixed-panel diagnostics rather than
population uncertainty. Neither battery measures raw-text extraction,
downstream answer quality, or deployed integration performance.
""")
    return manuscript


def source_orion14(dst: Path) -> Path:
    rev = "46a3a4f893ac936cb1f1215494c9662ed1a5c66e"
    base = "papers/paper-04-verified-scientific-discovery/manuscript"
    manuscript = dst / "manuscript"
    manuscript.mkdir(parents=True)
    (manuscript / "main.tex").write_bytes(git_file(rev, f"{base}/main.tex"))
    (manuscript / "bibliography.bib").write_bytes(git_file(rev, f"{base}/bibliography.bib"))
    shutil.copy2(ROOT / "papers/orion-14-verified-scientific-discovery/manuscript/tmlr.sty", manuscript / "tmlr.sty")
    shutil.copy2(ROOT / "papers/orion-14-verified-scientific-discovery/manuscript/tmlr.bst", manuscript / "tmlr.bst")
    for folder in ("figures", "tables"):
        copytree(ROOT / f"papers/orion-14-verified-scientific-discovery/{folder}", dst / folder)
    main = manuscript / "main.tex"
    text = main.read_text()
    text = text.replace(r"\newcommand{\cannot}{\texttt{CANNOT\_CHECK}\xspace}", r"\newcommand{\cannot}{undetermined\xspace}")
    text = text.replace(r"\newcommand{\blockstate}{\texttt{BLOCK}\xspace}", r"\newcommand{\blockstate}{blocked\xspace}")
    text = text.replace(r"\newcommand{\promote}{\texttt{PROMOTE}\xspace}", r"\newcommand{\promote}{promotion\xspace}")
    text = text.replace("the repaired ORION subject", "the non-escalating pipeline")
    text = text.replace("ORION produced", "The non-escalating pipeline produced")
    text = text.replace("ORION and", "the non-escalating pipeline and")
    text = text.replace("for ORION and", "for the non-escalating pipeline and")
    text = text.replace("ORION's", "The pipeline's")
    start = text.index("\\section{Reproducibility and availability}")
    end = text.index("\\section{Conclusion}", start)
    replacement = r"""\section{Reproducibility and availability}
The anonymous review supplement contains the frozen public attack slice,
per-case verdicts, comparator and ablation configuration, headline tables and an
independent recomputation script. It reconstructs every number reported here
without exposing protected labels or author identity. Exact execution-custody
identifiers are withheld from the double-blind manuscript and will be deposited
with the identified archival record after review.

The 360 case-level pairs form a fixed panel nested within 12 attack families.
The reported case-resampled interval is descriptive. A family-level sensitivity
analysis has six discordant families in the favorable direction and none in the
reverse direction (exact sign test $p=.031$); the family bootstrap interval for
the false-promotion difference is $[-0.75,-0.25]$. Direction is supported more
strongly than the precision suggested by the case-level interval.

"""
    text = text[:start] + replacement + text[end:]
    appendix = text.find("\\appendix")
    if appendix >= 0:
        text = text[:appendix] + "\\end{document}\n"
    main.write_text(text)
    return manuscript


def source_orion19(dst: Path) -> Path:
    archive = ROOT / "papers/orion-19-structured-epistemic-learning/journal_package/wave1_current/source.zip"
    with zipfile.ZipFile(archive) as zf:
        zf.extractall(dst)
    return dst


def source_orion21(dst: Path) -> Path:
    manuscript = dst / "manuscript"
    copytree(ROOT / "papers/orion-21-state-as-computation/manuscript", manuscript)
    shutil.copy2(ROOT / "papers/orion-14-verified-scientific-discovery/manuscript/tmlr.sty", manuscript / "tmlr.sty")
    main = manuscript / "main.tex"
    text = main.read_text()
    text = text.replace("\\documentclass[11pt]{article}\n\\usepackage[margin=1in]{geometry}", "\\documentclass[10pt]{article}\n\\usepackage{tmlr}")
    text = text.replace("\\date{21 August 2026}", "\\def\\month{08}\n\\def\\year{2026}\n\\def\\openreview{\\url{https://openreview.net/}}")
    main.write_text(text)
    conclusion = manuscript / "sections/08-limitations-discussion-conclusion.md"
    conclusion.write_text(conclusion.read_text().replace(
        " The repository control-plane binding remains `P11_ACTIVE_CLAIM_AUTHORITY_V2.json`; this identifier is not part of the reader-facing scientific claim.",
        "",
    ))
    return manuscript


def source_orion23(dst: Path) -> Path:
    manuscript = dst / "manuscript"
    copytree(ROOT / "papers/orion-23-responsibility-carrying-state/manuscript", manuscript)
    main = manuscript / "main.tex"
    text = main.read_text().replace(
        "\\author{Anonymous authors}",
        f"\\author{{{AUTHOR}\\\\{AFFILIATION}\\\\\\texttt{{{EMAIL}}}}}",
    ).replace("P11 build", "build").replace(
        "The chapter Markdown", "The manuscript Markdown"
    ).replace("\\date{21 August 2026}", "\\date{}\n\\hypersetup{pdftitle={Responsibility-Carrying State: Auditable Sufficiency, Reopen Contracts, and Safe State Reuse},pdfauthor={Sze Chun Yiu}}").replace(
        "\\input{sections/01-introduction.tex}",
        "\\noindent\\textbf{Keywords:} agent memory; state reuse; responsibility; authorization; provenance; recovery.\n\\input{sections/01-introduction.tex}",
    ).replace(
        "\\input{sections/99-references.tex}",
        "\\input{sections/99-references.tex}\n\\section*{Statements and declarations}\nNo funding was received for this work. The author declares no competing interests. No human participants, personal data or animals were involved. Sze Chun Yiu is the sole author and is responsible for conception, methodology, implementation, analysis, source verification and the final submission decision. Generative AI tools were used for drafting and editing assistance. The author is responsible for all scientific content.",
    )
    main.write_text(text)
    return manuscript


def source_orion24(dst: Path) -> Path:
    md = ROOT / "papers/orion-24-orion-rse/WAVE3_SCOPED_MANUSCRIPT_V1.md"
    text = md.read_text()
    text = re.sub(r"^# .*?\n", "", text, count=1)
    abstract_match = re.search(r"\n## Abstract\n\n(.+?)\n\n## 1\. ", text, flags=re.S)
    if not abstract_match:
        raise RuntimeError("ORION-24 abstract could not be isolated")
    abstract = " ".join(abstract_match.group(1).split())
    text = text[:abstract_match.start()] + "\n## 1. " + text[abstract_match.end():]
    front = f"""---
title: "Fail-Closed Evaluation Contracts for Autonomous Research Software Engineering"
author:
  - "{AUTHOR}"
date: ""
abstract: |
  {abstract}
geometry: margin=1in
colorlinks: false
---

**Affiliation:** {AFFILIATION}

**Correspondence:** {EMAIL}

**Keywords:** autonomous agents; research software engineering; evaluation; reproducibility; evidence custody; fail-closed systems.

"""
    text += "\n\n## Statements and declarations\n\nNo funding was received for this work. The author declares no competing interests. No human participants, personal data or animals were involved. Sze Chun Yiu is the sole author and is responsible for conception, methodology, specification, analysis, source verification and the final submission decision. Generative AI tools were used for drafting and editing assistance. The author is responsible for all scientific content.\n"
    write(dst / "manuscript.md", front + text)
    run("pandoc", "manuscript.md", "--standalone", "--from=gfm", "--to=latex", "-o", "main.tex", cwd=dst)
    return dst


SOURCE_BUILDERS = {
    "orion13": source_orion13,
    "orion14": source_orion14,
    "orion19": source_orion19,
    "orion21": source_orion21,
    "orion23": source_orion23,
    "orion24": source_orion24,
}


def compile_source(kind: str, source_root: Path) -> Path:
    cwd = source_root if kind in {"orion19", "orion24"} else source_root / "manuscript"
    if kind == "orion24":
        run("latexmk", "-xelatex", "-interaction=nonstopmode", "-halt-on-error", "main.tex", cwd=cwd)
    else:
        args = ["latexmk", "-pdf", "-interaction=nonstopmode", "-halt-on-error"]
        if kind in {"orion21", "orion23"}:
            args.append("-shell-escape")
        args.append("main.tex")
        run(*args, cwd=cwd)
    return cwd / "main.pdf"


def clean_build_products(source_root: Path) -> None:
    suffixes = {".aux", ".bbl", ".blg", ".fdb_latexmk", ".fls", ".log", ".out", ".pdf", ".toc", ".xdv"}
    names = {"main.markdown.lua", "main.markdown.out"}
    for path in sorted(source_root.rglob("_markdown_main"), reverse=True):
        if path.is_dir():
            shutil.rmtree(path)
    for path in source_root.rglob("*"):
        if path.is_file() and (path.suffix in suffixes or path.name in names):
            path.unlink()


def result_retention(paper: str) -> str:
    rows = {
        "ORION-13": [
            "Flat canonicalization: 6/32 false merges (0.1875); coordinate-governed mapping: 0/32.",
            "False-split difference against the conservative exact-coordinate control: 0.",
            "All discordances occur in one polarity family; other registered ablations have zero effect.",
            "Information-equivalent typed product ties 400/400; no universal coordinate-necessity claim.",
            "Raw-text and downstream scientific-utility claims remain undetermined.",
        ],
        "ORION-14": [
            "H3 abstention contrast is NOT_SUPPORTED: both arms are correct on 30/30 eligible cases.",
            "The earlier 39-case live-model arm remains excluded because of label, denominator and leakage defects.",
            "Case-level uncertainty is descriptive; 12 attack-family clusters give 6 favorable discordances, 0 reverse, exact sign p=.031.",
        ],
        "ORION-19": [
            "Wine accessibility result is null.",
            "The registered Qwen2.5 monotone-scaling hypothesis is negative.",
            "The digit accessibility family is indeterminate on protected data.",
            "A semantics-preserving symbol remint withdraws an older serialization contrast.",
            "The redraw follow-up fails its half-sample stability gate.",
        ],
        "ORION-21": [
            "Sparse-decoder >=4x claim fails in one of two cells; residuals are 2x and 4x.",
            "The pooled attack prevails in the width-three regime.",
            "Digits support is 3/10 (linear), 5/10 (RBF), 5/10 (nearest neighbour), below the frozen 8/10 gate.",
            "Independent random unit for the width-seven replication is seed n=3; nine cells are not nine replicates.",
        ],
        "ORION-23": [
            "The earlier self-scored zero has zero reachable harm opportunities and carries no empirical safety authority.",
            "Historical predecessor gate 0.0556640625 > 0.05 remains failed.",
            "Confidence-only and provenance-only comparators retain their unsafe-reuse failures.",
            "The 12,288-episode composed result is a complete authored finite world, not population inference or external validation.",
        ],
        "ORION-24": [
            "Zero of eight counts missing required artifact classes, not attempted external cases.",
            "Execution was unauthorized; external scientific n=0 and all efficacy endpoints are undetermined.",
            "The architecture is specified, not implemented end to end; historical 'executable handoff' wording is not an executability assertion.",
            "P14A unattainability, P14B circularity/protocol mismatch and P14C bounded conformance remain historical evidence, not Wave-3 efficacy.",
        ],
    }
    return "# Result-retention ledger\n\n" + "\n".join(f"- {x}" for x in rows[paper]) + "\n"


def venue_requirements(spec: dict) -> str:
    return f"""# Venue decision and requirements

- Venue: **{spec['venue']}**
- Article type: **{spec['article_type']}**
- Official requirements: {spec['requirements']}
- Accessed: {DATE}
- Identity mode: `{spec['identity']}`

The package separates repository-controlled completion from portal-controlled
author confirmations. The selected venue and article type govern identity
checks; no universal anonymity rule is applied.
"""


def information_sheet(paper: str) -> str | None:
    if paper == "ORION-23":
        return """# JAAMAS regular-paper information sheet

## 1. Main claim and importance

State sufficiency is responsibility-relative. An authenticated support/reopen
contract can prevent unsafe compact-state reuse when downstream responsibility
or certificate validity changes. This matters for agents that reuse summaries,
memories and cached tool state across tasks: recency, confidence and provenance
do not by themselves show that the retained distinctions answer a new task.

## 2. Precise evidence

An earlier self-scored zero is withheld because its harm endpoint had no live
opportunities. A fresh 30-case certificate-independent panel gives 30 live
opportunities in each of four corruption worlds; authentication rejects every
mutation, makes no unsafe reuse and costs 0.6111 times always raw on valid
certificates. In a 12,288-episode composed finite world with 2,457 scheduled
corruptions, authentication rejects all corruptions, makes no unsafe reuse,
attains correctness 0.97933 and costs 0.539 times always raw. The unverified arm
makes 330 unsafe reuses and 123 unnecessary reopens. These are complete authored
finite worlds, not population samples or external validation.

## 3. Closest papers and relation

Proof-Carrying Agent Actions (Wang, arXiv:2606.04104) owns portable action
certificates; STALE (Chao et al., arXiv:2605.06527) owns stale-memory detection;
Commit-Time Authorization (Santos-Grueiro, arXiv:2607.10487), Cordon (Chen et
al., arXiv:2606.17573) and AID-Guard (Tong et al., arXiv:2608.21159) own
freshness, transactional recovery and authorization-to-effect lifecycle
binding. The residual here is responsibility-indexed state support with a
material-reopen rule and the bounded composed safety contrast.

## 4. Prior publication

The author must confirm at filing whether any part appeared in an archival
venue. The repository record describes this as an original journal manuscript;
no prior archival publication is asserted by this package.
"""
    if paper == "ORION-24":
        return """# JAAMAS Viewpoint information sheet

## 1. Novelty and significance

The viewpoint specifies a fail-closed evidence chain for evaluating autonomous
research-software agents: task custody, matched arm contracts, neutralized
packets, mechanical or blinded adjudication, failure-inclusive denominators and
independent endpoint reconstruction. Its significance is the separation between
readiness to measure and authority to claim an outcome.

## 2. Timeliness

Research-engineering and scientific-reproduction benchmarks now evaluate
frontier agents, while reporting standards show that omitted failures and
mutable scoring rules can materially alter conclusions. A custody-aware
evaluation contract is therefore timely.

## 3. Basis and rigor

The proposal is organized as explicit role, artifact, denominator and hostile-
control obligations. Its own preflight fails closed: zero of eight required
external-input artifact classes is present, execution is unauthorized, and no
efficacy endpoint is estimated. This is a specified architecture, not a claim
of an implemented harness.

## 4. Closest work

RE-Bench (Wijk et al., arXiv:2411.15114), CORE-Bench (Siegel et al.,
arXiv:2409.11363) and PaperBench (Starace et al., arXiv:2504.01848) own realistic
research-engineering and reproduction benchmarks. Rollout Cards (Masters et
al., arXiv:2605.12131) owns retained rollout records, failure counts and
reporting-rule disclosure. The viewpoint claims no novelty for these components.

## 5. Difference from prior viewpoints or surveys

This is not a benchmark survey. It is a concrete fail-closed specification that
composes custody and authority obligations and demonstrates its boundary by
refusing execution when prerequisite artifact classes are absent.

## 6. Prior publication

The author must confirm at filing whether any part appeared in an archival
venue. The repository record describes this as an original viewpoint; no prior
archival publication is asserted by this package.
"""
    return None


def review_materials(paper: str, spec: dict, dst: Path) -> None:
    src = ROOT / "papers" / spec["slug"]
    staging = dst / "review_materials"
    staging.mkdir()
    for rel in [spec["authority"], "PUBLICATION_FREEZE_ADDENDUM_V1.md"]:
        path = src / rel
        if path.exists():
            shutil.copy2(path, staging / path.name)
    if paper == "ORION-24":
        for rel in ["P14D_EXTERNAL_ACQUISITION_PREFLIGHT_V1.json", "WAVE3_PUBLICATION_DISPOSITION_V1.json"]:
            shutil.copy2(src / rel, staging / rel)
    if paper == "ORION-21":
        for rel in ["P11I_WIDE_HIGH_WIDTH_REPLICATION_RESULT_V1.json", "P11I_REVALIDATION_RECEIPT_V1_1.json"]:
            shutil.copy2(src / rel, staging / rel)
    if paper == "ORION-23":
        for rel in ["P13C_COMPOSED_RESULT_V1.json", "P13_P14_CONSOLIDATION_SCOPE_BINDING_V1.json"]:
            if (src / rel).exists():
                shutil.copy2(src / rel, staging / rel)
    deterministic_zip(staging, dst / "review_materials.zip")
    shutil.rmtree(staging)


def build_one(paper: str, spec: dict) -> dict:
    paper_root = ROOT / "papers" / spec["slug"]
    final = paper_root / "submission" / "final-20260831"
    if final.exists():
        shutil.rmtree(final)
    final.mkdir(parents=True)
    with tempfile.TemporaryDirectory(prefix=f"{paper.lower()}-") as temp:
        source = Path(temp) / "source"
        source.mkdir()
        build_root = SOURCE_BUILDERS[spec["source_kind"]](source)
        pdf = compile_source(spec["source_kind"], source)
        shutil.copy2(pdf, final / "manuscript.pdf")
        clean_build_products(source)
        deterministic_zip(source, final / "source.zip")
    review_materials(paper, spec, final)
    write(final / "VENUE_REQUIREMENTS.md", venue_requirements(spec))
    write(final / "RESULT_RETENTION.md", result_retention(paper))
    write(final / "DATA_AND_CODE_AVAILABILITY.md", "# Data and code availability\n\nThe source and review-material archives in this package bind the reader-facing manuscript and the evidence needed to inspect its submitted claims. A persistent public identifier remains a portal-time author input unless already supplied; no DOI or archive receipt is synthesized here.\n")
    write(final / "HUMAN_INPUTS_REQUIRED.md", "# Human filing inputs\n\n" + "\n".join(f"- [ ] {x}" for x in spec["human"]) + "\n")
    write(final / "AI_USE_DISCLOSURE.md", "# AI-use disclosure\n\nGenerative AI tools were used for drafting and editing assistance. The author is responsible for all scientific content.\n")
    sheet = information_sheet(paper)
    if sheet:
        write(final / "INFORMATION_SHEET.md", sheet)
    pages = int(re.search(r"Pages:\s+(\d+)", run("pdfinfo", str(final / "manuscript.pdf"))).group(1))
    payload_names = sorted(p.name for p in final.iterdir() if p.is_file() and p.name not in {"PACKAGE_MANIFEST.json", "SHA256SUMS"})
    payload = {name: {"sha256": sha(final / name), "bytes": (final / name).stat().st_size} for name in payload_names}
    manifest = {
        "schema": "ORION.PublicationClosure.v1",
        "paper": paper,
        "date": DATE,
        "title": spec["title"],
        "venue": spec["venue"],
        "article_type": spec["article_type"],
        "requirements_url": spec["requirements"],
        "requirements_accessed": DATE,
        "identity_policy": spec["identity"],
        "active_authority": str((paper_root / spec["authority"]).relative_to(ROOT)),
        "active_authority_sha256": sha(paper_root / spec["authority"]),
        "terminal": spec["terminal"],
        "package_status": "INTERNAL_PACKAGE_VALIDATED__HUMAN_PORTAL_INPUTS_PENDING",
        "blocker_classification": {
            "current_claim_blocker": False,
            "package_blocker": False,
            "human_filing_only": True,
            "successor_science_only": True,
        },
        "scientific_authority_delta": "NONE",
        "skills_applied": [
            "nature-writing",
            "nature-polishing",
            "nature-reviewer",
            "nature-statistics",
            "nature-ref-verifier",
            "nature-publication-closure",
        ],
        "publication_closure_skill": {
            "path": "papers/skills/nature/nature-publication-closure/SKILL.md",
            "sha256": sha(ROOT / "papers/skills/nature/nature-publication-closure/SKILL.md"),
        },
        "verifier": {
            "path": "scripts/check_publication_closure.py",
            "sha256": sha(ROOT / "scripts/check_publication_closure.py"),
        },
        "pdf_pages": pages,
        "build_environment": {
            "python": platform.python_version(),
            "latexmk": run("latexmk", "-v").splitlines()[0],
            "pdftex": run("pdflatex", "--version").splitlines()[0],
            "xetex": run("xelatex", "--version").splitlines()[0],
            "uv_lock_sha256": sha(ROOT / "uv.lock"),
        },
        "payload": payload,
        "inferential_units": {
            "ORION-13": "32 fixed mapping cases; six discordances in one family; fixed-panel diagnostics",
            "ORION-14": "12 attack-family clusters; case-level interval descriptive",
            "ORION-19": "five fixed heterogeneous task families; descriptive counts",
            "ORION-21": "three independent execution seeds; geometry within seed; query repeats technical",
            "ORION-23": "complete authored finite panels/worlds; no population inference",
            "ORION-24": "zero external cases; eight missing prerequisite artifact classes",
        }[paper],
    }
    write(final / "PACKAGE_MANIFEST.json", json.dumps(manifest, indent=2, sort_keys=True) + "\n")
    sum_paths = sorted(p for p in final.iterdir() if p.is_file() and p.name != "SHA256SUMS")
    write(final / "SHA256SUMS", "".join(f"{sha(p)}  {p.name}\n" for p in sum_paths))
    notice = f"""# Current publication source — {paper}

Current filing directory: `submission/final-20260831/`.

The package is the sole reader-facing filing object for the bounded claim named
in its manifest. Earlier manuscripts, PDFs, readiness notes, journal-package
directories and content manifests are historical development/custody surfaces
and are superseded for filing by `submission/final-20260831/PACKAGE_MANIFEST.json`.
They remain preserved because they contain adverse, null and provenance history.
This notice changes no scientific authority.
"""
    write(paper_root / "PUBLICATION_SUPERSESSION_NOTICE_2026-08-31.md", notice)
    return manifest


def main() -> int:
    manifests = [build_one(paper, spec) for paper, spec in SPECS.items()]
    out = ROOT / "papers/publication_closure/orion_13_24_final/CLOSURE_REGISTRY.json"
    write(out, json.dumps({
        "schema": "ORION.PublicationClosureRegistry.v1",
        "date": DATE,
        "requested_papers": list(SPECS),
        "phase": "PACKAGE_READY",
        "mirror_phase": "PENDING_POST_MERGE",
        "papers": [{
            "paper": m["paper"],
            "package_manifest": f"papers/{SPECS[m['paper']]['slug']}/submission/final-20260831/PACKAGE_MANIFEST.json",
            "terminal": m["terminal"],
        } for m in manifests],
    }, indent=2, sort_keys=True) + "\n")
    write(out.parent / "REVIEWER_AUDIT_AND_RELEASE_DECISION.md", """# ORION-13/14/19/21/23/24 reviewer audit and release decision

## Decision

All six bounded manuscripts have one current filing package and no current-claim
or repository-controlled package blocker. Their package status is
`INTERNAL_PACKAGE_VALIDATED__HUMAN_PORTAL_INPUTS_PENDING`. This status does not
claim that an author account, editor routing, archive PID or submission ID
exists. It also does not authorize successor science.

## Adversarial findings retained

- ORION-13: all six mapping discordances lie in one polarity family; uncertainty
  is a fixed-panel diagnostic. The information-equivalent typed product ties the
  registered rule at 400/400.
- ORION-14: H3 is not supported (30/30 in both arms). The legacy 39-case arm is
  excluded; its verdict-leak checker fails on three insufficient-evidence cases.
  Twelve-family analysis retains 6 favorable discordances, 0 reverse, exact
  two-sided sign-test p=0.03125 and family-bootstrap interval [-0.75,-0.25].
- ORION-19: Wine is null, Qwen2.5 scaling is negative, digit accessibility is
  indeterminate, symbol reminting withdraws the old serialization contrast and
  the redraw follow-up fails its stability gate.
- ORION-21: the independent replication unit is seed (n=3), not nine cells; the
  digits family fails the frozen 8/10 gate under every registered decoder.
- ORION-23: the self-scored predecessor has no harm opportunities; the positive
  result is a complete authored finite world, not population or external
  evidence.
- ORION-24: zero of eight means missing prerequisite artifact classes. No
  external case ran, execution was unauthorized and efficacy is `CANNOT_CHECK`.

## Reproduction

```bash
python papers/publication_closure/orion_13_24_final/build_final_packages.py
python scripts/check_publication_closure.py --rebuild ORION-13 ORION-14 ORION-19 ORION-21 ORION-23 ORION-24
```

The verifier checks registry coverage, active-authority hashes, complete payload
and checksum inventories, deterministic/safe archives, venue-routed identity,
negative-result wording, PDF readability and clean-source render equivalence.
The generated package manifest binds the verifier and the publication-closure
skill by content hash.
""")
    print("BUILT " + ", ".join(SPECS))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

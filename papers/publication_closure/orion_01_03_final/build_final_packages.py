#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import zipfile
from dataclasses import dataclass
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
PAPERS = ROOT / "papers"
SOURCE_DATE_EPOCH = "1788134400"  # 2026-08-31T00:00:00Z
SKILLS_REVISION = "a45568215d648e5d446a03980277d282b19e57d7"
TMLR_STYLE_REVISION = "7bf90efe3a0debbba703c05c43f3ff7e4d4a2992"

@dataclass(frozen=True)
class Spec:
    key: str
    canonical: Path
    ledger: Path
    out: Path
    title: str
    stem: str
    venue: str
    mode: str
    ancillary: Path
    keywords: str

SPECS = [
    Spec(
        "ORION-01A",
        PAPERS / "orion-01-certificate-realization/theory-A-MANUSCRIPT_V3.md",
        PAPERS / "orion-01-certificate-realization/theory-A-CLAIM_LEDGER_V3.md",
        PAPERS / "orion-01-certificate-realization/journal_package_A_final",
        "Restore-Sensitive Support Normal Forms for Multi-Tag Quantum Compilation",
        "Restore-Sensitive_Support_Normal_Forms_for_Multi-Tag_Quantum_Compilation",
        "Quantum",
        "quantum",
        PAPERS / "orion-01-certificate-realization/journal_package_A/submission/anc",
        "quantum compilation; Pauli strings; support normal forms; zero-sum deletion; sparse optimization",
    ),
    Spec(
        "ORION-01B",
        PAPERS / "orion-01-certificate-realization/theory-B-MANUSCRIPT_V3.md",
        PAPERS / "orion-01-certificate-realization/theory-B-CLAIM_LEDGER_V3.md",
        PAPERS / "orion-01-certificate-realization/journal_package_B_final",
        "Certifiable Support Budgets versus Intrinsic Support in Quantum Compilation",
        "Certifiable_Support_Budgets_versus_Intrinsic_Support_in_Quantum_Compilation",
        "Quantum",
        "quantum",
        PAPERS / "orion-01-certificate-realization/journal_package_B/submission/anc",
        "quantum compilation; certifiable support; intrinsic support; proof systems; Pauli strings",
    ),
    Spec(
        "ORION-02",
        PAPERS / "orion-02-fiberguard-finite-fibre/MANUSCRIPT_V3.md",
        PAPERS / "orion-02-fiberguard-finite-fibre/CLAIM_LEDGER_V3.md",
        PAPERS / "orion-02-fiberguard-finite-fibre/journal_package_final",
        "When a Representation Can Certify: Sharp Fibre-Diameter Limits and Minimal Refinement",
        "When_a_Representation_Can_Certify",
        "Transactions on Machine Learning Research (TMLR)",
        "tmlr",
        PAPERS / "orion-02-fiberguard-finite-fibre/submission/anc",
        "representation sufficiency; certification; fibre diameter; refinement; selective uncertainty",
    ),
    Spec(
        "ORION-03",
        PAPERS / "orion-03-typed-merge-falsification/MANUSCRIPT_V3.md",
        PAPERS / "orion-03-typed-merge-falsification/CLAIM_LEDGER_V3.md",
        PAPERS / "orion-03-typed-merge-falsification/journal_package_final",
        "Typed Scientific Authority with Fail-Closed Nonpromotion",
        "Typed_Scientific_Authority_with_Fail-Closed_Nonpromotion",
        "Journal of Automated Reasoning",
        "springer",
        PAPERS / "orion-03-typed-merge-falsification/submission/artifact",
        "scientific authority; falsification; provenance; least fixed points; evidence licenses",
    ),
]

A_REFERENCES = r"""
## Tool-use disclosure

A generative language model assisted manuscript organization, language revision,
adversarial review, and submission-package preparation. The listed author remains
responsible for the mathematical statements, proofs, references, executable claims,
and final text.

## Data and code availability

The source package accompanying this manuscript contains finite-group and
Restore-sensitivity control records used for implementation checks. These files are
provenance aids rather than theorem authority; the displayed proofs and the cited
parent theorem/witness carry the all-size claims.

## References

1. N. Schillo, A. Sturm, and R. Quay, “TARE: Block Encoding Linear Combinations
   of Pauli Strings Without Ancilla State Preparation,” arXiv:2601.05740v4
   [quant-ph] (2026).
2. I. Aliev, J. A. De Loera, F. Eisenbrand, T. Oertel, and R. Weismantel,
   “The Support of Integer Optimal Solutions,” *SIAM Journal on Optimization*
   **28**, 2152–2157 (2018). DOI: 10.1137/17M1162792.
3. M. Freeze and W. A. Schmid, “Remarks on a generalization of the Davenport
   constant,” *Discrete Mathematics* **310**, 3373–3389 (2010).
   DOI: 10.1016/j.disc.2010.07.028.
4. G. Wang, “The universal zero-sum invariant and weighted zero-sum for infinite
   abelian groups,” *Communications in Algebra* **53**(4), 1581–1599 (2025).
   DOI: 10.1080/00927872.2024.2418017.
5. J. Dehaene and B. De Moor, “Clifford group, stabilizer states, and linear and
   quadratic operations over GF(2),” *Physical Review A* **68**, 042318 (2003).
   DOI: 10.1103/PhysRevA.68.042318.
6. S. Aaronson and D. Gottesman, “Improved simulation of stabilizer circuits,”
   *Physical Review A* **70**, 052328 (2004).
   DOI: 10.1103/PhysRevA.70.052328.
""".strip()

B_REFERENCES = r"""
## Tool-use disclosure

A generative language model assisted manuscript organization, language revision,
adversarial review, and submission-package preparation. The listed author remains
responsible for the mathematical statements, proofs, references, executable claims,
and final text.

## Data and code availability

The source package contains finite control records and the standalone verifier used
for the dependent local lemmas and product bookkeeping. The all-size support claims
remain proof- and witness-authorized; packaged computations do not enlarge them.

## References

1. I. Aliev, J. A. De Loera, F. Eisenbrand, T. Oertel, and R. Weismantel,
   “The Support of Integer Optimal Solutions,” *SIAM Journal on Optimization*
   **28**, 2152–2157 (2018). DOI: 10.1137/17M1162792.
2. M. Freeze and W. A. Schmid, “Remarks on a generalization of the Davenport
   constant,” *Discrete Mathematics* **310**, 3373–3389 (2010).
   DOI: 10.1016/j.disc.2010.07.028.
3. G. Wang, “The universal zero-sum invariant and weighted zero-sum for infinite
   abelian groups,” *Communications in Algebra* **53**(4), 1581–1599 (2025).
   DOI: 10.1080/00927872.2024.2418017.
4. S. A. Cook and R. A. Reckhow, “The relative efficiency of propositional proof
   systems,” *Journal of Symbolic Logic* **44**(1), 36–50 (1979).
   DOI: 10.2307/2273702.
5. N. Schillo, A. Sturm, and R. Quay, “TARE: Block Encoding Linear Combinations
   of Pauli Strings Without Ancilla State Preparation,” arXiv:2601.05740v4
   [quant-ph] (2026).
6. G. Li, A. Wu, Y. Shi, A. Javadi-Abhari, Y. Ding, and Y. Xie,
   “Paulihedral: A Generalized Block-Wise Compiler Optimization Framework for
   Quantum Simulation Kernels,” in *ASPLOS 2022*, 554–569 (2022).
   DOI: 10.1145/3503222.3507715.
""".strip()

D_REFERENCES = r"""
## Tool-use disclosure

A generative language model assisted manuscript organization, language revision,
adversarial review, and submission-package preparation. The listed author remains
responsible for the mathematical statements, proofs, references, executable claims,
and final text.

## Data and code availability

The source archive includes the JSON schema, deterministic Python evaluator, unit
tests, and bounded case fixtures required to reproduce the executable claims. The
external X.509 measurements remain bound to the committed corpus records; analytic
policy identities are not re-labelled as empirical detector performance.

## References

1. J. Doyle, “A Truth Maintenance System,” *Artificial Intelligence* **12**,
   231–272 (1979). DOI: 10.1016/0004-3702(79)90008-0.
2. J. P. Martins and S. C. Shapiro, “A Model for Belief Revision,”
   *Artificial Intelligence* **35**, 25–79 (1988).
   DOI: 10.1016/0004-3702(88)90031-8.
3. C. Bourgaux, P. Bourhis, L. Peterfreund, and M. Thomazo, “Revisiting
   Semiring Provenance for Datalog,” in *KR 2022* (2022).
   DOI: 10.24963/kr.2022/10.
4. M. Abo Khamis, H. Q. Ngo, R. Pichler, D. Suciu, and Y. R. Wang,
   “Convergence of Datalog over (Pre-)Semirings,” in *PODS 2022*, 105–117
   (2022). DOI: 10.1145/3517804.3524140.
5. T. J. Green, G. Karvounarakis, and V. Tannen, “Provenance Semirings,” in
   *PODS 2007*, 31–40 (2007). DOI: 10.1145/1265530.1265535.
6. P. A. Bonatti, A. Hogan, A. Polleres, and L. Sauro, “Robust and Scalable
   Linked Data Reasoning Incorporating Provenance and Trust Annotations,”
   *Journal of Web Semantics* **9**(2), 165–201 (2011).
   DOI: 10.1016/j.websem.2011.06.003.
""".strip()

TOOL_DISCLOSURE = r"""
## Tool-use disclosure

A generative language model assisted manuscript organization, language revision,
adversarial review, and submission-package preparation. Scientific claims and final
submission decisions remain the responsibility of the listed author.
""".strip()


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256(path: Path) -> str:
    return sha256_bytes(path.read_bytes())


def run(cmd: list[str], *, cwd: Path | None = None, input_text: str | None = None) -> str:
    env = os.environ.copy()
    env["SOURCE_DATE_EPOCH"] = SOURCE_DATE_EPOCH
    env["TZ"] = "UTC"
    proc = subprocess.run(
        cmd,
        cwd=cwd or ROOT,
        input=input_text,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        env=env,
        check=False,
    )
    if proc.returncode:
        raise SystemExit(f"command failed ({proc.returncode}): {' '.join(cmd)}\n{proc.stdout}\n{proc.stderr}")
    return proc.stdout


def strip_control_front_matter(text: str) -> str:
    lines = text.splitlines()
    if lines and lines[0].strip() == "---":
        try:
            close = lines.index("---", 1)
        except ValueError as exc:
            raise SystemExit("unterminated YAML front matter") from exc
        front = lines[1:close]
        title_line = next((line for line in front if line.startswith("title:")), "")
        title = title_line.split(":", 1)[1].strip().strip('"')
        abstract_start = next((i for i, line in enumerate(front) if line.startswith("abstract:")), None)
        if not title or abstract_start is None:
            raise SystemExit("YAML front matter is missing title or abstract")
        abstract_lines: list[str] = []
        for line in front[abstract_start + 1:]:
            if line.startswith("  "):
                abstract_lines.append(line[2:])
            else:
                break
        body = lines[close + 1:]
        # Reserve level one for the article title and level two for the
        # reconstructed abstract and top-level manuscript sections.
        body = ["#" + line if line.startswith("#") else line for line in body]
        return (
            f"# {title}\n\n## Abstract\n\n"
            + "\n".join(abstract_lines).strip()
            + "\n\n"
            + "\n".join(body).strip()
            + "\n"
        )
    if not lines or not lines[0].startswith("# "):
        raise SystemExit("missing H1 title")
    out = [lines[0], ""]
    i = 1
    while i < len(lines):
        line = lines[i]
        if line.startswith("## "):
            break
        if line.strip() and not line.startswith("**"):
            break
        i += 1
    out.extend(lines[i:])
    return "\n".join(out).strip() + "\n"


def insert_keywords(text: str, keywords: str) -> str:
    if "**Keywords:**" in text:
        return text
    start = text.index("## Abstract")
    nxt = text.index("\n## ", start + len("## Abstract"))
    return text[:nxt].rstrip() + f"\n\n**Keywords:** {keywords}\n" + text[nxt:]


def clean_orion02(text: str) -> str:
    text = text.split("\n## Publication decision record", 1)[0].rstrip() + "\n"
    text = text.replace(
        "Exhaustive independent checks found no violations",
        "Exhaustive independent-code-path checks within this repository found no violations",
    )
    text = text.replace("## 6. Independent verification", "## 6. Finite hostile verification")
    text = text.replace(
        "Separate exhaustive checkers were used as hostile finite-model verification rather than as theorem authority.",
        "Separate exhaustive in-repository checkers were used as hostile finite-model verification rather than as theorem authority or external replication.",
    )
    text = text.replace("The registered claims R1-R5 had zero violations.", "The specified checker claims had zero violations.")
    text = re.sub(
        r" \(`rounds/r23-density-backoff-revival/R23_CONTROL_PAIRED_TEST_V1\.json`, recomputed from the per-dataset records by `verify_r23_control_paired_test\.py`\)",
        "",
        text,
    )
    text = re.sub(r"The R23 terminal is `C_R23_PMLB_BACKOFF_COVERAGE_IMPROVED_BELOW_GATE`\.\s*", "The first study therefore remained below its pre-specified coverage gate.\n\n", text)
    text = re.sub(r"The R24 terminal remains `C_R24_ARM_CONDITIONAL_CERTIFICATE_INVALID`\.\s*", "The second study therefore failed its pre-specified validity criterion.\n\n", text)
    text = text.replace("R23's", "the first study's").replace("R24's", "the second study's")
    text = re.sub(r"\bR23\b", "the first study", text)
    text = re.sub(r"\bR24\b", "the second study", text)
    text = text.replace("Across both counted attempts the same negative control outperformed the registered geometry.", "Across both counted attempts the same negative control was at least as strong on the recorded criteria as the specified geometry.")
    text = text.replace("registered maximum", "pre-specified maximum")
    text = text.replace("registered target", "pre-specified target")
    text = text.replace("registered `0.95` gate", "pre-specified `0.95` gate")
    text = text.replace("registered Hamming geometry", "specified Hamming geometry")
    text = text.replace("registered geometry", "specified geometry")
    text = text.replace("registered finite configuration families", "specified finite configuration families")
    text = text.replace("registered checker", "specified checker")
    text = text.replace("registered `alpha=.10`", "pre-specified `alpha=.10`")
    text = text.replace(
        "The serialized paired flags give $(\\text{both},\\text{geometry only},\\text{control only},\\text{neither})=(14,6,0,24)$",
        "The serialized paired counts (both, geometry only, control only, neither) are $(14,6,0,24)$",
    )
    text = text.replace("Current conditional-coverage work continues", "Recent conditional-coverage work continues")
    text = text.replace(
        "- Y. Jin and Z. Ren, *Confidence on the Focal: Conformal Prediction with Selection-Conditional Coverage*, arXiv:2403.03868 (2024).",
        "- Y. Jin and Z. Ren, *Confidence on the focal: conformal prediction with selection-conditional coverage*, Journal of the Royal Statistical Society: Series B 87, 1239–1259 (2025). DOI: 10.1093/jrsssb/qkaf016.",
    )
    return text


def clean_orion03(text: str) -> str:
    text = text.replace("under `packages/typed-merge-evaluator/`", "in the accompanying artifact")
    text = text.replace("`PARITY_PARTITION` family", "parity-partition benchmark family")
    text = text.replace("the `M4_OURS_B` policy", "the bounded typed-witness policy")
    text = text.replace("The registered typed witness policy", "The specified typed-witness policy")
    text = text.replace("The registered least fixed point", "The specified least fixed point")
    text = text.replace("registered seeds", "specified seeds")
    text = text.replace("registered rule", "specified rule")
    text = text.replace("registered capped rule", "specified capped rule")
    text = text.replace("registered refutations", "specified refutations")
    text = text.replace("registered authority algebra", "specified authority algebra")
    text = text.replace("registered scientific cases", "specified scientific cases")
    text = text.replace("registered X.509", "specified X.509")
    return text


def publication_markdown(spec: Spec) -> str:
    text = strip_control_front_matter(spec.canonical.read_text(encoding="utf-8"))
    if spec.key == "ORION-02":
        text = clean_orion02(text)
    elif spec.key == "ORION-03":
        text = clean_orion03(text)
    else:
        text = text.replace("A1 parent evidence", "parent evidence")
        text = text.replace("B1 package", "parent evidence package")
        text = text.replace("A1 parent package", "parent evidence package")
    text = insert_keywords(text, spec.keywords)
    if spec.key == "ORION-01A":
        text = text.rstrip() + "\n\n" + A_REFERENCES + "\n"
    elif spec.key == "ORION-01B":
        text = text.rstrip() + "\n\n" + B_REFERENCES + "\n"
    elif spec.key == "ORION-02":
        text = text.replace("\n## Selected references", "\n" + TOOL_DISCLOSURE + "\n\n## Selected references", 1)
    elif spec.key == "ORION-03":
        text = text.rstrip() + "\n\n" + D_REFERENCES + "\n"
    return text


def mathify_code(text: str) -> str:
    # Only reader-facing mathematical code spans are converted. Identifiers,
    # filenames and evidence terminals remain verbatim code.
    math_tokens = (
        "<=", ">=", "!=", "=", "zsf", "kappa", "beta_", "Theta(",
        "support(", "rank(", "D_phi", "D(z)", "F_z", "V(", "c(", "r(",
        "phi", "eps", "Auth_", "Ret_", "F_R(", "sigma(", "tau_",
    )

    def conv(expr: str) -> str:
        if any(x in expr for x in (".md", "/", "C_R", "http", "PROSPECTIVE", "THEOREM", "POST_OUTCOME", "FINITE_EXACT", "BOUNDED_COMPUTATION", "EXTERNAL_REPLAY", "FORECAST_ONLY", "CONSTRUCTIVE_BOUND")):
            return f"`{expr}`"
        if not any(tok in expr for tok in math_tokens):
            return f"`{expr}`"
        s = expr
        s = s.replace(">=", r"\ge ").replace("<=", r"\le ").replace("!=", r"\ne ")
        s = re.sub(r"\bsubseteq\b", r"\\subseteq", s)
        s = re.sub(r"\bintersect\b", r"\\cap", s)
        s = re.sub(r"\bunion\b", r"\\cup", s)
        s = re.sub(r"\bempty\b", r"\\varnothing", s)
        s = re.sub(r"\bTheta\b", r"\\Theta", s)
        s = re.sub(r"\bzsf\b", r"\\operatorname{zsf}", s)
        s = re.sub(r"\brank\b", r"\\operatorname{rank}", s)
        s = re.sub(r"\bsupport\b", r"\\operatorname{support}", s)
        return f"${s}$"

    # A paragraph consisting only of one code span becomes display math.
    lines = []
    for line in text.splitlines():
        m = re.fullmatch(r"`([^`]+)`", line.strip())
        if m and any(tok in m.group(1) for tok in math_tokens):
            inline = conv(m.group(1))
            if inline.startswith("$") and inline.endswith("$"):
                lines.append("$$" + inline[1:-1] + "$$")
                continue
        lines.append(re.sub(r"`([^`]+)`", lambda m: conv(m.group(1)), line))
    return "\n".join(lines) + "\n"


def split_abstract(md: str) -> tuple[str, str, str]:
    lines = md.splitlines()
    title = lines[0][2:].strip()
    try:
        a = lines.index("## Abstract")
    except ValueError as e:
        raise SystemExit("missing Abstract") from e
    b = next(i for i in range(a + 1, len(lines)) if lines[i].startswith("## "))
    abstract_lines = lines[a + 1 : b]
    keyword = ""
    kept = []
    for line in abstract_lines:
        if line.startswith("**Keywords:**"):
            keyword = line.split("**Keywords:**", 1)[1].strip()
        else:
            kept.append(line)
    body = "\n".join(lines[b:]).strip() + "\n"
    return title, "\n".join(kept).strip(), keyword + "", body


def pandoc_fragment(markdown: str, *, shift: bool = False) -> str:
    cmd = ["pandoc", "--from=markdown+tex_math_single_backslash", "--to=latex"]
    if shift:
        cmd += ["--shift-heading-level-by=-1"]
    return run(cmd, input_text=markdown)


def make_tex(spec: Spec, md: str, submission: Path) -> str:
    title, abstract_md, keywords, body_md = split_abstract(mathify_code(md))
    abstract_tex = pandoc_fragment(abstract_md)
    body_tex = pandoc_fragment(body_md, shift=True)
    common = r"""\usepackage{amsmath,amssymb}
\usepackage[T1]{fontenc}
\usepackage[utf8]{inputenc}
\usepackage{lmodern}
\usepackage{microtype}
\usepackage{booktabs}
\usepackage{longtable,array,calc}
\usepackage{xurl}
\usepackage[hidelinks]{hyperref}
\providecommand{\tightlist}{%
  \setlength{\itemsep}{0pt}\setlength{\parskip}{0pt}}
\DeclareUnicodeCharacter{220E}{\ensuremath{\square}}
\setlength{\emergencystretch}{3em}
"""
    if spec.mode == "tmlr":
        preamble = "\\documentclass[10pt]{article}\n\\usepackage{tmlr}\n" + common
        author = "Anonymous authors"
        extra = "\\def\\month{MM}\n\\def\\year{YYYY}\n\\def\\openreview{\\url{https://openreview.net/forum?id=XXXX}}\n"
    else:
        preamble = "\\documentclass[11pt]{article}\n\\usepackage[margin=1in]{geometry}\n" + common
        author = r"Sze Chun Yiu\\Independent Researcher\\\texttt{sze-chun.yiu@fysik.su.se}"
        extra = ""
    tex = (
        preamble
        + f"\\title{{{title}}}\n"
        + f"\\author{{{author}}}\n"
        + extra
        + "\\date{}\n\\begin{document}\n\\maketitle\n\n"
        + "\\begin{abstract}\n"
        + abstract_tex.strip()
        + "\n\\end{abstract}\n\n"
        + f"\\noindent\\textbf{{Keywords:}} {keywords}\n\n"
        + body_tex
        + "\n\\end{document}\n"
    )
    return tex


def deterministic_zip(output: Path, files: dict[str, Path]) -> None:
    output.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(output, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=9) as zf:
        for arcname in sorted(files):
            data = files[arcname].read_bytes()
            info = zipfile.ZipInfo(arcname, date_time=(1980, 1, 1, 0, 0, 0))
            info.compress_type = zipfile.ZIP_DEFLATED
            info.external_attr = 0o100644 << 16
            zf.writestr(info, data)


def collect_files(root: Path, prefix: str) -> dict[str, Path]:
    result: dict[str, Path] = {}
    for p in sorted(root.rglob("*")):
        if p.is_file() and "__pycache__" not in p.parts and p.suffix != ".pyc":
            result[f"{prefix}/{p.relative_to(root).as_posix()}"] = p
    return result


def make_readme(spec: Spec) -> str:
    if spec.mode == "quantum":
        filing = "Quantum uses single-blind review and takes an arXiv quant-ph reference as the manuscript submission. The repository therefore freezes an arXiv-ready source archive and review PDF; obtaining the external arXiv identifier and completing the journal form remain human filing actions. A cover letter is intentionally omitted because Quantum states that it is not required."
    elif spec.mode == "tmlr":
        filing = "The review PDF is anonymized and built with the pinned TMLR style. The supplementary archive is also anonymized. OpenReview profile metadata, conflict/funding fields, action-editor recommendations, and the final upload remain human filing actions and are not encoded as scientific authority."
    else:
        filing = "The package provides the review PDF, editable LaTeX source, artifact archive, and a conservative cover-letter draft. Author metadata and final portal fields remain human filing actions."
    return f"""# {spec.key} final journal package\n\nPrimary target: **{spec.venue}**.\n\nScientific source of authority remains `{spec.canonical.relative_to(ROOT)}` with claim ledger `{spec.ledger.relative_to(ROOT)}`. `MANUSCRIPT.md` is a claim-equivalent reader-facing publication surface: it removes project-control front matter, fixes already-recorded independence wording where applicable, verifies/updates citations, and preserves the bounded claims and negative results.\n\n{filing}\n\nThis package does **not** claim acceptance, external specialist validation, external replication, or any authority beyond the bound manuscript and ledger.\n"""


def make_checklist(spec: Spec) -> str:
    lines = [
        f"# {spec.key} repository-side filing checklist",
        "",
        "- [x] Canonical V3 science and live claim ledger bound by SHA-256.",
        "- [x] Reader-facing manuscript surface removes repository control metadata without changing claim authority.",
        "- [x] Negative/adverse results and forbidden promotions retained.",
        "- [x] PDF compiles cleanly; extracted text is non-empty; no undefined references; no overfull boxes.",
        "- [x] Editable source and reproducibility/artifact archive included.",
        "- [x] Package manifest and SHA256SUMS generated deterministically.",
    ]
    if spec.mode == "tmlr":
        lines += [
            "- [x] TMLR submission PDF and supplementary material are anonymized.",
            "- [x] Pinned TMLR style/template files included in source archive.",
        ]
    if spec.mode == "quantum":
        lines += [
            "- [x] arXiv-ready source archive prepared for quant-ph filing.",
            "- [x] Author/tool-use disclosure included in the manuscript surface.",
        ]
    lines += [
        "- [ ] Complete external portal/account metadata and upload (human action).",
    ]
    if spec.mode == "quantum":
        lines += ["- [ ] Obtain arXiv quant-ph identifier before Quantum journal submission (human/external action)."]
    return "\n".join(lines) + "\n"


def build_one(spec: Spec, tmlr_vendor: Path | None) -> None:
    if spec.out.exists():
        shutil.rmtree(spec.out)
    submission = spec.out / "submission"
    submission.mkdir(parents=True)

    md = publication_markdown(spec)
    (spec.out / "MANUSCRIPT.md").write_text(md, encoding="utf-8")
    shutil.copy2(spec.ledger, spec.out / "CLAIM_LEDGER.md")
    (spec.out / "README.md").write_text(make_readme(spec), encoding="utf-8")
    (submission / "README.md").write_text(make_readme(spec), encoding="utf-8")
    (submission / "submission_checklist.md").write_text(make_checklist(spec), encoding="utf-8")

    anc_name = "artifact" if spec.mode == "springer" else "anc"
    anc_dest = submission / anc_name
    shutil.copytree(spec.ancillary, anc_dest)
    if spec.mode != "springer":
        shutil.copy2(ROOT / "LICENSE", anc_dest / "LICENSE_CODE.txt")

    if spec.mode == "springer":
        cover = f"""# Cover-letter draft — {spec.venue}\n\nDear Editors,\n\nPlease consider the manuscript *{spec.title}* for the Journal of Automated Reasoning. The paper studies a finite positive conjunctive authority calculus in which evidence licenses propagate only through permitted rule caps and directly refuted claims fail closed. The journal-facing contribution is deliberately narrower than generic fixed-point or provenance theory: it is the scientific evidence-license/nonpromotion specialization, an executable evaluator, and a third-party X.509 obstruction/cost instantiation.\n\nThe manuscript explicitly treats generic least-fixed-point, Datalog, truth-maintenance, provenance, and retraction mathematics as prior work. It also distinguishes measured X.509 obstruction/cost quantities from analytic identities of the typed-witness policy and makes no security or broad human-science deployment claim.\n\nThe accompanying source and artifact archive reproduce the executable cases. No adverse result has been removed or promoted.\n\nSincerely,\nSze Chun Yiu\n"""
        (submission / "cover_letter.md").write_text(cover, encoding="utf-8")

    tex = make_tex(spec, md, submission)
    tex_path = submission / f"{spec.stem}.tex"
    tex_path.write_text(tex, encoding="utf-8")

    if spec.mode == "tmlr":
        assert tmlr_vendor is not None
        shutil.copy2(tmlr_vendor / "tmlr.sty", submission / "tmlr.sty")
        shutil.copy2(tmlr_vendor / "tmlr.bst", submission / "tmlr.bst")

    run(["latexmk", "-pdf", "-interaction=nonstopmode", "-halt-on-error", tex_path.name], cwd=submission)
    log = submission / f"{spec.stem}.log"
    log_text = log.read_text(encoding="utf-8", errors="replace")
    bad = re.findall(r"LaTeX Warning: (?:Citation .* undefined|Reference .* undefined)|There were undefined references|There were undefined citations|Overfull \\[hv]box", log_text, re.I)
    if bad:
        raise SystemExit(f"LaTeX surface failure for {spec.key}: {bad[:5]}")
    run(["latexmk", "-c", tex_path.name], cwd=submission)
    for suffix in ("aux", "fdb_latexmk", "fls", "log", "out", "synctex.gz"):
        p = submission / f"{spec.stem}.{suffix}"
        if p.exists():
            p.unlink()
    pdf = submission / f"{spec.stem}.pdf"
    run(["pdfinfo", str(pdf)])
    extracted = run(["pdftotext", str(pdf), "-"])
    if not extracted.strip():
        raise SystemExit(f"empty PDF text for {spec.key}")
    if b"%%EOF" not in pdf.read_bytes()[-2048:]:
        raise SystemExit(f"missing PDF EOF for {spec.key}")

    source_files: dict[str, Path] = {"main.tex": tex_path, "README.md": submission / "README.md", "submission_checklist.md": submission / "submission_checklist.md"}
    source_files.update(collect_files(anc_dest, "anc"))
    if spec.mode == "tmlr":
        source_files["tmlr.sty"] = submission / "tmlr.sty"
        source_files["tmlr.bst"] = submission / "tmlr.bst"
        deterministic_zip(submission / f"{spec.stem}_tmlr_source.zip", source_files)
        supp = collect_files(anc_dest, "anc")
        deterministic_zip(submission / f"{spec.stem}_supplementary_anonymous.zip", supp)
    elif spec.mode == "quantum":
        deterministic_zip(submission / f"{spec.stem}_journal_source.zip", source_files)
        arxiv_files = {"main.tex": tex_path}
        arxiv_files.update(collect_files(anc_dest, "anc"))
        deterministic_zip(submission / f"{spec.stem}_arxiv_source.zip", arxiv_files)
    else:
        source_files["cover_letter.md"] = submission / "cover_letter.md"
        deterministic_zip(submission / f"{spec.stem}_journal_source.zip", source_files)
        deterministic_zip(submission / f"{spec.stem}_artifact.zip", collect_files(anc_dest, "artifact"))

    manifest_files = [p for p in sorted(spec.out.rglob("*")) if p.is_file() and p.name not in {"PACKAGE_MANIFEST.json", "SHA256SUMS"}]
    manifest = {
        "schema": "ORION.PublicationClosure.FinalJournalPackage.v1",
        "paper": spec.key,
        "primary_target": spec.venue,
        "canonical_science_path": spec.canonical.relative_to(ROOT).as_posix(),
        "canonical_science_sha256": sha256(spec.canonical),
        "claim_ledger_path": spec.ledger.relative_to(ROOT).as_posix(),
        "claim_ledger_sha256": sha256(spec.ledger),
        "publication_surface_sha256": sha256(spec.out / "MANUSCRIPT.md"),
        "academic_paper_skills_revision": SKILLS_REVISION,
        "source_parent_commit": os.environ.get("GITHUB_SHA", "local"),
        "scientific_authority_delta": "NONE__EDITORIAL_AND_PACKAGE_CLOSURE_ONLY",
        "files": {p.relative_to(spec.out).as_posix(): sha256(p) for p in manifest_files},
    }
    (spec.out / "PACKAGE_MANIFEST.json").write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    checksum_paths = [p for p in sorted(spec.out.rglob("*")) if p.is_file() and p.name != "SHA256SUMS"]
    (spec.out / "SHA256SUMS").write_text("".join(f"{sha256(p)}  {p.relative_to(spec.out).as_posix()}\n" for p in checksum_paths), encoding="utf-8")


def main() -> int:
    os.environ["SOURCE_DATE_EPOCH"] = SOURCE_DATE_EPOCH
    tmlr_vendor = Path(tempfile.mkdtemp(prefix="tmlr-style-"))
    base = f"https://raw.githubusercontent.com/JmlrOrg/tmlr-style-file/{TMLR_STYLE_REVISION}"
    run(["curl", "-fsSL", f"{base}/tmlr.sty", "-o", str(tmlr_vendor / "tmlr.sty")])
    run(["curl", "-fsSL", f"{base}/tmlr.bst", "-o", str(tmlr_vendor / "tmlr.bst")])
    for spec in SPECS:
        build_one(spec, tmlr_vendor)
    print("built", ", ".join(spec.key for spec in SPECS))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

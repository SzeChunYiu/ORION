#!/usr/bin/env python3
from pathlib import Path
import hashlib, os, subprocess, tempfile, zipfile

HERE = Path(__file__).resolve().parent
PAPER = HERE.parent.parent
MANUSCRIPT = PAPER / "WAVE3_SCOPED_MANUSCRIPT_V3.md"
RELATED = HERE / "RELATED_WORK_AND_NOVELTY.md"
FIXED_TIME = (2026, 8, 31, 0, 0, 0)
FIXED_PDF_ID = "0123456789ABCDEF0123456789ABCDEF"
AUTHOR = "Sze Chun Yiu"
AFFILIATION = "Stockholm University"
EMAIL = "sze-chun.yiu@fysik.su.se"

def run(cmd, cwd=None):
    env = os.environ.copy()
    env.setdefault("SOURCE_DATE_EPOCH", "1788166728")
    env.setdefault("FORCE_SOURCE_DATE", "1")
    subprocess.run(cmd, cwd=cwd, env=env, check=True)

def deterministic_zip_bytes(path, files):
    with zipfile.ZipFile(path, "w", zipfile.ZIP_DEFLATED) as zf:
        for arcname, payload in files:
            info = zipfile.ZipInfo(arcname, FIXED_TIME)
            info.external_attr = 0o644 << 16
            zf.writestr(info, payload)

def normalized_markdown(src):
    # The frozen manuscript contains research-internal front-matter, LaTeX
    # \(...\)/\[...\] delimiters, and a Unicode QED marker. The journal PDF
    # adapter removes only non-scientific routing labels and normalizes render
    # syntax in a temporary publication copy; canonical scientific bytes stay
    # untouched in the repository.
    text = Path(src).read_text(encoding="utf-8")
    drop_prefixes = (
        "**ORION-04 — exact-theorem successor V3**",
        "**Supersedes for journal science:**",
        "**Preserves:**",
    )
    # Drop the complete internal routing block.  The final line wraps in the
    # Markdown source, so prefix-only filtering used to leave an orphaned
    # sentence above the Abstract in the reader PDF.
    lines = text.splitlines()
    kept = []
    in_routing_block = False
    for line in lines:
        if line.startswith(drop_prefixes):
            in_routing_block = True
            continue
        if in_routing_block:
            if not line.strip():
                in_routing_block = False
            continue
        kept.append(line)
    text = "\n".join(kept) + "\n"
    text = text.replace("\\[", "$$").replace("\\]", "$$").replace("\\(", "$").replace("\\)", "$")
    text = text.replace("∎", "$\\square$")
    lines = text.splitlines()
    if not lines or not lines[0].startswith("# "):
        raise RuntimeError("publication manuscript must begin with a level-one title")
    title = lines[0][2:].strip().replace('"', '\\"')
    body = "\n".join(lines[1:]).lstrip()
    return (
        "---\n"
        f'title: "{title}"\n'
        f'author: "{AUTHOR}"\n'
        'date: ""\n'
        "---\n\n"
        f"**Affiliation:** {AFFILIATION}\n\n"
        f"**Correspondence:** {EMAIL}\n\n"
        + body
        + "\n"
    )

def deterministic_pdf_header():
    # pdfTeX otherwise emits a run-dependent trailer ID when Pandoc stages its
    # temporary TeX source. Pin the metadata/trailer fields so identical
    # publication input produces byte-identical PDF output across clean runs.
    return (
        "\\pdfinfoomitdate=1\n"
        f"\\pdftrailerid{{<{FIXED_PDF_ID}><{FIXED_PDF_ID}>}}\n"
        "\\pdfsuppressptexinfo=15\n"
    )

def main():
    submission_text = normalized_markdown(MANUSCRIPT).rstrip() + "\n\n" + RELATED.read_text(encoding="utf-8").lstrip()
    with tempfile.TemporaryDirectory() as td:
        td_path = Path(td)
        temp = td_path / "manuscript.md"
        header = td_path / "deterministic-pdf-header.tex"
        temp.write_text(submission_text, encoding="utf-8")
        header.write_text(deterministic_pdf_header(), encoding="utf-8")
        run([
            "pandoc", str(temp), "--pdf-engine=pdflatex", "-H", str(header),
            "-V", "geometry:margin=1in", "-V", "fontsize=11pt",
            "-o", str(HERE / "manuscript.pdf"),
        ])
    readme = (
        "ORION-04 journal source package\n\n"
        "`manuscript.md` is the publication-clean rendering source. The repository's "
        "WAVE3_SCOPED_MANUSCRIPT_V3.md and CLAIM_LEDGER_V3.md remain the scientific "
        "authority and are intentionally not rewritten by this package.\n"
    ).encode("utf-8")
    deterministic_zip_bytes(HERE / "source.zip", [
        ("manuscript.md", submission_text.encode("utf-8")),
        ("README.txt", readme),
    ])
    targets = ["manuscript.pdf", "source.zip"]
    lines = []
    for name in targets:
        digest = hashlib.sha256((HERE / name).read_bytes()).hexdigest()
        lines.append(f"{digest}  {name}")
    (HERE / "SHA256SUMS").write_text("\n".join(lines) + "\n", encoding="utf-8")

if __name__ == "__main__":
    main()

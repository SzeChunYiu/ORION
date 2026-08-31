#!/usr/bin/env python3
from pathlib import Path
import hashlib, os, subprocess, tempfile, zipfile

HERE = Path(__file__).resolve().parent
PAPER = HERE.parent.parent
MANUSCRIPT = PAPER / "WAVE3_SCOPED_MANUSCRIPT_V2.md"
RELATED = HERE / "RELATED_WORK_AND_NOVELTY.md"
FIXED_TIME = (2026, 8, 31, 0, 0, 0)

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
        "**ORION-04 — Wave 3 scientific successor V2**",
        "**Supersedes for journal science:**",
        "**Preserves:**",
    )
    text = "\n".join(line for line in text.splitlines() if not line.startswith(drop_prefixes)) + "\n"
    text = text.replace("\\[", "$$").replace("\\]", "$$").replace("\\(", "$").replace("\\)", "$")
    return text.replace("∎", "$\\square$")

def main():
    submission_text = normalized_markdown(MANUSCRIPT).rstrip() + "\n\n" + RELATED.read_text(encoding="utf-8").lstrip()
    with tempfile.TemporaryDirectory() as td:
        temp = Path(td) / "manuscript.md"
        temp.write_text(submission_text, encoding="utf-8")
        run(["pandoc", str(temp), "--pdf-engine=pdflatex", "-V", "geometry:margin=1in", "-V", "fontsize=11pt", "-o", str(HERE / "manuscript.pdf")])
    readme = (
        "ORION-04 journal source package\n\n"
        "`manuscript.md` is the publication-clean rendering source. The repository's "
        "WAVE3_SCOPED_MANUSCRIPT_V2.md and CLAIM_LEDGER_V2.md remain the scientific "
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

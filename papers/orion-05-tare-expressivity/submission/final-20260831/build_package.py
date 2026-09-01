#!/usr/bin/env python3
from pathlib import Path
import hashlib, os, shutil, subprocess, tempfile, zipfile

HERE = Path(__file__).resolve().parent
PAPER = HERE.parent.parent
SRC = PAPER / "manuscript"
FIXED_TIME = (2026, 8, 31, 0, 0, 0)

def run(cmd, cwd):
    env = os.environ.copy()
    env.setdefault("SOURCE_DATE_EPOCH", "1788166728")
    env.setdefault("FORCE_SOURCE_DATE", "1")
    subprocess.run(cmd, cwd=cwd, env=env, check=True)

def zip_tree(out_path, root):
    paths = [root / "main.tex", root / "bibliography.bib"] + sorted((root / "sections").glob("*.tex"))
    with zipfile.ZipFile(out_path, "w", zipfile.ZIP_DEFLATED) as zf:
        for src in paths:
            arc = src.relative_to(root).as_posix()
            info = zipfile.ZipInfo(arc, FIXED_TIME)
            info.external_attr = 0o644 << 16
            zf.writestr(info, src.read_bytes())

def main():
    with tempfile.TemporaryDirectory() as td:
        work = Path(td) / "source"
        shutil.copytree(SRC, work)
        run(["pdflatex", "-interaction=nonstopmode", "-halt-on-error", "main.tex"], work)
        run(["bibtex", "main"], work)
        run(["pdflatex", "-interaction=nonstopmode", "-halt-on-error", "main.tex"], work)
        run(["pdflatex", "-interaction=nonstopmode", "-halt-on-error", "main.tex"], work)
        shutil.copy2(work / "main.pdf", HERE / "manuscript.pdf")
        zip_tree(HERE / "arxiv-source.zip", work)
    names = ["manuscript.pdf", "arxiv-source.zip"]
    lines = [f"{hashlib.sha256((HERE/name).read_bytes()).hexdigest()}  {name}" for name in names]
    (HERE / "SHA256SUMS").write_text("\n".join(lines) + "\n", encoding="utf-8")

if __name__ == "__main__":
    main()

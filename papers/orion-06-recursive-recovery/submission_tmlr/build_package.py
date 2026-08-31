#!/usr/bin/env python3
from pathlib import Path
import hashlib, os, subprocess, tempfile, zipfile

HERE = Path(__file__).resolve().parent
PAPER = HERE.parent
SRC = PAPER / "manuscript"
FIXED_TIME = (2026, 8, 31, 0, 0, 0)

def run(cmd, cwd):
    env = os.environ.copy()
    env.setdefault("SOURCE_DATE_EPOCH", "1788166728")
    env.setdefault("FORCE_SOURCE_DATE", "1")
    subprocess.run(cmd, cwd=cwd, env=env, check=True)

def zip_files(out_path, entries):
    with zipfile.ZipFile(out_path, "w", zipfile.ZIP_DEFLATED) as zf:
        for arc, src in entries:
            info = zipfile.ZipInfo(arc, FIXED_TIME)
            info.external_attr = 0o644 << 16
            zf.writestr(info, Path(src).read_bytes())

def main():
    run(["pdflatex", "-interaction=nonstopmode", "-halt-on-error", "main.tex"], HERE)
    run(["bibtex", "main"], HERE)
    run(["pdflatex", "-interaction=nonstopmode", "-halt-on-error", "main.tex"], HERE)
    run(["pdflatex", "-interaction=nonstopmode", "-halt-on-error", "main.tex"], HERE)

    with tempfile.TemporaryDirectory() as td:
        work = Path(td)
        text = (HERE / "main.tex").read_text(encoding="utf-8")
        text = text.replace("../manuscript/sections/", "sections/")
        text = text.replace("../manuscript/bibliography", "bibliography")
        main_copy = work / "main.tex"
        main_copy.write_text(text, encoding="utf-8")
        entries = [
            ("main.tex", main_copy),
            ("tmlr.sty", HERE / "tmlr.sty"),
            ("tmlr.bst", HERE / "tmlr.bst"),
            ("fancyhdr.sty", HERE / "fancyhdr.sty"),
            ("bibliography.bib", SRC / "bibliography.bib"),
            ("09-ethics-safety-resources-anonymous.tex", HERE / "09-ethics-safety-resources-anonymous.tex"),
        ]
        entries += [(f"sections/{p.name}", p) for p in sorted((SRC / "sections").glob("*.tex")) if p.name != "09-ethics-safety-resources.tex"]
        zip_files(HERE / "anonymous-source.zip", entries)

    zip_files(HERE / "anonymous-review-supplement.zip", [
        ("ANONYMOUS_CLAIM_BOUNDARY.md", HERE / "ANONYMOUS_CLAIM_BOUNDARY.md"),
        ("REVIEW_SUPPLEMENT_README.md", HERE / "REVIEW_SUPPLEMENT_README.md"),
        ("AVAILABILITY_STATEMENT.md", HERE / "AVAILABILITY_STATEMENT.md"),
    ])

    names = ["main.pdf", "anonymous-source.zip", "anonymous-review-supplement.zip"]
    lines = [f"{hashlib.sha256((HERE/name).read_bytes()).hexdigest()}  {name}" for name in names]
    (HERE / "SHA256SUMS").write_text("\n".join(lines) + "\n", encoding="utf-8")

if __name__ == "__main__":
    main()

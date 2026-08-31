#!/usr/bin/env python3
from pathlib import Path
import re, sys, zipfile

ROOT = Path(__file__).resolve().parents[2]
errors = []

def need(path, text):
    data = (ROOT / path).read_text(encoding="utf-8")
    if text not in data:
        errors.append(f"{path}: missing required boundary {text!r}")

def reject(path, patterns):
    data = (ROOT / path).read_text(encoding="utf-8")
    for p in patterns:
        if re.search(p, data, flags=re.I):
            errors.append(f"{path}: forbidden publication phrase matched {p!r}")

need("papers/orion-04-rooted-completion-certificates/WAVE3_SCOPED_MANUSCRIPT_V2.md", "Exact D_4 remains open")
need("papers/orion-04-rooted-completion-certificates/CLAIM_LEDGER_V2.md", "WITHHELD / NOT CLAIMED")
need("papers/orion-05-tare-expressivity/CLAIM_LEDGER_V4.md", "NEGATIVE/OPEN TERMINAL PRESERVED")
need("papers/orion-05-tare-expressivity/manuscript/main.tex", "no full-circuit, hardware, or global block-encoding optimality is claimed")
need("papers/orion-06-recursive-recovery/CLAIM_LEDGER_V4.md", "CROSS-DOMAIN") if False else None
need("papers/orion-06-recursive-recovery/CLAIM_LEDGER_V4.md", "NEGATIVE/UNDETERMINED TERMINAL PRESERVED")
need("papers/orion-06-recursive-recovery/manuscript/main.tex", "one-programme case study, not a statistical evaluation")
need("papers/orion-06-recursive-recovery/submission_tmlr/PUBLICATION_CLOSURE.md", "CROSS_DOMAIN_UNDETERMINED")

reject("papers/orion-05-tare-expressivity/manuscript/sections/05-related-work-boundary.tex", [r"first ever", r"uniquely establishes"])
reject("papers/orion-06-recursive-recovery/manuscript/sections/05-related-work-boundary.tex", [r"first ever", r"uniquely establishes"])

zip_path = ROOT / "papers/orion-06-recursive-recovery/submission_tmlr/anonymous-source.zip"
if zip_path.exists():
    with zipfile.ZipFile(zip_path) as zf:
        joined = b"\n".join(zf.read(n) for n in zf.namelist() if n.endswith((".tex", ".bib", ".md"))).decode("utf-8", errors="replace")
    for token in ["Sze Chun Yiu", "sze-chun.yiu@", "ORION-Q", "development/orion", "research/extensions"]:
        if token in joined:
            errors.append(f"anonymous-source.zip leaks identifier: {token}")

if errors:
    print("ORION_04_06_PUBLICATION_CLOSURE=FAIL")
    for e in errors:
        print("-", e)
    sys.exit(1)
print("ORION_04_06_PUBLICATION_CLOSURE=PASS")

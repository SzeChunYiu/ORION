#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"
python verify_package.py
command -v pandoc >/dev/null
command -v pdflatex >/dev/null
command -v qpdf >/dev/null
command -v pdftotext >/dev/null
pandoc SOURCE.md --from=gfm+tex_math_dollars --standalone --pdf-engine=pdflatex -V geometry:margin=1in -V fontsize=11pt -o main.pdf
qpdf --check main.pdf
pdftotext main.pdf .main.txt
test -s .main.txt
python - <<'PY'
import json,re
from pathlib import Path
m=json.loads(Path('SUBMISSION_MANIFEST.json').read_text())
t=Path('.main.txt').read_text(errors='replace').lower()
words=[w.lower() for w in re.findall(r'[A-Za-z]{5,}',m['title'])][:4]
missing=[w for w in words if w not in t]
if len(t.strip()) < 1000 or missing: raise SystemExit(f'PDF text validation failed: missing={missing}, chars={len(t.strip())}')
PY
sha256sum SOURCE.md CLAIM_LEDGER.md main.pdf > BUILD_SHA256SUMS
python verify_package.py --require-render
rm -f .main.txt

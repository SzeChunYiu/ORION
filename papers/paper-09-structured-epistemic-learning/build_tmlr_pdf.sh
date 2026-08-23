#!/usr/bin/env bash
set -euo pipefail

HERE="$(cd "$(dirname "$0")" && pwd)"
MANUSCRIPT="$HERE/manuscript"

python "$HERE/reproduce_final.py"
python "$HERE/audit_final_manuscript.py"
bash "$HERE/fetch_tmlr_style.sh"

# The manuscript is maintained as reviewable text and historically used
# Markdown-style backticks for two machine terminal identifiers.  Build from a
# deterministic temporary LaTeX-safe rewrite and restore the source on exit;
# this changes no scientific prose or generated evidence.
cp "$MANUSCRIPT/main.tex" "$MANUSCRIPT/main.tex.build-backup"
restore_source() {
  mv -f "$MANUSCRIPT/main.tex.build-backup" "$MANUSCRIPT/main.tex" 2>/dev/null || true
}
trap restore_source EXIT
python - "$MANUSCRIPT/main.tex" <<'PY'
from pathlib import Path
import sys
p=Path(sys.argv[1])
s=p.read_text(encoding='utf-8')
replacements={
    '`P9_NEURAL_ESCALATION_NOT_JUSTIFIED`': r'\texttt{P9\_NEURAL\_ESCALATION\_NOT\_JUSTIFIED}',
    '`NEURAL_MODELS_FAIL`': r'\texttt{NEURAL\_MODELS\_FAIL}',
}
for old,new in replacements.items():
    s=s.replace(old,new)
p.write_text(s,encoding='utf-8')
PY

cd "$MANUSCRIPT"
pdflatex -interaction=nonstopmode -halt-on-error main.tex
bibtex main
pdflatex -interaction=nonstopmode -halt-on-error main.tex
pdflatex -interaction=nonstopmode -halt-on-error main.tex

if grep -Eq 'LaTeX Warning: (Citation|Reference).*undefined|There were undefined references' main.log; then
  echo 'undefined citations/references remain' >&2
  exit 1
fi
if grep -Eq 'Overfull \\hbox|Overfull \\vbox' main.log; then
  echo 'overfull box detected; inspect main.log' >&2
  grep -E 'Overfull \\hbox|Overfull \\vbox' main.log >&2 || true
  exit 1
fi

test -s main.pdf
echo "P9_TMLR_PDF=$MANUSCRIPT/main.pdf"

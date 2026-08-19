#!/usr/bin/env bash
set -euo pipefail

HERE="$(cd "$(dirname "$0")" && pwd)"
MANUSCRIPT="$HERE/manuscript"

python "$HERE/reproduce_final.py"
python "$HERE/audit_final_manuscript.py"
bash "$HERE/fetch_tmlr_style.sh"

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

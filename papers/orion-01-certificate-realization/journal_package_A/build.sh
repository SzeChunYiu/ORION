#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"
command -v pandoc >/dev/null
command -v pdflatex >/dev/null
pandoc SOURCE.md \
  --from=gfm \
  --standalone \
  --pdf-engine=pdflatex \
  -V geometry:margin=1in \
  -V fontsize=11pt \
  -o main.pdf
sha256sum SOURCE.md CLAIM_LEDGER.md main.pdf > BUILD_SHA256SUMS
printf 'built %s\n' "$(pwd)/main.pdf"

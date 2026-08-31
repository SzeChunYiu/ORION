#!/bin/sh
set -eu
PANDOC="${PANDOC:-pandoc}"
TECTONIC="${TECTONIC:-tectonic}"
export SOURCE_DATE_EPOCH="${SOURCE_DATE_EPOCH:-1788177600}"
"$PANDOC" MANUSCRIPT.md \
  --from=markdown+yaml_metadata_block \
  --to=latex \
  --natbib \
  --top-level-division=section \
  --template=jar-pandoc-template.tex \
  --wrap=preserve \
  --output=main.tex
python3 - <<'PY'
from pathlib import Path
p = Path('main.tex')
s = p.read_text(encoding='utf-8')
s = s.replace('\\section*{Statements and Declarations}',
              '\\backmatter\n\n\\section*{Statements and Declarations}', 1)
p.write_text(s, encoding='utf-8', newline='\n')
PY
"$TECTONIC" --keep-logs --keep-intermediates main.tex

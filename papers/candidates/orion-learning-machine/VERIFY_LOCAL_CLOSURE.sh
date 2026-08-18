#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")" && pwd)"
cd "$ROOT"
(cd framework && python -m pytest -q)
sha256sum -c closure_logs/FROZEN_SHA256SUMS.txt
python - <<'PY'
import json
from pathlib import Path
m=json.loads(Path('CLOSURE_MANIFEST.json').read_text())
assert m['authority'].startswith('LOCAL_CORE_COMPLETE')
print(f"manifest: {len(m['files'])} files recorded")
PY
printf 'Quick local closure verification PASS\n'

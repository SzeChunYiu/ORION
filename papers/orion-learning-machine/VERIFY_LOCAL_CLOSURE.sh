#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")" && pwd)"
cd "$ROOT"

python - <<'PY'
import hashlib
import json
from pathlib import Path

root = Path.cwd()
authority = json.loads((root / 'LOCAL_CLOSURE_AUTHORITY.json').read_text())
assert authority['authority'] == 'LOCAL_REPRODUCIBLE_CORE_ONLY'
manifest = root / 'PUBLICATION_MANIFEST_SHA256.txt'
checked = 0
for line in manifest.read_text().splitlines():
    if not line or line.startswith('#'):
        continue
    expected, relative = line.split('  ', 1)
    path = root / relative
    actual = hashlib.sha256(path.read_bytes()).hexdigest()
    if actual != expected:
        raise AssertionError(f'publication manifest drift: {relative}')
    checked += 1
print(f'publication manifest: PASS ({checked} files)')
print(f"authority: {authority['authority']}")
PY

PYTHONPATH=framework python -m pytest -q framework/tests
python ../paper-xx-executable-research-core/check_merged_ready.py
python ../archive/2026-08-pre-unification/paper-xx-content-bound-math-evaluation/check_technical_note_ready.py
printf 'P9/P10 bounded local closure: PASS\n'

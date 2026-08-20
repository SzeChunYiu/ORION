#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")" && pwd)"
cd "$ROOT"

# First require the historical closure verifier and its historical manifest to
# remain byte-for-byte valid. The V2 overlay is checked separately so the
# verifier never needs to validate its own superseded hash.
bash ./VERIFY_LOCAL_CLOSURE.sh

python - <<'PY'
import json
import subprocess
from pathlib import Path

root = Path.cwd()
overlay = json.loads((root / 'P10_PUBLICATION_OVERLAY_V2.json').read_text())
assert overlay['schema'] == 'P10.PublicationOverlay.v2'
expected = overlay['paths']
assert isinstance(expected, dict) and len(expected) == 9
for relative, blob_sha in sorted(expected.items()):
    path = root.parent / relative if relative.startswith('paper-') else root / relative
    if not path.is_file():
        raise AssertionError(f'overlay path missing: {relative}')
    actual = subprocess.check_output(['git', 'hash-object', str(path)], text=True).strip()
    if actual != blob_sha:
        raise AssertionError(f'P10 overlay drift: {relative}: {actual} != {blob_sha}')
print(f'P10 publication overlay V2: PASS ({len(expected)} files)')
PY

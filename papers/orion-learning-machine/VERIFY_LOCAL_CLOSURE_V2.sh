#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")" && pwd)"
cd "$ROOT"

# V2 preserves the historical verifier/manifests as immutable provenance, but
# the current review branch intentionally supersedes exactly nine P10 paper
# paths. Verify every other historical path against its frozen SHA-256, then
# verify the nine superseded paths against the fixed V2 Git-blob overlay.
python - <<'PY'
import hashlib
import json
import subprocess
from pathlib import Path

root = Path.cwd()
authority = json.loads((root / 'LOCAL_CLOSURE_AUTHORITY.json').read_text())
assert authority['authority'] == 'LOCAL_REPRODUCIBLE_CORE_ONLY'
overlay = json.loads((root / 'P10_PUBLICATION_OVERLAY_V2.json').read_text())
assert overlay['schema'] == 'P10.PublicationOverlay.v2'
expected = overlay['paths']
assert isinstance(expected, dict) and len(expected) == 9

def canonical_overlay_key(manifest_relative: str) -> str | None:
    # Historical P10 manifest entries are rooted from orion-learning-machine as
    # ../paper-xx-content-bound-math-evaluation/... . Normalize only that exact
    # namespace; no other legacy path may be skipped.
    prefix = '../paper-xx-content-bound-math-evaluation/'
    if manifest_relative.startswith(prefix):
        return 'paper-xx-content-bound-math-evaluation/' + manifest_relative[len(prefix):]
    return None

manifest = root / 'PUBLICATION_MANIFEST_SHA256.txt'
legacy_checked = 0
superseded_seen: set[str] = set()
for line in manifest.read_text().splitlines():
    if not line or line.startswith('#'):
        continue
    frozen_sha, relative = line.split('  ', 1)
    overlay_key = canonical_overlay_key(relative)
    if overlay_key in expected:
        superseded_seen.add(overlay_key)
        continue
    path = root / relative
    actual = hashlib.sha256(path.read_bytes()).hexdigest()
    if actual != frozen_sha:
        raise AssertionError(f'legacy publication manifest drift: {relative}')
    legacy_checked += 1

legacy_overlay_paths = {key for key in expected if key in superseded_seen}
# Four overlay files are additive and absent from the old manifest; five are
# exact substitutions. Require exactly those five substitutions to have been
# observed in the historical manifest.
if len(legacy_overlay_paths) != 5:
    raise AssertionError(f'expected exactly 5 superseded legacy P10 paths, saw {sorted(legacy_overlay_paths)}')

for relative, blob_sha in sorted(expected.items()):
    path = root.parent / relative
    if not path.is_file():
        raise AssertionError(f'overlay path missing: {relative}')
    actual = subprocess.check_output(['git', 'hash-object', str(path)], text=True).strip()
    if actual != blob_sha:
        raise AssertionError(f'P10 overlay drift: {relative}: {actual} != {blob_sha}')

print(f'legacy publication manifest excluding exact P10 substitutions: PASS ({legacy_checked} files)')
print(f'P10 publication overlay V2: PASS ({len(expected)} files; {len(legacy_overlay_paths)} substitutions, {len(expected)-len(legacy_overlay_paths)} additive)')
print(f"authority: {authority['authority']}")
PY

PYTHONPATH=framework python -m pytest -q framework/tests
python ../paper-xx-executable-research-core/check_merged_ready.py
python ../paper-xx-content-bound-math-evaluation/check_technical_note_ready.py
printf 'P9/P10 bounded local closure V2: PASS\n'

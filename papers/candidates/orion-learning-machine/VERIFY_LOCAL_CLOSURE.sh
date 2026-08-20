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
legacy_manifest = root / 'PUBLICATION_MANIFEST_SHA256.txt'
overlay_manifest = root / 'PUBLICATION_MANIFEST_P10_V2.txt'

# The 2026-08-18 SHA-256 manifest remains frozen for the large immutable corpus
# and all unchanged publication artifacts.  Only this exact allowlist is
# superseded by the 2026-08-20 P10 review-package overlay.
overlay_allowlist = {
    '../paper-10-content-bound-math-evaluation/CLAIM_LEDGER.md',
    '../paper-10-content-bound-math-evaluation/FOLLOW_UPS.md',
    '../paper-10-content-bound-math-evaluation/JOURNAL_READINESS.md',
    '../paper-10-content-bound-math-evaluation/P10_REVIEW_EXPANSION_BOUNDARY.md',
    '../paper-10-content-bound-math-evaluation/REVIEW_PACKAGE_STATUS_2026-08-20.md',
    '../paper-10-content-bound-math-evaluation/TECHNICAL_NOTE.md',
    '../paper-10-content-bound-math-evaluation/analyze_module_robustness_v1.py',
    '../paper-10-content-bound-math-evaluation/check_technical_note_ready.py',
    '../paper-10-content-bound-math-evaluation/results/MATHLIB_TRANSFER_V2_1_MODULE_ROBUSTNESS_RECEIPT_V1.json',
}

def rows(path: Path):
    parsed = []
    for line in path.read_text().splitlines():
        if not line or line.startswith('#'):
            continue
        expected, relative = line.split('  ', 1)
        parsed.append((expected, relative))
    return parsed

legacy_checked = 0
legacy_paths = set()
for expected, relative in rows(legacy_manifest):
    legacy_paths.add(relative)
    if relative in overlay_allowlist:
        continue
    path = root / relative
    actual = hashlib.sha256(path.read_bytes()).hexdigest()
    if actual != expected:
        raise AssertionError(f'legacy publication manifest drift: {relative}')
    legacy_checked += 1

# Every modified legacy P10 path must be present in the overlay; new overlay
# paths are also fixed by the allowlist above.  Nothing else can be silently
# skipped from the legacy manifest.
overlay_rows = rows(overlay_manifest)
overlay_paths = {relative for _, relative in overlay_rows}
if overlay_paths != overlay_allowlist:
    missing = sorted(overlay_allowlist - overlay_paths)
    extra = sorted(overlay_paths - overlay_allowlist)
    raise AssertionError(f'P10 overlay path set drift: missing={missing}, extra={extra}')

modified_legacy_paths = overlay_allowlist & legacy_paths
expected_modified_legacy = {
    '../paper-10-content-bound-math-evaluation/CLAIM_LEDGER.md',
    '../paper-10-content-bound-math-evaluation/FOLLOW_UPS.md',
    '../paper-10-content-bound-math-evaluation/JOURNAL_READINESS.md',
    '../paper-10-content-bound-math-evaluation/TECHNICAL_NOTE.md',
    '../paper-10-content-bound-math-evaluation/check_technical_note_ready.py',
}
if modified_legacy_paths != expected_modified_legacy:
    raise AssertionError(
        f'legacy P10 supersession set drift: {sorted(modified_legacy_paths)}'
    )

overlay_checked = 0
for expected_blob, relative in overlay_rows:
    path = root / relative
    data = path.read_bytes()
    header = f'blob {len(data)}\0'.encode('ascii')
    actual_blob = hashlib.sha1(header + data).hexdigest()
    if actual_blob != expected_blob:
        raise AssertionError(f'P10 V2 overlay drift: {relative}')
    overlay_checked += 1

print(f'legacy publication manifest: PASS ({legacy_checked} unchanged files)')
print(f'P10 V2 publication overlay: PASS ({overlay_checked} files)')
print(f"authority: {authority['authority']}")
PY

PYTHONPATH=framework python -m pytest -q framework/tests
python ../paper-09-executable-research-core/check_merged_ready.py
python ../paper-10-content-bound-math-evaluation/check_technical_note_ready.py
printf 'P9/P10 bounded local closure: PASS\n'

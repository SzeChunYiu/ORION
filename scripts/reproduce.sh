#!/usr/bin/env bash
# Clean-environment reproduction path.
#
# Exit codes are deliberately distinct:
#   0  ran and passed
#   1  ran and FAILED  -- a real defect
#   2  COULD NOT RUN   -- environment problem, verdict unknown
#
# Conflating 2 with 0 is the failure mode this script exists to avoid: a
# reproduction that silently skips its checks reports success while proving
# nothing.
set -uo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
VENV="${ORION_REPRO_VENV:-$(mktemp -d)/venv}"

step() { printf '\n=== %s ===\n' "$1"; }
cannot() { printf 'CANNOT_CHECK: %s\n' "$1" >&2; exit 2; }

step "preflight"
# Without this, a missing interpreter kills the script with the shell's 127
# and the caller sees a generic failure instead of this script's own
# CANNOT_CHECK. An exit code that cannot report "I could not run" is exactly
# what the 0/1/2 split exists to prevent.
for tool in python3 mktemp; do
  command -v "$tool" >/dev/null 2>&1 || cannot "required tool '$tool' is not on PATH"
done

step "clean interpreter"
python3 -m venv "$VENV" || cannot "could not create a virtualenv"
# shellcheck disable=SC1091
source "$VENV/bin/activate" || cannot "could not activate the virtualenv"
python -m pip install --quiet --upgrade pip || cannot "pip unavailable"

step "install from source"
python -m pip install --quiet -e "$ROOT" || { echo "FAILED: package does not install from a clean environment"; exit 1; }

step "import surface"
python - <<'PY' || { echo "FAILED: package does not import"; exit 1; }
import orion
from orion.programme.catalogue import ALL_CHECKS, ALL_CHECK_IDS
print(f"checks registered: {len(ALL_CHECKS)}")
assert len(ALL_CHECK_IDS) == len(set(ALL_CHECK_IDS)), "duplicate check ids"
PY

step "import sweep"
# A two-module smoke test passes on a package with incomplete dependency
# metadata. This walks every module and separates core failures (a real
# defect) from optional-extra failures (expected on a base install).
python "$ROOT/scripts/import_sweep.py" || { echo "FAILED: a core module does not import with declared dependencies alone"; exit 1; }

step "check battery self-consistency"
python - <<'PY' || { echo "FAILED: check battery is internally inconsistent"; exit 1; }
from orion.programme.catalogue import validate_catalogue
errs = validate_catalogue()
if errs:
    for e in errs:
        print("DEFECT:", e)
    raise SystemExit(1)
print("catalogue clean: every check has a unique id and its own negative fixture")
PY

step "environment manifest"
python "$ROOT/scripts/environment_manifest.py" "$ROOT/ENVIRONMENT_MANIFEST.json" || cannot "manifest could not be written"

printf '\nREPRODUCTION OK\n'

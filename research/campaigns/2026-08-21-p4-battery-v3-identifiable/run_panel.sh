#!/usr/bin/env bash
# Run the frozen P4 panel over a freshly minted V3 battery.
#
# Nothing here is modified from the frozen campaign except the battery it is
# pointed at: run_candidate.py, run_baselines.py, run_baselines_v2.py and
# evaluate_campaign_v2.py are used exactly as they stand. Protocol: FREEZE.md.
set -euo pipefail

ROOT=/home/user/ORION
HOST="$ROOT/papers/paper-04-verified-scientific-discovery/host"
PY="$ROOT/.venv/bin/python"
WORK="${1:?usage: run_panel.sh <workdir>}"
SEED="${2:-p4-v3-panel-20260821}"
CONSTRUCTION="${3:-v3}"

# The frozen subject commit the V2 campaign ran against; the subject is unchanged
# by this repair, only the battery is.
SUBJECT_COMMIT=f6e51b5c8f905382b8e2f5568d9035fc14241aa1
ZERO=$(printf '0%.0s' $(seq 64))

mkdir -p "$WORK"
BATTERY="$WORK/battery"
rm -rf "$BATTERY"

HARNESS=$("$PY" - <<'PY'
import hashlib
from pathlib import Path
root = Path("/home/user/ORION")
files = [
    'generate_protected_cases.py', 'run_candidate.py', 'run_baselines.py',
    'run_baselines_v2.py', 'run_ablations.py', 'evaluate_campaign.py',
    'evaluate_campaign_v2.py', 'evaluate_ablations.py',
    'independent_reproduce.py', 'independent_reproduce_v2.py',
    'BASELINE_CONFIGS_V2.json',
]
host = root / 'papers/paper-04-verified-scientific-discovery/host'
digest = hashlib.sha256()
for name in files:
    digest.update(name.encode()); digest.update(b'\0')
    digest.update(hashlib.sha256((host / name).read_bytes()).digest())
print(digest.hexdigest())
PY
)
BASELINE=$(sha256sum "$HOST/BASELINE_CONFIGS_V2.json" | awk '{print $1}')

echo "== minting battery (construction=$CONSTRUCTION seed=$SEED)"
"$PY" "$HOST/generate_protected_cases.py" \
  --seed "$SEED" \
  --construction "$CONSTRUCTION" \
  --output-dir "$BATTERY" \
  --subject-commit "$SUBJECT_COMMIT" \
  --subject-archive-sha256 "$ZERO" \
  --evaluator-artifact-sha256 "$HARNESS" \
  --baseline-config-sha256 "$BASELINE" \
  --host-run-id "p4-v3-local" \
  --evaluation-epoch "2026-08-21T00:00:00Z"

ORION_ARGS=()
BASE_ARGS=()
for i in 1 2 3 4 5; do
  echo "== repeat $i: ORION"
  "$PY" "$HOST/run_candidate.py" "$BATTERY/candidate_manifest.jsonl" "$WORK/orion-$i.jsonl"
  echo "== repeat $i: comparators"
  "$PY" "$HOST/run_baselines_v2.py" "$BATTERY/candidate_manifest.jsonl" "$WORK/baselines-$i.jsonl"
  ORION_ARGS+=(--orion-output "$WORK/orion-$i.jsonl")
  BASE_ARGS+=(--baseline-output "$WORK/baselines-$i.jsonl")
done

echo "== frozen evaluator"
rm -rf "$WORK/eval"
"$PY" "$HOST/evaluate_campaign_v2.py" \
  --protected-manifest "$BATTERY/protected_manifest.jsonl" \
  --run-manifest "$BATTERY/RUN_MANIFEST_V1.json" \
  "${ORION_ARGS[@]}" "${BASE_ARGS[@]}" \
  --output-dir "$WORK/eval" \
  --campaign-run-id "p4-${CONSTRUCTION}-local-20260821"
echo "== done: $WORK/eval"

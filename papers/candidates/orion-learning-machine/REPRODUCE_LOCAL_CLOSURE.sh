#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")" && pwd)"
cd "$ROOT"
mkdir -p closure_logs

printf '== framework tests ==\n'
(cd framework && python -m pytest -q) | tee closure_logs/pytest.txt

printf '\n== phase 0 ==\n'
python experiments/phase0_solver_ecology/run.py | tee closure_logs/phase0.txt

printf '\n== phase 1 (CPU-heavy) ==\n'
python experiments/phase1_mechanic_composition/run_v1.py | tee closure_logs/phase1.txt

printf '\n== phase 2A ==\n'
PYTHONPATH=framework python experiments/phase2_real_source/run_phase2a.py | tee closure_logs/phase2a.txt

printf '\n== phase 2B ==\n'
PYTHONPATH=framework python experiments/phase2_real_source/run_phase2b_goal_effect.py | tee closure_logs/phase2b.txt

printf '\n== hashes ==\n'
sha256sum closure_logs/*.txt | tee closure_logs/SHA256SUMS.txt
printf 'Local closure reproduction complete.\n'

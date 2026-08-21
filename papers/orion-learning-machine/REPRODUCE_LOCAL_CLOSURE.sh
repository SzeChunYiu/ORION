#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")" && pwd)"
cd "$ROOT"

printf '== bounded current closure ==\n'
./VERIFY_LOCAL_CLOSURE.sh

printf '\n== deterministic local experiments ==\n'
PYTHONPATH=framework python experiments/phase0_solver_ecology/run.py
PYTHONPATH=framework python experiments/phase1_mechanic_composition/run_v2.py
PYTHONPATH=framework python experiments/phase2_real_source/run_phase2a.py

printf '\nPhase 2B is intentionally not invoked: its legacy input is unavailable and the question is removed from the current P10 note.\n'
printf 'P9/P10 local reproduction complete.\n'

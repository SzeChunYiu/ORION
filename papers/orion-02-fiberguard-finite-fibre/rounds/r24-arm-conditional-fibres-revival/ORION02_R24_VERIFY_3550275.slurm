#!/usr/bin/env bash
#SBATCH --job-name=o02-r24-verify
#SBATCH --partition=lu48
#SBATCH --account=lu2026-2-51
#SBATCH --time=00:20:00
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=1
#SBATCH --mem=4G
#SBATCH --output=/projects/hep/fs9/scratch/scyiu-orion-ci/wtO02R24/papers/orion-02-fiberguard-finite-fibre/rounds/r24-arm-conditional-fibres-revival/ORION02_R24_VERIFY_3550275_JOB_%j.out
#SBATCH --error=/projects/hep/fs9/scratch/scyiu-orion-ci/wtO02R24/papers/orion-02-fiberguard-finite-fibre/rounds/r24-arm-conditional-fibres-revival/ORION02_R24_VERIFY_3550275_JOB_%j.err
set -euo pipefail

: "${EXPECTED_SOURCE_COMMIT:?submit with --export=ALL,EXPECTED_SOURCE_COMMIT=<amendment-commit>}"
W=/projects/hep/fs9/scratch/scyiu-orion-ci/wtO02R24
D=$W/papers/orion-02-fiberguard-finite-fibre/rounds/r24-arm-conditional-fibres-revival
F=$D/failed-executions/3550275
PYTHON=/projects/hep/fs9/scratch/scyiu-orion-ci/ORION/.venv/bin/python
cd "$W"

test "$(git rev-parse HEAD)" = "$EXPECTED_SOURCE_COMMIT"
unexpected=$(git status --porcelain | grep -Ev "^\?\? papers/orion-02-fiberguard-finite-fibre/rounds/r24-arm-conditional-fibres-revival/ORION02_R24_VERIFY_3550275_JOB_${SLURM_JOB_ID}\.(out|err)$" || true)
test -z "$unexpected"

# Verification-only recovery: never invoke the R24 executor.
forbidden='fiberguard_pmlb_arm_conditional_r24.py --subject''-repo'
! grep -q "$forbidden" "$0"
"$PYTHON" -m unittest \
  papers.orion-02-fiberguard-finite-fibre.rounds.r24-arm-conditional-fibres-revival.test_verify_fiberguard_pmlb_arm_conditional_r24
for run in a b; do
  "$PYTHON" "$D/verify_fiberguard_pmlb_arm_conditional_r24.py" \
    --result "$F/run_${run}.result.json" \
    --terminal "$F/run_${run}.terminal.txt" \
    --r23-parent "$F/run_${run}.parent.json"
done

cmp "$F/run_a.result.json" "$F/run_b.result.json"
cmp "$F/run_a.parent.json" "$F/run_b.parent.json"
cmp "$F/run_a.terminal.txt" "$F/run_b.terminal.txt"
test "$(sha256sum "$F/run_a.result.json" | awk '{print $1}')" = b21f54b9aad939b60e9600fc11ba856e8942bc81c73f84b3e28161667a20df54
test "$(sha256sum "$F/run_a.parent.json" | awk '{print $1}')" = cf1a0db71ab135278b64c02633f07d05a23604a121f0b62743f4e59c6358fc77
test "$(cat "$F/run_a.terminal.txt")" = C_R24_ARM_CONDITIONAL_CERTIFICATE_INVALID
echo "ORION02_R24_JOB_3550275_VERIFICATION_ONLY=PASS"
echo "RESULT_SHA256=b21f54b9aad939b60e9600fc11ba856e8942bc81c73f84b3e28161667a20df54"
echo "TERMINAL=C_R24_ARM_CONDITIONAL_CERTIFICATE_INVALID"

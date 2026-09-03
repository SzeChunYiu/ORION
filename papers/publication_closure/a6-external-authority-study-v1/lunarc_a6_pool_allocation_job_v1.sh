#!/usr/bin/env bash
# A6 downstream lane: eligible pool v1 -> frozen replication quotas ->
# deterministic pre-outcome allocation -> intake manifest v1 -> external
# adjudication prep. Pure-local deterministic compute over the frozen census
# snapshots; no network access is performed by any script in this job.
#SBATCH --job-name=orion-a6-pool
#SBATCH --account=lu2026-2-51
#SBATCH --partition=lu48
#SBATCH --time=01:00:00
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=2
#SBATCH --mem=8G
#SBATCH --output=/projects/hep/fs9/users/scyiu/a6-pool-20260903/logs/pool_%j.out
#SBATCH --error=/projects/hep/fs9/users/scyiu/a6-pool-20260903/logs/pool_%j.err

set -euo pipefail
BASE=/projects/hep/fs9/users/scyiu/a6-pool-20260903
DIR="$BASE/papers/publication_closure/a6-external-authority-study-v1"
mkdir -p "$BASE/logs"

cd "$DIR"
echo "=== host: $(hostname) date: $(date -u +%Y-%m-%dT%H:%M:%SZ) job: $SLURM_JOB_ID ==="
python3 --version

echo "=== hostile self-tests (pool / intake / prep + frozen validators) ==="
python3 build_eligible_external_authority_pool_v1.py --self-test > "$BASE/logs/pool_selftest_${SLURM_JOB_ID}.json"
python3 build_external_authority_intake_manifest_v1.py --self-test > "$BASE/logs/intake_selftest_${SLURM_JOB_ID}.json"
python3 prepare_external_adjudicator_packets_v1.py --self-test > "$BASE/logs/prep_selftest_${SLURM_JOB_ID}.json"
python3 validate_external_authority_packet_manifest_v1.py --self-test > "$BASE/logs/intake_validator_selftest_${SLURM_JOB_ID}.json"
python3 allocate_external_authority_packets_v1.py --self-test > "$BASE/logs/allocator_selftest_${SLURM_JOB_ID}.json"
python3 validate_external_adjudicator_packet_v1.py --self-test > "$BASE/logs/gold_validator_selftest_${SLURM_JOB_ID}.json"
grep -h '"decision"' "$BASE/logs"/*selftest_${SLURM_JOB_ID}.json

echo "=== eligible pool build (from frozen census + quota freeze) ==="
python3 build_eligible_external_authority_pool_v1.py \
  --quota-freeze A6_REPLICATION_QUOTA_FREEZE_V1.json \
  --output eligible-pool-v1/A6_ELIGIBLE_POOL_V1.json > "$BASE/logs/pool_build_${SLURM_JOB_ID}.summary.json"

echo "=== deterministic pre-outcome allocation (frozen allocator) ==="
mkdir -p allocation-v1
python3 allocate_external_authority_packets_v1.py \
  eligible-pool-v1/A6_ELIGIBLE_POOL_V1.json > allocation-v1/A6_PREOUTCOME_ALLOCATION_RESULT_V1.json

echo "=== intake manifest build + frozen intake validation ==="
mkdir -p intake-v1
python3 build_external_authority_intake_manifest_v1.py \
  --pool eligible-pool-v1/A6_ELIGIBLE_POOL_V1.json \
  --allocation allocation-v1/A6_PREOUTCOME_ALLOCATION_RESULT_V1.json \
  --output intake-v1/A6_EXTERNAL_AUTHORITY_PACKET_INTAKE_MANIFEST_V1.json \
  --validation-output intake-v1/A6_INTAKE_VALIDATION_RESULT_V1.json

echo "=== external adjudication prep (sign-off slots left empty) ==="
python3 prepare_external_adjudicator_packets_v1.py \
  --intake intake-v1/A6_EXTERNAL_AUTHORITY_PACKET_INTAKE_MANIFEST_V1.json \
  --prep-dir adjudication-prep-v1 > "$BASE/logs/prep_build_${SLURM_JOB_ID}.json"

echo "=== re-verification pass (verify mode) ==="
python3 prepare_external_adjudicator_packets_v1.py --verify \
  --intake intake-v1/A6_EXTERNAL_AUTHORITY_PACKET_INTAKE_MANIFEST_V1.json \
  --prep-dir adjudication-prep-v1 > "$BASE/logs/prep_verify_${SLURM_JOB_ID}.json"

echo "=== allocation terminal + digests ==="
python3 - <<'PY'
import json
a=json.load(open('allocation-v1/A6_PREOUTCOME_ALLOCATION_RESULT_V1.json'))
i=json.load(open('intake-v1/A6_INTAKE_VALIDATION_RESULT_V1.json'))
p=json.load(open('adjudication-prep-v1/A6_PREP_COVERAGE_MANIFEST_V1.json'))
print('terminal:',a['terminal'])
print('primary_n:',a['primary_n'],'replication_n:',a['replication_n'])
print('selection_manifest_sha256:',a['selection_manifest_sha256'])
print('intake_validation_decision:',i['decision'])
print('prep_packet_n:',p['prep_packet_n'],'sign_off_slots_empty:',p['sign_off_slots_empty_for_every_packet'])
PY
sha256sum eligible-pool-v1/A6_ELIGIBLE_POOL_V1.json allocation-v1/A6_PREOUTCOME_ALLOCATION_RESULT_V1.json intake-v1/A6_EXTERNAL_AUTHORITY_PACKET_INTAKE_MANIFEST_V1.json adjudication-prep-v1/A6_PREP_COVERAGE_MANIFEST_V1.json
echo "=== DONE ==="

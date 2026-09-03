#!/usr/bin/env bash
# A6 census: stratum 3 only (DataCite supplement-side enumeration).
#SBATCH --job-name=orion-a6-s3
#SBATCH --account=lu2026-2-51
#SBATCH --partition=lu48
#SBATCH --time=02:00:00
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=2
#SBATCH --mem=4G
#SBATCH --output=/home/scyiu/orion-a6-census/logs/a6_s3_%j.out
#SBATCH --error=/home/scyiu/orion-a6-census/logs/a6_s3_%j.err
set -euo pipefail
DIR=/home/scyiu/orion-a6-census/papers/publication_closure/a6-external-authority-study-v1
mkdir -p /home/scyiu/orion-a6-census/logs
cd "$DIR"
echo "=== host: $(hostname) date: $(date -u +%Y-%m-%dT%H:%M:%SZ) job: $SLURM_JOB_ID ==="
python3 census_a6_scientific_record_transitions_v1.py --self-test
echo "=== stratum-3 census run (datacite IsSupplementTo -> crossref article) ==="
python3 census_a6_scientific_record_transitions_v1.py --records 300 --workers 2 > "/home/scyiu/orion-a6-census/logs/a6_s3_result_${SLURM_JOB_ID}.json"
ls -la "$DIR/scientific-record-census-v1/"
echo "=== DONE ==="

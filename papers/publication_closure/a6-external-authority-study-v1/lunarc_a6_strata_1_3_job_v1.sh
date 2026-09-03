#!/usr/bin/env bash
# A6 census follow-up: stratum 1 (Zenodo software releases) + stratum 3
# (Crossref/DataCite scientific-record transitions). Stratum 2 already
# completed in job 3569334 and is NOT rerun (snapshots preserved).
#SBATCH --job-name=orion-a6-s1-s3
#SBATCH --account=lu2026-2-51
#SBATCH --partition=lu48
#SBATCH --time=04:00:00
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=2
#SBATCH --mem=4G
#SBATCH --output=/home/scyiu/orion-a6-census/logs/a6_strata_1_3_%j.out
#SBATCH --error=/home/scyiu/orion-a6-census/logs/a6_strata_1_3_%j.err

set -euo pipefail
BASE=/home/scyiu/orion-a6-census
DIR="$BASE/papers/publication_closure/a6-external-authority-study-v1"
mkdir -p "$BASE/logs"

cd "$DIR"
echo "=== host: $(hostname) date: $(date -u +%Y-%m-%dT%H:%M:%SZ) job: $SLURM_JOB_ID ==="
python3 --version

echo "=== stratum-1 self-test (zenodo) ==="
python3 census_a6_zenodo_software_releases_v1.py --self-test

echo "=== stratum-3 self-test (crossref/datacite) ==="
python3 census_a6_scientific_record_transitions_v1.py --self-test

echo "=== stratum-1 census run (zenodo, size=25 pages fix) ==="
python3 census_a6_zenodo_software_releases_v1.py --families 400 --workers 2 > "$BASE/logs/a6_s1_zenodo_${SLURM_JOB_ID}.json"

echo "=== stratum-3 census run (crossref is-supplemented-by -> datacite) ==="
python3 census_a6_scientific_record_transitions_v1.py --articles 300 --workers 2 > "$BASE/logs/a6_s3_crossref_${SLURM_JOB_ID}.json"

echo "=== snapshots ==="
ls -la "$DIR/zenodo-census-v1/" || true
ls -la "$DIR/scientific-record-census-v1/" || true
echo "=== DONE ==="

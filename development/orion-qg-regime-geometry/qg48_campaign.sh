#!/bin/bash
# QG48 campaign harness — pack (Mac) / launch (sanctioned host) / collect (Mac).
#
# Pure-math, no-network batch per the standing compute-host discipline
# (same pattern as qg47_campaign.sh):
#   - LUNARC: ship the tarball (NO repo clone, NO outbound network on
#     nodes), sbatch the R1 array + R2 arrays in waves of <= 250, tar the
#     parts back to the Mac.
#   - laptop billy: same tarball, bounded rolling queue.
#   - NEVER a local worker pool on the Mac mini.
#
# Usage:
#   ./qg48_campaign.sh pack                     # builds /tmp/qg48_campaign.tar.gz
#   ./qg48_campaign.sh launch-remote HOST DIR   # ssh: extract, sbatch R1 + R2 waves
#   ./qg48_campaign.sh launch-laptop DIR [PAR]  # rolling queue on billy-laptop
#   ./qg48_campaign.sh collect HOST DIR         # scp parts back to QG48_*_PARTS
#   python3 research/extensions/orion-qg/qg48_n3_frontier_prospection.py --merge   # Mac
set -euo pipefail

HERE_MAC="$(cd "$(dirname "$0")/../../" && pwd)"   # repo root (worktree)
QGDIR="$HERE_MAC/research/extensions/orion-qg"
TARBALL=/tmp/qg48_campaign.tar.gz

# Module-level import closure (AST-verified for qg47_n2_full_sweep +
# qg2_objective_robustness, identical to the QG47 pack): qg2 imports the
# orion-q donor machinery and resolves it as HERE.parent/"orion-q", so the
# tarball must preserve the two-directory layout.
ORION_Q_CLOSURE=(
  max_r4d_h2o_ducc_confirmation
  max_r5h_mixed_cardinality_development
  max_r6_exact_tare3_joint_frame_dp
  max_r6_p10_candidate_blind_frame_optimizer
  max_r6b_tare_transformation_reuse_donor
  max_r6d_sixterm_partition_representation_coopt
  max_r6e_deep_p10_exact_frame_saturation
  max_r6f_donor_clifford_preconditioned_tare3
  max_r6h_partial_tag_sharing_donor
  max_r6j_partial_restore_factor_donor
  max_r6m_exact_three_tare2_shared_factor_dp
  max_r6o_enlarged_tag_donor_closure
  max_r6p_weight2_frame_donor_closure
  max_r6q_regime_predicate
)

pack() {
  tmp=$(mktemp -d)
  mkdir -p "$tmp/qg48/ext/orion-qg" "$tmp/qg48/ext/orion-q"
  cp "$QGDIR/qg48_n3_frontier_prospection.py" \
     "$QGDIR/qg47_n2_full_sweep.py" \
     "$QGDIR/qg2_objective_robustness.py" \
     "$QGDIR/QG45_WITNESS8_ANATOMY_RESULTS.json" \
     "$QGDIR/QG46_KERNEL_ANATOMY_RESULTS.json" \
     "$QGDIR/QG47_N2_FULL_SWEEP_RESULTS.json" \
     "$tmp/qg48/ext/orion-qg/"
  for m in "${ORION_Q_CLOSURE[@]}"; do
    cp "$QGDIR/../orion-q/$m.py" "$tmp/qg48/ext/orion-q/"
  done
  # Read-only receipt inputs referenced by the donor machinery.
  cp "$QGDIR/../orion-q/MAX_R6M_EXACT_THREE_TARE2_SHARED_FACTOR_DP_RESULTS.json" \
     "$QGDIR/../orion-q/MAX_R6O_ENLARGED_TAG_DONOR_RESULTS.json" \
     "$QGDIR/../orion-q/MAX_R6P_WEIGHT2_FRAME_DONOR_CLOSURE_RESULTS.json" \
     "$QGDIR/../orion-q/MAX_R6Q_REGIME_PREDICATE_RESULTS.json" \
     "$tmp/qg48/ext/orion-q/"
  cat > "$tmp/qg48/r1_task.sh" <<'EOS'
#!/bin/bash
#SBATCH --job-name=qg48r1
#SBATCH --array=0-5
#SBATCH --time=02:00:00
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=1
#SBATCH --output=logs/r1_%a.out
#SBATCH --error=logs/r1_%a.err
set -euo pipefail
TOP="${SLURM_SUBMIT_DIR:-$(cd "$(dirname "$0")" && pwd)}"
mkdir -p "$TOP/r1_parts" "$TOP/logs"
python3 "$TOP/ext/orion-qg/qg48_n3_frontier_prospection.py" --r1-chunk "$SLURM_ARRAY_TASK_ID" --r1-parts-dir "$TOP/r1_parts"
EOS
  cat > "$tmp/qg48/r2_task.sh" <<'EOS'
#!/bin/bash
#SBATCH --job-name=qg48r2
#SBATCH --time=02:00:00
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=1
#SBATCH --output=logs/r2_%a.out
#SBATCH --error=logs/r2_%a.err
set -euo pipefail
TOP="${SLURM_SUBMIT_DIR:-$(cd "$(dirname "$0")" && pwd)}"
mkdir -p "$TOP/r2_parts" "$TOP/logs"
python3 "$TOP/ext/orion-qg/qg48_n3_frontier_prospection.py" --r2-chunk "$SLURM_ARRAY_TASK_ID" --r2-parts-dir "$TOP/r2_parts"
EOS
  chmod +x "$tmp/qg48/r1_task.sh" "$tmp/qg48/r2_task.sh"
  tar -C "$tmp" -czf "$TARBALL" qg48
  rm -rf "$tmp"
  echo "packed: $TARBALL ($(du -h "$TARBALL" | cut -f1))"
  echo "ship:   scp $TARBALL <host>:"
  echo "run:    ssh <host> 'mkdir -p qg48run && tar -C qg48run -xzf qg48_campaign.tar.gz && cd qg48run/qg48 && sbatch r1_task.sh && for w in 0-249 250-499 500-749 750-999 1000-1249 1250-1349; do sbatch --array=\$w r2_task.sh; done'"
}

launch_remote() {
  local host="$1" dir="$2"
  ssh "$host" "set -e; mkdir -p '$dir' && tar -C '$dir' -xzf - && cd '$dir/qg48' && mkdir -p r1_parts r2_parts logs && sbatch r1_task.sh && for w in 0-249 250-499 500-749 750-999 1000-1249 1250-1349; do sbatch --array=\$w r2_task.sh; done" < "$TARBALL"
}

launch_laptop() {
  # Bounded rolling queue on laptop billy (sanctioned heavy host).
  local dir="$1" par="${2:-6}"
  ssh billy-laptop "set -e; mkdir -p '$dir' && tar -C '$dir' -xzf - && cd '$dir/qg48' && mkdir -p r1_parts r2_parts logs && \
    seq 0 5 | xargs -P '$par' -I{} sh -c 'python3 ext/orion-qg/qg48_n3_frontier_prospection.py --r1-chunk {} --r1-parts-dir r1_parts >> logs/r1_{}.out 2>&1' && \
    seq 0 1349 | xargs -P '$par' -I{} sh -c 'python3 ext/orion-qg/qg48_n3_frontier_prospection.py --r2-chunk {} --r2-parts-dir r2_parts >> logs/r2_{}.out 2>&1' && \
    echo ALL_CHUNKS_DONE" < "$TARBALL"
}

collect() {
  local host="$1" dir="$2"
  local tmp
  tmp=$(mktemp -d)
  mkdir -p "$QGDIR/QG48_R1_PARTS" "$QGDIR/QG48_R2_PARTS"
  ssh "$host" "cd '$dir/qg48' && tar -czf - r1_parts r2_parts" | tar -C "$tmp" -xz
  cp "$tmp"/r1_parts/*.json "$QGDIR/QG48_R1_PARTS/"
  cp "$tmp"/r2_parts/*.json "$QGDIR/QG48_R2_PARTS/"
  rm -rf "$tmp"
  echo "collected r1: $(ls "$QGDIR/QG48_R1_PARTS" | grep -c 'r1_part') r2: $(ls "$QGDIR/QG48_R2_PARTS" | grep -c 'r2_part')"
  echo "next: python3 research/extensions/orion-qg/qg48_n3_frontier_prospection.py --merge"
}

case "${1:-}" in
  pack) pack ;;
  launch-remote) launch_remote "${2:?host}" "${3:?dir}" ;;
  launch-laptop) launch_laptop "${2:?dir}" "${3:-6}" ;;
  collect) collect "${2:?host}" "${3:?dir}" ;;
  *) echo "usage: $0 pack | launch-remote HOST DIR | launch-laptop DIR [PAR] | collect HOST DIR" >&2; exit 2 ;;
esac

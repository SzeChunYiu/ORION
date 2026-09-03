#!/bin/bash
# QG47 campaign harness — pack (Mac) / launch (sanctioned host) / collect (Mac).
#
# Pure-math, no-network batch per the standing compute-host discipline:
#   - LUNARC: scp the tarball over (NO repo clone, NO outbound network on
#     nodes), sbatch array, tar parts back, scp to the Mac.
#   - laptop billy: same tarball, run via a bounded rolling queue.
#   - NEVER a local worker pool on the Mac mini.
#
# Usage:
#   ./qg47_campaign.sh pack                 # builds /tmp/qg47_campaign.tar.gz
#   ./qg47_campaign.sh launch-remote HOST DIR   # ssh: extract, sbatch array
#   ./qg47_campaign.sh collect HOST DIR     # scp parts back to ./QG47_PARTS
#   python3 research/extensions/orion-qg/qg47_n2_full_sweep.py --merge   # Mac
set -euo pipefail

HERE_MAC="$(cd "$(dirname "$0")/../../" && pwd)"   # repo root (worktree)
QGDIR="$HERE_MAC/research/extensions/orion-qg"
DEVDIR="$HERE_MAC/development/orion-qg-regime-geometry"
TARBALL=/tmp/qg47_campaign.tar.gz

# Module-level import closure of qg2_objective_robustness inside orion-q
# (AST-verified from the driver; the flat pack of registration 6b76fcd1
# missed this closure — qg2 imports the orion-q donor machinery and
# resolves it as HERE.parent/"orion-q", so the tarball must preserve the
# two-directory layout).
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
  mkdir -p "$tmp/qg47/ext/orion-qg" "$tmp/qg47/ext/orion-q"
  cp "$QGDIR/qg47_n2_full_sweep.py" \
     "$QGDIR/qg2_objective_robustness.py" \
     "$QGDIR/QG45_WITNESS8_ANATOMY_RESULTS.json" \
     "$QGDIR/QG46_KERNEL_ANATOMY_RESULTS.json" \
     "$tmp/qg47/ext/orion-qg/"
  for m in "${ORION_Q_CLOSURE[@]}"; do
    cp "$QGDIR/../orion-q/$m.py" "$tmp/qg47/ext/orion-q/"
  done
  # Read-only receipt inputs referenced by the donor machinery.
  cp "$QGDIR/../orion-q/MAX_R6M_EXACT_THREE_TARE2_SHARED_FACTOR_DP_RESULTS.json" \
     "$QGDIR/../orion-q/MAX_R6O_ENLARGED_TAG_DONOR_RESULTS.json" \
     "$QGDIR/../orion-q/MAX_R6P_WEIGHT2_FRAME_DONOR_CLOSURE_RESULTS.json" \
     "$QGDIR/../orion-q/MAX_R6Q_REGIME_PREDICATE_RESULTS.json" \
     "$tmp/qg47/ext/orion-q/"
  cat > "$tmp/qg47/array_task.sh" <<'EOS'
#!/bin/bash
#SBATCH --job-name=qg47
#SBATCH --array=0-1349
#SBATCH --time=02:00:00
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=1
#SBATCH --output=logs/task_%a.out
#SBATCH --error=logs/task_%a.err
set -euo pipefail
TOP="$(cd "$(dirname "$0")" && pwd)"
mkdir -p "$TOP/parts" "$TOP/logs"
python3 "$TOP/ext/orion-qg/qg47_n2_full_sweep.py" --chunk "$SLURM_ARRAY_TASK_ID" --parts-dir "$TOP/parts"
EOS
  chmod +x "$tmp/qg47/array_task.sh"
  tar -C "$tmp" -czf "$TARBALL" qg47
  rm -rf "$tmp"
  echo "packed: $TARBALL ($(du -h "$TARBALL" | cut -f1))"
  echo "ship:   scp $TARBALL <host>:"
  echo "run:    ssh <host> 'mkdir -p qg47run && tar -C qg47run -xzf qg47_campaign.tar.gz && cd qg47run/qg47 && sbatch array_task.sh'"
}

launch_remote() {
  local host="$1" dir="$2"
  ssh "$host" "set -e; mkdir -p '$dir' && tar -C '$dir' -xzf - && cd '$dir/qg47' && mkdir -p parts logs && sbatch array_task.sh" < "$TARBALL"
}

launch_laptop() {
  # Bounded rolling queue on laptop billy (sanctioned heavy host).
  local dir="$1" par="${2:-6}"
  ssh billy-laptop "set -e; mkdir -p '$dir' && tar -C '$dir' -xzf - && cd '$dir/qg47' && mkdir -p parts logs && \
    seq 0 1349 | xargs -P '$par' -I{} sh -c 'python3 ext/orion-qg/qg47_n2_full_sweep.py --chunk {} --parts-dir parts >> logs/task_{}.out 2>&1' && \
    echo ALL_CHUNKS_DONE"
}

collect() {
  local host="$1" dir="$2"
  mkdir -p "$QGDIR/QG47_PARTS"
  ssh "$host" "cd '$dir/qg47' && tar -czf - parts" | tar -C "$QGDIR" -xz
  echo "collected parts: $(ls "$QGDIR/QG47_PARTS/parts" | wc -l | tr -d ' ')"
  echo "next: python3 research/extensions/orion-qg/qg47_n2_full_sweep.py --merge"
}

case "${1:-}" in
  pack) pack ;;
  launch-remote) launch_remote "${2:?host}" "${3:?dir}" ;;
  launch-laptop) launch_laptop "${2:?dir}" "${3:-6}" ;;
  collect) collect "${2:?host}" "${3:?dir}" ;;
  *) echo "usage: $0 pack | launch-remote HOST DIR | launch-laptop DIR [PAR] | collect HOST DIR" >&2; exit 2 ;;
esac

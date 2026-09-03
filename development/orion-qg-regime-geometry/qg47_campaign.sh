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

pack() {
  tmp=$(mktemp -d)
  mkdir -p "$tmp/qg47"
  cp "$QGDIR/qg47_n2_full_sweep.py" \
     "$QGDIR/qg2_objective_robustness.py" \
     "$QGDIR/QG45_WITNESS8_ANATOMY_RESULTS.json" \
     "$QGDIR/QG46_KERNEL_ANATOMY_RESULTS.json" \
     "$tmp/qg47/"
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
cd "$(dirname "$0")"
mkdir -p parts logs
python3 qg47_n2_full_sweep.py --chunk "$SLURM_ARRAY_TASK_ID" --parts-dir parts
EOS
  chmod +x "$tmp/qg47/array_task.sh"
  # Self-contained python path: the driver inserts its own dir into sys.path.
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
    seq 0 1349 | xargs -P '$par' -I{} sh -c 'python3 qg47_n2_full_sweep.py --chunk {} --parts-dir parts >> logs/task_{}.out 2>&1' && \
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

#!/usr/bin/env bash
#SBATCH --job-name=p1-sab-synth-v1
#SBATCH --account=lu2026-2-51
#SBATCH --partition=lu48
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=2
#SBATCH --mem=8G
#SBATCH --time=00:20:00

set -euo pipefail
umask 077

: "${ORION_SAB_REMOTE_ROOT:=/projects/hep/fs10/scratch/scyiu/orion_scienceagentbench_v1}"
: "${SLURM_JOB_ID:?must run under Slurm}"

: "${TMPDIR:?LUNARC node-local TMPDIR is required}"
JOB_ROOT="${TMPDIR}/orion-sab-runtime-v1"
AUDIT_JOB_ROOT="${ORION_SAB_REMOTE_ROOT}/synthetic-smoke-v1/${SLURM_JOB_ID}"
PACKET_ROOT="${ORION_SAB_REMOTE_ROOT}/packet-v1"
SCRIPT_ROOT="${ORION_SAB_REMOTE_ROOT}/scripts-v1"
TOOLCHAIN_ROOT="${ORION_SAB_REMOTE_ROOT}/podman-toolchain-v1"
mkdir -p "${JOB_ROOT}" "${AUDIT_JOB_ROOT}" "${PACKET_ROOT}"
chmod 700 "${JOB_ROOT}" "${AUDIT_JOB_ROOT}" "${PACKET_ROOT}"

export PATH="${TOOLCHAIN_ROOT}/bin:${PATH}"
export HOME="${JOB_ROOT}/home"
export XDG_RUNTIME_DIR="/tmp/orion-sab-${SLURM_JOB_ID}"
export XDG_CONFIG_HOME="${HOME}/.config"
export CONTAINERS_STORAGE_CONF="${JOB_ROOT}/storage.conf"
export DOCKER_HOST="unix://${XDG_RUNTIME_DIR}/podman/podman.sock"
mkdir -p "${HOME}" "${XDG_RUNTIME_DIR}/podman" "${XDG_CONFIG_HOME}/containers"
chmod 700 "${XDG_RUNTIME_DIR}" "${XDG_RUNTIME_DIR}/podman" "${XDG_CONFIG_HOME}"

cat >"${CONTAINERS_STORAGE_CONF}" <<EOF
[storage]
driver = "overlay"
runroot = "${JOB_ROOT}/containers-runroot"
graphroot = "${JOB_ROOT}/containers-graphroot"

[storage.options.overlay]
mount_program = "${TOOLCHAIN_ROOT}/bin/fuse-overlayfs"
ignore_chown_errors = "true"
EOF

cat >"${XDG_CONFIG_HOME}/containers/containers.conf" <<EOF
[engine]
cgroup_manager = "cgroupfs"
events_logger = "file"
runtime = "${TOOLCHAIN_ROOT}/bin/crun"
conmon_path = ["${TOOLCHAIN_ROOT}/bin/conmon"]
helper_binaries_dir = ["${TOOLCHAIN_ROOT}/bin", "${TOOLCHAIN_ROOT}/libexec/podman"]
EOF

cat >"${XDG_CONFIG_HOME}/containers/policy.json" <<'EOF'
{
  "default": [{"type": "reject"}],
  "transports": {
    "docker": {
      "docker.io": [{"type": "insecureAcceptAnything"}]
    }
  }
}
EOF

SERVICE_LOG="${AUDIT_JOB_ROOT}/podman-service.log"
podman system service --time=0 "${DOCKER_HOST}" >"${SERVICE_LOG}" 2>&1 &
SERVICE_PID=$!
cleanup() {
  kill "${SERVICE_PID}" 2>/dev/null || true
  wait "${SERVICE_PID}" 2>/dev/null || true
  rm -rf -- "${XDG_RUNTIME_DIR}"
}
trap cleanup EXIT

for _ in $(seq 1 80); do
  [[ -S "${XDG_RUNTIME_DIR}/podman/podman.sock" ]] && break
  sleep 0.25
done
[[ -S "${XDG_RUNTIME_DIR}/podman/podman.sock" ]]

python3 -m venv "${JOB_ROOT}/venv"
"${JOB_ROOT}/venv/bin/python" -m pip install --disable-pip-version-check --no-input 'docker==7.1.0'
"${JOB_ROOT}/venv/bin/python" "${SCRIPT_ROOT}/synthetic_docker_sdk_smoke_v1.py" \
  --receipt "${PACKET_ROOT}/SLURM_SYNTHETIC_RECEIPT_V1.json"

sha256sum \
  "${PACKET_ROOT}/SLURM_SYNTHETIC_RECEIPT_V1.json" \
  "${SCRIPT_ROOT}/docker_sdk_owner_normalization_v1.py" \
  "${SCRIPT_ROOT}/synthetic_docker_sdk_smoke_v1.py" \
  "${SCRIPT_ROOT}/run_lunarc_synthetic_smoke_v1.sh" \
  >"${PACKET_ROOT}/REMOTE_SHA256SUMS"

printf '%s\n' 'P1_SAB_LUNARC_SYNTHETIC_RUNTIME_JOB_COMPLETE__ZERO_TASKS_RUN__ZERO_OUTCOMES_OPENED'

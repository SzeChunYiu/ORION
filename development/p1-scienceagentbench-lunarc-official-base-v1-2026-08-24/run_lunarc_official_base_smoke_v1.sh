#!/usr/bin/env bash
#SBATCH --job-name=p1-sab-base-v1
#SBATCH --account=lu2026-2-51
#SBATCH --partition=lu48
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=4
#SBATCH --mem=32G
#SBATCH --time=02:00:00

set -euo pipefail
umask 077

: "${ORION_SAB_REMOTE_ROOT:=/projects/hep/fs10/scratch/scyiu/orion_scienceagentbench_v1}"
: "${SLURM_JOB_ID:?must run under Slurm}"
: "${TMPDIR:?LUNARC node-local TMPDIR is required}"

JOB_ROOT="${TMPDIR}/orion-sab-official-base-v1"
AUDIT_JOB_ROOT="${ORION_SAB_REMOTE_ROOT}/official-base-smoke-v1/${SLURM_JOB_ID}"
PACKET_ROOT="${ORION_SAB_REMOTE_ROOT}/packet-official-base-v1"
SCRIPT_ROOT="${ORION_SAB_REMOTE_ROOT}/scripts-official-base-v1"
TOOLCHAIN_ROOT="${ORION_SAB_REMOTE_ROOT}/podman-toolchain-v1"
mkdir -p "${JOB_ROOT}" "${AUDIT_JOB_ROOT}" "${PACKET_ROOT}"
chmod 700 "${JOB_ROOT}" "${AUDIT_JOB_ROOT}" "${PACKET_ROOT}"

sha256sum -c "${SCRIPT_ROOT}/REMOTE_INPUT_SHA256SUMS"
sha256sum -c "${TOOLCHAIN_ROOT}/SHA256SUMS"

SINGLEMAP_SHIM="${JOB_ROOT}/orion-singlemap-v1.so"
OWNER_COMMAND="${JOB_ROOT}/singlemap_owner_command_v1.pl"
ADDUSER_COMMAND="${JOB_ROOT}/singlemap_adduser_v1.sh"
gcc -shared -fPIC -O2 -Wall -Wextra \
  -o "${SINGLEMAP_SHIM}" \
  "${SCRIPT_ROOT}/singlemap_identity_normalization_v1.c" -ldl
chmod 700 "${SINGLEMAP_SHIM}"
cp "${SCRIPT_ROOT}/singlemap_owner_command_v1.pl" "${OWNER_COMMAND}"
chmod 700 "${OWNER_COMMAND}"
cp "${SCRIPT_ROOT}/singlemap_adduser_v1.sh" "${ADDUSER_COMMAND}"
chmod 700 "${ADDUSER_COMMAND}"

unset OPENAI_API_KEY AZURE_OPENAI_KEY AZURE_OPENAI_ENDPOINT \
  AZURE_OPENAI_API_VERSION AZURE_OPENAI_DEPLOYMENT_NAME || true

export PATH="${TOOLCHAIN_ROOT}/bin:${PATH}"
export HOME="${JOB_ROOT}/home"
export XDG_RUNTIME_DIR="/tmp/orion-sab-base-${SLURM_JOB_ID}"
export XDG_CONFIG_HOME="${HOME}/.config"
export CONTAINERS_STORAGE_CONF="${JOB_ROOT}/storage.conf"
export DOCKER_HOST="unix://${XDG_RUNTIME_DIR}/podman/podman.sock"
export ORION_SAB_NODE_LOCAL_JOB_ROOT="${JOB_ROOT}"
export ORION_SAB_NODE_LOCAL_GRAPHROOT="${JOB_ROOT}/containers-graphroot"
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

[containers]
env = ["LD_PRELOAD=/usr/local/lib/orion-singlemap-v1.so"]
volumes = [
  "${SCRIPT_ROOT}/apt_rootless_sandbox_v1.conf:/etc/apt/apt.conf.d/99-orion-rootless-sandbox:ro",
  "${SINGLEMAP_SHIM}:/usr/local/lib/orion-singlemap-v1.so:ro",
  "${OWNER_COMMAND}:/usr/bin/chown:ro",
  "${OWNER_COMMAND}:/usr/bin/chgrp:ro",
  "${ADDUSER_COMMAND}:/usr/local/sbin/adduser:ro"
]
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
cleanup_emergency() {
  if [[ -n "${SERVICE_PID:-}" ]]; then
    kill "${SERVICE_PID}" 2>/dev/null || true
    wait "${SERVICE_PID}" 2>/dev/null || true
  fi
  rm -rf -- "${XDG_RUNTIME_DIR}" "${JOB_ROOT}"
}
trap cleanup_emergency EXIT

for _ in $(seq 1 80); do
  [[ -S "${XDG_RUNTIME_DIR}/podman/podman.sock" ]] && break
  sleep 0.25
done
[[ -S "${XDG_RUNTIME_DIR}/podman/podman.sock" ]]

python3 -m venv "${JOB_ROOT}/venv"
"${JOB_ROOT}/venv/bin/python" -m pip install \
  --disable-pip-version-check --no-input 'docker==7.1.0'

RECEIPT="${PACKET_ROOT}/SLURM_OFFICIAL_BASE_RECEIPT_V1.json"
DRIVER_RC=0
"${JOB_ROOT}/venv/bin/python" \
  "${SCRIPT_ROOT}/official_base_docker_sdk_smoke_v1.py" \
  --dockerfile "${SCRIPT_ROOT}/OFFICIAL_BASE_DOCKERFILE_V1" \
  --source-receipt "${SCRIPT_ROOT}/SOURCE_BINDING_V1.json" \
  --apt-runtime-config "${SCRIPT_ROOT}/apt_rootless_sandbox_v1.conf" \
  --owner-normalization "${SCRIPT_ROOT}/docker_sdk_owner_normalization_v1.py" \
  --singlemap-shim-source "${SCRIPT_ROOT}/singlemap_identity_normalization_v1.c" \
  --singlemap-shim-binary "${SINGLEMAP_SHIM}" \
  --singlemap-owner-command "${SCRIPT_ROOT}/singlemap_owner_command_v1.pl" \
  --singlemap-adduser "${SCRIPT_ROOT}/singlemap_adduser_v1.sh" \
  --receipt "${RECEIPT}" || DRIVER_RC=$?

kill "${SERVICE_PID}" 2>/dev/null || true
wait "${SERVICE_PID}" 2>/dev/null || true
SERVICE_PID=""
rm -rf -- "${XDG_RUNTIME_DIR}" "${JOB_ROOT}"

JOB_ROOT_REMOVED=false
SOCKET_ROOT_REMOVED=false
[[ ! -e "${JOB_ROOT}" ]] && JOB_ROOT_REMOVED=true
[[ ! -e "${XDG_RUNTIME_DIR}" ]] && SOCKET_ROOT_REMOVED=true

FINAL_RC=0
python3 - "${RECEIPT}" "${DRIVER_RC}" "${JOB_ROOT_REMOVED}" \
  "${SOCKET_ROOT_REMOVED}" <<'PY' || FINAL_RC=$?
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

path = Path(sys.argv[1])
driver_rc = int(sys.argv[2])
job_root_removed = sys.argv[3] == "true"
socket_root_removed = sys.argv[4] == "true"
data = json.loads(path.read_text(encoding="utf-8"))
data["cleanup"]["node_local_job_root_removal_pending"] = False
data["cleanup"]["node_local_job_root_removed"] = job_root_removed
data["cleanup"]["runtime_socket_root_removed"] = socket_root_removed
data["cleanup"]["finalized_at_utc"] = datetime.now(timezone.utc).isoformat()
passed = (
    driver_rc == 0
    and data["status"] == "PASS"
    and job_root_removed
    and socket_root_removed
)
data["status"] = "PASS" if passed else "FAIL"
data["terminal"] = (
    "P1_SAB_LUNARC_OFFICIAL_PUBLIC_BASE_SMOKE_PASS__EXACT_PINNED_DOCKERFILE_BOUND__IMAGE_AND_NODE_LOCAL_LAYERS_REMOVED__ZERO_TASKS_RUN__ZERO_OUTCOMES_OPENED"
    if passed
    else "P1_SAB_LUNARC_OFFICIAL_PUBLIC_BASE_SMOKE_FAIL__ZERO_TASKS_RUN__ZERO_OUTCOMES_OPENED"
)
if not passed and data["error"] is None:
    data["error"] = {
        "type": "BatchCleanupFinalizationError",
        "message": (
            f"driver_rc={driver_rc} job_root_removed={job_root_removed} "
            f"socket_root_removed={socket_root_removed}"
        ),
    }
path.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n", encoding="utf-8")
print(data["terminal"])
raise SystemExit(0 if passed else 1)
PY

cp "${RECEIPT}" "${AUDIT_JOB_ROOT}/SLURM_OFFICIAL_BASE_RECEIPT_V1.json"

sha256sum \
  "${RECEIPT}" \
  "${SCRIPT_ROOT}/SOURCE_BINDING_V1.json" \
  "${SCRIPT_ROOT}/OFFICIAL_BASE_DOCKERFILE_V1" \
  "${SCRIPT_ROOT}/apt_rootless_sandbox_v1.conf" \
  "${SCRIPT_ROOT}/singlemap_identity_normalization_v1.c" \
  "${SCRIPT_ROOT}/singlemap_owner_command_v1.pl" \
  "${SCRIPT_ROOT}/singlemap_adduser_v1.sh" \
  "${SCRIPT_ROOT}/docker_sdk_owner_normalization_v1.py" \
  "${SCRIPT_ROOT}/official_base_docker_sdk_smoke_v1.py" \
  "${SCRIPT_ROOT}/run_lunarc_official_base_smoke_v1.sh" \
  "${SCRIPT_ROOT}/REMOTE_INPUT_SHA256SUMS" \
  >"${PACKET_ROOT}/REMOTE_SHA256SUMS"

trap - EXIT
printf '%s\n' 'P1_SAB_LUNARC_OFFICIAL_PUBLIC_BASE_JOB_COMPLETE__ZERO_TASKS_RUN__ZERO_OUTCOMES_OPENED'
exit "${FINAL_RC}"

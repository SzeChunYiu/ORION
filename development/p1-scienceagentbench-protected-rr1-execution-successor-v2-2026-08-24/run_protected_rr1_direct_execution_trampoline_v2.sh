#!/usr/bin/bash
#SBATCH --job-name=p1_sab_rr1_preflight_v1
#SBATCH --account=lu2026-2-51
#SBATCH --partition=gpua40i
#SBATCH --gres=gpu:a40:1
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=8
#SBATCH --mem=64G
#SBATCH --time=01:00:00
#SBATCH --signal=B:TERM@120

# Slurm may spool this submitted file. Runtime resolution therefore binds the
# spooled bytes to the canonical successor source, but executes the unchanged
# original launcher at its independently frozen absolute donor path.
set -Eeuo pipefail
umask 077

SUCCESSOR_ROOT='/projects/hep/fs10/scratch/scyiu/orion_p1_sab_protected_rr1_direct_route_v1_20260824/repo-exec-successor-v2-20260824'
TRAMPOLINE_REL='development/p1-scienceagentbench-protected-rr1-execution-successor-v2-2026-08-24/run_protected_rr1_direct_execution_trampoline_v2.sh'
ORIGINAL_ROOT='/projects/hep/fs10/scratch/scyiu/orion_p1_sab_protected_rr1_direct_route_v1_20260824/repo-51f13ba9/development/p1-scienceagentbench-protected-rr1-direct-route-freeze-v1-2026-08-24'
ORIGINAL_LAUNCHER="$ORIGINAL_ROOT/run_protected_rr1_direct_route_v1.sh"
ORIGINAL_MODULE="$ORIGINAL_ROOT/protected_rr1_direct_route_v1.py"
ORIGINAL_CONTRACT="$ORIGINAL_ROOT/PROTECTED_RR1_DIRECT_ROUTE_CONTRACT_V1.json"
ORIGINAL_LAUNCHER_SHA256='a540954aaa4ce638190162f39268bf660d7baac7d4e8841d4f56ba5441300219'
ORIGINAL_MODULE_SHA256='7ff4868a744af526384e199dab659a76a67f83ab51ee813ce65f53026b220a91'
ORIGINAL_CONTRACT_SHA256='a091bf0617d657ee7f8c2bcab08acda96d16246407d791d6a90704efffedc398'
BASH_PATH='/usr/bin/bash'
BASH_SHA256='ec6d007d48ef11bc47ad3f372b4b20ff2f0d4e63867e7e4cc0f1b17b19fa88b2'
SHA256SUM_PATH='/usr/bin/sha256sum'
SHA256SUM_SHA256='1950eda10a1bb0c6c2a086ba009b847edec6f30d25eb311b9154ae08819041a9'
READLINK_PATH='/usr/bin/readlink'
CMP_PATH='/usr/bin/cmp'
PYTHON_PATH_ENTRY='/sw/easybuild_milan/software/Python/3.11.5-GCCcore-13.2.0/bin'
PYTHON_COMMAND='/sw/easybuild_milan/software/Python/3.11.5-GCCcore-13.2.0/bin/python3'
PYTHON_REAL_TARGET='/lunarc/sw/easybuild_milan/software/Python/3.11.5-GCCcore-13.2.0/bin/python3.11'
PYTHON_REAL_TARGET_SHA256='34f2f9f9561850d15d8060a2565c3a81046425faaba575687d3b75e1212d0f77'
RUNTIME_PATH='/sw/easybuild_milan/software/Python/3.11.5-GCCcore-13.2.0/bin:/usr/bin:/bin'

hash_file() {
  local path=$1
  local output digest
  output=$("$SHA256SUM_PATH" -- "$path" 2>/dev/null) || return 1
  digest=${output%% *}
  [[ "$digest" =~ ^[0-9a-f]{64}$ ]] || return 1
  printf '%s' "$digest"
}

fail_body_free() {
  local code=$1
  local detail=$2
  local output digest
  output=$(printf '%s' "$detail" | "$SHA256SUM_PATH" 2>/dev/null) \
    || output='SHA256_UNAVAILABLE'
  digest=${output%% *}
  [[ "$digest" =~ ^[0-9a-f]{64}$ ]] || digest='SHA256_UNAVAILABLE'
  printf '%s\n' \
    "P1_SAB_PROTECTED_RR1_DIRECT_EXECUTION_TRAMPOLINE_V2_CANNOT_CHECK failure_code=${code} detail_sha256=${digest}" \
    >&2
  exit 2
}

[[ "$BASH" == "$BASH_PATH" ]] \
  || fail_body_free 'TOOLCHAIN_DRIFT' 'running Bash path differs from the exact freeze'
[[ -f "$SHA256SUM_PATH" && ! -L "$SHA256SUM_PATH" ]] \
  || fail_body_free 'TOOLCHAIN_DRIFT' 'sha256sum is absent, nonregular, or symlinked'
ACTUAL_SHA256SUM_SHA256=$(hash_file "$SHA256SUM_PATH") \
  || fail_body_free 'TOOLCHAIN_DRIFT' 'sha256sum cannot hash its frozen path'
[[ "$ACTUAL_SHA256SUM_SHA256" == "$SHA256SUM_SHA256" ]] \
  || fail_body_free 'TOOLCHAIN_DRIFT' 'sha256sum hash differs from the exact freeze'
[[ -f "$BASH_PATH" && ! -L "$BASH_PATH" ]] \
  || fail_body_free 'TOOLCHAIN_DRIFT' 'Bash is absent, nonregular, or symlinked'
ACTUAL_BASH_SHA256=$(hash_file "$BASH_PATH") \
  || fail_body_free 'TOOLCHAIN_DRIFT' 'Bash cannot be hashed'
[[ "$ACTUAL_BASH_SHA256" == "$BASH_SHA256" ]] \
  || fail_body_free 'TOOLCHAIN_DRIFT' 'Bash hash differs from the exact freeze'
[[ -x "$READLINK_PATH" && ! -L "$READLINK_PATH" ]] \
  || fail_body_free 'TOOLCHAIN_DRIFT' 'absolute readlink utility is unavailable'
[[ -x "$CMP_PATH" && ! -L "$CMP_PATH" ]] \
  || fail_body_free 'TOOLCHAIN_DRIFT' 'absolute cmp utility is unavailable'

export PATH="$RUNTIME_PATH"
[[ "$(command -v python3)" == "$PYTHON_COMMAND" ]] \
  || fail_body_free 'TOOLCHAIN_DRIFT' 'python3 command path differs from the exact freeze'
[[ -e "$PYTHON_COMMAND" && ! -d "$PYTHON_COMMAND" ]] \
  || fail_body_free 'TOOLCHAIN_DRIFT' 'python3 command path is unavailable'
PYTHON_COMMAND_RESOLVED=$("$READLINK_PATH" -f -- "$PYTHON_COMMAND" 2>/dev/null) \
  || fail_body_free 'TOOLCHAIN_DRIFT' 'python3 command path cannot be canonicalized'
[[ "$PYTHON_COMMAND_RESOLVED" == "$PYTHON_REAL_TARGET" ]] \
  || fail_body_free 'TOOLCHAIN_DRIFT' 'python3 real target differs from the exact freeze'
[[ -f "$PYTHON_REAL_TARGET" && ! -L "$PYTHON_REAL_TARGET" ]] \
  || fail_body_free 'TOOLCHAIN_DRIFT' 'python3 real target is absent, nonregular, or symlinked'
ACTUAL_PYTHON_SHA256=$(hash_file "$PYTHON_REAL_TARGET") \
  || fail_body_free 'TOOLCHAIN_DRIFT' 'python3 real target cannot be hashed'
[[ "$ACTUAL_PYTHON_SHA256" == "$PYTHON_REAL_TARGET_SHA256" ]] \
  || fail_body_free 'TOOLCHAIN_DRIFT' 'python3 real target hash differs from the exact freeze'

[[ "${SLURM_SUBMIT_DIR-}" == "$SUCCESSOR_ROOT" ]] \
  || fail_body_free 'SUBMIT_ROOT_INVALID' 'SLURM_SUBMIT_DIR differs from the exact successor snapshot root'
[[ "${PWD-}" == "$SUCCESSOR_ROOT" ]] \
  || fail_body_free 'SUBMIT_CWD_INVALID' 'PWD differs from the exact successor snapshot root'
CANONICAL_SUBMIT_DIR=$(CDPATH= cd -- "$SLURM_SUBMIT_DIR" 2>/dev/null && pwd -P) \
  || fail_body_free 'SUBMIT_ROOT_INVALID' 'SLURM_SUBMIT_DIR cannot be opened'
[[ "$CANONICAL_SUBMIT_DIR" == "$SUCCESSOR_ROOT" ]] \
  || fail_body_free 'SUBMIT_ROOT_INVALID' 'SLURM_SUBMIT_DIR contains a symlink, alias, case, or path drift'
CURRENT_CWD=$(pwd -P) \
  || fail_body_free 'SUBMIT_CWD_INVALID' 'runtime cwd cannot be canonicalized'
[[ "$CURRENT_CWD" == "$SUCCESSOR_ROOT" ]] \
  || fail_body_free 'SUBMIT_CWD_INVALID' 'runtime cwd contains a symlink, alias, case, or path drift'

CANONICAL_TRAMPOLINE="$SUCCESSOR_ROOT/$TRAMPOLINE_REL"
[[ -f "$CANONICAL_TRAMPOLINE" && ! -L "$CANONICAL_TRAMPOLINE" ]] \
  || fail_body_free 'SOURCE_DRIFT' 'canonical trampoline is absent, nonregular, or symlinked'
CANONICAL_TRAMPOLINE_RESOLVED=$("$READLINK_PATH" -f -- "$CANONICAL_TRAMPOLINE" 2>/dev/null) \
  || fail_body_free 'SOURCE_DRIFT' 'canonical trampoline cannot be canonicalized'
[[ "$CANONICAL_TRAMPOLINE_RESOLVED" == "$CANONICAL_TRAMPOLINE" ]] \
  || fail_body_free 'SOURCE_DRIFT' 'canonical trampoline path contains an alias or symlink'
case $0 in
  /*) ;;
  *) fail_body_free 'SOURCE_DRIFT' 'spooled script path is not absolute' ;;
esac
[[ -f "$0" && ! -L "$0" ]] \
  || fail_body_free 'SOURCE_DRIFT' 'spooled script is absent, nonregular, or symlinked'
CANONICAL_TRAMPOLINE_SHA256=$(hash_file "$CANONICAL_TRAMPOLINE") \
  || fail_body_free 'SOURCE_DRIFT' 'canonical trampoline cannot be hashed'
SPOOLED_TRAMPOLINE_SHA256=$(hash_file "$0") \
  || fail_body_free 'SOURCE_DRIFT' 'spooled script cannot be hashed'
[[ "$SPOOLED_TRAMPOLINE_SHA256" == "$CANONICAL_TRAMPOLINE_SHA256" ]] \
  || fail_body_free 'SOURCE_DRIFT' 'spooled and canonical trampoline hashes differ'
"$CMP_PATH" -s -- "$0" "$CANONICAL_TRAMPOLINE" \
  || fail_body_free 'SOURCE_DRIFT' 'spooled and canonical trampoline bytes differ'

verify_bound_file() {
  local path=$1
  local expected_sha256=$2
  local label=$3
  local resolved actual
  [[ -f "$path" && ! -L "$path" ]] \
    || fail_body_free 'DONOR_DRIFT' "$label is absent, nonregular, or symlinked"
  resolved=$("$READLINK_PATH" -f -- "$path" 2>/dev/null) \
    || fail_body_free 'DONOR_DRIFT' "$label cannot be canonicalized"
  [[ "$resolved" == "$path" ]] \
    || fail_body_free 'DONOR_DRIFT' "$label path contains an alias or symlink"
  actual=$(hash_file "$path") \
    || fail_body_free 'DONOR_DRIFT' "$label cannot be hashed"
  [[ "$actual" == "$expected_sha256" ]] \
    || fail_body_free 'DONOR_DRIFT' "$label hash differs from the freeze"
}

verify_bound_file "$ORIGINAL_LAUNCHER" "$ORIGINAL_LAUNCHER_SHA256" 'original launcher'
verify_bound_file "$ORIGINAL_MODULE" "$ORIGINAL_MODULE_SHA256" 'original module'
verify_bound_file "$ORIGINAL_CONTRACT" "$ORIGINAL_CONTRACT_SHA256" 'original contract'

EXPECTED_ARGV=(
  '--masked-packet'
  '/projects/hep/fs10/scratch/scyiu/orion_p1_sab_protected_rr1_direct_route_v1_20260824/private-inputs/MASKED_PACKET.json'
  '--recovered-packet'
  '/projects/hep/fs10/scratch/scyiu/orion_p1_sab_protected_rr1_direct_route_v1_20260824/private-inputs/RECOVERED_PACKET.json'
  '--model'
  '/projects/hep/fs10/scratch/scyiu/orion_p1_sab_exact_model_v1_20260824/model/Qwen3-Coder-30B-A3B-Instruct-Q4_K_M.gguf'
  '--llama-server'
  '/sw/pkg/ollama/0.32.14/lib/ollama/llama-server'
  '--cuda-backend'
  '/sw/pkg/ollama/0.32.14/lib/ollama/cuda_v13/libggml-cuda.so'
  '--output-root'
  '/projects/hep/fs10/scratch/scyiu/orion_p1_sab_protected_rr1_direct_route_v1_20260824/live-rr1-exec-successor-v2-20260824/runtime-parent/evidence'
)
[[ $# -eq ${#EXPECTED_ARGV[@]} ]] \
  || fail_body_free 'ARGV_INVALID' 'direct execution argv count differs from the exact freeze'
ACTUAL_ARGV=("$@")
for index in "${!EXPECTED_ARGV[@]}"; do
  [[ "${ACTUAL_ARGV[$index]}" == "${EXPECTED_ARGV[$index]}" ]] \
    || fail_body_free 'ARGV_INVALID' 'direct execution argv order or value differs from the exact freeze'
done

exec /usr/bin/bash "$ORIGINAL_LAUNCHER" "$@"

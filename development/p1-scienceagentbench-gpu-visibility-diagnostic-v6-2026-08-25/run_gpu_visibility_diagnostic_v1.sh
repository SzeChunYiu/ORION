#!/usr/bin/bash
#SBATCH --job-name=p1_sab_gpu_visibility_v1
#SBATCH --account=lu2026-2-51
#SBATCH --partition=gpua40i
#SBATCH --exclude=cg14
#SBATCH --gres=gpu:a40:1
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=1
#SBATCH --mem=4G
#SBATCH --time=00:10:00
#SBATCH --signal=B:TERM@120

# Slurm may execute a spooled copy. Bind that copy to the canonical frozen
# source, create one new private run parent, and exec only the body-free GPU
# visibility diagnostic with an exact argv. No server, model, network, or task
# surface is an input to this trampoline.
set -Eeuo pipefail
umask 077

SUCCESSOR_ROOT='/projects/hep/fs10/scratch/scyiu/orion_p1_sab_protected_rr1_direct_route_v1_20260824/repo-gpu-visibility-v6-20260825'
TRAMPOLINE_REL='development/p1-scienceagentbench-gpu-visibility-diagnostic-v6-2026-08-25/run_gpu_visibility_diagnostic_v1.sh'
MODULE_REL='development/p1-scienceagentbench-gpu-visibility-diagnostic-v6-2026-08-25/gpu_visibility_diagnostic_v1.py'
CONTRACT_REL='development/p1-scienceagentbench-gpu-visibility-diagnostic-v6-2026-08-25/GPU_VISIBILITY_DIAGNOSTIC_CONTRACT_V1.json'
RUN_ROOT='/projects/hep/fs10/scratch/scyiu/orion_p1_sab_protected_rr1_direct_route_v1_20260824/live-gpu-visibility-v6-20260825'
MODULE_SHA256='948d3165c11db898a352f8d85d51a4c99bc86e08d5608ef923c1bb0844596d07'
CONTRACT_SHA256='8197315f8dbbd3ed52836e5e34c60f39dbcea341f40c9abe5280d8227e98a704'
NORMALIZED_TRAMPOLINE_SHA256='87691b1bdfc198a074104675b0bd57fc92349a3a05caca74bb16f98156f44aea'

BASH_PATH='/usr/bin/bash'
BASH_SHA256='ec6d007d48ef11bc47ad3f372b4b20ff2f0d4e63867e7e4cc0f1b17b19fa88b2'
SHA256SUM_PATH='/usr/bin/sha256sum'
SHA256SUM_SHA256='1950eda10a1bb0c6c2a086ba009b847edec6f30d25eb311b9154ae08819041a9'
READLINK_PATH='/usr/bin/readlink'
READLINK_SHA256='99dbafcdcba4adb285ea164c3a3bf27539719328a8ae5df9be6d84cdde1146dc'
CMP_PATH='/usr/bin/cmp'
CMP_SHA256='16d8b82bf5ee1774585ce5c63691cb156aa350c48f0d0689b27d13aa4b0a62eb'
STAT_PATH='/usr/bin/stat'
STAT_SHA256='f7ef3b1376596ce952779ea53a91ec97ce8b57389a3ffde75a499564b1c8f25f'
PYTHON_COMMAND='/sw/easybuild_milan/software/Python/3.11.5-GCCcore-13.2.0/bin/python3'
PYTHON_REAL_TARGET='/lunarc/sw/easybuild_milan/software/Python/3.11.5-GCCcore-13.2.0/bin/python3.11'
PYTHON_REAL_TARGET_SHA256='34f2f9f9561850d15d8060a2565c3a81046425faaba575687d3b75e1212d0f77'
RUNTIME_PATH='/sw/easybuild_milan/software/Python/3.11.5-GCCcore-13.2.0/bin:/usr/bin:/bin'
PYTHON_LIBRARY_LOGICAL_DIR='/sw/easybuild_milan/software/Python/3.11.5-GCCcore-13.2.0/lib'
PYTHON_LIBRARY_CANONICAL_DIR='/lunarc/sw/easybuild_milan/software/Python/3.11.5-GCCcore-13.2.0/lib'
LIBPYTHON_LOGICAL_PATH="$PYTHON_LIBRARY_LOGICAL_DIR/libpython3.11.so.1.0"
LIBPYTHON_CANONICAL_PATH="$PYTHON_LIBRARY_CANONICAL_DIR/libpython3.11.so.1.0"
LIBPYTHON_SHA256='398cbf957b8584d4e06ce374b888555149d517ea1037f7ca44d62f855a5b83c5'
LIBPYTHON_SIZE='22160208'
LIBPYTHON_MODE='755'
LIBPYTHON_UID='1400'
LIBPYTHON_GID='1400'
LIBPYTHON_NLINK='1'
RUN_ROOT_MODE='700'
RUN_ROOT_UID='6350'
RUN_ROOT_GID='6300'
RUN_ROOT_NLINK='2'

hash_file() {
  local path=$1
  local output digest
  output=$("$SHA256SUM_PATH" -- "$path" 2>/dev/null) || return 1
  digest=${output%% *}
  [[ "$digest" =~ ^[0-9a-f]{64}$ ]] || return 1
  printf '%s' "$digest"
}

hash_normalized_trampoline() {
  local path=$1
  local line prefix digest normalized output matches
  prefix="NORMALIZED_TRAMPOLINE_SHA256='"
  normalized=''
  matches=0
  while IFS= read -r line; do
    if [[ "${line:0:${#prefix}}" == "$prefix" && "${line: -1}" == "'" ]]; then
      digest=${line#"$prefix"}
      digest=${digest%\'}
      [[ "$digest" =~ ^[0-9a-f]{64}$ ]] || return 1
      line="${prefix}0000000000000000000000000000000000000000000000000000000000000000'"
      matches=$((matches + 1))
    fi
    normalized="${normalized}${line}"$'\n'
  done < "$path"
  [[ "$matches" -eq 1 ]] || return 1
  output=$(printf '%s' "$normalized" | "$SHA256SUM_PATH" 2>/dev/null) || return 1
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
    "P1_SAB_GPU_VISIBILITY_DIAGNOSTIC_TRAMPOLINE_V1_CANNOT_CHECK failure_code=${code} detail_sha256=${digest}" \
    >&2
  exit 2
}

[[ "$#" -eq 0 ]] \
  || fail_body_free 'ARGV_INVALID' 'trampoline accepts no argv'
[[ ${LD_LIBRARY_PATH+x} != x ]] \
  || fail_body_free 'ENVIRONMENT_INVALID' 'LD_LIBRARY_PATH must be absent on trampoline entry'
[[ ${LD_PRELOAD+x} != x ]] \
  || fail_body_free 'ENVIRONMENT_INVALID' 'LD_PRELOAD must be absent on trampoline entry'
[[ "$BASH" == "$BASH_PATH" ]] \
  || fail_body_free 'TOOLCHAIN_DRIFT' 'running Bash path differs from the exact freeze'

[[ -f "$SHA256SUM_PATH" && -x "$SHA256SUM_PATH" && ! -L "$SHA256SUM_PATH" ]] \
  || fail_body_free 'TOOLCHAIN_DRIFT' 'sha256sum is unavailable at its frozen path'
ACTUAL_SHA256SUM_SHA256=$(hash_file "$SHA256SUM_PATH") \
  || fail_body_free 'TOOLCHAIN_DRIFT' 'sha256sum cannot hash its frozen path'
[[ "$ACTUAL_SHA256SUM_SHA256" == "$SHA256SUM_SHA256" ]] \
  || fail_body_free 'TOOLCHAIN_DRIFT' 'sha256sum hash differs from the exact freeze'
for tool_binding in \
  "$BASH_PATH:$BASH_SHA256:Bash" \
  "$READLINK_PATH:$READLINK_SHA256:readlink" \
  "$CMP_PATH:$CMP_SHA256:cmp" \
  "$STAT_PATH:$STAT_SHA256:stat"
do
  tool_path=${tool_binding%%:*}
  remainder=${tool_binding#*:}
  expected_tool_sha=${remainder%%:*}
  tool_label=${remainder#*:}
  [[ -f "$tool_path" && -x "$tool_path" && ! -L "$tool_path" ]] \
    || fail_body_free 'TOOLCHAIN_DRIFT' "$tool_label is unavailable at its frozen path"
  actual_tool_sha=$(hash_file "$tool_path") \
    || fail_body_free 'TOOLCHAIN_DRIFT' "$tool_label cannot be hashed"
  [[ "$actual_tool_sha" == "$expected_tool_sha" ]] \
    || fail_body_free 'TOOLCHAIN_DRIFT' "$tool_label hash differs from the exact freeze"
done

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
  || fail_body_free 'SUBMIT_ROOT_INVALID' 'SLURM_SUBMIT_DIR differs from the exact successor root'
[[ "${PWD-}" == "$SUCCESSOR_ROOT" ]] \
  || fail_body_free 'SUBMIT_CWD_INVALID' 'PWD differs from the exact successor root'
CANONICAL_SUBMIT_DIR=$(CDPATH= cd -- "$SLURM_SUBMIT_DIR" 2>/dev/null && pwd -P) \
  || fail_body_free 'SUBMIT_ROOT_INVALID' 'SLURM_SUBMIT_DIR cannot be opened'
[[ "$CANONICAL_SUBMIT_DIR" == "$SUCCESSOR_ROOT" ]] \
  || fail_body_free 'SUBMIT_ROOT_INVALID' 'SLURM_SUBMIT_DIR contains alias drift'
CURRENT_CWD=$(pwd -P) \
  || fail_body_free 'SUBMIT_CWD_INVALID' 'runtime cwd cannot be canonicalized'
[[ "$CURRENT_CWD" == "$SUCCESSOR_ROOT" ]] \
  || fail_body_free 'SUBMIT_CWD_INVALID' 'runtime cwd contains alias drift'

CANONICAL_TRAMPOLINE="$SUCCESSOR_ROOT/$TRAMPOLINE_REL"
MODULE_PATH="$SUCCESSOR_ROOT/$MODULE_REL"
CONTRACT_PATH="$SUCCESSOR_ROOT/$CONTRACT_REL"
[[ -f "$CANONICAL_TRAMPOLINE" && ! -L "$CANONICAL_TRAMPOLINE" ]] \
  || fail_body_free 'SOURCE_DRIFT' 'canonical trampoline is absent, nonregular, or symlinked'
CANONICAL_TRAMPOLINE_RESOLVED=$("$READLINK_PATH" -f -- "$CANONICAL_TRAMPOLINE" 2>/dev/null) \
  || fail_body_free 'SOURCE_DRIFT' 'canonical trampoline cannot be canonicalized'
[[ "$CANONICAL_TRAMPOLINE_RESOLVED" == "$CANONICAL_TRAMPOLINE" ]] \
  || fail_body_free 'SOURCE_DRIFT' 'canonical trampoline contains alias drift'
case $0 in
  /*) ;;
  *) fail_body_free 'SOURCE_DRIFT' 'spooled trampoline path is not absolute' ;;
esac
[[ -f "$0" && ! -L "$0" ]] \
  || fail_body_free 'SOURCE_DRIFT' 'spooled trampoline is absent, nonregular, or symlinked'
CANONICAL_TRAMPOLINE_SHA256=$(hash_file "$CANONICAL_TRAMPOLINE") \
  || fail_body_free 'SOURCE_DRIFT' 'canonical trampoline cannot be hashed'
SPOOLED_TRAMPOLINE_SHA256=$(hash_file "$0") \
  || fail_body_free 'SOURCE_DRIFT' 'spooled trampoline cannot be hashed'
[[ "$SPOOLED_TRAMPOLINE_SHA256" == "$CANONICAL_TRAMPOLINE_SHA256" ]] \
  || fail_body_free 'SOURCE_DRIFT' 'spooled and canonical trampoline hashes differ'
"$CMP_PATH" -s -- "$0" "$CANONICAL_TRAMPOLINE" \
  || fail_body_free 'SOURCE_DRIFT' 'spooled and canonical trampoline bytes differ'
CANONICAL_NORMALIZED_TRAMPOLINE_SHA256=$(hash_normalized_trampoline "$CANONICAL_TRAMPOLINE") \
  || fail_body_free 'SOURCE_DRIFT' 'canonical trampoline cannot be normalized and hashed'
[[ "$CANONICAL_NORMALIZED_TRAMPOLINE_SHA256" == "$NORMALIZED_TRAMPOLINE_SHA256" ]] \
  || fail_body_free 'SOURCE_DRIFT' 'canonical trampoline normalized hash differs from freeze'
SPOOLED_NORMALIZED_TRAMPOLINE_SHA256=$(hash_normalized_trampoline "$0") \
  || fail_body_free 'SOURCE_DRIFT' 'spooled trampoline cannot be normalized and hashed'
[[ "$SPOOLED_NORMALIZED_TRAMPOLINE_SHA256" == "$NORMALIZED_TRAMPOLINE_SHA256" ]] \
  || fail_body_free 'SOURCE_DRIFT' 'spooled trampoline normalized hash differs from freeze'

verify_bound_file() {
  local path=$1
  local expected_sha256=$2
  local label=$3
  local resolved actual
  [[ -f "$path" && ! -L "$path" ]] \
    || fail_body_free 'SOURCE_DRIFT' "$label is absent, nonregular, or symlinked"
  resolved=$("$READLINK_PATH" -f -- "$path" 2>/dev/null) \
    || fail_body_free 'SOURCE_DRIFT' "$label cannot be canonicalized"
  [[ "$resolved" == "$path" ]] \
    || fail_body_free 'SOURCE_DRIFT' "$label path contains alias drift"
  actual=$(hash_file "$path") \
    || fail_body_free 'SOURCE_DRIFT' "$label cannot be hashed"
  [[ "$actual" == "$expected_sha256" ]] \
    || fail_body_free 'SOURCE_DRIFT' "$label hash differs from the exact freeze"
}

verify_bound_file "$MODULE_PATH" "$MODULE_SHA256" 'diagnostic module'
verify_bound_file "$CONTRACT_PATH" "$CONTRACT_SHA256" 'diagnostic contract'

[[ -d "$PYTHON_LIBRARY_LOGICAL_DIR" && ! -L "$PYTHON_LIBRARY_LOGICAL_DIR" ]] \
  || fail_body_free 'LIBPYTHON_DRIFT' 'Python logical library directory is unavailable'
PYTHON_LIBRARY_DIR_RESOLVED=$("$READLINK_PATH" -f -- "$PYTHON_LIBRARY_LOGICAL_DIR" 2>/dev/null) \
  || fail_body_free 'LIBPYTHON_DRIFT' 'Python logical library directory cannot be canonicalized'
[[ "$PYTHON_LIBRARY_DIR_RESOLVED" == "$PYTHON_LIBRARY_CANONICAL_DIR" ]] \
  || fail_body_free 'LIBPYTHON_DRIFT' 'Python library directory canonical target differs'
[[ -f "$LIBPYTHON_LOGICAL_PATH" && ! -L "$LIBPYTHON_LOGICAL_PATH" ]] \
  || fail_body_free 'LIBPYTHON_DRIFT' 'libpython logical path is unavailable'
LIBPYTHON_RESOLVED=$("$READLINK_PATH" -f -- "$LIBPYTHON_LOGICAL_PATH" 2>/dev/null) \
  || fail_body_free 'LIBPYTHON_DRIFT' 'libpython cannot be canonicalized'
[[ "$LIBPYTHON_RESOLVED" == "$LIBPYTHON_CANONICAL_PATH" ]] \
  || fail_body_free 'LIBPYTHON_DRIFT' 'libpython canonical target differs'
LIBPYTHON_STAT=$("$STAT_PATH" -Lc '%s %a %u %g %h' -- "$LIBPYTHON_LOGICAL_PATH" 2>/dev/null) \
  || fail_body_free 'LIBPYTHON_DRIFT' 'libpython custody cannot be read'
[[ "$LIBPYTHON_STAT" == "$LIBPYTHON_SIZE $LIBPYTHON_MODE $LIBPYTHON_UID $LIBPYTHON_GID $LIBPYTHON_NLINK" ]] \
  || fail_body_free 'LIBPYTHON_DRIFT' 'libpython custody differs from freeze'
ACTUAL_LIBPYTHON_SHA256=$(hash_file "$LIBPYTHON_LOGICAL_PATH") \
  || fail_body_free 'LIBPYTHON_DRIFT' 'libpython cannot be hashed'
[[ "$ACTUAL_LIBPYTHON_SHA256" == "$LIBPYTHON_SHA256" ]] \
  || fail_body_free 'LIBPYTHON_DRIFT' 'libpython hash differs from freeze'
export LD_LIBRARY_PATH="$PYTHON_LIBRARY_LOGICAL_DIR"

RUN_PARENT=${RUN_ROOT%/*}
[[ -d "$RUN_PARENT" ]] \
  || fail_body_free 'RUN_ROOT_INVALID' 'run parent base directory is absent'
RUN_PARENT_RESOLVED=$("$READLINK_PATH" -f -- "$RUN_PARENT" 2>/dev/null) \
  || fail_body_free 'RUN_ROOT_INVALID' 'run parent base cannot be canonicalized'
[[ "$RUN_PARENT_RESOLVED" == "$RUN_PARENT" ]] \
  || fail_body_free 'RUN_ROOT_INVALID' 'run parent base contains alias drift'
[[ ! -e "$RUN_ROOT" && ! -L "$RUN_ROOT" ]] \
  || fail_body_free 'RUN_ROOT_INVALID' 'private run parent already exists or is symlinked'
"$PYTHON_COMMAND" -I -S -B -c \
  'import os,sys; path=sys.argv[1]; os.mkdir(path,0o700)' \
  "$RUN_ROOT" \
  || fail_body_free 'RUN_ROOT_INVALID' 'private run parent creation failed'
RUN_ROOT_RESOLVED=$("$READLINK_PATH" -f -- "$RUN_ROOT" 2>/dev/null) \
  || fail_body_free 'RUN_ROOT_INVALID' 'private run parent cannot be canonicalized'
[[ "$RUN_ROOT_RESOLVED" == "$RUN_ROOT" ]] \
  || fail_body_free 'RUN_ROOT_INVALID' 'private run parent contains alias drift'
RUN_ROOT_STAT=$("$STAT_PATH" -Lc '%a %u %g %h' -- "$RUN_ROOT" 2>/dev/null) \
  || fail_body_free 'RUN_ROOT_INVALID' 'private run parent custody cannot be read'
[[ "$RUN_ROOT_STAT" == "$RUN_ROOT_MODE $RUN_ROOT_UID $RUN_ROOT_GID $RUN_ROOT_NLINK" ]] \
  || fail_body_free 'RUN_ROOT_INVALID' 'private run parent custody differs from freeze'
[[ ! -e "$RUN_ROOT/evidence" && ! -L "$RUN_ROOT/evidence" ]] \
  || fail_body_free 'RUN_ROOT_INVALID' 'evidence child unexpectedly exists before core entry'

exec "$PYTHON_COMMAND" -I -S -B "$MODULE_PATH" --output-root "$RUN_ROOT/evidence"

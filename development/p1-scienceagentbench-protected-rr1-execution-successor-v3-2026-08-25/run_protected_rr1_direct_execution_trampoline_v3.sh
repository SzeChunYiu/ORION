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

SUCCESSOR_ROOT='/projects/hep/fs10/scratch/scyiu/orion_p1_sab_protected_rr1_direct_route_v1_20260824/repo-exec-successor-v3-20260825'
TRAMPOLINE_REL='development/p1-scienceagentbench-protected-rr1-execution-successor-v3-2026-08-25/run_protected_rr1_direct_execution_trampoline_v3.sh'
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
READLINK_SHA256='99dbafcdcba4adb285ea164c3a3bf27539719328a8ae5df9be6d84cdde1146dc'
CMP_PATH='/usr/bin/cmp'
CMP_SHA256='16d8b82bf5ee1774585ce5c63691cb156aa350c48f0d0689b27d13aa4b0a62eb'
STAT_PATH='/usr/bin/stat'
STAT_SHA256='f7ef3b1376596ce952779ea53a91ec97ce8b57389a3ffde75a499564b1c8f25f'
WC_PATH='/usr/bin/wc'
WC_SHA256='9cfb241d8d95fe3805a6d9af22b5dfac4f8aa0ce2d2b966db8b45a71baf501c9'
NORMALIZED_TRAMPOLINE_SHA256='a04b00ec70f346bf770438d039b94c10cdba38fa158b2af2c209942072f9b82d'
PYTHON_PATH_ENTRY='/sw/easybuild_milan/software/Python/3.11.5-GCCcore-13.2.0/bin'
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
PYTHON_LIBRARY_DIR_MODE='755'
PYTHON_LIBRARY_DIR_UID='1400'
PYTHON_LIBRARY_DIR_GID='1400'
PYTHON_LIBRARY_DIR_NLINK='4'
LIBPYTHON_ABI_PATH="$PYTHON_LIBRARY_LOGICAL_DIR/libpython3.so"
LIBPYTHON_ABI_SHA256='9ce9dfd0670cd9e05cdee0478b0a82425b1fd45abe7bdef807a4e7ba2a331f93'
LIBPYTHON_ABI_SIZE='15352'
LIBPYTHON_ABI_MODE='755'
LIBPYTHON_ABI_UID='1400'
LIBPYTHON_ABI_GID='1400'
LIBPYTHON_ABI_NLINK='1'

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
    "P1_SAB_PROTECTED_RR1_DIRECT_EXECUTION_TRAMPOLINE_V3_CANNOT_CHECK failure_code=${code} detail_sha256=${digest}" \
    >&2
  exit 2
}

[[ ${LD_LIBRARY_PATH+x} != x ]] \
  || fail_body_free 'ENVIRONMENT_INVALID' 'LD_LIBRARY_PATH must be absent on trampoline entry'
[[ ${LD_PRELOAD+x} != x ]] \
  || fail_body_free 'ENVIRONMENT_INVALID' 'LD_PRELOAD must be absent on trampoline entry'

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
for tool_binding in \
  "$READLINK_PATH:$READLINK_SHA256:readlink" \
  "$CMP_PATH:$CMP_SHA256:cmp" \
  "$STAT_PATH:$STAT_SHA256:stat" \
  "$WC_PATH:$WC_SHA256:wc"
do
  tool_path=${tool_binding%%:*}
  remainder=${tool_binding#*:}
  expected_tool_sha=${remainder%%:*}
  tool_label=${remainder#*:}
  [[ -x "$tool_path" && ! -L "$tool_path" ]] \
    || fail_body_free 'TOOLCHAIN_DRIFT' "absolute $tool_label utility is unavailable"
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
CANONICAL_NORMALIZED_TRAMPOLINE_SHA256=$(hash_normalized_trampoline "$CANONICAL_TRAMPOLINE") \
  || fail_body_free 'SOURCE_DRIFT' 'canonical trampoline cannot be normalized and hashed'
[[ "$CANONICAL_NORMALIZED_TRAMPOLINE_SHA256" == "$NORMALIZED_TRAMPOLINE_SHA256" ]] \
  || fail_body_free 'SOURCE_DRIFT' 'canonical trampoline normalized hash differs from the exact freeze'
SPOOLED_NORMALIZED_TRAMPOLINE_SHA256=$(hash_normalized_trampoline "$0") \
  || fail_body_free 'SOURCE_DRIFT' 'spooled trampoline cannot be normalized and hashed'
[[ "$SPOOLED_NORMALIZED_TRAMPOLINE_SHA256" == "$NORMALIZED_TRAMPOLINE_SHA256" ]] \
  || fail_body_free 'SOURCE_DRIFT' 'spooled trampoline normalized hash differs from the exact freeze'

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
  '/projects/hep/fs10/scratch/scyiu/orion_p1_sab_protected_rr1_direct_route_v1_20260824/live-rr1-exec-successor-v3-20260825/runtime-parent/evidence'
)
[[ $# -eq ${#EXPECTED_ARGV[@]} ]] \
  || fail_body_free 'ARGV_INVALID' 'direct execution argv count differs from the exact freeze'
ACTUAL_ARGV=("$@")
for index in "${!EXPECTED_ARGV[@]}"; do
  [[ "${ACTUAL_ARGV[$index]}" == "${EXPECTED_ARGV[$index]}" ]] \
    || fail_body_free 'ARGV_INVALID' 'direct execution argv order or value differs from the exact freeze'
done

[[ -d "$PYTHON_LIBRARY_LOGICAL_DIR" && ! -L "$PYTHON_LIBRARY_LOGICAL_DIR" ]] \
  || fail_body_free 'LIBPYTHON_DRIFT' 'Python library logical directory is absent, nondirectory, or leaf-symlinked'
PYTHON_LIBRARY_DIR_RESOLVED=$("$READLINK_PATH" -f -- "$PYTHON_LIBRARY_LOGICAL_DIR" 2>/dev/null) \
  || fail_body_free 'LIBPYTHON_DRIFT' 'Python library logical directory cannot be canonicalized'
[[ "$PYTHON_LIBRARY_DIR_RESOLVED" == "$PYTHON_LIBRARY_CANONICAL_DIR" ]] \
  || fail_body_free 'LIBPYTHON_DRIFT' 'Python library canonical directory differs from the exact freeze'
[[ -d "$PYTHON_LIBRARY_CANONICAL_DIR" && ! -L "$PYTHON_LIBRARY_CANONICAL_DIR" ]] \
  || fail_body_free 'LIBPYTHON_DRIFT' 'Python library canonical directory is absent, nondirectory, or leaf-symlinked'
PYTHON_LIBRARY_DIR_STAT=$("$STAT_PATH" -Lc '%a %u %g %h' -- "$PYTHON_LIBRARY_LOGICAL_DIR" 2>/dev/null) \
  || fail_body_free 'LIBPYTHON_DRIFT' 'Python library directory custody cannot be read'
[[ "$PYTHON_LIBRARY_DIR_STAT" == "$PYTHON_LIBRARY_DIR_MODE $PYTHON_LIBRARY_DIR_UID $PYTHON_LIBRARY_DIR_GID $PYTHON_LIBRARY_DIR_NLINK" ]] \
  || fail_body_free 'LIBPYTHON_DRIFT' 'Python library directory mode owner group or link count differs from the exact freeze'
PYTHON_LIBRARY_ENTRY_COUNT=0
for entry in \
  "$PYTHON_LIBRARY_LOGICAL_DIR"/* \
  "$PYTHON_LIBRARY_LOGICAL_DIR"/.[!.]* \
  "$PYTHON_LIBRARY_LOGICAL_DIR"/..?*
do
  [[ -e "$entry" || -L "$entry" ]] || continue
  entry_name=${entry##*/}
  case "$entry_name" in
    libpython3.11.so)
      [[ -L "$entry" && "$("$READLINK_PATH" -- "$entry" 2>/dev/null)" == 'libpython3.11.so.1.0' ]] \
        || fail_body_free 'LIBPYTHON_DRIFT' 'libpython3.11.so symlink target differs from the exact freeze'
      ;;
    libpython3.11.so.1.0|libpython3.so)
      [[ -f "$entry" && ! -L "$entry" ]] \
        || fail_body_free 'LIBPYTHON_DRIFT' 'Python library top-level regular file type differs from the exact freeze'
      ;;
    pkgconfig|python3.11)
      [[ -d "$entry" && ! -L "$entry" ]] \
        || fail_body_free 'LIBPYTHON_DRIFT' 'Python library top-level directory type differs from the exact freeze'
      entry_stat=$("$STAT_PATH" -Lc '%a %u %g' -- "$entry" 2>/dev/null) \
        || fail_body_free 'LIBPYTHON_DRIFT' 'Python library top-level directory custody cannot be read'
      [[ "$entry_stat" == "$PYTHON_LIBRARY_DIR_MODE $PYTHON_LIBRARY_DIR_UID $PYTHON_LIBRARY_DIR_GID" ]] \
        || fail_body_free 'LIBPYTHON_DRIFT' 'Python library top-level directory custody differs from the exact freeze'
      ;;
    *)
      fail_body_free 'LIBPYTHON_DRIFT' 'Python library directory contains an unexpected top-level search candidate'
      ;;
  esac
  PYTHON_LIBRARY_ENTRY_COUNT=$((PYTHON_LIBRARY_ENTRY_COUNT + 1))
done
[[ "$PYTHON_LIBRARY_ENTRY_COUNT" -eq 5 ]] \
  || fail_body_free 'LIBPYTHON_DRIFT' 'Python library top-level entry count differs from the exact freeze'
[[ -f "$LIBPYTHON_LOGICAL_PATH" && ! -L "$LIBPYTHON_LOGICAL_PATH" ]] \
  || fail_body_free 'LIBPYTHON_DRIFT' 'libpython logical path is absent, nonregular, or leaf-symlinked'
LIBPYTHON_RESOLVED=$("$READLINK_PATH" -f -- "$LIBPYTHON_LOGICAL_PATH" 2>/dev/null) \
  || fail_body_free 'LIBPYTHON_DRIFT' 'libpython logical path cannot be canonicalized'
[[ "$LIBPYTHON_RESOLVED" == "$LIBPYTHON_CANONICAL_PATH" ]] \
  || fail_body_free 'LIBPYTHON_DRIFT' 'libpython canonical path differs from the exact freeze'
[[ -f "$LIBPYTHON_CANONICAL_PATH" && ! -L "$LIBPYTHON_CANONICAL_PATH" ]] \
  || fail_body_free 'LIBPYTHON_DRIFT' 'libpython canonical path is absent, nonregular, or leaf-symlinked'
LIBPYTHON_STAT=$("$STAT_PATH" -Lc '%s %a %u %g %h' -- "$LIBPYTHON_LOGICAL_PATH" 2>/dev/null) \
  || fail_body_free 'LIBPYTHON_DRIFT' 'libpython custody cannot be read'
[[ "$LIBPYTHON_STAT" == "$LIBPYTHON_SIZE $LIBPYTHON_MODE $LIBPYTHON_UID $LIBPYTHON_GID $LIBPYTHON_NLINK" ]] \
  || fail_body_free 'LIBPYTHON_DRIFT' 'libpython size mode owner group or link count differs from the exact freeze'
ACTUAL_LIBPYTHON_SHA256=$(hash_file "$LIBPYTHON_LOGICAL_PATH") \
  || fail_body_free 'LIBPYTHON_DRIFT' 'libpython cannot be hashed'
[[ "$ACTUAL_LIBPYTHON_SHA256" == "$LIBPYTHON_SHA256" ]] \
  || fail_body_free 'LIBPYTHON_DRIFT' 'libpython hash differs from the exact freeze'
[[ -f "$LIBPYTHON_ABI_PATH" && ! -L "$LIBPYTHON_ABI_PATH" ]] \
  || fail_body_free 'LIBPYTHON_DRIFT' 'libpython ABI file is absent, nonregular, or leaf-symlinked'
LIBPYTHON_ABI_STAT=$("$STAT_PATH" -Lc '%s %a %u %g %h' -- "$LIBPYTHON_ABI_PATH" 2>/dev/null) \
  || fail_body_free 'LIBPYTHON_DRIFT' 'libpython ABI file custody cannot be read'
[[ "$LIBPYTHON_ABI_STAT" == "$LIBPYTHON_ABI_SIZE $LIBPYTHON_ABI_MODE $LIBPYTHON_ABI_UID $LIBPYTHON_ABI_GID $LIBPYTHON_ABI_NLINK" ]] \
  || fail_body_free 'LIBPYTHON_DRIFT' 'libpython ABI file size mode owner group or link count differs from the exact freeze'
ACTUAL_LIBPYTHON_ABI_SHA256=$(hash_file "$LIBPYTHON_ABI_PATH") \
  || fail_body_free 'LIBPYTHON_DRIFT' 'libpython ABI file cannot be hashed'
[[ "$ACTUAL_LIBPYTHON_ABI_SHA256" == "$LIBPYTHON_ABI_SHA256" ]] \
  || fail_body_free 'LIBPYTHON_DRIFT' 'libpython ABI file hash differs from the exact freeze'
export LD_LIBRARY_PATH="$PYTHON_LIBRARY_LOGICAL_DIR"
[[ "$LD_LIBRARY_PATH" == "$PYTHON_LIBRARY_LOGICAL_DIR" ]] \
  || fail_body_free 'ENVIRONMENT_INVALID' 'LD_LIBRARY_PATH exact assignment failed'
PYTHON_RUNTIME_PROBE_COMBINED_BYTES=$( \
  "$PYTHON_COMMAND" -B -I -S -c 'import ctypes,tarfile,zlib' 2>&1 \
    | "$WC_PATH" -c \
) || fail_body_free 'PYTHON_RUNTIME_UNAVAILABLE' 'exact Python loader and donor standard-library import probe failed'
PYTHON_RUNTIME_PROBE_COMBINED_BYTES=${PYTHON_RUNTIME_PROBE_COMBINED_BYTES//[[:space:]]/}
[[ "$PYTHON_RUNTIME_PROBE_COMBINED_BYTES" == '0' ]] \
  || fail_body_free 'PYTHON_RUNTIME_UNAVAILABLE' 'exact Python loader and donor standard-library import probe emitted output'

exec /usr/bin/bash "$ORIGINAL_LAUNCHER" "$@"

#!/usr/bin/env bash
#SBATCH --job-name=orion-04-crb-replay
#SBATCH --account=hep2023-1-3
#SBATCH --partition=hep
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=48
#SBATCH --mem=192G
#SBATCH --time=24:00:00
#SBATCH --output=%x-%j.out
#SBATCH --error=%x-%j.err

# ORION-04 CR-B full-census replay successor. This script cannot authorize
# itself. Process receipts do not promote scientific authority.

set -Eeuo pipefail
export PYTHONDONTWRITEBYTECODE=1

SUBJECT_COMMIT=0c451e862a0eeddac7c673813c4dc499f134b088
REPOSITORY="${SLURM_SUBMIT_DIR:?submit from the exact repository checkout}"
AUTHORIZED_COMMIT="${ORION04_CRB_AUTHORIZED_COMMIT:?missing exact authorized commit}"
AUTHORIZATION_PATH="${ORION04_CRB_AUTHORIZATION_PATH:?missing operator request path}"
SOURCE_MANIFEST_SHA256="${ORION04_CRB_SOURCE_MANIFEST_SHA256:?missing source manifest digest}"
NON_DUPLICATION_KEY="${ORION04_CRB_NON_DUPLICATION_KEY:?missing new nonduplication key}"
DURABLE_ROOT="${ORION04_CRB_DURABLE_ROOT:?missing explicit durable root}"
GLOBAL_REGISTRY_ROOT="${ORION04_CRB_GLOBAL_REGISTRY_ROOT:?missing global registry root}"
ENGINE_ROOT="${REPOSITORY}/papers/orion-04-rooted-completion-certificates/evidence/crb-full-replay/successor-v1/engine_b"
SUCCESSOR_ROOT="${ENGINE_ROOT}/.."
PREBIND="${SUCCESSOR_ROOT}/GLOBAL_REGISTRY_PREBIND_V1.json"
NODE_LOCAL_ROOT="${SLURM_TMPDIR:-/local/slurmtmp.${SLURM_JOB_ID}}"
OUTPUT_ROOT="${NODE_LOCAL_ROOT}/orion-04-crb-output"
D2_GENERATION_ROOT="${OUTPUT_ROOT}/census-d2"
D3_GENERATION_ROOT="${OUTPUT_ROOT}/census-d3"
D2_CHECKPOINT="${DURABLE_ROOT}/d2-generation-checkpoint"
D3_CHECKPOINT="${DURABLE_ROOT}/d3-generation-checkpoint"
VENV="${NODE_LOCAL_ROOT}/orion-04-crb-venv"
DRUP_SOURCE="${NODE_LOCAL_ROOT}/drat-trim-source"
COVERAGE_ARGUMENT="${ENGINE_ROOT}/docs/plans/2026-08-27-crb-census-coverage-argument.md"
D2_SCOPE=NQ_D2_NORMALIZED_LENGTH_19
D3_SCOPE=NQ_D3_STRUCTURED_LENGTH_25
GENERATION_WALL=43200
EXECUTION_WALL=14400
EXECUTION_THREADS=32
DRUP_THREADS=48
PHASE=BOOTSTRAP
REGISTRY_TERMINALIZATION_FAILURE=70

log() { printf '[%s] %s\n' "$(date -u +%Y-%m-%dT%H:%M:%SZ)" "$*"; }

if [[ "${DURABLE_ROOT}" != /* || "${GLOBAL_REGISTRY_ROOT}" != /* ]]; then
  echo "durable and registry roots must be absolute" >&2
  exit 64
fi
mkdir -p "${DURABLE_ROOT}"
exec > >(tee -a "${DURABLE_ROOT}/JOB_STDOUT.txt") \
  2> >(tee -a "${DURABLE_ROOT}/JOB_STDERR.txt" >&2)

on_err() {
  local status="$1" line="$2" command="$3"
  set +e
  trap - ERR
  python3 "${ENGINE_ROOT}/replay_custody.py" first-failure "${DURABLE_ROOT}" \
    --exit-code "${status}" --line "${line}" --command "${command}" --phase "${PHASE}" \
    >/dev/null 2>&1 || {
      printf 'FIRST_FAILURE_FALLBACK exit=%s line=%s phase=%s command=%q\n' \
        "${status}" "${line}" "${PHASE}" "${command}" \
        > "${DURABLE_ROOT}/FIRST_FAILURE_FALLBACK.txt"
    }
  return "${status}"
}

on_signal() {
  local signal="$1" status="$2"
  trap '' INT TERM
  set +e
  PHASE="SIGNAL_${signal}"
  on_err "${status}" "${LINENO}" "signal ${signal}"
  exit "${status}"
}

on_exit() {
  local status="$1"
  set +e
  trap - ERR EXIT
  trap '' INT TERM
  if ! python3 "${ENGINE_ROOT}/submission_gate.py" terminalize-started \
    --global-root "${GLOBAL_REGISTRY_ROOT}" --prebind "${PREBIND}" \
    --key "${NON_DUPLICATION_KEY}" --job-id "${SLURM_JOB_ID}" \
    --successor-commit "${AUTHORIZED_COMMIT}" \
    --process-exit-code "${status}" --phase "${PHASE}" >/dev/null; then
    printf 'ORION04_CRB_REGISTRY_TERMINALIZATION_FAILED\nexit=%s\nphase=%s\njob_id=%s\n' \
      "${status}" "${PHASE}" "${SLURM_JOB_ID}" \
      > "${DURABLE_ROOT}/REGISTRY_TERMINALIZATION_FALLBACK.txt"
    if [[ "${status}" -eq 0 ]]; then
      status="${REGISTRY_TERMINALIZATION_FAILURE}"
      PHASE=REGISTRY_TERMINALIZATION_FAILED
    fi
  fi
  python3 "${ENGINE_ROOT}/replay_custody.py" exit-receipt "${DURABLE_ROOT}" \
    --exit-code "${status}" --phase "${PHASE}" >/dev/null 2>&1 || \
    printf 'EXIT_RECEIPT_FALLBACK exit=%s phase=%s\n' "${status}" "${PHASE}" \
      > "${DURABLE_ROOT}/EXIT_RECEIPT_FALLBACK.txt"
  exit "${status}"
}

trap 'on_err "$?" "$LINENO" "$BASH_COMMAND"' ERR
trap 'on_exit "$?"' EXIT
trap 'on_signal TERM 143' TERM
trap 'on_signal INT 130' INT

AUTHORIZATION_SHA256="$(sha256sum "${AUTHORIZATION_PATH}" | awk '{print $1}')"
python3 "${ENGINE_ROOT}/replay_custody.py" capture-environment "${DURABLE_ROOT}" \
  --job-id "${SLURM_JOB_ID}" --authorized-commit "${AUTHORIZED_COMMIT}" \
  --source-manifest-sha256 "${SOURCE_MANIFEST_SHA256}" \
  --authorization-sha256 "${AUTHORIZATION_SHA256}" \
  --global-registry-root "${GLOBAL_REGISTRY_ROOT}" >/dev/null

PHASE=IDENTITY_GATE
test "$(git -C "${REPOSITORY}" rev-parse HEAD)" = "${AUTHORIZED_COMMIT}"
git -C "${REPOSITORY}" diff --quiet
git -C "${REPOSITORY}" diff --cached --quiet
test -z "$(git -C "${REPOSITORY}" status --porcelain --untracked-files=all)"
test -z "$(find "${REPOSITORY}" -type f \( -name '*.pyc' -o -name '*.pyo' \) -print -quit)"
git -C "${REPOSITORY}" merge-base --is-ancestor "${SUBJECT_COMMIT}" HEAD
python3 "${ENGINE_ROOT}/build_manifest.py" --verify \
  --root "${ENGINE_ROOT}" --output "${ENGINE_ROOT}/SOURCE_MANIFEST.json"
OBSERVED_SOURCE_MANIFEST_SHA256="$(python3 - "${ENGINE_ROOT}/SOURCE_MANIFEST.json" <<'PY'
import json
import sys
print(json.loads(open(sys.argv[1], encoding="utf-8").read())["manifest_sha256"])
PY
)"
test "${OBSERVED_SOURCE_MANIFEST_SHA256}" = "${SOURCE_MANIFEST_SHA256}"
VALIDATION_JSON="$(python3 "${ENGINE_ROOT}/submission_gate.py" validate \
  --authorization "${AUTHORIZATION_PATH}" --expected-commit "${AUTHORIZED_COMMIT}" \
  --source-manifest-sha256 "${SOURCE_MANIFEST_SHA256}")"
python3 - "${VALIDATION_JSON}" "${DURABLE_ROOT}" "${GLOBAL_REGISTRY_ROOT}" \
  "${NON_DUPLICATION_KEY}" <<'PY'
import json
import sys
receipt = json.loads(sys.argv[1])
bindings = {"durable_root": sys.argv[2], "global_registry_root": sys.argv[3],
            "nonduplication_key": sys.argv[4]}
if any(receipt.get(key) != value for key, value in bindings.items()):
    raise SystemExit(f"operator request environment binding mismatch: {receipt}")
if receipt.get("terminal") != "ORION04_ONE_SHOT_REQUEST_BINDINGS_VALID":
    raise SystemExit("operator request validation terminal mismatch")
if receipt.get("operator_attestation") != "USER_SUPPLIED_UNVERIFIED_BY_MACHINE":
    raise SystemExit("operator request attestation boundary mismatch")
if receipt.get("machine_established_externality") is not False:
    raise SystemExit("operator request cannot establish externality")
if receipt.get("scientific_authority_delta") != "NONE":
    raise SystemExit("operator request cannot create scientific authority")
PY
python3 "${ENGINE_ROOT}/submission_gate.py" assert-submitted \
  --global-root "${GLOBAL_REGISTRY_ROOT}" --prebind "${PREBIND}" \
  --key "${NON_DUPLICATION_KEY}" --job-id "${SLURM_JOB_ID}" \
  --successor-commit "${AUTHORIZED_COMMIT}" >/dev/null
log "identity, authorization, and global registry bound: ${AUTHORIZED_COMMIT}"

PHASE=NODE_LOCAL_PREFLIGHT
mkdir -p "${NODE_LOCAL_ROOT}"
AVAILABLE_KB="$(df -k "${NODE_LOCAL_ROOT}" | awk 'NR==2 {print $4}')"
if [[ "${AVAILABLE_KB}" -lt 41943040 ]]; then
  log "ORION04_CRB_NODE_LOCAL_INSUFFICIENT: ${AVAILABLE_KB} KiB free (40 GiB floor)"
  exit 1
fi
python3 -m venv "${VENV}"
"${VENV}/bin/python" -m pip install --disable-pip-version-check --no-input \
  --no-deps -r "${ENGINE_ROOT}/requirements.txt"

# Phase 0: build the exact pinned external DRUP checker.
PHASE=PHASE_0_EXTERNAL_CHECKER
DRUP_PROTOCOL="${ENGINE_ROOT}/EXTERNAL_DRUP_CHECKER_PROTOCOL.json"
DRUP_COMMIT="$("${VENV}/bin/python" - "${DRUP_PROTOCOL}" <<'PY'
import json
import sys
print(json.loads(open(sys.argv[1], encoding="utf-8").read())["tool"]["commit"])
PY
)"
git clone --quiet https://github.com/marijnheule/drat-trim.git "${DRUP_SOURCE}"
git -C "${DRUP_SOURCE}" checkout --quiet "${DRUP_COMMIT}"
"${VENV}/bin/python" - "${DRUP_PROTOCOL}" "${DRUP_SOURCE}" <<'PY'
import json
import subprocess
import sys
protocol = json.loads(open(sys.argv[1], encoding="utf-8").read())["tool"]
source = sys.argv[2]
def git(*args):
    return subprocess.run(("git", "-C", source, *args), check=True,
                          stdout=subprocess.PIPE, text=True).stdout.strip()
observed = {"commit": git("rev-parse", "HEAD"), "tree": git("rev-parse", "HEAD^{tree}")}
if observed != {"commit": protocol["commit"], "tree": protocol["tree"]}:
    raise SystemExit(f"drat-trim source identity drift: {observed}")
if git("status", "--porcelain"):
    raise SystemExit("drat-trim source tree is dirty")
PY
make -C "${DRUP_SOURCE}" drat-trim
test -x "${DRUP_SOURCE}/drat-trim"
log "external checker built at ${DRUP_COMMIT}"

# Phase 1A: generate D2 alone and durably publish every byte before D3 starts.
PHASE=PHASE_1A_D2_CENSUS_GENERATION
mkdir -p "${OUTPUT_ROOT}"
"${VENV}/bin/python" "${ENGINE_ROOT}/crb_census.py" \
  --scope d2 --output-root "${D2_GENERATION_ROOT}" \
  --coverage-argument "${COVERAGE_ARGUMENT}" --threads 48 \
  --execution-context AUTHORIZED_LUNARC_REPLAY \
  --max-wall-seconds "${GENERATION_WALL}" --max-nodes-per-task 2000000000
"${VENV}/bin/python" - "${D2_GENERATION_ROOT}/census_generation_receipt.json" <<'PY'
import json
import sys
receipt = json.loads(open(sys.argv[1], encoding="utf-8").read())
if receipt["terminal"] != "NQ_CR_B_D2_CENSUS_GENERATED_INDEPENDENTLY":
    raise SystemExit(f"D2 census generation failed: {receipt['terminal']}")
counts = {item["scope"]: item["record_count"] for item in receipt["scopes"]}
expected = {"NQ_D2_NORMALIZED_LENGTH_19": 98622}
if counts != expected:
    raise SystemExit(f"frozen D2 denominator mismatch: {counts}")
if any(type(value) is not int for value in receipt.get("generation_metrics", {}).values()):
    raise SystemExit("D2 generation receipt contains a non-integer metric")
PY
PHASE=PHASE_1A_D2_DURABLE_CHECKPOINT
"${VENV}/bin/python" "${ENGINE_ROOT}/replay_custody.py" create-phase1-checkpoint \
  "${D2_GENERATION_ROOT}" "${D2_CHECKPOINT}" >/dev/null
"${VENV}/bin/python" "${ENGINE_ROOT}/replay_custody.py" verify-phase1-checkpoint "${D2_CHECKPOINT}" >/dev/null
log "D2 generation durably checkpointed before D3: 98622 records"

# Phase 1B: derive D3 only from the already-durable, byte-bound D2 checkpoint.
PHASE=PHASE_1B_D3_CENSUS_GENERATION
"${VENV}/bin/python" "${ENGINE_ROOT}/crb_census.py" \
  --scope d3 --d2-input-root "${D2_CHECKPOINT}/input/${D2_SCOPE}" \
  --output-root "${D3_GENERATION_ROOT}" \
  --coverage-argument "${COVERAGE_ARGUMENT}" --threads 48 \
  --execution-context AUTHORIZED_LUNARC_REPLAY \
  --max-wall-seconds "${GENERATION_WALL}" --max-nodes-per-task 2000000000
"${VENV}/bin/python" - "${D3_GENERATION_ROOT}/census_generation_receipt.json" \
  "${D2_CHECKPOINT}/input/${D2_SCOPE}/input_manifest.json" <<'PY'
import json
import sys
receipt = json.loads(open(sys.argv[1], encoding="utf-8").read())
d2_manifest = json.loads(open(sys.argv[2], encoding="utf-8").read())
if receipt["terminal"] != "NQ_CR_B_D3_CENSUS_GENERATED_FROM_CHECKPOINTED_D2":
    raise SystemExit(f"D3 census generation failed: {receipt['terminal']}")
counts = {item["scope"]: item["record_count"] for item in receipt["scopes"]}
if counts != {"NQ_D3_STRUCTURED_LENGTH_25": 230983}:
    raise SystemExit(f"frozen D3 denominator mismatch: {counts}")
if receipt.get("d2_input_manifest_sha256") != d2_manifest["manifest_sha256"]:
    raise SystemExit("D3 receipt is not bound to the durable D2 input manifest")
if any(type(value) is not int for value in receipt.get("generation_metrics", {}).values()):
    raise SystemExit("D3 generation receipt contains a non-integer metric")
PY
PHASE=PHASE_1B_D3_DURABLE_CHECKPOINT
"${VENV}/bin/python" "${ENGINE_ROOT}/replay_custody.py" create-phase1-checkpoint \
  "${D3_GENERATION_ROOT}" "${D3_CHECKPOINT}" >/dev/null
"${VENV}/bin/python" "${ENGINE_ROOT}/replay_custody.py" verify-phase1-checkpoint "${D3_CHECKPOINT}" >/dev/null
log "D3 generation durably checkpointed: 230983 records"

# Phase 2: execute every record and independently recheck every SAT witness.
PHASE=PHASE_2_STRUCTURAL_EXECUTION
for SCOPE in "${D2_SCOPE}" "${D3_SCOPE}"; do
  SCOPE_ROOT="${OUTPUT_ROOT}/${SCOPE}"
  if [[ "${SCOPE}" = "${D2_SCOPE}" ]]; then
    INPUT_ROOT="${D2_CHECKPOINT}/input/${D2_SCOPE}"
  else
    INPUT_ROOT="${D3_CHECKPOINT}/input/${D3_SCOPE}"
  fi
  mkdir -p "${SCOPE_ROOT}/proofs"
  "${VENV}/bin/python" "${ENGINE_ROOT}/run_engine_b.py" \
    --mode execute --subject-commit "${SUBJECT_COMMIT}" \
    --source-manifest "${ENGINE_ROOT}/SOURCE_MANIFEST.json" \
    --input-root "${INPUT_ROOT}" \
    --input-manifest "${INPUT_ROOT}/input_manifest.json" \
    --output "${SCOPE_ROOT}/ENGINE_B_RECEIPT.json" \
    --certificates "${SCOPE_ROOT}/ENGINE_B_CERTIFICATES.jsonl" \
    --proof-root "${SCOPE_ROOT}/proofs" --threads "${EXECUTION_THREADS}" \
    --max-wall-seconds "${EXECUTION_WALL}" --solver g4
  "${VENV}/bin/python" "${ENGINE_ROOT}/verify_receipt.py" \
    "${SCOPE_ROOT}/ENGINE_B_RECEIPT.json" \
    --source-manifest "${ENGINE_ROOT}/SOURCE_MANIFEST.json"
  "${VENV}/bin/python" "${ENGINE_ROOT}/verify_positive_witnesses.py" \
    --record-stream "${INPUT_ROOT}/records.jsonl" \
    --certificates "${SCOPE_ROOT}/ENGINE_B_CERTIFICATES.jsonl" \
    --output "${SCOPE_ROOT}/POSITIVE_WITNESS_RECEIPT.json"
  log "structural execution and positive-witness gate complete: ${SCOPE}"
done

# Phase 3: externally check every UNSAT proof and verify the batch receipts.
PHASE=PHASE_3_EXTERNAL_DRUP
for SCOPE in "${D2_SCOPE}" "${D3_SCOPE}"; do
  SCOPE_ROOT="${OUTPUT_ROOT}/${SCOPE}"
  if [[ "${SCOPE}" = "${D2_SCOPE}" ]]; then
    INPUT_ROOT="${D2_CHECKPOINT}/input/${D2_SCOPE}"
  else
    INPUT_ROOT="${D3_CHECKPOINT}/input/${D3_SCOPE}"
  fi
  "${VENV}/bin/python" "${ENGINE_ROOT}/batch_external_drup.py" \
    --protocol "${ENGINE_ROOT}/EXTERNAL_DRUP_CHECKER_PROTOCOL.json" \
    --record-stream "${INPUT_ROOT}/records.jsonl" \
    --certificates "${SCOPE_ROOT}/ENGINE_B_CERTIFICATES.jsonl" \
    --artifact-root "${SCOPE_ROOT}/proofs" --checker "${DRUP_SOURCE}/drat-trim" \
    --checker-source-root "${DRUP_SOURCE}" \
    --receipts "${SCOPE_ROOT}/DRUP_BATCH_LINES.jsonl" \
    --output "${SCOPE_ROOT}/DRUP_BATCH_RECEIPT.json" \
    --threads "${DRUP_THREADS}" --chunk-size 64
  "${VENV}/bin/python" "${ENGINE_ROOT}/batch_external_drup.py" \
    --verify --resample 32 \
    --protocol "${ENGINE_ROOT}/EXTERNAL_DRUP_CHECKER_PROTOCOL.json" \
    --record-stream "${INPUT_ROOT}/records.jsonl" \
    --certificates "${SCOPE_ROOT}/ENGINE_B_CERTIFICATES.jsonl" \
    --artifact-root "${SCOPE_ROOT}/proofs" --checker "${DRUP_SOURCE}/drat-trim" \
    --checker-source-root "${DRUP_SOURCE}" \
    --receipts "${SCOPE_ROOT}/DRUP_BATCH_LINES.jsonl" \
    --output "${SCOPE_ROOT}/DRUP_BATCH_RECEIPT.json"
  log "external DRUP batch verified: ${SCOPE}"
done

# Phase 4: copy the post-generation sealed chain durably with raw-byte hashes.
PHASE=PHASE_4_DURABLE_COPY
"${VENV}/bin/python" - "${OUTPUT_ROOT}" "${DURABLE_ROOT}" <<'PY'
import gzip
import hashlib
import os
import shutil
import sys
from pathlib import Path
output_root = Path(sys.argv[1])
durable_root = Path(sys.argv[2]) / "post-generation-chain"
stage = durable_root.with_name(f".{durable_root.name}.{os.getpid()}.tmp")
if durable_root.exists() or stage.exists():
    raise SystemExit("ORION04_CRB_DURABLE_DESTINATION_ALREADY_EXISTS")
stage.mkdir(parents=True)
scopes = ("NQ_D2_NORMALIZED_LENGTH_19", "NQ_D3_STRUCTURED_LENGTH_25")
rows = []
def sha(path):
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1 << 20), b""):
            digest.update(block)
    return digest.hexdigest()
def exact(relative):
    source = output_root / relative
    target = stage / relative
    target.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(source, target)
    expected = sha(source)
    if sha(target) != expected:
        raise SystemExit(f"ORION04_CRB_DURABLE_COPY_CORRUPT: {relative}")
    rows.append((expected, relative))
def compressed(relative):
    source = output_root / relative
    target = stage / f"{relative}.gz"
    target.parent.mkdir(parents=True, exist_ok=True)
    expected = sha(source)
    with source.open("rb") as reader, gzip.open(target, "wb") as writer:
        shutil.copyfileobj(reader, writer, 1 << 20)
    digest = hashlib.sha256()
    with gzip.open(target, "rb") as reader:
        for block in iter(lambda: reader.read(1 << 20), b""):
            digest.update(block)
    if digest.hexdigest() != expected:
        raise SystemExit(f"ORION04_CRB_DURABLE_COPY_CORRUPT: {relative}")
    rows.append((expected, relative))
for scope in scopes:
    exact(f"{scope}/ENGINE_B_RECEIPT.json")
    exact(f"{scope}/POSITIVE_WITNESS_RECEIPT.json")
    exact(f"{scope}/DRUP_BATCH_RECEIPT.json")
    compressed(f"{scope}/ENGINE_B_CERTIFICATES.jsonl")
    compressed(f"{scope}/DRUP_BATCH_LINES.jsonl")
(stage / "SHA256SUMS").write_text(
    "".join(f"{digest}  {relative}\n" for digest, relative in rows), encoding="ascii"
)
os.replace(stage, durable_root)
print("durable post-generation chain copied", flush=True)
PY

PHASE=PROCESS_COMPLETE_AWAITING_ADJUDICATION
log "ORION-04 CR-B process chain complete for job ${SLURM_JOB_ID}; science adjudication not promoted"

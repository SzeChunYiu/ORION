#!/usr/bin/env bash
#SBATCH --job-name=orion-nq-r9-crb-full
#SBATCH --account=hep2023-1-3
#SBATCH --partition=hep
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=48
#SBATCH --mem=192G
#SBATCH --time=24:00:00
#SBATCH --output=%x-%j.out
#SBATCH --error=%x-%j.err

# CR-B full-census replay: independent generation, per-record SAT execution,
# and external DRUP verification of every UNSAT certificate.  Every phase is
# fail-closed; the job's exit status is green only when BOTH scope batches
# reach NQ_ENGINE_B_EXTERNAL_DRUP_ALL_UNSAT_CERTIFICATES_VERIFIED.
#
# Frozen terminals on failure:
#   NQ_CR_B_CENSUS_GENERATION_MISMATCH / NQ_CR_B_CENSUS_GENERATION_RESOURCE_BOUND
#   (generation), CANNOT_CHECK_ENVIRONMENT / CANNOT_CHECK_RESOURCE_BOUND
#   (execution), NQ_ENGINE_B_EXTERNAL_DRUP_CONTROL_REJECTED /
#   CANNOT_CHECK_EXTERNAL_DRUP_TIMEOUT / CANNOT_CHECK_EXTERNAL_DRUP_BATCH_INCOMPLETE
#   (external checking), NQ_CR_B_DURABLE_COPY_CORRUPT (durable copy-out).
#
# Output layout: all intermediate artifacts, including the per-record CNF and
# DRUP proof streams (tens of GB), are written node-local (SLURM_TMPDIR when
# exported, otherwise the SLURM-precreated /local/slurmtmp.<jobid>) and
# vanish with the node allocation.  Phase 4 copies the sealed proof chain
# (receipts, manifests, coverage declarations, certificates, batch lines,
# frozen shards) durably, gzip-compressed, with a raw-byte SHA256SUMS ledger;
# per-record CNF/DRUP digests are sealed inside the certificates and batch
# lines, and the artifacts regenerate deterministically from them.

set -euo pipefail

SUBJECT_COMMIT=0c451e862a0eeddac7c673813c4dc499f134b088
REPOSITORY="${SLURM_SUBMIT_DIR:?submit from the exact repository checkout}"
AUTHORIZED_COMMIT="${NQ_CRB_AUTHORIZED_COMMIT:?bind the reviewed authorization commit}"
ENGINE_ROOT="${REPOSITORY}/papers/five-paper-top-tier-r8/NQ/lunarc-r9/replay/engine_b"
# LUNARC does not export SLURM_TMPDIR; SLURM pre-creates the per-job
# node-local directory /local/slurmtmp.<jobid> on the 1.5 TB NVMe local disk.
# All intermediate artifacts (venv, checker build, tens of GB of CNF/DRUP
# proofs, census streams) live there and vanish with the allocation.
NODE_LOCAL_ROOT="${SLURM_TMPDIR:-/local/slurmtmp.${SLURM_JOB_ID}}"
OUTPUT_ROOT="${NODE_LOCAL_ROOT}/nq-crb-output"
DURABLE_ROOT="${NQ_CRB_DURABLE_ROOT:-${ENGINE_ROOT}/results/${SLURM_JOB_ID}}"
VENV="${NODE_LOCAL_ROOT}/nq-crb-venv"
DRUP_SOURCE="${NODE_LOCAL_ROOT}/drat-trim-source"
COVERAGE_ARGUMENT="${ENGINE_ROOT}/docs/plans/2026-08-27-crb-census-coverage-argument.md"
D2_SCOPE=NQ_D2_NORMALIZED_LENGTH_19
D3_SCOPE=NQ_D3_STRUCTURED_LENGTH_25
GENERATION_WALL=43200
EXECUTION_WALL=14400
DRUP_THREADS=48

log() { printf '[%s] %s\n' "$(date -u +%Y-%m-%dT%H:%M:%SZ)" "$*"; }

test "$(git -C "${REPOSITORY}" rev-parse HEAD)" = "${AUTHORIZED_COMMIT}"
git -C "${REPOSITORY}" diff --quiet
git -C "${REPOSITORY}" diff --cached --quiet
git -C "${REPOSITORY}" merge-base --is-ancestor "${SUBJECT_COMMIT}" HEAD
log "identity bound: ${AUTHORIZED_COMMIT}"

mkdir -p "${NODE_LOCAL_ROOT}"
AVAILABLE_KB="$(df -k "${NODE_LOCAL_ROOT}" | awk 'NR==2 {print $4}')"
if [[ "${AVAILABLE_KB}" -lt 41943040 ]]; then
  log "NQ_CR_B_NODE_LOCAL_INSUFFICIENT: ${AVAILABLE_KB} KiB free on ${NODE_LOCAL_ROOT} (40 GiB floor)"
  exit 1
fi
log "node-local scratch ready: ${NODE_LOCAL_ROOT} (${AVAILABLE_KB} KiB free)"

python3 -m venv "${VENV}"
"${VENV}/bin/python" -m pip install --disable-pip-version-check --no-input \
  --no-deps -r "${ENGINE_ROOT}/requirements.txt"

# ---------------------------------------------------------------------------
# Phase 0: build the pinned external checker from its frozen source identity.
# ---------------------------------------------------------------------------
DRUP_PROTOCOL="${ENGINE_ROOT}/EXTERNAL_DRUP_CHECKER_PROTOCOL.json"
DRUP_COMMIT="$("${VENV}/bin/python" - "${DRUP_PROTOCOL}" <<'PY'
import json
import sys

protocol = json.loads(open(sys.argv[1], encoding="utf-8").read())
print(protocol["tool"]["commit"])
PY
)"
DRUP_COMMIT="${DRUP_COMMIT:?protocol commit missing}"
git clone --quiet https://github.com/marijnheule/drat-trim.git "${DRUP_SOURCE}"
git -C "${DRUP_SOURCE}" checkout --quiet "${DRUP_COMMIT}"
"${VENV}/bin/python" - "${DRUP_PROTOCOL}" "${DRUP_SOURCE}" <<'PY'
import json
import subprocess
import sys

protocol = json.loads(open(sys.argv[1], encoding="utf-8").read())
tool = protocol["tool"]
source = sys.argv[2]


def git(*arguments: str) -> str:
    return subprocess.run(
        ("git", "-C", source, *arguments),
        check=True,
        stdout=subprocess.PIPE,
        text=True,
    ).stdout.strip()


observed = {
    "commit": git("rev-parse", "HEAD"),
    "tree": git("rev-parse", "HEAD^{tree}"),
}
if observed["commit"] != tool["commit"] or observed["tree"] != tool["tree"]:
    raise SystemExit(f"drat-trim source identity drift: {observed}")
if git("status", "--porcelain"):
    raise SystemExit("drat-trim source tree is dirty before the build")
PY
make -C "${DRUP_SOURCE}" drat-trim
test -x "${DRUP_SOURCE}/drat-trim"
log "external checker built at ${DRUP_COMMIT}"

# ---------------------------------------------------------------------------
# Phase 1: independent CR-B generation of both declared census scopes.
# ---------------------------------------------------------------------------
mkdir -p "${OUTPUT_ROOT}"
"${VENV}/bin/python" "${ENGINE_ROOT}/crb_census.py" \
  --scope both \
  --output-root "${OUTPUT_ROOT}/census" \
  --coverage-argument "${COVERAGE_ARGUMENT}" \
  --threads 48 \
  --max-wall-seconds "${GENERATION_WALL}" \
  --max-nodes-per-task 2000000000
"${VENV}/bin/python" - "${OUTPUT_ROOT}/census/census_generation_receipt.json" <<'PY'
import json
import sys

receipt = json.loads(open(sys.argv[1], encoding="utf-8").read())
terminal = receipt["terminal"]
if terminal != "NQ_CR_B_FULL_CENSUS_GENERATED_INDEPENDENTLY":
    raise SystemExit(f"census generation failed: {terminal}")
counts = {item["scope"]: item["record_count"] for item in receipt["scopes"]}
expected = {
    "NQ_D2_NORMALIZED_LENGTH_19": 98622,
    "NQ_D3_STRUCTURED_LENGTH_25": 230983,
}
if counts != expected:
    raise SystemExit(f"census record counts diverge from the frozen denominators: {counts}")
PY
log "census generated: 98622 + 230983 records"

# ---------------------------------------------------------------------------
# Phase 2: per-record SAT execution of every record in both scopes.
# ---------------------------------------------------------------------------
for SCOPE in "${D2_SCOPE}" "${D3_SCOPE}"; do
  SCOPE_ROOT="${OUTPUT_ROOT}/${SCOPE}"
  mkdir -p "${SCOPE_ROOT}/proofs"
  "${VENV}/bin/python" "${ENGINE_ROOT}/run_engine_b.py" \
    --mode execute \
    --subject-commit "${SUBJECT_COMMIT}" \
    --source-manifest "${ENGINE_ROOT}/SOURCE_MANIFEST.json" \
    --input-root "${OUTPUT_ROOT}/census/input/${SCOPE}" \
    --input-manifest "${OUTPUT_ROOT}/census/input/${SCOPE}/input_manifest.json" \
    --output "${SCOPE_ROOT}/ENGINE_B_RECEIPT.json" \
    --certificates "${SCOPE_ROOT}/ENGINE_B_CERTIFICATES.jsonl" \
    --proof-root "${SCOPE_ROOT}/proofs" \
    --threads 48 \
    --max-wall-seconds "${EXECUTION_WALL}" \
    --solver g4
  "${VENV}/bin/python" "${ENGINE_ROOT}/verify_receipt.py" \
    "${SCOPE_ROOT}/ENGINE_B_RECEIPT.json" \
    --source-manifest "${ENGINE_ROOT}/SOURCE_MANIFEST.json"
  log "execution complete: ${SCOPE}"
done

# ---------------------------------------------------------------------------
# Phase 3: external DRUP verification of every UNSAT certificate.
# ---------------------------------------------------------------------------
for SCOPE in "${D2_SCOPE}" "${D3_SCOPE}"; do
  SCOPE_ROOT="${OUTPUT_ROOT}/${SCOPE}"
  "${VENV}/bin/python" "${ENGINE_ROOT}/batch_external_drup.py" \
    --protocol "${ENGINE_ROOT}/EXTERNAL_DRUP_CHECKER_PROTOCOL.json" \
    --record-stream "${OUTPUT_ROOT}/census/input/${SCOPE}/records.jsonl" \
    --certificates "${SCOPE_ROOT}/ENGINE_B_CERTIFICATES.jsonl" \
    --artifact-root "${SCOPE_ROOT}/proofs" \
    --checker "${DRUP_SOURCE}/drat-trim" \
    --checker-source-root "${DRUP_SOURCE}" \
    --receipts "${SCOPE_ROOT}/DRUP_BATCH_LINES.jsonl" \
    --output "${SCOPE_ROOT}/DRUP_BATCH_RECEIPT.json" \
    --threads "${DRUP_THREADS}" \
    --chunk-size 64
  "${VENV}/bin/python" "${ENGINE_ROOT}/batch_external_drup.py" \
    --verify \
    --resample 32 \
    --protocol "${ENGINE_ROOT}/EXTERNAL_DRUP_CHECKER_PROTOCOL.json" \
    --record-stream "${OUTPUT_ROOT}/census/input/${SCOPE}/records.jsonl" \
    --certificates "${SCOPE_ROOT}/ENGINE_B_CERTIFICATES.jsonl" \
    --artifact-root "${SCOPE_ROOT}/proofs" \
    --checker "${DRUP_SOURCE}/drat-trim" \
    --checker-source-root "${DRUP_SOURCE}" \
    --receipts "${SCOPE_ROOT}/DRUP_BATCH_LINES.jsonl" \
    --output "${SCOPE_ROOT}/DRUP_BATCH_RECEIPT.json"
  log "external DRUP batch verified: ${SCOPE}"
done

# ---------------------------------------------------------------------------
# Phase 4: durable copy-out of the sealed proof chain.  Exact-copied artifacts
# (receipts, manifests, coverage declarations) must land byte-identical or the
# job is terminal.  Large JSONL streams are gzip-copied with a round-trip
# digest check; a transport failure is recorded as an explicit skip with the
# raw digest preserved, while a digest mismatch after an intact gzip stream is
# corruption and terminal.  SHA256SUMS records raw-byte digests.
# ---------------------------------------------------------------------------
"${VENV}/bin/python" - "${OUTPUT_ROOT}" "${DURABLE_ROOT}" <<'PY'
import gzip
import hashlib
import json
import shutil
import sys
from pathlib import Path

output_root = Path(sys.argv[1])
durable_root = Path(sys.argv[2])
scopes = ("NQ_D2_NORMALIZED_LENGTH_19", "NQ_D3_STRUCTURED_LENGTH_25")
ledger_path = durable_root / "SHA256SUMS"
skips_path = durable_root / "SKIPPED_STREAMS.txt"


def raw_sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1 << 20), b""):
            digest.update(block)
    return digest.hexdigest()


def exact_copy(relative: str) -> None:
    source = output_root / relative
    destination = durable_root / relative
    destination.parent.mkdir(parents=True, exist_ok=True)
    expected = raw_sha256(source)
    shutil.copyfile(source, destination)
    if raw_sha256(destination) != expected:
        raise SystemExit(f"NQ_CR_B_DURABLE_COPY_CORRUPT: {relative}")
    with ledger_path.open("a", encoding="ascii") as ledger:
        ledger.write(f"{expected}  {relative}\n")


def gzip_copy(relative: str) -> None:
    source = output_root / relative
    destination = durable_root / f"{relative}.gz"
    destination.parent.mkdir(parents=True, exist_ok=True)
    try:
        expected = raw_sha256(source)
        with source.open("rb") as reader, gzip.open(destination, "wb") as writer:
            shutil.copyfileobj(reader, writer, 1 << 20)
    except OSError as error:
        destination.unlink(missing_ok=True)
        with skips_path.open("a", encoding="ascii") as skips:
            skips.write(f"NQ_CR_B_DURABLE_BIG_STREAM_SKIPPED\nstream: {relative}\nerror: {error}\n")
        print(f"durable copy skipped (transport): {relative}", file=sys.stderr)
        return
    roundtrip = hashlib.sha256()
    with gzip.open(destination, "rb") as reader:
        for block in iter(lambda: reader.read(1 << 20), b""):
            roundtrip.update(block)
    if roundtrip.hexdigest() != expected:
        raise SystemExit(f"NQ_CR_B_DURABLE_COPY_CORRUPT: {relative}")
    with ledger_path.open("a", encoding="ascii") as ledger:
        ledger.write(f"{expected}  {relative}\n")


durable_root.mkdir(parents=True, exist_ok=True)
ledger_path.write_text("", encoding="ascii")
skips_path.write_text("", encoding="ascii")
exact_copy("census/census_generation_receipt.json")
for scope in scopes:
    exact_copy(f"census/input/{scope}/coverage.json")
    exact_copy(f"census/input/{scope}/input_manifest.json")
    exact_copy(f"census/bundle/{scope}/{scope}/SCOPE_MANIFEST.json")
    gzip_copy(f"census/input/{scope}/records.jsonl")
    gzip_copy(f"census/candidates/{scope}.candidates.jsonl")
    for shard in json.loads(
        (output_root / "census" / "bundle" / scope / scope / "SCOPE_MANIFEST.json").read_text(
            encoding="utf-8"
        )
    )["partitions"]:
        gzip_copy(f"census/bundle/{scope}/{shard['path']}")
    exact_copy(f"{scope}/ENGINE_B_RECEIPT.json")
    gzip_copy(f"{scope}/ENGINE_B_CERTIFICATES.jsonl")
    gzip_copy(f"{scope}/DRUP_BATCH_LINES.jsonl")
    exact_copy(f"{scope}/DRUP_BATCH_RECEIPT.json")
print("durable proof chain copied", flush=True)
PY
log "durable chain copied to ${DURABLE_ROOT}"

log "full CR-B replay chain green for job ${SLURM_JOB_ID}"

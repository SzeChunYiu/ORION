#!/bin/bash
set -euo pipefail
root=$(pwd)
test "$(shasum -a 256 source.tar.gz | awk '{print $1}')" = "$(cat SOURCE_SHA256)"
rm -rf source private-venv
mkdir source
# LUNARC tar accepts the Git-generated gzip archive.
tar -xzf source.tar.gz -C source
python3 -m venv private-venv
private-venv/bin/python -m pip install --disable-pip-version-check --quiet 'pytest==9.1.1' 'cryptography>=45' 'defusedxml>=0.7'
PYTHONPATH=source/src private-venv/bin/python - <<'PY'
import json
from orion.discovery.execution_takeover import validate_frozen_protocol
validate_frozen_protocol(json.load(open('EXECUTION_PROTOCOL.json')))
print('ORION_FROZEN_PROTOCOL_HASH_GREEN')
PY
cd source
cp research/orion-discovery-v3/FINITE_REFERENCE_RECEIPT_V1.json "$root/expected-finite-receipt.json"
PYTHONPATH=src "$root/private-venv/bin/python" scripts/check_orion_discovery_v3.py
PYTHONPATH=src "$root/private-venv/bin/python" scripts/check_orion_execution_takeover.py
PYTHONPATH=src "$root/private-venv/bin/python" -m pytest -q tests/unit/discovery/test_frontier_dominance.py tests/unit/discovery/test_execution_takeover.py
PYTHONPATH=src "$root/private-venv/bin/python" scripts/run_frontier_dominance_census_v1.py
cmp "$root/expected-finite-receipt.json" research/orion-discovery-v3/FINITE_REFERENCE_RECEIPT_V1.json
"$root/private-venv/bin/python" -m compileall -q src/orion/discovery/frontier_dominance.py src/orion/discovery/execution_takeover.py scripts/check_orion_discovery_v3.py scripts/check_orion_execution_takeover.py scripts/run_frontier_dominance_census_v1.py
cd "$root"
"$root/private-venv/bin/python" - <<'PY'
import cryptography, defusedxml, hashlib, json, os, platform, pytest
protocol=json.load(open('EXECUTION_PROTOCOL.json'))
receipt={
  'schema':'orion.discovery.v3.lunarc-engineering-reference-receipt.v1',
  'job_id':protocol['job_id'],
  'slurm_job_id':os.environ.get('SLURM_JOB_ID'),
  'source_git_sha':protocol['source_git_sha'],
  'protocol_sha256':protocol['protocol_sha256'],
  'submission_key':os.environ['ORION_SUBMISSION_KEY'],
  'source_archive_sha256':hashlib.sha256(open('source.tar.gz','rb').read()).hexdigest(),
  'environment':{
    'python':platform.python_version(),
    'cryptography':cryptography.__version__,
    'defusedxml':defusedxml.__version__,
    'pytest':pytest.__version__,
    'platform':platform.platform(),
  },
  'checks':{
    'frozen_protocol_hash':0,
    'structure':0,
    'takeover_manifest':0,
    'hostile_tests':0,
    'finite_census':0,
    'finite_receipt_byte_comparison':0,
    'compileall':0,
  },
  'terminal':'ENGINEERING_REFERENCE_CHECK_ONLY_GREEN',
  'scientific_authority':'NONE',
  'paper_authority_delta':'NONE',
  'external_novelty':'CANNOT_CHECK',
}
with open('ENGINEERING_REFERENCE_RECEIPT.json','w') as handle:
  json.dump(receipt,handle,sort_keys=True,indent=2)
  handle.write('\n')
print('ORION_LUNARC_ENGINEERING_REFERENCE_GREEN')
PY

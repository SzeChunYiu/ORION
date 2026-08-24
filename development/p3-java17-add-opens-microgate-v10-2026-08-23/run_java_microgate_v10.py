from __future__ import annotations
import datetime as dt
import hashlib
import json
import os
from pathlib import Path
import stat
import subprocess
import time

ROOT=Path(__file__).resolve().parent
PROTOCOL_PATH=ROOT/"PROTOCOL_V10.json"
LOCK=ROOT/"ATTEMPT_LOCK_V10.json"
RECEIPT=ROOT/"RECEIPT_V10.json"
STDOUT=ROOT/"JAVA_STDOUT_V10.log"
STDERR=ROOT/"JAVA_STDERR_V10.log"
TERMINAL=ROOT/"TERMINAL_V10.txt"

def sha256(p: Path)->str:
    h=hashlib.sha256()
    with p.open("rb") as f:
        for chunk in iter(lambda:f.read(1024*1024),b""):
            h.update(chunk)
    return h.hexdigest()

def regular_non_symlink(p: Path)->bool:
    try:
        s=p.lstat()
    except FileNotFoundError:
        return False
    return stat.S_ISREG(s.st_mode) and not p.is_symlink()

def now()->str:
    return dt.datetime.now(dt.timezone.utc).isoformat()

if LOCK.exists() or RECEIPT.exists():
    raise SystemExit("REFUSE_RERUN: V10 single-attempt lock or receipt already exists")
protocol=json.loads(PROTOCOL_PATH.read_text())
observed={}
for name,spec in protocol["frozen_inputs"].items():
    p=Path(spec["path"])
    digest=sha256(p)
    observed[name]={"path":str(p),"sha256":digest,"bytes":p.stat().st_size,"matches_v9_frozen_hash":digest==spec["sha256"]}
if not all(x["matches_v9_frozen_hash"] for x in observed.values()):
    raise SystemExit("FROZEN_INPUT_HASH_MISMATCH: Java child not launched")
started_at=now()
LOCK.write_text(json.dumps({
    "schema_version":"orion.p3.java17-add-opens-repair-microgate.attempt-lock.v10",
    "protocol_sha256":sha256(PROTOCOL_PATH),
    "started_at":started_at,
    "authorized_java_child_invocations":1,
    "retries_permitted":0
},indent=2,sort_keys=True)+"\n")
command=protocol["command"]
start_ns=time.monotonic_ns()
timed_out=False
try:
    completed=subprocess.run(command,cwd=ROOT,stdout=subprocess.PIPE,stderr=subprocess.PIPE,timeout=protocol["single_authorized_attempt"]["timeout_seconds"],check=False)
    exit_code=completed.returncode
    stdout=completed.stdout
    stderr=completed.stderr
except subprocess.TimeoutExpired as exc:
    timed_out=True
    exit_code=None
    stdout=exc.stdout or b""
    stderr=exc.stderr or b""
wall_ns=time.monotonic_ns()-start_ns
STDOUT.write_bytes(stdout)
STDERR.write_bytes(stderr)
required=Path(protocol["success_gate"]["required_output"])
regular=regular_non_symlink(required)
output={"path":str(required),"present":required.exists(),"regular_non_symlink":regular,"bytes":required.stat().st_size if regular else None,"sha256":sha256(required) if regular else None}
success=(exit_code==0 and regular and not timed_out)
if success:
    terminal="P3_V10_JAVA17_ADD_OPENS_REPAIR_MICROGATE_PASS__DIRECT_CHILD_EXIT_ZERO__REGULAR_REPAIRED_MAPPING_OUTPUT_PRESENT__NO_RETRY__FULL_NATIVE_SUCCESSOR_AUTHORIZED"
else:
    terminal="P3_V10_JAVA17_ADD_OPENS_REPAIR_MICROGATE_FAIL__DIRECT_CHILD_EXIT_OR_REGULAR_OUTPUT_GATE_NOT_SATISFIED__NO_RETRY__FULL_NATIVE_SUCCESSOR_NOT_AUTHORIZED"
receipt={
 "schema_version":"orion.p3.java17-add-opens-repair-microgate.receipt.v10",
 "protocol_id":protocol["protocol_id"],
 "authority":protocol["authority"],
 "protocol_sha256":sha256(PROTOCOL_PATH),
 "started_at":started_at,
 "finished_at":now(),
 "command":command,
 "cwd":str(ROOT),
 "frozen_inputs_observed":observed,
 "java_child_invocations":1,
 "direct_child_exit_code":exit_code,
 "timed_out":timed_out,
 "timeout_seconds":protocol["single_authorized_attempt"]["timeout_seconds"],
 "retries_used":0,
 "wall_nanoseconds":wall_ns,
 "wall_seconds":wall_ns/1_000_000_000,
 "stdout":{"path":str(STDOUT),"bytes":len(stdout),"sha256":sha256(STDOUT)},
 "stderr":{"path":str(STDERR),"bytes":len(stderr),"sha256":sha256(STDERR),"retained_exactly":True},
 "required_output":output,
 "success_gate":{"direct_child_exit_zero":exit_code==0,"regular_non_symlink_output":regular},
 "success":success,
 "gold_or_reference_alignment_opened":False,
 "scientific_scoring_performed":False,
 "full_deeponto_or_bertmap_run":False,
 "terminal":terminal
}
RECEIPT.write_text(json.dumps(receipt,indent=2,sort_keys=True)+"\n")
TERMINAL.write_text(terminal+"\n")
print(json.dumps({"terminal":terminal,"direct_child_exit_code":exit_code,"wall_seconds":receipt["wall_seconds"],"required_output":output,"stderr_sha256":receipt["stderr"]["sha256"]},indent=2))
raise SystemExit(0 if success else 1)

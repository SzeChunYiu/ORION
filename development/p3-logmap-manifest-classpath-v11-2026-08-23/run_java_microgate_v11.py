from __future__ import annotations
import datetime as dt
import hashlib
import json
from pathlib import Path
import stat
import subprocess
import time
ROOT=Path(__file__).resolve().parent
PROTOCOL_PATH=ROOT/'PROTOCOL_V11.json'; PREFLIGHT=ROOT/'CLOSURE_PREFLIGHT_V11.json'; LOCK=ROOT/'ATTEMPT_LOCK_V11.json'; RECEIPT=ROOT/'RECEIPT_V11.json'; STDOUT=ROOT/'JAVA_STDOUT_V11.log'; STDERR=ROOT/'JAVA_STDERR_V11.log'; TERMINAL=ROOT/'TERMINAL_V11.txt'
def sha(p:Path)->str:
 h=hashlib.sha256()
 with p.open('rb') as f:
  for c in iter(lambda:f.read(1024*1024),b''): h.update(c)
 return h.hexdigest()
def regular_non_symlink(p:Path)->bool:
 try:s=p.lstat()
 except FileNotFoundError:return False
 return stat.S_ISREG(s.st_mode) and not p.is_symlink()
def now()->str:return dt.datetime.now(dt.timezone.utc).isoformat()
if LOCK.exists() or RECEIPT.exists():raise SystemExit('REFUSE_RERUN: V11 single-attempt lock or receipt exists')
protocol=json.loads(PROTOCOL_PATH.read_text()); closure=json.loads(PREFLIGHT.read_text())
if sha(PREFLIGHT)!=protocol['closure_preflight']['sha256']:raise SystemExit('CLOSURE_PREFLIGHT_HASH_MISMATCH: Java not launched')
if not closure['complete_exact_closure'] or closure['manifest_class_path_entries_matching_v9']!=90:raise SystemExit('CLOSURE_NOT_EXACT_90_OF_90: Java not launched')
closure_observed=[]
for row in closure['entries']:
 p=ROOT/'runtime'/row['manifest_path']; digest=sha(p)
 closure_observed.append({'path':str(p),'sha256':digest,'bytes':p.stat().st_size,'matches_v9_sbom':digest==row['expected_sha256'] and p.stat().st_size==row['expected_bytes']})
if len(closure_observed)!=90 or not all(x['matches_v9_sbom'] for x in closure_observed):raise SystemExit('LIVE_CLOSURE_HASH_MISMATCH: Java not launched')
observed={}
for name,spec in protocol['frozen_inputs'].items():
 p=Path(spec['path']); digest=sha(p); observed[name]={'path':str(p),'sha256':digest,'bytes':p.stat().st_size,'matches_v9_frozen_hash':digest==spec['sha256']}
if not all(x['matches_v9_frozen_hash'] for x in observed.values()):raise SystemExit('FROZEN_INPUT_HASH_MISMATCH: Java not launched')
started=now(); LOCK.write_text(json.dumps({'schema_version':'orion.p3.logmap-manifest-classpath.attempt-lock.v11','protocol_sha256':sha(PROTOCOL_PATH),'closure_preflight_sha256':sha(PREFLIGHT),'started_at':started,'authorized_java_child_invocations':1,'retries_permitted':0},indent=2,sort_keys=True)+'\n')
start_ns=time.monotonic_ns(); timed_out=False
try:
 completed=subprocess.run(protocol['command'],cwd=ROOT,stdout=subprocess.PIPE,stderr=subprocess.PIPE,timeout=protocol['single_authorized_attempt']['timeout_seconds'],check=False); exit_code=completed.returncode; stdout=completed.stdout; stderr=completed.stderr
except subprocess.TimeoutExpired as exc:
 timed_out=True; exit_code=None; stdout=exc.stdout or b''; stderr=exc.stderr or b''
wall_ns=time.monotonic_ns()-start_ns; STDOUT.write_bytes(stdout); STDERR.write_bytes(stderr)
required=Path(protocol['success_gate']['required_output']); regular=regular_non_symlink(required); output={'path':str(required),'present':required.exists(),'regular_non_symlink':regular,'bytes':required.stat().st_size if regular else None,'sha256':sha(required) if regular else None}
success=exit_code==0 and regular and not timed_out
terminal='P3_V11_EXACT_V9_CLASSPATH_90_OF_90_PASS__JAVA17_ADD_OPENS_REPAIR_MICROGATE_PASS__DIRECT_CHILD_EXIT_ZERO__REGULAR_REPAIRED_MAPPING_OUTPUT_PRESENT__NO_RETRY__FULL_NATIVE_SUCCESSOR_AUTHORIZED' if success else 'P3_V11_EXACT_V9_CLASSPATH_90_OF_90_PASS__JAVA17_ADD_OPENS_REPAIR_MICROGATE_FAIL__DIRECT_CHILD_EXIT_OR_REGULAR_OUTPUT_GATE_NOT_SATISFIED__NO_RETRY__FULL_NATIVE_SUCCESSOR_NOT_AUTHORIZED'
receipt={'schema_version':'orion.p3.logmap-manifest-classpath.repair-microgate.receipt.v11','protocol_id':protocol['protocol_id'],'authority':protocol['authority'],'protocol_sha256':sha(PROTOCOL_PATH),'closure_preflight_sha256':sha(PREFLIGHT),'started_at':started,'finished_at':now(),'command':protocol['command'],'cwd':str(ROOT),'closure_entries_live_verified':'90/90','frozen_inputs_observed':observed,'java_child_invocations':1,'direct_child_exit_code':exit_code,'timed_out':timed_out,'timeout_seconds':protocol['single_authorized_attempt']['timeout_seconds'],'retries_used':0,'wall_nanoseconds':wall_ns,'wall_seconds':wall_ns/1_000_000_000,'stdout':{'path':str(STDOUT),'bytes':len(stdout),'sha256':sha(STDOUT)},'stderr':{'path':str(STDERR),'bytes':len(stderr),'sha256':sha(STDERR),'retained_exactly':True},'required_output':output,'success_gate':{'direct_child_exit_zero':exit_code==0,'regular_non_symlink_output':regular},'success':success,'gold_or_reference_alignment_opened':False,'scientific_scoring_performed':False,'full_deeponto_or_bertmap_run':False,'terminal':terminal}
RECEIPT.write_text(json.dumps(receipt,indent=2,sort_keys=True)+'\n'); TERMINAL.write_text(terminal+'\n')
print(json.dumps({'terminal':terminal,'direct_child_exit_code':exit_code,'wall_seconds':receipt['wall_seconds'],'required_output':output,'stderr_sha256':receipt['stderr']['sha256']},indent=2)); raise SystemExit(0 if success else 1)

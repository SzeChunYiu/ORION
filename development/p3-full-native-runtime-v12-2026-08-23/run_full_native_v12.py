#!/usr/bin/env python3
from __future__ import annotations
import csv,datetime as dt,hashlib,json,os,re,signal,stat,subprocess,time
from collections import Counter
from pathlib import Path
ROOT=Path(__file__).resolve().parent
PROTOCOL=ROOT/'PROTOCOL_V12.json'; PREFLIGHT=ROOT/'RUNTIME_PREFLIGHT_V12.json'; LOCK=ROOT/'NATIVE_ATTEMPT_LOCK_V12.json'; RECEIPT=ROOT/'NATIVE_EXECUTION_RECEIPT_V12.json'; STDOUT=ROOT/'NATIVE_STDOUT_V12.log'; STDERR=ROOT/'NATIVE_STDERR_V12.log'; PARSER_RECEIPT=ROOT/'NATIVE_ARTIFACT_CONTRACT_V12.json'; PARSER_STDOUT=ROOT/'PARSER_STDOUT_V12.log'; PARSER_STDERR=ROOT/'PARSER_STDERR_V12.log'; LEXICAL=ROOT/'LEXICAL_SEMANTICS_AUDIT_V12.json'; TERMINAL=ROOT/'TERMINAL_V12.txt'
PYTHON=ROOT/'runtime/venv/bin/python'; MATCH=ROOT/'runtime/results/bertmap-out/bertmap/match'; REQUIRED=['raw_mappings.json','raw_mappings.tsv','extended_mappings.tsv','filtered_mappings.tsv','repaired_mappings.tsv']
def sha(p:Path)->str:
 h=hashlib.sha256()
 with p.open('rb') as f:
  for c in iter(lambda:f.read(1024*1024),b''):h.update(c)
 return h.hexdigest()
def now()->str:return dt.datetime.now(dt.timezone.utc).isoformat()
def regular(p:Path)->bool:
 try:s=p.lstat()
 except FileNotFoundError:return False
 return stat.S_ISREG(s.st_mode) and not p.is_symlink()
def terminate(proc):
 try:os.killpg(proc.pid,signal.SIGTERM);proc.wait(timeout=10)
 except (ProcessLookupError,subprocess.TimeoutExpired):
  try:os.killpg(proc.pid,signal.SIGKILL)
  except ProcessLookupError:pass
  proc.wait()
def inventory():
 out={}
 for name in REQUIRED:
  p=MATCH/name;ok=regular(p);out[name]={'path':str(p),'regular_non_symlink':ok,'bytes':p.stat().st_size if ok else None,'sha256':sha(p) if ok else None}
 return out
def read_tsv(p:Path,header:bool):
 with p.open(newline='') as f:rows=list(csv.reader(f,delimiter='\t',strict=True))
 return rows[1:] if header and rows else rows
def lexical_audit():
 raw=MATCH/'logmap-repair/mappings_repaired_with_LogMap.tsv'; final=MATCH/'repaired_mappings.tsv'; uni=json.loads((ROOT/'UNIVERSE_MANIFEST_V12.json').read_text()); src=set(uni['expected_source_iris']);tgt=set(uni['expected_target_iris'])
 if not regular(raw) or not regular(final):
  out={'schema_version':'orion.p3.full-native-runtime.lexical-semantics-audit.v12','authority':'EXACT_LEXICAL_MEMBERSHIP_AND_TRANSPORT_ONLY__NO_MAPPING_TRUTH_AUTHORITY','normalization_applied':False,'pass':False,'error':'required raw LogMap or final repaired TSV absent','terminal':'CANNOT_CHECK_LEXICAL_SEMANTICS_ARTIFACT_ABSENT'};LEXICAL.write_text(json.dumps(out,indent=2,sort_keys=True)+'\n');return out
 rawrows=read_tsv(raw,False);finalrows=read_tsv(final,True);three_raw=[x for x in rawrows if len(x)==3];three_final=[x for x in finalrows if len(x)==3]
 exact_src=sum(x[0] in src for x in three_final);exact_tgt=sum(x[1] in tgt for x in three_final);opt_src=sum(x[0].startswith('Optional.of(') for x in three_final);opt_tgt=sum(x[1].startswith('Optional.of(') for x in three_final);transport=Counter(map(tuple,three_raw))==Counter(map(tuple,three_final));passed=len(three_final)==len(finalrows) and exact_src==len(finalrows) and exact_tgt==len(finalrows) and transport
 out={'schema_version':'orion.p3.full-native-runtime.lexical-semantics-audit.v12','authority':'EXACT_LEXICAL_MEMBERSHIP_AND_TRANSPORT_ONLY__NO_MAPPING_TRUTH_AUTHORITY','normalization_applied':False,'raw_logmap_rows':len(rawrows),'final_repaired_rows':len(finalrows),'final_three_field_rows':len(three_final),'exact_source_universe_members':exact_src,'exact_target_universe_members':exact_tgt,'source_optional_wrapper_rows':opt_src,'target_optional_wrapper_rows':opt_tgt,'raw_to_final_exact_row_multiset_equal':transport,'pass':passed,'failure_reason':None if passed else 'Final repaired entity strings are not exact frozen-universe IRIs; Optional.of wrappers violate downstream lexical membership.' if opt_src or opt_tgt else 'Final repaired entity strings violate exact frozen-universe membership.','terminal':'PASS_EXACT_DOWNSTREAM_LEXICAL_SEMANTICS' if passed else 'FAIL_OPTIONAL_WRAPPER_DOWNSTREAM_LEXICAL_SEMANTICS'}
 LEXICAL.write_text(json.dumps(out,indent=2,sort_keys=True)+'\n');return out
if any(p.exists() for p in [LOCK,RECEIPT,STDOUT,STDERR,PARSER_RECEIPT,LEXICAL,TERMINAL]):raise SystemExit('REFUSE_RERUN_OR_STALE_EXECUTION_ARTIFACT')
protocol=json.loads(PROTOCOL.read_text());pre=json.loads(PREFLIGHT.read_text())
if sha(PROTOCOL)!=pre['protocol_sha256'] or not pre['native_execution_authorized'] or pre['checks_passed']!=pre['checks_total']:raise SystemExit('PREFLIGHT_NOT_AUTHORIZED')
if MATCH.exists() or any((ROOT/'runtime/results').iterdir()):raise SystemExit('OUTPUT_NOT_EMPTY_PRELAUNCH')
# Recheck the launch-critical identities after frozen preflight.
for spec in protocol['frozen_inputs'].values():
 p=Path(spec['path']);expected=spec['sha256']
 if not regular(p) or sha(p)!=expected:raise SystemExit('LAUNCH_IDENTITY_DRIFT:'+str(p))
if sha(Path(protocol['frozen_runtime']['java']['binary']))!=protocol['frozen_runtime']['java']['binary_sha256']:raise SystemExit('JAVA_IDENTITY_DRIFT')
if sha(ROOT/'runtime/model/pytorch_model.bin')!=protocol['frozen_runtime']['model_weight_sha256']:raise SystemExit('MODEL_IDENTITY_DRIFT')
if sha(ROOT/'runtime/venv/lib/python3.10/site-packages/deeponto/align/mapping.py')!=protocol['frozen_runtime']['installed_mapping_sha256']:raise SystemExit('TABLE_READER_IDENTITY_DRIFT')
if sha(ROOT/'runtime/venv/lib/python3.10/site-packages/deeponto/utils/file_utils.py')!=protocol['frozen_runtime']['installed_file_utils_sha256']:raise SystemExit('RUNTIME_ADAPTER_IDENTITY_DRIFT')
started=now();LOCK.write_text(json.dumps({'schema_version':'orion.p3.full-native-runtime.attempt-lock.v12','protocol_sha256':sha(PROTOCOL),'preflight_sha256':sha(PREFLIGHT),'started_at':started,'native_attempts_authorized':1,'retries_permitted':0,'command':protocol['command']},indent=2,sort_keys=True)+'\n')
home=ROOT/'runtime/home';cache=ROOT/'runtime/cache/native';tmp=ROOT/'runtime/tmp'
for p in [home,cache,tmp,cache/'xdg',cache/'huggingface',cache/'huggingface/hub',cache/'transformers',cache/'torch']:p.mkdir(parents=True,exist_ok=True)
env={'PATH':f"{PYTHON.parent}:{Path(protocol['frozen_runtime']['java']['binary']).parent}:/usr/bin:/bin:/usr/sbin:/sbin",'HOME':str(home),'XDG_CACHE_HOME':str(cache/'xdg'),'HF_HOME':str(cache/'huggingface'),'HF_HUB_CACHE':str(cache/'huggingface/hub'),'TRANSFORMERS_CACHE':str(cache/'transformers'),'TORCH_HOME':str(cache/'torch'),'TMPDIR':str(tmp),'PYTHONNOUSERSITE':'1','PYTHONUNBUFFERED':'1','JAVA_HOME':str(Path(protocol['frozen_runtime']['java']['binary']).parent.parent),'LANG':'C.UTF-8','LC_ALL':'C',**protocol['attempt']['offline_guards']}
start_ns=time.monotonic_ns();timed_out=False;launch_error=None
try:
 proc=subprocess.Popen(protocol['command'],cwd=ROOT,env=env,stdin=subprocess.PIPE,stdout=subprocess.PIPE,stderr=subprocess.PIPE,start_new_session=True)
 try:stdout,stderr=proc.communicate(b'2g\n',timeout=protocol['attempt']['timeout_seconds'])
 except subprocess.TimeoutExpired:timed_out=True;terminate(proc);stdout,stderr=proc.communicate()
 exit_code=proc.returncode
except Exception as exc:
 stdout=b'';stderr=b'';exit_code=None;launch_error=f'{type(exc).__name__}: {exc}'
wall_ns=time.monotonic_ns()-start_ns;STDOUT.write_bytes(stdout);STDERR.write_bytes(stderr);text=stdout.decode('utf-8',errors='replace');direct_codes=[int(x) for x in re.findall(r'^ORION_LOGMAP_DIRECT_CHILD_EXIT_CODE=(-?\d+)$',text,re.M)];effective=[x for x in text.splitlines() if x.startswith('ORION_LOGMAP_EFFECTIVE_COMMAND=')]
artifacts=inventory();five=all(x['regular_non_symlink'] for x in artifacts.values());direct_ok=direct_codes==[0] and len(effective)==1 and effective[0].count('--add-opens=java.base/java.lang=ALL-UNNAMED')==1 and '--add-opens=' not in effective[0].replace('--add-opens=java.base/java.lang=ALL-UNNAMED','')
native_success=exit_code==0 and not timed_out and launch_error is None and five and direct_ok
# Frozen structural parser is run once after native execution; its adverse result does not alter files.
parser_command=[str(PYTHON),str(ROOT/'bertmap_native_parser_v7.py'),'--output-dir',str(MATCH),'--manifest',str(ROOT/'UNIVERSE_MANIFEST_V12.json'),'--write-receipt',str(PARSER_RECEIPT)]
parser_exit=None
if five:
 try:
  pc=subprocess.run(parser_command,cwd=ROOT,env=env,capture_output=True,timeout=120,check=False);parser_exit=pc.returncode;PARSER_STDOUT.write_bytes(pc.stdout);PARSER_STDERR.write_bytes(pc.stderr)
 except Exception as exc:PARSER_STDOUT.write_text('');PARSER_STDERR.write_text(f'{type(exc).__name__}: {exc}\n')
else:PARSER_STDOUT.write_text('');PARSER_STDERR.write_text('parser skipped: five-artifact gate failed\n')
parser_result=json.loads(PARSER_RECEIPT.read_text()) if PARSER_RECEIPT.is_file() else {}
lex=lexical_audit()
if native_success and lex.get('pass') and parser_exit==0:terminal='P3_V12_SINGLE_FULL_NATIVE_ATTEMPT_PASS__DIRECT_LOGMAP_CHILD_EXIT_ZERO__FIVE_OF_FIVE_REGULAR_ARTIFACTS__LEXICAL_AND_STRUCTURAL_CONTRACT_PASS__NO_RETRY__NATIVE_READINESS_THREE_OF_THREE'
elif native_success and not lex.get('pass'):terminal='P3_V12_SINGLE_FULL_NATIVE_ATTEMPT_PASS__DIRECT_LOGMAP_CHILD_EXIT_ZERO__FIVE_OF_FIVE_REGULAR_ARTIFACTS__OPTIONAL_WRAPPER_LEXICAL_SEMANTICS_FAIL__STRUCTURAL_PARSER_CANNOT_CHECK__NO_RETRY__NATIVE_READINESS_THREE_OF_THREE__SCIENTIFIC_READINESS_ZERO_OF_THREE'
else:terminal='P3_V12_SINGLE_FULL_NATIVE_ATTEMPT_FAIL__DIRECT_LOGMAP_OR_FIVE_ARTIFACT_GATE_NOT_SATISFIED__NO_RETRY__NATIVE_READINESS_NOT_PROMOTED'
receipt={'schema_version':'orion.p3.full-native-runtime.execution-receipt.v12','protocol_id':protocol['protocol_id'],'authority':protocol['authority'],'protocol_sha256':sha(PROTOCOL),'preflight_sha256':sha(PREFLIGHT),'started_at':started,'finished_at':now(),'command':protocol['command'],'cwd':str(ROOT),'environment':env,'stdin_utf8':'2g\\n','native_attempts':1,'retries_used':0,'timeout_seconds':protocol['attempt']['timeout_seconds'],'timed_out':timed_out,'launch_error':launch_error,'native_exit_code':exit_code,'wall_nanoseconds':wall_ns,'wall_seconds':wall_ns/1e9,'stdout':{'path':str(STDOUT),'bytes':len(stdout),'sha256':sha(STDOUT)},'stderr':{'path':str(STDERR),'bytes':len(stderr),'sha256':sha(STDERR),'retained_exactly':True},'direct_logmap_child':{'observed_exit_codes':direct_codes,'effective_command_lines':effective,'propagated_zero':direct_ok},'artifacts':artifacts,'five_regular_non_symlink_artifacts':five,'native_success_gate_pass':native_success,'parser':{'command':parser_command,'exit_code':parser_exit,'receipt':parser_result,'receipt_sha256':sha(PARSER_RECEIPT) if PARSER_RECEIPT.is_file() else None,'stdout_sha256':sha(PARSER_STDOUT),'stderr_sha256':sha(PARSER_STDERR)},'lexical_audit':lex,'lexical_audit_sha256':sha(LEXICAL),'gold_or_reference_opened':False,'protected_outcome_opened':False,'scientific_scoring_performed':False,'terminal':terminal}
RECEIPT.write_text(json.dumps(receipt,indent=2,sort_keys=True)+'\n');TERMINAL.write_text(terminal+'\n');print(json.dumps({'terminal':terminal,'native_exit_code':exit_code,'direct_logmap_child_exit_codes':direct_codes,'five_regular_artifacts':five,'wall_seconds':receipt['wall_seconds'],'parser_exit_code':parser_exit,'parser_terminal':parser_result.get('terminal'),'lexical_terminal':lex.get('terminal'),'artifacts':artifacts},indent=2));raise SystemExit(0 if native_success else 1)

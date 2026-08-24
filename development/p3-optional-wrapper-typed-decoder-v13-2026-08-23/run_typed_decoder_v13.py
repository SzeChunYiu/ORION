#!/usr/bin/env python3
from __future__ import annotations
import csv,datetime as dt,hashlib,json,os,re,shutil,stat,subprocess,sys,time
from pathlib import Path
ROOT=Path(__file__).resolve().parent;PROTOCOL=ROOT/'PROTOCOL_V13.json';LOCK=ROOT/'ATTEMPT_LOCK_V13.json';RECEIPT=ROOT/'RECEIPT_V13.json';MICRO=ROOT/'ADVERSARIAL_MICROCASES_V13.json';PARSER_RECEIPT=ROOT/'PARSER_RECEIPT_V13.json';PARSER_STDOUT=ROOT/'PARSER_STDOUT_V13.log';PARSER_STDERR=ROOT/'PARSER_STDERR_V13.log';TERMINAL=ROOT/'TERMINAL_V13.txt';OUT=ROOT/'runtime/decoded-match';ORIGINAL=ROOT/'ORIGINAL_WRAPPED_REPAIRED_MAPPINGS_V12.tsv'
def sha(p:Path)->str:
 h=hashlib.sha256()
 with p.open('rb') as f:
  for c in iter(lambda:f.read(1024*1024),b''):h.update(c)
 return h.hexdigest()
def regular(p:Path)->bool:
 try:s=p.lstat()
 except FileNotFoundError:return False
 return stat.S_ISREG(s.st_mode) and not p.is_symlink()
def now():return dt.datetime.now(dt.timezone.utc).isoformat()
class DecodeError(ValueError):pass
if any(p.exists() for p in [LOCK,RECEIPT,MICRO,PARSER_RECEIPT,TERMINAL,ORIGINAL]):raise SystemExit('REFUSE_RERUN_OR_STALE_V13_ARTIFACT')
p=json.loads(PROTOCOL.read_text());start_ns=time.monotonic_ns();started=now()
# Fail closed on every frozen identity before any derived output.
for name,spec in p['frozen_inputs'].items():
 path=Path(spec['path'])
 if not regular(path) or sha(path)!=spec['sha256']:raise SystemExit('FROZEN_INPUT_DRIFT:'+name)
LOCK.write_text(json.dumps({'schema_version':'orion.p3.optional-wrapper-typed-decoder.attempt-lock.v13','protocol_sha256':sha(PROTOCOL),'started_at':started,'decoder_attempts':1,'parser_attempts':1,'retries':0},indent=2,sort_keys=True)+'\n')
universe=json.loads(Path(p['frozen_inputs']['universe_manifest']['path']).read_text());sets={'source':set(universe['expected_source_iris']),'target':set(universe['expected_target_iris'])};grammar=re.compile(p['typed_grammar']['anchored_regex'])
def decode(text:str,role:str)->str:
 if role not in sets:raise DecodeError('unknown role')
 if not isinstance(text,str):raise DecodeError('entity is not a string')
 m=grammar.fullmatch(text)
 if m is None:raise DecodeError('surface string does not match the exact typed grammar')
 decoded=m.group('ontology_iri')+m.group('fragment')
 if decoded not in sets[role]:raise DecodeError('decoded IRI is not an exact member of the role-specific frozen universe')
 return decoded
# Frozen adversarial microcases.
case_rows=[]
for case in p['adversarial_microcases']:
 try:observed=decode(case['text'],case['role']);accepted=True;error=None
 except DecodeError as exc:observed=None;accepted=False;error=str(exc)
 passed=accepted is case['accept'] and (not accepted or observed==case['decoded'])
 case_rows.append({'id':case['id'],'role':case['role'],'text':case['text'],'expected_accept':case['accept'],'observed_accept':accepted,'expected_decoded':case.get('decoded'),'observed_decoded':observed,'error':error,'pass':passed})
micro_pass=len(case_rows)==12 and all(x['pass'] for x in case_rows)
MICRO.write_text(json.dumps({'schema_version':'orion.p3.optional-wrapper-typed-decoder.adversarial-microcases.v13','grammar':p['typed_grammar'],'cases':case_rows,'checks_passed':sum(x['pass'] for x in case_rows),'checks_total':len(case_rows),'pass':micro_pass,'terminal':'PASS_TYPED_DECODER_ADVERSARIAL_MICROCASES' if micro_pass else 'FAIL_TYPED_DECODER_ADVERSARIAL_MICROCASES'},indent=2,sort_keys=True)+'\n')
if not micro_pass:raise SystemExit('ADVERSARIAL_MICROCASES_FAIL')
# Read the exact retained V12 artifact and preserve a byte-identical V13 copy.
wrapped=Path(p['frozen_inputs']['wrapped_repaired_v12']['path']);before=sha(wrapped);shutil.copyfile(wrapped,ORIGINAL)
with wrapped.open(newline='') as f:rows=list(csv.reader(f,delimiter='\t',strict=True))
if not rows or rows[0]!=['SrcEntity','TgtEntity','Score'] or len(rows[1:])!=16 or any(len(x)!=3 for x in rows[1:]):raise SystemExit('WRAPPED_TABLE_SHAPE_FAIL')
decoded=[];src_map={};tgt_map={}
for src,tgt,score in rows[1:]:
 ds=decode(src,'source');dtgt=decode(tgt,'target');src_map[src]=ds;tgt_map[tgt]=dtgt;decoded.append((ds,dtgt,score))
src_injective=len(set(src_map))==len(set(src_map.values()));tgt_injective=len(set(tgt_map))==len(set(tgt_map.values()))
if not src_injective or not tgt_injective:raise SystemExit('DECODE_NOT_INJECTIVE')
# Copy four immutable predecessor artifacts and write only the separate decoded repair artifact.
copy_roles={'raw_mappings.json':'raw_mappings_json','raw_mappings.tsv':'raw_mappings_tsv','extended_mappings.tsv':'extended_mappings_tsv','filtered_mappings.tsv':'filtered_mappings_tsv'}
for dest,key in copy_roles.items():shutil.copyfile(Path(p['frozen_inputs'][key]['path']),OUT/dest)
decoded_path=OUT/'repaired_mappings.tsv'
with decoded_path.open('w',newline='') as f:
 w=csv.writer(f,delimiter='\t',lineterminator='\n');w.writerow(['SrcEntity','TgtEntity','Score']);w.writerows(decoded)
# Parser runs exactly once on the separate decoded five-artifact interface.
parser_cmd=[sys.executable,str(Path(p['frozen_inputs']['unchanged_parser']['path'])),'--output-dir',str(OUT),'--manifest',str(Path(p['frozen_inputs']['universe_manifest']['path'])),'--write-receipt',str(PARSER_RECEIPT)]
parser_start=time.monotonic_ns();pc=subprocess.run(parser_cmd,cwd=ROOT,capture_output=True,timeout=120,check=False);parser_ns=time.monotonic_ns()-parser_start;PARSER_STDOUT.write_bytes(pc.stdout);PARSER_STDERR.write_bytes(pc.stderr);parser_result=json.loads(PARSER_RECEIPT.read_text()) if PARSER_RECEIPT.is_file() else {}
after=sha(wrapped);raw_unchanged=before==after==p['frozen_inputs']['wrapped_repaired_v12']['sha256'] and sha(ORIGINAL)==before
membership={'source':sum(x[0] in sets['source'] for x in decoded),'target':sum(x[1] in sets['target'] for x in decoded)}
success=micro_pass and len(decoded)==16 and membership=={'source':16,'target':16} and src_injective and tgt_injective and raw_unchanged and pc.returncode==0 and parser_result.get('terminal')=='STRUCTURAL_NATIVE_ARTIFACT_CONTRACT_PASS'
terminal='P3_V13_TYPED_OPTIONAL_DECODER_PASS__SIXTEEN_OF_SIXTEEN_EXACT_ROLE_UNIVERSE_MEMBERS__INJECTIVE__TWELVE_OF_TWELVE_ADVERSARIAL_MICROCASES_PASS__UNCHANGED_V7_STRUCTURAL_PARSER_PASS__RAW_V12_UNCHANGED' if success else 'P3_V13_TYPED_OPTIONAL_DECODER_FAIL__FAIL_CLOSED__RAW_V12_UNCHANGED'
artifacts={}
for q in sorted(OUT.iterdir()):
 if q.is_file():artifacts[q.name]={'path':str(q),'bytes':q.stat().st_size,'sha256':sha(q),'regular_non_symlink':regular(q)}
wall=time.monotonic_ns()-start_ns
receipt={'schema_version':'orion.p3.optional-wrapper-typed-decoder.receipt.v13','protocol_id':p['protocol_id'],'authority':p['authority'],'protocol_sha256':sha(PROTOCOL),'started_at':started,'finished_at':now(),'runtime_nanoseconds':wall,'runtime_seconds':wall/1e9,'decoder_attempts':1,'parser_attempts':1,'retries':0,'training_attempts':0,'logmap_attempts':0,'native_attempts':0,'downloads':0,'grammar':p['typed_grammar'],'adversarial_microcases':{'checks':'12/12' if micro_pass else f"{sum(x['pass'] for x in case_rows)}/12",'receipt_sha256':sha(MICRO)},'real_decode':{'input_rows':len(rows)-1,'decoded_rows':len(decoded),'exact_source_members':membership['source'],'exact_target_members':membership['target'],'source_injective':src_injective,'target_injective':tgt_injective,'decoded_artifact':artifacts['repaired_mappings.tsv']},'raw_v12':{'path':str(wrapped),'sha256_before':before,'sha256_after':after,'unchanged':raw_unchanged,'byte_identical_v13_copy_sha256':sha(ORIGINAL)},'parser':{'command':parser_cmd,'exit_code':pc.returncode,'runtime_nanoseconds':parser_ns,'runtime_seconds':parser_ns/1e9,'receipt':parser_result,'receipt_sha256':sha(PARSER_RECEIPT) if PARSER_RECEIPT.is_file() else None,'stdout_sha256':sha(PARSER_STDOUT),'stderr_sha256':sha(PARSER_STDERR)},'five_artifact_interface':artifacts,'success':success,'gold_or_reference_opened':False,'protected_outcome_opened':False,'scientific_scoring_performed':False,'terminal':terminal}
RECEIPT.write_text(json.dumps(receipt,indent=2,sort_keys=True)+'\n');TERMINAL.write_text(terminal+'\n');print(json.dumps({'terminal':terminal,'runtime_seconds':receipt['runtime_seconds'],'adversarial_microcases':receipt['adversarial_microcases']['checks'],'decoded_rows':len(decoded),'membership':membership,'injective':{'source':src_injective,'target':tgt_injective},'raw_v12_unchanged':raw_unchanged,'parser_exit':pc.returncode,'parser_terminal':parser_result.get('terminal'),'decoded_artifact':artifacts['repaired_mappings.tsv']},indent=2));raise SystemExit(0 if success else 1)

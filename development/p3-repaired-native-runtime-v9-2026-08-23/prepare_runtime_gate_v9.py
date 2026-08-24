#!/usr/bin/env python3
from __future__ import annotations
import hashlib,json,subprocess
from datetime import datetime,timezone
from pathlib import Path
from xml.etree import ElementTree as ET
ROOT=Path(__file__).resolve().parent; REPO=ROOT.parent.parent
V6=ROOT.parent/'p3-comparator-native-preflight-v6-2026-08-23';V7=ROOT.parent/'p3-bertmap-execution-binding-v7-2026-08-23';V8=ROOT.parent/'p3-bertmap-table-reader-repair-v8-2026-08-23'
SRC=ROOT/'runtime/source';MODEL=ROOT/'runtime/model';INPUTS=ROOT/'runtime/inputs';RESULTS=ROOT/'runtime/results/bertmap-out'
def sha(p):
 h=hashlib.sha256()
 with p.open('rb') as f:
  for b in iter(lambda:f.read(1024*1024),b''):h.update(b)
 return h.hexdigest()
def now():return datetime.now(timezone.utc).isoformat()
def j(name):return json.loads((ROOT/name).read_text())
def run(*args):return subprocess.run(args,capture_output=True,text=True,check=True).stdout.strip()
protocol=j('PROTOCOL_V9.json');checks=[]
def ck(name,condition,detail=None):checks.append({'check':name,'pass':bool(condition),'detail':detail});return bool(condition)
ck('protocol_hash',sha(ROOT/'PROTOCOL_V9.json')==j('PROTOCOL_FREEZE_RECEIPT_V9.json')['protocol_sha256'])
for key,base in [('v6_protocol',V6),('v6_k3_result',V6),('v7_result',V7),('v7_compatibility_lock',V7),('v7_parser',V7),('v8_result',V8),('v8_patch',V8)]:
 x=protocol['predecessors'][key];ck('predecessor_'+key,sha(base/Path(x['path']).name)==x['sha256'])
commit=run('git','-C',str(SRC),'rev-parse','HEAD');tree=run('git','-C',str(SRC),'rev-parse','HEAD^{tree}')
ck('source_commit',commit==protocol['source_identity']['commit'],commit);ck('source_tree',tree==protocol['source_identity']['tree'],tree)
status=run('git','-C',str(SRC),'status','--short');ck('source_only_mapping_modified',status.strip()=='M src/deeponto/align/mapping.py',status)
ck('source_patch_hash',sha(ROOT/'V8_PATCH_EXACT.patch')==protocol['single_source_change']['patch_sha256'])
ck('repaired_mapping_hash',sha(SRC/'src/deeponto/align/mapping.py')==protocol['single_source_change']['expected_repaired_sha256'])
ck('source_license',sha(SRC/'LICENSE')==protocol['source_identity']['root_license_sha256'])
tracked=[]
for rel in run('git','-C',str(SRC),'ls-files').splitlines():
 p=SRC/rel
 if p.is_file():tracked.append({'path':rel,'bytes':p.stat().st_size,'sha256':sha(p),'modified':rel=='src/deeponto/align/mapping.py'})
source_manifest={'schema_version':'orion.p3.repaired-native-runtime.source-manifest.v9','commit':commit,'tree':tree,'single_patch_sha256':sha(ROOT/'V8_PATCH_EXACT.patch'),'tracked_file_count':len(tracked),'tracked_files':tracked}
(ROOT/'PATCHED_SOURCE_MANIFEST_V9.json').write_text(json.dumps(source_manifest,indent=2,sort_keys=True)+'\n')
py=j('PYTHON_RUNTIME_SBOM_V9.json');jdk=j('JDK_RUNTIME_MANIFEST_V9.json');jsbom=j('JAVA_COMPONENT_SBOM_V9.json');jrights=j('JAVA_COMPONENT_RIGHTS_V9.json')
ck('python_rights',py['rights_gate']=='PASS',py['summary']);ck('python_distribution_count',py['summary']['distribution_count']==126,py['summary']['distribution_count'])
versions={x['name'].lower():x['version'] for x in py['distributions']}
expected={**protocol['python_runtime']['exact_compatibility_tuple'],'deeponto':'0.9.3'}
ck('python_exact_key_versions',all(versions.get(k)==v for k,v in expected.items()),{k:versions.get(k) for k in expected})
ck('full_lock_hash',sha(ROOT/'V9_FULL_REQUIREMENTS.txt')=='b3b2f366692f283b154a42238e465ab939268092bbdbf2accca465d081b53790')
ck('jdk_rights',jdk['rights_gate'].startswith('PASS'),jdk['summary']);ck('jdk_version','17.0.19' in jdk['java_version'] and jdk['machine']=='arm64',jdk['java_version'])
ck('jar_inventory',jsbom['summary']['tracked_jar_paths']==208 and jsbom['summary']['unique_jar_hashes']==192,jsbom['summary'])
ck('jar_rights',jrights['rights_gate']=='PASS' and jrights['summary']['rights_bound']==192 and jrights['summary']['rights_unbound']==0,jrights['summary'])
model=[]
for rel,digest in protocol['model']['required_files'].items():
 p=MODEL/rel;model.append({'path':rel,'exists':p.is_file(),'bytes':p.stat().st_size if p.is_file() else None,'sha256':sha(p) if p.is_file() else None,'expected_sha256':digest,'match':p.is_file() and sha(p)==digest})
ck('model_files',all(x['match'] for x in model),model);ck('model_license',next(x for x in model if x['path']=='LICENSE')['match'])
model_manifest={'schema_version':'orion.p3.repaired-native-runtime.model-manifest.v9','repository':protocol['model']['repository'],'revision':protocol['model']['revision'],'license':'MIT','files':model,'all_match':all(x['match'] for x in model)}
(ROOT/'MODEL_MANIFEST_V9.json').write_text(json.dumps(model_manifest,indent=2,sort_keys=True)+'\n')
for role in ['source','target']:
 ck(role+'_input_hash',sha(INPUTS/(role+'.owl'))==protocol['unchanged_no_gold_smoke'][role]['sha256'])
ns='{http://www.w3.org/2002/07/owl#}Class';rdf='{http://www.w3.org/1999/02/22-rdf-syntax-ns#}about'
def iris(p):return sorted(x.attrib[rdf] for x in ET.parse(p).getroot().iter(ns))
siri=iris(INPUTS/'source.owl');tiri=iris(INPUTS/'target.owl')
ck('input_class_counts',len(siri)==len(tiri)==16,{'source':len(siri),'target':len(tiri)})
raw=(INPUTS/'source.owl').read_text()+(INPUTS/'target.owl').read_text()
ck('input_no_gold_tokens',not any(x in raw.lower() for x in ['gold','referencealignment','disjointwith','protected','outcome']))
if RESULTS.exists() and any(RESULTS.rglob('*')):ck('output_absent_before_execution',False,[str(x) for x in RESULTS.rglob('*')])
else:ck('output_absent_before_execution',True)
config=f'''model: bertmap\noutput_path: {RESULTS.resolve()}\nannotation_property_iris:\n  - http://www.w3.org/2000/01/rdf-schema#label\nknown_mappings: null\nauxiliary_ontos: []\nbert:\n  pretrained_path: {MODEL.resolve()}\n  max_length_for_input: 128\n  num_epochs_for_training: 3.0\n  batch_size_for_training: 1\n  batch_size_for_prediction: 16\n  resume_training: null\nglobal_matching:\n  enabled: true\n  num_raw_candidates: 200\n  num_best_predictions: 10\n  mapping_extension_threshold: 0.9\n  mapping_filtered_threshold: 0.9995\n  for_oaei: false\n'''
(ROOT/'runtime/config.yaml').write_text(config)
universe={'schema_version':'orion.p3.bertmap-universe-manifest.v7','expected_source_iris':siri,'expected_target_iris':tiri,'mapping_extension_threshold':'0.9','mapping_filtered_threshold':'0.9995','for_oaei':False,'excluded_source_iris':[]}
(ROOT/'UNIVERSE_MANIFEST_V9.json').write_text(json.dumps(universe,indent=2,sort_keys=True)+'\n')
ck('config_logical_values',all(x in config for x in ['known_mappings: null','auxiliary_ontos: []','mapping_extension_threshold: 0.9','mapping_filtered_threshold: 0.9995','for_oaei: false','num_epochs_for_training: 3.0','batch_size_for_training: 1','batch_size_for_prediction: 16']))
passed=sum(x['pass'] for x in checks);gate='PASS__COMPLETE_CONTENT_ADDRESSED_RUNTIME_AND_COMPONENT_RIGHTS_BOUND' if passed==len(checks) else 'CANNOT_CHECK_RUNTIME_OR_RIGHTS'
out={'schema_version':'orion.p3.repaired-native-runtime.rights-gate.v9','protocol_id':protocol['protocol_id'],'evaluated_at':now(),'authority':'PRE_EXECUTION_RUNTIME_IDENTITY_AND_RIGHTS_GATE__NOT_LEGAL_ADVICE','terminal':gate,'checks_passed':passed,'checks_total':len(checks),'checks':checks,'manifests':{'patched_source_sha256':sha(ROOT/'PATCHED_SOURCE_MANIFEST_V9.json'),'python_runtime_sbom_sha256':sha(ROOT/'PYTHON_RUNTIME_SBOM_V9.json'),'jdk_runtime_manifest_sha256':sha(ROOT/'JDK_RUNTIME_MANIFEST_V9.json'),'java_component_sbom_sha256':sha(ROOT/'JAVA_COMPONENT_SBOM_V9.json'),'java_component_rights_sha256':sha(ROOT/'JAVA_COMPONENT_RIGHTS_V9.json'),'model_manifest_sha256':sha(ROOT/'MODEL_MANIFEST_V9.json'),'config_sha256':sha(ROOT/'runtime/config.yaml'),'universe_manifest_sha256':sha(ROOT/'UNIVERSE_MANIFEST_V9.json')},'content_counts':{'source_tracked_files':len(tracked),'python_distributions':py['summary']['distribution_count'],'python_installed_file_records':py['summary']['installed_distribution_file_records'],'python_base_files':py['summary']['python_base_file_records'],'jdk_files':jdk['summary']['file_count'],'jdk_legal_files':jdk['summary']['legal_file_count'],'deeponto_jar_paths':jsbom['summary']['tracked_jar_paths'],'deeponto_unique_jar_hashes':jsbom['summary']['unique_jar_hashes'],'jar_rights_bound':jrights['summary']['rights_bound'],'model_files':len(model)},'gold_or_outcomes_opened':False,'native_execution_authorized':gate.startswith('PASS')}
(ROOT/'RUNTIME_RIGHTS_GATE_V9.json').write_text(json.dumps(out,indent=2,sort_keys=True)+'\n')
print(json.dumps({'terminal':gate,'checks':f'{passed}/{len(checks)}','counts':out['content_counts'],'native_execution_authorized':out['native_execution_authorized']},sort_keys=True))
if not out['native_execution_authorized']:raise SystemExit(1)

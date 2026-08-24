#!/usr/bin/env python3
"""Fetch frozen ontology blobs and extract only direct explicit identity/equivalence/disjoint certificates."""
from __future__ import annotations
import collections, datetime as dt, hashlib, itertools, json, pathlib, sys, time, urllib.parse, urllib.request
ROOT=pathlib.Path(__file__).resolve().parent
sys.path.insert(0,str(ROOT/'.runtime'))
from rdflib import Graph, URIRef
from rdflib.namespace import RDF,RDFS,OWL,DCTERMS
PREFREEZE=json.loads((ROOT/'SOURCE_FRAME_PREFREEZE_V5.json').read_text())
ADAPTERS=json.loads((ROOT/'COMPARATOR_ADAPTERS_V5.json').read_text())
RIGHTS_PATH=ROOT/'RIGHTS_IDENTITY_AUDIT_V5.json'
UA='ORION-P3-V5-explicit-axiom-harvest/1.0'
def now():return dt.datetime.now(dt.timezone.utc).isoformat()
def git_blob(b):return hashlib.sha1(f'blob {len(b)}\0'.encode()+b).hexdigest()
def fetch(url):
 attempts=[]
 for i in range(1,4):
  try:
   with urllib.request.urlopen(urllib.request.Request(url,headers={'User-Agent':UA}),timeout=60) as r:b=r.read();status=r.status;ct=r.headers.get('Content-Type')
   attempts.append({'attempt':i,'http_status':status,'bytes':len(b),'sha256':hashlib.sha256(b).hexdigest(),'content_type':ct,'error':None});return b,attempts
  except Exception as e:attempts.append({'attempt':i,'http_status':getattr(e,'code',None),'bytes':0,'sha256':None,'content_type':None,'error':f'{type(e).__name__}:{e}'});time.sleep(i)
 return None,attempts
def in_namespace(value,prefixes):return isinstance(value,URIRef) and any(str(value).startswith(p) for p in prefixes)
def rdf_list(g,head):
 out=[];seen=set();node=head
 while node and node!=RDF.nil and node not in seen:
  seen.add(node);first=g.value(node,RDF.first);rest=g.value(node,RDF.rest)
  if first is None or rest is None:return [],'CANNOT_CHECK_MALFORMED_RDF_LIST'
  out.append(first);node=rest
 if node in seen:return [],'CANNOT_CHECK_CYCLIC_RDF_LIST'
 return out,'PASS'
def pair(a,b):return tuple(sorted((str(a),str(b))))
def main():
 if not RIGHTS_PATH.exists():
  raise SystemExit('CANNOT_CHECK: independent RIGHTS_IDENTITY_AUDIT_V5.json is required before family admission')
 rights_audit=json.loads(RIGHTS_PATH.read_text())
 rights_families=rights_audit.get('families',{})
 byte_rows=[]; evidence={}; family_graph_counts=collections.Counter(); family_licenses=collections.defaultdict(set); parse_errors=[]
 for family_id,spec in PREFREEZE['families'].items():
  prefixes=ADAPTERS['truth_adapter']['namespace_guards'][family_id]
  ev={'classes':collections.defaultdict(set),'equiv':collections.defaultdict(set),'disjoint':collections.defaultdict(set),'all_disjoint_lists':0,'list_errors':[]}
  for f in spec['files']:
   path=f['path'];url=f"https://raw.githubusercontent.com/{spec['repository']}/{spec['commit']}/{urllib.parse.quote(path,safe='/')}"
   b,attempts=fetch(url); row={'family_id':family_id,'path':path,'url':url,'expected_git_blob_sha1':f['git_blob_sha1'],'advertised_bytes':f.get('advertised_bytes'),'attempts':attempts,'observed_git_blob_sha1':git_blob(b) if b is not None else None,'observed_sha256':hashlib.sha256(b).hexdigest() if b is not None else None,'observed_bytes':len(b) if b is not None else 0,'parse_status':None,'triple_count':0}
   if b is None or row['observed_git_blob_sha1']!=f['git_blob_sha1']:
    row['parse_status']='CANNOT_CHECK_TRANSPORT_OR_GIT_BLOB_MISMATCH';parse_errors.append({'family_id':family_id,'path':path,'status':row['parse_status']});byte_rows.append(row);continue
   fmt='turtle' if path.lower().endswith('.ttl') else 'xml'
   g=Graph()
   try:g.parse(data=b,format=fmt,publicID=url)
   except Exception as e:
    row['parse_status']=f'CANNOT_CHECK_RDF_PARSE:{type(e).__name__}:{e}';parse_errors.append({'family_id':family_id,'path':path,'status':row['parse_status']});byte_rows.append(row);continue
   row['parse_status']='PASS';row['triple_count']=len(g);family_graph_counts[family_id]+=len(g)
   for lic in g.objects(None,DCTERMS.license):
    if isinstance(lic,URIRef):family_licenses[family_id].add(str(lic))
   for typ in (OWL.Class,RDFS.Class):
    for c in g.subjects(RDF.type,typ):
     if in_namespace(c,prefixes):ev['classes'][str(c)].add(path)
   for a,bv in g.subject_objects(OWL.equivalentClass):
    if in_namespace(a,prefixes) and in_namespace(bv,prefixes):
     if a!=bv:ev['equiv'][pair(a,bv)].add(path)
     ev['classes'][str(a)].add(path);ev['classes'][str(bv)].add(path)
   for a,bv in g.subject_objects(OWL.disjointWith):
    if in_namespace(a,prefixes) and in_namespace(bv,prefixes) and a!=bv:
     ev['disjoint'][pair(a,bv)].add(path);ev['classes'][str(a)].add(path);ev['classes'][str(bv)].add(path)
   for node in g.subjects(RDF.type,OWL.AllDisjointClasses):
    head=g.value(node,OWL.members) or g.value(node,OWL.distinctMembers)
    if head is None:ev['list_errors'].append({'path':path,'status':'CANNOT_CHECK_MISSING_MEMBERS_LIST'});continue
    members,status=rdf_list(g,head)
    if status!='PASS':ev['list_errors'].append({'path':path,'status':status});continue
    named=sorted({m for m in members if in_namespace(m,prefixes)},key=str)
    if len(named)!=len(members):
     ev['list_errors'].append({'path':path,'status':'CANNOT_CHECK_ALL_DISJOINT_LIST_HAS_OUT_OF_NAMESPACE_OR_BLANK_MEMBER','member_count':len(members),'retained_count':len(named)});continue
    ev['all_disjoint_lists']+=1
    for a,bv in itertools.combinations(named,2):ev['disjoint'][pair(a,bv)].add(path);ev['classes'][str(a)].add(path);ev['classes'][str(bv)].add(path)
   byte_rows.append(row)
  evidence[family_id]=ev
 (ROOT/'SOURCE_BYTE_MANIFEST_V5.json').write_text(json.dumps({'schema_version':'orion.p3.authoritative-negative-semantics.source-byte-manifest.v5','created_at':now(),'files':byte_rows,'counts':{'files':len(byte_rows),'transport_and_git_blob_pass':sum(r['parse_status']=='PASS' for r in byte_rows),'observed_bytes':sum(r['observed_bytes'] for r in byte_rows),'triples':sum(r['triple_count'] for r in byte_rows)},'parse_errors':parse_errors,'raw_payloads_retained':False},indent=2,sort_keys=True)+'\n')
 certs=[];family_results={}
 for family_id,ev in evidence.items():
  glue={pair(c,c):{'IDENTICAL_IRI_BYTE_IDENTICAL_VIEWS'} for c in ev['classes']}
  for p in ev['equiv']:glue.setdefault(p,set()).add('DIRECT_ASSERTED_OWL_EQUIVALENT_CLASS')
  obs={p:{'DIRECT_ASSERTED_OWL_DISJOINTNESS'} for p in ev['disjoint']}
  conflicts=set(glue)&set(obs)
  for truth,src in [('GLUE',glue),('OBSTRUCTION',obs)]:
   for p,authorities in sorted(src.items()):
    if p in conflicts:continue
    paths=ev['classes'].get(p[0],set())|ev['classes'].get(p[1],set())|ev['equiv'].get(p,set())|ev['disjoint'].get(p,set())
    ident=f'{family_id}|{p[0]}|{p[1]}|{truth}'
    certs.append({'schema_version':'orion.p3.direct-axiom-certificate.v5','certificate_id':hashlib.sha256(ident.encode()).hexdigest()[:24],'family_id':family_id,'left_iri':p[0],'right_iri':p[1],'truth':truth,'authority':sorted(authorities),'source_paths':sorted(paths),'absence_used':False,'inference_used':False})
  file_rows=[r for r in byte_rows if r['family_id']==family_id]
  rights_row=rights_families.get(family_id,{})
  rights_ok=(
   rights_row.get('verdict')=='PASS'
   and rights_row.get('identity_pass') is True
   and rights_row.get('applicability_pass') is True
   and rights_row.get('research_use_pass') is True
  )
  transport_ok=bool(file_rows) and all(r['parse_status']=='PASS' for r in file_rows)
  family_results[family_id]={'frozen_file_count':len(file_rows),'transport_and_parse_pass':transport_ok,'observed_bytes':sum(r['observed_bytes'] for r in file_rows),'triple_count_sum_without_cross_file_dedup':family_graph_counts[family_id],'authority_namespace_class_count':len(ev['classes']),'identity_glue_certificate_count':len(ev['classes']),'distinct_equivalence_glue_certificate_count':len(ev['equiv']),'explicit_disjoint_obstruction_certificate_count':len(obs),'all_disjoint_lists_expanded':ev['all_disjoint_lists'],'conflict_count':len(conflicts),'list_error_count':len(ev['list_errors']),'list_errors':ev['list_errors'],'ontology_declared_license_iris':sorted(family_licenses[family_id]),'rights_registry_pass':rights_ok,'source_family_disjoint_governance_pass':True,'family_admitted':rights_ok and transport_ok and len(ev['classes'])>0 and len(obs)>0 and len(conflicts)==0}
 certs.sort(key=lambda x:(x['family_id'],x['truth'],x['left_iri'],x['right_iri']))
 (ROOT/'CERTIFICATE_REGISTRY_V5.jsonl').write_text(''.join(json.dumps(r,sort_keys=True,separators=(',',':'))+'\n' for r in certs))
 result={'schema_version':'orion.p3.authoritative-negative-semantics.extraction-result.v5','created_at':now(),'frame_id':'P3_V5_DIRECT_AXIOM_NEGATIVE_SEMANTICS_CALIBRATION_FRAME','families':family_results,'counts':{'frozen_families':3,'admitted_families':sum(x['family_admitted'] for x in family_results.values()),'required_families':3,'certificate_rows':len(certs),'glue_rows':sum(x['truth']=='GLUE' for x in certs),'obstruction_rows':sum(x['truth']=='OBSTRUCTION' for x in certs),'conflicts':sum(x['conflict_count'] for x in family_results.values())},'frame_gate_pass':all(x['family_admitted'] for x in family_results.values()) and len(family_results)>=3,'boundary':{'candidate_universe':'certificate-bearing pairs only','cartesian_absence_used':False,'positive_reference_absence_used':False,'reasoner_inference_used':False,'comparator_outputs_opened':False,'protected_outcomes_opened':False,'naturalistic_cross_ontology_claim':False}}
 (ROOT/'EXTRACTION_RESULT_V5.json').write_text(json.dumps(result,indent=2,sort_keys=True)+'\n')
 print(json.dumps(result['counts']|{'frame_gate_pass':result['frame_gate_pass']},indent=2,sort_keys=True))
if __name__=='__main__':main()

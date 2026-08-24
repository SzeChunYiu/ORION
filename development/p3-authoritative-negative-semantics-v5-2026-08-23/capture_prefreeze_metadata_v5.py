#!/usr/bin/env python3
"""Capture only source identities, path manifests and rights metadata before axiom access."""
from __future__ import annotations
import datetime as dt, hashlib, json, pathlib, subprocess, urllib.request
ROOT=pathlib.Path(__file__).resolve().parent
UA='ORION-P3-V5-preoutcome-rights-identity-audit/1.0'
def now():return dt.datetime.now(dt.timezone.utc).isoformat()
def fetch(url):
 b=urllib.request.urlopen(urllib.request.Request(url,headers={'User-Agent':UA}),timeout=45).read()
 return b
# Exact metadata chosen by governance diversity, rights clarity and immutable source identity, not axiom counts.
families={
 'W3C_PROV_O_REC_20130430':{
  'governance_family':'W3C_PROV_WORKING_GROUP','repository':'w3c/prov','commit':'aa82bd71b6bb1f7b735bf3f7f5b948fae87764f0','tree':'5afb605675880080abcb4d1baedcafd18e42737e',
  'files':[{'path':'ontology/releases/REC-prov-o-20130430/ns/prov-o.ttl','git_blob_sha1':'8b4d4b18d73d1e8f3e671e879c6c242205b6a729','advertised_bytes':68795}],
  'rights_urls':['https://www.w3.org/TR/2013/REC-prov-o-20130430/','https://www.w3.org/copyright/software-license-2023/'],
  'rights_identity':'W3C Software and Document License; dated W3C Recommendation copyright and document-use notice',
 },
 'ENVO_2026_06_26':{
  'governance_family':'ENVIRONMENT_ONTOLOGY_OBO','repository':'EnvironmentOntology/envo','tag':'v2026-06-26','commit':'a2455d1a77e46bb8a664d65a157166b539269042','tree':'c58dbb82d3985d84c549236bc0184704867a8fc6',
  'files':[{'path':'envo.owl','git_blob_sha1':'54a8273c22d570590ea87daeee26196035f84c1f','advertised_bytes':9614229}],
  'rights_urls':['https://raw.githubusercontent.com/EnvironmentOntology/envo/a2455d1a77e46bb8a664d65a157166b539269042/LICENSE'],
  'rights_identity':'CC0-1.0 repository licence at exact release commit',
 },
 'FIBO_FND_2026Q2':{
  'governance_family':'EDM_COUNCIL_FIBO','repository':'edmcouncil/fibo','tag':'master_2026Q2','commit':'f59157fe156e3d91b1c045222d0a7dc06b7d78a2','tree':'82d3273e1e93a98152b730538761b9e3264a37ea',
  'files':[],
  'rights_urls':['https://raw.githubusercontent.com/edmcouncil/fibo/f59157fe156e3d91b1c045222d0a7dc06b7d78a2/LICENSE'],
  'rights_identity':'MIT repository licence at exact release commit',
 }
}
tree=json.loads(subprocess.run(['gh','api','repos/edmcouncil/fibo/git/trees/f59157fe156e3d91b1c045222d0a7dc06b7d78a2?recursive=1'],check=True,capture_output=True,text=True).stdout)
fibo=[{'path':x['path'],'git_blob_sha1':x['sha'],'advertised_bytes':x.get('size')} for x in tree['tree'] if x.get('type')=='blob' and x['path'].startswith('FND/') and x['path'].endswith('.rdf')]
fibo.sort(key=lambda x:x['path']); assert len(fibo)==59
families['FIBO_FND_2026Q2']['files']=fibo
rights=[]
for family_id,spec in families.items():
 for url in spec['rights_urls']:
  b=fetch(url); rights.append({'family_id':family_id,'url':url,'http_body_bytes':len(b),'http_body_sha256':hashlib.sha256(b).hexdigest()})
registry={
 'schema_version':'orion.p3.authoritative-negative-semantics.source-frame-prefreeze.v5','created_at':now(),'status':'SOURCE_IDENTITIES_PATHS_AND_RIGHTS_FROZEN_BEFORE_AXIOM_ACCESS',
 'selection_authority':'PUBLIC_SOURCE_METADATA_ONLY__NO_ONTOLOGY_AXIOM_OR_COMPARATOR_OUTCOME_INSPECTION',
 'selection_rule':'One independently governed W3C, OBO environmental-science, and EDM Council finance ontology family; exact release/commit/blob path identities; permissive public rights; selection made without opening frozen ontology bytes or relation axioms.',
 'families':families,'rights_captures':rights,
 'counts':{'families':3,'governance_families':len({x['governance_family'] for x in families.values()}),'frozen_files':sum(len(x['files']) for x in families.values()),'advertised_bytes':sum((f.get('advertised_bytes') or 0) for x in families.values() for f in x['files'])},
 'boundaries':{'ontology_axiom_payloads_opened':False,'explicit_negative_counts_observed':False,'comparator_outputs_opened':False,'protected_outcomes_opened':False,'positive_reference_absence_as_negative':False}
}
(ROOT/'SOURCE_FRAME_PREFREEZE_V5.json').write_text(json.dumps(registry,indent=2,sort_keys=True)+'\n')
print(json.dumps(registry['counts'],indent=2,sort_keys=True))

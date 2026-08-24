#!/usr/bin/env python3
"""Outcome-blind seven-field Retraction Watch relation census.

Never prints, persists, hashes individually, aggregates, or branches on forbidden
columns. A raw transport is required to parse CSV framing; only the frozen seven
allowlisted cells are materialized semantically.
"""
from __future__ import annotations
import csv, hashlib, json, re, sys
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path

LANE=Path(__file__).resolve().parent
RAW=LANE/'.runtime/retraction_watch.csv'
PROTOCOL=LANE/'RELATION_CENSUS_PROTOCOL_V2.json'
AMEND=LANE/'RELATION_CENSUS_PROTOCOL_V2_AMENDMENT_A.json'
AMEND_B=LANE/'RELATION_CENSUS_PROTOCOL_V2_AMENDMENT_B.json'
EXPECTED_SHA='ceaab201d728dfcf9929ec1e229acd2ad88c650c847ec922ba9ffe831e366abb'
EXPECTED_BYTES=65984968
EXPECTED_ROWS=71944
EXPECTED_HEADER=['Record ID','Title','Subject','Institution','Journal','Publisher','Country','Author','URLS','ArticleType','RetractionDate','RetractionDOI','RetractionPubMedID','OriginalPaperDate','OriginalPaperDOI','OriginalPaperPubMedID','RetractionNature','Reason','Paywalled','Notes','']
ALLOW=['Record ID','RetractionDate','RetractionDOI','RetractionPubMedID','OriginalPaperDate','OriginalPaperDOI','OriginalPaperPubMedID']
DOI_RE=re.compile(r'^10\.\d{4,9}/\S+$',re.I)

class UF:
    def __init__(self): self.p={}
    def add(self,x): self.p.setdefault(x,x)
    def find(self,x):
        self.add(x)
        while self.p[x]!=x:
            self.p[x]=self.p[self.p[x]]; x=self.p[x]
        return x
    def union(self,a,b):
        ra,rb=self.find(a),self.find(b)
        if ra!=rb: self.p[rb]=ra

def sha(p):
    h=hashlib.sha256()
    with p.open('rb') as f:
        for b in iter(lambda:f.read(1024*1024),b''): h.update(b)
    return h.hexdigest()

def norm_doi(s):
    x=s.strip().casefold()
    if not x or x=='unavailable': return None, 'missing'
    for pref in ('https://doi.org/','http://doi.org/','https://dx.doi.org/','http://dx.doi.org/','doi:'):
        if x.startswith(pref): x=x[len(pref):].strip(); break
    if DOI_RE.fullmatch(x) and not any(c.isspace() for c in x): return x,'valid'
    return None,'invalid'

def norm_pmid(s):
    x=s.strip()
    if not x or x=='0': return None,'missing'
    if x.isascii() and x.isdigit() and int(x)>0: return str(int(x)),'valid'
    return None,'invalid'

def node_doi(x): return 'D:'+x
def node_pmid(x): return 'P:'+x

def endpoint_key(nodes):
    dois=sorted(n[2:] for n in nodes if n.startswith('D:'))
    if dois: return 'DOI:'+dois[0]
    pmids=sorted((n[2:] for n in nodes if n.startswith('P:')), key=lambda z:(int(z),z))
    return 'PMID:'+pmids[0] if pmids else None

def main():
    assert sha(PROTOCOL)=='af8b7373a6ce2de34d0a5185d5d70410b46fbda44af996f922f9fa098e3117dc'
    assert sha(AMEND)=='6932397a6c85ebc8586a9903f55507a9412222d5fd7fa441d2ba1660989b3596'
    assert sha(AMEND_B)=='ce18a89594b4e850e09204ce5b66695340239b9a25b4f09475e660e8376cb4aa'
    raw_sha=sha(RAW); raw_bytes=RAW.stat().st_size
    if raw_sha!=EXPECTED_SHA or raw_bytes!=EXPECTED_BYTES: raise SystemExit('pinned identity mismatch')

    alias=UF(); rows=[]; seen_record=set(); basic=Counter(); invalid_fields=Counter()
    doi_to_pmids=defaultdict(set); pmid_to_dois=defaultdict(set)
    header_ok=False; row_width=Counter()
    with RAW.open('r',encoding='utf-8-sig',newline='') as f:
        rd=csv.reader(f)
        header=next(rd)
        header_ok=(header==EXPECTED_HEADER)
        if not header_ok: raise SystemExit('schema mismatch')
        idx={k:header.index(k) for k in ALLOW}
        for n,row in enumerate(rd,1):
            basic['rows_total']+=1; row_width[len(row)]+=1
            if len(row)!=len(header):
                basic['row_width_mismatch']+=1; continue
            if row[-1] != '':
                raise SystemExit('undocumented trailing column is nonempty')
            # This is the sole semantic gateway. Forbidden cells are never indexed.
            a={k:row[idx[k]] for k in ALLOW}
            rid=a['Record ID'].strip()
            if not rid:
                basic['invalid_record_id']+=1; continue
            if rid in seen_record:
                basic['record_id_collision_later_occurrence']+=1; continue
            seen_record.add(rid)
            od,ods=norm_doi(a['OriginalPaperDOI']); op,ops=norm_pmid(a['OriginalPaperPubMedID'])
            nd,nds=norm_doi(a['RetractionDOI']); np,nps=norm_pmid(a['RetractionPubMedID'])
            invalid_fields['original_doi_'+ods]+=1; invalid_fields['original_pmid_'+ops]+=1
            invalid_fields['notice_doi_'+nds]+=1; invalid_fields['notice_pmid_'+nps]+=1
            on=[]; nn=[]
            if od: on.append(node_doi(od)); alias.add(on[-1])
            if op: on.append(node_pmid(op)); alias.add(on[-1])
            if nd: nn.append(node_doi(nd)); alias.add(nn[-1])
            if np: nn.append(node_pmid(np)); alias.add(nn[-1])
            if od and op:
                alias.union(node_doi(od),node_pmid(op)); doi_to_pmids[od].add(op); pmid_to_dois[op].add(od)
            if nd and np:
                alias.union(node_doi(nd),node_pmid(np)); doi_to_pmids[nd].add(np); pmid_to_dois[np].add(nd)
            if not on and not nn: basic['missing_both_endpoints']+=1; continue
            if not on: basic['missing_original_endpoint']+=1; continue
            if not nn: basic['missing_notice_endpoint']+=1; continue
            basic['explicit_both_endpoints_rows']+=1
            rows.append({'rid':rid,'on':on,'nn':nn})
    if basic['rows_total']!=EXPECTED_ROWS: raise SystemExit('row count mismatch')

    # Freeze alias roots after every source-declared within-endpoint union.
    root_nodes=defaultdict(set)
    for n in list(alias.p): root_nodes[alias.find(n)].add(n)
    ambiguous_nodes=set()
    for d,ps in doi_to_pmids.items():
        if len(ps)>1: ambiguous_nodes.add(node_doi(d)); ambiguous_nodes.update(node_pmid(p) for p in ps)
    for p,ds in pmid_to_dois.items():
        if len(ds)>1: ambiguous_nodes.add(node_pmid(p)); ambiguous_nodes.update(node_doi(d) for d in ds)
    ambiguous_roots={alias.find(n) for n in ambiguous_nodes}

    role_orig=set(); role_notice=set(); edge_occ=[]
    for r in rows:
        o=alias.find(r['on'][0]); n=alias.find(r['nn'][0])
        role_orig.add(o); role_notice.add(n); edge_occ.append((o,n))
    role_collision_roots=role_orig & role_notice

    # Relation components use only source-declared edges.
    fam=UF()
    for o,n in edge_occ: fam.add(o); fam.add(n); fam.union(o,n)
    component_alias_roots=defaultdict(set)
    for x in set(role_orig)|set(role_notice): component_alias_roots[fam.find(x)].add(x)
    component_flags={}
    for c,ars in component_alias_roots.items():
        fs=[]
        if ars & ambiguous_roots: fs.append('IDENTIFIER_ALIAS_AMBIGUITY')
        if ars & role_collision_roots: fs.append('ORIGINAL_NOTICE_ROLE_COLLISION')
        component_flags[c]=fs

    seen_edges=set(); duplicate_edges=0; unique=[]; self_occ=0
    for o,n in edge_occ:
        if o==n:
            self_occ+=1; continue
        e=(o,n)
        if e in seen_edges:
            duplicate_edges+=1; continue
        seen_edges.add(e); unique.append(e)

    relation_status=Counter(); admitted=[]
    for o,n in unique:
        c=fam.find(o); flags=component_flags[c]
        if 'IDENTIFIER_ALIAS_AMBIGUITY' in flags: relation_status['CANNOT_CHECK_IDENTIFIER_ALIAS_AMBIGUITY']+=1
        elif 'ORIGINAL_NOTICE_ROLE_COLLISION' in flags: relation_status['CANNOT_CHECK_ORIGINAL_NOTICE_ROLE_COLLISION']+=1
        else: relation_status['ADMITTED_EXPLICIT_RW_CC0_RELATION']+=1; admitted.append((o,n))
    relation_status['CANNOT_CHECK_SELF_RELATION_OCCURRENCES']=self_occ
    relation_status['DUPLICATE_RELATION_KEY_LATER_OCCURRENCES']=duplicate_edges

    admitted_components=defaultdict(list)
    for e in admitted: admitted_components[fam.find(e[0])].append(e)
    family_relation_multiplicity=Counter(len(es) for es in admitted_components.values())
    endpoint_mode=Counter(); both_pmids=0; both_dois=0
    runtime_families=[]
    for c,es in admitted_components.items():
        orig_roots={o for o,n in es}; notice_roots={n for o,n in es}
        orig_nodes=set().union(*(root_nodes[x] for x in orig_roots)); notice_nodes=set().union(*(root_nodes[x] for x in notice_roots))
        roots=[]
        for o in orig_roots:
            k=endpoint_key(root_nodes[o])
            if k: roots.append(k)
        canonical=min((k for k in roots if k.startswith('DOI:')),default=None) or min(roots)
        rr=[]
        for o,n in es:
            oks=endpoint_key(root_nodes[o]); nks=endpoint_key(root_nodes[n])
            ohp=any(x.startswith('P:') for x in root_nodes[o]); nhp=any(x.startswith('P:') for x in root_nodes[n])
            ohd=any(x.startswith('D:') for x in root_nodes[o]); nhd=any(x.startswith('D:') for x in root_nodes[n])
            endpoint_mode[('DOI' if ohd else 'PMID')+'_'+('DOI' if nhd else 'PMID')]+=1
            both_pmids += int(ohp and nhp); both_dois += int(ohd and nhd)
            rr.append({'original':{'doi':sorted(x[2:] for x in root_nodes[o] if x.startswith('D:')),'pmid':sorted((x[2:] for x in root_nodes[o] if x.startswith('P:')),key=int)},'notice':{'doi':sorted(x[2:] for x in root_nodes[n] if x.startswith('D:')),'pmid':sorted((x[2:] for x in root_nodes[n] if x.startswith('P:')),key=int)}})
        runtime_families.append({'family_key':canonical,'relations':rr})

    all_comp=Counter()
    for c,ars in component_alias_roots.items():
        flags=component_flags[c]
        if 'IDENTIFIER_ALIAS_AMBIGUITY' in flags: all_comp['CANNOT_CHECK_IDENTIFIER_ALIAS_AMBIGUITY']+=1
        elif 'ORIGINAL_NOTICE_ROLE_COLLISION' in flags: all_comp['CANNOT_CHECK_ORIGINAL_NOTICE_ROLE_COLLISION']+=1
        else: all_comp['ADMITTED_EXPLICIT_RW_CC0_FAMILY']+=1

    result={
      'schema_version':'orion.p1.rw-rights-relation-census-result.v2',
      'identity':'P1.RW.CC0.RIGHTS.RELATION.CENSUS.RESULT.V2',
      'generated_at_utc':datetime.now(timezone.utc).isoformat(),
      'authority':'OUTCOME_BLIND_METADATA_RELATION_CENSUS_ONLY',
      'protocol':{'path':PROTOCOL.name,'sha256':sha(PROTOCOL),'amendment_path':AMEND.name,'amendment_sha256':sha(AMEND),'schema_amendment_path':AMEND_B.name,'schema_amendment_sha256':sha(AMEND_B)},
      'source':{'commit':'7bb2ced143b764974c53c6c61abfdd2379f5307d','git_blob':'40a049f02044fab8286c0304fd296bf1fa2cb8ca','sha256':raw_sha,'bytes':raw_bytes,'header_exact_match':header_ok,'data_rows':basic['rows_total'],'row_width_counts':{str(k):v for k,v in sorted(row_width.items())}},
      'gateway':{'semantic_allowlist':ALLOW,'forbidden_columns_opened_or_used':False,'forbidden_columns_persisted_or_aggregated':False,'case_text_accessed':False,'action_or_outcome_column_accessed':False,'raw_transport_will_be_deleted':True},
      'row_level_structural_counts':dict(sorted(basic.items())),
      'identifier_field_counts':dict(sorted(invalid_fields.items())),
      'alias_audit':{'alias_components':len(root_nodes),'doi_to_multiple_pmid_keys':sum(len(v)>1 for v in doi_to_pmids.values()),'pmid_to_multiple_doi_keys':sum(len(v)>1 for v in pmid_to_dois.values()),'ambiguous_alias_components':len(ambiguous_roots),'original_notice_role_collision_alias_components':len(role_collision_roots)},
      'relation_census':{'unique_nonself_explicit_relations_before_component_gates':len(unique),'status_counts':dict(sorted(relation_status.items())),'admitted_explicit_rw_cc0_relations':len(admitted),'admitted_relations_with_both_endpoint_pmids':both_pmids,'admitted_relations_with_both_endpoint_dois':both_dois,'endpoint_preferred_key_mode_counts':dict(sorted(endpoint_mode.items()))},
      'family_census':{'source_connected_components_before_gates':len(component_alias_roots),'status_counts':dict(sorted(all_comp.items())),'admitted_explicit_rw_cc0_source_families':len(admitted_components),'family_relation_multiplicity':{str(k):v for k,v in sorted(family_relation_multiplicity.items())}},
      'rights':{'rw_allowlisted_metadata_license':'CC0','rw_blob_identity_pass':True,'admitted_relation_metadata_rights_pass':len(admitted),'admitted_family_metadata_rights_pass':len(admitted_components),'linked_content_rights_assessed':False,'content_rights_admissible_pairs':0},
      'typed_feasibility':{'rw_action_columns_opened':False,'source_native_action_cells_assigned':0,'scientific_terminal_cells_assigned':0,'state':'CANNOT_CHECK_PENDING_OFFICIAL_EPMC_AGGREGATE_ONLY_METADATA_REDUCER'},
      'claim_boundary':'The pinned CC0 database contains the reported exact count of explicit, source-declared identifier relations and source-connected metadata families after frozen structural gates. This is a positive metadata-relation existence/prevalence result only; it is not linked-content admission, scientific action gold, causal responsibility, case construct validity, model evidence, transport, or external authority.',
      'current_terminal':'P1_RW_CC0_EXPLICIT_METADATA_RELATION_CENSUS_PASS__CONTENT_RIGHTS_AND_TYPED_FEASIBILITY_CANNOT_CHECK'
    }
    (LANE/'RW_RELATION_CENSUS_RESULT_V2.json').write_text(json.dumps(result,indent=2,sort_keys=True)+'\n')
    (LANE/'.runtime/allowlisted_families_v2.json').write_text(json.dumps({'families':runtime_families},separators=(',',':')))
    print(json.dumps({'rows':basic['rows_total'],'relations':len(admitted),'families':len(admitted_components),'both_pmids':both_pmids,'status':result['current_terminal']},sort_keys=True))

if __name__=='__main__': main()

#!/usr/bin/env python3
from __future__ import annotations
import argparse, concurrent.futures as cf, hashlib, json, re, threading, time
import urllib.parse, urllib.request
import xml.etree.ElementTree as ET
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path

LANE=Path(__file__).resolve().parent
INPUT=LANE/'.runtime/allowlisted_families_v2.json'
CACHE=LANE/'.runtime/epmc_search_cache_v2.json'
PREFREEZE=LANE/'EPMC_AGGREGATE_RIGHTS_REDUCER_PREFREEZE_V2.json'
CORE_AMEND=LANE/'EPMC_CORE_LICENSE_GATEWAY_AMENDMENT_C_V2.json'
EPMC='https://www.ebi.ac.uk/europepmc/webservices/rest/search'
OA='https://www.ncbi.nlm.nih.gov/pmc/utils/oa/oa.fcgi'
UA='Orion-P1-metadata-rights-census/2.0 (research aggregate; no content retrieval)'
LIC='OPEN_ACCESS:Y AND IN_PMC:Y AND (LICENSE:"cc0" OR LICENSE:"cc by" OR LICENSE:"cc by-sa") AND NOT (LICENSE:"cc by-nd" OR LICENSE:"cc by-nc" OR LICENSE:"cc by-nc-nd" OR LICENSE:"cc by-nc-sa")'
STRATA={
 'EPMC_RETRACTION_NOTICE':'PUB_TYPE:"Retraction of Publication"',
 'EPMC_CORRECTION_OR_ERRATUM':'(PUB_TYPE:"Correction" OR PUB_TYPE:"Published Erratum")',
 'EPMC_EXPRESSION_OF_CONCERN':'PUB_TYPE:"Expression of Concern"'
}

def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def chunks(xs,n=80):
    xs=sorted(xs,key=int)
    for i in range(0,len(xs),n): yield xs[i:i+n]

def get_bytes(url, timeout=45, retries=4):
    err=None
    for k in range(retries):
        try:
            req=urllib.request.Request(url,headers={'User-Agent':UA,'Accept':'application/json, application/xml;q=0.9'})
            with urllib.request.urlopen(req,timeout=timeout) as z: return z.read()
        except Exception as e:
            err=e; time.sleep(min(8,0.7*(2**k)))
    raise RuntimeError(f'request failed after {retries}: {type(err).__name__}: {err}')

def query_chunk(pmids, extra):
    ids=' OR '.join('EXT_ID:'+x for x in pmids)
    q=f'({ids}) AND SRC:MED AND {extra}'
    u=EPMC+'?'+urllib.parse.urlencode({'query':q,'resultType':'idlist','format':'json','pageSize':1000,'synonym':'false','cursorMark':'*'})
    b=get_bytes(u); x=json.loads(b)
    if str(x.get('version'))!='6.9': raise RuntimeError('provider version drift')
    if int(x.get('hitCount',0))>len(pmids): raise RuntimeError('unexpected nonunique PMID hit count')
    out={}
    for r in x.get('resultList',{}).get('result',[]):
        # idlist-only response; semantically inspect identifiers only.
        if r.get('source')!='MED': raise RuntimeError('unexpected source')
        ident=str(r.get('id',''))
        if ident not in pmids: raise RuntimeError('returned identifier outside query')
        pmcid=r.get('pmcid')
        if pmcid: out.setdefault(ident,set()).add(str(pmcid))
    return out, hashlib.sha256(b).hexdigest(), int(x.get('hitCount',0))

def parallel_search(pmids, extra, workers=4):
    batches=list(chunks(pmids)); merged=defaultdict(set); hashes=[]; hit_sum=0; errors=[]
    def one(batch):
        time.sleep(0.05)
        return query_chunk(batch,extra)
    with cf.ThreadPoolExecutor(max_workers=workers) as ex:
        fs={ex.submit(one,b):b for b in batches}
        for fut in cf.as_completed(fs):
            try: out,h,n=fut.result(); hashes.append(h); hit_sum+=n
            except Exception as e: errors.append({'batch_size':len(fs[fut]),'error':str(e)}); continue
            for k,v in out.items(): merged[k].update(v)
    if errors: raise RuntimeError(f'EPMC batch failures: {errors[:3]} total={len(errors)}')
    return {k:sorted(v) for k,v in merged.items()}, sorted(hashes), hit_sum, len(batches)

def yes(v): return v is True or str(v).strip().casefold() in {'y','yes','true','1'}

def query_core_chunk(pmids):
    ids=' OR '.join('EXT_ID:'+x for x in pmids)
    q=f'({ids}) AND SRC:MED'
    u=EPMC+'?'+urllib.parse.urlencode({'query':q,'resultType':'core','format':'json','pageSize':1000,'synonym':'false','cursorMark':'*'})
    b=get_bytes(u); x=json.loads(b)
    if str(x.get('version'))!='6.9': raise RuntimeError('provider version drift')
    if int(x.get('hitCount',0))>len(pmids): raise RuntimeError('unexpected nonunique PMID core hit count')
    out={}
    for r in x.get('resultList',{}).get('result',[]):
        # Sealed semantic gateway: never index any field beyond this allowlist.
        if r.get('source')!='MED': raise RuntimeError('unexpected core source')
        ident=str(r.get('id') or r.get('pmid') or '')
        if ident not in pmids: raise RuntimeError('core identifier outside query')
        val={'pmcid':r.get('pmcid'),'license':r.get('license'),'isOpenAccess':r.get('isOpenAccess'),'inPMC':r.get('inPMC')}
        if ident in out: out[ident]={'duplicate':True}
        else: out[ident]=val
    return out,hashlib.sha256(b).hexdigest(),int(x.get('hitCount',0))

def parallel_core(pmids, workers=4):
    batches=list(chunks(pmids)); merged={}; hashes=[]; hit_sum=0; errors=[]
    with cf.ThreadPoolExecutor(max_workers=workers) as ex:
        fs={ex.submit(query_core_chunk,b):b for b in batches}
        for fut in cf.as_completed(fs):
            try: out,h,n=fut.result(); hashes.append(h); hit_sum+=n
            except Exception as e: errors.append({'batch_size':len(fs[fut]),'error':str(e)}); continue
            merged.update(out)
    if errors: raise RuntimeError(f'EPMC core batch failures: {errors[:3]} total={len(errors)}')
    return merged,sorted(hashes),hit_sum,len(batches)

class RateLimiter:
    def __init__(self, interval): self.interval=interval; self.lock=threading.Lock(); self.last=0.0
    def wait(self):
        with self.lock:
            now=time.monotonic(); delay=self.interval-(now-self.last)
            if delay>0: time.sleep(delay)
            self.last=time.monotonic()

def normalize_license(x):
    if not x: return 'CANNOT_CHECK_MISSING_LICENSE'
    s=' '.join(x.upper().replace('_','-').split())
    s=re.sub(r'[- ]+',' ',s).strip()
    toks=s.split()
    if toks==['CC0'] or (len(toks)==2 and toks[0]=='CC0' and re.fullmatch(r'\d+(?:\.\d+)?',toks[1])): return 'ALLOW_CC0'
    if len(toks) in (2,3) and toks[:2]==['CC','BY'] and (len(toks)==2 or re.fullmatch(r'\d+(?:\.\d+)?',toks[2])): return 'ALLOW_CC_BY'
    if len(toks) in (3,4) and toks[:3]==['CC','BY','SA'] and (len(toks)==3 or re.fullmatch(r'\d+(?:\.\d+)?',toks[3])): return 'ALLOW_CC_BY_SA'
    if 'NC' in toks or 'ND' in toks: return 'EXCLUDE_NC_OR_ND'
    return 'CANNOT_CHECK_CUSTOM_OR_UNPARSED_LICENSE'

def oa_one(pmcid, limiter):
    limiter.wait(); u=OA+'?'+urllib.parse.urlencode({'id':pmcid}); b=get_bytes(u)
    root=ET.fromstring(b); rec=root.find('records/record')
    if rec is None: return pmcid,'CANNOT_CHECK_NO_OA_RECORD',None,hashlib.sha256(b).hexdigest()
    if rec.get('id')!=pmcid: return pmcid,'CANNOT_CHECK_OA_ID_MISMATCH',None,hashlib.sha256(b).hexdigest()
    lic=rec.get('license'); return pmcid,normalize_license(lic),lic,hashlib.sha256(b).hexdigest()

def wave(k): return 'PRIMARY' if int(hashlib.sha256(k.encode()).hexdigest()[:16],16)%2==0 else 'REPLICATION'

def main():
    ap=argparse.ArgumentParser(); ap.add_argument('--search-only',action='store_true'); args=ap.parse_args()
    assert sha(PREFREEZE)=='4a80d9408aa594141f1d9c475a2145b7349ae129a006117c832830071db898c9'
    assert sha(CORE_AMEND)=='70d0591c353fa156d5be4dcfc7640649b10bcc3a6578e98d0f24b538c6783d9d'
    data=json.loads(INPUT.read_text())
    rel=[]
    for f in data['families']:
        for r in f['relations']:
            if r['original']['pmid'] and r['notice']['pmid']:
                rel.append((f['family_key'],r['original']['pmid'][0],r['notice']['pmid'][0]))
    all_pmids={x for _,o,n in rel for x in (o,n)}
    if CACHE.exists(): cache=json.loads(CACHE.read_text())
    else:
        hits,hs,hit_sum,batches=parallel_search(all_pmids,LIC)
        cache={'generated_at_utc':datetime.now(timezone.utc).isoformat(),'input_relations_with_both_pmids':len(rel),'unique_endpoint_pmids':len(all_pmids),'allowlist_search_matches':hits,'response_hashes':hs,'hit_count_sum':hit_sum,'batches':batches}
        CACHE.write_text(json.dumps(cache,separators=(',',':')))
    hits=cache['allowlist_search_matches']
    candidate_pmids={k for k,v in hits.items() if len(v)==1}; ambiguous_pmids={k for k,v in hits.items() if len(v)>1}
    candidate_pmcids={hits[p][0] for p in candidate_pmids}
    print(json.dumps({'relations_with_both_pmids':len(rel),'unique_pmids':len(all_pmids),'search_match_pmids':len(candidate_pmids),'ambiguous_match_pmids':len(ambiguous_pmids),'unique_candidate_pmcids':len(candidate_pmcids)},sort_keys=True))
    if args.search_only: return

    core,core_hashes,core_hit_sum,core_batches=parallel_core(candidate_pmids)
    core_status={}; core_raw_license=Counter(); core_pmcid={}
    for p in candidate_pmids:
        r=core.get(p)
        if not r: core_status[p]='CANNOT_CHECK_CORE_ABSENCE'; continue
        if r.get('duplicate'): core_status[p]='CANNOT_CHECK_MULTIPLE_CORE_ROWS'; continue
        if not r.get('pmcid'): core_status[p]='CANNOT_CHECK_CORE_MISSING_PMCID'; continue
        if not yes(r.get('isOpenAccess')) or not yes(r.get('inPMC')): core_status[p]='CANNOT_CHECK_CORE_OA_OR_PMC_FLAG'; continue
        s=normalize_license(r.get('license')); core_status[p]=s; core_pmcid[p]=str(r.get('pmcid')); core_raw_license[r.get('license') or '<MISSING>']+=1
    allowed={'ALLOW_CC0','ALLOW_CC_BY','ALLOW_CC_BY_SA'}
    pmid_rights=core_status
    relation_stage=Counter(); pass_rel=[]
    for fam,o,n in rel:
        if o in ambiguous_pmids or n in ambiguous_pmids: relation_stage['CANNOT_CHECK_EPMC_MULTIPLE_PMCID_RESOLUTION']+=1; continue
        if o not in pmid_rights or n not in pmid_rights: relation_stage['CANNOT_CHECK_EPMC_ALLOWLIST_SEARCH_ABSENCE']+=1; continue
        if pmid_rights[o] not in allowed or pmid_rights[n] not in allowed: relation_stage['CANNOT_CHECK_OR_EXCLUDE_EXACT_LICENSE']+=1; continue
        if core_pmcid.get(o)==core_pmcid.get(n): relation_stage['CANNOT_CHECK_EPMC_ENDPOINT_RESOLUTION_COLLISION']+=1; continue
        relation_stage['EXACT_BOTH_ENDPOINT_CONTENT_RIGHTS_PASS']+=1; pass_rel.append((fam,o,n))
    no_both_pmids=sum(len(f['relations']) for f in data['families'])-len(rel)
    relation_stage['CANNOT_CHECK_NO_BOTH_PMID_FOR_BOUNDED_REDUCER']=no_both_pmids

    notice_pmids={n for _,o,n in pass_rel}; membership={}; stratum_meta={}
    for sid,clause in STRATA.items():
        hit,hs,hit_sum,batches=parallel_search(notice_pmids,clause)
        membership[sid]=set(hit); stratum_meta[sid]={'matched_notice_pmids':len(hit),'hit_count_sum':hit_sum,'batches':batches,'response_sha256_multiset_digest':hashlib.sha256(('\n'.join(hs)+'\n').encode()).hexdigest()}
    relation_cells=Counter(); family_cells=defaultdict(set); wave_families=defaultdict(set)
    for fam,o,n in pass_rel:
        bands=[s for s,m in membership.items() if n in m]
        cell=bands[0] if len(bands)==1 else ('EPMC_OTHER_OR_CANNOT_CHECK' if not bands else 'EPMC_AMBIGUOUS_MULTIPLE_STRATA')
        relation_cells[cell]+=1; family_cells[cell].add(fam); wave_families[(cell,wave(fam))].add(fam)
    typed={}
    for cell in list(STRATA)+['EPMC_OTHER_OR_CANNOT_CHECK','EPMC_AMBIGUOUS_MULTIPLE_STRATA']:
        p=len(wave_families[(cell,'PRIMARY')]); r=len(wave_families[(cell,'REPLICATION')])
        typed[cell]={'exact_rights_pass_relations':relation_cells[cell],'unique_source_families':len(family_cells[cell]),'primary_families':p,'replication_families':r,'minimum_20_families_each_wave_pass':p>=20 and r>=20}

    exact_family={fam for fam,o,n in pass_rel}
    result={
      'schema_version':'orion.p1.epmc-rights-reducer-result.v2','identity':'P1.RW.EPMC.RIGHTS.TYPED.FEASIBILITY.RESULT.V2','generated_at_utc':datetime.now(timezone.utc).isoformat(),'authority':'OFFICIAL_METADATA_RIGHTS_AND_SOURCE_NATIVE_AGGREGATE_TYPE_FEASIBILITY_ONLY',
      'protocol':{'path':PREFREEZE.name,'sha256':sha(PREFREEZE)},
      'input':{'admitted_rw_cc0_relations':sum(len(f['relations']) for f in data['families']),'admitted_rw_cc0_families':len(data['families']),'relations_with_both_endpoint_pmids':len(rel),'unique_endpoint_pmids_queried':len(all_pmids)},
      'search_stage':{'epmc_provider_version':'6.9','batches':cache['batches'],'hit_count_sum':cache['hit_count_sum'],'unique_pmids_with_one_allowlist_search_match':len(candidate_pmids),'unique_pmids_with_multiple_pmcid_matches':len(ambiguous_pmids),'unique_candidate_pmcids':len(candidate_pmcids),'response_sha256_multiset_digest':hashlib.sha256(('\n'.join(cache['response_hashes'])+'\n').encode()).hexdigest(),'absence_interpretation':'CANNOT_CHECK, never incompatible rights or negative science'},
      'epmc_core_exact_rights':{'amendment_path':CORE_AMEND.name,'amendment_sha256':sha(CORE_AMEND),'unique_pmids_queried':len(candidate_pmids),'batches':core_batches,'hit_count_sum':core_hit_sum,'normalized_status_counts':dict(sorted(Counter(core_status.values()).items())),'raw_license_aggregate_counts':dict(sorted(core_raw_license.items())),'response_sha256_multiset_digest':hashlib.sha256(('\n'.join(core_hashes)+'\n').encode()).hexdigest(),'case_text_or_forbidden_fields_semantically_accessed':False,'raw_payloads_persisted':False},
      'relation_feasibility':{'status_counts':dict(sorted(relation_stage.items())),'exact_both_endpoint_content_rights_pass_relations':len(pass_rel),'exact_rights_pass_unique_source_families':len(exact_family)},
      'source_native_aggregate_stratum_query_receipts':stratum_meta,
      'typed_feasibility_cells':typed,
      'typed_boundary':{'rw_action_columns_opened':False,'identifier_to_type_mapping_persisted':False,'publication_type_is_scientific_terminal_or_gold':False,'scientific_terminal_cells_assigned':0,'case_text_accessed':False,'model_or_comparator_executed':False,'protected_scores_accessed':False},
      'positive_result':'The exact-rights-pass relations/families and nonempty provider-native strata demonstrate a rights-valid public construction pool under frozen metadata-only rules. They do not demonstrate that anti-leak candidate evidence or independently adjudicated minimal scientific actions exist.',
      'current_terminal':'P1_RW_EPMC_RIGHTS_VALID_RELATION_AND_SOURCE_NATIVE_TYPED_FEASIBILITY_PASS__SCIENTIFIC_ACTION_GOLD_AND_CONSTRUCT_VALIDITY_CANNOT_CHECK' if pass_rel else 'P1_RW_EPMC_RIGHTS_VALID_RELATION_FEASIBILITY_CANNOT_CHECK_ZERO_EXACT_PAIR',
      'raw_or_temporary_payloads_retained':False
    }
    (LANE/'EPMC_RIGHTS_TYPED_FEASIBILITY_RESULT_V2.json').write_text(json.dumps(result,indent=2,sort_keys=True)+'\n')
    print(json.dumps({'exact_relations':len(pass_rel),'exact_families':len(exact_family),'cells':typed,'terminal':result['current_terminal']},sort_keys=True))

if __name__=='__main__': main()

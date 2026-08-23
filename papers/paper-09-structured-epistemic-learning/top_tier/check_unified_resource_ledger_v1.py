#!/usr/bin/env python3
"""Independent schema/information-preservation audit for P9 resource ledger."""
from __future__ import annotations
import hashlib,json,sys
from pathlib import Path
FIELDS=("I_sem","A_dim","A_transform","M_state","C_fit","C_infer","C_explicit","R_registered")
def main():
    path=Path(sys.argv[1]) if len(sys.argv)>1 else Path('p9_unified_resource_ledger_v1.json')
    p=json.loads(path.read_text());rows=p['rows'];assert p['terminal']=='P9_UNIFIED_RESOURCE_LEDGER_V1_GREEN'
    assert len(rows)==15 and p['scalarization']=='PROHIBITED'
    keys={(r['task'],r['intervention']) for r in rows};assert len(keys)==15
    by={(r['task'],r['intervention']):r for r in rows}
    for r in rows:
        assert all(f in r and isinstance(r[f],(int,float)) for f in FIELDS),(r,FIELDS)
        assert all(r[f]>=0 for f in FIELDS)
    for task in ('D-A','D-I','B-I','B-A','B-C'):
        assert by[(task,'ACCESSIBILITY')]['I_sem']==by[(task,'COMPUTATION')]['I_sem']
    assert by[('D-I','INFORMATION')]['I_sem']>by[('D-I','COMPUTATION')]['I_sem']
    assert by[('B-I','INFORMATION')]['I_sem']>by[('B-I','COMPUTATION')]['I_sem']
    # Learned arms must expose fit and model-state cost. Exact computation tasks must expose explicit work.
    assert all(r['C_fit']>0 and r['M_state']>0 for r in rows if r['task'].startswith('D-'))
    assert all(by[(t,'COMPUTATION')]['C_explicit']>0 for t in ('B-I','B-A','B-C'))
    assert p['decisions']['D-A']=={'predicted':'ACCESSIBILITY','protected_gold':'CANNOT_CHECK'}
    receipt={'schema':'P9.UnifiedResourceLedgerIndependent.v1','source_receipt_sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'row_count':15,'information_preservation_green':True,'full_vector_green':True,'scalarization_prohibited':True,'terminal':'P9_UNIFIED_RESOURCE_LEDGER_SECOND_CHECKER_GREEN'}
    raw=json.dumps(receipt,sort_keys=True,separators=(',',':')).encode();receipt['receipt_sha256']=hashlib.sha256(raw).hexdigest();print(json.dumps(receipt,indent=2,sort_keys=True));return 0
if __name__=='__main__':raise SystemExit(main())

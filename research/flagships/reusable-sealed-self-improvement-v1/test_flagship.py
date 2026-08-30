import hashlib,json,subprocess,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parent
def test_rebuild_and_check(tmp_path):
 c=tmp_path/'control.json';g=tmp_path/'generic.json'
 p=subprocess.run([sys.executable,str(ROOT/'build_controls.py'),'--output',str(c)],capture_output=True,text=True)
 assert p.returncode==0 and c.read_bytes()==(ROOT/'CONTROL_RESULT.json').read_bytes()
 q=subprocess.run([sys.executable,str(ROOT/'independent_checker/check_controls.py'),'--output',str(g)],capture_output=True,text=True)
 assert q.returncode==0 and g.read_bytes()==(ROOT/'GENERIC_RESULT.json').read_bytes()
def test_authority_and_hostile_terminals():
 r=json.loads((ROOT/'GENERIC_RESULT.json').read_text());assert r['decision']=='CONTROL_PLANE_VERIFIED__EMPIRICAL_CAMPAIGN_NOT_RUN';assert all(r['checks'].values())
 assert r['protected_transfer_authority'] is False and r['submission_authority'] is False
 t={k:v['observed']['terminal'] for k,v in r['fixtures'].items()}
 assert t['valid_promotion']=='CONTROL_PROMOTED';assert t['replay_only_rejected']=='CONTROL_REJECTED';assert t['alpha_budget_overrun_blocked']=='LEDGER_BLOCKED';assert t['negative_history_deletion_blocked']=='LEDGER_BLOCKED'
def test_manifest():
 m=json.loads((ROOT/'SOURCE_MANIFEST.json').read_text())
 for row in m['files']:assert hashlib.sha256((ROOT/row['path']).read_bytes()).hexdigest()==row['sha256']

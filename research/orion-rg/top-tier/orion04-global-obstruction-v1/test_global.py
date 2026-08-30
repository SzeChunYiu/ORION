from __future__ import annotations
import hashlib,json,shutil,subprocess,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parent
def canon(x):return json.dumps(x,sort_keys=True,separators=(',',':'),allow_nan=False)
def sha(s):return hashlib.sha256(s.encode()).hexdigest()
def run(path,*args):return subprocess.run([sys.executable,str(path),*map(str,args)],capture_output=True,text=True)
def test_static_and_result_checkers_accept():
 for p in [ROOT/'independent_checker/check_static.py',ROOT/'independent_checker/check_full_cover.py',ROOT/'independent_checker/check_result.py']:
  q=run(p);assert q.returncode==0,q.stdout+q.stderr
def test_missing_result_branch_is_rejected(tmp_path):
 dst=tmp_path/'packet';shutil.copytree(ROOT,dst);p=dst/'RESULT.json';r=json.loads(p.read_text());r['runs'].pop();r['branches'].pop();u=dict(r);u.pop('result_digest',None);r['result_digest']=sha(canon(u));p.write_text(json.dumps(r,indent=2,sort_keys=True)+'\n');q=run(dst/'independent_checker/check_result.py');assert q.returncode!=0
def test_source_mutation_is_rejected(tmp_path):
 dst=tmp_path/'packet';shutil.copytree(ROOT,dst);p=dst/'engine_high_u128.c';p.write_text(p.read_text()+'\n/* hostile byte */\n');q=run(dst/'independent_checker/check_result.py');assert q.returncode!=0
def test_missing_cover_branch_is_rejected(tmp_path):
 dst=tmp_path/'packet';shutil.copytree(ROOT,dst);p=dst/'FULL_CUBE_COVER.json';r=json.loads(p.read_text());r['lower_branches'].pop();u=dict(r);u.pop('digest',None);r['digest']=sha(canon(u));p.write_text(json.dumps(r,indent=2,sort_keys=True)+'\n');q=run(dst/'independent_checker/check_full_cover.py');assert q.returncode!=0
def test_removed_zero_detection_produces_false_survivor(tmp_path):
 src=(ROOT/'engine_high_u128.c').read_text().replace('if(z&ONE)return 0;','/* hostile mutation */');c=tmp_path/'m.c';x=tmp_path/'m';c.write_text(src)
 cc=subprocess.run(['gcc','-std=gnu11','-O3','-march=native','-Wall','-Wextra','-Werror',str(c),'-o',str(x)],capture_output=True,text=True);assert cc.returncode==0,cc.stderr
 q=subprocess.run([str(x),'1','11','2','4','4','2','0'],capture_output=True,text=True);assert q.returncode==1;assert 'solutions=1' in q.stdout

def test_source_manifest_binds_all_nonself_files():
    m=json.loads((ROOT/'SOURCE_MANIFEST.json').read_text())
    observed=[]
    for p in sorted(ROOT.rglob('*')):
        if p.is_file() and p.name!='SOURCE_MANIFEST.json' and '.pytest_cache' not in p.parts and '__pycache__' not in p.parts:
            observed.append(p.relative_to(ROOT).as_posix())
    assert observed==[x['path'] for x in m['files']]
    for row in m['files']:
        p=ROOT/row['path'];assert p.stat().st_size==row['size'];assert hashlib.sha256(p.read_bytes()).hexdigest()==row['sha256']

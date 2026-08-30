from __future__ import annotations
import subprocess,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
P=ROOT/'research/orion-rg/top-tier/orion04-global-obstruction-v1'
def test_committed_global_packet():
 for rel in ['independent_checker/check_static.py','independent_checker/check_full_cover.py','independent_checker/check_result.py']:
  q=subprocess.run([sys.executable,str(P/rel)],cwd=ROOT,capture_output=True,text=True)
  assert q.returncode==0,q.stdout+q.stderr
 q=subprocess.run([sys.executable,'-m','pytest','-q',str(P/'test_global.py')],cwd=ROOT,capture_output=True,text=True)
 assert q.returncode==0,q.stdout+q.stderr

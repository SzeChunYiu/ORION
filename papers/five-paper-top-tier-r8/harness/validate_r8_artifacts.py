from __future__ import annotations
import hashlib, json, sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
EXPECTED={
 "AB/artifact/xor_production_separation_r8.py":"379c58e0d4a209a59d738035578879d06db82949b2ae95617ecb5d611bab226f",
 "AB/artifact/XOR_PRODUCTION_SEPARATION_R8_RESULTS.json":"e2670cf73c30e409f52b6270a5f66a5612856f4093fc3580c1ee4574767283a5",
 "C/artifact/fiberguard_r8.py":"2229377f3ea33211fd1658068b81ec4e11cc8d661351a4b57abdbdea47885084",
 "C/artifact/FIBERGUARD_R8_RESULTS.json":"b6cbcd28fab0754750d65e1d98c3b218581aa2f4c4a814bc4685fe70563b2eaa",
 "D/artifact/typed_authority_merge_r8.py":"5716bf32e2df2a951cf0459ba895311d317900b6ba842045356ef55f2ba8d58b",
 "D/artifact/TYPED_AUTHORITY_MERGE_R8_RESULTS.json":"c9fb232f7675b811bab64df07ab77ea01784e495977e0f0e367e407206130eca",
}
rows=[]
for rel,want in EXPECTED.items():
 p=ROOT/rel
 got=hashlib.sha256(p.read_bytes()).hexdigest()
 rows.append({"path":rel,"sha256":got,"match":got==want})
 if got!=want:
  raise SystemExit(f"hash mismatch {rel}: {got} != {want}")
for rel in ["AB/artifact/XOR_PRODUCTION_SEPARATION_R8_RESULTS.json","C/artifact/FIBERGUARD_R8_RESULTS.json","D/artifact/TYPED_AUTHORITY_MERGE_R8_RESULTS.json"]:
 json.loads((ROOT/rel).read_text())
out={"schema":"ORION.FivePaperR8.ArtifactValidation.v1","status":"PASS","files":rows}
print(json.dumps(out,indent=2,sort_keys=True))

from __future__ import annotations
import json
from orion.study.p9.s3_shape_ablation import run_shape_ablation

if __name__ == "__main__":
    result=run_shape_ablation()
    print(json.dumps(result,sort_keys=True))

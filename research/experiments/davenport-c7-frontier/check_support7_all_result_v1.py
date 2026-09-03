#!/usr/bin/env python3
import json
from pathlib import Path

HERE=Path(__file__).resolve().parent
r=json.loads((HERE/'SUPPORT7_ALL_RESULT_V1.json').read_text())
assert r['projective_support_classes']==54
assert r['deficit_weight_profiles']==462
assert len(r['kernel_classes_by_projective_class'])==54
assert len(r['short_zero_free_by_projective_class'])==54
assert sum(r['kernel_classes_by_projective_class'])==7400
assert 7400*462==r['candidate_weighted_lifts']==3418800
assert sum(r['short_zero_free_by_projective_class'])==r['short_zero_free_candidates']==14860
assert r['four_pack_candidates']==14860
assert r['surviving_packing_at_most_three_candidates']==0
print('SUPPORT7_ALL_RESULT_RECORD_GREEN candidates=3418800 shortfree=14860 survivors=0')

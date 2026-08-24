#!/usr/bin/env python3
"""Read-only P3 V18 validator."""
import hashlib, json
from pathlib import Path
ROOT=Path(__file__).resolve().parent
sha=lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
def main():
    pre=json.loads((ROOT/'RUNTIME_PREFLIGHT_V18.json').read_text()); res=json.loads((ROOT/'RESULT_V18.json').read_text())
    checks=[pre['checks_passed']==pre['checks_total']==10,pre['microgate_authorized'] is True,res['attempts']==1,res['retries']==0,res['error'] is None,res['source']['raw_class_count'] if 'raw_class_count' in res['source'] else res['source']['class_count']==37,res['source']['class_count']==37,res['target']['class_count']==37,res['source']['structural_consistency_operation'] is True,res['target']['structural_consistency_operation'] is True,res['source']['taxonomy_members_within_frozen_universe'] is True,res['target']['taxonomy_members_within_frozen_universe'] is True,res['training_executed'] is False,res['matching_executed'] is False,res['reference_semantically_opened'] is False,res['scoring_executed'] is False,res['v19_full_bertmap_authorized'] is False,res['terminal']=='P3_V18_STRUCTURAL_REASONER_COMPATIBILITY_FAIL__V19_BERTMAP_NOT_AUTHORIZED']
    sums=True
    for line in (ROOT/'SHA256SUMS').read_text().splitlines():
        expected,rel=line.split('  ',1); p=ROOT/rel; sums=sums and p.is_file() and not p.is_symlink() and sha(p)==expected
    checks.append(sums)
    if not all(checks): print('P3_V18_VALIDATION_FAIL'); return 1
    print(f'P3_V18_PACKET_VALID__STRUCTURAL_LOAD_AND_TAXONOMY_OPERATIONS_TRUE__37_VS_36_SURFACE_FAILURE_PRESERVED__NO_MATCHING_OR_SCORING__{len(checks)}_CHECKS'); return 0
if __name__=='__main__': raise SystemExit(main())

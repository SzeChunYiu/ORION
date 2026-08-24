#!/usr/bin/env python3
"""Read-only P3 V19 validator."""
import hashlib, json
from pathlib import Path
ROOT=Path(__file__).resolve().parent
sha=lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
def main():
    pre=json.loads((ROOT/'RUNTIME_PREFLIGHT_V19.json').read_text()); res=json.loads((ROOT/'RESULT_V19.json').read_text())
    checks=[pre['checks_passed']==pre['checks_total']==10,pre['microgate_authorized'] is True,res['attempts']==1,res['retries']==0,res['error'] is None,res['source']['pass'] is True,res['target']['pass'] is True,res['source']['raw_class_count']==res['target']['raw_class_count']==37,res['source']['class_count']==res['target']['class_count']==36,res['source']['nonempty_annotation_class_count']==res['target']['nonempty_annotation_class_count']==33,res['source']['empty_annotation_class_count']==res['target']['empty_annotation_class_count']==3,res['source']['removed_builtin']==res['target']['removed_builtin']=='http://www.w3.org/2002/07/owl#Thing',res['source']['underlying_ontology_axioms_modified'] is False,res['target']['underlying_ontology_axioms_modified'] is False,res['training_executed'] is False,res['matching_executed'] is False,res['reference_semantically_opened'] is False,res['scoring_executed'] is False,res['v20_full_bertmap_authorized'] is True,res['terminal'].startswith('P3_V19_DEEPONTO_BUILTIN_CLASS_SURFACE_PASS__')]
    sums=True
    for line in (ROOT/'SHA256SUMS').read_text().splitlines():
        expected,rel=line.split('  ',1); p=ROOT/rel; sums=sums and p.is_file() and not p.is_symlink() and sha(p)==expected
    checks.append(sums)
    if not all(checks): print('P3_V19_VALIDATION_FAIL'); return 1
    print(f'P3_V19_PACKET_VALID__RAW_37_POSTFILTER_36__33_NONEMPTY_3_EMPTY_LABEL_KEYS__NO_AXIOM_CHANGE_OR_OUTCOME_EXECUTION__{len(checks)}_CHECKS'); return 0
if __name__=='__main__': raise SystemExit(main())

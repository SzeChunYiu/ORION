#!/usr/bin/env python3
"""Read-only P3 V17 validator."""
import hashlib, json
from pathlib import Path
ROOT=Path(__file__).resolve().parent
sha=lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
def main():
    pre=json.loads((ROOT/'RUNTIME_PREFLIGHT_V17.json').read_text()); res=json.loads((ROOT/'BERTMAP_RESULT_V17.json').read_text())
    exact="java.lang.IllegalArgumentException: Non-simple property '<http://co4.inrialpes.fr/align/Contest/101/onto.rdf#isPartOf>' or its inverse appears in the cardinality restriction 'ObjectMaxCardinality(1 <http://co4.inrialpes.fr/align/Contest/101/onto.rdf#isPartOf> owl:Thing)'."
    stderr=(ROOT/'BERTMAP_STDERR_V17.log').read_text()
    checks=[pre['checks_passed']==pre['checks_total']==30,pre['native_execution_authorized'] is True,res['attempts']==1,res['retries']==0,res['native_exit_code']==1,res['native_success'] is False,res['timed_out'] is False,res['five_regular_non_symlink_artifacts'] is False,all(item['regular_non_symlink'] is False for item in res['native_artifacts'].values()),res['typed_decoder_pass'] is False,res['reference_semantically_opened'] is False,res['common_scoring_authorized'] is False,exact in stderr,res['terminal']=='P3_V17_BERTMAP_NATIVE_ATTEMPT_FAIL__NO_RETRY__COMMON_SCORING_NOT_AUTHORIZED']
    sums=True
    for line in (ROOT/'SHA256SUMS').read_text().splitlines():
        expected,rel=line.split('  ',1); p=ROOT/rel; sums=sums and p.is_file() and not p.is_symlink() and sha(p)==expected
    checks.append(sums)
    if not all(checks): print('P3_V17_VALIDATION_FAIL'); return 1
    print(f'P3_V17_PACKET_VALID__30_OF_30_PREFLIGHT__ONE_HERMIT_FAILURE_NO_RETRY__ZERO_NATIVE_ARTIFACTS__REFERENCE_UNOPENED__{len(checks)}_CHECKS'); return 0
if __name__=='__main__': raise SystemExit(main())

# Checker corpus survey — 2026-08-25

Every `check_*.py` under `papers/` executed on LUNARC. Recorded rather than
summarised, because "the checkers pass" is a claim that needs a denominator.

**109 checkers. 84 exit 0. 25 do not.**

Each was run twice: once from its own directory, once from the repository
root. Two that failed the first way pass the second, so they were harness
errors rather than defects — `check_content_binding_v1.py` and
`check_set_normalization_boundary.py` build repo-relative paths and must be
invoked from the root. Reporting them as failures would have been a false
positive, which is why the second pass exists.

## The 25, by cause

### REAL_FAIL — 8

Ran and reported a genuine integrity failure

- `Q-paper-03-dual-instrument/check_q3_completion.py` (exit 1)
  - Q3_COMPLETION_CHECK=FAIL
- `candidates/paper-10-content-bound-math-evaluation/check_p11_peer_review_ready.py` (exit 1)
  - P11_PEER_REVIEW_READY: FAIL: forbidden overclaim matched: discover(?:s|ed)? reus
- `check_q_qg_publication.py` (exit 1)
  - Q_QG_PUBLICATION_CHECK=FAIL
- `check_q_qg_science_manifests.py` (exit 1)
  - Q_QG_SCIENCE_MANIFEST_CHECK=FAIL
- `paper-02-open-world-scientific-discovery/scripts/check_claim_ledger.py` (exit 1)
  - VIOLATION UNLEDGERED_CLAIM: region 'conclusion' asserts an outcome with no ledge
- `paper-02-open-world-scientific-discovery/scripts/check_claim_ledger_v1.py` (exit 1)
  - VIOLATION UNLEDGERED_CLAIM: region 'conclusion' asserts an outcome with no ledge
- `paper-04-verified-scientific-discovery/protocol/check_verdict_leak_v1.py` (exit 1)
  - VERDICT LEAK CHECK: FAIL — 3/39 cases state the verdict
- `paper-06-formal-epistemic-structures-and-mechanics/evidence/independent/check_p6_cleanroom_replay_v1.py` (exit 1)
  -   FAIL every contract/manifest digest recomputes ['papers/paper-06-formal-episte

### ERROR — 13

Cannot run — missing subject artifact or import error

- `candidates/checkers/check_negative_null_history_v1.py` (exit 1)
  - Traceback (most recent call last):
- `candidates/paper-10-content-bound-math-evaluation/check_technical_note_ready.py` (exit 1)
  - Traceback (most recent call last):
- `paper-06-formal-epistemic-structures-and-mechanics/formal/check_certificate_lifting_scope_smt_v1.py` (exit 1)
  - Traceback (most recent call last):
- `paper-09-structured-epistemic-learning/top_tier/check_unified_resource_ledger_v1.py` (exit 1)
  - Traceback (most recent call last):
- `paper-09-structured-epistemic-learning/top_tier/check_unified_resource_ledger_v2.py` (exit 1)
  - Traceback (most recent call last):
- `paper-11-state-as-computation/top_tier/check_decoder_attacks_independent_v1.py` (exit 1)
  - Traceback (most recent call last):
- `paper-11-state-as-computation/top_tier/check_donor_comparator_independent_v1.py` (exit 1)
  - Traceback (most recent call last):
- `paper-11-state-as-computation/top_tier/check_query_family_phase_independent_v1.py` (exit 1)
  - Traceback (most recent call last):
- `paper-12-adaptive-state-reasoning/top_tier/check_p12_robustness_independent_v1.py` (exit 1)
  - Traceback (most recent call last):
- `paper-12-adaptive-state-reasoning/top_tier/check_transfer_allocation_independent_v1.py` (exit 1)
  - Traceback (most recent call last):
- `paper-15-orion-research-harness/top_tier/check_attestation_composition_independent_v1.py` (exit 1)
  - Traceback (most recent call last):
- `paper-15-orion-research-harness/top_tier/check_attestation_composition_independent_v2.py` (exit 1)
  - Traceback (most recent call last):
- `paper-15-orion-research-harness/top_tier/check_provenance_interop_independent_v1.py` (exit 1)
  - Traceback (most recent call last):

### OTHER — 4

Non-zero exit without a matched message

- `candidates/checkers/check_p9_p10_claim_boundary.py` (exit 1)
- `paper-02-open-world-scientific-discovery/scripts/check_manuscript_typography.py` (exit 2)
  - check_manuscript_typography.py: error: the following arguments are required: --l
- `paper-02-open-world-scientific-discovery/scripts/check_p2_v2.py` (exit 1)
- `paper-12-adaptive-state-reasoning/top_tier/check_p12_price_aware_successor_independent_v1.py` (exit 1)

## The finding that matters most

Eight of the thirteen ERROR checkers fail on `FileNotFoundError` for a JSON
subject that **does not exist anywhere in the repository**:

```
p9_unified_resource_ledger_v1.json    p9_unified_resource_ledger_v2.json
p11_decoder_attack_v1.json            p11_donor_comparator_v1.json
p12_robustness_stress_v1.json         p12_transfer_allocation_v1.json
p15_attestation_composition_v1.json   p15_attestation_composition_v2.json
```

These are the *independent* checkers for P9, P11, P12 and P15 — the layer
that exists to verify those papers' top-tier results from outside the code
that produced them.

They have never been run against real output, because the output was never
committed. That is a different and worse problem than a checker that runs
and fails: a checker that fails has looked at something. These have no
subject at all, so their silence has been read as coverage.

## Reproducing

```bash
find papers -name 'check_*.py' | while read c; do
  (cd "$(dirname "$c")" && python "$(basename "$c")") >/dev/null 2>&1 \
    || python "$c" >/dev/null 2>&1 \
    || echo "FAIL $c"
done
```


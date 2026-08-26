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

- `orion-07-dual-instrument/check_q3_completion.py` (exit 1)
  - Q3_COMPLETION_CHECK=FAIL
- `candidates/paper-10-content-bound-math-evaluation/check_p11_peer_review_ready.py` (exit 1)
  - P11_PEER_REVIEW_READY: FAIL: forbidden overclaim matched: discover(?:s|ed)? reus
- `check_q_qg_publication.py` (exit 1)
  - Q_QG_PUBLICATION_CHECK=FAIL
- `check_q_qg_science_manifests.py` (exit 1)
  - Q_QG_SCIENCE_MANIFEST_CHECK=FAIL
- `orion-12-open-world-scientific-discovery/scripts/check_claim_ledger.py` (exit 1)
  - VIOLATION UNLEDGERED_CLAIM: region 'conclusion' asserts an outcome with no ledge
- `orion-12-open-world-scientific-discovery/scripts/check_claim_ledger_v1.py` (exit 1)
  - VIOLATION UNLEDGERED_CLAIM: region 'conclusion' asserts an outcome with no ledge
- `orion-14-verified-scientific-discovery/protocol/check_verdict_leak_v1.py` (exit 1)
  - VERDICT LEAK CHECK: FAIL — 3/39 cases state the verdict
- `orion-16-formal-epistemic-structures-and-mechanics/evidence/independent/check_p6_cleanroom_replay_v1.py` (exit 1)
  -   FAIL every contract/manifest digest recomputes ['papers/orion-16-formal-epistemic-structures-and-mechanics

### ERROR — 13

Cannot run — missing subject artifact or import error

- `candidates/checkers/check_negative_null_history_v1.py` (exit 1)
  - Traceback (most recent call last):
- `candidates/paper-10-content-bound-math-evaluation/check_technical_note_ready.py` (exit 1)
  - Traceback (most recent call last):
- `orion-16-formal-epistemic-structures-and-mechanics/formal/check_certificate_lifting_scope_smt_v1.py` (exit 1)
  - Traceback (most recent call last):
- `orion-19-structured-epistemic-learning/top_tier/check_unified_resource_ledger_v1.py` (exit 1)
  - Traceback (most recent call last):
- `orion-19-structured-epistemic-learning/top_tier/check_unified_resource_ledger_v2.py` (exit 1)
  - Traceback (most recent call last):
- `orion-21-state-as-computation/top_tier/check_decoder_attacks_independent_v1.py` (exit 1)
  - Traceback (most recent call last):
- `orion-21-state-as-computation/top_tier/check_donor_comparator_independent_v1.py` (exit 1)
  - Traceback (most recent call last):
- `orion-21-state-as-computation/top_tier/check_query_family_phase_independent_v1.py` (exit 1)
  - Traceback (most recent call last):
- `orion-22-adaptive-state-reasoning/top_tier/check_p12_robustness_independent_v1.py` (exit 1)
  - Traceback (most recent call last):
- `orion-22-adaptive-state-reasoning/top_tier/check_transfer_allocation_independent_v1.py` (exit 1)
  - Traceback (most recent call last):
- `orion-25-orion-research-harness/top_tier/check_attestation_composition_independent_v1.py` (exit 1)
  - Traceback (most recent call last):
- `orion-25-orion-research-harness/top_tier/check_attestation_composition_independent_v2.py` (exit 1)
  - Traceback (most recent call last):
- `orion-25-orion-research-harness/top_tier/check_provenance_interop_independent_v1.py` (exit 1)
  - Traceback (most recent call last):

### OTHER — 4

Non-zero exit without a matched message

- `candidates/checkers/check_p9_p10_claim_boundary.py` (exit 1)
- `orion-12-open-world-scientific-discovery/scripts/check_manuscript_typography.py` (exit 2)
  - check_manuscript_typography.py: error: the following arguments are required: --l
- `orion-12-open-world-scientific-discovery/scripts/check_p2_v2.py` (exit 1)
- `orion-22-adaptive-state-reasoning/top_tier/check_p12_price_aware_successor_independent_v1.py` (exit 1)

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


---

# Update: the orphaned checkers were never orphaned

The section above reported eight independent checkers failing on a subject
JSON that "does not exist anywhere in the repository". That was measured
correctly and concluded wrongly.

The subjects are not committed artifacts. They are **runner output**. Each
independent checker has a sibling runner in the same directory that emits the
JSON on **stdout**, and nothing had ever connected the two. Redirect the
runner into the filename the checker expects, and the verification runs.

## Executed

| independent checker | runner | terminal |
|---|---|---|
| `check_decoder_attacks_independent_v1.py` | `run_decoder_attacks_v1.py` | `P11_DECODER_ATTACK_V1_INDEPENDENT_GREEN` |
| `check_donor_comparator_independent_v1.py` | `run_donor_compiler_comparator_v1.py` | `P11_DONOR_COMPARATOR_V1_INDEPENDENT_GREEN` |
| `check_p12_robustness_independent_v1.py` | `run_p12_robustness_v1.py` | `P12_ROBUSTNESS_SECOND_CHECKER_GREEN` |
| `check_transfer_allocation_independent_v1.py` | `run_transfer_allocation_v1.py` | `P12_TRANSFER_ALLOCATION_SECOND_INDEPENDENT_CHECKER_GREEN` |

These are genuine second-implementation checks, not reruns. The P11
decoder-attack checker re-derives every runner claim through exact
Fourier/Möbius spectra in `Fraction` arithmetic, explicit witness pairs, and
the Kraft identity — where the runner used direct truth-table comparison. Its
`run_receipt_sha256` matches the runner receipt, so it verified the run that
was just produced rather than a stored one.

## A real verdict, not a crash

`check_query_family_phase_independent_v1.py` returns
`P11_QUERY_FAMILY_PHASE_SECOND_CHECKER_GATE_NOT_MET` (runner exit 1). That is
the second checker declining to confirm, which is a result and is recorded as
one.

## All nine, executed

Every independent checker in the set now runs and returns a verdict.

| independent checker | producer | terminal |
|---|---|---|
| `check_decoder_attacks_independent_v1.py` | `run_decoder_attacks_v1.py` | `P11_DECODER_ATTACK_V1_INDEPENDENT_GREEN` |
| `check_donor_comparator_independent_v1.py` | `run_donor_compiler_comparator_v1.py` | `P11_DONOR_COMPARATOR_V1_INDEPENDENT_GREEN` |
| `check_p12_robustness_independent_v1.py` | `run_p12_robustness_v1.py` | `P12_ROBUSTNESS_SECOND_CHECKER_GREEN` |
| `check_transfer_allocation_independent_v1.py` | `run_transfer_allocation_v1.py` | `P12_TRANSFER_ALLOCATION_SECOND_INDEPENDENT_CHECKER_GREEN` |
| `check_unified_resource_ledger_v1.py` | `build_unified_resource_ledger_v1.py` | `P9_UNIFIED_RESOURCE_LEDGER_SECOND_CHECKER_GREEN` |
| `check_unified_resource_ledger_v2.py` | `build_unified_resource_ledger_v2.py` | `P9_UNIFIED_RESOURCE_LEDGER_SECOND_CHECKER_V2_GREEN` |
| `check_attestation_composition_independent_v1.py` | `run_attestation_composition_v1.py` | `P15_ATTESTATION_COMPOSITION_SECOND_CHECKER_GREEN` |
| `check_attestation_composition_independent_v2.py` | `run_attestation_composition_v2.py` | `P15_ATTESTATION_COMPOSITION_V2_SECOND_CHECKER_GREEN` |
| `check_provenance_interop_independent_v1.py` | `run_provenance_interop_v1.py` | `P15_PROVENANCE_INTEROP_SECOND_INDEPENDENT_CHECKER_GREEN` |

Nine green. One further checker,
`check_query_family_phase_independent_v1.py`, returns
`P11_QUERY_FAMILY_PHASE_SECOND_CHECKER_GATE_NOT_MET` — a second checker
declining to confirm, recorded as the result it is.

### What had actually blocked them

Three things, none of them a defect in any checker:

1. **Nobody connected runner to checker.** The subject JSON is stdout.
2. **The producer is not always named `run_*`.** P9's is
   `build_unified_resource_ledger_v1.py`, so a `ls run_*.py` search missed it
   and reported "no runner exists".
3. **An undeclared dependency.** `prov` is imported unguarded by both the P15
   provenance runner and its independent checker, and was in no extra. The
   checker failed with `ModuleNotFoundError` rather than a verdict, which
   reads as a broken checker when the environment was simply never told what
   it needs. Now declared as the `independent-checks` extra, folded into
   `dev`.

A fourth cause was mine: the scratch copy took `*.py *.json *.md` and not
`*.jsonl`, so the P15 attestation runner could not find
`sei_fault_cases_v1.jsonl`. Three of my own harness bugs produced false REDs
across this investigation, each caught only by a case already verified by
hand.

## Previously unresolved

- `check_unified_resource_ledger_v1.py` / `_v2.py` (P9) — no runner in
  `paper-09-.../top_tier` produces `p9_unified_resource_ledger_v1.json`. All
  three candidates were tried.
- `check_attestation_composition_independent_v1.py` / `_v2.py` (P15) — runner
  exits non-zero.
- `check_provenance_interop_independent_v1.py` (P15).

## How the wrong conclusion happened

The first pass ran each checker bare, saw `FileNotFoundError`, searched the
repository for the filename, found nothing, and concluded the subject did not
exist. Every step was correct except the last: a file absent from a
repository has not been shown to be unproducible, only uncommitted.

The corrected search was for the checker's distinctive **field names** rather
than its input filename — `kraft_identity`, `minimal_degree` — which found
the runner immediately, sitting in the same directory.

Two automated pairing harnesses were written before this table and both
produced false REDs: one selected runners with `ls run_*.py | head -1`, and
one wrote the runner's output to an absolute path escaping its scratch
directory. Both were caught because a case already verified by hand came back
RED. Without that fixed point the harness output would have been reported as
the finding.

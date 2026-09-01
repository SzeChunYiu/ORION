# Data, code, and reproducibility — ORION-06

## Data availability

The evidence for this paper is a programme's own record: an inventory of every
eligible receipt, a transition graph over the subset that qualifies, and an
audit that reports the denominator rather than only the numerator. Digests are
SHA-256 over file bytes at the submitted revision.

| Artifact | Supports | SHA-256 |
|---|---|---|
| `Q2_ELIGIBLE_RECEIPT_INVENTORY_V1.json` | The declared receipt universe (51 eligible records) against which coverage is measured | `4152805b973e6fc402e2dcf434f7ee3c136f16bd244e08654fa2feb409eddf55` |
| `Q2_TRANSITION_GRAPH_V2.json` | Included nodes, asserted successor edges, and the excluded-with-reason set | `deb18866abd028141acc5cb94e3e4147835fbb684fb01cc5a0a9358b30acab0b` |
| `revival/ORION06_NEGATIVE_COVERAGE_PROTOCOL.json` | Prospectively frozen coverage protocol | `aaab45ffcc2b184bc02a72d663036e885df8649536a02614d6f65665e6aa02ee` |
| `revival/ORION06_NEGATIVE_COVERAGE_RESULT.json` | Coverage audit result, including the undetermined cross-domain verdict | `f6b12b271f7e09ef0bff859c173e8f38686b42bc7b04b36a65f69453b4f629ec` |
| `CLAIM_LEDGER_V3.md` | The claim ceiling this manuscript is written to | `58f99f39afb9df6a17330517c4555cc17028e52e8748b4643586d611e192d255` |

The individual scientific results the paper cites as outcomes of the discipline
live under `research/extensions/orion-q/` and are separately reported.

## Code availability

- `check_transition_graph.py` — validates the transition graph against the
  eligible inventory and prints the denominator alongside every count. It
  states explicitly that it grants no scientific-causality authority.
- `revival/verify_orion06_negative_coverage.py` — reruns the coverage audit and
  emits the signed audit record.

Both are runnable without arguments from the repository root.

## Reproducibility statement

1. Run `check_transition_graph.py`. It should report a declared receipt universe
   of 51, 23 included graph nodes, 28 excluded with reason, 13 asserted
   successor edges, 10 negative-or-partial nodes, and 7 standalone nodes with no
   invented successor.
2. Run `verify_orion06_negative_coverage.py`. It should print
   `ORION06_NEGATIVE_COVERAGE=PASS` and emit an audit whose
   `scientific_authority_delta` is `NONE`.
3. Confirm that the cross-domain general-method row still reports an
   undetermined revival outcome. It is undetermined because no second
   prospectively admitted programme with matched workflow budgets and
   independent scoring exists, not because the question was tried and failed.

The denominator is the point of this reproduction. An audit that reports 23
included nodes without also reporting the 28 excluded and the 51 eligible has
not reproduced the paper's method; it has reproduced the failure mode the
method exists to prevent.

## Scope of the digests

These digests establish that the record is complete and has not moved. They do
not establish that the methodology improves research outcomes. The paper makes
no such claim, and the audit explicitly withholds authority over cross-domain
effectiveness, external independence, and productivity comparisons.

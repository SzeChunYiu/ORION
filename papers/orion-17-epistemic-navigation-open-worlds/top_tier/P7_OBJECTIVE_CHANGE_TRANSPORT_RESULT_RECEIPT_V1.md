# ORION-17 objective-change transport result receipt V1

**Run:** GitHub Actions `32663143579`  
**Artifact:** `p7-objective-change-transport-v1`, artifact ID `9499582737`  
**Artifact ZIP SHA-256:** `e185ca1a35b01dd33bd23592dd9c3d8cf3c5c73eba34a828e2277c605b085296`  
**Primary terminal:** `P7_OBJECTIVE_CHANGE_TRANSPORT_V1_SUPPORTED`  
**Independent terminal:** `P7_OBJECTIVE_CHANGE_TRANSPORT_SECOND_INDEPENDENT_CHECKER_GREEN`  
**Agreement:** `P7_OBJECTIVE_CHANGE_TRANSPORT_TWO_IMPLEMENTATIONS_AGREE`

## Exact binding

- protocol SHA-256: `dacec04b8a7de4736af0b7160261515c43d12c12c8e751e2118396189999ceec`
- primary receipt SHA-256: `6726ecc5be0e7c962828e369993a68a6f55b8bd80f2ae2f3b890bb64179d5277`
- independent receipt SHA-256: `ecef1a5b19f977b3b66bfd4ca0c9e4342257ce9ec1e7879247c89d120ae10085`
- deterministic primary replay (byte-identical `cmp`): GREEN
- independent verifier replay (byte-identical `cmp`): GREEN
- independent implementation agreement (per-fold gold + accuracy + malignant recall): GREEN

## Domain C — real objective/obligation change

The study uses the 569-example Wisconsin Diagnostic Breast Cancer data bundled by scikit-learn. Predictions are produced once under a frozen `StratifiedKFold(n_splits=5, shuffle=True, random_state=20261217)` split with fold-fitted `StandardScaler` + `LogisticRegression(C=1, solver=lbfgs, max_iter=5000)`; after the predictions are frozen, the scientific obligation changes from `accuracy >= 0.95` to `malignant-class recall >= 0.95` (malignant = class `0`). No threshold tuning, refit or recollection occurs after the change.

Across the 10 protected cells (5 folds x 2 evidence states):

| system | exact accuracy | false closure | unnecessary reopen | correct `CANNOT_CHECK` |
|---|---|---|---|---|
| WITNESS_AWARE | `1.0` | 0 | 0 | 5 |
| VALUE_ONLY | `0.3` | 5 | 1 | 0 |
| ALWAYS_REOPEN | `0.1` | 0 | 4 | 0 |

Full-witness gold dispositions: 4 `PRESERVE`, 1 `REOPEN`. Old accuracy obligation: 4 satisfied, 1 not satisfied.

Per-fold facts (FULL_CLASS_WITNESS cells):

| fold | accuracy | malignant recall | malignant tp/fn | changed-obligation gold |
|---|---|---|---|---|
| 0 | `0.964912...` | `0.906977...` | 39/4 | `REOPEN` |
| 1 | `0.947368...` | `0.953488...` | 41/2 | `PRESERVE` |
| 2 | `0.982456...` | `0.952381...` | 40/2 | `PRESERVE` |
| 3 | `0.973684...` | `0.952381...` | 40/2 | `PRESERVE` |
| 4 | `1.0` | `1.0` | 42/0 | `PRESERVE` |

The obligation change cuts both ways and value-only transport fails in both directions:

- fold 0 satisfies the old accuracy obligation (`0.965 >= 0.95`) but fails the new recall obligation (`0.907 < 0.95`): value-only false closure under the changed objective;
- fold 1 fails the old accuracy obligation (`0.947 < 0.95`) but satisfies the new recall obligation (`0.953 >= 0.95`): value-only would needlessly reopen a valid transition;
- all five ACCURACY_ONLY cells are `CANNOT_CHECK` under the changed obligation; no candidate may infer malignant recall from aggregate accuracy, and the four accuracy-passing folds become additional value-only false closures;
- always-reopen reopens the four fully-witnessed valid transitions unnecessarily and never returns `CANNOT_CHECK`.

The second implementation (manual scaling, manual confusion accounting, no reuse of the primary's facts/gold code) independently reproduces all five full-witness gold dispositions, all per-fold accuracies and malignant recalls, the 5 accuracy-only `CANNOT_CHECK` cells, the 5 value-only false closures and the 4 always-reopen unnecessary reopens.

## Scientific disposition

Together with the RO-Crate representation-change and Wine responsibility-change receipts, ORION-17 now has non-synthetic evidence in all three change classes: representation, responsibility/ontology, and objective/world/obligation. Witness-aware transport is `1.0` in each; value-only and always-reopen are each separated in every class.

This licenses the bounded claim that witness/evidence-aware closure transport survives all three executed change classes. It does **not** establish universal scientific-regime transport across arbitrary world-model, objective or research-agent changes, independent scientific authority beyond same-workflow two-implementation agreement, or any clinical use; no classifier or medical decision rule is claimed.

# ORION-21 donor-complete compiler comparator result receipt V1

**Run:** GitHub Actions `32661293913` (conclusion: success, both jobs green)  
**Artifact:** `p11-donor-comparator-v1`, artifact ID `9498981380`  
**Artifact ZIP SHA-256:** `e870bdce3937ecc18b9a23b5ebc9dc63d4be10741f8dcc7289cb5ffa2e77dbe9`  
**Terminal:** `P11_DONOR_COMPARATOR_V1_SUPPORTED` + `P11_DONOR_COMPARATOR_V1_INDEPENDENT_GREEN`  
**Replay:** `P11_DONOR_COMPARATOR_V1_BYTE_REPLAY_GREEN` (runner rerun byte-identical)

## Exact binding

- protocol SHA-256: `2e1b9671eab77db6980fa96deaa9b5f91fa091c9955177298101df1111291e2b`
- frozen gold SHA-256: `eb02731b31c993d25652beec24f611e934af1e2134f1755a9a76e152abc2aa91`
- freeze commit: `1724b07a1258f4b84ac0c5fe2b34bf33fb525d27` (precedes all machinery and outcomes)
- pull request: #993

## Protected result

Five-fold stratified accuracy (frozen folds/seeds, k matched across all selectors):

| dataset | UNIVERSAL_LINEAR | COMPILED_LINEAR (f_classif) | DONOR_MI (D5 principle) | RANDOM_K | donor disposition | random disposition |
|---|---:|---:|---:|---:|---|---|
| breast_cancer | 0.9754 | 0.9490 | 0.9490 | 0.9736 | BOTH_FAIL | CHALLENGER_ABOVE |
| wine | 0.9833 | 0.9776 | 0.9776 | 0.9663 | BOTH_PASS | BOTH_PASS |
| digits | 0.9683 | 0.9577 | 0.9577 | 0.9176 | BOTH_PASS | CHALLENGER_BELOW |

- EP1 reproduction: `positive_datasets == ["wine", "digits"]` — the parent study's
  registered result reproduced exactly under the frozen protocol.
- EP4 resource parity: all 15 (dataset, fold) cells charged the identical
  `n_train*d` fit proxy; MI additionally charged `mi_estimator_calls=d` and
  `mi_nn_distance_evals_proxy=d*n_train`.
- Donor MI is at accuracy parity with the registered compiler on **all three**
  datasets (within the frozen 0.01 threshold; identical to 4 dp everywhere),
  with identical top-k feature sets in 11/15 folds.
- RANDOM_K coincides with the f_classif selection in 0/15 folds.
- Pre-registered prediction outcomes (frozen gold, no post-hoc edits):
  - donor MI: breast_cancer **CONFIRMED**, wine **CONFIRMED**, digits **WITHHELD**.
  - RANDOM_K: breast_cancer **CORRECTED** (predicted BOTH_FAIL, observed
    CHALLENGER_ABOVE), wine **CORRECTED** (predicted CHALLENGER_BELOW, observed
    BOTH_PASS), digits **WITHHELD**.

## Scientific disposition

The donor's (D5, arXiv:2301.00557) mutual-information selection principle,
raced at matched charged compiler work and matched k, **does not beat the
registered f_classif compiler anywhere** (no CHALLENGER_ABOVE cell) and tracks
it to accuracy parity on all three datasets: the placement verdicts are
invariant under swapping selection principles. The donor is absorbed, not
threatened — the registered result generalizes across the selection-principle
fiber rather than depending on f_classif specifically.

The RANDOM_K control swing is the load-bearing control result: CHALLENGER_ABOVE
on breast_cancer but CHALLENGER_BELOW on digits. On digits — one of the two
datasets carrying the SUPPORTED terminal — random selection fails placement
(0.9176 vs 0.9577 principled) while both principled selectors pass, so the
compiled placement there is genuinely selection-dependent rather than an
artifact of dimension reduction alone. The two CORRECTED cells on the control
are reported as binding: the control was predicted to fail everywhere
selection matters, and in fact fails only where selection is hardest. No
retuning was performed; the frozen predicate and gold are untouched.

## Not earned here

- No claim about the donor's full interactive pipeline (D5 is represented by
  its selection principle at matched charged work, as the frozen protocol
  states).
- No forest-arm comparator claim: the head-to-head is the linear downstream
  decoder the placement predicate is defined on.
- No external promotion: this is internal evidence under the programme's
  no-self-authority rule (#977 §2.3).
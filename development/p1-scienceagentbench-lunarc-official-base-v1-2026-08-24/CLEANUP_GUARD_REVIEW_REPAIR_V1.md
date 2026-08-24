# Cleanup-guard independent-review repair V1

## Finding

The first clean runtime job, `3533859`, recorded null error and verified every
removal. Independent review nevertheless found a fail-open counterfactual in
the harness: if residual image enumeration/removal/pruning raised, the initial
empty `remaining_image_ids` value could survive and the driver plus batch
finalizer could still emit PASS.

## Repair

- `cleanup_gate_v1.py` now defines the single driver and batch cleanup gates.
- Every caught cleanup exception is retained in `cleanup_errors`.
- Driver PASS requires adapter-probe container, inspection container, built
  image and resolved base image removed; residual image IDs empty; and
  `cleanup_errors` empty.
- Batch PASS additionally requires driver exit zero, receipt error null, both
  node-local roots removed and every driver cleanup condition still true.
- The static validator injects each false flag, a residual image, a cleanup
  exception and a non-null receipt error; none can pass.

## Whole rerun

The hardened inputs were uploaded with content hashes and the whole public-base
smoke was rerun as Slurm job `3533961`. It completed `0:0` in `00:06:56` on
`cn045`. The receipt has `error=null`, `cleanup_errors=[]`, all per-object
removal flags true, an empty residual list and both node-local roots removed.

Job `3533859` remains in `superseded-receipts/` for provenance but is not the
integration witness. No archive/task/outcome/evaluator/credential was opened.

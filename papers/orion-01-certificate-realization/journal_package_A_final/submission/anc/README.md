# ORION-01A reproducibility records

Run the standard-library checker from this directory:

```sh
python3 proof_checker_v3.py --output reproduced-proof-result.json
python3 -m unittest -v test_proof_checker_v3.py
```

`finite_records.json` summarizes the exact finite checks and the complete
two-site support-at-most-one enumeration. The all-size normal-form authority
remains the displayed manuscript proof; finite enumeration is used only for
the exact lower witness and transcription controls.

`adverse-pyzx-round1/` preserves the exact counterexample graphs, result,
status delta, and interpretation for the consumed adverse transfer round. Its
terminal remains `CANNOT_CHECK_MOVE_COMPLETENESS`. Those records refute only
free macro reordering under callable guards. They do not refute scheduled
`full_reduce`, establish complete move coverage, realize a certificate gap, or
authorize a complete-domain null.

# Finite hostile verification artifact

This anonymous supplementary artifact contains the two deterministic checkers used for the finite verification statements in the manuscript. Run:

```text
python3 check_fibre_diameter_floor.py
python3 check_refinement_to_certifiability.py
```

The corresponding `expected_*.json` files are the frozen outputs produced by this package build. The scripts use only the Python standard library. They search for finite counterexamples and include planted-violation controls so an all-clear result is not accepted from a checker that cannot fire. These computations corroborate implementation and transcription only; the manuscript proofs carry the general finite theorem authority.

# ORION-01B reproducibility records

Run the two standard-library checkers from this directory:

```sh
python3 proof_checker_v3.py --output reproduced-proof-result.json
python3 -m unittest -v test_proof_checker_v3.py
python3 verify_dependent_triple_lemmas.py
```

`certificate_control_records.json` separates the exact R6M control from the
R6I rank-only and whole-system records. In R6I, one rank-only word position is
one block column in the union support of the two independent generators. The
ten-bit block-change alphabets have rank five; maximum individual-frame weight
is not substituted for that word length.

The finite replay exhausts 2,880 deletion rows, 6,912 core-alignment rows, 576
same-site rigidity rows, and 9,216 distinct-site Tag rows. It corroborates the
local cases but does not replace the analytic composition proof or establish
production move completeness.

`adverse-pyzx-round1/` preserves the consumed transfer round with the exact
terminal `CANNOT_CHECK_MOVE_COMPLETENESS`. It refutes only free macro
reordering under callable guards; scheduled `full_reduce`, complete move
coverage, a realized certificate gap, and a complete-domain null remain
unestablished.

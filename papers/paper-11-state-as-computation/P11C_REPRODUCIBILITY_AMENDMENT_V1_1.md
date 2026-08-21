# P11C Reproducibility Amendment V1.1 — Vectorized Parity Bank

The first execution attempt of `P11C_STRONGER_DECODER_ATTACK_PROTOCOL_V1.md` exceeded the available runner wall-time before emitting a terminal or result artifact. No protected metric or gate outcome was observed.

This amendment changes **implementation only**:

- the parity bank is evaluated by NumPy advanced indexing and `prod(axis=2)` rather than a Python loop over the identical frozen subset list;
- master seed, RNG call order, cells, queries, training sizes, test set size, decoder identities/hyperparameters, laundering checks, thresholds, gates and JSON schema are unchanged;
- the original frozen runner remains in the branch; `run_p11c_stronger_decoder_attack_v1_optimized.py` imports it and replaces only `parity_bank` before calling the original `main()`.

The vectorized function is elementwise identical to the frozen function for every input array and subset list. This amendment does not authorize changing the protocol after an outcome.

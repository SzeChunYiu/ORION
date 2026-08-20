# P14A Outcome Disposition V1

Status: **FROZEN NEGATIVE TERMINAL WITH EXACT CONSTRUCTION RETAINED**  
Date: 2026-08-20

Protocol: `P14A_CONTROLLED_SUFFICIENCY_DEBT_PROTOCOL_V1.md`  
Runner: `run_p14a_controlled_sufficiency_debt_v1.py`  
Result: `results/P14A_CONTROLLED_SUFFICIENCY_DEBT_V1.json`

Terminal:

`P14_CONTROLLED_SUFFICIENCY_DEBT_GATE_NOT_MET`

## What passed

Full enumeration of the eight latent states exactly matches the registered ladder:

- all `Z1/Z2/Z3` are perfect for PREDICT and DECIDE;
- `Z1` is exactly `0.5` for INTERVENE and VERIFY while `Z2/Z3` are `1.0`;
- `Z2` is exactly `0.5` for REPAIR while `Z3` is `1.0`;
- each registered upward sufficiency debt is therefore exactly `+0.50`;
- no representation carries a responsibility answer field.

## What failed

The protocol additionally required the maximum deviation over 100 finite-sample sanity replicates of n=1024 to be <=0.05. The observed maximum was:

`0.0556640625`

(rep 92), so the V1 terminal is negative and may not be retuned or relabeled.

## Interpretation

The exact finite construction remains mathematically valid, but P14A did **not** earn its own combined controlled terminal because its pre-registered empirical sanity sentinel failed. Any later sampling protocol must be separately frozen and justified from its own statistical design; it cannot overwrite this V1 history.

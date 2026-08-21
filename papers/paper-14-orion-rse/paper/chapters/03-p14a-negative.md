# P14A — preserved negative mixed benchmark

P14A used 20 held-out families × 400 cases with independently varied fact rates. Full ORION-RSE produced false promotion `0.000000`, useful-discovery recall `1.000000`, disposition accuracy `1.000000` and history/reopen accuracy `1.000000`.

The strongest comparator, `MULTI_REVIEW`, produced false promotion `0.018375`, useful-discovery recall `1.000000`, disposition accuracy `0.981625` and history/reopen accuracy `0.505051`.

The frozen protocol required strongest-baseline false promotion ≥0.05 and accuracy separation ≥0.08. Both gates failed. Terminal: `P14A_CONTROLLED_GOVERNANCE_SUPERIORITY_GATE_NOT_MET`. This terminal is permanent.

## Root cause

After validity, freeze, identifiability, donor and interaction checks, the only difference between `MULTI_REVIEW` and full ORION-RSE is live negative history without material new evidence. In the realized random mixture, that effective discriminator occupied only **1.8375%** of cases, so the maximum possible aggregate accuracy gap was also 1.8375 points. The result identifies a benchmark-design problem: natural/random mixtures may underweight the decision boundary being tested. P14A is not retuned; it motivates a balanced successor.
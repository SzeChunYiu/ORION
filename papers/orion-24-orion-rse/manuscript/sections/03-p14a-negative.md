# P14A — preserved negative mixed benchmark

P14A used 20 held-out families × 400 cases with independently varied fact rates. Full ORION-RSE produced false promotion `0.000000`, useful-discovery recall `1.000000`, disposition accuracy `1.000000` and history/reopen accuracy `1.000000`.

The strongest comparator, `MULTI_REVIEW`, produced false promotion `0.018375`, useful-discovery recall `1.000000`, disposition accuracy `0.981625` and history/reopen accuracy `0.505051`.

The frozen protocol required strongest-baseline false promotion ≥0.05 and accuracy separation ≥0.08. Both gates failed. Terminal: `P14A_CONTROLLED_GOVERNANCE_SUPERIORITY_GATE_NOT_MET`. This terminal is permanent.

## Root cause

After validity, freeze, identifiability, donor and interaction checks, the only difference between `MULTI_REVIEW` and full ORION-RSE is live negative history without material new evidence. In the realized random mixture, that effective discriminator occupied only **1.8375%** of cases, so the maximum possible aggregate accuracy gap was also 1.8375 points. The result identifies a benchmark-design problem: natural/random mixtures may underweight the decision boundary being tested. P14A is not retuned; it motivates a balanced successor.

## What the negative established, and what it did not

The paragraph above is a statement about the draw that happened. The stronger statement is about every draw the protocol admits, and it is the one that decides how the terminal may be cited.

Both failing gates read one quantity. `MULTI_REVIEW` reproduces the gold adjudication except where a positive is a same-evidence rereading of a live negative history; over the 144 fact states the generator can emit, that exception is a single state, and it is also `MULTI_REVIEW`'s only false promotion. `strongest_baseline_false_promotion_ge_0_05` reads its frequency; `accuracy_gain_ge_0_08` reads `1 - (1 - that frequency)`. They are one number, which is why the receipt prints `0.018375` twice.

The eight case facts are independent Bernoulli draws whose rates are each monotone in a different declared uniform, and every family's draw is mixed half-and-half with a fixed base. The prevalence is therefore a product whose extrema over the declared box sit at corners, and that box's **supremum is 0.042326** — below the 0.05 bar and well below the 0.08 one. Exercised over five registered admissible worlds spanning the declared ranges and ending at the extremal corner, the best reachable value is 0.040250, so the attainment margins are **−0.009750** and **−0.039750** and no admissible world satisfies either gate. The other five gates are satisfied by every admissible world — three of them because the graded `ORION_RSE_FULL` arm is the gold function that scores it, measured at 0 divergent points of 256. The seven-gate conjunction therefore had **one reachable value** before the seed was drawn.

The emitter is not the problem. Re-opening the declared sampling ranges and nothing else — same seed, same nine arms, same seven thresholds, same terminal expression — moves the terminal to the positive branch in three of three registered capability worlds, with two distinct terminals observed and no inert case.

P14A's terminal, seed, thresholds and receipt are retained verbatim and nothing is relabelled positive. Its evidential disposition is **`CANNOT_CHECK`**: a measurement the frozen protocol could not take, not evidence against the governance contract. The adjudication is `P14_GATE_ATTAINABILITY_ADJUDICATION_V1.json`, and the successor benchmark answers the same question at these unchanged thresholds.

A threshold is a claim about a distribution. Freeze the threshold and the support of the statistic it reads together, or an outcome has been frozen rather than a test.

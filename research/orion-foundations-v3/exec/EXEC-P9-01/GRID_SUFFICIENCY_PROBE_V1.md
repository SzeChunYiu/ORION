# EXEC-P9-01 grid-sufficiency probe (not part of the frozen protocol)

**This probe is labelled separately because it was run AFTER outcome access.**
It is not evidence for or against T14 and it does not alter the job's terminal.
It exists to answer one question the declared grid could not: is the frozen
negative a fact about T14, or a fact about the grid?

## The frozen negative

The protocol required greedy set cover to be strictly worse than the exact
minimum at least once, on the grounds that if greedy always matches optimal then
the reduction to set cover is doing no work and reporting it as support would
overstate the finding. On the declared 4x4 binary grid, over all 1,820 matrices:
**greedy tied the exact minimum every time, 0 strictly worse, 0 better.**

## The probe

Random binary matrices at larger sizes, 4,000 draws per size, duplicate-row
matrices discarded:

| rows x cols | usable samples | greedy strictly worse | greedy ever better |
|---|---|---|---|
| 5 x 6 | 3,400 | 83 | 0 |
| 6 x 7 | 3,541 | 366 | 0 |
| 7 x 8 | 3,688 | 495 | 0 |
| 8 x 9 | 3,798 | 427 | 0 |

## Reading

Greedy never beats the exact minimum at any size, which is the direction that
would have indicated the exact search was not exact. The gap appears from 5x6
onward and is absent at 4x4 simply because greedy is optimal on instances that
small.

So the frozen negative is a statement about the **discriminating power of the
declared grid**, not about T14. The theorem's identifiability biconditional was
confirmed with zero violations over 116,480 cells, and every reported minimum was
verified minimum by exhaustive smaller-subset search across all 1,820 matrices.

## Why the grid was not simply redeclared

#1234's constitutional rule forbids moving a gate after outcome access. The
declared grid stays declared and the frozen negative stays reported. A successor
job wanting the set-cover half exercised should freeze a grid of at least 5x6
**before** running it, and cite this probe as the reason.

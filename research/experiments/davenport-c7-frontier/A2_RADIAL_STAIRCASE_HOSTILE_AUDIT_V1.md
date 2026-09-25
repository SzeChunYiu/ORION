# Independent hostile audit of the exact `a=2` radial staircase — V1

Status: **independent verification and mutation audit; no competing theorem authority**.

The canonical theorem is `A2_EXACT_OVERLAP_AND_RADIAL_STAIRCASE_V1.md` on the Paper-2 integration lane. That theorem proves

`lambda_{2,c}(D)=D+2 ceil(max(D-c-2,0)/2)`

for the first-corridor capacity range. This file records a separately derived, deliberately broader replay rather than restating the theorem as a second authority surface.

## Independent scope

`verify_a2_radial_staircase_independent_v1.py`:

- reconstructs the exact bounded-resource oracle directly from counts of `s`, `g`, `e1`, and `e2`;
- includes the endpoint prime `p=5`, the empty-overlap control `c=0`, and the full formal capacity range `0<=c<=p-3`;
- proves the inverse-of-two even/odd residue split through prime `1009`;
- verifies every possible lower endpoint of the nonwrapped feasibility interval;
- freezes the first optimal resource pair `(q,z)` rather than only the optimal cost;
- checks the doubled target against the earlier parity-dependent synthesis costs;
- includes a hostile mutation that rounds the staircase down instead of up.

## Frozen audit receipt

The committed replay requires exactly:

- 167 primes through `1009`;
- 76,964 parity checks;
- 25,066,528 broad feasibility checks;
- 12,513,856 broad floor-rounding mutation disagreements;
- 73,672 full-capacity oracle rows through prime `101`;
- 73,672 even optimizers;
- 17,858 oracle-level floor-rounding mutation disagreements;
- 38,396 doubled-target checks;
- oracle transcript SHA-256

`a1775e11ae11f91b54766349013754aff9d0e159d72770cc32156414db8d6371`.

The mutation count is load-bearing: a checker that replaced the ceiling by a floor would still agree on many staircase entries and could look superficially plausible. The audit requires millions of symbolic disagreements and thousands of direct-oracle disagreements.

## Authority boundary

- The analytic theorem remains `A2_EXACT_OVERLAP_AND_RADIAL_STAIRCASE_V1.md`.
- This audit contributes independent implementation evidence and hostile calibration only.
- It does not eliminate any companion face by itself.
- No generalized Davenport value, novelty, priority, or venue claim is made.

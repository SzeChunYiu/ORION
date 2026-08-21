# ORION-Q N1-A frozen protocol — parameterized operator-schema invention (fresh re-execution)

Date frozen: 2026-08-21
Lane: ORION-Q N1 (issue #674), family N1-A
Registered design source: issue #674 body ("N1-A — parameterized operator-schema invention") and
issue comment 5355044616 (the original N1-A execution record, which was never committed).
Status of this document: protocol frozen BEFORE the result-bearing run of
`research/extensions/orion-q/nlanes/n1a_parameterized_schema_invention.py`.

## Standing

This is a **fresh re-execution** of the registered N1-A design. The numbers recorded in issue
comment 5355044616 (0/17 finite, 17/17 schema, 17/17 symbolic parent, max phase error 2.78e-16)
are the uncommitted original run and are treated as prior registration, not as this run's data.
This study is a deterministic exact-synthetic diagnostic. It carries no protected-confirmatory,
P10, novelty, or real-quantum authority. Honest negatives are valid results.

## Frozen synthetic world

- Target family: `U(x) = Rz(theta(x))` with `theta(x) = 0.7*x - 0.4*x**3` (exact, hidden from all arms
  as a formula; every arm sees only per-instance data as specified below).
- Train coordinates (13): `x = -1.2 + 0.2*j, j = 0..12` (i.e. linspace(-1.2, 1.2, 13)).
- Held-out test coordinates (17): `x = -1.5 + 0.185*i, i = 0..16`. Disjoint from train (asserted in
  code); range slightly exceeds the train hull so pure interpolation cannot pass.
- Held-out target family (registered control "at least one held-out target family"): two-qubit
  controlled rotation `CRz(theta(x))` at the same 17 test coordinates. No arm is refit on this family.
- Exact phase-safe verifier: extract the relative phase `theta = arg(U[1,1]/U[0,0])`
  (for CRz, of the controlled block); error `= |wrap(theta_target - theta_candidate)|` with wrap to
  `(-pi, pi]`. Solve tolerance `TOL = 1e-12`. `|theta(x)| < pi` on the whole coordinate range, so
  extraction is unambiguous.

## Arms (all deterministic; no RNG anywhere in this study)

1. **FINITE_EDIT_ENUMERATION (old-QC2 incumbent):** candidate edits are the 17 fixed angles
   `{k*pi/8 : k = -8..8}`; per instance the best angle is chosen by exact verifier; solve iff error
   <= TOL.
2. **ORION_SCHEMA_INVENTION (candidate mechanism):** the incumbent fails on every train instance;
   the certified obstruction certificate per failed instance is the exact required residual phase
   `theta(x)`. From the multi-instance obstruction set the mechanism (a) checks the odd-symmetry
   pattern `theta(-x) = -theta(x)` on paired train coordinates (tolerance 1e-12); (b) on success
   proposes the typed schema `theta_hat(x) = a*x + b*x**3` and fits `(a, b)` by exact least squares
   on the 13 train obstructions; (c) verifies exactly on train before any test claim.
3. **SYMBOLIC_SYNTHESIS_PARENT (strongest registered parent, first right of refusal):** receives the
   *same* visible train pairs `(x, theta(x))` and the *same schema vocabulary and more*: basis
   `{x, x**2, x**3, sin(x), cos(x)-1, x**5}`; enumerates all subsets of size <= 3, least-squares fit,
   selects the subset with minimal train max-error (ties: fewer terms, then lexicographic). Applied
   unchanged to both held-out sets.
4. **LOOKUP_INTERPOLATION control (registered "no credit for interpolating a lookup table"):**
   piecewise-linear interpolation of train `(x, theta)` evaluated at test coordinates.

Both ORION and the parent transfer their fitted `theta_hat` to the held-out `CRz` family with no
refit; the finite library uses fixed-angle CRz edits.

## Prespecified gates

- `G1_WORLD_VALID`: finite enumeration scores 0/17 on held-out Rz and 0/17 on held-out CRz
  (the schema genuinely lies outside the finite edit list).
- `G2_LOOKUP_FAILS`: lookup interpolation scores 0/17 exact solves.
- `G3_ORION_EXACT`: ORION schema scores 17/17 on both held-out sets with max error <= 1e-12.
- `G4_PARENT_DECISION`: parent solve counts compared to ORION on both held-out sets.

## Terminal rule (frozen)

- If G1, G2, G3 all pass and parent >= ORION on all held-out sets:
  `N1A_SYMBOLIC_SYNTHESIS_PARENT_SUFFICIENT` (registered expected outcome; negative retained).
- If G1, G2, G3 pass and parent < ORION anywhere: `N1A_SCHEMA_INVENTION_SUPPORTED` (bounded).
- If G3 fails: `N1A_NO_INCREMENTAL_VALUE`.
- If G1 or G2 fails: `N1A_WORLD_INVALID` (no outcome claim permitted).

## Determinism

No random numbers are used. All grids and libraries are the exact constants above. Receipt line:
`ORIONQ_N1A_PARAM_SCHEMA=<canonical sorted json>`; pretty receipt written to
`research/extensions/orion-q/nlanes/N1_A_PARAM_SCHEMA_RESULTS.json`.

## Claim boundary

Exact-synthetic scope only. No claim of novelty for parameterized-constant synthesis (CEGIS(T),
DreamCoder-family, quantum component learning are acknowledged parents). No real-quantum authority.

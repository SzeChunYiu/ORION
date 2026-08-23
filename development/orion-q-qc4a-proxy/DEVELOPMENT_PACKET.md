# ORION-Q QC-4A — asymptotic route-proxy development packet

Tracking issue: #648
Parent: #633
Donor saturation: #638

## Development question

Before training any P9 route selector, is the simplest standard-QSVT vs randomized-QSVT choice already analytically closed by donor-published asymptotic scaling under a frozen common LCU/LCH parameterization?

## Donor facts frozen for this diagnostic

From *Randomized Quantum Singular Value Transformation* (2025):

- standard LCU block-encoded QSVT circuit depth scales as `O_tilde(L * lambda * d)` and uses `O(log L)` ancillas;
- randomized QSVT circuit depth scales as `O_tilde(lambda^2 * d^2)`, is independent of `L`, and uses one ancilla;
- the randomized quadratic dependence on polynomial degree is optimal within the paper's sampling access model.

This packet does not claim those formulas as ORION results.

## Atomic fibres

1. Freeze a tiny parameter object `(L, lambda, d)` with positive finite values.
2. Compute only the two published scaling proxies, with no hidden constants fabricated.
3. Derive the exact algebraic proxy crossover `L > lambda*d` for randomized depth advantage.
4. Record ancilla comparison separately; do not scalarize depth and ancillas.
5. Represent equality as `NO_DEPTH_DOMINANCE` rather than choosing a winner.
6. Explicitly mark the whole object `ASYMPTOTIC_PROXY_ONLY`.
7. Test counterfactual monotonicity and crossover boundaries.

## Challenge to the formulation

This proxy is invalid for scientific route selection if treated as compiled resource estimates, if hidden polylogarithms/constants are ignored in a claimed real advantage, or if route access assumptions differ. Its purpose is diagnostic: decide whether learning has any role in the simplest abstraction.

## Miss hypotheses

1. Algebraic crossover could be implemented with an inequality sign error.
2. Lambda or degree could be allowed to be zero/negative, creating nonsense comparisons.
3. A scalar score could hide the fact that randomized QSVT has an ancilla advantage even where its depth proxy is worse.
4. A learned selector could appear to add value only because the analytic donor rule was omitted as a baseline.

## Frozen hypothesis

> Under the frozen proxy formulas, the depth-preference boundary is exactly `L > lambda*d`; therefore a hand-coded donor-complete selector is sufficient for the two-route depth subproblem, and no P9 learning claim is scientifically justified there.

## Frozen tests

- `L > lambda*d` -> randomized depth proxy lower;
- `L < lambda*d` -> standard depth proxy lower;
- equality -> no depth dominance;
- increasing `L` alone can cross toward randomized;
- increasing `d` alone can cross toward standard;
- invalid values fail closed;
- ancilla recommendation remains vector-valued and does not overwrite depth outcome;
- proxy payload states that constants/polylogs/access-model details are unresolved.

## Expected scientific disposition

If tests pass, record `QC4A_TWO_ROUTE_ANALYTICALLY_CLOSED`: a negative result for learned route selection at this abstraction level, and a reason to escalate only to the multi-route/interface-diagnosis problem.

## Authority

Diagnostic engineering result only. No claim that either route wins on a concrete physical workload is authorized.
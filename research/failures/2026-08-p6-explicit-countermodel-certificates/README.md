# P6 explicit countermodel certificates

## Observed

Two hosted CI runs preserved an adverse result from P6's former bounded
countermodel-discovery path.

- [Run 32927946106](https://github.com/SzeChunYiu/ORION/actions/runs/32927946106),
  head `8a966761677e9fac40bbbe69ed9a382cb2370206`, failed. The edge-restriction
  condition was reported as carried only intermittently, the P6 CLI returned
  3, and the suite ended with 1 failed and 6,707 passed tests.
- [Run 32946736266](https://github.com/SzeChunYiu/ORION/actions/runs/32946736266),
  head `4d80fe679bea289a00f19fb5a2ea393fe2fae669`, failed. The same condition had
  no theorem in the intersection of three runs, which cascaded into four P6
  failures: the frame-condition assertion, its named stable-core assertion,
  the report assertion, and CLI exit 3. The suite ended with 4 failed and 6,707
  passed tests.

Both outcomes remain failures. Neither is reclassified as a passing scientific
result.

## Failure

The retired check asked Z3 to discover countermodels for every theorem after
each dropped condition, three times, in a universe of at most four nodes. The
bound was sound for refutation but operationally insufficient: it left symmetry
and unconstrained structure in a quantified search. Under concurrent load, a
known one-node countermodel for the edge restriction could consume the 20 s
budget and return `UNKNOWN`.

The decisive transition was reproduced locally under load. The certificate-
supports-nothing query returned `COUNTERMODEL` in two rounds and `UNDECIDED`
after 20.033 s in the third. The earlier classifier correctly retained that as
`CANNOT_CHECK`; the mistake was relying on model discovery for a witness that
could be stated directly.

## Failure class

`LOAD_DEPENDENT_COUNTERMODEL_DISCOVERY`

A finite upper bound does not make a quantified model search deterministic, and
repeating a timeout-sensitive search does not turn its intersection into an
immutable certificate.

## Correct response

Do not raise the timeout, retry until green, or reinterpret `UNKNOWN` as either
proof or refutation. Pin one complete smallest countermodel for each frame
condition and verify it:

- dropping coordinate support: an exact two-node model refuting certificate
  withdrawal;
- dropping the edge restriction: an exact one-node model refuting that the
  certificate supports nothing;
- dropping certificate non-coordinateness: an exact one-node model refuting
  certificate withdrawal.

The verifier fixes the exact domain and every coordinate, edge, reachability,
change and rank entry. `SAT` verifies the supplied countermodel;
`UNSAT` invalidates that certificate rather than declaring the condition inert;
`UNKNOWN` remains `CANNOT_CHECK`.

## Authority boundary

These are local, self-authored formal countermodel certificates. They establish
necessity only relative to the checked axioms, named theorems and finite models.
They do not establish empirical performance, novelty, superiority, independent
reproduction, or external scientific authority. External and independent
validation remains `CANNOT_CHECK` under P6-U-T4.

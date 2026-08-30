# Amendment 1 — the adversarial encoding is measured, not assumed

**Made before any diagnosis outcome was computed.** Only encoding cost was
measured; no arm was run, no threshold fitted, no terminal assigned.

## What was wrong

`PROTOCOL_V1.md` named the accessibility-deficient form as "a one-hot cardinality
constraint expanded into pairwise form", assuming the boolean pairwise encoding is
the hard one and a high-level integer encoding is the reference. **That assumption
is backwards for this solver**, and the first run showed it immediately: the
integer-`Distinct` "reference" returned `unknown` at the 10 s budget for *every*
pigeonhole size from n=8 up, while the boolean form it was supposed to be easier
than returned `unsat` in 0.18 s at n=8.

A study whose reference form does not solve has no reference. Calibration replaced
assumption:

| pigeonhole | int (`Distinct`) | bool (pairwise) | **bv** |
|---|---|---|---|
| n=7 | unsat 1.51 s | unsat 0.02 s | unsat 0.53 s |
| n=8 | **unknown** | unsat 0.18 s | unsat 0.06 s |
| n=10 | unknown | **unknown** | unsat 1.00 s |
| n=11 | unknown | unknown | **unsat 2.03 s** |

The bit-vector encoding is the accessible one and the integer encoding is the
adversarial one — the reverse of what was written down.

## Roles, now assigned by measurement

| family | reference (accessible) | accessibility-deficient | usable range |
|---|---|---|---|
| pigeonhole | bit-vector `Distinct` | integer `Distinct` | n = 6…11 |
| colouring | bit-vector | integer | k = 6…10 |
| factoring | bit-vector, no-overflow | integer | 17…28 bits |

`INFORMATION` still deletes a necessary constraint and flips the verdict;
`COMPUTE` still runs the reference under a budget below what it needs. Only the
identity of the adversarial encoding changed.

## The linear family is dropped

Both its encodings solved in under 0.1 s at every size tried up to m=30, and a
reformulation as odd-weight subset sum was satisfiable rather than contradictory.
No accessibility gap exists there at reachable sizes, so it contributes nothing and
is removed rather than padded out.

## A bug in the factoring encoding, found by a positive control

The first factoring encoding returned **`sat` for primes** — impossible. Bit-vector
multiplication wraps modulo 2^W, and with `y` unbounded above the solver satisfied
`x*y == N` by overflow. Fixed with an explicit `BVMulNoOverflow` and a widened word.

The control that caught it is retained: composites **must** return `sat`, and they
do (65536, 1000004, 15485864). Without it, `unsat` on primes could have been
vacuous — true because the encoding admitted no models at all rather than because
the number has no factors.

## What is unchanged

Utilities, arms, matched budgets, the development/held-out split and seed, the
primary endpoint of false compute escalation, the no-retuning rule, and every
terminal stay exactly as `PROTOCOL_V1.md` committed them.

## An honest limitation

All three families end up with a bit-vector reference and an integer adversarial
form. The problems differ — counting, graph, arithmetic — but the *encoding axis*
does not, so this measures accessibility along one axis rather than several.

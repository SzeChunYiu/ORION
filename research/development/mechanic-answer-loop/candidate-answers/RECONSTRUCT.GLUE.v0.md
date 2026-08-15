# Candidate answer — RECONSTRUCT.GLUE.v0

**Target dimensions:** MATHEMATICS, FAILURE (falsifier), INVARIANTS, OUTPUTS.
**Incumbent evidence:** RAKL `publication/papers/paper-01-epistemic-mechanics/sections/02_compatibility_authority.tex` @ `bd4ce50f` (§The current object: a typed compatibility complex; §A three-context parity obstruction; §From compatibility to closure; §Two layers rather than one overloaded object).

## Proposed step-specific contract

**Mathematics — two layers, never one overloaded object.**

1. *Compatibility layer:* \(\mathfrak C=(A, W, \mathcal P)\) — typed atoms, a partial map of witnessed pairwise compatibility statuses, and admissible finite constructive paths. Incumbent proposition (with proof): this data does **not** define an order-theoretic lattice (witnessed compatibility is symmetric; no meet/join elements are constructed). Lattice vocabulary is forbidden at this layer.
2. *Closure layer:* only a declared closure operator \(\mathrm{cl}\) (extensive, monotone, idempotent) yields a genuine complete lattice of closed states, with \(\wedge=\cap\) and \(\vee=\mathrm{cl}(\cup)\) (closure-system theorem, Birkhoff/FCA/abstract-interpretation lineage). Saturation relative to \(\mathrm{cl}\) is a fixed point — certified only against a bounded basis and horizon, because the open-world universe and discovery operator can expand.

**Invariant (the load-bearing one).** *Pairwise compatibility does not imply global consistency.* Gluing verdicts must support obstruction objects on covers larger than pairs; edge labels alone are insufficient.

**Outputs.** `GLUED(section)`, `OBSTRUCTED(cover, obstruction-object)`, `NOT_GLUABLE_UNDER_WITNESS_POLICY`, `CANNOT_CHECK(missing witness/map)`.

## Known-answer test candidate (exact, from the incumbent)

Three binary variables, three contexts \(U_{xy}, U_{yz}, U_{xz}\) with parity constraints \(x\oplus y=0,\; y\oplus z=0,\; x\oplus z=1\): every pairwise overlap is compatible, yet no global assignment exists. The GLUE mechanic must return `OBSTRUCTED` on the triple cover while all three pairwise checks pass. A GLUE implementation that answers `GLUED` here is refuted.

## Hostile test candidate

Rename an atom in one chart ("different words") and check the mechanic does not manufacture an obstruction from vocabulary alone — identity resolution must precede gluing.

## Not licensed

The incumbent explicitly does not implement sheaf axioms or causal-abstraction gluing (D'Acunto et al. own the stronger claim); the cell's contract must not claim them either. Live multi-domain portrait quality remains an empirical open coordinate.

# ORION-01 R11 implementation amendment 02

Date: 2026-08-27

The post-counterexample custody review found that including `HEAD` at execution
inside a byte-stable generated receipt would make a later committed replay
differ solely because the result commit had advanced `HEAD`. Amendment 02
removes that unstable field. The stable freeze commit, current frozen blob
manifest, and runner's last-change commit remain bound.

This is a custody-only repair. It changes no scientific subject, source,
registry, input, objective, semantics gate, terminal, or interpretation, and
it does not erase either prior execution failure.

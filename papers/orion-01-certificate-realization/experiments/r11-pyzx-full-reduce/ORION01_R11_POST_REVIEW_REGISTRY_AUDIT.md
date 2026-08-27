# ORION-01 R11 additive post-review registry audit

## Controlling disposition

```text
ORION01_R11_POST_REVIEW_REGISTRY_AUDIT_PASS__ADVERSE_TERMINAL_UNCHANGED
```

This is an additive hostile-review correction. It does not edit the frozen
runner, registry, raw result, counterexample graphs, failure receipts, or the
Round-1 terminal `CANNOT_CHECK_MOVE_COMPLETENESS`.

Two auxiliary controls in the frozen runner were insufficient as written:

1. the inline one-entry omission loop compared two sets already known to be
   unequal after deleting an element, so its twelve `rejected` flags were
   non-identifying rather than an independent hostile test;
2. the AST comparison filtered calls through a known-symbol whitelist before
   comparing the control graph, so it could not by itself exclude an omitted
   unknown call.

The additive verifier repairs both controls without changing outcome bytes. It
actually removes each of the twelve entries from a copied frozen registry and
requires `derive_source_registry` to reject every mutant. It also inventories
**every** call expression in the four pinned PyZX control functions, then
requires the complete call set to equal the frozen expected inventory. The
only explicitly non-mutating calls outside the twelve registered rewrite
macros and control wrappers are `ValueError`, `any`, `g.types`, and
`g.vertices` in `full_reduce`.

This repair corroborates only the exact pinned-source structural audit. It does
not establish a complete contextual production registry, a certificate gap,
the unexecuted 4,681-word null, PyZX unsoundness, external independence,
novelty, journal authority, or submission readiness. The deterministic
`H0,H0,H0` callable-guard counterexample and its narrow adverse interpretation
remain unchanged.

# Implementation amendment 03: genuine registry-surface mutation replay

The first additive post-review checker removed each operation from
`registered_symbol_order` and `registered_schemas`, but not from
`control_call_graph`. Its rejection therefore arose from inconsistent registry
fields rather than from an unregistered call observed in the pinned PyZX
source. That control is non-authoritative.

The corrected checker now removes each operation from all three registry
surfaces and reruns the unfiltered full-call audit against the pinned source.
Every mutant is rejected specifically because the omitted operation remains an
observed source call. The frozen runner, raw result, failure receipts,
counterexample graphs, and Round-1 terminal remain byte-identical.

This repair does not establish a complete contextual production registry or
change `CANNOT_CHECK_MOVE_COMPLETENESS`.

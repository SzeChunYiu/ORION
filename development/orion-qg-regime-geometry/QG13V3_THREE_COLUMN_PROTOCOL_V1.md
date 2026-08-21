# QG-13 V3 — three-column R6I combined-edit mining

Issue: SzeChunYiu/ORION#785
Frozen base: `cad8b1b4d3be3668449658d10ef718eb1682d1c9`
Branch: `shadow/orion-qg-qg13-v3-r6i-three-column-edits`
Status: FROZEN BEFORE PROTECTED OUTCOME.

V3 changes exactly one scientific coordinate from V2: action arity is three distinct columns. The action alphabet remains A/B/AB, the inferred five-bit block syndrome is unchanged, Tag repair is forbidden, and targets/Tag/permutation/central choices/other block remain fixed.

A three-column action is globally safe only when the XOR of the three production-derived syndrome changes is zero and the sum of their exact single-column worst local cost deltas is <=0. It must strictly reduce `(max_generator_support,total_generator_support)`.

The global domain is recomputed from scratch: every canonical five-column structural pattern with accepting R6I block syndrome, QG-1 SOLO/PAIR irreducibility, and at least one support-five generator.

V3 reports:
- E3-only coverage over the full support-five domain;
- a separately recomputed V2 E2-uncovered domain and how many are closed by E3;
- cumulative E2 union E3 coverage, successor evidence only.

Frozen terminals:
- `QG13V3_SUPPORT4_CANDIDATE` if E3 alone covers every support-five pattern;
- `QG13V3_V2_OBSTRUCTIONS_CLOSED_BUT_NEW_OBSTRUCTION_REMAINS` if every recomputed V2 obstruction is closed but E3 alone leaves another support-five pattern;
- `QG13V3_MINIMAL_THREE_COLUMN_OBSTRUCTION` if any V2 obstruction survives E3;
- `QG13V3_RESOURCE_BOUNDARY`, semantic/binding, or CANNOT_CHECK as honest alternatives.

Even if cumulative E2 union E3 covers every pattern, V3 cannot promote that to support<=4 theorem authority. That requires a new prospective packet under QG-9.

No QG-13 V2 result file is read during synthesis; V2 is recomputed from the same production local table only after E3 action classes/census are formed. No chemistry/protected subject; no network; no post-outcome grammar widening.

`new_theorem_authority=false`
`novelty_authority=false`
`physical_quantum_advantage_claim=false`

# X1-B k=4 — R3-11 and R3-12 exact ten-prefix primary results

Parent: #900.
Protocol: `X1B_K4_RANK3_FORBIDDEN_PREFIX_PROTOCOL.md`.
Implementation: `x1b_k4_rank3_forbidden_prefix_exact.cpp`.

## Evidence status

**PROSPECTIVE PRIMARY EXACT ENUMERATIONS.** The class definitions and success criterion were frozen before these runs. Independent replay is still required before theorem promotion.

## R3-11

Exact layer census:

```text
depth 0:          1
depth 1:        114
depth 2:      5,968
depth 3:    173,931
depth 4:  2,603,426
depth 5: 10,097,562
depth 6:  3,239,592
depth 7:    210,896
depth 8:      3,038
depth 9:          1
depth 10:         0
```

Legal transitions generated: `48,518,243`.

Result: **NO length-10 prefix; exact maximum length 9.**

Subject to independent confirmation, this eliminates all 40 rank-3 completions in class R3-11.

## R3-12

Exact layer census:

```text
depth 0:          1
depth 1:        113
depth 2:      5,809
depth 3:    163,127
depth 4:  2,248,287
depth 5:  6,479,538
depth 6:  1,426,145
depth 7:     75,757
depth 8:      1,073
depth 9:          1
depth 10:         0
```

Legal transitions generated: `31,212,863`.

Result: **NO length-10 prefix; exact maximum length 9.**

Subject to independent confirmation, this eliminates all 64 rank-3 completions in class R3-12.

## Aggregate primary result

Together with the separately committed R3-10 primary result, **all three `GL(3,5)` classes covering all 116 rank-3 bilinear completions have primary exact maximum prefix length 9**.

No rank-3 completion presently survives the frozen ten-prefix condition at the primary-enumeration level.

## Authority boundary

This packet does not yet close the rank-3 family for theorem use because the frozen protocol requires independent replay of a NO. It also does not address the separate rank-2 radical realization family or prove `D(C_15^3)=43`.

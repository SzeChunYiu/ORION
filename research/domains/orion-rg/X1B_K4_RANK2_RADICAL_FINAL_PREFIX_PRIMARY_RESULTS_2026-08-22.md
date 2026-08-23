# X1-B k=4 — primary exact NO for final rank-2 radical prefix classes

Parent: #900.
Frozen protocol: `X1B_K4_RANK2_RADICAL_FINAL_PREFIX_PROTOCOL.md`.
Implementation: `x1b_k4_rank2_radical_final_prefix_exact.cpp`.

## Evidence status

**PROSPECTIVE PRIMARY EXACT ENUMERATIONS.** Independent replay remains required before theorem promotion.

## R2R-11

Exact layer census:

```text
depth 0:          1
depth 1:        114
depth 2:      5,969
depth 3:    174,097
depth 4:  2,624,280
depth 5: 10,214,173
depth 6:  3,212,251
depth 7:    245,172
depth 8:      9,949
depth 9:          1
depth 10:         0
```

Legal transitions: `50,999,751`.

Result: **NO length-10 prefix; exact maximum length 9.**

## R2R-12

Exact layer census:

```text
depth 0:          1
depth 1:        113
depth 2:      5,813
depth 3:    163,662
depth 4:  2,296,600
depth 5:  7,160,425
depth 6:  1,817,849
depth 7:    105,173
depth 8:      1,452
depth 9:          1
depth 10:         0
```

Legal transitions: `34,793,396`.

Result: **NO length-10 prefix; exact maximum length 9.**

## Primary consequence

Together with the complete radical census and containment reduction, these two NO results primary-eliminate every remaining inclusion-minimal rank-2 radical forbidden class.

If an algorithmically independent replay confirms both NO results, the entire rank-2 radical branch closes. Since all rank-3 completions are already independently eliminated, that would close the complete k=4 residual interface.

## Authority boundary

This is not yet k=4 theorem authority because the frozen protocol requires independent replay. It does not by itself prove `D(C_15^3)=43`.
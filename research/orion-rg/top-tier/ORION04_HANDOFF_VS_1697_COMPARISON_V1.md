# ORION-04: comparing the handoff theorem against #1697

#1701 asks to *compare the handoff theorem against #1697* and to *repurpose #1697
as independent certificate/proof corroboration rather than rediscovery*. Both are
done here, and the answer to the second is qualified in a way that matters.

## They target the identical claim

| | handoff packet | #1697 |
|---|---|---|
| location | `research/orion-rg/top-tier/orion04-global-obstruction-v1/` | `research/orion-rg/promotion/orion04-global-certified-search-v1/` |
| terminal | `ORION04_C0_31_PROVED__IMPLIES_D4_C5CUBED_EXACT_30` | `ORION04_C0_31_PROVED__D4_C5CUBED_EXACT_30` |
| method | dual C engines (bit-vector and AVX2), 78 exhaustive rank/plane branches | deterministic OPB/CNF encoding of the whole length-31 obstruction |
| independence device | two engines must agree byte-for-byte on stdout | standalone witness checker + pinned external DRAT proof checker |

These are genuinely different routes. One enumerates branches in compiled C and
requires two implementations to agree; the other reduces the whole object to a
pseudo-Boolean instance and defers authority to an external proof checker. They
share the mathematical object and nothing else.

## #1697 cannot corroborate yet, and says so itself

`CLAIM_DISPOSITION.md` in the #1697 packet is explicit. Earned: a complete
encoding, a deterministic generator, small-group controls, a standalone checker, a
fail-closed receipt wrapper. **Not earned: "No full-instance solver outcome or
proof has been admitted."** There is no RESULT file and no receipt in that packet.

So #1697 is an independent route that **has not been run**. Calling it
corroboration today would be counting a design as a result. It is correctly
repurposed as *the corroboration path*, and its status is `CANNOT_CHECK` until a
proof or witness is admitted through it.

## What can be corroborated today, and is

The handoff's structural census does not need either implementation. It claims
**60 multiplicity patterns over supports 14–31**. With multiplicities in {1,2,4},
total length 31 and support at least 14, the patterns are exactly the triples
`(a,b,c)` with `a + 2b + 4c = 31` and `a + b + c >= 14`.

Enumerated directly:

- **60 patterns**, support range **14–31** — matching the packet exactly.
- Patterns per support: 14:4, 15:5, 16:6, 17:5, 18:5, 19:5, 20:4, 21:4, 22:4,
  23:3, 24:3, 25:3, 26:2, 27:2, 28:2, 29:1, 30:1, 31:1.
- The support-31 extreme is the unique `(31,0,0)`, which is the packet's own
  largest branch `s31:a31:b0:c0:ALL_SINGLETON_FULL_BASIS` with pattern `[31,0,0]`.
- A support-14 pattern is `(1,11,2)`, which is the packet's first recorded branch,
  `a1=1 b2=11 c4=2`.

This is a third derivation, arithmetic only, agreeing with the packet at both
extremes and on the total. It corroborates the **combinatorial frame**. It says
nothing about the 78-branch rank/plane decomposition, which depends on the
`GL(3,5)` normalization, and nothing about the zero-survivor result, which is the
part that needs a solver.

## Consequence

The handoff's counts are independently sound at the level arithmetic can reach.
The claim that no obstruction survives still rests on one executed route with an
internal two-engine agreement, and #1697 remains the outstanding external check
rather than a completed one. The packet's own fields already say this:
`external_independent_replay_complete: false`.

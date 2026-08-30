# ORION-09 — independent checker execution receipt

**Executed:** 2026-08-29 on **LUNARC**, by the ORION-17xx orchestration lane, from a fresh
checkout of `wk/p0-evidence-20260829` at commit `787b6274`, LUNARC venv, Python 3.11.5.
**Not executed on the author's workstation.** Transcript retained by the orchestrator.

**Authority label:** `IMPLEMENTATION_INDEPENDENT`. This is **not** external verification
and **not** independent-investigator replication — same programme, same researcher,
different machine and different code path. `scientific_authority_delta = NONE`.

**Applicability to this tree:** the only change inside
`theory/regime-separator-complexity-v1/` between `787b6274` and the current branch head is
this packet's prose receipt (`MANUSCRIPT_INTEGRATION_RECEIPT_V1.md`). No checker, input
receipt, protocol or result artifact moved, so the run attests the current tree's checker
inputs. Verified with `git diff --name-status 787b6274 HEAD -- <this dir>`.

## Results — all three exited 0 (not 3), all `"status": "PASS"`

| checker | exit | outcome |
|---|---|---|
| `independent_checker/extract_frozen_matrix.py` | 0 | `PASS`, `"mismatches": {}`, `protocol_sha256_matches_receipt: true` |
| `independent_checker/separator_complexity.py` | 0 | `PASS`, `k_star: 4`, `k_star_proved_minimal: true` |
| `independent_checker/verify_minimality.py` | 0 | `PASS`, `k_star_at_least_4_PROVED: true` |

Exit code 3 is this packet's reserved `CANNOT_CHECK` signal. It was not returned.

### Stage-1 replay reproduced exactly

1,146 instances, 127 features, 1,109 cells, 1,072 singletons, 0 mixed cells, floor 0,
compression 0.967714; per-`n` domain 6 / 60 / 1,080 with 5 / 28 / 189 donor-exact. Zero
mismatches against the frozen R2 receipt.

### `k* = 4` has two-route confirmation that does not share search logic

This is stronger than "a checker agreed", and the packet says why in its own output:

> `"independence": "exhaustive enumeration over subsets; shares no search logic with the
> branch-and-bound in separator_complexity.py"`

- **Route 1 (exhaustive refutation):** all 127 singletons, all 8,001 pairs and all 333,375
  triples tested; every covering-subset list empty; `k_star_at_least_4_PROVED: true`.
- **Route 2 (witness):** `{15, 30, 39, 42}` re-projected over all 1,146 instances gives 523
  cells, 0 mixed, floor 0.
- **Route 2b (drop-one guard)**, which uses no discernibility machinery at all and would
  therefore expose a constraint-dropping fault shared by routes 1 and 2: dropping each
  witness coordinate gives floors 47, 22, 17 and 1 — all strictly positive, so every
  coordinate is individually necessary and the witness is minimal, not merely of minimum
  cardinality.

So the branch-and-bound search in `separator_complexity.py` is confirmed by an exhaustive
enumeration that shares none of its logic, plus a third check sharing neither.

### Both structure-free nulls reproduced

Full L3 map: `N - c = 37`, bound `[0, 37/1146] = [0, 0.032286]`; exact probability
`7.057e-07` with `0/20,000` permutation hits. Witness map: compression 0.45637, bound
`623/1146`, exact probability `1.442e-120`.

### The adverse block-attribution finding is reproduced, not softened

`route_3_block_attribution` returns V2 alone floor 1, donor-path alone floor 5, sign-aware
STATE block alone floor 43; and **V2 + donor-path floor 0** with `witness_block_composition`
`{V2_33: 2, donor_path_53: 2}` and `state_block_features_in_witness: 0`. The independent
checker therefore confirms the negative: the conversion did not require the new sign-aware
block, and the mechanism attribution remains unsupported.

The `n=4` non-transfer (32/120 CV errors, shuffle-null mean 32.41, `p=0.51`) is outside
these checkers' scope and is unchanged.
